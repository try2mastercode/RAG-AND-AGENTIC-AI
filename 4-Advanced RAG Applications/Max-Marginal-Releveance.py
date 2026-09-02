

# ---------- SECTION 1: IMPORTS ----------
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq                          # Groq-hosted LLM (OpenAI-compatible API)
from langchain_huggingface import HuggingFaceEmbeddings      # local embedding model (text -> vector)
from langchain_community.vectorstores import Chroma          # in-memory/on-disk vector database
from langchain_core.documents import Document                # the object a vectorstore stores/returns


# ---------- SECTION 2: MODELS ----------
load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=r"C:\Users\THARU\.cache\huggingface\hub",
)
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)  # temperature=0 -> consistent, non-creative answers


# ---------- SECTION 3: SAMPLE DOCUMENTS ----------
raw_texts = [
    "Solar panels convert sunlight directly into electricity using photovoltaic cells.",
    "Photovoltaic cells inside solar panels turn sunlight into electrical power.",
    "Wind turbines generate electricity by capturing the kinetic energy of moving air.",
    "Hydroelectric dams produce power by using flowing water to spin turbines.",
    "Geothermal plants tap heat from deep underground to generate steam and electricity.",
    "Battery storage systems help balance supply and demand on renewable energy grids.",
]
documents = [Document(page_content=t) for t in raw_texts]


# ---------- SECTION 4: VECTOR DATABASE ----------
vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)

question = "How do renewable energy sources generate electricity?"


# ---------- SECTION 5: BASELINE - PLAIN SIMILARITY SEARCH ----------
plain_results = vectorstore.similarity_search(question, k=3)
print("=== Plain similarity search (baseline) ===")
for doc in plain_results:
    print(f"- {doc.page_content}")


# ---------- SECTION 6: MMR SEARCH ----------
mmr_results = vectorstore.max_marginal_relevance_search(
    question,
    k=3,
    fetch_k=6,
    lambda_mult=0.5,
)
print("\n=== MMR search (diversity-aware) ===")
for doc in mmr_results:
    print(f"- {doc.page_content}")

# the retriever wrapper form of the exact same thing, for use in chains
mmr_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 6, "lambda_mult": 0.5},
)


# ---------- SECTION 7: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
retrieved_docs = mmr_retriever.invoke(question)
context = "\n".join(doc.page_content for doc in retrieved_docs)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = llm.invoke(prompt)
print("\n=== Final LLM answer (grounded in MMR context) ===")
print(response.content)
