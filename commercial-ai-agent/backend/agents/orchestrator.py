import uuid
from typing import Dict, Any, List, Optional
from backend.agents.prompt_engineer import PromptEngineerAgent
from backend.agents.planner import PlannerAgent
from backend.agents.response_agent import ResponseAgent
from backend.execution.executor_improved import ExecutionEngine
from backend.execution.state_machine import StateMachine, ExecutionState
from backend.mcp.registry import registry
from backend.llm.router import ModelRouter
from backend.mcp.client import MCPClient

class Orchestrator:
    def __init__(self):
        self.router = ModelRouter()
        self.prompt_engineer = PromptEngineerAgent(self.router)
        self.planner = PlannerAgent(self.router)
        self.response_agent = ResponseAgent(self.router)
        self.mcp_client = MCPClient()
        self.executor = ExecutionEngine(self.mcp_client)
        
        # In memory state store for MVP. In prod, use DB.
        self.executions: Dict[str, Dict[str, Any]] = {}

    def process_request(self, user_input: str) -> Dict[str, Any]:
        """Main entry point for a new user request."""
        execution_id = str(uuid.uuid4())
        state_machine = StateMachine()
        
        # 1. Analyze Intent
        state_machine.transition_to(ExecutionState.ANALYZING)
        intent = self.prompt_engineer.analyze(user_input)
        
        # 2. Planning
        state_machine.transition_to(ExecutionState.PLANNING)
        available_tools = registry.get_planner_tools()
        plan = self.planner.plan(intent, available_tools)
        
        self.executions[execution_id] = {
            "execution_id": execution_id,
            "user_input": user_input,
            "intent": intent,
            "plan": plan,
            "state_machine": state_machine,
            "approved_step_ids": [],
            "results": {},
            "waiting_step_id": None,
        }
        
        # 3. Execution
        return self._run_execution(execution_id)

    def process_approval(self, execution_id: str, step_id: int, approved: bool) -> Dict[str, Any]:
        """Handle human approval and resume execution."""
        if execution_id not in self.executions:
            return {"error": "Execution not found"}
            
        execution = self.executions[execution_id]
        state_machine = execution["state_machine"]
        
        if state_machine.current_state != ExecutionState.WAITING_APPROVAL:
            return {"error": "Execution is not waiting for approval"}
        if execution["waiting_step_id"] != step_id:
            return {"error": "Approval does not match the pending step"}
        if not isinstance(approved, bool):
            return {"error": "approved must be a boolean"}
            
        if approved:
            if step_id not in execution["approved_step_ids"]:
                execution["approved_step_ids"].append(step_id)
            return self._run_execution(execution_id)
        else:
            state_machine.transition_to(ExecutionState.FAILED, "User rejected approval")
            return {
                "status": "failed",
                "execution_id": execution_id,
                "message": "Execution cancelled due to user rejection."
            }

    def _run_execution(self, execution_id: str) -> Dict[str, Any]:
        execution = self.executions[execution_id]
        state_machine = execution["state_machine"]
        
        result = self.executor.execute_plan(
            execution_id=execution_id,
            plan=execution["plan"],
            state_machine=state_machine,
            approved_step_ids=execution["approved_step_ids"],
            prior_results=execution["results"],
        )
        execution["results"] = result.get("results", result.get("results_so_far", execution["results"]))
        
        if state_machine.current_state == ExecutionState.COMPLETED:
            # 4. Generate Final Response
            final_response = self.response_agent.generate_response(
                execution["user_input"], 
                result["results"]
            )
            return {
                "status": "completed",
                "execution_id": execution_id,
                "response": final_response,
                "results": result["results"]
            }
        elif state_machine.current_state == ExecutionState.WAITING_APPROVAL:
            execution["waiting_step_id"] = result["step"]
            return {
                "status": "waiting_approval",
                "execution_id": execution_id,
                "step": result["step"],
                "tool": result["tool"],
                "arguments": result["arguments"]
            }
        else:
            execution["waiting_step_id"] = None
            # Failed
            final_response = self.response_agent.generate_response(
                execution["user_input"], 
                result
            )
            return {
                "status": "failed",
                "execution_id": execution_id,
                "response": final_response,
                "error": state_machine.error
            }
