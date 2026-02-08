"""Graph (Pyvis iframe) styling helpers."""

from __future__ import annotations

from pathlib import Path

from config import GRAPH_BG_COLOR, GRAPH_NODE_BORDER_COLOR


def apply_graph_embed_styles(html: str, css_path: str | Path | None = None) -> str:
    """Inject CSS into the Pyvis-generated HTML (inside the iframe)."""
    if css_path is None:
        css_path = Path(__file__).resolve().parents[1] / "assets" / "graph_embed.css"
    css_file = Path(css_path)

    try:
        css = css_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return html

    css = css.replace("__GRAPH_BG_COLOR__", GRAPH_BG_COLOR)
    css = css.replace("__GRAPH_NODE_BORDER_COLOR__", GRAPH_NODE_BORDER_COLOR)

    style_tag = f"<style>\n{css}\n</style>"
    if "<head>" in html:
        return html.replace("<head>", "<head>" + style_tag, 1)
    return style_tag + html

