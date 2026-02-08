"""Tests for src.rag.build_graph_context"""
import math
import networkx as nx
import pytest
from src.rag import build_graph_context


@pytest.fixture
def graph():
    """Small test graph with edge metadata."""
    G = nx.Graph()
    G.add_node("Zeus")
    G.add_node("Hera")
    G.add_node("Apollo")
    G.add_node("Athena")
    G.add_node("Poseidon")
    G.add_edge("Zeus", "Hera", weight=0.9, title="Iliad", author="Homer", chapter="Book 1")
    G.add_edge("Zeus", "Apollo", weight=0.7, title="Theogony", author="Hesiod", chapter="")
    G.add_edge("Zeus", "Athena", weight=0.8, title="Odyssey", author="Homer", chapter="Book 5")
    G.add_edge("Zeus", "Poseidon", weight=0.6, title="", author="", chapter="")
    G.add_edge("Hera", "Athena", weight=0.5, title="Iliad", author="Homer", chapter="Book 4")
    return G


def test_none_graph():
    assert build_graph_context(None, ["Zeus"]) == ""


def test_empty_selected_nodes(graph):
    assert build_graph_context(graph, []) == ""


def test_edges_between_selected_nodes(graph):
    """Edges directly connecting selected nodes should appear."""
    result = build_graph_context(graph, ["Zeus", "Hera"])
    assert "Zeus" in result
    assert "Hera" in result


def test_backfill_with_neighbors(graph):
    """When only one node is selected, backfill should add neighbor edges."""
    result = build_graph_context(graph, ["Zeus"])
    assert len(result.strip().splitlines()) > 0


def test_max_total_lines(graph):
    result = build_graph_context(graph, ["Zeus", "Hera"], max_total_lines=2)
    lines = result.strip().splitlines()
    assert len(lines) <= 2


def test_missing_node_skipped(graph):
    """A node not in the graph should be silently skipped."""
    result = build_graph_context(graph, ["NonExistent", "Zeus"])
    assert "NonExistent" not in result
    assert "Zeus" in result


def test_edge_metadata_formatting(graph):
    """Edge with metadata should include author/title info in parentheses."""
    result = build_graph_context(graph, ["Zeus", "Hera"])
    # The Zeus-Hera edge has Homer, Iliad, Book 1
    assert "Homer" in result
    assert "Iliad" in result


def test_edge_without_metadata(graph):
    """Edge with no metadata should still appear without parentheses."""
    result = build_graph_context(graph, ["Zeus", "Poseidon"])
    assert "Poseidon" in result


def test_nan_edge_attributes():
    """NaN values in edge attributes should be handled gracefully."""
    G = nx.Graph()
    G.add_node("A")
    G.add_node("B")
    G.add_edge("A", "B", weight=0.5, title=float("nan"), author=float("nan"), chapter=float("nan"))
    result = build_graph_context(G, ["A", "B"])
    assert "A" in result
    assert "B" in result
    # Should not contain 'nan'
    assert "nan" not in result.lower()


def test_no_duplicate_edges(graph):
    """Same edge should not appear twice even when both endpoints are selected."""
    result = build_graph_context(graph, ["Zeus", "Hera"])
    lines = result.strip().splitlines()
    # Check no duplicate lines
    assert len(lines) == len(set(lines))
