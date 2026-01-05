"""SAE Retrieval tab UI and event handlers."""

from typing import Any

import gradio as gr

from sae_scope.backend.dataset import SAELensDataset
from sae_scope.backend.retriever import SearchMode


def create_sae_retrieval_ui() -> dict[str, Any]:
    """
    Create the SAE Retrieval tab UI components.

    Returns:
        Dictionary of component references.
    """
    with gr.Tab("SAE Retrieval") as tab:
        # State for latent search results: list of (index, label, score)
        latent_search_results_state: gr.State = gr.State(value=[])

        gr.Markdown(
            "# Retrieval method from [Interpretable Embeddings with Sparse Autoencoders: A Data Analysis Toolkit](https://www.interp-embed.com/)"
        )

        gr.Markdown(
            "> For a natural-language query, we (1) retrieve candidate latents by dense embedding similarity between labels and the query, (2) optionally rerank relevant latents with an LLM, and (3) score each document by a weighted sum (with a tunable temperature) of these latents' activations"
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

    return {
        "tab": tab,
        "latent_search_results_state": latent_search_results_state,
        "sae_search_mode": sae_search_mode,
        "sae_candidate_count": sae_candidate_count,
        "sae_query": sae_query,
        "find_latents_btn": find_latents_btn,
        "latent_checkboxes": latent_checkboxes,
        "sae_temperature": sae_temperature,
        "sae_max_results": sae_max_results,
        "find_texts_btn": find_texts_btn,
        "text_results": text_results,
    }


def wire_sae_retrieval_events(
    components: dict[str, Any],
    state: dict[str, Any],
    get_interp_retriever: callable,
) -> None:
    """
    Wire event handlers for SAE Retrieval tab components.

    Args:
        components: Dictionary of SAE Retrieval tab component references.
        state: Dictionary containing shared state (current_dataset).
        get_interp_retriever: Callable that returns the current InterpEmbedRetriever instance.
    """
    import time

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
        interp_retriever = get_interp_retriever()

        if dataset is None or interp_retriever is None:
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
        search_results = interp_retriever.search_latents(
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
        selected_columns: list[str],
    ) -> object:
        """Handle Find Texts button click (Phase 2).

        Args:
            selected_choices: List of selected checkbox labels.
            search_results: Full search results from state.
            temperature: Temperature for softmax weighting.
            max_results: Maximum number of texts to return.
            selected_columns: List of additional column names to display.

        Returns:
            gr.update with data rows and dynamic headers.
        """
        interp_retriever = get_interp_retriever()

        if not selected_choices:
            raise gr.Error(
                "Please select at least one latent before finding texts."
            )

        if interp_retriever is None:
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

        # Build headers: Index, Text, Score, + selected columns
        headers = ["Index", "Text", "Score"]
        if selected_columns:
            headers.extend(selected_columns)

        try:
            results = interp_retriever.search_texts(
                selected_features,
                float(temperature),
                int(max_results),
                selected_columns=selected_columns if selected_columns else None,
            )
            formatted = []
            for r in results:
                row = [r.doc_index, r.text[:200], round(r.score, 6)]
                # Add column values (T020: handle null/empty with placeholder)
                if selected_columns:
                    for col in selected_columns:
                        value = r.column_data.get(col, "")
                        # Handle null, None, NaN, or empty values
                        if value is None or (isinstance(value, float) and value != value):
                            row.append("-")
                        elif value == "":
                            row.append("-")
                        else:
                            row.append(str(value))
                formatted.append(row)
        except NotImplementedError:
            # Backend not yet implemented - show placeholder message
            formatted = [[0, "(search_texts not yet implemented)", 0.0]]

        print(f"[TIMING] on_find_texts END: {time.time() - start:.3f}s")
        return gr.update(value=formatted, headers=headers)

    # Wire SAE Retrieval tab - Find Latents button
    components["find_latents_btn"].click(
        fn=on_find_latents,
        inputs=[
            components["sae_query"],
            components["sae_search_mode"],
            components["sae_candidate_count"],
            state["current_dataset"],
        ],
        outputs=[
            components["latent_search_results_state"],
            components["latent_checkboxes"],
            components["find_texts_btn"],
        ],
    )

    # Wire SAE Retrieval tab - Latent checkbox selection changes
    components["latent_checkboxes"].change(
        fn=on_latent_checkbox_change,
        inputs=[
            components["latent_checkboxes"],
            components["latent_search_results_state"],
        ],
        outputs=[components["find_texts_btn"]],
    )

    # Wire SAE Retrieval tab - Find Texts button
    components["find_texts_btn"].click(
        fn=on_find_texts,
        inputs=[
            components["latent_checkboxes"],
            components["latent_search_results_state"],
            components["sae_temperature"],
            components["sae_max_results"],
            state["selected_columns"],
        ],
        outputs=[components["text_results"]],
    )
