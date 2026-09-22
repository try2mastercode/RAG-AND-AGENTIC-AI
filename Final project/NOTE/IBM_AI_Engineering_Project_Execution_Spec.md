# IBM AI Engineering Capstone — Project Execution Specification

> **Purpose:** This document is an execution/reference specification for completing the IBM restaurant recommendation capstone. It is designed to be useful to both a human developer and a coding assistant such as Claude.
>
> **Primary rule:** Treat the IBM-provided project material and submission instructions as the mandatory source of truth for certification requirements. External research is used only to clarify implementation details, current library/protocol behavior, and professional engineering considerations.
>
> **Status:** Execution specification built from the supplied project files and current official documentation reviewed in September 2026.

---

## 1. How to use this document

Use this file as the working project context while implementing the capstone.

### For the developer

Use it to answer:

- What must be built?
- What must exist before starting the next stage?
- What files/data/components are expected?
- What exact screenshot must be produced?
- What must be visible in each screenshot?
- What must remain unchanged because it is part of the IBM requirement?
- What should be tested before marking a task complete?

### For a coding assistant

Treat the document as a project specification, not as a request to redesign the project.

A coding assistant should:

1. Preserve IBM-mandated names, outputs, screenshot names, collection names, and requested technologies unless the developer explicitly asks for a redesign.
2. Prefer a minimal, targeted code correction over replacing the whole implementation.
3. Check the current project files before inventing new files, data formats, or APIs.
4. Preserve working behavior while fixing the reported problem.
5. Call out any change that could affect an IBM screenshot requirement.
6. Distinguish a course requirement from an optional professional enhancement.
7. Never silently substitute a different library or architecture merely because it is newer.

---

# 2. Project at a glance

## 2.1 Project objective

Build an end-to-end restaurant recommendation application that progresses through:

**Unstructured restaurant data → structured knowledge → multimodal enrichment → vector indexing → retrieval → multimodal ranking/fusion → specialized agents → coordinated agent workflow → chatbot → MCP server → MCP client → MCP host application.**

The supplied project overview describes the capstone as an end-to-end AI engineering exercise covering structured data generation, multimodal retrieval, multi-agent orchestration, interactive interfaces, and Model Context Protocol integration. **Source:** `info.md`, `Transcript.txt`, and the individual module files.

## 2.2 Mandatory final submission

The final assignment consists of **12 screenshot-based questions (Q1–Q12), worth 5 points each**, covering the four modules. The submission instructions define the screenshot filename and required visible content for each question.

**Primary source:** `Submission instruction.txt`.

The implementation itself is still required in order to generate the screenshots; the screenshots are the formal final-submission artifacts.

---

# 3. Source-of-truth map

Use the following order when resolving conflicting instructions.

| Priority | Source | Purpose |
|---|---|---|
| 1 | `Submission instruction.txt` | Final Q1–Q12 requirements and screenshot acceptance criteria |
| 2 | `M1L1.txt` … `M4L3.txt` | Individual lab scope and implementation requirements |
| 3 | `info.md` | High-level project framing |
| 4 | `Transcript.txt` | Course/project narrative and additional context |
| 5 | Current official documentation | Current implementation/API behavior when course material is underspecified |
| 6 | This document | Consolidated execution view; does not override IBM requirements |

### Supplied files

- `info.md`
- `M1L1.txt`
- `M1L2.txt`
- `M1L3.txt`
- `M2L1.txt`
- `M3L1.txt`
- `M3L2.txt`
- `M3L3.txt`
- `M4L1.txt`
- `M4L2.txt`
- `M4L3.txt`
- `Submission instruction.txt`
- `Transcript.txt`

### Important source-gap rule

Detailed lab files for **M2L2** and **M2L3** were not supplied in the current source set. Their final screenshot requirements are present in `Submission instruction.txt`, so this document records those requirements but **does not invent missing implementation instructions**.

Likewise, the Q12 screenshot requirement comes from `Submission instruction.txt`; the `M4L3.txt` overview supplies the application scope and deliverables.

---

# 4. Mandatory project boundaries

## 4.1 What this project is

This is an AI engineering project combining:

- LLM-based information extraction
- Schema-constrained structured data
- Multimodal image understanding
- Embedding-based retrieval
- Vector databases
- Metadata filtering
- Multimodal retrieval/ranking
- Multi-agent design
- Stateful workflow orchestration
- Natural-language chatbot UX
- Tool calling
- MCP server/client architecture
- ReAct-style agent execution
- End-to-end application integration

## 4.2 What this document is not

This is **not** a replacement for the IBM labs, and it does not attempt to reproduce every teaching explanation from the course.

It is the operational layer you use while building the project.

---

# 5. High-level dependency graph

The implementation should be treated as a staged pipeline.

```text
Raw restaurant descriptions
        |
        v
M1L1 — Structured restaurant JSON
        |
        +-----------------------------+
        |                             |
        v                             v
M1L2 — Recipe/image enrichment   M1L3 — Data management UI
        |                             |
        +-------------+---------------+
                      |
                      v
M2L1 — Multimodal vector index
                      |
                      v
M2L2 — Similarity retrieval
                      |
                      v
M2L3 — Multimodal fusion/ranking
                      |
                      v
M3L1 — Specialized agents
                      |
                      v
M3L2 — Multi-agent workflow
                      |
                      v
M3L3 — Gradio chatbot
                      |
                      v
M4L1 — MCP server
                      |
                      v
M4L2 — MCP client
                      |
                      v
M4L3 — Full MCP host application
                      |
                      v
Final Q1–Q12 screenshots
```

This is a logical dependency order. The IBM submission questions themselves are screenshot checkpoints rather than a separate software architecture.

---

# 6. Recommended project workspace

The IBM material does not mandate a single directory layout. The following layout is a practical organization layer that keeps the capstone understandable to both humans and coding assistants.

