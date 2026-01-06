"""Features tab UI and event handlers."""

from typing import Any

import gradio as gr
import pandas as pd

from sae_scope.backend.dataset import SAELensDataset
from sae_scope.backend.retriever import SearchMode, WeaviateRetriever
from sae_scope.frontend.components.search_component import create_search_ui


def get_summary_stats(dataset: SAELensDataset | None) -> pd.DataFrame | None:
    """
    Get summary statistics (describe()) for feature statistics columns.

    Args:
        dataset: Current dataset or None.

    Returns:
        DataFrame with describe() output for frequency, std, max columns.
    """
    if dataset is None:
        return None

    stats = dataset._feature_stats
    return stats[["frequency", "std", "max"]].describe()


def get_top_n_features(
    dataset: SAELensDataset | None,
    n: int,
    sort_by: str,
) -> pd.DataFrame | None:
    """
    Get top N features sorted by a specific metric.

    Args:
        dataset: Current dataset or None.
        n: Number of top features to return.
        sort_by: Column name to sort by ("frequency", "std", or "max").

    Returns:
        DataFrame with columns: index, label, and the sort metric.
    """
    if dataset is None:
        return None

    stats = dataset._feature_stats
    sorted_stats = stats.sort_values(by=sort_by, ascending=False).head(n)
    return sorted_stats[["index", "label", sort_by]].reset_index(drop=True)


def search_features(
    query: str,
    dataset: SAELensDataset | None,
    retriever: WeaviateRetriever | None,
    search_mode: str = "Lexical",
    k: int = 10,
) -> list[list[str | int]]:
    """
    Search features and return results for dataframe display.

    Args:
        query: Search query string.
        dataset: Current dataset or None.
        retriever: Weaviate retriever instance or None.
        search_mode: Search mode ("Lexical", "Vector", or "Hybrid").
        k: Maximum number of results to return.

    Returns:
        List of [index, label] pairs for matching features.
    """
    if dataset is None:
        return []

    if not query.strip():
        # Show first k features when no search query
        results = [
            (i, dataset.features.labels[i])
            for i in range(min(k, len(dataset.features)))
        ]
        return [[idx, label] for idx, label in results]

    # Use retriever if available
    if retriever is not None:
        mode = SearchMode[search_mode.upper()]
        search_results = retriever.search(query, mode, k=k)
        return [[r.index, r.label] for r in search_results]

    # Fallback to basic search if retriever not available
    results = dataset.features.search(query)[:k]
    return [[idx, label] for idx, label in results]


def create_features_ui() -> dict[str, Any]:
    """
    Create the Features tab UI components.

    Returns:
        Dictionary of component references.
    """
    with gr.Tab("Features") as tab:
        with gr.Accordion("Feature Statistics", open=True):
            summary_stats_df = gr.Dataframe(
                label="Summary Statistics",
                interactive=False,
                wrap=True,
            )
            top_n_input = gr.Number(
                label="Top N Features",
                value=10,
                precision=0,
                minimum=1,
                maximum=100,
            )
            top_by_frequency = gr.Dataframe(
                headers=["Index", "Label", "Frequency"],
                label="Top N by Frequency (normalized 0-1)",
                interactive=False,
                wrap=True,
            )
            top_by_std = gr.Dataframe(
                headers=["Index", "Label", "Std Dev"],
                label="Top N by Std Dev",
                interactive=False,
                wrap=True,
            )
            top_by_max = gr.Dataframe(
                headers=["Index", "Label", "Max Value"],
                label="Top N by Max Value",
                interactive=False,
                wrap=True,
            )

        with gr.Accordion("Search Features", open=False):
            search_components = create_search_ui(
                placeholder="Type to search feature labels...",
                default_mode="Lexical",
                default_k=10,
                results_label="Feature Search Results",
            )

    return {
        "tab": tab,
        "summary_stats_df": summary_stats_df,
        "top_n_input": top_n_input,
        "top_by_frequency": top_by_frequency,
        "top_by_std": top_by_std,
        "top_by_max": top_by_max,
        # Search components (aliased for backward compatibility)
        "search_mode_dropdown": search_components["search_mode"],
        "feature_search_input": search_components["query"],
        "search_results_limit": search_components["max_results"],
        "feature_search_button": search_components["search_btn"],
        "feature_results": search_components["results"],
    }


def wire_features_events(
    components: dict[str, Any],
    state: dict[str, Any],
    get_retriever: callable,
) -> None:
    """
    Wire event handlers for Features tab components.

    Args:
        components: Dictionary of Features tab component references.
        state: Dictionary containing shared state (current_dataset).
        get_retriever: Callable that returns the current WeaviateRetriever instance.
    """
    import time

    def on_top_n_change(
        n: int,
        dataset: SAELensDataset | None,
    ) -> tuple:
        """
        Handle Top N input change.

        Args:
            n: Number of top features to display.
            dataset: Current dataset or None.

        Returns:
            Tuple of (top_by_frequency, top_by_std, top_by_max).
        """
        if dataset is None:
            return None, None, None

        n = int(n)
        return (
            get_top_n_features(dataset, n, "frequency"),
            get_top_n_features(dataset, n, "std"),
            get_top_n_features(dataset, n, "max"),
        )

    def on_feature_search_change(
        query: str,
        search_mode: str,
        k: int,
        dataset: SAELensDataset | None,
    ) -> list[list[str | int]]:
        """
        Handle feature search button click.

        Args:
            query: Search query string.
            search_mode: Selected search mode.
            k: Maximum number of results.
            dataset: Current dataset or None.

        Returns:
            List of [index, label] pairs for display.
        """
        start = time.time()
        print(
            f"[TIMING] on_feature_search_change START query={query!r} mode={search_mode} k={k}"
        )

        retriever = get_retriever()
        results = search_features(query, dataset, retriever, search_mode, int(k))

        print(f"[TIMING] on_feature_search_change END: {time.time() - start:.3f}s")
        return results

    # Wire top N input
    components["top_n_input"].change(
        fn=on_top_n_change,
        inputs=[components["top_n_input"], state["current_dataset"]],
        outputs=[
            components["top_by_frequency"],
            components["top_by_std"],
            components["top_by_max"],
        ],
    )

    # Wire feature search
    components["feature_search_button"].click(
        fn=on_feature_search_change,
        inputs=[
            components["feature_search_input"],
            components["search_mode_dropdown"],
            components["search_results_limit"],
            state["current_dataset"],
        ],
        outputs=[components["feature_results"]],
    )
