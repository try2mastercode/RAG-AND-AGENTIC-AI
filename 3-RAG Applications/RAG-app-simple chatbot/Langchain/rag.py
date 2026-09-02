from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv("D:\CODE\RAG and Agentic AI\.env")
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_community.vectorstores import Chroma
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

def load_all_chunks(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        text = f.read()
        splitter=RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = splitter.split_text(text)
        return chunks
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
def build_vectorstore(chunks):
    vectorstore = Chroma.from_texts(chunks, embedding=embeddings)
    return vectorstore
def get_retriever(vectorstore):
    retriever = vectorstore.as_retriever()
    return retriever
def answer_question(retriever,llm, question):
    docs=retriever.invoke(question)
    context="\n\n".join(doc.page_content for doc in docs)
    prompt = f"""You are Sage, a warm and friendly assistant who helps users understand documents they upload. You're approachable, encouraging, and enjoy explaining things clearly.

Rules:
- If the user greets you or makes small talk (e.g. "hi", "hello", "thanks", "how are you"), reply briefly and warmly, in character — you don't need the context for this.
- If the user asks a question about the document, answer using ONLY the context below.
- If it's a document question but the context doesn't contain the answer, say so honestly instead of guessing.
- Never break character or mention that you are an AI language model.

Context:
{context}

Question: {question}"""
    response=llm.invoke(prompt)
    if isinstance(response.content, list):
        return response.content[0]["text"]
    return response.content

