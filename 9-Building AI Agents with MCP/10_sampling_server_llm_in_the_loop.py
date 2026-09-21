# ---------- SECTION 1: IMPORTS ----------
import mcp.types as types
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("sampling-server")


# ---------- SECTION 2: SAMPLING - THE SERVER ASKS *THE CLIENT* FOR A COMPLETION ----------
# Every earlier example had the CLIENT hold the LLM and call tools on the
# server. Sampling reverses that: a tool can ask the connected client to run
# an LLM completion on its behalf via ctx.session.create_message(), without
# the server needing its own API key or model. The client decides whether to
# honor the request (see the sampling_callback in the paired client file).
@mcp.tool()
async def summarize_note(ctx: Context, note_text: str) -> str:
    """Ask the connected client's LLM to summarize a note in one sentence."""
    result = await ctx.session.create_message(
        messages=[
            types.SamplingMessage(
                role="user",
                content=types.TextContent(
                    type="text", text=f"Summarize this note in one sentence:\n\n{note_text}"
                ),
            )
        ],
        max_tokens=100,
    )
    return result.content.text


if __name__ == "__main__":
    mcp.run(transport="stdio")
