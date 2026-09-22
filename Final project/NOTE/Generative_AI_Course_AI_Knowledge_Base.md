---
title: "Generative AI Application Course — AI Knowledge Base"
type: "course_knowledge_base"
source: "5 course-module screenshots provided by the user"
language: "en"
format: "Markdown"
purpose: "AI retrieval, question answering, study, summarization, and course navigation"
scope: "Modules 1–5"
---

# Generative AI Application Course — AI Knowledge Base

## 0. Document Instructions

This document is designed to be consumed by an AI system.

### AI usage rules

- Treat the **course content** sections as the primary source of truth.
- Treat sections marked **AI-enriched detail** as explanatory material added to make the concepts easier to understand.
- Do not present AI-enriched detail as if it were explicitly stated in the original course screenshots.
- When answering questions about course structure, prefer the exact module/lesson hierarchy.
- When answering conceptual questions, use both the course topic and the corresponding AI-enriched explanation.
- Preserve technical distinctions between:
  - LLMs
  - multimodal LLMs
  - embeddings
  - vector search
  - RAG
  - metadata filtering
  - multimodal fusion
  - agents
  - multi-agent systems
  - LangChain
  - LangGraph
  - MCP
- If a question asks what the course explicitly teaches, do not infer additional technologies beyond the source material unless clearly labeled as additional context.

---

# 1. Course Overview

The course teaches how to build an end-to-end generative AI application by progressively combining:

1. Structured LLM-based data extraction
2. Multimodal LLM processing
3. Multimodal RAG
4. Vector search and metadata filtering
5. Multi-agent systems
6. Agent orchestration
7. Chatbot/UI integration
8. MCP-based tool and resource integration
9. LangChain and LangGraph
10. A final portfolio-ready generative AI application

## High-Level Progression

```text
Unstructured Data
      ↓
LLM Structured Extraction
      ↓
Multimodal Data Processing
      ↓
Multimodal RAG
      ↓
Vector Search + Metadata Filtering
      ↓
Multimodal Fusion + Ranking
      ↓
Specialized Agents
      ↓
Multi-Agent Workflow
      ↓
Chatbot / UI
      ↓
MCP Tools + Resources
      ↓
Integrated AI Application
      ↓
Final Project
```

---

# 2. Module 1 — Build a Structured Generative AI Application

## Module objective

Use LLMs to transform unstructured restaurant descriptions into structured JSON by designing prompts and extracting predefined attributes.

Use multimodal LLMs to generate captions from review images and integrate those captions into structured user-review data.

Build a command-line Python interface to:

- browse restaurant records
- add restaurant records
- edit restaurant records
- delete restaurant records
- use LLM-powered structuring functions for new entries
- create file backups before updates

## Module concepts

- LLM prompting
- Structured output
- JSON generation
- Information extraction
- Predefined attributes
- Multimodal LLMs
- Image captioning
- Structured review data
- Python CLI
- CRUD-style data management
- File backups

---

## Module 1 — Lesson 1: Structure Text Data with LLMs

### Source activities

- **Reading:** Assignment Overview: Structure Unstructured Restaurant Data with an LLM
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Structure Unstructured Restaurant Data with an LLM
  - Ungraded App Item
  - 45 minutes
- **Checklist:** Structure Text Data with LLMs
  - Practice Assignment
  - Submitted
  - Grade: 100%
  - Graded

### Concepts

The lesson focuses on converting free-form restaurant descriptions into predictable structured data.

### AI-enriched detail

Typical transformation:

```text
Unstructured restaurant description
        ↓
Prompt
        ↓
LLM
        ↓
Structured JSON
        ↓
Validation
        ↓
Application storage
```

Example:

```json
{
  "restaurant_name": "Example Restaurant",
  "cuisine": "South Indian",
  "location": "Bengaluru",
  "rating": 4.5,
  "price_range": "₹₹"
}
```

Important implementation concerns:

- Define the expected schema before prompting.
- Validate model output.
- Handle missing fields.
- Normalize inconsistent values.
- Prevent malformed JSON from entering application storage.
- Separate model-generated values from trusted application data.

---

