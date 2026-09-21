# ---------- SECTION 1: IMPORTS ----------
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("resources-and-prompts-server")


# ---------- SECTION 2: A STATIC RESOURCE ----------
# Resources are read-only data a client can fetch by URI, without an LLM
# deciding to "call" anything. Good for docs, config, reference data.
@mcp.resource("config://server-info")
def server_info() -> str:
    """Static metadata about this server."""
    return "name=resources-and-prompts-server; version=1.0; author=tharun"


# ---------- SECTION 3: A TEMPLATED (DYNAMIC) RESOURCE ----------
# The {name} placeholder makes this a resource TEMPLATE: the client can ask
# for greeting://Alice, greeting://Bob, etc., and this function is called
# with name="Alice" to build that specific resource on demand.
@mcp.resource("greeting://{name}")
def personalized_greeting(name: str) -> str:
    """A greeting resource, generated per-name."""
    return f"Welcome back, {name}. This text was fetched as an MCP resource, not a tool call."


# ---------- SECTION 4: A PROMPT TEMPLATE ----------
# Prompts are reusable, parameterized message templates a client's UI can
# surface to a user (e.g. a slash command), which then get sent to an LLM.
@mcp.prompt()
def summarize_request(topic: str, tone: str = "concise") -> str:
    """Build a prompt asking for a summary of `topic` in a given tone."""
    return f"Write a {tone} summary about: {topic}"


# ---------- SECTION 5: RUN ----------
if __name__ == "__main__":
    mcp.run(transport="stdio")
