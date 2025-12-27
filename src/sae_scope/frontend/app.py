"""Gradio application entry point for SAE Scope dashboard."""

import time
from pathlib import Path

import gradio as gr
import pandas as pd

from sae_scope.backend.dataset import SAELensDataset
from sae_scope.backend.interp_dataset import InterpEmbedDataset
from sae_scope.backend.retriever import (
    InterpEmbedRetriever,
    SearchMode,
    WeaviateRetriever,
)
from sae_scope.frontend.components.tabs import create_scatterplot

# Global retriever instances (initialized on first dataset load)
_retriever: WeaviateRetriever | None = None
_interp_retriever: InterpEmbedRetriever | None = None


def list_data_files() -> list[str]:
    """
    List .pkl files in the /data directory.

    Returns:
        List of .pkl filenames available in the data directory.
    """
    data_dir = Path("data")
    if not data_dir.exists():
        return []
    return sorted([f.name for f in data_dir.glob("*.pkl")])


def search_features(
    query: str,
    dataset: SAELensDataset | None,
    search_mode: str = "Lexical",
    k: int = 10,
) -> list[list[str | int]]:
    """
    Search features and return results for dataframe display.

    Args:
        query: Search query string.
        dataset: Current dataset or None.
        search_mode: Search mode ("Lexical", "Vector", or "Hybrid").
        k: Maximum number of results to return.

    Returns:
        List of [index, label] pairs for matching features.
    """
    global _retriever

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
    if _retriever is not None:
        mode = SearchMode[search_mode.upper()]
        search_results = _retriever.search(query, mode, k=k)
        return [[r.index, r.label] for r in search_results]

    # Fallback to basic search if retriever not available
    results = dataset.features.search(query)[:k]
    return [[idx, label] for idx, label in results]


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


