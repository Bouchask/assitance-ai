from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Callable


class ToolInputValidationError(ValueError):
    """Raised when an agent-generated tool call does not match its contract."""


def validate_tool_arguments(arguments: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Small, dependency-free validator for the JSON-schema subset used by MCP tools.

    Tool contracts are generated into the planner prompt, but they must also be
    enforced at the execution boundary.  This intentionally supports only the
    constructs used in this project (objects, arrays, primitive types and enum).
    """
    if not isinstance(arguments, dict):
        raise ToolInputValidationError("Tool arguments must be an object")

    properties = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in arguments or arguments[name] is None:
            raise ToolInputValidationError(f"Missing required argument: {name}")

    if schema.get("additionalProperties") is False:
        unknown = set(arguments) - set(properties)
        if unknown:
            raise ToolInputValidationError(f"Unsupported argument(s): {', '.join(sorted(unknown))}")

    def validate_value(value: Any, value_schema: Dict[str, Any], path: str, parent: dict, key: str) -> None:
        if value is None:
            return
        expected = value_schema.get("type")
        
        # Implicit coercion for array when string is provided
        if expected == "array" and isinstance(value, str):
            if not value.strip() or value.strip().lower() == "none" or value.strip() == "[]":
                value = []
                parent[key] = value
            else:
                # Try parsing as JSON list, otherwise wrap in list
                import json
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        value = parsed
                    else:
                        value = [value]
                except json.JSONDecodeError:
                    value = [value]
                parent[key] = value

        # Implicit coercion for integer/number when string is provided
        if expected in ("integer", "number") and isinstance(value, str):
            try:
                if expected == "integer":
                    value = int(value)
                else:
                    value = float(value)
                parent[key] = value
            except (ValueError, TypeError):
                pass # let the validator fail later
                
        valid = {
            "string": isinstance(value, str),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
            "array": isinstance(value, list),
            "object": isinstance(value, dict),
        }
        if expected and not valid.get(expected, True):
            raise ToolInputValidationError(f"{path} must be a {expected}")
        if "enum" in value_schema and value not in value_schema["enum"]:
            raise ToolInputValidationError(f"{path} must be one of {value_schema['enum']}")
        if expected == "array":
            item_schema = value_schema.get("items", {})
            for index, item in enumerate(value):
                # Note: nested coercion not strictly required, passing a dummy dict/key for now
                dummy = {str(index): item}
                validate_value(item, item_schema, f"{path}[{index}]", dummy, str(index))
                value[index] = dummy[str(index)]
        elif expected == "object":
            for k, nested_schema in value_schema.get("properties", {}).items():
                if k in value:
                    validate_value(value[k], nested_schema, f"{path}.{k}", value, k)

    for name, value in arguments.items():
        if name in properties:
            validate_value(value, properties[name], name, arguments, name)

class ToolParameter(BaseModel):
    type: str
    description: str
    required: bool = True

class ToolSchema(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    risk_level: str = "low" # low, medium, high, critical
    requires_approval: bool = False
    required_permission: Optional[str] = None
    
    # Internal callback function for the execution engine to invoke
    handler: Optional[Callable] = None

class ToolResult(BaseModel):
    success: bool
    tool: str
    execution_id: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
