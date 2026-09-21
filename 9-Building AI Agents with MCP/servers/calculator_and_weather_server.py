# ---------- SECTION 1: IMPORTS ----------
import ast
import operator

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-and-weather-server")


# ---------- SECTION 2: A SAFE ARITHMETIC TOOL ----------
# eval() would let a model run arbitrary code; walking the parsed AST and only
# allowing a fixed set of numeric operators keeps this safe to expose to an LLM.
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("unsupported expression")


@mcp.tool()
def calculate(expression: str) -> float:
    """Evaluate a plain arithmetic expression, e.g. '12 * (3 + 4)'. No variables or functions."""
    return _safe_eval(ast.parse(expression, mode="eval").body)


# ---------- SECTION 3: A MOCK WEATHER TOOL ----------
# Standing in for a real weather API (so this runs with no extra key) - the
# concept being taught is the MCP wiring, not the weather data itself.
_WEATHER = {
    "chennai": {"condition": "Humid", "temp_c": 32},
    "bangalore": {"condition": "Pleasant", "temp_c": 24},
    "delhi": {"condition": "Hazy", "temp_c": 29},
}


@mcp.tool()
def get_weather(city: str) -> dict:
    """Get mock current weather for a city (chennai, bangalore, or delhi)."""
    return _WEATHER.get(city.lower(), {"condition": "unknown", "temp_c": None})


if __name__ == "__main__":
    mcp.run(transport="stdio")
