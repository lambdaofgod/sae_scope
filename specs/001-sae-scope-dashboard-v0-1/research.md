# Research: SAE Scope Dashboard v0.1 - Performance UI Refactor

**Date**: 2025-12-18
**Feature**: 001-sae-scope-dashboard-v0-1

## Research Summary

This document covers the UI refactor to address performance issues with thousands of features.

## Research Questions

### 1. Feature Indices Input Component (NEW)

**Decision**: Use single `gr.Textbox` for comma-separated feature indices (e.g., "0, 1").

**Rationale**:
- Single input field simplifies UI and event handling
- One change handler instead of two
- Familiar pattern for users (comma-separated values)
- Easy to parse with Python's split() and int()

**Alternatives Considered**:
- Two `gr.Number` fields: Rejected - requires separate event handlers for each, more complex wiring
- `gr.Slider` pair: Rejected - not suitable for thousands of possible values

**Key Implementation Details**:
```python
feature_indices_input = gr.Textbox(
    label="Feature Indices (X, Y)",
    value="0, 1",
    placeholder="e.g., 0, 1",
)

def parse_feature_indices(text: str) -> tuple[int, int]:
    """Parse comma-separated indices like '0, 1' into (x_idx, y_idx)."""
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 2:
        raise ValueError("Expected exactly 2 comma-separated indices")
    return int(parts[0]), int(parts[1])
```

### 2. Features Tab Search Results Display (NEW)

**Decision**: Use `gr.Dataframe` with limited rows for search results.

**Rationale**:
- Already used in Data tab, consistent UX
- Supports structured data (index + label)
- Can limit displayed rows easily
- Renders only visible content

**Alternatives Considered**:
- `gr.Radio`: Rejected - would still render all options upfront
- `gr.Dropdown` with search: Rejected - preloads all choices into DOM
- `gr.CheckboxGroup`: Rejected - current problem, renders all checkboxes

**Key Implementation Details**:
```python
search_results = gr.Dataframe(
    headers=["Index", "Label"],
    max_rows=100,  # Limit displayed results
    interactive=False,
)
```

### 3. Search Result Limit (NEW)

**Decision**: Limit to 100 search results maximum.

**Rationale**:
- Prevents rendering slowdown
- Users typically refine search rather than scroll through hundreds
- Provides instant feedback on matching features
- Message shown when results are truncated

### 4. Sidebar Removal Strategy (UPDATED)

**Decision**: Delete `sidebar.py` entirely, do not migrate any code.

**Rationale**:
- `enforce_two_selections` logic not needed with direct index inputs
- `filter_features` will be reimplemented simply in features_tab.py
- Clean break is simpler than partial migration
- Reduces codebase complexity

**Previous Decision (Superseded)**:
- Was using `gr.Sidebar` with CheckboxGroup for feature selection
- Caused performance issues with thousands of features

### 5. Gradio Tabs Structure (UPDATED)

**Decision**: Use `gr.Tabs` with THREE tabs: "Scatterplot", "Features", and "Data".

**Rationale**: Separating feature discovery (Features tab) from feature selection (index inputs in Scatterplot tab) provides:
- Fast feature selection via direct indices
- Searchable feature discovery when needed
- No upfront rendering of all features

**Key Implementation Details**:
```python
with gr.Tabs():
    with gr.Tab("Scatterplot"):
        # Feature index inputs
        x_feature_idx = gr.Number(...)
        y_feature_idx = gr.Number(...)
        plot = gr.Plot()
    with gr.Tab("Features"):
        search_input = gr.Textbox(...)
        search_results = gr.Dataframe(...)
    with gr.Tab("Data"):
        dataframe = gr.Dataframe()
```

### 6. Plotly Express for Scatterplot (UNCHANGED)

**Decision**: Use Plotly Express (`px.scatter`) for the scatterplot visualization.

**Rationale**: Plotly Express integrates natively with Gradio's `gr.Plot` component, supports interactive features (click events, hover), and works seamlessly with Pandas DataFrames.

### 7. Dataset File Format (UNCHANGED)

**Decision**: Use `interp_embed.Dataset` as the data source, loading `.pkl` files from `/data` directory.

**Rationale**: The `interp_embed` library is already a project dependency and provides exactly what we need:
- Pre-computed SAE feature activations via `latents()`
- Feature labels via `feature_labels()`
- Text content via `pandas()` or `documents()`

### 8. Dataset Selection UI (UNCHANGED)

**Decision**: Use `gr.Dropdown` populated with `.pkl` files from `/data` folder.

**Rationale**: Simple UX, only pre-processed datasets available, consistent with interp_embed workflow.

## Dependencies

No new dependencies required. Using existing:
- gradio (>=5.0.0)
- plotly (>=5.0.0)
- pandas (>=2.0.0)
- interp_embed (existing)

### 9. Feature Statistics Display (NEW)

**Decision**: Add feature statistics to Features tab using Gradio Accordions with user-configurable top N.

**Rationale**:
- Accordions allow collapsible sections to organize content
- Statistics accordion open by default (primary discovery tool)
- Search accordion closed by default (secondary tool)
- User-configurable N (default 10) gives flexibility without overwhelming
- Statistics computed once and cached; slicing is cheap

**Statistics to compute**:
- Frequency: Normalized (0-1) count of nonzero activations per feature (count_nonzero / num_documents)
- Standard deviation: Spread of activation values
- Maximum value: Peak activation value

**UI Structure**:
- Number input for "Top N Features" (default: 10, min: 1, max: 100)
- Three dataframes showing top N by each metric
- Search functionality in separate accordion

### 10. Feature Index Inputs (UPDATED - Phase 12)

**Decision**: Use two `gr.Number` inputs with "Update Plot" button.

**Rationale**:
- Explicit number fields clearer than comma-separated text
- Button gives user control over when to update (no accidental updates while typing)
- Simpler validation (gr.Number enforces numeric input)

**Supersedes**: Previous decision to use single textbox with comma-separated values.

## Open Questions (None)

All technical questions resolved. Ready to proceed with implementation.
