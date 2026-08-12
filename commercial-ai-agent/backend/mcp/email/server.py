from backend.mcp.registry import registry
from backend.mcp.schemas import ToolSchema
from backend.mcp.email.tools import prepare_email, send_email

def register_email_tools():
    registry.register_tool(
        ToolSchema(
            name="email.prepare",
            description="Prepare an email to be sent. Use this to format the email payload before requesting to send it.",
            input_schema={
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "attachments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to attach."
                    }
                },
                "required": ["to", "subject", "body"]
            },
            output_schema={
                "type": "object",
                "additionalProperties": True
            },
            risk_level="low",
            requires_approval=False,
            handler=prepare_email
        )
    )

    registry.register_tool(
        ToolSchema(
            name="email.send",
            description="Send an email to a recipient. This requires human approval.",
            input_schema={
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "attachments": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["to", "subject", "body"]
            },
            output_schema={
                "type": "object",
                "additionalProperties": True
            },
            risk_level="high",
            requires_approval=True,
            handler=send_email
        )
    )
