"""
Main Streamlit application for Greek Mythology Assistant
"""
import logging
import streamlit as st
import json
import numpy as np
import os
from dotenv import load_dotenv
from config import (
    BIBLIOTHECA_JSON_PATH, NODES_CSV_PATH, EDGES_CSV_PATH,
    EMBEDDINGS_CACHE_PATH, TOP_K
)
from src.embeddings import get_embeddings_batch
from src.rag import VectorStore, generate_answer
from src.graph import load_graph, get_neighbors, create_visualization
import streamlit.components.v1 as components

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

load_dotenv()

st.title("Greek Mythology Assistant")

# --- Upfront API key check ---
if not os.getenv("OPENAI_API_KEY"):
    st.error("Missing `OPENAI_API_KEY`. Add it to your `.env` file and restart the app.")
    st.stop()

# --- Load Bibliotheca data ---
try:
    with open(BIBLIOTHECA_JSON_PATH, 'r', encoding='utf-8') as f:
        bibliotheca_data = json.load(f)
    bibliotheca_loaded = True
except FileNotFoundError:
    st.error(f"Bibliotheca file not found: {BIBLIOTHECA_JSON_PATH}")
    bibliotheca_loaded = False
    bibliotheca_data = []

# Helper function to generate embeddings (no UI calls)
def generate_embeddings(segments, progress_callback=None):
    """Generate embeddings for segments"""
    texts = [segment['content'] for segment in segments]
    batch_size = 100
    embeddings_list = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = get_embeddings_batch(batch)
        embeddings_list.extend(batch_embeddings)

        if progress_callback:
            progress = (i + len(batch)) / len(texts)
            progress_callback(progress, i + len(batch), len(texts))

    return embeddings_list

# Initialize vector store
@st.cache_resource
def load_vector_store(_bibliotheca_data):
    """Load vector store from cached embeddings"""
    embeddings = np.load(EMBEDDINGS_CACHE_PATH)
    embeddings_list = embeddings.tolist()
    return VectorStore(_bibliotheca_data, embeddings_list)

