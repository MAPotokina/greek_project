"""Tests for utils.character_extraction.extract_characters"""
import networkx as nx
import pytest
from utils.character_extraction import extract_characters


@pytest.fixture
def graph():
    """Small test graph with a few mythological characters."""
    G = nx.Graph()
    G.add_node("Zeus", name="Zeus", description="King of the gods")
    G.add_node("Hera", name="Hera", description="Queen of the gods")
    G.add_node("Apollo", name="Apollo", description="God of the sun")
    G.add_node("Aphrodite", name="Aphrodite", description="Goddess of love")
    G.add_node("Ares", name="Ares", description="God of war")
    # Node whose name attribute differs from its ID
    G.add_node("Heracles", name="Hercules", description="Hero")
    G.add_edge("Zeus", "Hera")
    G.add_edge("Zeus", "Apollo")
    G.add_edge("Zeus", "Ares")
    G.add_edge("Zeus", "Aphrodite")
    return G


def test_empty_text(graph):
    assert extract_characters("", graph) == []


def test_none_graph():
    assert extract_characters("Zeus is powerful", None) == []


def test_single_match(graph):
    result = extract_characters("Tell me about Zeus", graph)
    assert "Zeus" in result


def test_case_insensitive(graph):
    result = extract_characters("tell me about zeus", graph)
    assert "Zeus" in result


def test_multiple_matches(graph):
    result = extract_characters("Zeus and Hera are married", graph)
    assert "Zeus" in result
    assert "Hera" in result


def test_word_boundary_no_partial(graph):
    """'Are' should not match node 'Ares'."""
    result = extract_characters("Are they gods?", graph)
    assert "Ares" not in result


def test_max_characters_limit(graph):
    text = "Zeus Hera Apollo Aphrodite Ares"
    result = extract_characters(text, graph, max_characters=2)
    assert len(result) <= 2


def test_name_attribute_match(graph):
    """Should match via the 'name' attribute (Hercules) and return the node ID (Heracles)."""
    result = extract_characters("Hercules was a great hero", graph)
    assert "Heracles" in result


def test_no_matches(graph):
    result = extract_characters("The weather is nice today", graph)
    assert result == []
