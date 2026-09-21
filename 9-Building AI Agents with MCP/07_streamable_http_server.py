# ---------- SECTION 1: IMPORTS ----------
from mcp.server.fastmcp import FastMCP


# ---------- SECTION 2: SAME TOOLS, DIFFERENT TRANSPORT ----------
# Everything so far ran over stdio: the client OWNED the server as a
# subprocess. Streamable HTTP flips that - this server is a standalone
# network service other processes (even on other machines) can connect to,
# the same way a real hosted MCP server (e.g. a SaaS tool provider) works.
mcp = FastMCP("http-server", host="127.0.0.1", port=8765)


@mcp.tool()
def word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())


@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


# ---------- SECTION 3: RUN AS AN HTTP SERVICE ----------
# Run this file directly and leave it running, THEN run
# 08_streamable_http_client.py in a separate terminal to connect to it.
if __name__ == "__main__":
    print("Serving MCP over Streamable HTTP at http://127.0.0.1:8765/mcp")
    mcp.run(transport="streamable-http")