# Load vector store with UI feedback
if bibliotheca_loaded and len(bibliotheca_data) > 0:
    if os.path.exists(EMBEDDINGS_CACHE_PATH):
        try:
            vector_store = load_vector_store(bibliotheca_data)
        except Exception:
            st.warning("Embeddings cache is corrupt — regenerating...")
            os.remove(EMBEDDINGS_CACHE_PATH)
            st.cache_resource.clear()
            vector_store = None
    else:
        vector_store = None

    # Generate embeddings if not loaded
    if vector_store is None:
        st.info("Generating embeddings (this may take a few minutes)...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(progress, current, total):
            progress_bar.progress(progress)
            status_text.text(f"Processed {current}/{total} segments")

        embeddings_list = generate_embeddings(bibliotheca_data, update_progress)

        # Save to cache
        embeddings_array = np.array(embeddings_list)
        os.makedirs(os.path.dirname(EMBEDDINGS_CACHE_PATH), exist_ok=True)
        np.save(EMBEDDINGS_CACHE_PATH, embeddings_array)

        progress_bar.empty()
        status_text.empty()

        vector_store = VectorStore(bibliotheca_data, embeddings_list)
else:
    vector_store = None

# Load graph
try:
    with st.spinner("Loading graph..."):
        graph = load_graph()
    graph_loaded = True
except Exception as e:
    st.error(f"Error loading graph: {e}")
    graph_loaded = False
    graph = None

# --- Sidebar: instructions, status, attribution ---
with st.sidebar:
    st.header("About")
    st.write(
        "Ask questions about Greek mythology. Answers are generated using "
        "Bibliotheca text passages and a character relationship graph."
    )

    st.subheader("How to use")
    st.write("Type a question below and press Enter. The app retrieves relevant "
             "text, queries the character graph, and generates an answer.")

    st.subheader("Data loaded")
    if bibliotheca_loaded:
        st.success(f"Bibliotheca segments: {len(bibliotheca_data)}")
    else:
        st.error("Bibliotheca data not loaded")
    if graph_loaded and graph is not None:
        st.success(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    else:
        st.error("Graph not loaded")
    if vector_store is not None:
        st.success("Vector store ready")
    else:
        st.error("Vector store not ready")

    st.divider()
    st.caption(
        "**Data sources**\n\n"
        "Text: [Bibliotheca (Pseudo-Apollodorus)](https://www.theoi.com/Text/Apollodorus1.html)\n\n"
        "Graph: [Greek Mythology Knowledge Graph (Kaggle)](https://www.kaggle.com/datasets/)"
    )

# --- Main area: Q&A ---
# Initialize session state for graph display tracking
if 'graph_shown_with_selection' not in st.session_state:
    st.session_state.graph_shown_with_selection = False

if vector_store is not None:
    st.header("Ask a Question")

    query = st.text_input("Enter your question about Greek mythology:", placeholder="e.g., Who is Zeus?")

    if query:
        with st.spinner("Searching Bibliotheca and generating answer..."):
            results = vector_store.search(query, k=TOP_K)

        if results:
            try:
                with st.spinner("Generating answer..."):
                    result = generate_answer(query, results, graph if graph_loaded else None)
                    with st.expander("Graph context"):
                        st.text(result.get("graph_context", ""))
                        st.write("Selected nodes:", result.get("selected_nodes", []))
                    answer = result.get("answer", "")
                    llm_characters = result.get("characters", [])
                    selected_characters = result.get("selected_nodes", []) or []

                # Fallback: Match LLM-extracted character names to graph nodes
                if not selected_characters and graph_loaded and graph is not None and llm_characters:
                    graph_nodes_lower = {str(node).lower(): node for node in graph.nodes()}
                    for char_name in llm_characters:
                        char_lower = char_name.lower().strip()
                        if char_lower in graph_nodes_lower:
                            selected_characters.append(graph_nodes_lower[char_lower])
                        else:
                            for node_lower, node_id in graph_nodes_lower.items():
                                if char_lower in node_lower or node_lower in char_lower:
                                    selected_characters.append(node_id)
                                    break
                    selected_characters = list(set(selected_characters))

                # Display answer
                st.subheader("Answer")
                st.write(answer)

                # Display retrieved segments
                st.subheader(f"Retrieved Segments ({len(results)})")
                for i, result in enumerate(results, 1):
                    segment = result['segment']
                    score = result['score']

                    with st.expander(f"Segment {i} (Distance: {score:.2f})"):
                        st.write(f"**Segment ID:** {segment.get('segment_id', 'N/A')}")
                        st.write(f"**Book:** {segment.get('book', 'N/A')}")
                        st.write(f"**Section:** {segment.get('section', 'N/A')}")
                        st.write(f"**Content:**")
                        st.write(segment.get('content', 'N/A'))

                # Update graph visualization with selected characters
                if graph_loaded and graph is not None and selected_characters:
                    st.subheader("Graph Visualization")
                    st.write(f"Showing characters: {', '.join([str(c) for c in selected_characters[:5]])}")
                    try:
                        with st.spinner("Rendering graph..."):
                            graph_html = create_visualization(graph, selected_nodes=selected_characters)
                        components.html(graph_html, height=600, scrolling=False)
                        st.session_state.graph_shown_with_selection = True
                    except Exception as e:
                        st.error(f"Error updating graph visualization: {e}")
                        st.session_state.graph_shown_with_selection = False
                else:
                    st.session_state.graph_shown_with_selection = False
                    if llm_characters:
                        st.info(f"LLM identified characters: {', '.join(llm_characters)}, but they weren't found in the graph.")
            except Exception as e:
                st.error(f"Error generating answer: {str(e)}")
                st.info("Please try again or check your API key.")
                st.session_state.graph_shown_with_selection = False
        else:
            st.warning("No relevant segments found in Bibliotheca for your question.")
            st.session_state.graph_shown_with_selection = False

# Graph Visualization Section (default view, only if no selection shown)
if graph_loaded and graph is not None and not st.session_state.get('graph_shown_with_selection', False):
    st.header("Graph Visualization")
    st.write("Interactive graph showing relationships between mythological characters")
    st.info("Ask a question to see relevant characters highlighted in the graph.")

    try:
        with st.spinner("Rendering graph..."):
            graph_html = create_visualization(graph)
        components.html(graph_html, height=600, scrolling=False)
    except Exception as e:
        st.error(f"Error creating graph visualization: {e}")
