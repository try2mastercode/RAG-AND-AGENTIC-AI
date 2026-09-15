import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableParallel

load_dotenv()

GROQ_MODEL = "qwen/qwen3.8-27b"
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0.7)
parser = StrOutputParser()

# ---------- SECTION 1: SEQUENTIAL CHAIN (dish -> recipe -> time) ----------
dish_prompt = PromptTemplate(
    template="Suggest one classic dish from {location}. Reply with just the dish name, nothing else.",
    input_variables=["location"],
)
recipe_prompt = PromptTemplate(
    template="Give a short, simple recipe (under 80 words) for {dish}.",
    input_variables=["dish"],
)
time_prompt = PromptTemplate(
    template="Given this recipe: {recipe}\n\nReply with only the estimated total cooking time.",
    input_variables=["recipe"],
)

dish_chain = dish_prompt | llm | parser
recipe_chain = recipe_prompt | llm | parser
time_chain = time_prompt | llm | parser


def run_sequential(location: str) -> dict:
    dish = dish_chain.invoke({"location": location})
    recipe = recipe_chain.invoke({"dish": dish})
    cook_time = time_chain.invoke({"recipe": recipe})
    return {"dish": dish, "recipe": recipe, "time": cook_time}


# ---------- SECTION 2: PARALLEL CHAIN (fact + joke, one round trip) ----------
fact_prompt = PromptTemplate(
    template="Give one interesting, factual sentence about {dish}.",
    input_variables=["dish"],
)
joke_prompt = PromptTemplate(
    template="Tell one short, clean joke about {dish}.",
    input_variables=["dish"],
)

parallel_chain = RunnableParallel(
    fact=fact_prompt | llm | parser,
    joke=joke_prompt | llm | parser,
)


def run_parallel(dish: str) -> dict:
    return parallel_chain.invoke({"dish": dish})


# ---------- SECTION 3: BRANCH CHAIN (short vs detailed, routed at runtime) ----------
short_prompt = PromptTemplate(template="In one sentence, explain: {topic}", input_variables=["topic"])
long_prompt = PromptTemplate(
    template="Explain in detail, in 3-4 sentences: {topic}",
    input_variables=["topic"],
)

branch_chain = RunnableBranch(
    (lambda x: x["detailed"], long_prompt | llm | parser),
    short_prompt | llm | parser,
)


def run_branch(topic: str, detailed: bool) -> str:
    return branch_chain.invoke({"topic": topic, "detailed": detailed})


# ---------- SECTION 4: CONVERSATIONAL MEMORY (per-session chat history) ----------
chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a friendly cooking assistant. Keep answers to 1-2 sentences."),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)
chat_chain = chat_prompt | llm | parser

_sessions: dict[str, InMemoryChatMessageHistory] = {}


def run_chat(session_id: str, message: str) -> str:
    history = _sessions.setdefault(session_id, InMemoryChatMessageHistory())
    reply = chat_chain.invoke({"history": history.messages, "input": message})
    history.add_user_message(message)
    history.add_ai_message(reply)
    return reply
