# RAG and Agentic AI

Coursework and hands-on exercises from a certification track covering
Retrieval-Augmented Generation (RAG) and agentic AI systems, built with
LangChain, LlamaIndex, LangGraph, CrewAI, AutoGen, BeeAI, and the Model
Context Protocol (MCP). LLM calls run against the Groq API.

## Structure

| Folder | Topic |
| --- | --- |
| `1-Generative AI applications` | LangChain basics: chains, memory, runnables (parallel/sequence) |
| `2-Vector DB for RAG` | Chroma vector database fundamentals, HNSW indexing |
| `3-RAG Applications` | First RAG pipelines with LangChain and LlamaIndex, a simple RAG chatbot |
| `4-Advanced RAG Applications` | Advanced retrievers: MMR, multi-query, parent-document, self-query, reciprocal-rank/relative-score/distribution-based fusion, BM25, auto-merging, document summary index |
| `5-MultiModel Gen AI` | Multimodal apps: image captioning, visual QA, speech-to-text/text-to-speech, a nutrition chatbot over image + text |
| `6-Fundamentals Agentic AI` | Tool calling, LCEL, and a from-scratch LangChain agent (incl. an AI-powered SQL agent and a data-viz agent) |
| `7-Agentic AI with LangChain and LangGraph` | LangGraph fundamentals, a ReAct agent, a Reflexion agent, and a self-improving agent with cross-run lesson memory |
| `8-Agentic AI with LangGraph, CrewAI, AutoGen and BeeAI` | Multi-agent frameworks compared: CrewAI crew, AutoGen multi-agent chat, BeeAI ReAct agent |
| `9-Building AI Agents with MCP` | MCP from first principles: servers, clients, resources, prompts, sampling, multi-server aggregation, Streamable HTTP transport, and a LangGraph MCP adapter agent |

Most folders that produce a runnable app (chatbots, agent tools, retriever
demos) include their own `requirements.txt`, `.env.example`, and README with
setup steps.

## Running an example

Each script/app is self-contained within its folder. General pattern:

```bash
cd "<folder>"
pip install -r requirements.txt
cp .env.example .env   # then add your GROQ_API_KEY
python <script>.py
```

## Notes

- LLM inference uses the [Groq API](https://console.groq.com/) (migrated
  from local Ollama models for speed and free-tier limits).
- Vector stores (Chroma) and other generated/binary artifacts are gitignored
  and rebuilt locally.
