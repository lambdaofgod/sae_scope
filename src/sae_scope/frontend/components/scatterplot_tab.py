"""Scatterplot tab UI and event handlers."""

from typing import Any

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sae_scope.backend.dataset import SAELensDataset


def create_scatterplot(
    df: pd.DataFrame,
    x_label: str,
    y_label: str,
) -> go.Figure:
    """
    Create a scatterplot figure from the provided dataframe.

    Args:
        df: DataFrame with columns "x", "y", and "text".
        x_label: Label for X axis.
        y_label: Label for Y axis.

    Returns:
        Plotly Figure object.
    """
    fig = px.scatter(
        df,
        x="x",
        y="y",
        hover_data=["text"],
    )
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
    )
    return fig


def create_scatterplot_ui() -> dict[str, Any]:
    """
    Create the Scatterplot tab UI components.

    Returns:
        Dictionary of component references.
    """
    with gr.Tab("Scatterplot") as tab:
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

    return {
        "tab": tab,
        "x_feature_idx": x_feature_idx,
        "y_feature_idx": y_feature_idx,
        "update_plot_btn": update_plot_btn,
        "plot": plot,
    }


def wire_scatterplot_events(
    components: dict[str, Any],
    state: dict[str, Any],
) -> None:
    """
    Wire event handlers for Scatterplot tab components.

    Args:
        components: Dictionary of Scatterplot tab component references.
        state: Dictionary containing shared state (current_dataset, selected_features).
    """
    import time

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

    # Wire update plot button
    components["update_plot_btn"].click(
        fn=on_update_plot_click,
        inputs=[
            components["x_feature_idx"],
            components["y_feature_idx"],
            state["current_dataset"],
        ],
        outputs=[state["selected_features"], components["plot"]],
    )
