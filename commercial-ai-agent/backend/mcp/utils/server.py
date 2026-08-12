from backend.mcp.registry import registry
from backend.mcp.schemas import ToolSchema
from backend.mcp.utils.tools import calculate, prepare_quote_items

def register_utils_tools():
    registry.register_tool(
        ToolSchema(
            name="utils.calculate",
            description="Evaluate a mathematical expression (e.g. '120000 + 25000' or '145000 * 1.2'). Returns the float result.",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The mathematical expression to evaluate."}
                },
                "required": ["expression"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "number"}
                }
            },
            risk_level="low",
            requires_approval=False,
            handler=calculate
        )
    )
    
    registry.register_tool(
        ToolSchema(
            name="utils.prepare_quote_items",
            description="Look up a list of product codes from the database, aggregate them into a list of items, apply a discount percentage (e.g. 0.15 for 15%), and calculate taxes. Use this to prepare dynamic item lists for the quote and document generator.",
            input_schema={
                "type": "object",
                "properties": {
                    "codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of product codes (e.g. ['WEB-ECOMM', 'SEO-OPT']). To specify quantities > 1, either pass the code multiple times, or use the 'quantities' dictionary."
                    },
                    "quantities": {
                        "type": "object",
                        "additionalProperties": {"type": "integer"},
                        "description": "Optional mapping of product codes to quantities (e.g. {'SEO-OPT': 2}). If omitted, quantities default to 1 (or the number of times the code appears in 'codes')."
                    },
                    "discount_percent": {
                        "type": "number",
                        "description": "Discount as a decimal (e.g. 0.15 for 15%). Default is 0.0."
                    },
                    "tax_rate": {
                        "type": "number",
                        "description": "Tax rate as a decimal (e.g. 0.20 for 20%). Default is 0.20."
                    }
                },
                "required": ["codes"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "items": {"type": "array"},
                    "original_subtotal": {"type": "number"},
                    "discount_amount": {"type": "number"},
                    "discount_percent_val": {"type": "number"},
                    "total_ht": {"type": "number"},
                    "tax": {"type": "number"},
                    "total_ttc": {"type": "number"}
                }
            },
            risk_level="low",
            requires_approval=False,
            handler=prepare_quote_items
        )
    )
