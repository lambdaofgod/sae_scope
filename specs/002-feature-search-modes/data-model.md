# Data Model: Feature Search Modes

**Feature**: 002-feature-search-modes
**Date**: 2025-12-26

## Entities

### SearchMode (Enum)

Enumeration of available search strategies.

| Value | Description |
|-------|-------------|
| LEXICAL | Keyword-based BM25 search |
| VECTOR | Semantic similarity search using embeddings |
| HYBRID | Combined lexical and vector search |

### SearchResult (Dataclass)

A single search result item.

| Field | Type | Description |
|-------|------|-------------|
| index | int | Feature index in the dataset |
| label | str | Feature label text |
| score | float | Relevance score (higher = more relevant) |
| metadata | dict | Additional info (e.g., score breakdown, source) |

### Retriever (Abstract Class)

Abstract interface for search implementations.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| ensure_indexed | dataset_name: str, labels: list[str] | None | Ensure labels are indexed for dataset |
| search | query: str, mode: SearchMode, k: int | list[SearchResult] | Find top k matching features |

### WeaviateRetriever (Concrete Class)

Weaviate-based implementation supporting all three search modes.

| Attribute | Type | Description |
|-----------|------|-------------|
| client | WeaviateClient | Weaviate client connection |
| current_collection | str | Active collection name (derived from dataset) |

| Method | Description |
|--------|-------------|
| ensure_indexed | Check if collection exists, create and populate if not |
| search | Query Weaviate with BM25, vector, or hybrid based on mode |

## Relationships

```text
SearchMode (enum)
    |
    v
Retriever (abstract) <--- WeaviateRetriever (concrete)
    |
    +---> returns list[SearchResult]
```

## Weaviate Schema

Collection: `<DatasetName>` (one per dataset, e.g., `EmotionsSaeFeatures`)

| Property | Type | Vectorized | Description |
|----------|------|------------|-------------|
| label | text | Yes | Feature label text |
| feature_index | int | No | Original index in dataset |

## State Transitions

### Dataset Load Flow

```text
User selects dataset
    |
    v
Derive collection name from filename
    |
    v
Check if collection exists in Weaviate
    |
    +--[exists]-----> Use existing collection
    |
    +--[not exists]--> Create collection
                           |
                           v
                       Index all feature labels
                           |
                           v
                       Retriever ready
```

### Search Flow

```text
User enters search query
    |
    v
Get current search mode from dropdown
    |
    v
retriever.search(query, mode, k=100)
    |
    v
Results displayed in dataframe
```

## Validation Rules

1. **SearchResult.index**: Must be >= 0
2. **SearchResult.score**: Must be >= 0.0
3. **Retriever.search k parameter**: Must be >= 1 and <= 1000
4. **Query string**: Must not be empty for vector/hybrid search (empty returns first N for lexical)
