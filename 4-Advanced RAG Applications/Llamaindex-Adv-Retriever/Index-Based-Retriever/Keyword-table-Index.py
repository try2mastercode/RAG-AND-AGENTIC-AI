

# ---------- SECTION 1: IMPORTS ----------
from llama_index.core import Settings, Document, SimpleKeywordTableIndex
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


# ---------- SECTION 4: KEYWORD TABLE INDEX ----------
index = SimpleKeywordTableIndex.from_documents(documents)   # regex keyword extraction, no embeddings needed

question = "How do wind and hydro plants generate electricity?"


# ---------- SECTION 5: RETRIEVER ----------
retriever = index.as_retriever(retriever_mode="simple")   # matches keywords extracted from the query, not vector similarity
retrieved_nodes = retriever.retrieve(question)

print("=== Keyword table retrieval ===")
for node in retrieved_nodes:
    print(f"- {node.get_content()}")


# ---------- SECTION 6: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
context = "\n".join(node.get_content() for node in retrieved_nodes)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = Settings.llm.complete(prompt)
print("\n=== Final LLM answer (grounded in keyword-table context) ===")
print(response.text)
