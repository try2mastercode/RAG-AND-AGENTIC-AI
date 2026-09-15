import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnableParallel, RunnablePassthrough

load_dotenv()

GROQ_MODEL = "qwen/qwen3.8-27b"
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0.3)
parser = StrOutputParser()


# ---------- SECTION 1: RunnableParallel - FAN OUT TO MULTIPLE CHAINS ----------
summarize_chain = ChatPromptTemplate.from_template("Summarize this in one sentence: {text}") | llm | parser
translate_chain = ChatPromptTemplate.from_template("Translate to French: {text}") | llm | parser
parallel_chain = RunnableParallel(summary=summarize_chain, translation=translate_chain)


def run_parallel(text: str) -> dict:
    return parallel_chain.invoke({"text": text})


# ---------- SECTION 2: RunnablePassthrough - CARRY THE ORIGINAL INPUT FORWARD ----------
answer_chain = ChatPromptTemplate.from_template("Answer briefly: {question}") | llm | parser
with_original_question = RunnableParallel(question=RunnablePassthrough(), answer=answer_chain)


def run_passthrough(question: str) -> dict:
    # RunnablePassthrough() hands back the exact dict it received, i.e.
    # {"question": question} - unwrapped here so the API returns the plain
    # string rather than the whole input object nested a second time.
    result = with_original_question.invoke({"question": question})
    return {"question": result["question"]["question"], "answer": result["answer"]}


# ---------- SECTION 3: RunnableLambda - PLAIN PYTHON AS A PIPELINE STEP ----------
# No LLM call at all - this step is pure Python, wrapped so it can still sit
# in a `|` chain like any other Runnable.
def _word_count(text: str) -> dict:
    return {"text": text, "word_count": len(text.split())}


count_chain = RunnableLambda(_word_count)


def run_lambda(text: str) -> dict:
    return count_chain.invoke(text)


# ---------- SECTION 4: RunnableBranch - CONDITIONAL ROUTING ----------
# Only one branch runs, chosen from the input at invoke time - unlike
# RunnableParallel above, where every branch always runs.
short_chain = ChatPromptTemplate.from_template("Reply in one short sentence: {text}") | llm | parser
long_chain = ChatPromptTemplate.from_template("Reply with a detailed paragraph: {text}") | llm | parser
routed_chain = RunnableBranch((lambda x: len(x["text"]) < 30, short_chain), long_chain)


def run_branch(text: str) -> dict:
    took_short_branch = len(text) < 30
    return {
        "reply": routed_chain.invoke({"text": text}),
        "branch_taken": "short (input under 30 chars)" if took_short_branch else "long (default branch)",
    }
