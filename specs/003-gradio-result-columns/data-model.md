# Data Model: Data Tab Refactor with Text Search

## Entities

### TextSearchResult (new concept)

| Field | Type | Description |
|-------|------|-------------|
| index | int | Document index in dataset |
| text | str | Document text (truncated for display) |
| score | float | Search relevance score |
| column_data | dict | Additional column values from dataset |

### Weaviate Collections

**Existing**: `{dataset_name}_features` - Feature labels for semantic search

**New**: `{dataset_name}_texts` - Document texts for semantic search

| Field | Type | Description |
|-------|------|-------------|
| doc_index | int | Index in original dataset |
| content | str | Full document text |

## Data Flow

```text
[User enters query in Data tab]
    |
    v
[WeaviateRetriever.search() on texts collection]
    |
    v
[Get top-k document indices + scores]
    |
    v
[InterpEmbedDataset.get_dataframe_with_columns()]
    |
    v
[Return DataFrame: index, selected_columns, text, Score]
```

## Component Relationships

```text
create_search_ui() --> returns dict of Gradio components
    |
    +-- search_mode: gr.Dropdown
    +-- max_results: gr.Number
    +-- query: gr.Textbox
    +-- search_btn: gr.Button
    +-- results: gr.Dataframe

data_tab uses:
    +-- create_search_ui() for text search
    +-- gr.Accordion for full data view
    +-- WeaviateRetriever for text search backend

features_tab uses:
    +-- create_search_ui() for feature search (refactored)
    +-- WeaviateRetriever for feature search backend
```
