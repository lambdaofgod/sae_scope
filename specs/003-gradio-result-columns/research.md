# Research: Gradio Result Columns Configuration

## Current Architecture Analysis

### app.py Structure (773 lines)
- Global state: `_retriever`, `_interp_retriever`
- Helper functions: `list_data_files`, `search_features`, `get_summary_stats`, `get_top_n_features`
- Main function: `create_app()` containing:
  - All UI component definitions (4 tabs)
  - All event handlers (8 nested functions)
  - All event wiring

### Existing Tab Components
- `components/tabs.py`: Only contains `create_scatterplot()` helper and unused `create_tabs()`

### Dataset Column Access
- Pickle files contain `dataset` key with DataFrame
- DataFrame has named columns (e.g., `text`, `section_header`, `file_name`, `heading`, etc.)
- `field` key specifies which column was used for SAE training
- Current `get_text_dataframe()` only returns `index` and `text` columns

## Research Findings

### R1: Gradio Tab Module Pattern

**Decision**: Each tab module exports UI creation and event wiring functions separately

**Rationale**:
- Gradio components must be created within `gr.Blocks()` context
- Event handlers need access to shared state
- Separating UI creation from wiring allows clean orchestration

**Alternatives considered**:
- Single function returning both UI and handlers - rejected because handlers need state references
- Class-based tabs - rejected as over-engineering for this use case

### R2: Column Selection Component

**Decision**: Use `gr.CheckboxGroup` for column selection

**Rationale**:
- Consistent with existing latent selection pattern in SAE Retrieval tab
- Allows multiple columns to be selected
- Native Gradio component, no custom CSS needed

**Alternatives considered**:
- `gr.Dropdown` with `multiselect=True` - works but checkboxes are clearer
- Custom HTML/JS component - over-engineering

### R3: Column Data Access

**Decision**: Add methods to InterpEmbedDataset for column access

**Rationale**:
- Keeps DataFrame access encapsulated in dataset class
- Consistent with existing `get_text_dataframe()` pattern

**Methods to add**:
- `get_column_names() -> list[str]` - Returns all column names from underlying DataFrame
- `get_text_field() -> str` - Returns the field name used for SAE (always displayed)
- `get_dataframe_with_columns(columns: list[str]) -> pd.DataFrame` - Returns DataFrame with specified columns

### R4: Result Display Updates

**Decision**: Modify search result display to include selected columns

**Affected components**:
- Data tab: `dataframe` component already shows full data
- SAE Retrieval tab: `text_results` needs to show additional columns

**Implementation**:
- Pass selected columns to result formatting functions
- Dynamic column headers based on selection
