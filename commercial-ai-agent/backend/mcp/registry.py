from typing import Dict, List, Optional
from backend.mcp.schemas import ToolSchema

class MCPRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolSchema] = {}

    def register_tool(self, tool: ToolSchema):
        """Register a tool with its schema and handler."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolSchema]:
        """Get a registered tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[ToolSchema]:
        """List all registered tools."""
        return list(self._tools.values())
        
    def get_planner_tools(self) -> List[Dict]:
        """Format the registered tools for the Planner LLM prompt."""
        tools = []
        for tool in self.list_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })
        return tools

# Global registry instance
registry = MCPRegistry()
