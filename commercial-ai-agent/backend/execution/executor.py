from typing import Dict, Any, List
from backend.mcp.client import MCPClient
from backend.mcp.registry import registry
from backend.execution.state_machine import StateMachine, ExecutionState
from backend.execution.approval import ApprovalManager
from backend.execution.retry import RetryPolicy

class ExecutionEngine:
    def __init__(self, mcp_client: MCPClient):
        self.mcp = mcp_client
        
    def execute_plan(
        self, 
        execution_id: str, 
        plan: Dict[str, Any], 
        state_machine: StateMachine, 
        approved_step_ids: List[int] = None,
        prior_results: Dict[int, Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an execution plan.
        Supports pausing for approval and resuming.
        """
        import re
        import logging
        logger = logging.getLogger("ExecutionEngine")
        
        if approved_step_ids is None:
            approved_step_ids = []
            
        state_machine.transition_to(ExecutionState.EXECUTING)
        
        # Successful steps are retained across human-approval pauses.  Replaying
        # them would duplicate quotes, documents, or other side effects.
        results = dict(prior_results or {})  # Keyed by int step IDs
        steps = sorted(plan.get("steps", []), key=lambda x: x.get("id", 0))

        if not steps:
            state_machine.transition_to(ExecutionState.FAILED, "Plan contains no steps")
            return {"status": "failed", "reason": "empty_plan", "results": results}

        try:
            step_ids = [int(step["id"]) for step in steps]
        except (KeyError, TypeError, ValueError):
            state_machine.transition_to(ExecutionState.FAILED, "Each plan step requires an integer id")
            return {"status": "failed", "reason": "invalid_plan", "results": results}
        if len(step_ids) != len(set(step_ids)) or any(step_id <= 0 for step_id in step_ids):
            state_machine.transition_to(ExecutionState.FAILED, "Plan step ids must be unique positive integers")
            return {"status": "failed", "reason": "invalid_plan", "results": results}
        
        logger.info(f"Executing plan with {len(steps)} steps")
        for step in steps:
            logger.info(f"  Step {step.get('id')}: {step.get('tool')} args={step.get('arguments')}")
        
        for step in steps:
            # Normalize step ID to int
            step_id = int(step["id"])
            tool_name = step.get("tool")
            arguments = step.get("arguments", {})
            try:
                depends_on = [int(d) for d in step.get("depends_on", [])]
            except (TypeError, ValueError):
                state_machine.transition_to(ExecutionState.FAILED, f"Invalid dependencies for step {step_id}")
                return {"status": "failed", "step": step_id, "reason": "invalid_plan", "results": results}

            if any(dep_id not in step_ids or dep_id == step_id for dep_id in depends_on):
                state_machine.transition_to(ExecutionState.FAILED, f"Invalid dependencies for step {step_id}")
                return {"status": "failed", "step": step_id, "reason": "invalid_plan", "results": results}

            if results.get(step_id, {}).get("success"):
                logger.info(f"Skipping already completed step {step_id} ({tool_name})")
                continue
            
            # Check dependencies
            for dep_id in depends_on:
                if dep_id not in results or not results[dep_id].get("success"):
                    state_machine.transition_to(ExecutionState.FAILED, f"Dependencies failed for step {step_id}")
                    return {"status": "failed", "step": step_id, "reason": "dependencies_failed"}
                
            tool_schema = registry.get_tool(tool_name)
            if not tool_schema:
                state_machine.transition_to(ExecutionState.FAILED, f"Tool {tool_name} not found")
                return {"status": "failed", "step": step_id, "reason": "tool_not_found"}
                
            # Check approval
            if ApprovalManager.requires_approval(tool_schema) and step_id not in approved_step_ids:
                state_machine.transition_to(ExecutionState.WAITING_APPROVAL)
                return {
                    "status": "waiting_approval",
                    "step": step_id,
                    "tool": tool_name,
                    "arguments": arguments,
                    "results_so_far": results
                }
                
            # --- Interpolation Engine ---
            _NOT_FOUND = object()
            
            def _extract_from_data(data, key_path):
                """Extract a value from step result data using a dot-separated key path.
                Handles lists (takes first element), dicts (navigates keys), and fallbacks."""
                keys = key_path.split(".")
                current = data
                
                for i, key in enumerate(keys):
                    # Unwrap lists — take first element
                    if isinstance(current, list):
                        if len(current) == 0:
                            return _NOT_FOUND
                        current = current[0]
                    
                    if isinstance(current, dict):
                        if key in current:
                            current = current[key]
                        elif key.endswith("_id") and "id" in current:
                            current = current["id"]
                        elif key == "result" and i < len(keys) - 1:
                            # Smart fallback: if LLM hallucinated 'result' as an intermediate key 
                            # (e.g. step1.result.id) but 'result' isn't in the dict, just ignore 'result'
                            pass
                        elif key == "result" and i == len(keys) - 1:
                            # Smart fallback: if LLM asked for 'result' at the end of the path (e.g. step4.result)
                            # but it's not there, try to guess the most likely output it wanted.
                            if "file_path" in current:
                                current = current["file_path"]
                            elif "id" in current:
                                current = current["id"]
                            else:
                                return _NOT_FOUND
                        else:
                            return _NOT_FOUND
                    else:
                        # Can't navigate further into a scalar
                        return current if i == len(keys) - 1 else _NOT_FOUND
                
                return current
            
            # Regex: capture optional 'step' prefix, then number, then full dotted key path (e.g. "result.email")
            PLACEHOLDER_RE = r"\{\{(?:step)?(\d+)\.([a-zA-Z0-9_.]+)\}\}"
            
            def resolve_value(val):
                if isinstance(val, str):
                    # Exact match: entire value is one placeholder
                    exact_match = re.fullmatch(PLACEHOLDER_RE, val.strip())
                    if exact_match:
                        s_num = int(exact_match.group(1))
                        k = exact_match.group(2)
                        if s_num in results and results[s_num].get("success"):
                            resolved = _extract_from_data(results[s_num]["data"], k)
                            if resolved is not _NOT_FOUND:
                                logger.info(f"Interpolated {{{{step{s_num}.{k}}}}} -> {resolved}")
                                return resolved
                        logger.warning(f"Could not resolve {{{{step{s_num}.{k}}}}} — results keys: {list(results.keys())}")
                        return val
                            
                    # Embedded match: placeholder inside a larger string
                    def replace_match(match):
                        s_num = int(match.group(1))
                        k = match.group(2)
                        if s_num in results and results[s_num].get("success"):
                            resolved = _extract_from_data(results[s_num]["data"], k)
                            if resolved is not _NOT_FOUND:
                                return "" if resolved is None else str(resolved)
                        return match.group(0)
                        
                    return re.sub(PLACEHOLDER_RE, replace_match, val)
                elif isinstance(val, dict):
                    return {k: resolve_value(v) for k, v in val.items()}
                elif isinstance(val, list):
                    return [resolve_value(v) for v in val]
                return val
                
            interpolated_arguments = resolve_value(arguments)
            logger.info(f"Step {step_id} ({tool_name}): raw args = {arguments}")
            logger.info(f"Step {step_id} ({tool_name}): interpolated args = {interpolated_arguments}")
            
            # Guard: fail early if any placeholders remain unresolved
            def has_unresolved(val):
                if isinstance(val, str):
                    return "{{" in val and "}}" in val
                elif isinstance(val, dict):
                    return any(has_unresolved(v) for v in val.values())
                elif isinstance(val, list):
                    return any(has_unresolved(v) for v in val)
                return False
            
            if has_unresolved(interpolated_arguments):
                error_msg = f"Step {step_id}: unresolved placeholders in arguments: {interpolated_arguments}"
                logger.error(error_msg)
                state_machine.transition_to(ExecutionState.FAILED, error_msg)
                return {"status": "failed", "step": step_id, "reason": "unresolved_placeholders", "results": results}
            
            # Execute with retry
            is_safe = tool_schema.risk_level == "low"
            try:
                result = RetryPolicy.execute_with_retry(
                    func=self.mcp.execute_tool,
                    args=(tool_name, interpolated_arguments, execution_id),
                    is_safe_to_retry=is_safe
                )
                
                results[step_id] = {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error
                }
                
                logger.info(f"Step {step_id} result: success={result.success}, data={result.data}")
                
                if not result.success:
                    state_machine.transition_to(ExecutionState.FAILED, f"Step {step_id} failed: {result.error}")
                    return {"status": "failed", "step": step_id, "results": results}
                    
            except Exception as e:
                state_machine.transition_to(ExecutionState.FAILED, f"Step {step_id} exception: {str(e)}")
                return {"status": "failed", "step": step_id, "results": results}
                
        state_machine.transition_to(ExecutionState.COMPLETED)
        return {"status": "completed", "results": results}
