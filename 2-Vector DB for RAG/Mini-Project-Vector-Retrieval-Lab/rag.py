import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from vector_store import search

load_dotenv()

GROQ_MODEL = "qwen/qwen3.8-27b"
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0.3)
parser = StrOutputParser()


# ---------- SECTION 1: GROUNDED ANSWER PROMPT ----------
rag_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer using ONLY the numbered context passages below. "
            "If they don't contain the answer, say you don't have enough information.",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)
rag_chain = rag_prompt | llm | parser


# ---------- SECTION 2: RETRIEVE THEN GENERATE ----------
def answer(question: str, top_k: int = 3, topic: str | None = None, source: str | None = None, contains: str | None = None):
    matches = search(question, top_k=top_k, topic=topic, source=source, contains=contains)

    if not matches:
        return {"answer": "No documents matched those filters — try widening them.", "retrieved": []}

    context = "\n\n".join(f"[{i + 1}] {m['document']}" for i, m in enumerate(matches))
    reply = rag_chain.invoke({"context": context, "question": question})
    return {"answer": reply, "retrieved": matches}
