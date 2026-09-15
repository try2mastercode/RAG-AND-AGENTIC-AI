# Reflexion agent: run this file top to bottom, read the section you're on.


# ---------- SECTION 1: IMPORTS ----------
import os
import re
import sys
import operator
import subprocess
import tempfile
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"
HAVE_KEY = bool(os.getenv("GROQ_API_KEY"))

MAX_TRIALS = 4


# ---------- SECTION 2: HOW THIS DIFFERS FROM PLAIN REFLECTION ----------
# The reflection agent in this folder scores its own output with an LLM judge and only
# ever carries the single latest critique forward. Reflexion (Shinn et al., 2023) is
# stricter about two things:
#   - the evaluator is a REAL, external, verifiable signal when one exists (here: actually
#     running the code against unit tests) instead of an LLM's opinion of quality.
#   - the self-reflection text ACCUMULATES in an episodic memory for this task, and every
#     past reflection (not just the last one) is fed back into the actor on the next trial.


# ---------- SECTION 3: STATE ----------
class ReflexionState(TypedDict):
    task: str
    tests: list[str]
    code: str
    test_output: str
    passed: bool
    reflections: Annotated[list[str], operator.add]   # episodic memory: every past reflection, kept
    trial: int


# ---------- SECTION 4: ACTOR (writes/rewrites the code) ----------
def extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def actor_node(state: ReflexionState) -> ReflexionState:
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0.3)

    if state["reflections"]:
        memory = "\n".join(f"- {r}" for r in state["reflections"])
        prompt = (
            f"Task: {state['task']}\n\n"
            f"Reflections from your past failed attempts on THIS task:\n{memory}\n\n"
            "Write a new, corrected implementation that addresses every reflection above. "
            "Respond with only a python code block, nothing else."
        )
    else:
        prompt = f"Task: {state['task']}\n\nRespond with only a python code block, nothing else."

    response = llm.invoke([SystemMessage("You are a careful Python programmer."), HumanMessage(prompt)])
    return {"code": extract_code(response.content), "trial": state["trial"] + 1}


# ---------- SECTION 5: EVALUATOR (real signal: run the tests, don't ask an LLM to guess) ----------
def evaluator_node(state: ReflexionState) -> ReflexionState:
    script = state["code"] + "\n\n" + "\n".join(state["tests"]) + "\nprint('ALL TESTS PASSED')\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        path = f.name

    try:
        result = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=10)
        output = (result.stdout + result.stderr).strip()
        passed = result.returncode == 0 and "ALL TESTS PASSED" in result.stdout
    except subprocess.TimeoutExpired:
        output, passed = "Execution timed out after 10s.", False
    finally:
        os.remove(path)

    return {"test_output": output, "passed": passed}


# ---------- SECTION 6: SELF-REFLECTION (verbal feedback added to episodic memory) ----------
def reflect_node(state: ReflexionState) -> ReflexionState:
    llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)
    prompt = (
        f"Task: {state['task']}\n\nCode that was tried:\n{state['code']}\n\n"
        f"Test run output:\n{state['test_output']}\n\n"
        "In 1-3 sentences, explain what specifically caused the failure and what to change next time."
    )
    response = llm.invoke([HumanMessage(prompt)])
    return {"reflections": [response.content.strip()]}


# ---------- SECTION 7: ROUTER + GRAPH ASSEMBLY ----------
def should_continue(state: ReflexionState) -> str:
    if state["passed"] or state["trial"] >= MAX_TRIALS:
        return "finish"
    return "reflect"


def build_graph():
    graph = StateGraph(ReflexionState)
    graph.add_node("actor", actor_node)
    graph.add_node("evaluate", evaluator_node)
    graph.add_node("reflect", reflect_node)
    graph.add_edge(START, "actor")
    graph.add_edge("actor", "evaluate")
    graph.add_conditional_edges("evaluate", should_continue, {"reflect": "reflect", "finish": END})
    graph.add_edge("reflect", "actor")
    return graph.compile()


# ---------- SECTION 8: DEMO ----------
TASK = "Write a Python function `is_palindrome(s: str) -> bool` that returns True if s is a palindrome, ignoring case and any non-alphanumeric characters."
TESTS = [
    "assert is_palindrome('A man, a plan, a canal: Panama') == True",
    "assert is_palindrome('Not a palindrome') == False",
    "assert is_palindrome('') == True",
    "assert is_palindrome('Was it a car or a cat I saw?') == True",
]


def run_reflexion_agent(task: str, tests: list[str]):
    if not HAVE_KEY:
        print("Skipped (no GROQ_API_KEY): run_reflexion_agent")
        return
    app = build_graph()
    result = app.invoke({
        "task": task, "tests": tests, "code": "", "test_output": "",
        "passed": False, "reflections": [], "trial": 0,
    })

    for i, reflection in enumerate(result["reflections"], start=1):
        print(f"Reflection after trial {i}: {reflection}\n")
    print(f"Solved: {result['passed']} (after {result['trial']} trial(s))\n")
    print("Final code:\n", result["code"])


def main():
    run_reflexion_agent(TASK, TESTS)


if __name__ == "__main__":
    main()
