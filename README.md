# Greek Mythology Assistant

A Streamlit application that answers questions about Greek mythology using **GraphRAG** — combining Bibliotheca text retrieval with a character relationship graph to generate LLM-powered answers.

## Features

- **Retrieval-Augmented Generation** — Embeds your question, retrieves the most relevant Bibliotheca passages via FAISS vector search, and feeds them as context to GPT-4o-mini.
- **Graph-Enhanced Context** — Extracts character names from your question, queries a NetworkX knowledge graph (~3 000 characters, ~26 000 relationships), and includes relationship data in the LLM prompt.
- **Interactive Graph Visualization** — PyVis renders an interactive graph highlighting the characters relevant to your question.
- **Sidebar Status** — Shows what data is loaded, usage instructions, and dataset attribution.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file** with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   On first run, embeddings are generated for all Bibliotheca segments (takes a few minutes) and cached to `data/embeddings.npy`.

## Usage

Type a question in the input field and press Enter. Example:

> **Who were the children of Zeus and Hera?**

The app will:
1. Retrieve the 3 most relevant Bibliotheca passages
2. Extract character names and query the relationship graph
3. Generate an answer using GPT-4o-mini
4. Display an interactive graph of the relevant characters

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings and chat completions |

All other settings (model name, temperature, top-k, file paths) are in `config.py`.

## Running Tests

```bash
pytest tests/
```

## Project Structure

```
├── app.py                # Streamlit UI and orchestration
├── config.py             # All configuration constants
├── src/
│   ├── rag.py            # VectorStore (FAISS), graph context builder, LLM answer generation
│   ├── embeddings.py     # OpenAI embedding API calls
│   └── graph.py          # NetworkX graph loading + PyVis visualization
├── utils/
│   └── character_extraction.py  # Regex-based character name extraction
├── tests/                # Pytest tests for character extraction and graph context
├── data/
│   ├── raw/              # Source data (Bibliotheca JSON, nodes/edges CSV)
│   └── embeddings.npy    # Cached embeddings (auto-generated)
└── doc/                  # Design documents (vision.md, tasklist.md)
```

## Deployment (Streamlit Community Cloud)

1. Push the repository to GitHub (ensure `.env` is in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repository.
3. Set `OPENAI_API_KEY` in the app's **Secrets** settings.
4. Deploy — the app will install dependencies from `requirements.txt` automatically.

**Note:** The `data/` directory is in `.gitignore` by default. For cloud deployment, either remove it from `.gitignore` or host the data files separately.
