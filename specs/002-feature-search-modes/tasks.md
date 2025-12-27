# Tasks: Feature Search Modes

**Input**: Design documents from `/specs/002-feature-search-modes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested in specification - test tasks not included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/sae_scope/` at repository root
- Docker Compose at repository root

---

## Phase 1: Setup (Infrastructure)

**Purpose**: Docker Compose configuration and dependency installation

- [X] T001 Create docker-compose.yml at repository root with Weaviate and text2vec-transformers-onnx services
- [X] T002 Add weaviate-client dependency using `uv add weaviate-client`
- [X] T003 Verify Weaviate services start correctly with `docker-compose up -d`

---

## Phase 2: Foundational (Abstract Retriever)

**Purpose**: Core abstractions that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create src/sae_scope/backend/retriever/__init__.py with public exports
- [X] T005 [P] Create SearchMode enum in src/sae_scope/backend/retriever/base.py with LEXICAL, VECTOR, HYBRID values
- [X] T006 [P] Create SearchResult dataclass in src/sae_scope/backend/retriever/base.py with index, label, score, metadata fields
- [X] T007 Create abstract Retriever class in src/sae_scope/backend/retriever/base.py with ensure_indexed() and search() methods

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Select Search Mode (Priority: P1) MVP

**Goal**: Users can choose their preferred search method from a dropdown in the Features tab

**Independent Test**: Load a dataset, open Features tab, verify dropdown shows three modes, select each mode and verify selection persists

### Implementation for User Story 1

- [X] T008 [US1] Add search mode dropdown to Features tab in src/sae_scope/frontend/app.py with choices ["Lexical", "Vector", "Hybrid"]
- [X] T009 [US1] Set default search mode to "Lexical" in the dropdown component
- [X] T010 [US1] Store selected search mode in session state in src/sae_scope/frontend/app.py

**Checkpoint**: User Story 1 complete - mode selection UI is functional

---

## Phase 4: User Story 2 - Search with Selected Mode (Priority: P2)

**Goal**: Users can search for feature labels using their selected search mode and get ranked results

**Independent Test**: Select each search mode, enter the same query, verify results are returned for all modes

### Implementation for User Story 2

- [X] T011 [P] [US2] Create WeaviateRetriever class in src/sae_scope/backend/retriever/weaviate.py with client connection
- [X] T012 [US2] Implement collection name derivation from dataset filename in WeaviateRetriever
- [X] T013 [US2] Implement ensure_indexed() method: check if collection exists, create and populate if not
- [X] T014 [US2] Implement search() method with BM25 query for LEXICAL mode
- [X] T015 [US2] Implement search() method with near_text query for VECTOR mode
- [X] T016 [US2] Implement search() method with hybrid query (alpha=0.5) for HYBRID mode
- [X] T017 [US2] Add Weaviate connection check with fail-first error handling (raise on unavailable)
- [X] T018 [US2] Wire WeaviateRetriever into dataset loading flow in src/sae_scope/frontend/app.py
- [X] T019 [US2] Connect search input to retriever.search() with selected mode in src/sae_scope/frontend/app.py
- [X] T020 [US2] Display search results in dataframe format (Index, Label columns)

**Checkpoint**: User Story 2 complete - all three search modes return results

---

## Phase 5: User Story 3 - Consistent Search Interface (Priority: P3)

**Goal**: Search experience feels consistent regardless of which mode is selected

**Independent Test**: Switch between all three modes, verify search input, result format, and interaction remain identical

### Implementation for User Story 3

- [X] T021 [US3] Ensure all modes return results in same dataframe format in src/sae_scope/frontend/app.py
- [X] T022 [US3] Apply consistent result limit (k=10 default, configurable via UI) across all search modes
- [X] T023 [US3] Handle empty query case consistently (show first k features) for all modes

**Checkpoint**: User Story 3 complete - consistent UI across all modes

---

## Phase 6: User Story 4 - SAE Retrieval Tab: Two-Phase Text Search (Priority: P4)

**Goal**: Users can search for texts using a two-phase workflow: find latents by query, select which latents to use, then find matching texts based on selected latent activations.

**Independent Test**: Load a dataset, open SAE Retrieval tab, enter a query, click "Find Latents", verify results with checkboxes appear, select/deselect some latents, click "Find Texts", verify text results appear.

### Backend Implementation for User Story 4

