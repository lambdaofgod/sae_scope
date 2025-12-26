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

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, final validation

- [X] T024 Add informative error message when Weaviate is unavailable in src/sae_scope/frontend/app.py
- [X] T025 Handle empty search results with appropriate messaging
- [X] T026 Run quickstart.md validation scenarios (all 4 scenarios)

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 2 requires User Story 1 (needs mode selection to exist)
  - User Story 3 requires User Story 2 (needs search to work first)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Within Each User Story

- Models/abstractions before concrete implementations
- Backend before frontend integration
- Core implementation before polish

### Parallel Opportunities

- T005, T006 can run in parallel (different components in same file, but independent)
- T011 can run in parallel with US1 tasks (different files)

---

## Parallel Example: Foundational Phase

```bash
# Launch independent tasks together:
Task: "Create SearchMode enum in src/sae_scope/backend/retriever/base.py"
Task: "Create SearchResult dataclass in src/sae_scope/backend/retriever/base.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup (Docker Compose, dependency)
2. Complete Phase 2: Foundational (abstract Retriever)
3. Complete Phase 3: User Story 1 (mode selection dropdown)
4. Complete Phase 4: User Story 2 (search functionality)
5. **STOP and VALIDATE**: Test all three search modes work
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational - Foundation ready
2. Add User Story 1 - Test mode selection - MVP UI ready
3. Add User Story 2 - Test search - Core feature complete
4. Add User Story 3 - Test consistency - Full feature complete
5. Polish - Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Weaviate must be running for User Story 2+ (fail-first, no fallbacks)
- Collection creation happens lazily on first dataset load per dataset
- Commit after each task or logical group
