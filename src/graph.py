"""Graph operations using NetworkX"""
import networkx as nx
import pandas as pd
from pyvis.network import Network
from config import NODES_CSV_PATH, EDGES_CSV_PATH, MAX_VISUALIZATION_NODES

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
            'name': row.get('name', ''),
            'description': row.get('description', ''),
            'type': row.get('type', ''),
            'domain': row.get('domain', ''),
            'gender': row.get('gender', ''),
            'aliases': row.get('aliases', ''),
            'residence': row.get('residence', ''),
            'theoi_url': row.get('theoi_url', ''),
        }
        # Use id as node identifier
        G.add_node(row['id'], **node_attrs)
    
    # Add edges (bidirectional/undirected) with metadata
    edges_added = 0
    edges_skipped = 0
    for _, row in edges_df.iterrows():
        source = row['source']
        target = row['target']
        weight = row.get('normalized_weight', 1.0)
        
        # Only add edge if both nodes exist
        if G.has_node(source) and G.has_node(target):
            # Store edge metadata for relationship description
            edge_attrs = {
                'weight': weight,
                'title': row.get('title', ''),
                'author': row.get('author', ''),
                'chapter': row.get('chapter', ''),
            }
            G.add_edge(source, target, **edge_attrs)
            edges_added += 1
        else:
            edges_skipped += 1
    
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges ({edges_added} added, {edges_skipped} skipped)")
    return G

def get_neighbors(graph, character_name: str) -> list:
    """Get neighbors of a character"""
    if graph.has_node(character_name):
        return list(graph.neighbors(character_name))
    return []


def create_visualization(graph, max_nodes: int = MAX_VISUALIZATION_NODES, selected_nodes=None) -> str:
    """Create interactive graph visualization"""
    # Create pyvis network with optimized settings
    net = Network(
        height="600px", 
        width="100%", 
        bgcolor="#ffffff", 
        font_color="black",
        directed=False,
    )
    
    # Determine nodes to show
    degrees = dict(graph.degree())
    if selected_nodes:
        # Show selected nodes and their neighbors
        nodes_to_show = set(selected_nodes)
        for node in selected_nodes:
            if graph.has_node(node):
                neighbors = list(graph.neighbors(node))[:2]
                nodes_to_show.update(neighbors)
        nodes_to_show = list(nodes_to_show)[:max_nodes]
    else:
        # Get top nodes by degree for performance
        if not degrees:
            # If no edges, show all nodes
            nodes_to_show = list(graph.nodes())[:max_nodes]
        else:
            nodes_to_show = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            nodes_to_show = [node for node, _ in nodes_to_show]
    
    # Add nodes
    for node_id in nodes_to_show:
        if graph.has_node(node_id):
            attrs = graph.nodes[node_id]
            # Use id as label (id is the character name in nodes.csv)
            label = str(node_id)
            # Truncate long labels
            if len(label) > 20:
                label = label[:17] + "..."
            description = attrs.get('description', '')
            title = f"{label}\n{description}" if description else label
            # Size based on degree
            degree = degrees.get(node_id, 0)
            size = min(10 + degree * 2, 30)  # Scale size with degree, max 30
            
            # Highlight selected nodes
            if selected_nodes and node_id in selected_nodes:
                color = "#FF6B6B"  # Red for selected
                size = max(size, 15)  # Make selected nodes larger
            else:
                color = "#4A90E2"  # Blue for regular nodes
            
            net.add_node(str(node_id), label=label, title=title, color=color, size=size)
    
    # Add edges between shown nodes (limit to avoid performance issues)
    edge_count = 0
    max_edges = 50  # Limit total edges for performance
    edges_added = set()  # Track edges to avoid duplicates
    
    for node_id in nodes_to_show:
        if graph.has_node(node_id) and edge_count < max_edges:
            for neighbor in graph.neighbors(node_id):
                if neighbor in nodes_to_show and edge_count < max_edges:
                    # Create edge key to avoid duplicates
                    edge_key = tuple(sorted([str(node_id), str(neighbor)]))
                    if edge_key not in edges_added:
                        # Get edge attributes for description
                        edge_data = graph.get_edge_data(node_id, neighbor, {})
                        title = edge_data.get('title', '')
                        author = edge_data.get('author', '')
                        
                        # Create short label from metadata
                        label = ""
                        if title:
                            # Use short title (first 30 chars)
                            short_title = title[:30] + "..." if len(title) > 30 else title
                            label = short_title
                        elif author:
                            label = f"by {author}"
                        
                        # Add edge with label
                        net.add_edge(
                            str(node_id), 
                            str(neighbor), 
                            color="#cccccc", 
                            width=1,
                            title=label if label else "Connected",
                            label=label[:15] if label else ""  # Short label on edge
                        )
                        edges_added.add(edge_key)
                        edge_count += 1
    
    # Set optimized physics for better layout and performance
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 12
        }
      },
      "edges": {
        "smooth": false,
        "font": {
          "size": 10,
          "align": "middle"
        },
        "labelHighlightBold": false
      },
      "physics": {
        "enabled": true,
        "stabilization": {
          "enabled": true,
          "iterations": 50
        },
        "barnesHut": {
          "gravitationalConstant": -3000,
          "centralGravity": 0.3,
          "springLength": 150,
          "springConstant": 0.05,
          "damping": 0.09
        }
      }
    }
    """)
    # net.show_buttons(filter_=['nodes'])
    # Generate HTML
    return net.generate_html()