def create_app() -> gr.Blocks:
    """
    Create and configure the Gradio application.

    Returns:
        Configured gr.Blocks application.
    """
    with gr.Blocks(title="SAE Scope Dashboard") as app:
        # State
        current_dataset: gr.State = gr.State(value=None)
        selected_features: gr.State = gr.State(value=None)

        # Main content area
        with gr.Column():
            # Header
            gr.Markdown("# SAE Scope Dashboard")

            # Dataset selection dropdown
            dataset_dropdown = gr.Dropdown(
                label="Select Dataset",
                choices=list_data_files(),
                value=None,
                interactive=True,
            )

            # Aggregation method dropdown
            aggregation_dropdown = gr.Dropdown(
                label="Aggregation Method",
                choices=["max", "mean", "binarize", "count"],
                value="max",
                interactive=True,
            )

            # Tabs with plot, features search, and dataframe
            with gr.Tabs():
                with gr.Tab("Scatterplot") as scatterplot_tab:
                    gr.Markdown(
                        "Plot the activation values of two selected latents. Check 'Features' tab to explore them and search by feature labels."
                    )
                    with gr.Row():
                        x_feature_idx = gr.Number(
                            label="X Feature Index",
                            value=0,
                            precision=0,
                            minimum=0,
                        )
                        y_feature_idx = gr.Number(
                            label="Y Feature Index",
                            value=1,
                            precision=0,
                            minimum=0,
                        )
                        update_plot_btn = gr.Button("Update Plot")
                    plot = gr.Plot(label="Feature Scatterplot")

                with gr.Tab("Features") as features_tab:
                    with gr.Accordion("Feature Statistics", open=True):
                        summary_stats_df = gr.Dataframe(
                            label="Summary Statistics",
                            interactive=False,
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
                        )
                        top_by_std = gr.Dataframe(
                            headers=["Index", "Label", "Std Dev"],
                            label="Top N by Std Dev",
                            interactive=False,
                        )
                        top_by_max = gr.Dataframe(
                            headers=["Index", "Label", "Max Value"],
                            label="Top N by Max Value",
                            interactive=False,
                        )

                    with gr.Accordion("Search Features", open=False):
                        search_mode_dropdown = gr.Dropdown(
                            label="Search Mode",
                            choices=["Lexical", "Vector", "Hybrid"],
                            value="Lexical",
                            interactive=True,
                        )
                        feature_search_input = gr.Textbox(
                            label="Search Features",
                            placeholder="Type to search feature labels...",
                        )
                        search_results_limit = gr.Number(
                            label="Max Results",
                            value=10,
                            minimum=1,
                            maximum=100,
                            step=1,
                            interactive=True,
                        )
                        feature_search_button = gr.Button("Search")
                        feature_results = gr.Dataframe(
                            headers=["Index", "Label"],
                            label="Feature Search Results",
                            interactive=False,
                        )

                with gr.Tab("Data") as data_tab:
                    dataframe = gr.Dataframe(label="Text Data")

                with gr.Tab("SAE Retrieval") as sae_retrieval_tab:
                    # State for latent search results: list of (index, label, score)
                    latent_search_results_state: gr.State = gr.State(value=[])
                    gr.Markdown(
                        "# Retrieval method from [Interpretable Embeddings with Sparse Autoencoders: A Data Analysis Toolkit](https://www.interp-embed.com/)"
                    )

                    gr.Markdown(
                        "> For a natural-language query, we (1) retrieve candidate latents by dense embedding similarity between labels and the query, (2) optionally rerank relevant latents with an LLM, and (3) score each document by a weighted sum (with a tunable temperature) of these latents’ activations"
                    )
                    gr.Markdown("### Phase 1: Find Latents")
                    with gr.Row():
                        sae_search_mode = gr.Dropdown(
                            label="Search Mode",
                            choices=["Lexical", "Vector", "Hybrid"],
                            value="Hybrid",
                            interactive=True,
                        )
                        sae_candidate_count = gr.Number(
                            label="Candidate Count",
                            value=10,
                            minimum=1,
                            maximum=100,
                            precision=0,
                            interactive=True,
                        )
                    sae_query = gr.Textbox(
                        label="Query",
                        placeholder="Enter search query...",
                    )
                    find_latents_btn = gr.Button("Find Latents")
                    latent_checkboxes = gr.CheckboxGroup(
                        label="Select latents for text search (all selected by default)",
                        choices=[],
                        value=[],
                        interactive=True,
                    )

                    gr.Markdown("### Phase 2: Find Texts")
                    with gr.Row():
                        sae_temperature = gr.Number(
                            label="Temperature",
                            value=1.0,
                            minimum=0.1,
                            maximum=10.0,
                            step=0.1,
                            interactive=True,
                        )
                        sae_max_results = gr.Number(
                            label="Max Results",
                            value=10,
                            minimum=1,
                            maximum=100,
                            precision=0,
                            interactive=True,
                        )
                    find_texts_btn = gr.Button("Find Texts", interactive=False)
                    text_results = gr.Dataframe(
                        headers=["Index", "Text", "Score"],
                        label="Matching Texts",
                        interactive=False,
                    )

        def on_dataset_select(
            filename: str | None,
            aggregation_method: str = "max",
        ) -> tuple:
            """
            Handle dataset selection from dropdown.

            Args:
                filename: Selected .pkl filename from dropdown.
                aggregation_method: Method for aggregating latents.

            Returns:
                Tuple of outputs for all connected components.
            """
            start = time.time()
            print(
                f"[TIMING] on_dataset_select START filename={filename} aggregation={aggregation_method}"
            )

            if filename is None:
                print(
                    f"[TIMING] on_dataset_select END (no file): {time.time() - start:.3f}s"
                )
                return (
                    None,  # current_dataset
                    None,  # selected_features
                    0,  # x_feature_idx
                    1,  # y_feature_idx
                    None,  # plot
                    None,  # dataframe
                    None,  # summary_stats_df
                    None,  # top_by_frequency
                    None,  # top_by_std
                    None,  # top_by_max
                    [],  # feature_results
                )

            file_path = Path("data") / filename
            if not file_path.exists():
                raise gr.Error(f"Dataset file not found: {file_path}")

            try:
                t0 = time.time()
                dataset = InterpEmbedDataset.load(
                    str(file_path), aggregation_method=aggregation_method
                )
                print(f"[TIMING]   load dataset: {time.time() - t0:.3f}s")
            except Exception as e:
                raise gr.Error(f"Failed to load dataset: {e}") from e

            # Initialize retrievers and index feature labels
            global _retriever, _interp_retriever
            try:
                t0 = time.time()
                if _retriever is None:
                    _retriever = WeaviateRetriever()
                _retriever.ensure_indexed(filename, dataset.features.labels)
                # Initialize InterpEmbedRetriever for SAE Retrieval tab
                _interp_retriever = InterpEmbedRetriever(_retriever, dataset)
                print(f"[TIMING]   ensure_indexed: {time.time() - t0:.3f}s")
            except ConnectionError as e:
                raise gr.Error(str(e)) from e

            # Get default features (first two)
            x_idx, y_idx = dataset.get_default_feature_indices()

            # Create initial scatterplot
            t0 = time.time()
            df = dataset.get_scatter_dataframe(x_idx, y_idx)
            print(f"[TIMING]   get_scatter_dataframe: {time.time() - t0:.3f}s")

            x_label = dataset.features.get_formatted_label(x_idx)
            y_label = dataset.features.get_formatted_label(y_idx)
            fig = create_scatterplot(df, x_label, y_label)

            # Get data table
            t0 = time.time()
            data_df = dataset.get_text_dataframe()
            print(f"[TIMING]   get_text_dataframe: {time.time() - t0:.3f}s")

            # Get feature statistics
            summary_stats = get_summary_stats(dataset)
            top_freq = get_top_n_features(dataset, 10, "frequency")
            top_std = get_top_n_features(dataset, 10, "std")
            top_max = get_top_n_features(dataset, 10, "max")

            # Get initial feature results (first 100)
            feature_list = search_features("", dataset)

            print(f"[TIMING] on_dataset_select END: {time.time() - start:.3f}s")
            return (
                dataset,
                (x_idx, y_idx),
                x_idx,
                y_idx,
                fig,
                data_df,
                summary_stats,
                top_freq,
                top_std,
                top_max,
                feature_list,
            )

        def on_update_plot_click(
            x_idx: int,
            y_idx: int,
            dataset: SAELensDataset | None,
        ) -> tuple[tuple[int, int] | None, object]:
            """
            Handle Update Plot button click.

            Args:
                x_idx: X axis feature index.
                y_idx: Y axis feature index.
                dataset: Current dataset or None.

            Returns:
                Tuple of (feature_tuple, plot).
            """
            start = time.time()
            print(f"[TIMING] on_update_plot_click START x={x_idx}, y={y_idx}")

            if dataset is None:
                print(
                    f"[TIMING] on_update_plot_click END (no dataset): {time.time() - start:.3f}s"
                )
                return None, None

            # Convert to int (gr.Number returns float)
            x_idx = int(x_idx)
            y_idx = int(y_idx)

            # Validate indices
            num_features = len(dataset.features)
            if x_idx < 0 or x_idx >= num_features:
                raise gr.Error(
                    f"X index {x_idx} out of range (0 to {num_features - 1})"
                )
            if y_idx < 0 or y_idx >= num_features:
                raise gr.Error(
                    f"Y index {y_idx} out of range (0 to {num_features - 1})"
                )

            feature_tuple = (x_idx, y_idx)

            # Create scatterplot
            t0 = time.time()
            df = dataset.get_scatter_dataframe(x_idx, y_idx)
            print(f"[TIMING]   get_scatter_dataframe: {time.time() - t0:.3f}s")

            x_label = dataset.features.get_formatted_label(x_idx)
            y_label = dataset.features.get_formatted_label(y_idx)
            fig = create_scatterplot(df, x_label, y_label)

            print(f"[TIMING] on_update_plot_click END: {time.time() - start:.3f}s")
            return feature_tuple, fig

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

            results = search_features(query, dataset, search_mode, int(k))

            print(f"[TIMING] on_feature_search_change END: {time.time() - start:.3f}s")
            return results

        def update_data_table(dataset: SAELensDataset | None) -> object:
            """Update data table with dataset texts."""
            start = time.time()
            print(f"[TIMING] update_data_table START")

            if dataset is None:
                print(
                    f"[TIMING] update_data_table END (no dataset): {time.time() - start:.3f}s"
                )
                return None

            t0 = time.time()
            result = dataset.get_text_dataframe()
            print(f"[TIMING]   get_text_dataframe: {time.time() - t0:.3f}s")

            print(f"[TIMING] update_data_table END: {time.time() - start:.3f}s")
            return result

        def on_find_latents(
            query: str,
            search_mode: str,
            candidate_count: int,
            dataset: SAELensDataset | None,
        ) -> tuple[list[tuple[int, str, float]], object, object]:
            """Handle Find Latents button click (Phase 1).

            Args:
                query: Search query string.
                search_mode: Search mode (Lexical, Vector, Hybrid).
                candidate_count: Number of latents to retrieve.
                dataset: Current dataset or None.

            Returns:
                Tuple of (search_results_state, latent_checkboxes, find_texts_btn).
            """
            global _interp_retriever

            if dataset is None or _interp_retriever is None:
                return [], gr.update(choices=[], value=[]), gr.update(interactive=False)

            start = time.time()
            print(f"[TIMING] on_find_latents START query={query!r} mode={search_mode}")

            if not query.strip():
                # Show first k features when no query
                k = int(candidate_count)
                state_results = [
                    (i, dataset.features.labels[i], 1.0)
                    for i in range(min(k, len(dataset.features)))
                ]
                # Create checkbox choices with score: "[idx] label (score)"
                choices = [
                    f"[{i}] {dataset.features.labels[i]} (1.0000)"
                    for i in range(min(k, len(dataset.features)))
                ]
                print(
                    f"[TIMING] on_find_latents END (empty query): {time.time() - start:.3f}s"
                )
                return (
                    state_results,
                    gr.update(
                        choices=choices, value=choices
                    ),  # All selected by default
                    gr.update(interactive=True),
                )

            mode = SearchMode[search_mode.upper()]
            search_results = _interp_retriever.search_latents(
                query, mode, int(candidate_count)
            )

            # Store full results in state
            state_results = [(r.index, r.label, r.score) for r in search_results]
            # Create checkbox choices with score: "[idx] label (score)"
            choices = [f"[{r.index}] {r.label} ({r.score:.4f})" for r in search_results]

            print(f"[TIMING] on_find_latents END: {time.time() - start:.3f}s")
            return (
                state_results,
                gr.update(choices=choices, value=choices),  # All selected by default
                gr.update(interactive=len(choices) > 0),
            )

        def on_latent_checkbox_change(
            selected_choices: list[str],
            search_results: list[tuple[int, str, float]],
        ) -> object:
            """Handle latent checkbox selection changes.

            Args:
                selected_choices: List of selected checkbox labels.
                search_results: Full search results from state.

            Returns:
                Updated find_texts_btn interactivity.
            """
            return gr.update(interactive=len(selected_choices) > 0)

        def on_find_texts(
            selected_choices: list[str],
            search_results: list[tuple[int, str, float]],
            temperature: float,
            max_results: int,
        ) -> list[list]:
            """Handle Find Texts button click (Phase 2).

            Args:
                selected_choices: List of selected checkbox labels.
                search_results: Full search results from state.
                temperature: Temperature for softmax weighting.
                max_results: Maximum number of texts to return.

            Returns:
                List of [index, text, score] rows for display.
            """
            global _interp_retriever

            if not selected_choices:
                raise gr.Error(
                    "Please select at least one latent before finding texts."
                )

            if _interp_retriever is None:
                raise gr.Error("Please load a dataset first.")

            # Build selected features list from checkbox selections
            # Parse "[idx] label (score)" format to get indices
            selected_indices = set()
            for choice in selected_choices:
                # Extract index from "[idx]" at the start
                idx_str = choice.split("]")[0].replace("[", "").strip()
                selected_indices.add(int(idx_str))

            # Get scores from search results
            selected_features = [
                (idx, score)
                for idx, label, score in search_results
                if idx in selected_indices
            ]

            start = time.time()
            print(
                f"[TIMING] on_find_texts START n_latents={len(selected_features)} temp={temperature}"
            )

            try:
                results = _interp_retriever.search_texts(
                    selected_features,
                    float(temperature),
                    int(max_results),
                )
                formatted = [
                    [r.doc_index, r.text[:200], round(r.score, 6)] for r in results
                ]
            except NotImplementedError:
                # Backend not yet implemented - show placeholder message
                formatted = [[0, "(search_texts not yet implemented)", 0.0]]

            print(f"[TIMING] on_find_texts END: {time.time() - start:.3f}s")
            return formatted

        # Wire dataset dropdown
        dataset_dropdown.change(
            fn=on_dataset_select,
            inputs=[dataset_dropdown, aggregation_dropdown],
            outputs=[
                current_dataset,
                selected_features,
                x_feature_idx,
                y_feature_idx,
                plot,
                dataframe,
                summary_stats_df,
                top_by_frequency,
                top_by_std,
                top_by_max,
                feature_results,
            ],
        )

        # Wire aggregation dropdown (reloads dataset with new aggregation method)
        aggregation_dropdown.change(
            fn=on_dataset_select,
            inputs=[dataset_dropdown, aggregation_dropdown],
            outputs=[
                current_dataset,
                selected_features,
                x_feature_idx,
                y_feature_idx,
                plot,
                dataframe,
                summary_stats_df,
                top_by_frequency,
                top_by_std,
                top_by_max,
                feature_results,
            ],
        )

        # Wire update plot button
        update_plot_btn.click(
            fn=on_update_plot_click,
            inputs=[x_feature_idx, y_feature_idx, current_dataset],
            outputs=[selected_features, plot],
        )

        # Wire top N input
        top_n_input.change(
            fn=on_top_n_change,
            inputs=[top_n_input, current_dataset],
            outputs=[top_by_frequency, top_by_std, top_by_max],
        )

        # Wire feature search
        feature_search_button.click(
            fn=on_feature_search_change,
            inputs=[
                feature_search_input,
                search_mode_dropdown,
                search_results_limit,
                current_dataset,
            ],
            outputs=[feature_results],
        )

        # Wire data tab
        data_tab.select(
            fn=update_data_table,
            inputs=[current_dataset],
            outputs=[dataframe],
        )

        # Wire SAE Retrieval tab - Find Latents button
        find_latents_btn.click(
            fn=on_find_latents,
            inputs=[sae_query, sae_search_mode, sae_candidate_count, current_dataset],
            outputs=[latent_search_results_state, latent_checkboxes, find_texts_btn],
        )

        # Wire SAE Retrieval tab - Latent checkbox selection changes
        latent_checkboxes.change(
            fn=on_latent_checkbox_change,
            inputs=[latent_checkboxes, latent_search_results_state],
            outputs=[find_texts_btn],
        )

        # Wire SAE Retrieval tab - Find Texts button
        find_texts_btn.click(
            fn=on_find_texts,
            inputs=[
                latent_checkboxes,
                latent_search_results_state,
                sae_temperature,
                sae_max_results,
            ],
            outputs=[text_results],
        )

    return app


def main() -> None:
    """Launch the Gradio application."""
    app = create_app()
    app.launch()


if __name__ == "__main__":
    main()
