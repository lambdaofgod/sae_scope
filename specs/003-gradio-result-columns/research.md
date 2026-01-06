# Research: Data Tab Refactor with Text Search

## R1: Reusable Search Component Pattern

**Decision**: Create a factory function `create_search_ui()` that returns a dict of Gradio components

**Rationale**:
- Follows existing pattern in codebase (`create_*_ui()` functions)
- Returns dict allows flexible wiring by caller
- Avoids class-based approach which would be over-engineering for Gradio

**Alternatives considered**:
- Class-based component: Rejected - Gradio components must be created within `gr.Blocks()` context, classes add complexity
- Higher-order function returning wired component: Rejected - different tabs need different search handlers

## R2: Text Search Implementation

**Decision**: Use Weaviate to index document texts, similar to how feature labels are indexed

**Rationale**:
- WeaviateRetriever already implements BM25, vector, and hybrid search
- Consistent architecture with feature search
- Avoids duplicating search logic

**Implementation approach**:
- Create separate Weaviate collection for document texts (per dataset)
- Reuse `ensure_indexed()` pattern with text content
- Return DataFrame directly (like `search_texts_dataframe()`)

**Alternatives considered**:
- In-memory text search: Rejected - doesn't scale, loses vector search capability
- New retriever class: Rejected - WeaviateRetriever already has all needed functionality

## R3: Gradio Accordion Component

**Decision**: Use `gr.Accordion` with `open=False` for collapsed-by-default DataFrame

**Rationale**:
- Native Gradio component, no custom CSS needed
- Simple API: `with gr.Accordion("Label", open=False): gr.Dataframe(...)`

**Code pattern**:
```python
with gr.Accordion("All Data", open=False):
    dataframe = gr.Dataframe(label="Text Data")
```

## R4: Search Result Columns

**Decision**: Text search results include: index, [selected_columns], text_field, Score

**Rationale**:
- Consistent with existing `search_texts_dataframe()` output
- Respects user's column selection from header
- Score column provides relevance ranking

## R5: Event Wiring Pattern

**Decision**: Keep search handler logic in tab modules, not in reusable component

**Rationale**:
- Different tabs need different search backends (WeaviateRetriever vs InterpEmbedRetriever)
- Handlers need access to tab-specific state
- Component only provides UI, wiring is caller's responsibility

**Pattern**:
```python
# In data_tab.py
search_components = create_search_ui(placeholder="Search texts...")

def on_text_search(query, mode, k, dataset, selected_columns):
    # Tab-specific search logic
    return retriever.search_texts_by_query(...)

search_components["search_btn"].click(
    fn=on_text_search,
    inputs=[search_components["query"], ...],
    outputs=[search_components["results"]],
)
```

## R6: HTMLTableElement for Text Wrapping

**Decision**: Create `HTMLTableElement` class to replace `gr.Dataframe` for search results with proper text wrapping

**Rationale**:
- `gr.Dataframe(wrap=True)` has inconsistent behavior - text still appears too wide
- Custom HTML table with CSS gives full control over text wrapping
- `gr.HTML` component can display raw HTML strings
- Pandas `to_html()` provides base HTML generation

**Design**:
```python
class HTMLTableElement:
    """HTML table generator with proper text wrapping for long fields."""

    def __init__(self, df: pd.DataFrame, max_width: int = 400):
        self._df = df
        self._max_width = max_width

    def html(self) -> str:
        """Return HTML string suitable for gr.HTML component."""
        # Generate table HTML with CSS for text wrapping
        ...
```

**CSS Approach**:
```css
table.sae-table {
    width: 100%;
    border-collapse: collapse;
}
table.sae-table td, table.sae-table th {
    padding: 8px;
    border: 1px solid #ddd;
    text-align: left;
    vertical-align: top;
}
table.sae-table td {
    white-space: normal;
    word-wrap: break-word;
    max-width: 400px;
}
```

**Alternatives considered**:
- `gr.Dataframe(wrap=True, datatype="markdown")`: Tested but text columns still too wide
- External table library (e.g., DataTables.js): Rejected - adds complexity, Gradio CSS isolation issues
- CSS-only fix on gr.Dataframe: Already attempted, insufficient control

**Implementation notes**:
- Use inline `<style>` in HTML string for self-contained styling
- Escape HTML entities in cell values to prevent XSS
- Support optional column width configuration per column
