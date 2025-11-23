# Greek Mythology Assistant

A stand-alone application for answering questions about Greek mythology using Bibliotheca and GraphRAG.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py` - Main Streamlit application
- `config.py` - Configuration settings
- `src/` - Source modules
- `utils/` - Utility functions
- `data/raw/` - Data files (Bibliotheca JSON, graph CSVs)

