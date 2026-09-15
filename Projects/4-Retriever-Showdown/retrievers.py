import os

from dotenv import load_dotenv
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

GROQ_MODEL = "qwen/qwen3.8-27b"
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ---------- SECTION 1: FIXED SAMPLE CORPUS (same one used across this folder's scripts) ----------
CORPUS = [
    "Solar panels convert sunlight directly into electricity using photovoltaic cells.",
    "Photovoltaic cells inside solar panels turn sunlight into electrical power.",
    "Wind turbines generate electricity by capturing the kinetic energy of moving air.",
    "Hydroelectric dams produce power by using flowing water to spin turbines.",
    "Geothermal plants tap heat from deep underground to generate steam and electricity.",
    "Battery storage systems help balance supply and demand on renewable energy grids.",
]
documents = [Document(page_content=t) for t in CORPUS]

vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)
bm25_full_rank = BM25Retriever.from_documents(documents, k=len(documents))  # used by RRF, ranks the whole corpus


# ---------- SECTION 2: BASELINE -- plain dense similarity search ----------
def run_baseline(question: str, k: int = 3) -> list[str]:
    return [d.page_content for d in vectorstore.similarity_search(question, k=k)]


# ---------- SECTION 3: MMR -- diversity-aware dense search ----------
def run_mmr(question: str, k: int = 3, fetch_k: int = 6, lambda_mult: float = 0.5) -> list[str]:
    results = vectorstore.max_marginal_relevance_search(question, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult)
    return [d.page_content for d in results]


# ---------- SECTION 4: MULTI-QUERY -- LLM rewords the question, results merged + de-duplicated ----------
def run_multiquery(question: str, k_per_query: int = 2) -> dict:
    prompt = (
        "Generate 3 different rephrasings of the question below, one per line, "
        "no numbering, no extra commentary.\n\nQuestion: " + question
    )
    generated = llm.invoke(prompt).content
    queries = [q.strip("-* ").strip() for q in generated.splitlines() if q.strip()]

    merged: list[str] = []
    for q in [question] + queries:
        for doc in vectorstore.similarity_search(q, k=k_per_query):
            if doc.page_content not in merged:
                merged.append(doc.page_content)
    return {"generated_queries": queries, "merged_results": merged}


# ---------- SECTION 5: BM25 -- sparse / keyword search, no embeddings involved ----------
def run_bm25(question: str, k: int = 3) -> list[str]:
    retriever = BM25Retriever.from_documents(documents, k=k)
    return [d.page_content for d in retriever.invoke(question)]


# ---------- SECTION 6: RECIPROCAL RANK FUSION -- combine dense + sparse rankings ----------
def run_rrf(question: str, k: int = 3, k_const: int = 60) -> list[dict]:
    dense_ranked = [d.page_content for d in vectorstore.similarity_search(question, k=len(documents))]
    sparse_ranked = [d.page_content for d in bm25_full_rank.invoke(question)]

    scores: dict[str, float] = {}
    for rank, text in enumerate(dense_ranked, start=1):
        scores[text] = scores.get(text, 0.0) + 1 / (k_const + rank)
    for rank, text in enumerate(sparse_ranked, start=1):
        scores[text] = scores.get(text, 0.0) + 1 / (k_const + rank)

    fused = sorted(scores.items(), key=lambda item: -item[1])[:k]
    return [{"text": text, "score": score} for text, score in fused]
