import uuid
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.prompt_engineer import PromptEngineerAgent
from backend.agents.planner import PlannerAgent
from backend.agents.response_agent import ResponseAgent
from backend.execution.executor import ExecutionEngine
from backend.execution.state_machine import StateMachine, ExecutionState
from backend.mcp.registry import registry
from backend.llm.router import ModelRouter
from backend.mcp.client import MCPClient

class AgentState(TypedDict):
    execution_id: str
    user_input: str
    intent: Dict[str, Any]
    plan: Dict[str, Any]
    results: Dict[int, Dict[str, Any]]
    approved_step_ids: List[int]
    status: str
    error: str
    pending_approval: Dict[str, Any]
    final_response: str
    execution_state: str

class LangGraphOrchestrator:
    def __init__(self):
        self.router = ModelRouter()
        self.prompt_engineer = PromptEngineerAgent(self.router)
        self.planner = PlannerAgent(self.router)
        self.response_agent = ResponseAgent(self.router)
        self.mcp_client = MCPClient()
        self.executor = ExecutionEngine(self.mcp_client)
        
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("analyze", self._node_analyze)
        workflow.add_node("plan", self._node_plan)
        workflow.add_node("execute", self._node_execute)
        workflow.add_node("generate_response", self._node_generate_response)
        workflow.add_node("wait_for_approval", self._node_wait_for_approval)
        
        workflow.add_edge(START, "analyze")
        workflow.add_edge("analyze", "plan")
        workflow.add_edge("plan", "execute")
        
        def route_execution(state: AgentState):
            return state.get("status")
            
        workflow.add_conditional_edges(
            "execute",
            route_execution,
            {
                "completed": "generate_response",
                "waiting_approval": "wait_for_approval",
                "failed": "generate_response"
            }
        )
        
        # After waiting for approval, we always loop back to execute
        workflow.add_edge("wait_for_approval", "execute")
        workflow.add_edge("generate_response", END)
        
        # We interrupt execution BEFORE entering the 'wait_for_approval' node
        # This allows the Flask app to return control to the UI
        return workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=["wait_for_approval"]
        )

    def _node_analyze(self, state: AgentState):
        if state.get("intent"):
            return state
        intent = self.prompt_engineer.analyze(state["user_input"])
        state["intent"] = intent
        return state

    def _node_plan(self, state: AgentState):
        if state.get("plan"):
            return state
        available_tools = registry.get_planner_tools()
        plan = self.planner.plan(state["intent"], available_tools)
        state["plan"] = plan
        return state

    def _node_execute(self, state: AgentState):
        # Checkpoints are serialized by LangGraph, so keep only primitive
        # state in AgentState.  A StateMachine is reconstructed for each run.
        try:
            previous_state = ExecutionState(state.get("execution_state", ExecutionState.RECEIVED.value))
        except ValueError:
            previous_state = ExecutionState.RECEIVED
        sm = StateMachine(previous_state)
            
        result = self.executor.execute_plan(
            execution_id=state["execution_id"],
            plan=state["plan"],
            state_machine=sm,
            approved_step_ids=state.get("approved_step_ids", []),
            prior_results=state.get("results", {})
        )
        
        if sm.current_state == ExecutionState.COMPLETED:
            state["status"] = "completed"
            state["results"] = result.get("results", {})
        elif sm.current_state == ExecutionState.WAITING_APPROVAL:
            state["status"] = "waiting_approval"
            state["results"] = result.get("results_so_far", state.get("results", {}))
            state["pending_approval"] = {
                "step": result["step"],
                "tool": result["tool"],
                "arguments": result["arguments"]
            }
        else:
            state["status"] = "failed"
            state["error"] = sm.error

        state["execution_state"] = sm.current_state.value
        
        return state

    def _node_wait_for_approval(self, state: AgentState):
        # This is a dummy node. Execution pauses BEFORE entering this node.
        # When we resume, it simply passes through back to 'execute'.
        return state

    def _node_generate_response(self, state: AgentState):
        if state.get("status") == "completed":
            final = self.response_agent.generate_response(state["user_input"], state.get("results", []))
        else:
            final = self.response_agent.generate_response(state["user_input"], {"error": state.get("error", "Unknown error")})
        state["final_response"] = final
        return state

    def process_request(self, user_input: str, thread_id: str = None) -> Dict[str, Any]:
        execution_id = thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": execution_id}}
        
        initial_state = {
            "execution_id": execution_id,
            "user_input": user_input,
            "intent": {},
            "plan": {},
            "results": {},
            "approved_step_ids": [],
            "status": "",
            "error": "",
            "pending_approval": {},
            "final_response": "",
            "execution_state": ExecutionState.RECEIVED.value
        }
        
        result_state = self.graph.invoke(initial_state, config)
        return self._format_response(result_state, execution_id)

    def process_approval(self, execution_id: str, step_id: int, approved: bool) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": execution_id}}
        state_snapshot = self.graph.get_state(config)
        
        if not state_snapshot or not state_snapshot.values:
            return {"error": "Execution not found"}
            
        state = dict(state_snapshot.values)
        if state.get("status") != "waiting_approval":
            return {"error": "Execution is not waiting for approval"}
        if state.get("pending_approval", {}).get("step") != step_id:
            return {"error": "Approval does not match the pending step"}
        if not isinstance(approved, bool):
            return {"error": "approved must be a boolean"}
            
        if approved:
            approved_steps = state.get("approved_step_ids", [])
            if step_id not in approved_steps:
                approved_steps.append(step_id)
            
            # Update the graph state with the new approved steps
            self.graph.update_state(config, {"approved_step_ids": approved_steps})
            
            # Resume execution (it will enter 'wait_for_approval' and then loop to 'execute')
            result_state = self.graph.invoke(None, config)
            return self._format_response(result_state, execution_id)
        else:
            # If rejected, we update the state directly to failed and run it to generate response
            self.graph.update_state(config, {"status": "failed", "error": "User rejected approval"})
            result_state = self.graph.invoke(None, config)
            return {
                "status": "failed",
                "execution_id": execution_id,
                "message": "Execution cancelled due to user rejection."
            }

    def _format_response(self, state: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        if state.get("status") == "completed":
            return {
                "status": "completed",
                "execution_id": execution_id,
                "response": state.get("final_response", ""),
                "results": state.get("results", [])
            }
        elif state.get("status") == "waiting_approval":
            pending = state.get("pending_approval", {})
            return {
                "status": "waiting_approval",
                "execution_id": execution_id,
                "step": pending.get("step"),
                "tool": pending.get("tool"),
                "arguments": pending.get("arguments")
            }
        else:
            return {
                "status": "failed",
                "execution_id": execution_id,
                "response": state.get("final_response", ""),
                "error": state.get("error", "Unknown error")
            }
