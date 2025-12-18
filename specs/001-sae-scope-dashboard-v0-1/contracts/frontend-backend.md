# Frontend-Backend Contract: SAE Scope Dashboard v0.1

**Date**: 2025-12-18
**Feature**: 001-sae-scope-dashboard-v0-1

## Overview

This document defines the contract between the Gradio frontend and the Python backend. Since this is a single-process application (not a web API), contracts are defined as Python function signatures and return types.

## Data Flow

```text
User Action          Frontend (Gradio)              Backend
-----------          -----------------              -------
Load File     -->    File Upload Component   -->    SAELensDataset.load()
                                             <--    SAELensDataset instance

Get Features  -->    Sidebar render          -->    dataset.features.get_all_formatted_labels()
                                             <--    list[str]

Search        -->    Search input            -->    dataset.features.search(query)
                                             <--    list[tuple[int, str]]

Select Axes   -->    Feature checkboxes      -->    dataset.get_scatter_dataframe(x_idx, y_idx)
                                             <--    pd.DataFrame

Render Plot   -->    gr.Plot                 -->    plotly.express.scatter(df, ...)
                                             <--    plotly.graph_objects.Figure
                     (hover shows text via Plotly's native hover_data)

View Data     -->    Data tab                -->    dataset.get_text_dataframe()
                                             <--    pd.DataFrame
```

## Contract Definitions

### 1. Dataset Loading

**Trigger**: User selects file via `gr.File` component

**Input**: File path (str)

**Output**: `SAELensDataset` instance or error

**Error Conditions**:
- `FileNotFoundError`: File does not exist
- `ValueError`: File format invalid or missing required data

### 2. Feature List Retrieval

**Trigger**: After dataset load, sidebar needs feature list

**Input**: None (uses loaded dataset)

**Output**: `list[str]` - Formatted labels like `["0: feature_a", "1: feature_b", ...]`

**Contract**:
```python
def get_feature_choices(dataset: SAELensDataset) -> list[str]:
    return dataset.features.get_all_formatted_labels()
```

### 3. Feature Search

**Trigger**: User types in search input

**Input**:
- `query: str` - Search string

**Output**: `list[str]` - Filtered formatted labels

**Contract**:
```python
def search_features(dataset: SAELensDataset, query: str) -> list[str]:
    if not query.strip():
        return dataset.features.get_all_formatted_labels()
    results = dataset.features.search(query)
    return [dataset.features.get_formatted_label(idx) for idx, _ in results]
```

**Error Conditions**:
- Empty query returns all features (not an error)

### 4. Scatterplot Data

**Trigger**: User selects two features from sidebar

**Input**:
- `feature_x: str` - Formatted label for X axis
- `feature_y: str` - Formatted label for Y axis

**Output**: `pd.DataFrame` with columns `["x", "y", "text"]`

**Contract**:
```python
def get_scatter_data(
    dataset: SAELensDataset,
    feature_x: str,
    feature_y: str
) -> pd.DataFrame:
    x_idx = dataset.features.parse_formatted_label(feature_x)
    y_idx = dataset.features.parse_formatted_label(feature_y)
    return dataset.get_scatter_dataframe(x_idx, y_idx)
```

**Plotly Usage**:
```python
import plotly.express as px

fig = px.scatter(
    df,
    x="x",
    y="y",
    hover_data=["text"]  # Text displayed on hover via Plotly native feature
)
```

**Error Conditions**:
- `ValueError`: Same feature selected for both axes
- `ValueError`: Invalid formatted label string

### 5. Data Table

**Trigger**: User switches to Data tab

**Input**: None (uses loaded dataset)

**Output**: `pd.DataFrame` with columns `["index", "text"]`

**Contract**:
```python
def get_data_table(dataset: SAELensDataset) -> pd.DataFrame:
    return dataset.get_text_dataframe()
```

## Gradio Component Mapping

| User Story | Gradio Component | Backend Method |
|------------|------------------|----------------|
| Load Data | `gr.File` | `SAELensDataset.load()` |
| Feature List | `gr.CheckboxGroup` | `features.get_all_formatted_labels()` |
| Search | `gr.Textbox` | `features.search()` |
| Scatterplot | `gr.Plot` | `get_scatter_dataframe()` |
| Text Display | Plotly hover | N/A (native Plotly feature using `hover_data`) |
| Data Tab | `gr.Dataframe` | `get_text_dataframe()` |
| Sidebar Toggle | `gr.Sidebar` | N/A (UI only) |

## State Management

The frontend maintains:
- `current_dataset: SAELensDataset | None` - Loaded dataset instance
- `selected_features: tuple[str, str]` - Currently selected feature labels for axes

State is managed via Gradio's `gr.State` component.

## Notes

- Text inspection is handled natively by Plotly's hover feature - no separate click handling required
- The scatterplot DataFrame includes the "text" column specifically for Plotly's `hover_data` parameter
