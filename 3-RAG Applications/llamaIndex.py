# ============================================================
# RAG PIPELINE MAP (matches how you described it):
#   prompt -> question -> retriever -> context -> context encoder
#   -> vector database -> retrieve -> (context + prompt) -> LLM -> response
#
# Splitting that into two phases:
#   BUILD PHASE (sections 1-5): turn your files into searchable vectors, once
#   QUERY PHASE (sections 6-8): turn a user prompt into an answer, every time
# ============================================================

# ---------- SECTION 1: IMPORTS ----------
from dotenv import load_dotenv                                      # loads GOOGLE_API_KEY from ../.env
import chromadb                                                     # the vector database itself
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings, get_response_synthesizer
from llama_index.core.node_parser import SentenceSplitter           # splits documents into chunks ("nodes")
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # the "context encoder" (text -> vector)
from llama_index.vector_stores.chroma import ChromaVectorStore      # bridge between llama_index and chromadb
from llama_index.llms.google_genai import GoogleGenAI               # the LLM used to actually answer questions

load_dotenv()  # reads the .env file at the project root so GOOGLE_API_KEY is available below

# llama_index's LLM-dependent calls (get_response_synthesizer, as_query_engine) default to OpenAI
# unless told otherwise. There's no OPENAI_API_KEY in this project, only GOOGLE_API_KEY, so point
# Settings.llm at Gemini instead — every section below that needs an LLM will use this automatically.
Settings.llm = GoogleGenAI(model="gemini-flash-latest")


# ---------- SECTION 2: LOAD YOUR DATA ----------
# reads every file under "resours" (recursive=True = include subfolders) into Document objects
documents = SimpleDirectoryReader("resours", recursive=True).load_data()


# ---------- SECTION 3: SPLIT DOCUMENTS INTO CHUNKS ("nodes") ----------
# a whole document is too big/unfocused to embed well, so we cut it into small pieces first
node_parser = SentenceSplitter()
nodes = node_parser.get_nodes_from_documents(documents)


# ---------- SECTION 4: CONTEXT ENCODER (embedding model) ----------
# this is the model that turns text (chunks, and later the question) into vectors
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=r"C:\Users\THARU\.cache\huggingface\hub",  # avoids a broken cache path bug on this machine
)


# ---------- SECTION 5: VECTOR DATABASE + BUILD THE INDEX ----------
chroma_client = chromadb.PersistentClient(path="./chroma_db")            # open/create the on-disk chroma db
chroma_collection = chroma_client.get_or_create_collection("rag_applications")  # a named "table" inside it
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)    # lets llama_index write/read chroma
storage_context = StorageContext.from_defaults(vector_store=vector_store)  # bundles that vector_store for the index

# this is where the actual work happens: each node -> embed_model -> vector -> saved into chroma
index = VectorStoreIndex(
    nodes=nodes,
    embed_model=embed_model,
    storage_context=storage_context,
)
print(f"Build phase done: {len(nodes)} chunk(s) embedded and stored in chroma collection '{chroma_collection.name}'.")


# ============================================================
# QUERY PHASE — this is the part you run per user prompt
# ============================================================

user_prompt = "What is the name and age mentioned in the document?"

# ---------- SECTION 6: PROMPT -> RETRIEVER -> CONTEXT ----------
# as_retriever() gives you an object that: encodes the prompt with the SAME embed_model,
# then searches the vector database for the closest matching chunks
retriever = index.as_retriever(similarity_top_k=5)  # top_k = how many chunks to pull back
retrieved_nodes = retriever.retrieve(user_prompt)   # this is the "context" step

print("\nRetrieved context:")
for n in retrieved_nodes:
    print(f"- (score={n.score:.3f}) {n.text!r}")


# ---------- SECTION 7: (CONTEXT + PROMPT) -> LLM -> RESPONSE, spelled out manually ----------
# a response_synthesizer is the piece that stuffs [context + prompt] into an LLM call
response_synthesizer = get_response_synthesizer()
response = response_synthesizer.synthesize(
    query=user_prompt,
    nodes=retrieved_nodes,
)
print("\nManual synthesis response:")
print(response)


# ---------- SECTION 8: SAME THING, SHORTCUT VERSION ----------
# query_engine = retriever (section 6) + response_synthesizer (section 7) combined into one call
query_engine = index.as_query_engine(similarity_top_k=5)
response = query_engine.query(user_prompt)
print("\nQuery engine response:")
print(response)
