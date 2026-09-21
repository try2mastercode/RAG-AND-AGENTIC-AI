# ---------- SECTION 1: IMPORTS ----------
from mcp.server.fastmcp import FastMCP


# ---------- SECTION 2: SERVER INSTANCE ----------
# The name shows up in client logs / MCP inspector; it has no other effect.
mcp = FastMCP("intro-server")


# ---------- SECTION 3: TOOLS ----------
# @mcp.tool turns a plain function into something an LLM-driven client can
# discover and call. The docstring + type hints become the tool's JSON schema.
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """Return a friendly greeting for the given name."""
    return f"Hello, {name}! This greeting came from an MCP tool call."


# ---------- SECTION 4: RUN ----------
# transport="stdio" means this process talks MCP over its own stdin/stdout.
# It is meant to be launched BY a client (see 02_first_mcp_client.py), not run
# directly and left sitting in a terminal.
if __name__ == "__main__":
    mcp.run(transport="stdio")
