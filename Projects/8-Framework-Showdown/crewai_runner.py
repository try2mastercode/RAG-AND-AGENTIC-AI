"""Runs inside the C:\\v8\\crewai Python 3.11 venv, launched as a subprocess by
app.py. CrewAI's dependency chain (pydantic<2.13) conflicts with BeeAI's
(pydantic-core>=2.46.5), so the two can't share an interpreter — this script
is the isolation boundary. Talks to app.py over stdin/stdout JSON only.
"""
import json
import os
import sys

os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")  # skip the interactive "share this trace?" prompt

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
import crewai.llms.cache as _crewai_cache

# CrewAI tags every message with an Anthropic-style "cache_breakpoint" flag and
# only strips it for its native providers. Groq isn't one, so the raw flag
# reaches Groq's API and gets rejected as an unknown field.
_crewai_cache.mark_cache_breakpoint = lambda message: message

load_dotenv()


def run(topic: str) -> dict:
    llm = LLM(model="groq/qwen/qwen3.8-27b", api_key=os.getenv("GROQ_API_KEY"), temperature=0)

    researcher = Agent(
        role="Researcher",
        goal=f"Find 3-4 short, concrete facts about: {topic}",
        backstory="A terse market analyst who deals only in specifics, never fluff.",
        llm=llm,
        verbose=False,
    )
    writer = Agent(
        role="Writer",
        goal="Turn the researcher's facts into a punchy pitch.",
        backstory="A copywriter who writes tight, 3-sentence product pitches.",
        llm=llm,
        verbose=False,
    )

    research_task = Task(
        description=f"List 3-4 short, concrete facts about: {topic}.",
        expected_output="A short bullet list of facts.",
        agent=researcher,
    )
    write_task = Task(
        description="Using the facts above, write a punchy 3-sentence product pitch.",
        expected_output="A 3-sentence product pitch.",
        agent=writer,
        context=[research_task],
    )

    crew = Crew(agents=[researcher, writer], tasks=[research_task, write_task], process=Process.sequential, verbose=False)
    pitch = crew.kickoff()
    return {"research": str(research_task.output), "pitch": str(pitch)}


if __name__ == "__main__":
    payload = json.loads(sys.argv[1])
    print(json.dumps(run(payload["topic"])))
