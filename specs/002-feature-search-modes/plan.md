# Implementation Plan: Feature Search Modes - User Story 4 (SAE Retrieval Tab)

**Branch**: `002-feature-search-modes` | **Date**: 2025-12-27 | **Spec**: `spec.md`
**Input**: Feature specification from `/specs/002-feature-search-modes/spec.md`

**Note**: This plan focuses on User Story 4 (SAE Retrieval Tab). User Stories 1-3 are already implemented.

## Summary

Add an "SAE Retrieval" tab with a two-phase text search workflow:

**Phase 1 - Find Latents**: User enters query, retrieves candidate latents by label similarity. Results displayed with checkboxes (all selected by default).

**Phase 2 - Find Texts**: User selects which latents to use, then scores documents by weighted sum of selected latent activations (with tunable temperature).

This gives researchers control over which latents influence text matching.

## Technical Context

**Language/Version**: Python 3.10
**Primary Dependencies**: Gradio 5.x, weaviate-client (existing), numpy
**Storage**: Weaviate vector database (for feature label search)
**Testing**: Manual validation via quickstart scenarios
**Target Platform**: Local development (macOS/Linux)
**Project Type**: Single project (src/sae_scope/)
**Performance Goals**: Search results within 2 seconds
**Constraints**: Weaviate must be running; fail-first on unavailable
**Scale/Scope**: Feature labels (~10k) + dataset texts (~10k documents)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Single Responsibility | PASS | InterpEmbedRetriever: text retrieval; Retriever: feature search |
| Open/Closed | PASS | Extends pattern without modifying existing code |
| Liskov Substitution | N/A | Uses composition, not inheritance |
| Interface Segregation | PASS | Focused methods: search_features, search_texts |
| Dependency Inversion | PASS | Depends on abstract Retriever, not WeaviateRetriever |
| DRY | PASS | Reuses Retriever for feature label search |
| Fail-First | PASS | Errors propagate, no silent fallbacks |

## Project Structure

### Documentation (this feature)

```text
specs/002-feature-search-modes/
├── plan.md              # This file
├── research.md          # Existing (augmented for US4)
├── data-model.md        # Existing (augmented for US4)
├── quickstart.md        # Existing (augmented for US4)
└── tasks.md             # Will be updated by /speckit.tasks
```

### Source Code

```text
src/sae_scope/
├── backend/
│   ├── retriever/
│   │   ├── __init__.py         # Add InterpEmbedRetriever, TextSearchResult exports
│   │   ├── base.py             # Add TextSearchResult dataclass
│   │   ├── weaviate.py         # Existing (no changes)
│   │   └── interp_embed.py     # NEW: InterpEmbedRetriever implementation
│   └── interp_dataset.py       # Existing (no changes)
└── frontend/
    └── app.py                  # Add SAE Retrieval tab
```

**Structure Decision**: Single project structure. New file `interp_embed.py` in existing retriever module.

## Complexity Tracking

No constitution violations requiring justification.

---

## Phase 0: Research (US4 - Text Retrieval Algorithm)

### 1. Two-Phase Text Retrieval Workflow

**Decision**: Split retrieval into two user-controlled phases.

**Phase 1 - Find Latents**:
```
Input: query (string), mode (SearchMode), candidate_k (int)
Output: list[SearchResult] with checkboxes for selection

1. Use Retriever to get top-k features by label similarity
   - results = retriever.search(query, mode, k=candidate_k)
2. Display results with checkboxes (all selected by default)
3. User can select/deselect individual latents
```

**Phase 2 - Find Texts**:
```
Input: selected_features (list of (index, score)), temperature (float), k (int)
Output: list[TextSearchResult] sorted by score

1. RERANK (stub): Optional LLM reranking
   - reranked = rerank(selected_features, query)  # Returns same list

2. SCORE: Compute weighted sum of latent activations
   - weights = softmax([score / temperature for (idx, score) in reranked])
   - doc_scores = latents[:, feature_indices] @ weights

3. RANK: Sort documents by score, return top-k
```

**Rationale**:
- Two phases give user control over which latents influence text matching
- Can refine text results by changing selection without re-searching
- Temperature controls score distribution sharpness
- Softmax ensures weights sum to 1

### 2. Temperature Parameter

**Decision**: Default temperature = 1.0, exposed as UI parameter.

