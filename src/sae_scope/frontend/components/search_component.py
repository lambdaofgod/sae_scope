"""Reusable search UI component."""

from typing import Any

import gradio as gr


def create_search_ui(
    placeholder: str = "Type to search...",
    default_mode: str = "Hybrid",
    default_k: int = 10,
    results_label: str = "Results",
) -> dict[str, Any]:
    """
    Create reusable search UI components.

    This factory function creates a standardized search UI that can be used
    for both feature search and text search.

    Args:
        placeholder: Placeholder text for the query input.
        default_mode: Default search mode ("Lexical", "Vector", or "Hybrid").
        default_k: Default maximum number of results.
        results_label: Label for the results dataframe.

    Returns:
        Dictionary with Gradio component references:
        - search_mode: Dropdown for search mode selection
        - max_results: Number input for result limit
        - query: Textbox for search query
        - search_btn: Search button
        - results: HTML component for displaying results
    """
    with gr.Row():
        search_mode = gr.Dropdown(
            label="Search Mode",
            choices=["Lexical", "Vector", "Hybrid"],
            value=default_mode,
            interactive=True,
        )
        max_results = gr.Number(
            label="Max Results",
            value=default_k,
            minimum=1,
            maximum=100,
            step=1,
            interactive=True,
        )
    query = gr.Textbox(
        label="Query",
        placeholder=placeholder,
    )
    search_btn = gr.Button("Search")
    results = gr.HTML(label=results_label)

    return {
        "search_mode": search_mode,
        "max_results": max_results,
        "query": query,
        "search_btn": search_btn,
        "results": results,
    }
