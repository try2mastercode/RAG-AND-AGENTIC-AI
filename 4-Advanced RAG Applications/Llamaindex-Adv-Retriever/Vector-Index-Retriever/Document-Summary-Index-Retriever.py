

# ---------- SECTION 1: IMPORTS ----------
from llama_index.core import Settings, Document, DocumentSummaryIndex, get_response_synthesizer
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.indices.document_summary import (
    DocumentSummaryIndexEmbeddingRetriever,
    DocumentSummaryIndexLLMRetriever,
)
import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# ---------- SECTION 2: MODELS ----------
load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=r"C:\Users\THARU\.cache\huggingface\hub",
)
Settings.llm = Groq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)


# ---------- SECTION 3: SAMPLE DOCUMENTS ----------
raw_texts = [
    "Solar power comes from photovoltaic cells, which are made of semiconductor "
    "material - usually silicon. When sunlight hits a cell, it knocks electrons "
    "loose, and that flow of electrons is captured as an electric current.",

    "Wind power works by converting the kinetic energy of moving air into "
    "electricity. Blades shaped like airfoils spin a rotor when wind passes over "
    "them, and that rotor turns a generator inside the turbine's nacelle.",

    "Hydroelectric dams hold back a river to create a reservoir, then release that "
    "water through turbines. The falling water spins the turbines, which drive "
    "generators that produce electricity.",
]
documents = [Document(text=t, doc_id=f"doc_{i}") for i, t in enumerate(raw_texts)]


# ---------- SECTION 4: DOCUMENT SUMMARY INDEX ----------
splitter = SentenceSplitter(chunk_size=1024)
response_synthesizer = get_response_synthesizer(response_mode="tree_summarize")

index = DocumentSummaryIndex.from_documents(
    documents,
    transformations=[splitter],
    response_synthesizer=response_synthesizer,
)

question = "How does a dam produce electricity?"


# ---------- SECTION 5: EMBEDDING-BASED RETRIEVER (compares question to each summary's vector) ----------
embedding_retriever = DocumentSummaryIndexEmbeddingRetriever(index, similarity_top_k=1)
embedding_nodes = embedding_retriever.retrieve(question)

print("=== Embedding-based summary retrieval ===")
for node in embedding_nodes:
    print(f"- {node.get_content()!r}")


# ---------- SECTION 6: LLM-BASED RETRIEVER (LLM reads every summary and picks the relevant ones) ----------
llm_retriever = DocumentSummaryIndexLLMRetriever(index)
llm_nodes = llm_retriever.retrieve(question)

print("\n=== LLM-based summary retrieval ===")
for node in llm_nodes:
    print(f"- {node.get_content()!r}")


# ---------- SECTION 7: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
context = "\n".join(node.get_content() for node in embedding_nodes)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = Settings.llm.complete(prompt)
print("\n=== Final LLM answer (grounded in embedding-retrieved summary context) ===")
print(response.text)
