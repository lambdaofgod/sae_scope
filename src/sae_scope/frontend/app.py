"""Gradio application entry point for SAE Scope dashboard."""

import sys
import time
from pathlib import Path

import gradio as gr

from sae_scope.backend.interp_dataset import InterpEmbedDataset
from sae_scope.backend.retriever import (
    InterpEmbedRetriever,
    WeaviateRetriever,
)
from sae_scope.frontend.components import (
    HTMLTableElement,
    create_data_ui,
    create_features_ui,
    create_sae_retrieval_ui,
    create_scatterplot,
    create_scatterplot_ui,
    get_summary_stats,
    get_top_n_features,
    search_features,
    wire_data_events,
    wire_features_events,
    wire_sae_retrieval_events,
    wire_scatterplot_events,
)


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


def create_app(retriever: WeaviateRetriever) -> gr.Blocks:
    """
    Create and configure the Gradio application.

    Args:
        retriever: Pre-initialized WeaviateRetriever instance.

    Returns:
        Configured gr.Blocks application.
    """
    interp_retriever: InterpEmbedRetriever | None = None
    texts_collection: str | None = None

    def _get_retriever() -> WeaviateRetriever:
        return retriever

    def _get_interp_retriever() -> InterpEmbedRetriever | None:
        return interp_retriever

    def _get_texts_collection() -> str | None:
        return texts_collection

    with gr.Blocks(title="SAE Scope Dashboard") as app:
        # Shared State
        current_dataset: gr.State = gr.State(value=None)
        selected_features: gr.State = gr.State(value=None)
        selected_columns: gr.State = gr.State(value=[])

        state = {
            "current_dataset": current_dataset,
            "selected_features": selected_features,
            "selected_columns": selected_columns,
        }

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

            # Load Dataset button
            load_dataset_btn = gr.Button("Load Dataset")

            # Column selector with Apply button (hidden until dataset is loaded)
            with gr.Row(visible=False) as column_row:
                column_selector = gr.CheckboxGroup(
                    label="Additional Columns to Display",
                    choices=[],
                    value=[],
                    interactive=True,
                )
                apply_columns_btn = gr.Button("Apply")

            # Create tabs with modular components
            with gr.Tabs():
                scatterplot_components = create_scatterplot_ui()
                features_components = create_features_ui()
                data_components = create_data_ui()
                sae_retrieval_components = create_sae_retrieval_ui()

        # Wire tab events
        wire_scatterplot_events(scatterplot_components, state)
        wire_features_events(features_components, state, _get_retriever)
        wire_data_events(data_components, state, _get_interp_retriever, _get_texts_collection)
        wire_sae_retrieval_events(sae_retrieval_components, state, _get_interp_retriever)

        # Dataset selection handler
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
            nonlocal interp_retriever, texts_collection

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
                    [],  # selected_columns
                    gr.update(visible=False),  # column_row
                    gr.update(choices=[], value=[]),  # column_selector
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
            try:
                t0 = time.time()
                retriever.ensure_indexed(filename, dataset.features.labels)
                # Initialize InterpEmbedRetriever for SAE Retrieval tab
                interp_retriever = InterpEmbedRetriever(retriever, dataset)
                # Index document texts for text search in Data tab
                texts_collection = interp_retriever.ensure_texts_indexed(filename)
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
            data_df = HTMLTableElement(dataset.get_text_dataframe()).html()
            print(f"[TIMING]   get_text_dataframe: {time.time() - t0:.3f}s")

            # Get feature statistics
            summary_stats = get_summary_stats(dataset)
            top_freq = get_top_n_features(dataset, 10, "frequency")
            top_std = get_top_n_features(dataset, 10, "std")
            top_max = get_top_n_features(dataset, 10, "max")

            # Get initial feature results (first 10)
            feature_list = search_features("", dataset, retriever)

            # Get available columns for column selector (excluding text field)
            all_columns = dataset.get_column_names()
            text_field = dataset.get_text_field()
            available_columns = [col for col in all_columns if col != text_field]

            # Handle edge case: dataset with only text column
            if not available_columns:
                column_row_update = gr.update(visible=False)
                column_selector_update = gr.update(choices=[], value=[])
            else:
                column_row_update = gr.update(visible=True)
                column_selector_update = gr.update(choices=available_columns, value=[])

            print(f"[TIMING] on_dataset_select END: {time.time() - start:.3f}s")
            return (
                dataset,
                (x_idx, y_idx),
                [],  # selected_columns (empty by default)
                column_row_update,
                column_selector_update,
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

        # Wire Load Dataset button
        load_dataset_btn.click(
            fn=on_dataset_select,
            inputs=[dataset_dropdown, aggregation_dropdown],
            outputs=[
                current_dataset,
                selected_features,
                selected_columns,
                column_row,
                column_selector,
                scatterplot_components["x_feature_idx"],
                scatterplot_components["y_feature_idx"],
                scatterplot_components["plot"],
                data_components["dataframe"],
                features_components["summary_stats_df"],
                features_components["top_by_frequency"],
                features_components["top_by_std"],
                features_components["top_by_max"],
                features_components["feature_results"],
            ],
        )

        # Wire Apply Columns button to update selected_columns state and refresh Data tab
        def on_apply_columns(
            selected: list[str],
            dataset: InterpEmbedDataset | None,
        ) -> tuple[list[str], str]:
            """Update selected_columns state and refresh Data tab when user clicks Apply."""
            print(f"[INFO] Applied columns: {selected}")

            # Refresh Data tab with new columns
            if dataset is None:
                return selected, HTMLTableElement(None).html()

            text_field = dataset.get_text_field()
            # Selected columns come BEFORE text column
            columns_to_show = list(selected) if selected else []
            columns_to_show.append(text_field)

            data_df = dataset.get_dataframe_with_columns(columns_to_show)
            return selected, HTMLTableElement(data_df).html()

        apply_columns_btn.click(
            fn=on_apply_columns,
            inputs=[column_selector, current_dataset],
            outputs=[selected_columns, data_components["dataframe"]],
        )

    return app


def main() -> None:
    """Launch the Gradio application."""
    try:
        retriever = WeaviateRetriever()
    except Exception as e:
        print(f"Startup check failed: {e}", file=sys.stderr)
        sys.exit(1)

    app = create_app(retriever)
    app.launch()


if __name__ == "__main__":
    main()
