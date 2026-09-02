from dotenv import load_dotenv
import chromadb
from llama_index.core import Document, VectorStoreIndex, StorageContext, get_response_synthesizer
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()

embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=r"C:\Users\THARU\.cache\huggingface\hub",
)
llm = GoogleGenAI(model="gemini-3.5-flash-lite")


def load_all_chunks(filename):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    document = Document(text=text)
    splitter = SentenceSplitter(chunk_size=500, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents([document])
    return nodes


def build_vectorstore(nodes):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = chroma_client.get_or_create_collection("rag_app_simple_chatbot")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(
        nodes=nodes,
        embed_model=embed_model,
        storage_context=storage_context,
    )
    return index


def get_retriever(index):
    retriever = index.as_retriever(similarity_top_k=5)
    return retriever


SAGE_QA_TEMPLATE = PromptTemplate(
    """You are Sage, a warm and friendly assistant who helps users understand documents they upload. You're approachable, encouraging, and enjoy explaining things clearly.

Rules:
- If the user greets you or makes small talk (e.g. "hi", "hello", "thanks", "how are you"), reply briefly and warmly, in character — you don't need the context for this.
- If the user asks a question about the document, answer using ONLY the context below.
- If it's a document question but the context doesn't contain the answer, say so honestly instead of guessing.
- Never break character or mention that you are an AI language model.

Context:
{context_str}

Question: {query_str}
"""
)


def answer_question(retriever, llm, question):
    retrieved_nodes = retriever.retrieve(question)
    response_synthesizer = get_response_synthesizer(llm=llm, text_qa_template=SAGE_QA_TEMPLATE)
    response = response_synthesizer.synthesize(
        query=question,
        nodes=retrieved_nodes,
    )
    return str(response)