```text
project-root/
├── README.md
├── PROJECT_SPEC.md
├── requirements.txt              # or pyproject.toml / equivalent
├── .env.example
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── structured/
│   ├── recipes/
│   ├── images/
│   └── reviews/
│
├── notebooks/                    # IBM lab notebooks/cells if used
│
├── src/
│   ├── data/
│   ├── schemas/
│   ├── llm/
│   ├── retrieval/
│   ├── agents/
│   ├── chatbot/
│   └── mcp/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── chroma_data/                  # only if persistent local Chroma storage is used
│
├── screenshots/
│   ├── M1L1_structure_for_loop.jpg
│   ├── M1L2_caption_all_recipes.jpg
│   ├── M1L3_new_data_entry_process.jpg
│   ├── M2L1_multimodal_vector_index.jpg
│   ├── M2L2_similarity_retrieval.jpg
│   ├── M2L3_multimodal_fusion_results.jpg
│   ├── M3L1_food_style_expert_goal.jpg
│   ├── M3L2_node_analyze_styles.jpg
│   ├── M3L3_preference_extraction_test.jpg
│   ├── M4L1_Configure_Tools_Data_MCP_Server.jpg
│   ├── M4L2_Build_Test_MCP_Client.jpg
│   └── M4L3_Design_LLM_MCP_Host.jpg
│
└── docs/
    └── IBM_AI_Engineering_Project_Execution_Spec.md
```

**Important:** This structure is a recommended organization, not an IBM submission requirement. Preserve any IBM-provided notebook/file locations when the lab environment depends on them.

---

# 7. Environment and setup requirements

## 7.1 Base environment

Use a dedicated Python virtual environment for the project.

Do **not** globally upgrade all AI packages just because newer versions exist. Course notebooks can depend on particular API surfaces. Establish a working course environment first, then upgrade deliberately.

Keep a reproducible dependency record:

```text
requirements.txt
```

or, preferably for a larger project:

```text
pyproject.toml
```

Also preserve the environment information used successfully for the final submission.

## 7.2 Secrets

Do not hard-code API keys into notebooks, source files, or screenshots.

Use environment variables or an equivalent secret mechanism, for example:

```text
WATSONX_APIKEY=...
WATSONX_PROJECT_ID=...
WATSONX_URL=...
ANTHROPIC_API_KEY=...
```

Only define variables that the actual lab implementation requires.

IBM’s current watsonx documentation uses credentials/API access and a project or space identifier for programmatic access. The exact credential names and provider used by the course implementation must follow the course environment. See IBM’s current developer documentation for the relevant SDK/API setup.

## 7.3 Libraries/components appearing in the supplied project material

Expect some or all of the following, depending on the lab:

- Python
- LLM SDK/provider libraries
- LangChain
- LangGraph
- Pydantic or JSON schema validation
- Chroma
- Sentence Transformers
- CLIP
- PyTorch
- PIL/Pillow
- Gradio
- FastMCP / MCP SDK
- Testing utilities such as `pytest`

Do not treat every package as a universal requirement for every notebook. Install what the specific lab uses.

## 7.4 Current dependency compatibility note

Current Sentence Transformers documentation recommends Python 3.10+ for its current releases and describes separate support for image-related dependencies. This is useful when building outside the IBM environment, but **do not replace a course-provided runtime with the latest package stack unless required**.

Source: current Sentence Transformers installation documentation.

---

# 8. Global implementation rules

These rules should apply throughout the project.

## 8.1 Reproducibility

Every generated artifact should be reproducible from the input data, code, and configuration.

Track:

- Model name
- Embedding model
- LLM provider
- Important generation parameters
- Data file used
- Vector-store location
- Execution date when appropriate

## 8.2 Explicit schemas

Whenever the pipeline expects structured JSON, define the target structure explicitly.

Minimum contract:

```text
LLM response
    -> parse
    -> validate schema
    -> if invalid: repair
    -> validate again
    -> persist only validated output
```

Do not assume that syntactically valid JSON is semantically valid data.

## 8.3 Error handling

Every external boundary should have an error path:

- LLM call failure
- malformed JSON
- missing image
- invalid image
- embedding failure
- vector database failure
- empty retrieval result
- agent failure
- tool failure
- MCP connection failure
- malformed tool response
- invalid user input

## 8.4 Logging

Use informative logging or print output at key boundaries so that a failing stage can be located quickly.

At minimum, a developer should be able to identify:

```text
stage started
stage completed
number of records processed
validation failures
repair attempts
retrieval count
agent/workflow step
MCP connection/tool call
final output
```

## 8.5 Do not hide failures

Do not catch an exception and silently continue with corrupted or empty data.

If the pipeline intentionally skips an item, record that event.

## 8.6 Stable identifiers

Use deterministic IDs for persisted records where possible. Changing an ID on every run can create duplicate vector records and make debugging retrieval difficult.

## 8.7 Preserve IBM names

The following names are part of explicit IBM submission requirements and should not be casually renamed:

- `restaurant_articles`
- `food_images`
- screenshot filenames listed in `Submission instruction.txt`
- `new_data_entry_process`
- `node_analyze_styles`
- the six named agents in M3L1
- MCP tool names required by M4L2: `get_restaurant_info`, `recommend_by_vibe`, `get_review`

---

# 9. Module 1 — Data and multimodal enrichment

---

## 9.1 M1L1 — Structure Unstructured Restaurant Data with an LLM

**Primary source:** `M1L1.txt`

### Objective

Transform raw, unstructured restaurant descriptions into a validated structured JSON knowledge base.

### Required capabilities

1. Load raw restaurant description text files.
2. Inspect the variability and content of the input data.
3. Define the restaurant attributes to be extracted.
4. Create a one-shot prompt template.
5. Ask the LLM to return structured JSON.
6. Validate the output against a schema.
7. Repair malformed JSON responses using an LLM-based repair step.
8. Apply the pipeline across all restaurant descriptions.
9. Persist the resulting structured JSON dataset.

### Required conceptual pipeline

```text
raw restaurant text
    -> extraction prompt
    -> LLM response
    -> JSON parsing
    -> schema validation
    -> repair if invalid
    -> re-validation
    -> structured restaurant record
```

### Non-negotiable behavior

The loop must process the restaurant records systematically rather than manually transforming one example.

The saved dataset must contain only outputs that have passed the intended validation process.

### Screenshot requirement

**Filename:**

```text
M1L1_structure_for_loop.jpg
```

**Submission requirement:** The screenshot must show the loop used to generate and validate JSON outputs for each restaurant using the LLM.

Source: `Submission instruction.txt`.

### Acceptance checklist

- [ ] Raw restaurant data loads successfully.
- [ ] Prompt explicitly asks for the intended attributes.
- [ ] Target JSON structure is defined.
- [ ] Validation is performed.
- [ ] Invalid responses trigger repair logic.
- [ ] Repaired output is validated again.
- [ ] The loop processes the dataset.
- [ ] Final structured JSON is saved.
- [ ] Screenshot shows the required loop.
- [ ] Screenshot filename is exact.

---

## 9.2 M1L2 — Process Multimodal Data with LLMs

**Primary source:** `M1L2.txt`

### Objective

