

# ---------- SECTION 1: IMPORTS ----------
from llama_index.core import Settings, Document, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
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
    "combine many cells together to produce a usable amount of power.\n"
    "Utility-scale solar farms track the sun across the sky to squeeze out extra "
    "output, while rooftop panels are usually fixed in place for simplicity and cost.",

    "Wind power works by converting the kinetic energy of moving air into "
    "electricity. Blades shaped like airfoils spin a rotor when wind passes over "
    "them, and that rotor turns a generator inside the turbine's nacelle.\n"
    "Turbine placement matters a lot: wind farms are sited using years of wind-speed "
    "data, and taller towers reach steadier, faster wind higher above the ground.",
]
documents = [Document(text=t) for t in raw_texts]


# ---------- SECTION 4: HIERARCHICAL NODES (big parent chunks -> small leaf chunks) ----------
node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[512, 128])
all_nodes = node_parser.get_nodes_from_documents(documents)
leaf_nodes = get_leaf_nodes(all_nodes)


# ---------- SECTION 5: STORAGE (docstore holds every node, index only embeds the leaves) ----------
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(all_nodes)

index = VectorStoreIndex(leaf_nodes, storage_context=storage_context)


# ---------- SECTION 6: AUTO-MERGING RETRIEVER ----------
base_retriever = index.as_retriever(similarity_top_k=6)
retriever = AutoMergingRetriever(base_retriever, storage_context, verbose=True)   # merges sibling leaves back into their parent

question = "How does wind get turned into electricity?"
retrieved_nodes = retriever.retrieve(question)

print("=== Auto-merging retrieval ===")
for node in retrieved_nodes:
    print(f"- {node.get_content()!r}")


# ---------- SECTION 7: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
context = "\n".join(node.get_content() for node in retrieved_nodes)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = Settings.llm.complete(prompt)
print("\n=== Final LLM answer (grounded in auto-merged context) ===")
print(response.text)
