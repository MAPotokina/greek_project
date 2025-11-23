"""
Main Streamlit application for Greek Mythology Assistant
"""
import streamlit as st
import json
import pandas as pd
import numpy as np
import os
from config import (
    BIBLIOTHECA_JSON_PATH, NODES_CSV_PATH, EDGES_CSV_PATH,
    EMBEDDINGS_CACHE_PATH, TOP_K
)
from src.embeddings import get_embeddings_batch
from src.rag import VectorStore, generate_answer
from src.graph import load_graph, get_neighbors, create_visualization
import streamlit.components.v1 as components

st.title("Greek Mythology Assistant")

# Load Bibliotheca data
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
        st.info("Loading cached embeddings...")
        vector_store = load_vector_store(bibliotheca_data)
        st.success("Embeddings loaded from cache!")
    else:
        st.info("Generating embeddings (this may take a few minutes)...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(progress, current, total):
            progress_bar.progress(progress)
            status_text.text(f"Processed {current}/{total} segments")
        
        # Generate embeddings with progress
        embeddings_list = generate_embeddings(bibliotheca_data, update_progress)
        
        # Save to cache
        embeddings_array = np.array(embeddings_list)
        os.makedirs(os.path.dirname(EMBEDDINGS_CACHE_PATH), exist_ok=True)
        np.save(EMBEDDINGS_CACHE_PATH, embeddings_array)
        
        progress_bar.empty()
        status_text.empty()
        st.success("Embeddings generated and cached!")
        
        # Create vector store
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

# Display data information
st.header("Data Information")

if bibliotheca_loaded:
    st.success(f"✅ Bibliotheca Segments: {len(bibliotheca_data)}")
    if len(bibliotheca_data) > 0:
        st.write(f"First segment ID: {bibliotheca_data[0].get('segment_id', 'N/A')}")
else:
    st.error("❌ Bibliotheca data not loaded")

if graph_loaded and graph is not None:
    st.success(f"✅ Graph Nodes: {graph.number_of_nodes()}")
    st.success(f"✅ Graph Edges: {graph.number_of_edges()}")
    # Get a sample node
    if graph.number_of_nodes() > 0:
        sample_node = list(graph.nodes())[0]
        st.write(f"Sample node: {sample_node}")
else:
    st.error("❌ Graph not loaded")

# Display sample data
if bibliotheca_loaded and len(bibliotheca_data) > 0:
    with st.expander("Sample Bibliotheca Segment"):
        sample = bibliotheca_data[0]
        st.json(sample)

if graph_loaded and graph is not None and graph.number_of_nodes() > 0:
    with st.expander("Sample Graph Node"):
        sample_node = list(graph.nodes())[0]
        node_attrs = graph.nodes[sample_node]
        st.write(f"**Name:** {sample_node}")
        st.write(f"**Description:** {node_attrs.get('description', 'N/A')}")
        st.write(f"**Type:** {node_attrs.get('type', 'N/A')}")
        
    # Test graph queries
    st.subheader("Test Graph Queries")
    test_character = st.text_input("Enter character name to find neighbors:", placeholder="e.g., Zeus")
    if test_character:
        neighbors = get_neighbors(graph, test_character)
        if neighbors:
            st.write(f"**Neighbors of {test_character}:**")
            st.write(", ".join(neighbors[:10]))  # Show first 10
            if len(neighbors) > 10:
                st.write(f"... and {len(neighbors) - 10} more")
        else:
            if graph.has_node(test_character):
                st.info(f"{test_character} has no neighbors in the graph.")
            else:
                st.warning(f"{test_character} not found in the graph.")

# Graph Visualization Section (Always Visible)
if graph_loaded and graph is not None:
    st.header("Graph Visualization")
    st.write(f"Interactive graph showing relationships between mythological characters (showing top {min(100, graph.number_of_nodes())} nodes by connections)")
    st.write(f"Total nodes: {graph.number_of_nodes()}, Total edges: {graph.number_of_edges()}")
    st.info("Showing top 50 nodes by connections for performance. Graph may take a moment to stabilize.")
    
    try:
        graph_html = create_visualization(graph)
        components.html(graph_html, height=600, scrolling=False)
    except Exception as e:
        st.error(f"Error creating graph visualization: {e}")
        import traceback
        st.code(traceback.format_exc())

# Question Answering Section
if vector_store is not None:
    st.header("Ask a Question")
    
    # Question input
    query = st.text_input("Enter your question about Greek mythology:", placeholder="e.g., Who is Zeus?")
    
    if query:
        with st.spinner("Searching Bibliotheca and generating answer..."):
            # Retrieve relevant segments
            results = vector_store.search(query, k=TOP_K)
        
        if results:
            # Generate answer using LLM
            try:
                with st.spinner("Generating answer..."):
                    answer = generate_answer(query, results)
                
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
            except Exception as e:
                st.error(f"Error generating answer: {str(e)}")
                st.info("Please try again or check your API key.")
        else:
            st.warning("No relevant segments found in Bibliotheca for your question.")

