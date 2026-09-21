# ---------- SECTION 1: IMPORTS ----------
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_SCRIPT = Path(__file__).parent / "03_server_resources_and_prompts.py"
server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_SCRIPT)])


# ---------- SECTION 2: DISCOVER AND READ RESOURCES ----------
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            resources = await session.list_resources()
            print("Static resources:")
            for r in resources.resources:
                print(f"  - {r.uri}")

            templates = await session.list_resource_templates()
            print("\nResource templates:")
            for t in templates.resourceTemplates:
                print(f"  - {t.uriTemplate}")

            info = await session.read_resource("config://server-info")
            print("\nconfig://server-info ->", info.contents[0].text)

            # A template resource is fetched by filling in the placeholder.
            greeting = await session.read_resource("greeting://Tharun")
            print("greeting://Tharun ->", greeting.contents[0].text)

            # ---------- SECTION 3: DISCOVER AND RENDER A PROMPT ----------
            prompts = await session.list_prompts()
            print("\nPrompts:")
            for p in prompts.prompts:
                print(f"  - {p.name}: {p.description}")

            rendered = await session.get_prompt(
                "summarize_request", {"topic": "the Model Context Protocol", "tone": "playful"}
            )
            print("\nRendered prompt messages:")
            for msg in rendered.messages:
                print(f"  [{msg.role}] {msg.content.text}")


if __name__ == "__main__":
    asyncio.run(main())
