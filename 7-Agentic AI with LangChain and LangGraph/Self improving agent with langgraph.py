# Self-improving agent: run this file top to bottom, read the section you're on.


# ---------- SECTION 1: IMPORTS ----------
import os
import json
import operator
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"
HAVE_KEY = bool(os.getenv("GROQ_API_KEY"))

LESSONS_FILE = os.path.join(os.path.dirname(__file__), "self_improvement_lessons.json")
MAX_ITERATIONS = 3
SCORE_THRESHOLD = 8


# ---------- SECTION 2: THE CORE IDEA ----------
# Two feedback loops, nested:
#  - within one run: generate -> critique -> revise, looping until the score clears
#    the threshold or MAX_ITERATIONS is hit (a "reflection" agent).
#  - across runs: the final critique gets appended to a JSON file on disk, and every
#    future run reads that file and feeds the accumulated lessons back into the very
#    first draft, so the agent's starting point improves run over run.


# ---------- SECTION 3: STATE ----------
class AgentState(TypedDict):
    task: str
    draft: str
    critique: str
    score: int
    iteration: int
    history: Annotated[list[str], operator.add]


# ---------- SECTION 4: STRUCTURED CRITIC OUTPUT ----------
class Critique(BaseModel):
    score: int = Field(description="Quality score from 1 (bad) to 10 (excellent)")
    feedback: str = Field(description="Specific, actionable feedback on how to improve the draft")


# ---------- SECTION 5: PERSISTENT LESSON MEMORY ----------
def load_lessons() -> list[str]:
    if not os.path.exists(LESSONS_FILE):
        return []
    with open(LESSONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_lesson(feedback: str) -> None:
    lessons = load_lessons()
    lessons.append(feedback)
    with open(LESSONS_FILE, "w", encoding="utf-8") as f:
        json.dump(lessons, f, indent=2)


# ---------- SECTION 6: NODES ----------
def generate_node(state: AgentState) -> AgentState:
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0.7)

    if state["iteration"] == 0:
        lessons = load_lessons()[-5:]  # only the most recent lessons, so the prompt stays short
        lesson_block = "\n".join(f"- {lesson}" for lesson in lessons) if lessons else "None yet."
        prompt = f"Lessons from past attempts on similar tasks:\n{lesson_block}\n\nTask: {state['task']}"
    else:
        prompt = (
            f"Task: {state['task']}\n\nYour previous draft:\n{state['draft']}\n\n"
            f"Feedback to address:\n{state['critique']}\n\nWrite an improved draft."
        )

    response = llm.invoke([HumanMessage(prompt)])
    next_iteration = state["iteration"] + 1
    return {
        "draft": response.content,
        "iteration": next_iteration,
        "history": [f"iteration {next_iteration}: draft generated"],
    }


def critique_node(state: AgentState) -> AgentState:
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0).with_structured_output(Critique)
    result = llm.invoke([HumanMessage(
        f"Task: {state['task']}\n\nDraft:\n{state['draft']}\n\n"
        "Score this draft from 1-10 and give specific, actionable feedback."
    )])
    return {
        "score": result.score,
        "critique": result.feedback,
        "history": [f"iteration {state['iteration']}: scored {result.score}/10 - {result.feedback}"],
    }


def finish_node(state: AgentState) -> AgentState:
    save_lesson(state["critique"])   # feeds the next run's generate_node, even for a different task
    return {}


# ---------- SECTION 7: ROUTER + GRAPH ASSEMBLY ----------
def should_continue(state: AgentState) -> str:
    if state["score"] >= SCORE_THRESHOLD or state["iteration"] >= MAX_ITERATIONS:
        return "finish"
    return "revise"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("generate", generate_node)
    graph.add_node("critique", critique_node)
    graph.add_node("finish", finish_node)
    graph.add_edge(START, "generate")
    graph.add_edge("generate", "critique")
    graph.add_conditional_edges("critique", should_continue, {"revise": "generate", "finish": "finish"})
    graph.add_edge("finish", END)
    return graph.compile()


# ---------- SECTION 8: DEMO ----------
def run_self_improving_agent(task: str):
    if not HAVE_KEY:
        print("Skipped (no GROQ_API_KEY): run_self_improving_agent")
        return
    app = build_graph()
    result = app.invoke({"task": task, "draft": "", "critique": "", "score": 0, "iteration": 0, "history": []})

    for line in result["history"]:
        print(line)
    print("\nFinal draft:\n", result["draft"])
    print(f"\nFinal score: {result['score']}/10")
    print(f"Lessons saved so far: {len(load_lessons())}")


def main():
    run_self_improving_agent("Write a two-sentence pitch for a plant-watering reminder app.")


if __name__ == "__main__":
    main()
