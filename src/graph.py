"""Graph operations using NetworkX"""
import networkx as nx
import pandas as pd
from config import NODES_CSV_PATH, EDGES_CSV_PATH

def load_graph():
    """Load graph from CSV files"""
    # Load nodes
    nodes_df = pd.read_csv(NODES_CSV_PATH)
    
    # Load edges
    edges_df = pd.read_csv(EDGES_CSV_PATH)
    
    # Create undirected graph
    G = nx.Graph()
    
    # Add nodes with attributes
    for _, row in nodes_df.iterrows():
        node_attrs = {
            'id': row.get('id', ''),
            'description': row.get('description', ''),
            'type': row.get('type', ''),
            'domain': row.get('domain', ''),
            'gender': row.get('gender', ''),
            'aliases': row.get('aliases', ''),
            'residence': row.get('residence', ''),
            'theoi_url': row.get('theoi_url', ''),
        }
        # Use name as node identifier
        G.add_node(row['id'], **node_attrs)
    
    # Add edges (bidirectional/undirected)
    for _, row in edges_df.iterrows():
        source = row['source']
        target = row['target']
        weight = row.get('normalized_weight', 1.0)
        
        # Only add edge if both nodes exist
        if G.has_node(source) and G.has_node(target):
            G.add_edge(source, target, weight=weight)
    
    return G

def get_neighbors(graph, character_name: str) -> list:
    """Get neighbors of a character"""
    if graph.has_node(character_name):
        return list(graph.neighbors(character_name))
    return []