- [X] T027 [P] [US4] Create TextSearchResult dataclass in src/sae_scope/backend/retriever/base.py with doc_index, text, score, metadata fields
- [X] T028 [US4] Export TextSearchResult from src/sae_scope/backend/retriever/__init__.py
- [X] T029 [P] [US4] Create InterpEmbedRetriever class in src/sae_scope/backend/retriever/interp_embed.py with __init__(feature_retriever, dataset) accepting Retriever and InterpEmbedDataset
- [X] T030 [US4] Implement search_latents(query, mode, k) method that delegates to composed Retriever.search()
- [X] T031 [US4] Implement _rerank_features(features, query) stub method that returns input unchanged
- [X] T032 [US4] Implement _score_documents(feature_indices, weights, k) method using dataset latents matrix
- [X] T033 [US4] Implement search_texts(selected_features, temperature, k) method with softmax weighting
- [X] T034 [US4] Export InterpEmbedRetriever from src/sae_scope/backend/retriever/__init__.py

### Frontend Implementation for User Story 4

- [X] T035 [US4] Add "SAE Retrieval" tab to src/sae_scope/frontend/app.py after existing tabs
- [X] T036 [US4] Add Phase 1 UI components: Search Mode dropdown (default Hybrid), Candidate Count input (default 10), Query textbox, "Find Latents" button
- [X] T037 [US4] Add Phase 1 results dataframe with checkbox column: Select, Index, Label, Score
- [X] T038 [US4] Add gr.State for storing selected latents as list of (index, score) tuples
- [X] T039 [US4] Add Phase 2 UI components: Temperature input (default 1.0, range 0.1-10.0), Max Results input (default 10), "Find Texts" button
- [X] T040 [US4] Add Phase 2 results dataframe with columns: Index, Text, Score
- [X] T041 [US4] Initialize InterpEmbedRetriever in on_dataset_select with WeaviateRetriever and loaded dataset
- [X] T042 [US4] Wire "Find Latents" button to call retriever.search_latents() and populate Phase 1 results with all checkboxes selected
- [X] T043 [US4] Wire checkbox changes to update selected latents state
- [X] T044 [US4] Wire "Find Texts" button to call retriever.search_texts() with selected latents from state
- [X] T045 [US4] Disable "Find Texts" button until latents are retrieved and at least one is selected
- [X] T046 [US4] Show error message when no latents are selected and user clicks "Find Texts"

### Validation for User Story 4

- [X] T047 [US4] Run quickstart.md Scenario 5: Two-Phase Workflow - Complete Flow
- [X] T048 [US4] Run quickstart.md Scenario 6: Latent Selection Refinement
- [X] T049 [US4] Run quickstart.md Scenario 7: No Latents Selected

**Checkpoint**: User Story 4 complete - two-phase text search workflow is functional

---

## Phase 7: Polish and Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, final validation

- [X] T024 Add informative error message when Weaviate is unavailable in src/sae_scope/frontend/app.py
- [X] T025 Handle empty search results with appropriate messaging
- [X] T026 Run quickstart.md validation scenarios (all 4 scenarios for US1-3)

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 2 requires User Story 1 (needs mode selection to exist)
  - User Story 3 requires User Story 2 (needs search to work first)
  - User Story 4: Independent of US1-3 (uses existing Retriever infrastructure)
- **Polish (Phase 7)**: Depends on all user stories being complete

### Within Each User Story

- Models/abstractions before concrete implementations
- Backend before frontend integration
- Core implementation before polish

### Parallel Opportunities

- T005, T006 can run in parallel (different components in same file, but independent)
- T011 can run in parallel with US1 tasks (different files)
- T027, T029 can run in parallel (different files: base.py, interp_embed.py)

---

## Parallel Example: Foundational Phase

```bash
# Launch independent tasks together:
Task: "Create SearchMode enum in src/sae_scope/backend/retriever/base.py"
Task: "Create SearchResult dataclass in src/sae_scope/backend/retriever/base.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2) - COMPLETE

1. Complete Phase 1: Setup (Docker Compose, dependency) - DONE
2. Complete Phase 2: Foundational (abstract Retriever) - DONE
3. Complete Phase 3: User Story 1 (mode selection dropdown) - DONE
4. Complete Phase 4: User Story 2 (search functionality) - DONE
5. Complete Phase 5: User Story 3 (consistent UI) - DONE

### Next: User Story 4 (SAE Retrieval Tab)

1. Complete backend tasks T027-T034 (InterpEmbedRetriever)
2. Complete frontend tasks T035-T046 (SAE Retrieval tab UI)
3. **STOP and VALIDATE**: Run quickstart scenarios 5-7
4. Polish - Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Weaviate must be running for User Story 2+ (fail-first, no fallbacks)
- Collection creation happens lazily on first dataset load per dataset
- Commit after each task or logical group
