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
MAX_VISUALIZATION_NODES = 20  # Reduced for performance
MAX_VISUALIZATION_EDGES = 10  # Limit relations shown (demo-friendly)

# Graph theme (ancient Greece-inspired)
GRAPH_BG_COLOR = "#F3E7D3"  # parchment
GRAPH_FONT_COLOR = "#2B241B"  # dark sepia
GRAPH_NODE_COLOR = "#B07A3A"  # terracotta
GRAPH_NODE_BORDER_COLOR = "#6B4A2D"  # bronze
GRAPH_NODE_HIGHLIGHT_COLOR = "#C9A227"  # gold
GRAPH_EDGE_COLOR = "#8A7A66"  # warm grey-brown