Extend the structured knowledge base with visual information from recipe images using a vision-capable LLM.

### Required capabilities

1. Load structured recipe JSON data.
2. Load associated recipe images.
3. Load/inspect user visit history data where referenced by the lab.
4. Design an image-captioning prompt.
5. Run small tests on sample images.
6. Generate captions for all required images.
7. Insert the generated captions into the structured JSON.
8. Save the enriched multimodal knowledge file.

### Expected logical flow

```text
recipe JSON + image
        |
        v
vision LLM prompt
        |
        v
caption
        |
        v
update recipe record
        |
        v
save enriched JSON
```

### Caption requirements

The course describes captions as informative descriptions emphasizing relevant visual information such as:

- ingredients/visible food items
- presentation
- cooking style/appearance
- contextual information where applicable

### Screenshot requirement

**Filename:**

```text
M1L2_caption_all_recipes.jpg
```

The screenshot must show the loop that calls the vision LLM and assigns generated captions to recipe entries.

Source: `Submission instruction.txt`.

### Acceptance checklist

- [ ] Recipe JSON loads.
- [ ] Associated images resolve correctly.
- [ ] Caption prompt is defined.
- [ ] Sample captions are tested before full execution.
- [ ] Caption generation runs over all required images.
- [ ] Captions are written back to the correct recipe records.
- [ ] Final multimodal JSON is saved.
- [ ] Screenshot shows the full captioning loop and relevant output.

---

## 9.3 M1L3 — Build a Command-Line Data Management UI

**Primary source:** `M1L3.txt`

### Objective

Provide a command-line application for browsing, adding, editing, and deleting restaurant records while preserving schema consistency and preventing accidental destructive operations.

### Required capabilities

#### Browse

- Load the structured restaurant JSON file.
- Show high-level summaries and/or detailed records.

#### Add

- Accept a raw restaurant description paragraph.
- Pass it through `new_data_entry_process`.
- Use the LLM to generate a structured record.
- Validate the resulting structure.
- Save it in the JSON knowledge file.

#### Edit

- Allow a user to select/update an existing record.
- Protect the write operation with explicit confirmation.

#### Delete

- Allow deletion of an existing record.
- Protect the destructive operation with explicit confirmation.

#### Tests

Implement unit tests for critical behavior, including cases where operations are cancelled.

### Required function

The source explicitly identifies:

```text
new_data_entry_process
```

This function must reuse the structured LLM pipeline rather than manually duplicating the extraction logic.

### Screenshot requirement

**Filename:**

```text
M1L3_new_data_entry_process.jpg
```

The screenshot must show the function implementation that:

- uses an LLM to generate structured JSON from a restaurant paragraph,
- validates the output,
- includes a loop to repair invalid JSON responses.

### Acceptance checklist

- [ ] Menu-driven CLI runs.
- [ ] Restaurant records can be viewed.
- [ ] New restaurant paragraph is transformed by the LLM.
- [ ] Output is validated.
- [ ] Invalid LLM output can be repaired.
- [ ] Edit operation exists.
- [ ] Delete operation exists.
- [ ] Write operations require confirmation.
- [ ] Unit tests cover critical paths.
- [ ] Cancelled operations do not unintentionally mutate data.
- [ ] Screenshot shows the required function and repair loop.

---

# 10. Module 2 — Multimodal retrieval

---

## 10.1 M2L1 — Construct a Multimodal Vector Index

**Primary source:** `M2L1.txt`

### Objective

Build persistent vector indexes for restaurant text and food images.

### Mandatory collections

```text
restaurant_articles
food_images
```

### Text index

The source specifies:

```text
Model: Sentence-Transformers all-MiniLM-L6-v2
Dimension: 384
Domain: restaurant article representations
```

### Image index

The source specifies:

```text
Model: CLIP ViT-B/32
Dimension: 512
Domain: food recipe images
```

### Design

The two modalities are intentionally kept in separate collections.

```text
Restaurant text
    -> MiniLM
    -> 384-d vector
    -> restaurant_articles

Food image
    -> CLIP
    -> 512-d vector
    -> food_images
```

Do not assume that vectors from the two modalities can simply be mixed because they are both vectors. The project explicitly keeps modality-specific embedding spaces at this stage.

### Required document construction

Each vectorized document should preserve:

- page content
- unique document ID
- metadata

For restaurant articles, the lab specifies page content built from information including:

- restaurant name
- cuisine
- location

For images, the lab specifies recipe name as page content and metadata such as:

- image path
- cuisine
- source

### Embedding normalization

The source specifies:

- L2 normalization for text embeddings.
- L2 normalization for image embeddings.

The purpose is to make cosine-similarity behavior consistent for later retrieval work.

### Persistence requirements

The lab requires:

1. Create Chroma collections.
2. Generate embeddings.
3. Upsert vectors.
4. Store metadata.
5. Persist the database directory.
6. Reset the persistence directory before rebuilding when appropriate to avoid duplicate vectors.

Current Chroma documentation confirms collections are the core storage/query primitive and supports supplying embeddings directly. Chroma also requires query-vector dimensionality to match the collection embedding dimension.

### Screenshot requirement

**Filename:**

```text
M2L1_multimodal_vector_index.jpg
```

The screenshot must clearly show:

- creation of `restaurant_articles`
- creation of `food_images`
- final output message:

```text
Multimodal Vector Index Construction COMPLETE
```

### Acceptance checklist

- [ ] Restaurant JSON loaded.
- [ ] Image dataset loaded.
- [ ] `all-MiniLM-L6-v2` initialized.
- [ ] CLIP `ViT-B/32` initialized.
- [ ] Restaurant document objects built.
- [ ] Image document objects built.
- [ ] Text vectors are 384-dimensional.
- [ ] Image vectors are 512-dimensional.
- [ ] Required metadata is preserved.
- [ ] Vectors are normalized as required by the lab.
- [ ] Both collections are created.
- [ ] Both collections receive data.
- [ ] Persistence works.
- [ ] Re-running the build does not unintentionally duplicate entries.
- [ ] Completion message is visible.
- [ ] Screenshot is saved with the exact filename.

### Current implementation notes

The current CLIP reference implementation exposes `encode_image()` and `encode_text()` and supports loading `ViT-B/32`. The source code and README remain useful references when debugging tensor/device/preprocessing issues.

---

## 10.2 M2L2 — Similarity Retrieval with Metadata Filtering

**Primary source for submission requirements:** `Submission instruction.txt`.

### Known mandatory output

**Screenshot filename:**

```text
M2L2_similarity_retrieval.jpg
```

