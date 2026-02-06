"""Simple character node extraction from text."""

import re
from typing import Any


def extract_characters(text: str, graph: Any, max_characters: int = 5) -> list:
    """
    Extract graph node IDs from text by matching against:
    - the node ID (graph identifier)
    - the node attribute 'name' (when present)

    Returns a list of graph node IDs (deduped, most specific/longest matches first).
    """
    if not text or graph is None:
        return []

    text_lower = text.lower().strip()
    found_node_ids: list = []

    # Build candidate match strings for each node: (match_string, node_id)
    candidates: list[tuple[str, Any]] = []
    for node_id, attrs in graph.nodes(data=True):
        node_id_str = str(node_id).strip()
        if node_id_str:
            candidates.append((node_id_str, node_id))

        name = (attrs or {}).get("name", "")
        name_str = str(name).strip() if name is not None else ""
        if name_str and name_str != node_id_str:
            candidates.append((name_str, node_id))

    # Prefer more specific matches first
    candidates.sort(key=lambda x: len(x[0]), reverse=True)

    for match_str, node_id in candidates:
        match_lower = match_str.lower().strip()
        if not match_lower:
            continue

        # Exact word boundary match (best - most specific)
        word_pattern = r"\b" + re.escape(match_lower) + r"\b"
        if re.search(word_pattern, text_lower):
            found_node_ids.append(node_id)

    # Remove duplicates while preserving order
    seen: set = set()
    result: list = []
    for node_id in found_node_ids:
        if node_id not in seen:
            seen.add(node_id)
            result.append(node_id)

    return result[:max_characters]

