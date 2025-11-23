"""RAG retrieval functions"""
import faiss
import numpy as np
from src.embeddings import get_embedding
from config import EMBEDDING_DIMENSION, TOP_K

class VectorStore:
    def __init__(self, segments: list, embeddings: list):
        """Initialize FAISS index with embeddings"""
        self.segments = segments
        self.dimension = EMBEDDING_DIMENSION
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Convert embeddings to numpy array and add to index
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
    
    def search(self, query: str, k: int = TOP_K) -> list:
        """Search for top-k similar segments"""
        # Get query embedding
        query_embedding = get_embedding(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_vector, k)
        
        # Return segments with scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.segments):
                results.append({
                    'segment': self.segments[idx],
                    'score': float(distances[0][i])
                })
        return results

