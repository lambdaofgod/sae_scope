# Implementation Plan: Data Tab Refactor with Text Search

**Branch**: `003-gradio-result-columns` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)

## Summary

Refactor the Data tab to:
1. Put the existing DataFrame in an accordion (collapsed by default)
2. Add a text search component (similar to "Search features" in Features tab)
3. Extract a reusable search component that works for both feature search and text search

## Technical Context

**Language/Version**: Python 3.10
**Primary Dependencies**: Gradio 5.x, Pandas, Weaviate
**Storage**: Local .pkl files in /data directory
**Testing**: pytest
**Target Platform**: Local desktop (web browser)
**Project Type**: Single project with frontend/backend split

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Single Responsibility | PASS | Extracting reusable search component improves SRP |
| Open/Closed | PASS | New search component extends functionality without modifying existing |
| DRY | VIOLATION -> FIXED | Currently search UI is duplicated between Features and SAE Retrieval tabs - will be extracted |
| Fail-First | PASS | Search errors surface via gr.Error |

## Wireframe

### Data Tab - New Layout

```text
+------------------------------------------------------------------+
|  [ Data ]                                                         |
+------------------------------------------------------------------+
|                                                                   |
|  ### Search Texts                                                 |
|                                                                   |
|  Search Mode              Max Results                             |
|  +------------------+     +------------------+                    |
|  | Hybrid        v  |     | 10               |                    |
|  +------------------+     +------------------+                    |
|                                                                   |
|  Query                                                            |
|  +------------------------------------------------------------+  |
|  | Type to search texts...                                    |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  [ Search ]                                                       |
|                                                                   |
|  +------------------------------------------------------------+  |
|  | index | [selected cols] | text           | Score           |  |
|  |-------|-----------------|----------------|-----------------|  |
|  |   42  | review.md       | "The game..."  | 0.8234          |  |
|  |  128  | notes.md        | "Combat sys.." | 0.7891          |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  v All Data (click to expand)                                     |
|  +------------------------------------------------------------+  |
|  | (Accordion - collapsed by default)                         |  |
|  | Full DataFrame with all rows                               |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### Reusable Search Component Pattern

```text
+------------------------------------------------------------------+
|  SearchComponent(                                                 |
|    placeholder="Type to search...",                               |
|    result_columns=["Index", "Label"] or ["Index", "Text", "Score"]|
|    on_search=callable,                                            |
|  )                                                                |
+------------------------------------------------------------------+
|  Search Mode              Max Results                             |
|  +------------------+     +------------------+                    |
|  | Hybrid        v  |     | 10               |                    |
|  +------------------+     +------------------+                    |
|                                                                   |
|  Query                                                            |
|  +------------------------------------------------------------+  |
|  | {placeholder}                                              |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  [ Search ]                                                       |
|                                                                   |
|  +------------------------------------------------------------+  |
|  | {result_columns dynamically}                               |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

## Design Overview

### 1. Reusable Search Component

Create `src/sae_scope/frontend/components/search_component.py`:

```python
def create_search_ui(
    placeholder: str = "Type to search...",
    default_mode: str = "Hybrid",
    default_k: int = 10,
) -> dict[str, Any]:
    """Create reusable search UI components."""
    with gr.Row():
        search_mode = gr.Dropdown(
            label="Search Mode",
            choices=["Lexical", "Vector", "Hybrid"],
            value=default_mode,
        )
        max_results = gr.Number(
            label="Max Results",
            value=default_k,
            minimum=1,
            maximum=100,
        )
    query = gr.Textbox(label="Query", placeholder=placeholder)
    search_btn = gr.Button("Search")
    results = gr.Dataframe(label="Results", interactive=False)

    return {
        "search_mode": search_mode,
        "max_results": max_results,
        "query": query,
        "search_btn": search_btn,
        "results": results,
    }
```

### 2. Text Search Backend

Add to `InterpEmbedRetriever`:

```python
def search_texts_by_query(
    self,
    query: str,
    mode: SearchMode,
    k: int = 10,
    selected_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Direct text search using Weaviate on document texts."""
    # Index document texts in Weaviate (similar to feature labels)
    # Search and return matching documents as DataFrame
```

### 3. Data Tab Refactor

Update `data_tab.py`:
- Add search component at top
- Wrap existing DataFrame in `gr.Accordion`
- Wire search to new `search_texts_by_query()` method

### 4. Features Tab Refactor

Update `features_tab.py`:
- Replace inline search UI with `create_search_ui()`
- Keep existing search handler logic

## Project Structure

```text
src/sae_scope/
  frontend/
    components/
      search_component.py    # NEW: Reusable search UI
      data_tab.py            # MODIFY: Add search, accordion
      features_tab.py        # MODIFY: Use reusable search
      sae_retrieval_tab.py   # NO CHANGE (two-phase is different)
  backend/
    retriever/
      interp_embed.py        # MODIFY: Add search_texts_by_query()
```

## Files to Modify

| File | Changes |
|------|---------|
| `src/sae_scope/frontend/components/search_component.py` | NEW: Reusable search UI factory |
| `src/sae_scope/frontend/components/data_tab.py` | Add search UI + accordion for DataFrame |
| `src/sae_scope/frontend/components/features_tab.py` | Use reusable search component |
| `src/sae_scope/frontend/components/__init__.py` | Export new search component |
| `src/sae_scope/backend/retriever/interp_embed.py` | Add text search by query method |

## Phase Implementation Order

1. **Phase 1**: Create reusable search component
2. **Phase 2**: Add text search backend method
3. **Phase 3**: Refactor Data tab (search + accordion)
4. **Phase 4**: Refactor Features tab to use reusable component
5. **Phase 5**: Testing and validation
6. **Phase 6**: Create HTMLTableElement for search results

---

## Phase 6: HTMLTableElement for Search Results

### Problem

`gr.Dataframe(wrap=True)` does not provide adequate text wrapping for search results - columns remain too wide.

### Solution

Create `HTMLTableElement` class that generates HTML tables with CSS for proper text wrapping. Replace `gr.Dataframe` with `gr.HTML` in search component only.

### Design

```python
# src/sae_scope/frontend/components/html_table.py

class HTMLTableElement:
    """HTML table generator with proper text wrapping."""

    def __init__(self, df: pd.DataFrame, max_width: int = 400):
        self._df = df
        self._max_width = max_width

    def html(self) -> str:
        """Return HTML string for gr.HTML component."""
        # Inline CSS + table HTML
        ...
```

### Files to Modify

| File | Changes |
|------|---------|
| `src/sae_scope/frontend/components/html_table.py` | NEW: HTMLTableElement class |
| `src/sae_scope/frontend/components/search_component.py` | Replace gr.Dataframe with gr.HTML |
| `src/sae_scope/frontend/components/data_tab.py` | Update handler to return HTMLTableElement.html() |
| `src/sae_scope/frontend/components/features_tab.py` | Update handler to return HTMLTableElement.html() |
