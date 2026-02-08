# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Run tests (when they exist — Iteration 7)
pytest
```

No build step. No linter configured. The app requires an `OPENAI_API_KEY` in a `.env` file.

## Architecture

This is a **GraphRAG Streamlit app** that answers Greek mythology questions by combining vector-searched Bibliotheca text with NetworkX graph relationships, then feeding both as context to an LLM.

### Query flow (2 external API calls per question)

1. **`app.py:157`** — user enters question in `st.text_input`
2. **`VectorStore.search()`** (`src/rag.py`) — embeds query via OpenAI (`src/embeddings.py`), FAISS L2 search returns top-3 Bibliotheca segments
3. **`extract_characters()`** (`utils/character_extraction.py`) — regex word-boundary matches query + segment text against all ~3000 graph node IDs/names, returns up to 5 node IDs
4. **`build_graph_context()`** (`src/rag.py`) — traverses NetworkX edges between/around selected nodes, formats as `"A ↔ B (author, title, chapter)"` lines (max 20)
5. **`generate_answer()`** (`src/rag.py`) — builds LangChain prompt with Bibliotheca context + graph context, calls GPT-4o-mini in JSON mode, parses `{answer, characters[]}` response
6. **`create_visualization()`** (`src/graph.py`) — PyVis renders selected nodes (red) + neighbors (blue) as interactive HTML embedded via `st.components.html()`

### Data loaded at startup (all in-memory, no database)

- `data/raw/bibliotheca_segments.json` — ~3700 text segments → FAISS index
- `data/embeddings.npy` — cached 1536-dim embeddings (regenerated if missing)
- `data/raw/nodes.csv` + `edges.csv` — ~3000 nodes, ~26k edges → NetworkX undirected graph

### Module responsibilities

| Module | Does |
|--------|------|
| `app.py` | Streamlit UI, startup loading, orchestrates query flow |
| `src/rag.py` | `VectorStore` (FAISS wrapper), `build_graph_context()`, `generate_answer()` (LangChain + OpenAI) |
| `src/embeddings.py` | `get_embedding()` / `get_embeddings_batch()` via OpenAI API |
| `src/graph.py` | `load_graph()` (CSV → NetworkX), `get_neighbors()`, `create_visualization()` (PyVis) |
| `utils/character_extraction.py` | `extract_characters()` — regex match text against graph node IDs |
| `config.py` | All constants: model names, file paths, dimensions, limits |

## Development workflow

This project follows an iterative development process defined in `doc/tasklist.md`. Iterations are completed sequentially (1→7). Currently on **Iteration 7** (polish & tests). The workflow for each iteration:

1. **Propose** solution and wait for approval
2. **Implement** only the approved approach
3. **Test** against criteria in `doc/tasklist.md`
4. **Update** `doc/tasklist.md` progress
5. **Commit** with message format: `Iteration X: brief description`

## Conventions

- All settings come from `config.py` — no hardcoded values
- API keys in `.env` only (never committed)
- KISS: simplest solution that works, no premature abstractions
- Functions ≤50 lines, single responsibility
- Flat project structure, max 3-4 levels of nesting
- Error handling: simple try/except, 1 retry max for API calls
- Console-only logging via Python `logging` module
- Reference `vision.md` for architecture decisions and `doc/tasklist.md` for current iteration scope
