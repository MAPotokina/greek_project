# Development Task List

## Progress Report

| Iteration | Status | Description | Completion Date |
|-----------|--------|-------------|-----------------|
| 1. Setup & Data Loading | ✅ Complete | Project setup, data loading, basic structure | 2024-11-23 |
| 2. Basic RAG System | ✅ Complete | Vector store, embeddings, retrieval | 2024-11-23 |
| 3. LLM Integration | ✅ Complete | OpenAI API, question answering | 2024-11-23 |
| 4. Graph Loading | ⬜ Not Started | NetworkX graph from CSV data | - |
| 5. Graph Visualization | ⬜ Not Started | Interactive graph display in UI | - |
| 6. Graph-Enhanced RAG | ⬜ Not Started | Combine graph context with RAG | - |
| 7. Monitoring & Polish | ⬜ Not Started | Logging, error handling, final touches | - |

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

- [ ] Create src/graph.py for graph operations
- [ ] Load nodes.csv into NetworkX graph
- [ ] Load edges.csv as bidirectional edges
- [ ] Store node attributes (description, type, etc.)
- [ ] Add graph info display to Streamlit (node/edge counts)
- [ ] Test: Verify graph structure, query neighbors of a character

**Test Criteria**: Graph loads correctly, can query character relationships

---

## Iteration 5: Graph Visualization

**Goal**: Display interactive graph in Streamlit UI

- [ ] Choose visualization library (vis-network or similar)
- [ ] Create graph visualization component
- [ ] Convert NetworkX graph to visualization format
- [ ] Add graph display to Streamlit UI (always visible)
- [ ] Implement basic interactivity (zoom, pan)
- [ ] Test: Graph displays correctly, can interact with nodes

**Test Criteria**: Interactive graph visible in UI, responds to user interaction

---

## Iteration 6: Graph-Enhanced RAG

**Goal**: Combine graph context with RAG for better answers

- [ ] Extract character names from user question
- [ ] Extract character names from retrieved segments
- [ ] Query graph for character neighbors and relationships
- [ ] Update prompt template to include graph context
- [ ] Auto-select characters in graph visualization
- [ ] Update graph display when question is asked
- [ ] Test: Question about character relationships uses graph context

**Test Criteria**: Answers include graph relationship information, graph updates with question

---

## Iteration 7: Monitoring & Polish

**Goal**: Add logging, improve error handling, finalize MVP

- [ ] Set up Python logging (console output)
- [ ] Log LLM calls with metrics (tokens, time)
- [ ] Log vector store retrievals
- [ ] Log graph queries
- [ ] Improve error messages for users
- [ ] Add loading indicators in UI
- [ ] Create README.md with setup instructions
- [ ] Final testing of complete workflow
- [ ] Test: Verify all features work together, logs appear in console

**Test Criteria**: Complete workflow works, all operations logged, user-friendly errors

---

## Notes

- Each iteration should be tested before moving to the next
- Keep it simple - only essential features for MVP
- Reference [vision.md](../vision.md) for architecture details
- Follow [conventions.md](../conventions.md) for code quality