## Module 1 — Lesson 2: Process Multimodal Customer Data with LLMs

### Source activities

- **Reading:** Assignment Overview: Process Multimodal Data with LLMs
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Process Multimodal Data with LLMs
  - Ungraded App Item
  - 45 minutes
- **Checklist:** Process Multimodal Customer Data with LLMs
  - Practice Assignment
  - Submitted
  - Grade: 100%
  - Graded

### Concepts

- Multimodal LLMs
- Image understanding
- Image caption generation
- Review-image processing
- Structured user-review data

### AI-enriched detail

A multimodal pipeline can be represented as:

```text
Review image
    ↓
Multimodal LLM
    ↓
Caption / extracted information
    ↓
Structured review record
    ↓
Restaurant review dataset
```

A multimodal model differs from a text-only model because it can process image information together with textual instructions/context.

---

## Module 1 — Lesson 3: Build a Simple Interactive User Interface

### Source activities

- **Reading:** Assignment Overview: Build a Command Line Data Management UI for Restaurant Data
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Build a Command Line Data Management UI for Restaurant Data
  - Ungraded App Item
  - 45 minutes
- **Checklist:** Build a Simple Interactive User Interface
  - Practice Assignment
  - Submitted
  - Grade: 100%
  - Graded

### Concepts

- Python command-line interface
- Restaurant record management
- Create
- Read
- Update
- Delete
- LLM-assisted record creation
- Persistent file handling

### AI-enriched detail

The CLI can expose operations such as:

```text
1. List restaurants
2. Add restaurant
3. Edit restaurant
4. Delete restaurant
5. Exit
```

Before destructive or modifying operations, a backup can be created:

```text
Current data
    ↓
Create backup
    ↓
Apply modification
    ↓
Save updated data
```

---

## Module 1 — Lesson 4: Module Summary and Assessment

- **Podcast:** Recap: Build a Structured Generative AI Application
  - Ungraded Plugin
  - 3 minutes
- **Graded Quiz:** Build a Structured Generative AI Application
  - Graded Assignment

---

# 3. Module 2 — Design a Multimodal RAG System

## Module objective

Design and implement the retrieval layer of a multimodal RAG system using:

- structured restaurant text data
- food images

Construct multimodal vector indexes, generate text and image embeddings, and build retrieval workflows combining:

- similarity search
- metadata filtering
- multimodal retrieval
- late fusion
- result reranking

The module emphasizes practical retrieval design rather than tool-specific features.

## Module concepts

- RAG
- Multimodal RAG
- Vector indexes
- Text embeddings
- Image embeddings
- Similarity search
- Metadata filtering
- Hybrid retrieval
- Late fusion
- Multimodal ranking
- Retrieval relevance

---

## Module 2 — Lesson 1: Multimodal Vector Index Construction

### Source activities

- **Reading:** Assignment Overview: Construct a Multimodal Vector Index
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Construct a Multimodal Vector Index
  - Ungraded App Item
  - 45 minutes
- **Checklist:** Multimodal Vector Index Construction
  - Practice Assignment
  - Submitted
  - Grade: 100%
  - Graded

### Concepts

- Vector indexing
- Text embeddings
- Image embeddings
- Multimodal retrieval

### AI-enriched detail

A simplified indexing pipeline:

```text
Restaurant text ──→ Text embedding ──┐
                                    ├──→ Vector index
Food image ───────→ Image embedding ─┘
```

An embedding is a numerical vector representing semantic information. Similar items can be retrieved by comparing vectors using a similarity metric.

---

## Module 2 — Lesson 2: Similarity Retrieval with Metadata Filtering

### Source activities

- **Reading:** Assignment Overview: Similarity Retrieval with Metadata Filtering
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Similarity Retrieval with Metadata Filtering
  - Ungraded App Item
  - 45 minutes
- **Checklist:** Similarity Retrieval with Metadata Filtering
  - Practice Assignment
  - Submitted
  - Grade: 100%
  - Graded

### Concepts

- Similarity search
- Metadata filtering
- Hybrid retrieval

### AI-enriched detail

Vector similarity can find semantically related records, while metadata filtering can constrain the result set.

Example:

