"""Gradio application entry point for SAE Scope dashboard."""

import time
from pathlib import Path

import gradio as gr

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
        ) -> tuple[
            SAELensDataset | None,
            tuple[int, int] | None,
            int,
            int,
            object,
            object,
            list[list[str | int]],
        ]:
            """
            Handle dataset selection from dropdown.

            Args:
                filename: Selected .pkl filename from dropdown.

            Returns:
                Tuple of (dataset, features, x_idx, y_idx, plot, dataframe, feature_results).
            """
            start = time.time()
            print(f"[TIMING] on_dataset_select START filename={filename}")

            if filename is None:
                print(f"[TIMING] on_dataset_select END (no file): {time.time() - start:.3f}s")
                return None, None, 0, 1, None, None, []

            file_path = Path("data") / filename
            if not file_path.exists():
                raise gr.Error(f"Dataset file not found: {file_path}")

            try:
                t0 = time.time()
                dataset = InterpEmbedDataset.load(str(file_path))
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
            inputs=[dataset_dropdown],
            outputs=[
                current_dataset,
                selected_features,
                x_feature_idx,
                y_feature_idx,
                plot,
                dataframe,
                feature_results,
            ],
        )

        # Wire update plot button
        update_plot_btn.click(
            fn=on_update_plot_click,
            inputs=[x_feature_idx, y_feature_idx, current_dataset],
            outputs=[selected_features, plot],
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
