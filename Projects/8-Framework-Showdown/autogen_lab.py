"""Runs in-process (same Python 3.14 interpreter as app.py) — unlike CrewAI
and BeeAI, autogen-agentchat has no dependency conflict on this machine, so
it needs no venv subprocess isolation.
"""
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient


async def run_autogen_chat(topic: str) -> dict:
    model_client = OpenAIChatCompletionClient(
        model="qwen/qwen3.8-27b",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        # AutoGen only knows OpenAI/Anthropic/Gemini model families, so a
        # Groq-hosted model needs its capabilities declared by hand.
        model_info=ModelInfo(vision=False, function_calling=True, json_output=True, family="unknown", structured_output=False),
    )

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

    # Either the writer saying TERMINATE, or a 6-message safety cap, ends the chat.
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(6)
    team = RoundRobinGroupChat([researcher, writer], termination_condition=termination)

    turns = []
    stop_reason = None
    try:
        async for message in team.run_stream(task=f"Topic: {topic}"):
            if isinstance(message, TaskResult):
                stop_reason = message.stop_reason
                continue
            turns.append({"agent": getattr(message, "source", "?"), "text": str(getattr(message, "content", message))})
    finally:
        await model_client.close()

    return {"turns": turns, "stop_reason": stop_reason}