```text
Semantic query:
"good South Indian breakfast"

AND

Metadata:
cuisine = "South Indian"
location = "Bengaluru"
rating >= 4.0
```

Possible metadata fields:

- cuisine
- location
- rating
- price range
- dietary category
- meal type
- restaurant ID

---

## Module 2 — Lesson 3: Multimodal Similarity Fusion and Ranking

### Source activities

- **Reading:** Assignment Overview: Multimodal Similarity Fusion and Retrieval Ranking
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Multimodal Similarity Fusion and Retrieval Ranking
  - Ungraded App Item
  - 45 minutes
- **Checklist:** Multimodal Similarity Fusion and Ranking
  - Practice Assignment
  - Submitted
  - Grade: 100%
  - Graded

### Concepts

- Multimodal similarity
- Score fusion
- Late fusion
- Retrieval ranking
- Reranking

### AI-enriched detail

Late fusion means that different retrieval pipelines first produce results independently and those results are combined later.

```text
Text query
   ↓
Text retrieval ──────────┐
                         │
Image/query modality ────┤
   ↓                     │
Image retrieval ─────────┘
             ↓
       Score fusion
             ↓
          Reranking
             ↓
      Final retrieved set
```

A fusion system may:

1. Retrieve text results.
2. Retrieve image results.
3. Normalize scores if necessary.
4. Combine scores.
5. Apply modality weights if appropriate.
6. Rerank the combined results.
7. Return the most relevant context.

---

## Module 2 — Lesson 4: Module Summary and Assessment

- **Podcast:** Recap: Design a Multimodal RAG System
  - Ungraded Plugin
  - 3 minutes
- **Graded Quiz:** Design a Multimodal RAG System
  - Graded Assignment
  - Approximately 21 minutes

---

# 4. Module 3 — Combine Agents into a Multi-Agent System

## Module objective

Design and implement a multi-agent recommendation system.

Define specialized agents with:

- roles
- goals
- backstories
- tasks

Integrate the agents into a coordinated workflow.

Test collaboration between multiple agents to generate:

- restaurant recommendations
- recipe recommendations

from a single user input.

Build an interactive chatbot interface using Gradio.

The chatbot should process user queries, display coordinated agent outputs, and support basic database editing functionality.

## Module concepts

- Agents
- Specialized agents
- Agent roles
- Agent goals
- Agent backstories
- Agent tasks
- Agent orchestration
- Multi-agent workflows
- Recommendation systems
- Restaurant recommendations
- Recipe recommendations
- Gradio
- Chatbot UI
- Database editing

---

## Module 3 — Lesson 1: Define Agents and Their Roles

### Source activities

- **Reading:** Assignment Overview: Design Specialized Agents for a Recommendation System
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Design Specialized Agents for a Recommendation System
  - Ungraded App Item
  - 45 minutes
- **Checklist:** Define Agents and Their Roles
  - Practice Assignment
  - 10 minutes

### Concepts

A specialized agent should have a clearly defined responsibility.

Example conceptual design:

```text
Agent
├── Role
├── Goal
├── Backstory / context
└── Tasks
```

---

## Module 3 — Lesson 2: Integrate Agents into a Multi-Agent System

### Source activities

- **Reading:** Assignment Overview: Implement and Test a Multi Agent Recommendation System
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Implement and Test a Multi Agent Recommendation System
  - Ungraded App Item
  - 45 minutes
- **Role Play:** Pitching a Multimodal Travel Recommendation System
  - Role Play
  - 15 minutes
- **Checklist:** Integrate Agents into a Multi Agent System
  - Practice Assignment
  - 10 minutes

### AI-enriched detail

A multi-agent workflow can be modeled as:

```text
User request
      ↓
Coordinator / Orchestrator
      ↓
 ┌────────────┬────────────┬────────────┐
 │ Agent A    │ Agent B    │ Agent C    │
 │ Restaurant │ Recipe     │ Travel     │
 └────────────┴────────────┴────────────┘
      ↓             ↓             ↓
       └─────────────┬─────────────┘
                     ↓
             Coordinated result
                     ↓
                 Final answer
```

