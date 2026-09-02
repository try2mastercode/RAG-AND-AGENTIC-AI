# ---------- SECTION 1: IMPORTS ----------
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_classic.retrievers.self_query.base import SelfQueryRetriever
from langchain_classic.chains.query_constructor.schema import AttributeInfo
from langchain_community.query_constructors.chroma import ChromaTranslator


# ---------- SECTION 2: MODELS ----------
load_dotenv()
GROQ_MODEL = "qwen/qwen3.8-27b"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=r"C:\Users\THARU\.cache\huggingface\hub",
)
llm = ChatGroq(model=GROQ_MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)


# ---------- SECTION 3: SAMPLE DOCUMENTS WITH METADATA ----------
docs = [
    Document(
        page_content="Solar panels use photovoltaic cells to turn sunlight directly into electricity.",
        metadata={"category": "solar", "difficulty": "beginner"},
    ),
    Document(
        page_content="Maximum power point tracking (MPPT) adjusts a solar inverter's load in real "
        "time so the array always operates at its most efficient voltage/current point.",
        metadata={"category": "solar", "difficulty": "advanced"},
    ),
    Document(
        page_content="Wind turbines spin a rotor using moving air, and the rotor drives a generator.",
        metadata={"category": "wind", "difficulty": "beginner"},
    ),
    Document(
        page_content="Wind farm micrositing uses computational fluid dynamics to model turbulence "
        "and wake effects so turbines aren't placed where neighbors would steal their wind.",
        metadata={"category": "wind", "difficulty": "advanced"},
    ),
    Document(
        page_content="Hydroelectric dams generate power by using flowing water to spin turbines.",
        metadata={"category": "hydro", "difficulty": "beginner"},
    ),
]
vectordb = Chroma.from_documents(docs, embeddings)


# ---------- SECTION 4: DESCRIBE THE METADATA FIELDS TO THE LLM ----------
metadata_field_info = [
    AttributeInfo(
        name="category",
        description="The renewable energy category the document covers. One of: solar, wind, hydro.",
        type="string",
    ),
    AttributeInfo(
        name="difficulty",
        description="The reading level of the document. One of: beginner, advanced.",
        type="string",
    ),
]
document_content_description = "Short explanations of how a renewable energy technology works."


# ---------- SECTION 5: SELF-QUERY RETRIEVER ----------
retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectordb,
    document_contents=document_content_description,
    metadata_field_info=metadata_field_info,
    structured_query_translator=ChromaTranslator(),
)

question = "Show me an advanced wind energy topic"


# ---------- SECTION 6: RETRIEVE ----------
retrieved_docs = retriever.invoke(question)
print("=== Self-query retrieval (semantic search + inferred metadata filter) ===")
for doc in retrieved_docs:
    print(f"- {doc.page_content!r}  metadata={doc.metadata}")


# ---------- SECTION 7: (CONTEXT + PROMPT) -> LLM -> RESPONSE ----------
context = "\n".join(doc.page_content for doc in retrieved_docs)

prompt = f"""Answer the question using ONLY the context below.

Context:
{context}

Question: {question}"""

response = llm.invoke(prompt)
print("\n=== Final LLM answer (grounded in self-query context) ===")
print(response.content)
