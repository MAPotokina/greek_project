# Development Task List

## Progress Report

| Iteration | Status | Description | Completion Date |
|-----------|--------|-------------|-----------------|
| 1. Setup & Data Loading | ✅ Complete | Project setup, data loading, basic structure | 2025-11-23 |
| 2. Basic RAG System | ✅ Complete | Vector store, embeddings, retrieval | 2025-11-23 |
| 3. LLM Integration | ✅ Complete | OpenAI API, question answering | 2025-11-23 |
| 4. Graph Loading | ✅ Complete | NetworkX graph from CSV data | 2025-11-23 |
| 5. Graph Visualization | ✅ Complete | Interactive graph display in UI | 2025-11-23 |
| 6. Graph-Enhanced RAG | ✅ Complete | Add graph context to RAG answers + graph highlight | 2026-02-06 |
| 7. Presentability & Polish | ⬜ Not Started | README, robustness, light logging, minimal tests | - |

**Status Legend**: ✅ Complete | 🟡 In Progress | ⬜ Not Started | ❌ Blocked

---

## Iteration 1: Setup & Data Loading

**Goal**: Set up project structure and load data files

- [x] Create project structure (src/, utils/, data/, config.py, app.py)
- [x] Create requirements.txt with essential dependencies
- [x] Create config.py with basic settings
- [x] Create .env template for API keys
- [x] Load Bibliotheca JSON file and parse segments
- [x] Load graph CSV files (nodes.csv, edges.csv) with pandas
- [x] Create basic Streamlit app.py with data loading display
- [x] Test: Verify data loads correctly and displays in Streamlit

**Test Criteria**: App runs, shows data file info (segment count, node count, edge count)

---

## Iteration 2: Basic RAG System

**Goal**: Implement vector store and retrieval without LLM

- [x] Create src/embeddings.py for embedding generation
- [x] Generate embeddings for all Bibliotheca segments (OpenAI API)
- [x] Create vector store (FAISS or ChromaDB) with embeddings
- [x] Create src/rag.py with retrieval function
- [x] Implement top-3 segment retrieval by similarity
- [x] Add search input to Streamlit UI
- [x] Display retrieved segments in UI
- [x] Test: Enter query, verify top-3 relevant segments are retrieved

**Test Criteria**: Query returns 3 most relevant Bibliotheca segments

---

## Iteration 3: LLM Integration

**Goal**: Add OpenAI API for question answering

- [x] Integrate LangChain with OpenAI API
- [x] Create prompt template with Bibliotheca context
- [x] Implement LLM call function in src/rag.py
- [x] Add question input to Streamlit UI
- [x] Display LLM answer in UI
- [x] Add basic error handling for API calls
- [x] Test: Ask question, verify answer is generated from Bibliotheca context

**Test Criteria**: Question returns coherent answer based on retrieved segments

---

## Iteration 4: Graph Loading

**Goal**: Build NetworkX graph from CSV data

- [x] Create src/graph.py for graph operations
- [x] Load nodes.csv into NetworkX graph
- [x] Load edges.csv as bidirectional edges
- [x] Store node attributes (description, type, etc.)
- [x] Add graph info display to Streamlit (node/edge counts)
- [x] Test: Verify graph structure, query neighbors of a character

**Test Criteria**: Graph loads correctly, can query character relationships

---

## Iteration 5: Graph Visualization

**Goal**: Display interactive graph in Streamlit UI

- [x] Choose visualization library (vis-network or similar)
- [x] Create graph visualization component
- [x] Convert NetworkX graph to visualization format
- [x] Add graph display to Streamlit UI (always visible)
- [x] Implement basic interactivity (zoom, pan)
- [x] Test: Graph displays correctly, can interact with nodes

**Test Criteria**: Interactive graph visible in UI, responds to user interaction

---

## Iteration 6: Graph-Enhanced RAG

**Goal**: Combine graph context with RAG for better answers

- [x] Extract candidate character names via LLM JSON output (already used for graph highlighting)
- [x] Auto-select characters in graph visualization (selected nodes highlighted)
- [x] Update graph display when question is asked
- [x] Extract character names deterministically from question + retrieved segments (match against graph nodes)
- [x] Normalize / map extracted names → graph node IDs (match against node IDs + node attribute `name`)
- [x] Query graph for neighbors + relationship metadata (edge attributes where available)
- [x] Update LLM prompt to include a “Graph Relationships” context block (GraphRAG core)
- [ ] (Stretch) Second-pass retrieval: add extra Bibliotheca segments mentioning graph-neighbors
- [x] Test: relationship questions include at least one graph-derived relationship when available; highlighted nodes match extracted characters

**Test Criteria**: Answers incorporate graph-derived relationships when relevant, and the graph highlights the same characters used to build graph context

---

## Iteration 7: Presentability & Polish

**Goal**: Make the project robust + demo-ready (docs, UX, basic tests, light logging)

- [ ] Add sidebar instructions + clear “what’s loaded” status + dataset attribution
- [ ] Improve user-facing errors (missing API key, missing/corrupt embeddings cache, missing CSV columns)
- [ ] Add loading indicators where useful (keep it simple)
- [ ] Add light console logging for retrieval + graph query + LLM call duration (no heavy monitoring)
- [ ] Add minimal pytest tests for critical functions (character extraction, graph context builder)
- [ ] Expand README: features, usage, screenshot/GIF, env vars, deployment notes (Streamlit Community Cloud)
- [ ] Final manual demo checklist (fresh venv, clean run, one good example Q&A)

**Test Criteria**: A clean end-to-end demo run works reliably; README is presentable; a small test suite passes

---

## Notes

- Each iteration should be tested before moving to the next
- Keep it simple - only essential features for MVP
- Reference [vision.md](../vision.md) for architecture details
- Follow [conventions.md](../conventions.md) for code quality