The purpose of specialization is to divide complex responsibilities into smaller agent tasks.

---

## Module 3 — Lesson 3: Build a Chatbot Interface for the Recommendation System

### Source activities

- **Reading:** Assignment Overview: Build a Chatbot Interface for the Recommendation System
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Build a Chatbot Interface for the Recommendation System
  - Ungraded App Item
  - 45 minutes
- **Checklist:** Build a Chatbot Interface for the Recommendation System
  - Practice Assignment
  - 10 minutes

### Concepts

- Chatbot interface
- Gradio
- User input
- Agent workflow execution
- Displaying agent results
- Database editing

---

## Module 3 — Lesson 4: Module Summary and Assessment

- **Podcast:** Recap: Combine Agents into a Multi Agent System
  - Ungraded Plugin
  - 3 minutes
- **Graded Quiz:** Combine Agents into a Multi Agent System
  - Graded Assignment
  - Approximately 21 minutes

---

# 5. Module 4 — Integrate Agents, RAG, and Tools with MCP

## Module objective

Organize agent tools, databases, and documents within an MCP server.

Build:

- an MCP server
- an MCP client
- an LLM-based MCP host

Enable communication between the components and validate the system through testing.

Design and implement an LLM-powered MCP host with a GUI so that the LLM can access server-exposed tools and documents.

The module combines components built earlier into a unified MCP-based system and validates end-to-end tool execution through a GUI-based application.

## Module concepts

- Model Context Protocol (MCP)
- MCP server
- MCP client
- MCP host
- Tools
- Resources
- Databases
- Documents
- LLM tool use
- Tool execution
- End-to-end testing
- GUI
- Agents + RAG + tools

---

## Module 4 — Lesson 1: Organize Tools and Data in an MCP Server

### Source activities

- **Reading:** Assignment Overview: Build an MCP Server
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Build an MCP Server
  - Ungraded App Item
  - 30 minutes
- **Checklist:** Organize Tools and Data in an MCP Server
  - Practice Assignment
  - 10 minutes

### Concepts

An MCP server exposes capabilities and data that an MCP client/host can access.

Potential categories include:

```text
MCP Server
├── Tools
├── Resources / Data
└── Documents
```

---

## Module 4 — Lesson 2: Implement an MCP Client for Server Communication

### Source activities

- **Reading:** Assignment Overview: Build an MCP Client
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Build an MCP Client
  - Ungraded App Item
  - 30 minutes
- **Checklist:** Implement an MCP Client for Server Communication
  - Practice Assignment
  - 10 minutes

### Concepts

- MCP client
- Server communication
- Tool discovery/access
- Resource access

---

## Module 4 — Lesson 3: Design an LLM-based MCP Host

### Source activities

- **Reading:** Assignment Overview: Build a Full MCP Application
  - Ungraded Plugin
  - 5 minutes
- **Lab:** Build a Full MCP Application
  - Ungraded App Item
  - 30 minutes
- **Checklist:** Design an LLM-based MCP Host
  - Practice Assignment
  - 10 minutes

### AI-enriched detail

Conceptual architecture:

```text
                ┌──────────────────┐
                │     LLM Host     │
                │ Reasoning / Agent│
                └────────┬─────────┘
                         │
                    MCP Client
                         │
                         ↓
                ┌──────────────────┐
                │    MCP Server    │
                ├──────────────────┤
                │ Tools            │
                │ Resources        │
                │ Documents        │
                └────────┬─────────┘
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
         Database    Documents     APIs/Tools
```

### MCP terminology

**MCP Host**
- The application/environment containing the LLM and coordinating MCP interactions.

**MCP Client**
- The component that communicates with an MCP server.

**MCP Server**
- The component that exposes tools and resources.

**Tool**
- An executable capability that an AI application can invoke.

**Resource**
- Data/information exposed for consumption by the application or model.

---

## Module 4 — Lesson 4: Module Summary and Assessment

- **Podcast:** Summary: Integrate Agents, RAG, and Tools with MCP
  - Ungraded Plugin
  - 3 minutes
- **Graded Quiz:** Integrate Agents, RAG, and Tools with MCP
  - Graded Assignment
  - Approximately 21 minutes

