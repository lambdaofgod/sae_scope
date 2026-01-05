# Implementation Plan: Gradio Result Columns Configuration

**Branch**: `003-gradio-result-columns` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-gradio-result-columns/spec.md`

## Summary

Refactor the Gradio frontend to:
1. Split monolithic `app.py` into tab-specific modules
2. Add column selection multiselect after dataset load
3. Display selected columns in search results alongside the text column

## Technical Context

**Language/Version**: Python 3.10
**Primary Dependencies**: Gradio 5.x, Pandas, Plotly Express
**Storage**: Local .pkl files in /data directory
**Testing**: pytest
**Target Platform**: Local desktop (web browser)
**Project Type**: Single project with frontend/backend split

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Single Responsibility | VIOLATION | Current `app.py` (773 lines) handles all tabs - will be fixed by this refactor |
| Open/Closed | PASS | Tab modules will allow extension without modifying core |
| Liskov Substitution | N/A | No inheritance hierarchies affected |
| Interface Segregation | PASS | Tab interfaces will be focused |
| Dependency Inversion | PASS | Tabs depend on abstractions (dataset interface) |
| DRY | PASS | Column selection logic centralized |
| Fail-First | PASS | Will use gr.Error for invalid states |

**Post-design re-check**: The refactor resolves the SRP violation by splitting tabs into separate modules.

## Project Structure

### Documentation (this feature)

```text
specs/003-gradio-result-columns/
  plan.md              # This file
  research.md          # Phase 0 output
  data-model.md        # Phase 1 output
  quickstart.md        # Phase 1 output
  contracts/           # Phase 1 output (N/A - no API)
  tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/sae_scope/
  frontend/
    app.py                     # Main app, creates Blocks and wires tabs
    components/
      __init__.py
      tabs.py                  # Existing: create_scatterplot helper
      scatterplot_tab.py       # NEW: Scatterplot tab UI and handlers
      features_tab.py          # NEW: Features tab UI and handlers
      data_tab.py              # NEW: Data tab UI and handlers
      sae_retrieval_tab.py     # NEW: SAE Retrieval tab UI and handlers
  backend/
    interp_dataset.py          # MODIFY: Add get_column_names(), get_dataframe_with_columns()

tests/
  unit/
  integration/
```

**Structure Decision**: Keep single project structure but split frontend into modular tab components.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Refactoring during feature work | SRP violation in app.py makes feature addition error-prone | Adding more code to 773-line file increases tech debt |

## Design Overview

### 1. Frontend Refactor (Tab Modules)

Each tab module exports:
- `create_<tab>_ui()` - Returns dict of Gradio components
- `wire_<tab>_events(components, state)` - Connects handlers to components

**app.py** becomes orchestrator:
```python
def create_app():
    with gr.Blocks() as app:
        state = create_shared_state()
        header = create_header()

        scatterplot = create_scatterplot_ui()
        features = create_features_ui()
        data = create_data_ui()
        sae_retrieval = create_sae_retrieval_ui()

        wire_scatterplot_events(scatterplot, state)
        wire_features_events(features, state)
        wire_data_events(data, state)
        wire_sae_retrieval_events(sae_retrieval, state)
    return app
```

### 2. Column Selection Feature

**UI Wireframe - Dataset Loading Component**:

```text
+------------------------------------------------------------------+
|  # SAE Scope Dashboard                                           |
+------------------------------------------------------------------+
|                                                                  |
|  Select Dataset          Aggregation Method                      |
|  +--------------------+  +--------------------+                  |
|  | roam_df20250217.pkl|  | max             v |                  |
|  +--------------------+  +--------------------+                  |
|                                                                  |
|  Additional Columns to Display (appears after dataset loads)     |
|  +------------------------------------------------------------+  |
|  | [x] file_name    [x] heading    [ ] level    [ ] body      |  |
|  | [ ] org_id       [ ] links                                 |  |
|  +------------------------------------------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
|  [ Scatterplot ]  [ Features ]  [ Data ]  [ SAE Retrieval ]      |
+------------------------------------------------------------------+
|                                                                  |
|  (Tab content here)                                              |
|                                                                  |
+------------------------------------------------------------------+
```

**Search Results with Selected Columns** (SAE Retrieval tab):

```text
+------------------------------------------------------------------+
|  ### Phase 2: Find Texts                                         |
|                                                                  |
|  Temperature: [1.0]     Max Results: [10]                        |
|                                                                  |
|  [ Find Texts ]                                                  |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | Index | Text (truncated)        | Score  | file_name | ... |  |
|  |-------|-------------------------|--------|-----------|-----|  |
|  |   42  | "The game features..." | 0.8234 | review.md |     |  |
|  |  128  | "Combat system is..."  | 0.7891 | notes.md  |     |  |
|  |   15  | "Multiplayer mode..."  | 0.6543 | guide.md  |     |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

**UI Changes** (in app.py header area):
- After dataset dropdown and aggregation dropdown, add:
  - `column_selector`: gr.CheckboxGroup for additional columns (hidden until dataset loaded)

**Backend Changes** (InterpEmbedDataset):
- `get_column_names()` - Returns list of all DataFrame column names
- `get_dataframe_with_columns(columns: list[str])` - Returns DataFrame with specified columns

**Data Flow**:
1. User selects dataset, clicks Load
2. `on_dataset_select` calls `dataset.get_column_names()`
3. Populates `column_selector` with columns except text column
4. User selects additional columns
5. Search results use `dataset.get_dataframe_with_columns([text_col] + selected)`

### 3. Files to Modify

| File | Changes |
|------|---------|
| `src/sae_scope/frontend/app.py` | Slim down to orchestrator, add column_selector |
| `src/sae_scope/frontend/components/scatterplot_tab.py` | NEW: Extract scatterplot tab code |
| `src/sae_scope/frontend/components/features_tab.py` | NEW: Extract features tab code |
| `src/sae_scope/frontend/components/data_tab.py` | NEW: Extract data tab code |
| `src/sae_scope/frontend/components/sae_retrieval_tab.py` | NEW: Extract SAE retrieval tab code, update to use selected columns |
| `src/sae_scope/backend/interp_dataset.py` | Add get_column_names(), get_dataframe_with_columns() |

## Phase Implementation Order

1. **Phase 1**: Add backend methods for column access (no UI changes yet)
2. **Phase 2**: Refactor frontend - extract tabs to modules
3. **Phase 3**: Add column selector UI component
4. **Phase 4**: Wire column selection to search results display
5. **Phase 5**: Testing and validation
