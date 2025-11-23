# Technical Vision: Greek Mythology LLM Assistant

## Technologies

### Core Stack
- **Python 3.11+** - Primary programming language
- **FastAPI** - REST API backend (if needed for separation)
- **Streamlit** - Web UI framework

### LLM & RAG
- **OpenAI API** (GPT-4o-mini) - Language model for question answering
- **LangChain** - RAG orchestration and prompt management
- **FAISS** or **ChromaDB** - Vector database for embeddings (open source)

### Graph Processing
- **NetworkX** - In-memory graph data structure (no external database for MVP)
- **D3.js** or **vis-network** - Client-side graph visualization library

### Data Processing
- **Pandas** - CSV/JSON data handling
- **JSON** - Bibliotheca text storage format
- **CSV** - Kaggle Greek god dataset format

### Embeddings
- **OpenAI Embeddings API** - Text embedding generation
- Or **sentence-transformers** (open source alternative if needed)

## Development Principles

### Core Principles
- **KISS (Keep It Simple, Stupid)** - Always choose the simplest solution that works
- **MVP First** - Build minimal viable version, iterate later
- **No Premature Optimization** - Optimize only when there's a proven need
- **Single Responsibility** - Each component does one thing well
- **Open Source First** - Prefer open source tools (except OpenAI API)

### Code Quality
- **Readable over Clever** - Prioritize code clarity and maintainability
- **Minimal Dependencies** - Only include essential libraries
- **Flat Structure** - Avoid unnecessary deep nesting

### Development Approach
- **Iterative Development** - Build, test, refine in small cycles
- **Fail Fast** - Validate assumptions early

## Project Structure

```
greek-mythology-assistant/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Dependencies
├── README.md             # Setup instructions
├── .env                  # Environment variables (API keys)
├── data/
│   ├── bibliotheca.json  # Bibliotheca text data
│   └── greek_gods.csv    # Kaggle dataset
├── src/
│   ├── rag.py            # RAG logic (retrieval + LLM)
│   ├── graph.py          # Graph construction and queries
│   └── embeddings.py     # Embedding generation
├── utils/
│   └── (utility functions as needed)
└── config.py             # Configuration settings
```

## Project Architecture

### Simple 3-Layer Architecture

1. **UI Layer (Streamlit)** - User interface for questions and graph visualization
2. **Logic Layer** - RAG system and graph processing
3. **Data Layer** - Vector store (FAISS/ChromaDB) and graph (NetworkX in-memory)

### Component Flow

- User asks question → Streamlit UI
- Streamlit → RAG module (embeddings + retrieval from Bibliotheca)
- RAG → LLM (OpenAI API) with retrieved context
- Graph visualization reads from NetworkX (loaded from CSV)

### Key Simplifications

- **Single Process** - Everything runs in Streamlit (no separate backend API)
- **In-Memory Graph** - NetworkX graph loaded at startup (no database)
- **Startup Loading** - Vector store and graph loaded when app starts
- **No Persistence** - Data loaded fresh each session (sufficient for MVP)

## Data Model

### Bibliotheca Data (JSON)
- **Structure**: Array of segment objects
- **Fields**:
  - `segment_id`: Unique identifier (e.g., "segment_0000")
  - `content`: Text content of the segment
  - `book`: Book name (e.g., "Book 1")
  - `section`: Section name (e.g., "Chapter 1")
  - `section_number`: Hierarchical section identifier (e.g., "1.1.1")
  - `word_count`: Number of words
  - `char_count`: Number of characters
- **Usage**: Each segment becomes a chunk for RAG retrieval

### Greek Gods Graph Data (CSV)

**Nodes (`nodes.csv`):**
- **Primary Fields**: `id`, `name`, `description`, `type`, `domain`, `gender`, `aliases`, `residence`, `theoi_url`
- **Hierarchical Fields**: `level1` through `level5` (taxonomy levels)
- **Usage**: Nodes in NetworkX graph representing mythological characters

**Edges (`edges.csv`):**
- **Core Fields**: `source`, `target`, `normalized_weight`
- **Metadata**: Source and target character details, source references (author, title, chapter, etc.)
- **Usage**: Relationships between characters (bidirectional/undirected edges)
- **Note**: Edges contain rich metadata but we'll use source/target/weight for graph structure

### In-Memory Data Structures

**Vector Store (FAISS/ChromaDB):**
- **Content**: Bibliotheca text segments with embeddings
- **Key**: segment_id → embedding vector
- **Query**: Semantic search for relevant segments

**Graph (NetworkX):**
- **Nodes**: Character names (from nodes.csv)
- **Edges**: Undirected relationships (from edges.csv, source ↔ target)
- **Edge Attributes**: normalized_weight, metadata (optional)
- **Node Attributes**: All fields from nodes.csv stored as node attributes

### Data Loading
- **Startup**: Load JSON → create embeddings → build vector store
- **Startup**: Load CSV → build NetworkX graph (bidirectional edges)
- **No Database**: All data structures in memory

## Working with LLM