The screenshot must clearly show:

1. a retrieval query,
2. top-K retrieved restaurant results,
3. final output message:

```text
Similarity Retrieval with Metadata Filtering COMPLETE
```

### Important source limitation

The detailed M2L2 lab instructions were **not included in the supplied files**. Therefore this document intentionally does not invent exact query functions, filter field names, `k` values, or code structure beyond what the final submission instructions state.

### Safe implementation expectations

The implementation should support the course's stated combination of:

- similarity-based retrieval,
- metadata filtering,
- top-K results.

Current Chroma documentation confirms that metadata filters can be supplied through `where` and combined with document/vector queries.

### Acceptance checklist

- [ ] Retrieval query executes.
- [ ] Metadata filtering is applied according to the course implementation.
- [ ] Top-K restaurant results are returned.
- [ ] Results are visibly inspectable.
- [ ] Completion message is visible.
- [ ] Screenshot filename is exact.

---

## 10.3 M2L3 — Multimodal Similarity Fusion and Retrieval Ranking

**Primary source for submission requirements:** `Submission instruction.txt`.

### Known mandatory output

**Screenshot filename:**

```text
M2L3_multimodal_fusion_results.jpg
```

The screenshot must show:

- ranking results for different weight configurations,
- final completion message.

### Important source limitation

The detailed M2L3 lab file was not included in the supplied source set, so this document does not fabricate the exact fusion equation, specific weight values, variable names, or implementation API.

### Execution requirement

The implementation needs to demonstrate that text/image retrieval signals can be combined and that changing their weights changes the resulting ranking or ranking scores in the intended experiment.

### Acceptance checklist

- [ ] Multimodal retrieval results are available.
- [ ] Fusion/ranking logic is implemented.
- [ ] Multiple weight configurations are tested.
- [ ] Result rankings are printed/displayed.
- [ ] Completion message is visible.
- [ ] Screenshot contains the ranking evidence.
- [ ] Screenshot filename is exact.

---

# 11. Module 3 — Multi-agent recommendation system

---

## 11.1 M3L1 — Design Specialized Agents

**Primary source:** `M3L1.txt`

### Objective

Define six specialized agents with clear roles, goals, and backstories.

### Mandatory agents

| Agent | Responsibility |
|---|---|
| User Profile Generator | Analyze user history and preferences |
| RAG Retriever | Retrieve relevant restaurant/recipe information |
| Food Trend Analyst | Analyze food trends and emerging patterns |
| Food Style Expert | Analyze cuisine, cooking style, and flavor profiles |
| Nutrition Expert | Analyze nutrition, dietary restrictions, and allergens |
| Recommendation Expert | Synthesize all evidence into final recommendations |

### Required design fields

Each agent should define:

```text
role

goal

backstory
```

### Prompting patterns identified by the source

- ReAct (Reasoning + Acting)
- Few-shot prompting

The source also states that each task should define:

- description
- expected output
- context
- dependencies

### Screenshot requirement

**Filename:**

```text
M3L1_food_style_expert_goal.jpg
```

The screenshot must show the **Food Style Expert** configuration, including:

- role
- goal
- backstory

### Acceptance checklist

- [ ] All six agents are defined.
- [ ] Each agent has a distinct responsibility.
- [ ] No agent is overloaded with unrelated responsibilities.
- [ ] Role, goal, and backstory are defined.
- [ ] Tasks have explicit expected outputs.
- [ ] Food Style Expert screenshot is captured correctly.

---

## 11.2 M3L2 — Implement and Test Multi-Agent Recommendation System

**Primary source:** `M3L2.txt`

### Objective

Coordinate the six agents in a stateful hybrid workflow.

### Required workflow pattern

The source explicitly defines a **hybrid workflow**.

#### Phase 1 — User analysis

```text
User Profile Generator
```

Input:

- user restaurant visit history
- social media posts

Output:

- comprehensive user profile
- preferences
- dietary restrictions
- dining patterns

#### Phase 2 — Data retrieval

```text
RAG Retriever
```

Input:

- user profile

Output:

- top 20 candidate restaurants and recipes

#### Phase 3 — Parallel analysis

Run these agents independently/parallelized where the implementation supports it:

```text
Food Trend Analyst
Food Style Expert
Nutrition Expert
```

Inputs:

- user profile
- retrieved candidates

Outputs:

- trend analysis
- food-style analysis
- nutrition analysis

#### Phase 4 — Synthesis

```text
Recommendation Expert
```

Inputs:

- user profile
- retrieved candidates
- all three Phase 3 analyses

Output:

- top 5 restaurant recommendations
- top 5 recipe recommendations
- explanations

### LangGraph structure

The source defines:

- **State:** shared dictionary containing workflow information.
- **Nodes:** functions representing agent tasks.
- **Edges:** transitions between nodes.
- **Conditional edges:** optional state-based routing.
- **Graph:** complete workflow structure.

Current LangChain documentation describes LangGraph as a lower-level framework for directly building customized stateful workflows and multi-agent systems, including graph-based APIs and agent implementations.

### Testing personas

The source identifies four test personas:

1. Health-conscious user
2. Adventurous foodie
3. Budget-conscious student
4. Family with dietary restrictions

### Evaluation dimensions from the course

- Relevance
- Diversity
- Coherence
- Dietary compliance
- Timeliness

### Required screenshot

**Filename:**

```text
M3L2_node_analyze_styles.jpg
```

The screenshot must show the implementation of:

```text
node_analyze_styles
```

specifically the construction of:

```text
user_message
```

### Acceptance checklist

- [ ] Shared state structure exists.
- [ ] User profile node works.
- [ ] Retrieval node works.
- [ ] Candidate set is produced.
- [ ] Trend/style/nutrition analysis steps execute.
- [ ] The workflow reflects the required dependencies.
- [ ] Recommendation synthesis receives all required inputs.
- [ ] Four test personas are exercised.
- [ ] `node_analyze_styles` is implemented.
- [ ] `user_message` is visible in the required screenshot.
- [ ] Completion/output behavior is sensible and inspectable.

---

## 11.3 M3L3 — Build Chatbot Interface

**Primary source:** `M3L3.txt`

### Objective

Expose the recommendation system to non-technical users through a Gradio conversational interface.

### Required interface capabilities

At minimum:

- main chat area
- user input field
- clear/reset interaction

Optional features described by the source include:

- generated profile display
- progress indicators
- formatted recommendation output
- sample prompts

### Required request handling

The chatbot must be able to deal with:

1. Restaurant recommendation requests.
2. Recipe recommendation requests.
3. Follow-up questions.
4. Clarification when the user's request is ambiguous.

### Required intent classification

The source proposes these intent categories:

```text
restaurant_request
recipe_request
both
clarification
```

### Required preference extraction

The system should transform natural language into a structured preference object containing fields such as:

```text
dietary_restrictions
flavor_preferences
dining_occasion
price_range
favorite_cuisines
```

### Database-management capabilities

The source also requires the chatbot interface to support interaction with the knowledge base for:

- add restaurant
- add recipe
- update existing item
- delete item

### Implementation phases

The source describes:

1. Basic chat interface
2. Intent classification
3. Multi-agent integration
4. Output formatting
5. Database integration
6. Polish and testing

### Screenshot requirement

**Filename:**

```text
M3L3_preference_extraction_test.jpg
```

The screenshot must show the code implementation used to test `extract_preferences`.

### Acceptance checklist

- [ ] Gradio application launches.
- [ ] User can enter a message.
- [ ] Chat history works.
- [ ] Intent classification works.
- [ ] Preferences are extracted into structured data.
- [ ] Restaurant requests reach the correct workflow.
- [ ] Recipe requests reach the correct workflow.
- [ ] Follow-up interactions preserve relevant context.
- [ ] Database management operations are available as required by the lab.
- [ ] `extract_preferences` test is implemented.
- [ ] Screenshot shows the test code.

### Current Gradio implementation note

Current Gradio documentation uses `gr.Chatbot` for the conversation interface and supports a message-oriented history format with `role` and `content`. Gradio `State` provides session-oriented state management, which is relevant when preserving conversation context.

---

# 12. Module 4 — Model Context Protocol

---

## 12.1 M4L1 — Build an MCP Server

**Primary source:** `M4L1.txt`

### Objective

Wrap the existing restaurant data/search functionality in MCP so a compatible client/agent can discover and invoke it.

### Required MCP resource

Expose the raw California Culinary Map text as a named MCP resource.

Conceptually:

```text
client/agent
      |
      v
MCP resource
      |
      v
California Culinary Map raw text
```

### Required MCP tools

Three existing pieces of restaurant logic are exposed as callable MCP tools:

1. Restaurant lookup by name
2. Recommendation by vibe
3. Review retrieval

The source names the expected logical operations, and M4L2 explicitly identifies the callable tool names as:

```text
get_restaurant_info
recommend_by_vibe
get_review
```

### Required server behavior

- Register the resource.
- Register the three tools.
- Start the server locally.
- Test it with a client script.
- Verify that the tool returns a JSON-formatted result.

### Screenshot requirement

**Filename:**

```text
M4L1_Configure_Tools_Data_MCP_Server.jpg
```

The screenshot must show successful execution of a search query returning a JSON-formatted result.

### Acceptance checklist

- [ ] FastMCP/MCP server starts.
- [ ] Raw California Culinary Map resource is exposed.
- [ ] Three tools are registered.
- [ ] Tool arguments are validated appropriately.
- [ ] Test client can connect.
- [ ] Search query succeeds.
- [ ] Result is JSON-formatted.
- [ ] Screenshot proves successful execution.

---

## 12.2 M4L2 — Build an MCP Client

**Primary source:** `M4L2.txt`

### Objective

Build the client side of the MCP pair and demonstrate tool/resource discovery plus the course-required roots and sampling callbacks.

### Transport

The source specifies a client that launches the server as a subprocess and communicates over **stdio**.

### Required client setup

Use:

- `StdioServerParameters`
- `ClientSession`

Before calling tools, verify the server capabilities with:

```text
list_tools()
list_resources()
```

### Required roots callback

Implement:

```text
list_roots
```

The course describes this as declaring the filesystem directory the client is willing to share with the server, scoped to the project directory.

### Required sampling callback

Implement:

```text
handle_sampling
```

The course describes this callback as receiving prompts delegated by the MCP server, forwarding them to the Anthropic API, and returning the result.

### Required tool calls

The client must call all three server tools:

```text
get_restaurant_info
recommend_by_vibe
get_review
```

A shared helper can handle:

- session setup
- tool invocation
- JSON parsing
- output printing

### Screenshot requirement

**Filename:**

```text
M4L2_Build_Test_MCP_Client.jpg
```

The screenshot must clearly show:

- successful discovery and verification of required operational tools,
- identification of available resources,
- configured roots pointing to the correct project directory.

### Current MCP protocol compatibility note — important

Your IBM course material explicitly requires roots and sampling. However, the current MCP protocol documentation shows that **protocol revision 2026-07-28 deprecates the `roots/list` and `sampling/createMessage` surfaces**, while they remain supported for a transition period. The current MCP documentation recommends newer patterns for future integrations.

Therefore:

- **For the IBM assignment:** implement what the course requires.
- **For a future production redesign:** do not assume roots/sampling are the preferred architecture merely because they appear in this course.
- Never “modernize away” a required assignment feature before the IBM screenshot is captured.

### Acceptance checklist

- [ ] MCP server launches from client context.
- [ ] stdio connection succeeds.
- [ ] `list_tools()` succeeds.
- [ ] `list_resources()` succeeds.
- [ ] Roots callback is registered as required by course.
- [ ] Sampling callback is registered as required by course.
- [ ] All three tools can be called.
- [ ] JSON responses can be parsed.
- [ ] Project root is correct.
- [ ] Screenshot includes required discovery information.

---

## 12.3 M4L3 — Build a Full MCP Application

**Primary source:** `M4L3.txt` + `Submission instruction.txt`

### Objective

Combine the MCP server, client functionality, LLM, tool discovery, ReAct loop, and Gradio interface into a complete user-facing application.

### Required application behavior

The source describes an application that:

1. launches/connects to the MCP server,
2. discovers MCP tools dynamically,
3. converts tool schemas into the form required by the selected LLM/tool-binding layer,
4. accepts a natural-language user question,
5. lets the LLM decide which MCP tool(s) to call,
6. executes those tools,
7. feeds tool results back to the model,
8. repeats until no more tool calls are requested,
9. returns a natural-language answer,
10. presents the interaction in Gradio.

### ReAct loop

The core loop is conceptually:

```text
user message
    -> LLM
    -> tool call requested?
       | yes
       v
    MCP tool
       |
       v
    tool result
       |
       v
    LLM again
       |
       +---- repeat until no tool call
       |
       v
    final answer
```

### Required UI

The source specifies a Gradio Blocks interface containing:

- chat window
- text input
- three quick-start buttons that inject predefined prompts
- an async generator pattern for immediate feedback via a `Thinking...` placeholder

### Required MCP behavior

Do not hard-code a fixed set of tool decisions into the agent if the lab expects runtime discovery. The M4L3 description explicitly emphasizes treating the MCP server as a dynamic source of capabilities discovered at runtime.

### Screenshot requirement

**Filename:**

```text
M4L3_Design_LLM_MCP_Host.jpg
```

The submission instructions require the screenshot to clearly show:

- functional chatbot interface,
- a user query,
- corresponding agent response,
- input/navigation elements such as text entry and quick-action buttons,
- complete UI branding/layout,
- application title,
- `Built with Gradio` footer.

### Acceptance checklist

- [ ] App can launch end-to-end.
- [ ] MCP tools are discovered at runtime.
- [ ] Tool schemas are converted/bound correctly.
- [ ] ReAct loop runs.
- [ ] Agent can issue a tool call.
- [ ] Tool result returns to agent.
- [ ] Loop terminates with final natural-language answer.
- [ ] Gradio interface is functional.
- [ ] Quick-start buttons work.
- [ ] Thinking/streaming placeholder appears as required.
- [ ] UI branding is visible.
- [ ] `Built with Gradio` footer is visible.
- [ ] Q12 screenshot is captured with exact filename.

---

# 13. Final submission — Q1 through Q12

**Primary source:** `Submission instruction.txt`.

This is the most important final checklist.

| Question | Screenshot | What must be visible |
|---|---|---|
| Q1 | `M1L1_structure_for_loop.jpg` | Loop generating and validating JSON for each restaurant |
| Q2 | `M1L2_caption_all_recipes.jpg` | Vision LLM loop generating and assigning captions |
| Q3 | `M1L3_new_data_entry_process.jpg` | `new_data_entry_process`, validation, auto-repair loop |
| Q4 | `M2L1_multimodal_vector_index.jpg` | `restaurant_articles`, `food_images`, completion message |
| Q5 | `M2L2_similarity_retrieval.jpg` | Retrieval query, top-K results, completion message |
| Q6 | `M2L3_multimodal_fusion_results.jpg` | Different fusion weight rankings + completion message |
| Q7 | `M3L1_food_style_expert_goal.jpg` | Food Style Expert role, goal, backstory |
| Q8 | `M3L2_node_analyze_styles.jpg` | `node_analyze_styles`, specifically `user_message` construction |
| Q9 | `M3L3_preference_extraction_test.jpg` | Test implementation for `extract_preferences` |
| Q10 | `M4L1_Configure_Tools_Data_MCP_Server.jpg` | Successful search query returning JSON result |
| Q11 | `M4L2_Build_Test_MCP_Client.jpg` | Tool discovery, resource discovery, configured roots |
| Q12 | `M4L3_Design_LLM_MCP_Host.jpg` | Working chatbot, user query/response, inputs/buttons, branding/footer |

### Exact final screenshot list

```text
M1L1_structure_for_loop.jpg
M1L2_caption_all_recipes.jpg
M1L3_new_data_entry_process.jpg
M2L1_multimodal_vector_index.jpg
M2L2_similarity_retrieval.jpg
M2L3_multimodal_fusion_results.jpg
M3L1_food_style_expert_goal.jpg
M3L2_node_analyze_styles.jpg
M3L3_preference_extraction_test.jpg
M4L1_Configure_Tools_Data_MCP_Server.jpg
M4L2_Build_Test_MCP_Client.jpg
M4L3_Design_LLM_MCP_Host.jpg
```

### Screenshot quality rules

Even where the assignment only states that the screenshot must show specific material, use these practical rules:

- Text must be readable at normal zoom.
- Required code must not be hidden below the fold.
- Required output must be visible in the same screenshot when the instruction asks for it.
- Do not crop out the relevant variable/function/collection name.
- Avoid having unrelated terminal/browser windows obscure the result.
- Keep the screenshot filename exact.
- Verify the file opens before submission.

---

# 14. Project-wide acceptance criteria

The project is ready for final submission only when all of the following are true.

## Data layer

- [ ] Restaurant descriptions have been transformed into validated structured JSON.
- [ ] Invalid LLM JSON can be repaired.
- [ ] Recipe/image data is enriched with visual descriptions.
- [ ] Restaurant data management operations work.

## Retrieval layer

- [ ] Text vector collection exists.
- [ ] Image vector collection exists.
- [ ] Metadata is preserved.
- [ ] Persistent vector data can be loaded.
- [ ] Similarity retrieval works.
- [ ] Metadata filtering works.
- [ ] Multimodal fusion/ranking experiment works.

## Agent layer

- [ ] Six agents are defined.
- [ ] Shared state is defined.
- [ ] Hybrid workflow is implemented.
- [ ] Parallel analysis stage is represented correctly.
- [ ] Final recommendation synthesizes previous analyses.
- [ ] Test personas have been exercised.

## Chatbot layer

- [ ] Gradio chat UI runs.
- [ ] Intent classification works.
- [ ] Preference extraction works.
- [ ] Restaurant and recipe paths work.
- [ ] Follow-up context works sufficiently for the lab.
- [ ] Required database operations are available.

## MCP layer

- [ ] MCP server starts.
- [ ] MCP resource works.
- [ ] Three MCP tools work.
- [ ] MCP client discovers tools.
- [ ] MCP client discovers resources.
- [ ] Course-required roots and sampling callbacks work.
- [ ] Full MCP host application runs.
- [ ] Dynamic tool discovery/binding works.
- [ ] ReAct loop completes an end-to-end request.

## Submission layer

- [ ] Q1 screenshot exists and is readable.
- [ ] Q2 screenshot exists and is readable.
- [ ] Q3 screenshot exists and is readable.
- [ ] Q4 screenshot exists and is readable.
- [ ] Q5 screenshot exists and is readable.
- [ ] Q6 screenshot exists and is readable.
- [ ] Q7 screenshot exists and is readable.
- [ ] Q8 screenshot exists and is readable.
- [ ] Q9 screenshot exists and is readable.
- [ ] Q10 screenshot exists and is readable.
- [ ] Q11 screenshot exists and is readable.
- [ ] Q12 screenshot exists and is readable.
- [ ] Every filename exactly matches the submission specification.

---

# 15. Coding-assistant operating contract

Use the following rules when asking Claude or another coding assistant to help with this repository.

## 15.1 Context to provide

Give the assistant access to:

```text
PROJECT_SPEC.md
relevant source files/notebooks
current error/traceback
current environment/package versions
```

Do not provide only the traceback without the relevant source code.

## 15.2 Required assistant behavior

The assistant should:

1. Identify which IBM lab/task is being modified.
2. Identify the requirement the current code is supposed to satisfy.
3. Locate the failing implementation.
4. Explain the root cause briefly.
5. Make the smallest correct change.
6. Preserve existing interfaces/names where IBM requires them.
7. Show the corrected code.
8. State what to run to verify the fix.
9. State whether the change affects any screenshot requirement.

## 15.3 Do not allow silent redesigns

Do not let a coding assistant automatically replace:

- Chroma with another vector database,
- LangGraph with another orchestration library,
- CLIP with an unrelated image encoder,
- the MCP stack with a non-MCP tool system,
- Gradio with another UI framework,
- the course LLM/provider with a random local model,

unless the goal is explicitly to create an optional professional redesign after the IBM submission is complete.

## 15.4 Preferred debugging request template

```text
You are working on the IBM AI Engineering capstone.

Relevant requirement:
[PASTE THE REQUIREMENT FROM PROJECT_SPEC.md]

Lab:
[M1L1 / M1L2 / ... / M4L3]

Current code:
[PASTE CODE]

Error/output:
[PASTE EXACT ERROR OR WRONG OUTPUT]

Constraints:
- Preserve the IBM-required function/class/collection/tool names.
- Do not redesign unrelated code.
- Do not change the submission-visible output unless necessary.
- Make the smallest change that correctly fixes the issue.

Return:
1. Root cause.
2. Corrected code.
3. Verification steps.
4. Whether the IBM screenshot requirement is affected.
```

---

# 16. Testing strategy

## 16.1 Unit tests

Use unit tests around deterministic transformations and user-facing logic.

High-value unit-test areas:

- schema validation
- JSON repair helper
- restaurant parsing
- `new_data_entry_process`
- CRUD operations
- confirmation/cancellation behavior
- preference extraction
- intent classification adapter
- metadata filter construction
- score fusion calculations
- tool argument validation

## 16.2 Integration tests

Test boundaries between components:

```text
LLM -> parser -> validator

embedding -> Chroma

retrieval -> agent state

agent -> workflow

chatbot -> workflow

MCP client -> MCP server -> tool

LLM -> MCP tool -> result -> LLM
```

## 16.3 End-to-end tests

At minimum, verify:

1. One restaurant recommendation request through the agent workflow.
2. One recipe request.
3. One dietary-restriction request.
4. One MCP tool-driven request.
5. One request that requires more than one tool call.

These are engineering validation scenarios; the IBM submission screenshots remain governed by `Submission instruction.txt`.

---

# 17. Data integrity rules

## Structured JSON

Before saving a record:

```text
parse -> schema validate -> business sanity checks -> persist
```

Examples of sanity checks:

- required name present
- valid cuisine field
- valid location representation
- no accidental empty record
- IDs unique

## Multimodal links

Every recipe record that receives a generated caption should preserve the mapping:

```text
recipe ID <-> image path <-> caption
```

Do not generate captions into an unrelated record.

## Vector index integrity

Ensure the following always agree:

```text
record ID
record metadata
embedding
source document/image
```

A vector without traceable source metadata makes retrieval results difficult to interpret and debug.

---

# 18. Retrieval engineering rules

These are practical engineering constraints derived from the project architecture.

## 18.1 Query vectors must match the index dimension

Chroma requires query embedding dimensions to match the dimensions stored in the collection.

Therefore:

```text
MiniLM query -> 384 dimensions -> text collection
CLIP query   -> 512 dimensions -> image collection
```

Do not accidentally send a text embedding generated by one model into an index created by another model.

## 18.2 Metadata is not optional decoration

Metadata is part of the retrieval architecture because the project needs structured filtering.

At minimum preserve the metadata fields explicitly required by each lab.

## 18.3 Retrieval output must remain interpretable

A retrieved item should allow the application to identify:

- source record
- similarity score/distance as supported
- metadata needed for downstream processing
- enough content to explain why it was retrieved

---

# 19. Agent/workflow engineering rules

## 19.1 Agent responsibility boundaries

Each agent should have one primary responsibility.

Do not make the Nutrition Expert retrieve data, perform final synthesis, and control UI state unless the course design explicitly requires it.

## 19.2 Shared state contract

The state should have predictable fields.

A conceptual state shape may contain:

```text
user_input
user_profile
retrieved_candidates
trend_analysis
style_analysis
nutrition_analysis
final_recommendations
errors
```

The exact field names should follow the implementation already used in the course where required.

## 19.3 Parallel stage

The course explicitly intends the trend, style, and nutrition analyses to be independent after retrieval.

Keep these dependencies explicit so accidental sequential execution does not undermine the intended architecture.

---

# 20. MCP engineering rules

## 20.1 Resource vs tool

Use an MCP **resource** when the server is exposing readable contextual data.

Use an MCP **tool** when the client/agent needs to invoke an operation.

This distinction is central to the M4 architecture.

## 20.2 Tool contracts

Each tool should have:

- clear name
- clear description
- explicit input arguments
- deterministic output shape where practical
- controlled error behavior

## 20.3 Tool results

Prefer structured, predictable data over free-form prose when the calling agent needs to reason over the result.

## 20.4 Client/server separation

The client should not duplicate the server's restaurant search logic unnecessarily.

The point of the MCP layer is to expose reusable capabilities through a standardized interface.

---

# 21. Professional engineering practices that are useful without changing IBM scope

These are **engineering improvements**, not additional IBM grading requirements.

## Recommended

- Version-control the project.
- Keep secrets out of Git.
- Keep a reproducible dependency file.
- Add README setup instructions.
- Keep test fixtures small and deterministic.
- Separate data ingestion from retrieval logic.
- Separate retrieval from agent orchestration.
- Record model names and important configuration.
- Add basic logging.
- Keep interfaces between modules explicit.
- Make failures observable.
- Avoid duplicated prompt logic.
- Use schemas for structured LLM outputs.

## Optional later enhancements

These can be implemented after the IBM submission is stable:

- retrieval evaluation dataset
- reranking
- hybrid keyword + vector retrieval
- automated LLM evaluation
- tracing/observability
- token/cost accounting
- caching
- async concurrency optimization
- Dockerization
- CI/CD
- production API layer
- authentication/authorization
- security testing for prompt injection/tool abuse

Do not add these until the IBM baseline is working and all 12 screenshots can be reproduced.

---

