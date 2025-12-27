# Implementation Plan: Feature Search Modes - User Story 4 (SAE Retrieval Tab)

**Branch**: `002-feature-search-modes` | **Date**: 2025-12-27 | **Spec**: `spec.md`
**Input**: Feature specification from `/specs/002-feature-search-modes/spec.md`

**Note**: This plan focuses on User Story 4 (SAE Retrieval Tab). User Stories 1-3 are already implemented.

## Summary

Add an "SAE Retrieval" tab that provides unified search UI. InterpEmbedRetriever implements text retrieval using latent-based document scoring:
1. Retrieve candidate latents by dense embedding similarity (labels vs query)
2. (Optional) Rerank relevant latents with LLM (stub only, not implemented)
3. Score documents by weighted sum of latent activations (with tunable temperature)

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

### 1. Text Retrieval Algorithm

**Decision**: Latent-based document scoring with temperature-controlled softmax weighting.

**Algorithm**:
```
Input: query (string), latents (N docs x F features), temperature (float)
Output: list[TextSearchResult] sorted by score

1. RETRIEVE: Use Retriever to get top-k features by label similarity to query
   - result = retriever.search(query, mode=VECTOR, k=candidate_k)
   - candidate_features = [(r.index, r.score) for r in result]

2. RERANK (stub): Optional LLM reranking of candidate features
   - reranked_features = rerank(candidate_features, query)  # Returns same list (stub)

3. SCORE: For each document, compute weighted sum of latent activations
   - weights = softmax([score / temperature for (idx, score) in reranked_features])
   - For each doc_i in range(N):
       doc_score = sum(weights[j] * latents[doc_i, idx_j] for j, (idx_j, _) in enumerate(reranked_features))

4. RANK: Sort documents by score, return top-k
```

**Rationale**:
- Uses existing Retriever for feature selection (DRY)
- Temperature controls score distribution sharpness (lower = more peaked)
- Softmax ensures weights sum to 1
- Pure numpy implementation for efficiency

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

### 5. UI Layout for SAE Retrieval Tab

**Decision**: Single search input, parameter controls, two result sections.

**Layout**:
```
SAE Retrieval Tab
├── Search Mode Dropdown (Lexical/Vector/Hybrid)
├── Search Query Input
├── Row:
│   ├── Max Results (Number, default 10)
│   ├── Candidate Features (Number, default 10)
│   └── Temperature (Number, default 1.0)
├── Search Button
├── Results:
│   ├── Accordion: "Feature Labels" (k results)
│   │   └── Dataframe: [Index, Label, Score]
│   └── Accordion: "Dataset Texts" (k results)
│       └── Dataframe: [Index, Text (truncated), Score]
```

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
| __init__ | feature_retriever, dataset | None | Initialize with retriever and dataset |
| search_features | query, mode, k | list[SearchResult] | Delegate to feature_retriever |
| search_texts | query, mode, k, candidate_k, temperature | list[TextSearchResult] | Latent-based text retrieval |
| _rerank_features | features, query | list[tuple] | LLM reranking stub |
| _score_documents | feature_weights, k | list[TextSearchResult] | Compute weighted scores |

**Note on interp_embed API**: The `sort_by_features()` and `top_documents_for_feature()` methods in interp_embed operate on single features (finding which feature is "top" per document), not on weighted combinations. The weighted sum scoring requires custom implementation using:
- `dataset._latents` (cached matrix from `latents(aggregation_method)`)
- `dataset._dataset.documents()` for text retrieval

### Relationships

```text
InterpEmbedRetriever
    |
    +---(has-a)---> Retriever (for feature label search)
    +---(has-a)---> InterpEmbedDataset (wraps interp_embed.Dataset)
    |
    +---> search_features() -> list[SearchResult]
    +---> search_texts() -> list[TextSearchResult]
             |
             +---> Retriever.search() (step 1)
             +---> _rerank_features() (step 2, stub)
             +---> _score_documents() (step 3)
```

### Algorithm Details

**Step 1: Retrieve candidate features**
```python
results = self._feature_retriever.search(query, mode, k=candidate_k)
candidates = [(r.index, r.score) for r in results]
```

**Step 2: Rerank (stub)**
```python
reranked = self._rerank_features(candidates, query)  # Returns unchanged
```

**Step 3: Score documents**
```python
# Normalize weights with temperature
scores = np.array([score for _, score in reranked])
weights = softmax(scores / temperature)

# Compute document scores using dataset's cached latents
feature_indices = [idx for idx, _ in reranked]
latents = self._dataset._latents  # Cached matrix (N x F)
doc_scores = latents[:, feature_indices] @ weights  # (N,)

# Get texts via interp_embed API
texts = self._dataset._dataset.documents()

# Sort and return top-k
top_indices = np.argsort(doc_scores)[::-1][:k]
```

---

## Quickstart Additions (US4)

### Scenario 5: SAE Retrieval Tab - Feature Search

1. Load a dataset
2. Open "SAE Retrieval" tab
3. Enter a search query
4. Verify feature label results appear in "Feature Labels" section

### Scenario 6: SAE Retrieval Tab - Text Search

1. Load a dataset
2. Open "SAE Retrieval" tab
3. Enter a search query
4. Verify text results appear in "Dataset Texts" section
5. Adjust temperature and observe score distribution changes

### Scenario 7: Temperature Parameter Effect

1. Enter a query
2. Set temperature = 0.5 (sharp)
3. Note which documents score highest
4. Set temperature = 2.0 (flat)
5. Observe more diverse document scores

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
