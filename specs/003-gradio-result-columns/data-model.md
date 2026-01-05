# Data Model: Gradio Result Columns Configuration

## Entities

### Dataset (existing - InterpEmbedDataset)

| Field | Type | Description |
|-------|------|-------------|
| _dataset | interp_embed.Dataset | Underlying dataset from interp-embed library |
| _latents | np.ndarray | Activation matrix (N docs x F features) |
| _aggregation_method | str | How latents are aggregated |
| _feature_stats | pd.DataFrame | Computed feature statistics |

**New Methods**:

```python
def get_column_names(self) -> list[str]:
    """Return all column names from the underlying DataFrame."""
    return list(self._dataset._df.columns)

def get_text_field(self) -> str:
    """Return the field name used for SAE training (always displayed)."""
    return self._dataset._field

def get_dataframe_with_columns(self, columns: list[str]) -> pd.DataFrame:
    """Return DataFrame with specified columns plus index."""
    df = self._dataset._df[columns].copy()
    df.insert(0, 'index', range(len(df)))
    return df
```

### Column Selection State (new - Gradio State)

| Field | Type | Description |
|-------|------|-------------|
| available_columns | list[str] | All columns except text field |
| selected_columns | list[str] | User-selected additional columns |

**Lifecycle**:
1. Created empty on app init
2. Populated when dataset loads
3. Updated when user changes selection
4. Used when displaying search results

## Data Flow

```text
[Dataset Pickle]
    |
    v
[InterpEmbedDataset.load()]
    |
    +---> get_column_names() --> [available_columns]
    |
    +---> get_text_field() --> [text_column] (always shown)
    |
    v
[User selects columns in CheckboxGroup]
    |
    v
[selected_columns state updated]
    |
    v
[Search executed]
    |
    v
[get_dataframe_with_columns([text_col] + selected)] --> [Results display]
```

## Validation Rules

- `selected_columns` must be subset of `available_columns`
- `text_field` is never in `available_columns` (always displayed separately)
- Empty `selected_columns` is valid (shows only text column)
