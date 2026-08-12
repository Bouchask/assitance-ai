from backend.mcp.registry import registry
from backend.mcp.schemas import ToolSchema
from backend.mcp.document.tools import generate_document

def register_document_tools():
    registry.register_tool(
        ToolSchema(
            name="document.generate",
            description="Generate a PDF document (quote, invoice, proposal) based on structured content.",
            input_schema={
                "type": "object",
                "properties": {
                    "document_type": {"type": "string", "enum": ["quote"]},
                    "client_name": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "quantity": {"type": "number"},
                                "price": {"type": "number"}
                            }
                        }
                    },
                    "total_ht": {"type": "number"},
                    "tax": {"type": "number"},
                    "total_ttc": {"type": "number"},
                    "original_subtotal": {"type": "number"},
                    "discount_amount": {"type": "number"},
                    "discount_percent_val": {"type": "number"},
                    "template_name": {"type": "string"},
                    "additional_context": {"type": "object"},
                    "client_id": {"type": "integer"},
                    "reference_id": {"type": "integer"}
                },
                "required": ["document_type", "client_name", "items", "total_ht", "tax", "total_ttc"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "file_path": {"type": "string"},
                    "document_number": {"type": "string"},
                    "document_id": {"type": "integer"}
                }
            },
            risk_level="medium",
            requires_approval=False,
            handler=generate_document
        )
    )
