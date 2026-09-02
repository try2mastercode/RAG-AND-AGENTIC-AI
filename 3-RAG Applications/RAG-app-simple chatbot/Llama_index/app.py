import gradio as gr

from rag import load_all_chunks, build_vectorstore, get_retriever, answer_question, llm


def process_document(file):
    nodes = load_all_chunks(file.name)
    index = build_vectorstore(nodes)
    retriever = get_retriever(index)
    status = f"Document loaded successfully. Chunks created: {len(nodes)}"
    return retriever, status


def chat(message, history, retriever):
    if retriever is None:
        return "Please upload and process a document on the first tab before asking questions."
    return answer_question(retriever, llm, message)


with gr.Blocks(title="RAG-Chatbot (LlamaIndex)") as demo:
    retriever_state = gr.State(None)  # holds the retriever across tabs, per browser session

    with gr.Tab("1. Upload Document"):
        file_input = gr.File(label="Upload your document")
        upload_button = gr.Button("Process Document")
        status_output = gr.Textbox(label="Status")
        upload_button.click(
            fn=process_document,
            inputs=file_input,
            outputs=[retriever_state, status_output],
        )

    with gr.Tab("2. Ask Questions"):
        gr.ChatInterface(
            fn=chat,
            additional_inputs=[retriever_state],
        )

demo.launch()