# 22. Important security considerations

The project eventually gives an LLM access to tools, files, and data. Treat this as a real tool-using AI system rather than only a demo.

Minimum protections:

- keep secrets outside source code,
- validate tool arguments,
- limit filesystem access,
- avoid arbitrary code execution through user input,
- avoid allowing an LLM to directly choose unrestricted file paths,
- validate structured tool outputs,
- treat retrieved text and tool output as untrusted data,
- avoid blindly following instructions contained inside retrieved documents.

The MCP course's roots concept is specifically framed around scoping the filesystem context available to the server. The current MCP ecosystem has changed in this area, but the security principle remains useful: **scope access explicitly rather than granting broad filesystem authority**.

---

# 23. What not to do before submission

Do not:

- rename required screenshots,
- replace required models without a reason,
- remove the required MCP roots/sampling implementation before capturing Q11,
- remove required completion messages,
- change required collection names,
- hard-code API secrets into notebooks,
- fabricate missing M2L2/M2L3 requirements,
- assume the latest library API is identical to the API used by the IBM lab environment,
- make a large refactor just to fix a small bug,
- capture screenshots before verifying that the visible code/output actually satisfies the submission statement.

---

# 24. Final pre-submission procedure

Perform this in order.

## Step 1 — Clean environment

- [ ] Activate project environment.
- [ ] Verify Python version used for the project.
- [ ] Verify required environment variables.
- [ ] Verify dependencies import.

## Step 2 — Run the data pipeline

- [ ] M1L1 structured dataset generation succeeds.
- [ ] M1L2 image-caption enrichment succeeds.
- [ ] M1L3 CRUD/management flow succeeds.

## Step 3 — Run retrieval

- [ ] M2L1 vector index rebuild succeeds.
- [ ] M2L2 retrieval and metadata filtering succeed.
- [ ] M2L3 multimodal ranking experiment succeeds.

## Step 4 — Run agents

- [ ] M3L1 agent configurations load.
- [ ] M3L2 workflow executes.
- [ ] All required test personas are tested.
- [ ] M3L3 chatbot and preference extraction test work.

## Step 5 — Run MCP

- [ ] M4L1 server starts and tool/resource test works.
- [ ] M4L2 client connects and discovers required capabilities.
- [ ] M4L3 full application runs end-to-end.

## Step 6 — Capture screenshots

Capture each screenshot only after verifying the required content is visible.

## Step 7 — Verify screenshot filenames

Run a simple directory check and verify all 12 expected names exist.

## Step 8 — Open every screenshot

Do not rely only on filenames or file existence. Open them and check readability.

## Step 9 — Submission audit

Compare every screenshot against the Q1–Q12 table in this document and against `Submission instruction.txt`.

---

# 25. Minimal final checklist

```text
[ ] Project environment works
[ ] Secrets configured outside source code
[ ] M1L1 complete
[ ] M1L2 complete
[ ] M1L3 complete
[ ] M2L1 complete
[ ] M2L2 complete
[ ] M2L3 complete
[ ] M3L1 complete
[ ] M3L2 complete
[ ] M3L3 complete
[ ] M4L1 complete
[ ] M4L2 complete
[ ] M4L3 complete

[ ] Q1 screenshot
[ ] Q2 screenshot
[ ] Q3 screenshot
[ ] Q4 screenshot
[ ] Q5 screenshot
[ ] Q6 screenshot
[ ] Q7 screenshot
[ ] Q8 screenshot
[ ] Q9 screenshot
[ ] Q10 screenshot
[ ] Q11 screenshot
[ ] Q12 screenshot

[ ] All screenshot names exact
[ ] All screenshots readable
[ ] Required completion messages visible where required
[ ] No secrets exposed
[ ] No unverified redesigns introduced
```

---

# 26. Reference notes from current official documentation

These are **external implementation references**, not IBM submission requirements.

## IBM watsonx.ai

IBM's current developer documentation provides Python SDK/REST workflows for foundation-model inference, chat, tool calling, and agent-driven workflows. Use the exact provider/model configuration required by the course environment when reproducing IBM labs.

- IBM Developer Hub: https://www.ibm.com/docs/en/watsonx/saas?topic=developer-hub
- IBM chat API tutorial: https://www.ibm.com/docs/en/watsonx/saas?topic=code-chat
- IBM tool-calling tutorial: https://www.ibm.com/docs/en/watsonx/saas?topic=hub-call-tool-tutorial

## Chroma

Current Chroma documentation covers collections, direct embedding insertion, metadata filtering, and query dimension requirements.

- Collections: https://docs.trychroma.com/docs/collections/manage-collections
- Query/get: https://docs.trychroma.com/docs/querying-collections/query-and-get
- Metadata filtering: https://docs.trychroma.com/docs/querying-collections/metadata-filtering

## Sentence Transformers

- Documentation: https://www.sbert.net/README.html
- Installation: https://sbert.net/docs/installation.html

## OpenAI CLIP reference implementation

- Repository README: https://github.com/openai/CLIP/blob/main/README.md
- Model implementation: https://github.com/openai/CLIP/blob/main/clip/model.py

## LangChain / LangGraph

- LangChain learning documentation: https://docs.langchain.com/oss/python/learn

Use the Graph API and stateful workflow documentation for current LangGraph implementation details when adapting the course notebooks.

## Gradio

- Chatbot documentation: https://gradio.app/docs/gradio/chatbot
- State in Blocks: https://gradio.app/guides/state-in-blocks

## Model Context Protocol

- MCP specification: https://modelcontextprotocol.io/specification/
- Resources: https://modelcontextprotocol.io/specification/2026-07-28/server/resources

**Current protocol note:** the 2026-07-28 MCP revision changes/deprecates some earlier client/server capability surfaces, including roots and sampling. The IBM assignment still explicitly requires roots and sampling for Q11, so those course requirements take precedence for certification execution. Treat newer MCP behavior as a future modernization consideration, not a reason to break the required submission.

---

# 27. Final operating principle

The correct order for this project is:

```text
1. Satisfy IBM's exact lab requirements.
2. Verify the implementation works.
3. Capture the required screenshot.
4. Move to the next dependent component.
5. Complete all 12 submission artifacts.
6. Only after the submission baseline is stable, add professional AI-engineering enhancements.
```

The goal is not to build the fanciest possible system before submission. The goal is to build a **correct, reproducible, inspectable end-to-end AI engineering system**, satisfy every IBM checkpoint, and keep the architecture understandable enough that another engineer or coding assistant can work on it without guessing the project's contracts.