**Rationale**:
- temperature=1.0: Standard softmax behavior
- temperature<1.0: Sharper distribution, top features dominate
- temperature>1.0: Flatter distribution, more features contribute

**UI**: Number input in SAE Retrieval tab, range 0.1-10.0

### 3. Candidate Feature Count (candidate_k)

**Decision**: Default candidate_k = 10, separate from result limit k.

**Rationale**:
- candidate_k controls how many features influence document scoring
- k controls how many documents to return
- These are independent parameters

**UI**: Number input in SAE Retrieval tab, range 1-100

### 4. LLM Reranking Stub

**Decision**: Create stub method that returns input unchanged.

```python
def _rerank_features(
    self,
    features: list[tuple[int, float]],
    query: str,
) -> list[tuple[int, float]]:
    """Rerank features using LLM (stub - not implemented).

    Returns input unchanged. Will be implemented when LLM connection available.
    """
    return features
```

**Rationale**:
- Interface ready for future LLM integration
- No actual LLM calls (per user request)
- Easy to extend later

### 5. UI Layout for SAE Retrieval Tab (Two-Phase)

**Decision**: Two-phase workflow with latent selection between phases.

**ASCII Wireframe**:
```
+------------------------------------------------------------------+
|  SAE Retrieval                                                   |
+------------------------------------------------------------------+
|                                                                  |
|  === PHASE 1: Find Latents ===                                   |
|                                                                  |
|  Search Mode: [Hybrid v]    Candidate Count: [10]                |
|                                                                  |
|  Query: [                                                    ]   |
|                                                                  |
|  [ Find Latents ]                                                |
|                                                                  |
|  +--------------------------------------------------------------+|
|  | v Retrieved Latents (select for text search)                 ||
|  +--------------------------------------------------------------+|
|  | [x] | Index | Label                          | Score          ||
|  |-----|-------|--------------------------------|----------------|  |
|  | [x] | 42    | emotional_response             | 0.89           ||
|  | [x] | 17    | sentiment_positive             | 0.76           ||
|  | [ ] | 103   | feeling_expression             | 0.71           ||
|  | [x] | 88    | mood_indicator                 | 0.68           ||
|  +--------------------------------------------------------------+|
|                                                                  |
|  === PHASE 2: Find Texts ===                                     |
|                                                                  |
|  +----------------------+  +----------------------+              |
|  | Temperature          |  | Max Results          |              |
|  | [1.0            ]    |  | [10             ]    |              |
|  +----------------------+  +----------------------+              |
|                                                                  |
|  [ Find Texts ]                                                  |
|                                                                  |
|  +--------------------------------------------------------------+|
|  | v Matching Texts                                             ||
|  +--------------------------------------------------------------+|
|  | Index | Text                               | Score            ||
|  |-------|-----------------------------------|------------------|  |
|  | 2847  | I felt so happy when I saw...     | 0.0234           ||
|  | 1523  | The joy was overwhelming and...   | 0.0189           ||
|  | 892   | Excitement filled the room as...  | 0.0156           ||
|  +--------------------------------------------------------------+|
|                                                                  |
+------------------------------------------------------------------+
```

**Component Details**:

Phase 1 - Find Latents:
- Search Mode: gr.Dropdown, choices=["Lexical", "Vector", "Hybrid"], default="Hybrid"
- Candidate Count: gr.Number, default=10, min=1, max=100
- Query: gr.Textbox, placeholder="Enter search query..."
- Find Latents: gr.Button
- Retrieved Latents: gr.Dataframe with checkbox column (Select, Index, Label, Score)

Phase 2 - Find Texts:
- Temperature: gr.Number, default=1.0, min=0.1, max=10.0, step=0.1
- Max Results: gr.Number, default=10, min=1, max=100
- Find Texts: gr.Button (disabled until latents retrieved, requires at least 1 selected)
- Matching Texts: gr.Dataframe (headers: Index, Text, Score)

**State Management**:
- Selected latents stored in gr.State as list of (index, score) tuples
- Checkbox changes update state without re-running latent search
- Text search uses only selected latents from state

### 6. Empty Query Handling

**Decision**: Empty query shows first k items from each source.

**Rationale**:
- Consistent with existing feature search behavior
- For features: first k by index
- For texts: first k by index (no scoring applied)

---

## Phase 1: Data Model (US4)

### New Entity: TextSearchResult

| Field | Type | Description |
|-------|------|-------------|
| doc_index | int | Document index in dataset |
| text | str | Document text (max 200 chars for display) |
| score | float | Computed relevance score |
| metadata | dict | Additional info (e.g., contributing features) |

