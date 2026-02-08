"""Graph operations using NetworkX"""
import logging
import networkx as nx
import pandas as pd
from pyvis.network import Network
from config import (
    NODES_CSV_PATH,
    EDGES_CSV_PATH,
    MAX_VISUALIZATION_NODES,
    MAX_VISUALIZATION_EDGES,
    GRAPH_BG_COLOR,
    GRAPH_FONT_COLOR,
    GRAPH_NODE_COLOR,
    GRAPH_NODE_BORDER_COLOR,
    GRAPH_NODE_HIGHLIGHT_COLOR,
    GRAPH_EDGE_COLOR,
)
from utils.graph_style import apply_graph_embed_styles

logger = logging.getLogger(__name__)

def load_graph():
    """Load graph from CSV files"""
    # Load nodes
    nodes_df = pd.read_csv(NODES_CSV_PATH)
    if 'id' not in nodes_df.columns:
        raise ValueError(f"nodes.csv missing required column 'id'. Found: {list(nodes_df.columns)}")

    # Load edges
    edges_df = pd.read_csv(EDGES_CSV_PATH)
    for col in ('source', 'target'):
        if col not in edges_df.columns:
            raise ValueError(f"edges.csv missing required column '{col}'. Found: {list(edges_df.columns)}")
    
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
    
    logger.info("Graph loaded: %d nodes, %d edges (%d added, %d skipped)", G.number_of_nodes(), G.number_of_edges(), edges_added, edges_skipped)
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
        bgcolor=GRAPH_BG_COLOR,
        font_color=GRAPH_FONT_COLOR,
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
        # Keep selected nodes first (more deterministic edge rendering)
        ordered = []
        for n in selected_nodes:
            if n in nodes_to_show and n not in ordered:
                ordered.append(n)
        for n in nodes_to_show:
            if n not in ordered:
                ordered.append(n)
        nodes_to_show = ordered[:max_nodes]
    else:
        # Get top nodes by degree for performance
        if not degrees:
            # If no edges, show all nodes
            nodes_to_show = list(graph.nodes())[:max_nodes]
        else:
            nodes_to_show = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            nodes_to_show = [node for node, _ in nodes_to_show]

    # Decide which edges to render first (cap to MAX_VISUALIZATION_EDGES)
    max_edges = MAX_VISUALIZATION_EDGES
    edges_seen: set[tuple[str, str]] = set()
    edges_to_add: list[tuple[str, str, dict]] = []

    node_iteration = nodes_to_show
    if selected_nodes:
        node_iteration = list(selected_nodes) + [n for n in nodes_to_show if n not in selected_nodes]

    nodes_to_show_set = set(nodes_to_show)
    for node_id in node_iteration:
        if not graph.has_node(node_id) or len(edges_to_add) >= max_edges:
            continue
        for neighbor in graph.neighbors(node_id):
            if neighbor not in nodes_to_show_set or len(edges_to_add) >= max_edges:
                continue
            a, b = sorted([str(node_id), str(neighbor)])
            key = (a, b)
            if key in edges_seen:
                continue
            edges_seen.add(key)
            edge_data = graph.get_edge_data(node_id, neighbor, {}) or {}
            edges_to_add.append((str(node_id), str(neighbor), edge_data))

    # Remove isolated nodes: only render nodes that participate in at least one rendered edge
    connected_nodes: set[str] = set()
    for a, b, _ in edges_to_add:
        connected_nodes.add(a)
        connected_nodes.add(b)

    nodes_to_render = [n for n in nodes_to_show if str(n) in connected_nodes]
    
    # Add nodes
    for node_id in nodes_to_render:
        if graph.has_node(node_id):
            attrs = graph.nodes[node_id]
            # Prefer human-readable name attribute when present
            display_name = attrs.get("name") or node_id
            label = str(display_name)
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
                color = GRAPH_NODE_HIGHLIGHT_COLOR  # Gold highlight
                size = max(size, 15)  # Make selected nodes larger
            else:
                color = GRAPH_NODE_COLOR  # Terracotta

            net.add_node(
                str(node_id),
                label=label,
                title=title,
                color={
                    "background": color,
                    "border": GRAPH_NODE_BORDER_COLOR,
                    "highlight": {"background": GRAPH_NODE_HIGHLIGHT_COLOR, "border": GRAPH_NODE_BORDER_COLOR},
                },
                borderWidth=2,
                size=size,
                font={"face": "Georgia", "color": GRAPH_FONT_COLOR},
            )
    
    # Add selected edges (already capped); endpoints are already filtered to connected nodes
    for a, b, edge_data in edges_to_add:
        if a not in connected_nodes or b not in connected_nodes:
            continue

        title = (edge_data.get("title", "") or "")
        author = (edge_data.get("author", "") or "")

        # Create short label from metadata
        label = ""
        if title:
            short_title = title[:30] + "..." if len(title) > 30 else title
            label = short_title
        elif author:
            label = f"by {author}"

        net.add_edge(
            a,
            b,
            color=GRAPH_EDGE_COLOR,
            width=1,
            title=label if label else "Connected",
            label=label[:15] if label else "",
            font={"face": "Georgia", "size": 10, "color": GRAPH_FONT_COLOR},
        )
    
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
        "color": {
          "inherit": false
        },
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
          "gravitationalConstant": -2400,
          "centralGravity": 0.25,
          "springLength": 170,
          "springConstant": 0.04,
          "damping": 0.12
        }
      }
    }
    """)
    # net.show_buttons(filter_=['nodes'])
    # Generate HTML
    html = net.generate_html()

    return apply_graph_embed_styles(html)

