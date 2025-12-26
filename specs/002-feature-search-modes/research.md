# Research: Feature Search Modes

**Date**: 2025-12-26
**Feature**: 002-feature-search-modes

## Research Summary

Technical decisions for implementing multi-mode feature label search with Weaviate vector database.

## Research Questions

### 1. Vector Database Choice

**Decision**: Use Weaviate with text2vec-transformers module (ONNX variant for speed).

**Rationale**:
- User specified Weaviate as requirement
- Built-in vectorization via text2vec module (no separate embedding service needed)
- Simple Docker Compose setup
- Python client with good async support
- Hybrid search (BM25 + vector) built-in

**Alternatives Considered**:
- ChromaDB: Simpler but less mature hybrid search
- Pinecone: SaaS, requires API key, not self-hosted
- Qdrant: Good but Weaviate's hybrid search better documented

### 2. Docker Compose Configuration

**Decision**: Two services - weaviate and text2vec-transformers-onnx.

**Configuration**:
```yaml
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 100
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: true
      PERSISTENCE_DATA_PATH: /var/lib/weaviate
      DEFAULT_VECTORIZER_MODULE: text2vec-transformers
      ENABLE_MODULES: text2vec-transformers
      TRANSFORMERS_INFERENCE_API: http://text2vec:8080
    volumes:
      - weaviate_data:/var/lib/weaviate
    depends_on:
      - text2vec

  text2vec:
    image: semitechnologies/transformers-inference-onnx:sentence-transformers-all-MiniLM-L6-v2
    environment:
      ENABLE_CUDA: 0

volumes:
  weaviate_data:
```

**Rationale**:
- ONNX runtime is significantly faster than PyTorch for inference
- all-MiniLM-L6-v2 is fast and effective for short text (feature labels)
- Anonymous access for local development simplicity
- Persistent volume for data between restarts

### 3. Lexical Search Implementation

**Decision**: Use Weaviate's built-in BM25 search.

**Rationale**:
- Weaviate provides native BM25 via `bm25` query type
- No additional dependency needed
- Consistent interface across all search modes
- Can add rank_bm25 later if offline lexical search needed

### 4. Abstract Retriever Interface

**Decision**: Abstract base class with `search(query: str, k: int)` method.

**Interface**:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class SearchResult:
    index: int
    label: str
    score: float
    metadata: dict = field(default_factory=dict)

class Retriever(ABC):
    @abstractmethod
    def index(self, labels: list[str]) -> None:
        """Index feature labels for search."""
        ...

    @abstractmethod
    def search(self, query: str, k: int = 100) -> list[SearchResult]:
        """Search for features matching query, return top k results."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if retriever is ready (e.g., Weaviate is running)."""
        ...
```

**Rationale**:
- Simple interface covering all search modes
- `index()` allows lazy initialization when dataset loads
- `is_available()` enables graceful degradation
- `SearchResult` dataclass standardizes output format
- `metadata` dict allows storing additional info (source, scores breakdown, etc.)

### 5. Hybrid Search Strategy

**Decision**: Use Weaviate's native hybrid search with alpha parameter.

**Rationale**:
- Weaviate provides built-in hybrid combining BM25 and vector scores
- Alpha parameter controls blend (0=BM25, 1=vector, 0.5=balanced)
- Single query instead of separate BM25 + vector queries
- Consistent scoring methodology

**Configuration**:
- Default alpha: 0.5 (equal weight to lexical and vector)
- Can be exposed as user setting in future

### 6. Weaviate Collection Strategy - Per-Dataset Collections

**Decision**: Create one Weaviate collection per dataset file, named after the dataset.

**Collection Naming**:
- Collection name derived from dataset filename (sanitized for Weaviate naming rules)
- Example: `emotions_sae_features.pkl` -> `EmotionsSaeFeatures` collection
- Must start with uppercase letter, alphanumeric only

**Schema** (per collection):
```python
{
    "class": "<DatasetName>",  # e.g., "EmotionsSaeFeatures"
    "properties": [
        {
            "name": "label",
            "dataType": ["text"],
        },
        {
            "name": "feature_index",
            "dataType": ["int"],
        }
    ],
    "vectorizer": "text2vec-transformers",
}
```

**Rationale**:
- Different datasets have different feature labels
- Avoid re-indexing when switching datasets
- Collections persist across sessions (Weaviate data volume)
- Clear separation between datasets

### 7. Indexing Flow

**Decision**: Lazy indexing on dataset load with collection existence check.

**Flow**:
1. User selects dataset from dropdown
2. Derive collection name from dataset filename
3. Check if collection exists in Weaviate
4. If exists: Use existing collection (no re-indexing)
5. If not exists: Create collection and index all feature labels
6. Retriever ready for search

**Rationale**:
- No redundant indexing for previously loaded datasets
- Indexing happens once per dataset, not per session
- Transparent to user (just slightly slower first load)

### 8. Error Handling (Fail-First)

**Decision**: Fail explicitly when Weaviate is unavailable. No fallbacks.

**Behavior**:
- On startup/dataset load: Check Weaviate connection
- If unavailable: Raise error, do not proceed with search features
- If connection lost mid-session: Raise error on next search attempt
- Vector/Hybrid modes require Weaviate - no exceptions

**Rationale**:
- Per constitution Fail-First principle: no silent fallbacks
- Users must know when the system cannot function as expected
- Clear error messages guide user to start Weaviate

## Dependencies

New dependencies to add:
- weaviate-client (>=4.0.0)

## Open Questions (None)

All technical questions resolved. Ready to proceed with implementation.
