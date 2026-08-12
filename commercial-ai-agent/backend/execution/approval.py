from backend.mcp.schemas import ToolSchema

class ApprovalManager:
    @staticmethod
    def requires_approval(tool: ToolSchema) -> bool:
        """Determine if a tool execution requires human approval."""
        if tool.requires_approval or tool.risk_level in ("high", "critical"):
            return True
        return False
