

# ---------- SECTION 1: IMPORTS ----------
from llama_index.core import Settings, Document, VectorStoreIndex
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
    "Solar panels convert sunlight directly into electricity using photovoltaic cells.",
    "Wind turbines generate electricity by capturing the kinetic energy of moving air.",
    "Hydroelectric dams produce power by using flowing water to spin turbines.",
    "Geothermal plants tap heat from deep underground to generate steam and electricity.",
    "Battery storage systems help balance supply and demand on renewable energy grids.",
]
documents = [Document(text=t) for t in raw_texts]


# ---------- SECTION 4: VECTOR STORE INDEX ----------
index = VectorStoreIndex.from_documents(documents)   # embeds every document and stores it as a node

question = "How do renewable energy sources generate electricity?"


# ---------- SECTION 5: RETRIEVER ----------
retriever = index.as_retriever(similarity_top_k=3)
retrieved_nodes = retriever.retrieve(question)

print("=== VectorStoreIndex retrieval ===")
for node in retrieved_nodes:
    print(f"- ({node.score:.3f}) {node.get_content()}")


# ---------- SECTION 6: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
context = "\n".join(node.get_content() for node in retrieved_nodes)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = Settings.llm.complete(prompt)
print("\n=== Final LLM answer (grounded in vector-index context) ===")
print(response.text)
