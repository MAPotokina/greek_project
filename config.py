# Configuration settings for Greek Mythology Assistant

# Data file paths
BIBLIOTHECA_JSON_PATH = "data/raw/bibliotheca_segments.json"
NODES_CSV_PATH = "data/raw/nodes.csv"
EDGES_CSV_PATH = "data/raw/edges.csv"

# Embedding settings
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536  # For text-embedding-3-small
EMBEDDINGS_CACHE_PATH = "data/embeddings.npy"

# LLM settings (for future iterations)
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.7
MAX_TOKENS = 500
TOP_K = 3

# Graph visualization settings
MAX_VISUALIZATION_NODES = 10  # Reduced for performance

