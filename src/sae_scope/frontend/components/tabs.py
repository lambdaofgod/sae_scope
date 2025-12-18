"""Tab components for scatterplot and data views."""

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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


def create_tabs() -> tuple[gr.Tab, gr.Tab, gr.Plot, gr.Dataframe]:
    """
    Create the Scatterplot and Data tabs with their components.

    Returns:
        Tuple of (scatterplot_tab, data_tab, plot_component, dataframe_component).
    """
    with gr.Tabs():
        with gr.Tab("Scatterplot") as scatterplot_tab:
            plot = gr.Plot(label="Feature Scatterplot")
        with gr.Tab("Data") as data_tab:
            dataframe = gr.Dataframe(label="Text Data")

    return scatterplot_tab, data_tab, plot, dataframe