---

# 6. Module 5 — Final Project and Course Wrap-Up

## Module objective

Complete the AI capstone project by submitting screenshots of tasks performed in previous labs.

Organize and present artifacts demonstrating how the learner:

- designed structured data workflows
- built multimodal RAG systems
- built multi-agent workflows
- integrated LangChain
- integrated LangGraph
- integrated MCP

The submission is used for final evaluation through an AI-based grading system and serves as a portfolio-ready showcase of an end-to-end generative AI solution.

## Module concepts

- Capstone project
- Project evidence
- Screenshots
- Structured data
- Multimodal RAG
- Multi-agent workflows
- LangChain
- LangGraph
- MCP
- End-to-end AI application
- Portfolio presentation
- AI-based evaluation

---

## Module 5 — Lesson 1: Final Project

### Source activities

- **Reading:** Prepare to Submit Your Project
  - Ungraded Plugin
  - 5 minutes
- **Project:** Final Project Submission and Evaluation
  - Graded App Item

### Expected evidence

The final submission should demonstrate how the previously developed components work together.

Relevant evidence can include:

- structured-data processing
- multimodal processing
- vector retrieval
- metadata filtering
- multimodal ranking
- agent workflows
- MCP integration
- user interface
- final end-to-end execution

---

## Module 5 — Lesson 2: Course Wrap-Up

- **Course Wrap Up**
  - Video
  - 2 minutes
- **Congratulations and Next Steps**
  - Reading
  - 1 minute
- **Thanks from the Course Team**
  - Reading
  - 1 minute

---

# 7. Cross-Module Concept Map

## Structured Data

```text
Unstructured text
    ↓
Prompt
    ↓
LLM
    ↓
Structured JSON
    ↓
Validation
    ↓
Storage
```

Primary module: **Module 1**

---

## Multimodal Processing

```text
Text + Images
      ↓
Multimodal LLM
      ↓
Captions / extracted information
      ↓
Structured records
```

Primary module: **Module 1**

---

## RAG

```text
User query
    ↓
Retriever
    ↓
Relevant information
    ↓
Context
    ↓
LLM
    ↓
Generated answer
```

Primary module: **Module 2**

---

## Multimodal RAG

```text
Text embeddings ──────┐
                      │
Image embeddings ─────┤
                      ↓
               Vector retrieval
                      ↓
              Metadata filtering
                      ↓
                Score fusion
                      ↓
                  Reranking
                      ↓
                 Final context
```

Primary module: **Module 2**

---

## Multi-Agent System

```text
User
 ↓
Coordinator
 ├── Restaurant Agent
 ├── Recipe Agent
 └── Travel / Recommendation Agent
 ↓
Combined result
 ↓
User
```

Primary module: **Module 3**

---

## MCP Integration

```text
LLM
 ↓
Host
 ↓
MCP Client
 ↓
MCP Server
 ├── Tools
 ├── Resources
 └── Documents
 ↓
External capabilities / data
```

Primary module: **Module 4**

---

# 8. Technology Relationship

## LangChain

Used as an application framework/ecosystem for components such as:

- LLM interaction
- prompts
- retrieval
- tools
- agents
- application orchestration

## LangGraph

Used for graph-based and stateful agent workflows.

Conceptually:

```text
State
 ↓
Node / Agent
 ↓
Decision
 ↓
Another node
 ↓
Final state
```

It is particularly relevant when an agent workflow has multiple steps, branching, looping, or shared state.

## MCP

A protocol for connecting AI applications/hosts to external tools and resources.

Conceptually:

```text
AI application
      ↓
    MCP
      ↓
External tools / resources
```

## Relationship

These technologies solve different layers of the application:

```text
Application / UI
       ↓
LangChain components
       ↓
LangGraph workflows / agents
       ↓
MCP client
       ↓
MCP server
       ↓
Tools + Resources + Data
```

They can therefore be used together in a single system.

---

# 9. Module-to-Concept Index

