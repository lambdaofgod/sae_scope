"""Data tab UI and event handlers."""

from typing import Any

import gradio as gr
import pandas as pd

from sae_scope.backend.dataset import SAELensDataset
from sae_scope.backend.retriever import SearchMode
from sae_scope.backend.retriever.interp_embed import InterpEmbedRetriever
from sae_scope.frontend.components.html_table import HTMLTableElement
from sae_scope.frontend.components.search_component import create_search_ui


def create_data_ui() -> dict[str, Any]:
    """
    Create the Data tab UI components.

    Returns:
        Dictionary of component references.
    """
    with gr.Tab("Data") as tab:
        gr.Markdown("### Search Texts")
        search_components = create_search_ui(
            placeholder="Type to search texts...",
            default_mode="Hybrid",
            default_k=10,
            results_label="Text Search Results",
        )

        with gr.Accordion("All Data", open=False):
            dataframe = gr.HTML(label="Text Data")

    return {
        "tab": tab,
        "dataframe": dataframe,
        # Search components
        "search_mode": search_components["search_mode"],
        "max_results": search_components["max_results"],
        "query": search_components["query"],
        "search_btn": search_components["search_btn"],
        "search_results": search_components["results"],
    }


def wire_data_events(
    components: dict[str, Any],
    state: dict[str, Any],
    get_interp_retriever: callable,
    get_texts_collection: callable,
) -> None:
    """
    Wire event handlers for Data tab components.

    Args:
        components: Dictionary of Data tab component references.
        state: Dictionary containing shared state (current_dataset, selected_columns).
        get_interp_retriever: Callable that returns the current InterpEmbedRetriever instance.
        get_texts_collection: Callable that returns the current texts collection name.
    """
    import time

    def update_data_table(
        dataset: SAELensDataset | None,
        selected_columns: list[str],
    ) -> str:
        """Update data table with dataset texts and selected columns."""
        start = time.time()
        print("[TIMING] update_data_table START")

        if dataset is None:
            print(
                f"[TIMING] update_data_table END (no dataset): {time.time() - start:.3f}s"
            )
            return HTMLTableElement(None).html()

        t0 = time.time()
        # Get the text field name and build column list
        # Selected columns come BEFORE text column
        text_field = dataset.get_text_field()
        columns_to_show = list(selected_columns) if selected_columns else []
        columns_to_show.append(text_field)

        result = dataset.get_dataframe_with_columns(columns_to_show)
        print(f"[TIMING]   get_dataframe_with_columns: {time.time() - t0:.3f}s")

        print(f"[TIMING] update_data_table END: {time.time() - start:.3f}s")
        return HTMLTableElement(result).html()

    def on_text_search(
        query: str,
        search_mode: str,
        max_results: int,
        dataset: SAELensDataset | None,
        selected_columns: list[str],
    ) -> str:
        """Handle text search button click."""
        start = time.time()
        print(
            f"[TIMING] on_text_search START query={query!r} mode={search_mode} k={max_results}"
        )

        if dataset is None:
            print(f"[TIMING] on_text_search END (no dataset): {time.time() - start:.3f}s")
            return HTMLTableElement(None).html()

        interp_retriever = get_interp_retriever()
        texts_collection = get_texts_collection()

        if interp_retriever is None or texts_collection is None:
            print(f"[TIMING] on_text_search END (no retriever/collection): {time.time() - start:.3f}s")
            return HTMLTableElement(None).html()

        if not query.strip():
            print(f"[TIMING] on_text_search END (empty query): {time.time() - start:.3f}s")
            return HTMLTableElement(None).html()

        mode = SearchMode[search_mode.upper()]
        result_df = interp_retriever.search_texts_by_query(
            query,
            mode,
            int(max_results),
            selected_columns=selected_columns if selected_columns else None,
            texts_collection=texts_collection,
        )

        print(f"[TIMING] on_text_search END: {time.time() - start:.3f}s")
        return HTMLTableElement(result_df).html()

    # Wire data tab select event (for accordion data)
    components["tab"].select(
        fn=update_data_table,
        inputs=[state["current_dataset"], state["selected_columns"]],
        outputs=[components["dataframe"]],
    )

    # Wire text search button
    components["search_btn"].click(
        fn=on_text_search,
        inputs=[
            components["query"],
            components["search_mode"],
            components["max_results"],
            state["current_dataset"],
            state["selected_columns"],
        ],
        outputs=[components["search_results"]],
    )
