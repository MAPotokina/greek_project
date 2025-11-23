"""
Main Streamlit application for Greek Mythology Assistant
"""
import streamlit as st
import json
import pandas as pd
from config import BIBLIOTHECA_JSON_PATH, NODES_CSV_PATH, EDGES_CSV_PATH

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

# Load graph data
try:
    nodes_df = pd.read_csv(NODES_CSV_PATH)
    edges_df = pd.read_csv(EDGES_CSV_PATH)
    graph_loaded = True
except FileNotFoundError as e:
    st.error(f"Graph data file not found: {e}")
    graph_loaded = False
    nodes_df = pd.DataFrame()
    edges_df = pd.DataFrame()

# Display data information
st.header("Data Information")

if bibliotheca_loaded:
    st.success(f"✅ Bibliotheca Segments: {len(bibliotheca_data)}")
    if len(bibliotheca_data) > 0:
        st.write(f"First segment ID: {bibliotheca_data[0].get('segment_id', 'N/A')}")
else:
    st.error("❌ Bibliotheca data not loaded")

if graph_loaded:
    st.success(f"✅ Graph Nodes: {len(nodes_df)}")
    st.success(f"✅ Graph Edges: {len(edges_df)}")
    if len(nodes_df) > 0:
        st.write(f"Sample node: {nodes_df.iloc[0]['name'] if 'name' in nodes_df.columns else 'N/A'}")
else:
    st.error("❌ Graph data not loaded")

# Display sample data
if bibliotheca_loaded and len(bibliotheca_data) > 0:
    with st.expander("Sample Bibliotheca Segment"):
        sample = bibliotheca_data[0]
        st.json(sample)

if graph_loaded and len(nodes_df) > 0:
    with st.expander("Sample Graph Node"):
        st.dataframe(nodes_df.head(1))

