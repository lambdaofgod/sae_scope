"""Gradio application entry point for SAE Scope dashboard."""

import time
from pathlib import Path

import gradio as gr
import pandas as pd

from sae_scope.backend.dataset import SAELensDataset
from sae_scope.backend.interp_dataset import InterpEmbedDataset
from sae_scope.frontend.components.tabs import create_scatterplot


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
) -> list[list[str | int]]:
    """
    Search features and return results for dataframe display.

    Args:
        query: Search query string.
        dataset: Current dataset or None.

    Returns:
        List of [index, label] pairs for matching features, limited to 100.
    """
    if dataset is None:
        return []

    if not query.strip():
        # Show first 100 features when no search query
        results = [(i, dataset.features.labels[i]) for i in range(min(100, len(dataset.features)))]
    else:
        results = dataset.features.search(query)[:100]

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
                        feature_search_input = gr.Textbox(
                            label="Search Features",
                            placeholder="Type to search feature labels...",
                        )
                        feature_results = gr.Dataframe(
                            headers=["Index", "Label"],
                            label="Feature Search Results (max 100)",
                            interactive=False,
                        )

                with gr.Tab("Data") as data_tab:
                    dataframe = gr.Dataframe(label="Text Data")

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
            print(f"[TIMING] on_dataset_select START filename={filename} aggregation={aggregation_method}")

            if filename is None:
                print(f"[TIMING] on_dataset_select END (no file): {time.time() - start:.3f}s")
                return (
                    None,  # current_dataset
                    None,  # selected_features
                    0,     # x_feature_idx
                    1,     # y_feature_idx
                    None,  # plot
                    None,  # dataframe
                    None,  # summary_stats_df
                    None,  # top_by_frequency
                    None,  # top_by_std
                    None,  # top_by_max
                    [],    # feature_results
                )

            file_path = Path("data") / filename
            if not file_path.exists():
                raise gr.Error(f"Dataset file not found: {file_path}")

            try:
                t0 = time.time()
                dataset = InterpEmbedDataset.load(str(file_path), aggregation_method=aggregation_method)
                print(f"[TIMING]   load dataset: {time.time() - t0:.3f}s")
            except Exception as e:
                raise gr.Error(f"Failed to load dataset: {e}") from e

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
                print(f"[TIMING] on_update_plot_click END (no dataset): {time.time() - start:.3f}s")
                return None, None

            # Convert to int (gr.Number returns float)
            x_idx = int(x_idx)
            y_idx = int(y_idx)

            # Validate indices
            num_features = len(dataset.features)
            if x_idx < 0 or x_idx >= num_features:
                raise gr.Error(f"X index {x_idx} out of range (0 to {num_features - 1})")
            if y_idx < 0 or y_idx >= num_features:
                raise gr.Error(f"Y index {y_idx} out of range (0 to {num_features - 1})")

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
            dataset: SAELensDataset | None,
        ) -> list[list[str | int]]:
            """
            Handle feature search input changes.

            Args:
                query: Search query string.
                dataset: Current dataset or None.

            Returns:
                List of [index, label] pairs for display.
            """
            start = time.time()
            print(f"[TIMING] on_feature_search_change START query={query!r}")

            results = search_features(query, dataset)

            print(f"[TIMING] on_feature_search_change END: {time.time() - start:.3f}s")
            return results

        def update_data_table(dataset: SAELensDataset | None) -> object:
            """Update data table with dataset texts."""
            start = time.time()
            print(f"[TIMING] update_data_table START")

            if dataset is None:
                print(f"[TIMING] update_data_table END (no dataset): {time.time() - start:.3f}s")
                return None

            t0 = time.time()
            result = dataset.get_text_dataframe()
            print(f"[TIMING]   get_text_dataframe: {time.time() - t0:.3f}s")

            print(f"[TIMING] update_data_table END: {time.time() - start:.3f}s")
            return result

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
        feature_search_input.change(
            fn=on_feature_search_change,
            inputs=[feature_search_input, current_dataset],
            outputs=[feature_results],
        )

        # Wire data tab
        data_tab.select(
            fn=update_data_table,
            inputs=[current_dataset],
            outputs=[dataframe],
        )

    return app


def main() -> None:
    """Launch the Gradio application."""
    app = create_app()
    app.launch()


if __name__ == "__main__":
    main()
