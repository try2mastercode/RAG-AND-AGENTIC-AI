# ---------- SECTION 1: IMPORTS ----------
import os
import sys
import asyncio
from dotenv import load_dotenv
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console


# ---------- SECTION 2: MODEL CLIENT (Groq via its OpenAI-compatible endpoint) ----------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

model_client = OpenAIChatCompletionClient(
    model="qwen/qwen3.8-27b",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    # AutoGen only knows OpenAI/Anthropic/Gemini model families, so a Groq-hosted
    # model needs its capabilities declared by hand instead of auto-detected.
    model_info=ModelInfo(
        vision=False,
        function_calling=True,
        json_output=True,
        family="unknown",
        structured_output=False,
    ),
)


# ---------- SECTION 3: TWO AGENTS WITH DIFFERENT ROLES ----------
researcher = AssistantAgent(
    name="researcher",
    model_client=model_client,
    system_message=(
        "You are a researcher. Given a topic, list 3-4 short, concrete facts about it. "
        "Be terse, plain bullet points only, no fluff."
    ),
)

writer = AssistantAgent(
    name="writer",
    model_client=model_client,
    system_message=(
        "You are a writer. Using the researcher's facts, write a punchy 3-sentence "
        "product pitch. When your pitch is done, end the message with the word TERMINATE."
    ),
)


# ---------- SECTION 4: TEAM (agents take turns in a round robin) ----------
# Either the writer saying TERMINATE, or a 6-message safety cap, ends the chat.
termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(6)
team = RoundRobinGroupChat([researcher, writer], termination_condition=termination)


# ---------- SECTION 5: RUN ----------
async def main():
    await Console(team.run_stream(task="Topic: a solar-powered backpack for commuters."))
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
