# ---------- SECTION 1: IMPORTS ----------
import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
    RunnableBranch,
)


# ---------- SECTION 2: MODEL (Groq) ----------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

llm = ChatGroq(
    model="qwen/qwen3.8-27b",  # allam-2-7b (GROQ_MODEL) has no tool-calling support
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ---------- SECTION 3: LCEL BASICS - THE PIPE OPERATOR ----------
# prompt | llm | parser: each stage is a Runnable, and | wires the output of
# one straight into the input of the next.
summarize_prompt = ChatPromptTemplate.from_template(
    "Summarize this in exactly one sentence: {text}"
)
summarize_chain = summarize_prompt | llm | StrOutputParser()

print("=== Basic LCEL chain ===")
print(
    summarize_chain.invoke(
        {"text": "LCEL lets you compose prompts, models, and parsers with the | operator."}
    )
)


# ---------- SECTION 4: RunnableParallel - FAN OUT TO MULTIPLE CHAINS ----------
# Runs several chains on the same input at once and collects the results
# into a dict keyed by branch name.
translate_prompt = ChatPromptTemplate.from_template("Translate to French: {text}")
translate_chain = translate_prompt | llm | StrOutputParser()

parallel_chain = RunnableParallel(summary=summarize_chain, translation=translate_chain)

print("\n=== RunnableParallel ===")
print(parallel_chain.invoke({"text": "LangChain makes it easy to build LLM applications."}))


# ---------- SECTION 5: RunnablePassthrough - CARRY THE ORIGINAL INPUT FORWARD ----------
# Useful when a later step needs both the transformed value and the raw
# original input (e.g. showing the question next to its answer).
answer_prompt = ChatPromptTemplate.from_template("Answer briefly: {question}")
with_original_question = RunnableParallel(
    question=RunnablePassthrough(),
    answer=answer_prompt | llm | StrOutputParser(),
)

print("\n=== RunnablePassthrough ===")
print(with_original_question.invoke({"question": "What is LCEL short for?"}))


# ---------- SECTION 6: RunnableLambda - PLAIN PYTHON AS A PIPELINE STEP ----------
# Wraps an ordinary function so it can sit in the | chain like any other
# Runnable - no special base class needed.
def word_count(text: str) -> dict:
    return {"text": text, "word_count": len(text.split())}


count_chain = RunnableLambda(word_count)

print("\n=== RunnableLambda ===")
print(count_chain.invoke("this sentence has six words total"))


# ---------- SECTION 7: RunnableBranch - CONDITIONAL ROUTING ----------
# Picks which chain to run based on a condition checked against the input,
# instead of every branch running like RunnableParallel does.
short_prompt = ChatPromptTemplate.from_template("Reply in one short sentence: {text}")
long_prompt = ChatPromptTemplate.from_template("Reply with a detailed paragraph: {text}")

routed_chain = RunnableBranch(
    (lambda x: len(x["text"]) < 30, short_prompt | llm | StrOutputParser()),
    long_prompt | llm | StrOutputParser(),  # default branch
)

print("\n=== RunnableBranch ===")
print(routed_chain.invoke({"text": "Explain LCEL."}))


# ---------- SECTION 8: MANUAL TOOL CALLING - DEFINE TOOLS ----------
@tool
def get_stock_price(ticker: str) -> str:
    """Look up the current price for a stock ticker symbol."""
    fake_prices = {"AAPL": 227.50, "GOOG": 178.20, "MSFT": 420.10}
    price = fake_prices.get(ticker.upper())
    return f"{ticker.upper()}: ${price}" if price else f"No price found for {ticker}"


@tool
def compare_prices(price_a: str, price_b: str) -> str:
    """Compare two price strings like 'AAPL: $227.50' and say which is higher."""
    val_a = float(price_a.split("$")[1])
    val_b = float(price_b.split("$")[1])
    return price_a if val_a > val_b else price_b


tools_by_name = {get_stock_price.name: get_stock_price, compare_prices.name: compare_prices}
llm_with_tools = llm.bind_tools([get_stock_price, compare_prices])


# ---------- SECTION 9: MANUAL TOOL CALLING, THE LCEL WAY ----------
# Instead of a hand-rolled while loop, the tool-execution step is itself a
# RunnableLambda dropped into the pipe: llm_with_tools decides which tool(s)
# to call, execute_tool_calls runs them, and the results flow to the next
# invoke - the same round trip, expressed as a chain rather than a loop.
def execute_tool_calls(ai_msg):
    messages = [ai_msg]
    for call in ai_msg.tool_calls:
        result = tools_by_name[call["name"]].invoke(call["args"])
        messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
    return messages


tool_call_chain = llm_with_tools | RunnableLambda(execute_tool_calls)

print("\n=== Manual tool calling via LCEL ===")
question = [HumanMessage("What's the price of AAPL?")]
tool_result_messages = tool_call_chain.invoke(question)
final_answer = llm_with_tools.invoke(question + tool_result_messages)
print(final_answer.content)


# ---------- SECTION 10: BATCH AND STREAM - RUNNABLE METHODS BEYOND invoke() ----------
# Every LCEL chain gets .batch() and .stream() for free, with no extra code.
print("\n=== .batch() - run the same chain over multiple inputs at once ===")
batch_results = summarize_chain.batch(
    [{"text": "LCEL supports batching."}, {"text": "LCEL supports streaming."}]
)
for r in batch_results:
    print("-", r)

print("\n=== .stream() - receive the response as it's generated ===")
for chunk in summarize_chain.stream({"text": "Streaming shows tokens as they arrive."}):
    print(chunk, end="", flush=True)
print()
