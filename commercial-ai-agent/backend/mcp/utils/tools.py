import ast
import operator
from typing import Dict, Any, List


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _evaluate_expression(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate_expression(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_expression(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_expression(node.left)
        right = _evaluate_expression(node.right)
        if type(node.op) is ast.Pow and abs(right) > 10:
            raise ValueError("Exponent is too large")
        return _BINARY_OPERATORS[type(node.op)](left, right)
    raise ValueError("Only numeric arithmetic is allowed")

def calculate(expression: str) -> Dict[str, Any]:
    """Calculate the result of a mathematical expression."""
    try:
        parsed = ast.parse(expression, mode="eval")
        return {"result": float(_evaluate_expression(parsed))}
    except Exception as e:
        raise RuntimeError(f"Failed to evaluate expression: {str(e)}")

from collections import Counter

def prepare_quote_items(codes: List[str], quantities: Dict[str, int] = None, discount_percent: float = 0.0, tax_rate: float = 0.20) -> Dict[str, Any]:
    """Look up product codes, apply a discount and tax, and format the output for document generation."""
    from backend.mcp.database.tools import get_services
    
    quantities = quantities or {}
    code_counts = Counter(codes)
    services = get_services(list(code_counts.keys()))
    if not services:
        raise ValueError(f"No catalogue products match the requested codes: {', '.join(codes)}")
        
    items = []
    subtotal = 0.0
    
    for s in services:
        qty = quantities.get(s["code"], code_counts[s["code"]])
        price = s.get("unit_price", 0.0)
        line_total = price * qty
        items.append({
            "service_id": s["id"],
            "code": s["code"],
            "description": s.get("name", "Unknown"),
            "quantity": qty,
            "price": price,
            "line_total": line_total,
            "tax_rate": s.get("tax_rate", tax_rate),
        })
        subtotal += line_total
        
    # Apply discount
    discount_amount = subtotal * discount_percent
    subtotal_discounted = subtotal - discount_amount
    tax = subtotal_discounted * tax_rate
    total = subtotal_discounted + tax
    
    return {
        "items": items,
        "original_subtotal": subtotal,
        "discount_amount": discount_amount,
        "discount_percent_val": discount_percent * 100,
        "total_ht": subtotal_discounted,
        "tax": tax,
        "total_ttc": total
    }
