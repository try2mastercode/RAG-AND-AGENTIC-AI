

# ---------- SECTION 1: IMPORTS ----------
import logging
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_classic.retrievers.multi_query import MultiQueryRetriever




# ---------- SECTION 2: MODELS ----------
load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=r"C:\Users\THARU\.cache\huggingface\hub",
)
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)   # this is an already-built object, so use `llm` below, never `llm()`


# ---------- SECTION 3: SAMPLE DOCUMENTS ----------
raw_texts = [
    "Photovoltaic cells convert sunlight directly into electricity for solar panels.",
    "Wind turbines capture kinetic energy from moving air to generate power.",
    "Hydroelectric dams spin turbines using the force of flowing water.",
    "Geothermal plants use underground heat to produce steam that drives generators.",
    "Battery storage systems keep renewable grids stable when supply and demand don't match.",
]
documents = [Document(page_content=t) for t in raw_texts]


# ---------- SECTION 4: VECTOR DATABASE + BASELINE RETRIEVER ----------
vectordb = Chroma.from_documents(documents=documents, embedding=embeddings)
base_retriever = vectordb.as_retriever(search_kwargs={"k": 2})   # method call `as_retriever()`, not the attribute `as+retriever`

question = "What tech turns light from the sun into power?"


# ---------- SECTION 5: BASELINE - SINGLE-QUERY RETRIEVAL ----------
plain_results = base_retriever.invoke(question)
print("=== Baseline: single-query retrieval ===")
for doc in plain_results:
    print(f"- {doc.page_content}")


# ---------- SECTION 6: MULTI-QUERY RETRIEVER ----------
logging.basicConfig()
logging.getLogger("langchain_classic.retrievers.multi_query").setLevel(logging.INFO)

retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=llm,
)

docs = retriever.invoke(question)

print("\n=== Multi-query retrieval (merged + de-duplicated) ===")
for doc in docs:
    print(f"- {doc.page_content}")


# ---------- SECTION 7: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
context = "\n".join(doc.page_content for doc in docs)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = llm.invoke(prompt)
print("\n=== Final LLM answer (grounded in multi-query context) ===")
print(response.content)
