from backend.mcp.registry import registry
from backend.mcp.schemas import ToolSchema
from backend.mcp.spreadsheet.tools import search_spreadsheet

def register_spreadsheet_tools():
    registry.register_tool(
        ToolSchema(
            name="spreadsheet.search",
            description="Search an Excel or CSV file for rows matching a query.",
            input_schema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Absolute or relative path to the spreadsheet file."},
                    "query_column": {"type": "string", "description": "Column name to search in."},
                    "query_value": {"type": "string", "description": "Value to search for in the column."}
                },
                "required": ["filepath", "query_column", "query_value"]
            },
            output_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": True
                }
            },
            risk_level="low",
            requires_approval=False,
            handler=search_spreadsheet
        )
    )
