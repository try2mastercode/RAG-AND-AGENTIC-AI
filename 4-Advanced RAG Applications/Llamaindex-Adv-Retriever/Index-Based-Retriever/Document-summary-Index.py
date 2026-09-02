

# ---------- SECTION 1: IMPORTS ----------
from llama_index.core import Settings, Document, DocumentSummaryIndex, get_response_synthesizer
from llama_index.core.node_parser import SentenceSplitter
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
    "loose, and that flow of electrons is captured as an electric current. Panels "
    "combine many cells together to produce a usable amount of power.",

    "Wind power works by converting the kinetic energy of moving air into "
    "electricity. Blades shaped like airfoils spin a rotor when wind passes over "
    "them, and that rotor turns a generator inside the turbine's nacelle.",
]
documents = [Document(text=t, doc_id=f"doc_{i}") for i, t in enumerate(raw_texts)]


# ---------- SECTION 4: DOCUMENT SUMMARY INDEX ----------
splitter = SentenceSplitter(chunk_size=1024)
response_synthesizer = get_response_synthesizer(response_mode="tree_summarize")   # used to generate each document's summary

index = DocumentSummaryIndex.from_documents(
    documents,
    transformations=[splitter],
    response_synthesizer=response_synthesizer,
)

print("=== LLM-generated summary for doc_0 ===")
print(index.get_document_summary("doc_0"))


# ---------- SECTION 5: RETRIEVER (embedding search over the summaries) ----------
retriever = index.as_retriever(retriever_mode="embedding", similarity_top_k=1)

question = "How does wind get turned into electricity?"
retrieved_nodes = retriever.retrieve(question)

print("\n=== Document summary retrieval ===")
for node in retrieved_nodes:
    print(f"- {node.get_content()!r}")


# ---------- SECTION 6: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
context = "\n".join(node.get_content() for node in retrieved_nodes)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = Settings.llm.complete(prompt)
print("\n=== Final LLM answer (grounded in document-summary context) ===")
print(response.text)
