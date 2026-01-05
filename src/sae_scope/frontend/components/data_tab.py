"""Data tab UI and event handlers."""

from typing import Any

import gradio as gr

from sae_scope.backend.dataset import SAELensDataset


def create_data_ui() -> dict[str, Any]:
    """
    Create the Data tab UI components.

    Returns:
        Dictionary of component references.
    """
    with gr.Tab("Data") as tab:
        dataframe = gr.Dataframe(label="Text Data")

    return {
        "tab": tab,
        "dataframe": dataframe,
    }


def wire_data_events(
    components: dict[str, Any],
    state: dict[str, Any],
) -> None:
    """
    Wire event handlers for Data tab components.

    Args:
        components: Dictionary of Data tab component references.
        state: Dictionary containing shared state (current_dataset, selected_columns).
    """
    import time

    def update_data_table(
        dataset: SAELensDataset | None,
        selected_columns: list[str],
    ) -> object:
        """Update data table with dataset texts and selected columns."""
        start = time.time()
        print("[TIMING] update_data_table START")

        if dataset is None:
            print(
                f"[TIMING] update_data_table END (no dataset): {time.time() - start:.3f}s"
            )
            return None

        t0 = time.time()
        # Get the text field name and build column list
        # Selected columns come BEFORE text column
        text_field = dataset.get_text_field()
        columns_to_show = list(selected_columns) if selected_columns else []
        columns_to_show.append(text_field)

        result = dataset.get_dataframe_with_columns(columns_to_show)
        print(f"[TIMING]   get_dataframe_with_columns: {time.time() - t0:.3f}s")

        print(f"[TIMING] update_data_table END: {time.time() - start:.3f}s")
        return result

    # Wire data tab select event
    components["tab"].select(
        fn=update_data_table,
        inputs=[state["current_dataset"], state["selected_columns"]],
        outputs=[components["dataframe"]],
    )