| Concept | Primary Module | Related Modules |
|---|---|---|
| LLM prompting | 1 | 4, 5 |
| Structured JSON | 1 | 5 |
| Information extraction | 1 | 5 |
| Multimodal LLM | 1 | 2 |
| Image captioning | 1 | 2 |
| Python CLI | 1 | 5 |
| Embeddings | 2 | 5 |
| Vector index | 2 | 5 |
| Similarity search | 2 | 5 |
| Metadata filtering | 2 | 5 |
| Multimodal retrieval | 2 | 5 |
| Late fusion | 2 | 5 |
| Reranking | 2 | 5 |
| Agents | 3 | 4, 5 |
| Agent roles | 3 | 4 |
| Agent orchestration | 3 | 4, 5 |
| Multi-agent system | 3 | 4, 5 |
| Gradio | 3 | 5 |
| MCP server | 4 | 5 |
| MCP client | 4 | 5 |
| MCP host | 4 | 5 |
| MCP tools | 4 | 5 |
| MCP resources | 4 | 5 |
| LangChain | 5 | 3, 4 |
| LangGraph | 5 | 3, 4 |
| Capstone | 5 | All |

---

# 10. Course Architecture — Complete View

```text
                         USER
                          │
                          ↓
                    User Interface
                          │
             ┌────────────┴────────────┐
             ↓                         ↓
       Multi-Agent System          Direct Query
             │                         │
             ↓                         │
       Agent Orchestrator              │
             │                         │
      ┌──────┼──────┐                  │
      ↓      ↓      ↓                  │
   Agent   Agent   Agent               │
      │      │      │                  │
      └──────┼──────┘                  │
             ↓                         │
          RAG Layer ←──────────────────┘
             │
      ┌──────┴──────┐
      ↓             ↓
 Text Retrieval   Image Retrieval
      │             │
      ↓             ↓
 Text Embeddings Image Embeddings
      │             │
      └──────┬──────┘
             ↓
       Fusion / Ranking
             │
             ↓
       Relevant Context
             │
             ↓
            LLM
             │
             ↓
        MCP Client
             │
             ↓
        MCP Server
       ┌─────┼─────┐
       ↓     ↓     ↓
     Tools Resources Documents
       │     │     │
       └─────┴─────┘
             ↓
       External Data
```

---

# 11. AI Question-Answering Reference

## If asked: "What is Module 1 about?"

Answer using:

> Module 1 focuses on building a structured generative AI application. It covers transforming unstructured restaurant descriptions into structured JSON using LLMs, processing review images with multimodal LLMs, and building a Python command-line interface for restaurant record management.

## If asked: "What is Module 2 about?"

Answer using:

> Module 2 focuses on designing a multimodal RAG system. It covers multimodal vector indexes, text and image embeddings, similarity retrieval, metadata filtering, multimodal similarity fusion, and retrieval ranking.

## If asked: "What is Module 3 about?"

Answer using:

> Module 3 focuses on combining specialized agents into a multi-agent recommendation system and exposing the system through a Gradio chatbot interface.

## If asked: "What is Module 4 about?"

Answer using:

> Module 4 focuses on integrating agents, RAG, and tools using MCP. It covers MCP servers, MCP clients, LLM-based MCP hosts, tools, data, documents, and GUI-based end-to-end applications.

## If asked: "What is Module 5 about?"

Answer using:

> Module 5 is the final project and course wrap-up. It focuses on presenting evidence of the previous work and demonstrating an integrated generative AI solution using structured data, multimodal RAG, multi-agent workflows, LangChain, LangGraph, and MCP.

---

# 12. Short Course Summary

The course progresses from basic LLM-based structuring to a complete agentic AI application.

```text
Module 1
STRUCTURE
LLM → JSON → Multimodal data → CLI

Module 2
RETRIEVE
Embeddings → Vector search → Filtering → Fusion → Ranking

Module 3
REASON / COLLABORATE
Specialized agents → Orchestration → Recommendation → Chatbot

Module 4
CONNECT
Agents + RAG + MCP → Tools + Resources + Documents

Module 5
DELIVER
Integrated application → Evidence → Evaluation → Portfolio
```

## Core learning sequence

**Structure → Retrieve → Collaborate → Connect → Deliver**

This sequence represents the main conceptual progression of the course.
