"""RAG retrieval functions"""
import faiss
import numpy as np
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.embeddings import get_embedding
from config import EMBEDDING_DIMENSION, TOP_K, LLM_MODEL, TEMPERATURE, MAX_TOKENS

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


def generate_answer(query: str, retrieved_segments: list) -> str:
    """Generate answer using LLM with retrieved context"""
    # Build context from segments
    context = "\n\n".join([
        f"Segment {i+1} ({seg['segment'].get('book', 'Unknown')}, {seg['segment'].get('section', 'Unknown')}):\n{seg['segment'].get('content', '')}"
        for i, seg in enumerate(retrieved_segments)
    ])
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert on Greek mythology based on Bibliotheca. Only answer questions based on the provided context from Bibliotheca. If the context does not contain relevant information to answer the question, say so explicitly."),
        ("human", """Context from Bibliotheca:
{context}

Question: {question}

Answer based ONLY on the provided context. If the context does not contain enough information to answer the question, state that clearly:""")
    ])
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS
    )
    
    # Generate answer with error handling
    try:
        chain = prompt | llm
        response = chain.invoke({
            "context": context,
            "question": query
        })
        return response.content
    except Exception as e:
        # Simple retry (1 attempt)
        try:
            response = chain.invoke({
                "context": context,
                "question": query
            })
            return response.content
        except Exception as retry_error:
            raise Exception(f"LLM API error: {str(retry_error)}")

