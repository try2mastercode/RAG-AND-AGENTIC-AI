

# ---------- SECTION 1: IMPORTS ----------
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.storage import InMemoryStore
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document



# ---------- SECTION 2: MODELS ----------
load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=r"C:\Users\THARU\.cache\huggingface\hub",
)
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)


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
documents = [Document(page_content=t) for t in raw_texts]


# ---------- SECTION 4: TWO SPLITTERS, TWO GRANULARITIES ----------
parent_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0, separator="\n")
child_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0, separator=" ")


# ---------- SECTION 5: TWO STORES ----------
vectorstore = Chroma(collection_name="split_parents", embedding_function=embeddings)  # holds embedded CHILD chunks
docstore = InMemoryStore()                                                            # holds the full PARENT chunks


# ---------- SECTION 6: PARENT DOCUMENT RETRIEVER ----------
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
retriever.add_documents(documents)

question = "How does wind get turned into electricity?"


# ---------- SECTION 7: RETRIEVE (searches children, returns their parents) ----------
retrieved_docs = retriever.invoke(question)
print("=== Parent chunks returned (retrieved via child-chunk similarity) ===")
for doc in retrieved_docs:
    print(f"- {doc.page_content!r}")


# ---------- SECTION 8: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
context = "\n".join(doc.page_content for doc in retrieved_docs)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = llm.invoke(prompt)
print("\n=== Final LLM answer (grounded in full parent-chunk context) ===")
print(response.content)
