#give example fo each

import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableSequence,
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
    RunnableBranch,
)

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
parser = StrOutputParser()

# ---------------------------------------------------------------------------
# 1. RunnableSequence  ->  step 1 output feeds into step 2, feeds into step 3
#    (the `|` pipe operator builds this automatically, this is the explicit form)
# ---------------------------------------------------------------------------
dish_prompt = PromptTemplate(
    template="Suggest one classic dish from {location}. Just the dish name.",
    input_variables=["location"],
)
recipe_prompt = PromptTemplate(
    template="Give a short, simple recipe for {dish}.",
    input_variables=["dish"],
)

sequence_chain = RunnableSequence(
    dish_prompt, llm, parser,
    {"dish": RunnablePassthrough()} | recipe_prompt, llm, parser,
)
# equivalent shorthand: dish_prompt | llm | parser | {"dish": RunnablePassthrough()} | recipe_prompt | llm | parser

print("=== RunnableSequence ===")
print(sequence_chain.invoke({"location": "France"}))


# ---------------------------------------------------------------------------
# 2. RunnableParallel  ->  run multiple chains at once on the same input,
#    collect results into a dict
# ---------------------------------------------------------------------------
joke_prompt = PromptTemplate(
    template="Tell a short joke about {topic}.", input_variables=["topic"]
)
fact_prompt = PromptTemplate(
    template="Tell one interesting fact about {topic}.", input_variables=["topic"]
)

parallel_chain = RunnableParallel(
    joke=joke_prompt | llm | parser,
    fact=fact_prompt | llm | parser,
)

time.sleep(15)  # stay under the free-tier rate limit
print("\n=== RunnableParallel ===")
print(parallel_chain.invoke({"topic": "space travel"}))


# ---------------------------------------------------------------------------
# 3. RunnablePassthrough  ->  forward the input untouched (often used to keep
#    the original input alongside a transformed value)
# ---------------------------------------------------------------------------
passthrough_chain = RunnableParallel(
    original=RunnablePassthrough(),
    upper=RunnableLambda(lambda x: x["topic"].upper()),
)

print("\n=== RunnablePassthrough ===")
print(passthrough_chain.invoke({"topic": "space travel"}))


# ---------------------------------------------------------------------------
# 4. RunnableLambda  ->  wrap a plain python function as a step in a chain
# ---------------------------------------------------------------------------
count_words = RunnableLambda(lambda text: len(text.split()))

word_count_chain = joke_prompt | llm | parser | count_words

time.sleep(15)  # stay under the free-tier rate limit
print("\n=== RunnableLambda ===")
print(word_count_chain.invoke({"topic": "cats"}))


# ---------------------------------------------------------------------------
# 5. RunnableBranch  ->  route to a different chain based on a condition
# ---------------------------------------------------------------------------
short_prompt = PromptTemplate(
    template="In one sentence, what is {topic}?", input_variables=["topic"]
)
long_prompt = PromptTemplate(
    template="Give a detailed, multi-paragraph explanation of {topic}.",
    input_variables=["topic"],
)

branch_chain = RunnableBranch(
    (lambda x: x.get("detailed", False), long_prompt | llm | parser),
    short_prompt | llm | parser,  # default branch
)

time.sleep(15)  # stay under the free-tier rate limit
print("\n=== RunnableBranch ===")
print(branch_chain.invoke({"topic": "black holes", "detailed": False}))