### LLM Integration
- **API**: OpenAI API (GPT-4o-mini) via LangChain
- **Pattern**: RAG (Retrieval-Augmented Generation) with Graph Context
- **Flow**: 
  1. User question → embed query
  2. Retrieve top-3 Bibliotheca segments (vector search)
  3. Extract character names from question/segments
  4. Query graph for related characters and relationships
  5. Build prompt with Bibliotheca context + graph context
  6. Call LLM → return answer

### Prompt Structure
```
You are an expert on Greek mythology based on Bibliotheca.

Context from Bibliotheca:
{retrieved_segments (top 3)}

Graph Relationships:
{related_characters and their connections from graph}

Question: {user_question}

Answer based on the provided context and relationships:
```

### LLM Configuration
- **Model**: GPT-4o-mini
- **Temperature**: 0.7 (balanced creativity/accuracy)
- **Max Tokens**: 500 (sufficient for answers)
- **Top-k Retrieval**: 3 segments from Bibliotheca

### Graph Context Integration
- Extract character names from user question and retrieved segments
- Query NetworkX graph for:
  - Direct neighbors of mentioned characters
  - Relationship types (if available in edge metadata)
- Include graph context in prompt to enhance relationship understanding

### Error Handling
- **API Failures**: Simple retry (1 attempt) or graceful error message
- **No Complex Retry Logic**: Keep it simple for MVP

## LLM Monitoring

### Basic Tracking
- **Logging**: Console output only (no file logging for MVP)
- **Track Costs**: Monitor token usage per request
- **Simple Metrics**: Log each LLM call with basic information

### Metrics Logged
- Request timestamp
- User question
- Tokens used (input + output)
- Response time
- Success/failure status

### Implementation
- Use Python logging module (console handler)
- Log after each LLM API call
- Format: Simple text output with key metrics
- No external monitoring services
- No dashboards or real-time alerts (MVP only)

## Workflows

### Application Startup
1. Load Bibliotheca JSON → parse segments
2. Generate embeddings for all segments → build vector store (FAISS/ChromaDB)
3. Load graph CSVs (nodes.csv, edges.csv) → build NetworkX graph (bidirectional)
4. Initialize Streamlit UI
5. Ready to accept questions

### User Question Workflow
1. User enters question in Streamlit UI
2. Embed question using OpenAI embeddings
3. Retrieve top-3 Bibliotheca segments (vector similarity search)
4. Extract character names from question and retrieved segments
5. Auto-select characters and query graph for related characters/neighbors
6. Build prompt with Bibliotheca context + graph relationships
7. Call LLM API (OpenAI GPT-4o-mini)
8. Log request metrics (timestamp, tokens, response time) to console
9. Display answer in UI
10. Update graph visualization with auto-selected characters and their connections

### Graph Visualization Workflow
- **Always Visible**: Graph visualization displayed on UI at all times
- **Auto-Selection**: Characters automatically selected from user question
- **Display**: Show selected characters and their neighbors/relationships
- **Interactive**: User can explore connections (zoom, pan, click nodes)
- **Update**: Graph updates automatically when new question is asked

## Deployment

### Local Development
- **Run Command**: `streamlit run app.py`
- **Dependencies**: All in `requirements.txt`
- **Environment**: `.env` file for API keys (OpenAI API key)
- **Setup**: Simple `pip install -r requirements.txt`

### Deployment Strategy (MVP)
- **Local Only**: Run on local machine for MVP testing
- **No Cloud Deployment**: Keep it simple, deploy locally
- **Future**: Can migrate to Streamlit Cloud later if needed

### Requirements
- **Python**: 3.11+
- **Dependencies**: `requirements.txt` with all packages
- **Environment Variables**: `.env` file (not committed to git)
- **Documentation**: README.md with setup instructions

### No Complex Infrastructure
- No Docker containers (unless needed later)
- No CI/CD pipelines
- No load balancing
- Single instance, local deployment

## Configuration Approach

### Configuration Method
- **Environment Variables**: `.env` file for sensitive data only (API keys)
- **Python Config File**: `config.py` for all application settings
- **No External Config**: No YAML/JSON config files for MVP

### Settings in `config.py`
- LLM model name
- Temperature
- Max tokens
- Top-k retrieval count (3)
- Vector store settings
- Graph visualization settings
- Data file paths

### Environment Variables (`.env`)
- `OPENAI_API_KEY` - Required for OpenAI API

### Configuration Structure
- Simple Python module with constants/dicts
- Import directly: `from config import LLM_MODEL, TEMPERATURE`
- No complex validation or environment-specific configs
- All settings centralized in one file

## Logging Approach

### Logging Strategy
- **Python `logging` Module**: Standard library only, no external dependencies
- **Console Output Only**: No file logging for MVP
- **Simple Format**: Timestamp, level, message

### Log Levels
- **INFO**: Normal operations (LLM calls, retrievals, graph queries)
- **ERROR**: Failures (API errors, data loading issues)
- **WARNING**: Non-critical issues

### What to Log
- LLM API calls (with metrics: tokens, response time)
- Vector store retrievals (query, top-k results)
- Graph queries (characters, relationships)
- Application startup/shutdown
- Errors and warnings

### Logging Format
- Simple text output: `[TIMESTAMP] LEVEL: Message`
- Include relevant context (question, tokens, etc.)
- No structured logging (JSON) for MVP
- No log rotation or external log aggregation
- Console handler only

