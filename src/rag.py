"""RAG retrieval functions"""
import faiss  # type: ignore
import numpy as np
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.embeddings import get_embedding
from config import EMBEDDING_DIMENSION, TOP_K, LLM_MODEL, TEMPERATURE, MAX_TOKENS
from utils.character_extraction import extract_characters

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


def build_graph_context(
    graph,
    selected_nodes: list,
    max_neighbors_per_node: int = 4,
    max_total_lines: int = 20,
) -> str:
    """Build a compact, prompt-friendly summary of graph relationships for selected nodes."""
    if graph is None or not selected_nodes:
        return ""

    def _safe_str(value) -> str:
        if value is None:
            return ""
        if isinstance(value, float) and np.isnan(value):
            return ""
        return str(value).strip()

    selected_set = set(selected_nodes)

    def _format_edge(a, b) -> str:
        edge_data = graph.get_edge_data(a, b, {}) or {}
        title = _safe_str(edge_data.get("title", ""))
        author = _safe_str(edge_data.get("author", ""))
        chapter = _safe_str(edge_data.get("chapter", ""))
        meta = ", ".join([x for x in [author, title, chapter] if x])
        if meta:
            return f"{a} ↔ {b} ({meta})"
        return f"{a} ↔ {b}"

    lines: list[str] = []

    # 1) Prefer edges directly between selected nodes (most relevant to the user's question).
    edges_seen: set[tuple[str, str]] = set()
    for node_id in selected_nodes:
        if not graph.has_node(node_id):
            continue
        for neighbor in graph.neighbors(node_id):
            if neighbor not in selected_set:
                continue
            a, b = sorted([str(node_id), str(neighbor)])
            key = (a, b)
            if key in edges_seen:
                continue
            edges_seen.add(key)
            lines.append(_format_edge(node_id, neighbor))
            if len(lines) >= max_total_lines:
                return "\n".join(lines)

    # 2) Backfill with a few high-weight neighbors per selected node.
    for node_id in selected_nodes:
        if not graph.has_node(node_id):
            continue

        neighbors = list(graph.neighbors(node_id))
        neighbors = sorted(
            neighbors,
            key=lambda n: (graph.get_edge_data(node_id, n, {}) or {}).get("weight", 0),
            reverse=True,
        )[:max_neighbors_per_node]

        for neighbor in neighbors:
            a, b = sorted([str(node_id), str(neighbor)])
            key = (a, b)
            if key in edges_seen:
                continue
            edges_seen.add(key)
            lines.append(_format_edge(node_id, neighbor))

            if len(lines) >= max_total_lines:
                break

        if len(lines) >= max_total_lines:
            break

    return "\n".join(lines)


def generate_answer(query: str, retrieved_segments: list, graph=None) -> dict:
    """Generate answer using LLM with retrieved context. Returns dict with 'answer' and 'characters'."""
    # Build context from segments
    context = "\n\n".join([
        f"Segment {i+1} ({seg['segment'].get('book', 'Unknown')}, {seg['segment'].get('section', 'Unknown')}):\n{seg['segment'].get('content', '')}"
        for i, seg in enumerate(retrieved_segments)
    ])

    selected_nodes: list = []
    graph_context = ""
    if graph is not None:
        # Priority: characters explicitly mentioned in the user question.
        question_nodes = extract_characters(query, graph, max_characters=5)

        # Backfill (only if needed): add characters found in retrieved segments.
        if len(question_nodes) < 5:
            segments_text = "\n\n".join(
                (seg.get("segment", {}) or {}).get("content", "") for seg in retrieved_segments
            )
            segment_nodes = extract_characters(segments_text, graph, max_characters=25)
            for node_id in segment_nodes:
                if node_id not in question_nodes:
                    question_nodes.append(node_id)
                if len(question_nodes) >= 5:
                    break

        selected_nodes = question_nodes
        graph_context = build_graph_context(graph, selected_nodes)
    graph_context_for_prompt = graph_context if graph_context else "None"
    
    # Create prompt template with structured output request
    prompt_template = """Context from Bibliotheca:
{context}

Graph Relationships (from character network):
{graph_context}

Question: {question}

Provide your response as a JSON object with two fields:
1. "answer": Your answer based on the provided context. If the context does not contain enough information, state that clearly.
2. "characters": A list of Greek mythological character names mentioned in the question or your answer (use exact names as they appear in Greek mythology, e.g., "Zeus", "Aphrodite", "Heracles").
Limit the character list to exactly five characters that are most relevant to the question.

Return ONLY valid JSON, no other text. Format:
{{
  "answer": "your answer here",
  "characters": ["Character1", "Character2"]
}}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert on Greek mythology based on Bibliotheca. Return responses as JSON only."),
        ("human", prompt_template)
    ])
    
    # Initialize LLM with JSON mode.
    # NOTE: Some langchain-openai versions don't expose these kwargs in type stubs,
    # but they work at runtime. Keep the ignore narrow to this call-site.
    llm = ChatOpenAI(  # type: ignore[call-arg]
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    chain = prompt | llm
    payload = {
        "context": context,
        "graph_context": graph_context_for_prompt,
        "question": query,
    }
    
    # Generate answer with error handling
    try:
        response = chain.invoke(payload)
        
        # Parse JSON response
        try:
            result = json.loads(str(response.content))
            answer = result.get("answer", "No answer provided.")
            characters = result.get("characters", [])
            return {
                "answer": answer,
                "characters": characters,
                "selected_nodes": selected_nodes,
                "graph_context": graph_context,
            }
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            content = str(response.content).strip()
            # Try to find JSON in the response
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                result = json.loads(content)
                answer = result.get("answer", "No answer provided.")
                characters = result.get("characters", [])
                return {
                    "answer": answer,
                    "characters": characters,
                    "selected_nodes": selected_nodes,
                    "graph_context": graph_context,
                }
            except json.JSONDecodeError:
                # Last resort: return raw content as answer
                return {
                    "answer": response.content,
                    "characters": [],
                    "selected_nodes": selected_nodes,
                    "graph_context": graph_context,
                }
    except Exception:
        # Simple retry (1 attempt)
        try:
            response = chain.invoke(payload)
            result = json.loads(str(response.content))
            answer = result.get("answer", "No answer provided.")
            characters = result.get("characters", [])
            return {
                "answer": answer,
                "characters": characters,
                "selected_nodes": selected_nodes,
                "graph_context": graph_context,
            }
        except Exception as retry_error:
            raise Exception(f"LLM API error: {str(retry_error)}")