### New Entity: InterpEmbedRetriever

| Attribute | Type | Description |
|-----------|------|-------------|
| _feature_retriever | Retriever | Composed retriever for feature labels |
| _dataset | InterpEmbedDataset | Dataset wrapping interp_embed.Dataset |

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| __init__ | feature_retriever: Retriever, dataset: InterpEmbedDataset | None | Initialize with retriever and dataset |
| search_latents | query: str, mode: SearchMode, k: int | list[SearchResult] | Phase 1: Find latents by label similarity |
| search_texts | selected_features: list[tuple[int, float]], temperature: float, k: int | list[TextSearchResult] | Phase 2: Score texts using selected latents |
| _rerank_features | features: list[tuple[int, float]], query: str | list[tuple[int, float]] | LLM reranking stub |
| _score_documents | feature_indices: list[int], weights: np.ndarray, k: int | list[TextSearchResult] | Compute weighted scores |

**Note on interp_embed API**: The `sort_by_features()` and `top_documents_for_feature()` methods in interp_embed operate on single features (finding which feature is "top" per document), not on weighted combinations. The weighted sum scoring requires custom implementation using:
- `dataset._latents` (cached matrix from `latents(aggregation_method)`)
- `dataset._dataset.documents()` for text retrieval

### Relationships

```text
InterpEmbedRetriever
    |
    +---(has-a)---> Retriever (for latent/feature label search)
    +---(has-a)---> InterpEmbedDataset (wraps interp_embed.Dataset)
    |
    +---> search_latents(query, mode, k) -> list[SearchResult]    # Phase 1
    |         |
    |         +---> Retriever.search(query, mode, k)
    |
    +---> search_texts(selected_features, temperature, k) -> list[TextSearchResult]  # Phase 2
              |
              +---> _rerank_features(selected_features, query)
              +---> _score_documents(feature_indices, weights, k)
```

### Algorithm Details

**Phase 1: search_latents(query, mode, k)**
```python
# Delegates to composed Retriever
return self._feature_retriever.search(query, mode, k)
```

**Phase 2: search_texts(selected_features, temperature, k)**
```python
# Rerank (stub - returns unchanged)
reranked = self._rerank_features(selected_features, query="")

# Normalize weights with temperature
scores = np.array([score for _, score in reranked])
weights = softmax(scores / temperature)

# Compute document scores
feature_indices = [idx for idx, _ in reranked]
return self._score_documents(feature_indices, weights, k)
```

**_score_documents(feature_indices, weights, k)**
```python
latents = self._dataset._latents  # Cached matrix (N x F)
doc_scores = latents[:, feature_indices] @ weights  # (N,)

texts = self._dataset._dataset.documents()

top_indices = np.argsort(doc_scores)[::-1][:k]
return [TextSearchResult(idx, texts[idx][:200], doc_scores[idx]) for idx in top_indices]
```

---

## Quickstart Additions (US4)

### Scenario 5: Two-Phase Workflow - Complete Flow

1. Load a dataset
2. Open "SAE Retrieval" tab
3. Enter a search query, click "Find Latents"
4. Verify latent results appear with checkboxes (all selected)
5. Deselect some latents by unchecking boxes
6. Click "Find Texts"
7. Verify text results appear based on selected latents only

### Scenario 6: Latent Selection Refinement

1. Complete Phase 1 (find latents)
2. Click "Find Texts" with all latents selected
3. Note the text results
4. Deselect some latents
5. Click "Find Texts" again
6. Verify text results change based on new selection

### Scenario 7: No Latents Selected

1. Complete Phase 1 (find latents)
2. Deselect all latents
3. Click "Find Texts"
4. Verify error message appears requiring at least one selection

---

## Post-Design Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Single Responsibility | PASS | InterpEmbedRetriever: unified retrieval; Retriever: feature search |
| Open/Closed | PASS | New class, no modifications to existing Retriever |
| Liskov Substitution | N/A | Uses composition, not inheritance |
| Interface Segregation | PASS | search_features and search_texts are separate |
| Dependency Inversion | PASS | Depends on abstract Retriever |
| DRY | PASS | Feature search delegates to existing Retriever |
| Fail-First | PASS | Errors propagate, no silent fallbacks |

---

## Next Steps

Run `/speckit.tasks` to generate implementation tasks.
