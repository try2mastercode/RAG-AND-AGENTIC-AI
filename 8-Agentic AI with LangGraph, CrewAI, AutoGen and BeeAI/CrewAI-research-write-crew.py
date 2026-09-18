# ---------- SECTION 1: IMPORTS ----------
import os
import sys

os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")  # skip the interactive "share this trace?" prompt

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
import crewai.llms.cache as _crewai_cache

# CrewAI tags every message with an Anthropic-style "cache_breakpoint" flag and
# only strips it for its native providers. Groq isn't one, so the raw flag
# reaches Groq's API and gets rejected as an unknown field. Since Groq has no
# such caching feature to opt into anyway, disabling the tag is a safe no-op.
_crewai_cache.mark_cache_breakpoint = lambda message: message


# ---------- SECTION 2: MODEL (Groq, via CrewAI's LiteLLM-based LLM class) ----------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

llm = LLM(model="groq/qwen/qwen3.8-27b", api_key=os.getenv("GROQ_API_KEY"), temperature=0)


# ---------- SECTION 3: AGENTS (role, goal, backstory shape how each one behaves) ----------
researcher = Agent(
    role="Researcher",
    goal="Find 3-4 short, concrete facts about the given product idea.",
    backstory="A terse market analyst who deals only in specifics, never fluff.",
    llm=llm,
    verbose=True,
)

writer = Agent(
    role="Writer",
    goal="Turn the researcher's facts into a punchy pitch.",
    backstory="A copywriter who writes tight, 3-sentence product pitches.",
    llm=llm,
    verbose=True,
)


# ---------- SECTION 4: TASKS (the write task gets the research task's output as context) ----------
research_task = Task(
    description="List 3-4 short, concrete facts about: a solar-powered backpack for commuters.",
    expected_output="A short bullet list of facts.",
    agent=researcher,
)

write_task = Task(
    description="Using the facts above, write a punchy 3-sentence product pitch.",
    expected_output="A 3-sentence product pitch.",
    agent=writer,
    context=[research_task],
)


# ---------- SECTION 5: CREW (sequential process: research_task runs, then write_task) ----------
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n=== FINAL PITCH ===\n", result)
