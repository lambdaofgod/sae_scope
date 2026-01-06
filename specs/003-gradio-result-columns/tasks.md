# Tasks: Gradio Result Columns Configuration

**Input**: Design documents from `/specs/003-gradio-result-columns/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Backend Methods)

**Purpose**: Add backend methods for column access before any UI changes

- [x] T001 Add get_column_names() method to InterpEmbedDataset in src/sae_scope/backend/interp_dataset.py
- [x] T002 Add get_text_field() method to InterpEmbedDataset in src/sae_scope/backend/interp_dataset.py
- [x] T003 Add get_dataframe_with_columns() method to InterpEmbedDataset in src/sae_scope/backend/interp_dataset.py

---

## Phase 2: Foundational (Frontend Refactor)

**Purpose**: Extract tabs to separate modules - MUST complete before user story implementation

**Note**: This phase refactors existing functionality without changing behavior

- [x] T004 Create scatterplot_tab.py with create_scatterplot_ui() and wire_scatterplot_events() in src/sae_scope/frontend/components/scatterplot_tab.py
- [x] T005 [P] Create features_tab.py with create_features_ui() and wire_features_events() in src/sae_scope/frontend/components/features_tab.py
- [x] T006 [P] Create data_tab.py with create_data_ui() and wire_data_events() in src/sae_scope/frontend/components/data_tab.py
- [x] T007 [P] Create sae_retrieval_tab.py with create_sae_retrieval_ui() and wire_sae_retrieval_events() in src/sae_scope/frontend/components/sae_retrieval_tab.py
- [x] T008 Update components/__init__.py to export tab modules in src/sae_scope/frontend/components/__init__.py
- [x] T009 Refactor app.py to orchestrator pattern importing tab modules in src/sae_scope/frontend/app.py
- [x] T010 Verify app launches and all existing functionality works after refactor

**Checkpoint**: App runs with refactored tabs - behavior unchanged from before refactor

---

## Phase 3: User Story 1 - Configure Display Columns After Dataset Load (Priority: P1)

**Goal**: After loading a dataset, user sees column selector populated with available columns

**Independent Test**: Load any dataset, verify column selector appears with correct columns from DataFrame (excluding text column)

### Implementation for User Story 1

- [x] T011 [US1] Add column_selector CheckboxGroup component (hidden by default) in src/sae_scope/frontend/app.py
- [x] T012 [US1] Update on_dataset_select to call get_column_names() and populate column_selector in src/sae_scope/frontend/app.py
- [x] T013 [US1] Add selected_columns to Gradio State in src/sae_scope/frontend/app.py
- [x] T014 [US1] Wire column_selector change event to update selected_columns state in src/sae_scope/frontend/app.py
- [x] T015 [US1] Handle edge case: dataset with only text column (empty/disabled selector) in src/sae_scope/frontend/app.py

**Checkpoint**: Column selector appears after dataset load, selection updates state

---

## Phase 4: User Story 2 - View Additional Columns in Search Results (Priority: P1)

**Goal**: Search results display selected columns alongside text column

**Independent Test**: Select columns, perform search, verify results table shows text + selected columns

### Implementation for User Story 2

- [x] T016 [US2] Update TextSearchResult to include column data from dataset in src/sae_scope/backend/retriever/base.py
- [x] T017 [US2] Modify InterpEmbedRetriever._score_documents() to fetch additional column values in src/sae_scope/backend/retriever/interp_embed.py
- [x] T018 [US2] Update on_find_texts to pass selected_columns and format results with additional columns in src/sae_scope/frontend/components/sae_retrieval_tab.py
- [x] T019 [US2] Update text_results Dataframe headers dynamically based on selected columns in src/sae_scope/frontend/components/sae_retrieval_tab.py
- [x] T020 [US2] Handle null/empty column values with placeholder display in src/sae_scope/frontend/components/sae_retrieval_tab.py

**Checkpoint**: Search results show text + all selected additional columns

---

## Phase 5: User Story 3 - Display Selected Columns Before Text Column (Priority: P2)

**Goal**: Selected columns appear BEFORE the text column in all result displays

### Implementation for User Story 3

- [x] T021 [US3] Change column ordering in frontend callers to pass selected_columns before text_field (swap order in app.py, data_tab.py, sae_retrieval_tab.py)

---

## Phase 6: User Story 4 - Reusable Search Component (Priority: P2)

**Goal**: Extract reusable search UI component that works for both feature search and text search

**Independent Test**: Verify search UI appears identically in both Features and Data tabs with same controls

### Implementation for User Story 4

- [x] T022 [US4] Create search_component.py with create_search_ui() factory function in src/sae_scope/frontend/components/search_component.py
- [x] T023 [US4] Update components/__init__.py to export create_search_ui in src/sae_scope/frontend/components/__init__.py

**Checkpoint**: Reusable search component available for use by tabs

---

## Phase 7: User Story 5 - Text Search in Data Tab (Priority: P2)

**Goal**: Data tab has text search functionality with results above a collapsed DataFrame accordion

**Independent Test**: Load dataset, search texts in Data tab, verify results appear above collapsed "All Data" accordion

### Implementation for User Story 5

- [x] T024 [US5] Add search_texts_by_query() method to InterpEmbedRetriever in src/sae_scope/backend/retriever/interp_embed.py
- [x] T025 [US5] Ensure text collection indexed in Weaviate (add ensure_texts_indexed() or similar) in src/sae_scope/backend/retriever/interp_embed.py
- [x] T026 [US5] Refactor data_tab.py to use create_search_ui() component in src/sae_scope/frontend/components/data_tab.py
- [x] T027 [US5] Add gr.Accordion wrapper for existing DataFrame in data_tab.py in src/sae_scope/frontend/components/data_tab.py
- [x] T028 [US5] Wire text search events in data_tab.py to call retriever.search_texts_by_query() in src/sae_scope/frontend/components/data_tab.py

**Checkpoint**: Data tab has text search above collapsed DataFrame accordion

---

## Phase 8: User Story 6 - Refactor Features Tab to Use Reusable Component (Priority: P3)

**Goal**: Features tab uses the same reusable search component for consistency

**Independent Test**: Verify Features tab search works exactly as before after refactor

### Implementation for User Story 6

- [x] T029 [US6] Refactor features_tab.py to use create_search_ui() instead of inline search UI in src/sae_scope/frontend/components/features_tab.py
- [x] T030 [US6] Verify feature search functionality unchanged after refactor

**Checkpoint**: Both tabs use consistent search component pattern

---

## Phase 9: Polish & Validation

**Purpose**: Final validation and cleanup

- [x] T031 Run quickstart.md validation - test all search scenarios
- [x] T032 Verify both tabs have identical search UI layout

---

## Phase 10: User Story 7 - HTMLTableElement for Search Results (Priority: P2)

**Goal**: Replace gr.Dataframe with custom HTML table for proper text wrapping in search results

**Independent Test**: Perform search, verify text columns wrap properly within specified max-width

### Implementation for User Story 7

- [x] T033 [US7] Create HTMLTableElement class with html() method in src/sae_scope/frontend/components/html_table.py
- [x] T034 [US7] Update components/__init__.py to export HTMLTableElement in src/sae_scope/frontend/components/__init__.py
- [x] T035 [US7] Replace gr.Dataframe with gr.HTML in search_component.py in src/sae_scope/frontend/components/search_component.py
- [x] T036 [US7] Update data_tab.py search handler to return HTMLTableElement.html() in src/sae_scope/frontend/components/data_tab.py
- [x] T037 [US7] Update features_tab.py search handler to return HTMLTableElement.html() in src/sae_scope/frontend/components/features_tab.py

**Checkpoint**: Search results display with proper text wrapping in HTML tables

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion
- **Phase 4 (US2)**: Depends on Phase 3 (needs column selection working)
- **Phase 5 (US3)**: Depends on Phase 4 completion
- **Phase 6 (US4)**: No dependencies on other stories - can run in parallel
- **Phase 7 (US5)**: Depends on Phase 6 (needs reusable search component)
- **Phase 8 (US6)**: Depends on Phase 6 (needs reusable search component)
- **Phase 9 (Polish)**: Depends on all user story phases
- **Phase 10 (US7)**: Depends on Phase 6, 7, 8 (needs search component and tabs using it)

### Within Each Phase

- T001-T003: Sequential (same file)
- T004-T007: Parallel (different files)
- T008-T009: Sequential (depend on T004-T007)
- T011-T015: Sequential within US1 (same file, incremental changes)
- T016-T020: Sequential within US2 (depends on T016 changes)
- T022-T023: Sequential within US4 (T023 depends on T022)
- T024-T028: Sequential within US5 (backend first, then frontend refactor)
- T029-T030: Sequential within US6 (refactor then verify)
- T033-T037: Sequential within US7 (create class, export, update components)

### Parallel Opportunities

```text
Phase 2 (after T004):
  T005 [P] features_tab.py
  T006 [P] data_tab.py
  T007 [P] sae_retrieval_tab.py

Phase 7 and Phase 8 (after Phase 6 complete):
  Phase 7 (US5 - Data tab text search) can run in parallel with
  Phase 8 (US6 - Features tab refactor)
```

---

## Implementation Strategy

### MVP First (Through User Story 1)

1. Complete Phase 1: Backend methods (T001-T003) - DONE
2. Complete Phase 2: Frontend refactor (T004-T010) - DONE
3. Complete Phase 3: Column selector UI (T011-T015) - DONE
4. **STOP and VALIDATE**: Column selector works, selection updates state - DONE

### Column Display Feature (Through User Story 3)

1. Complete MVP above - DONE
2. Complete Phase 4: Results display (T016-T020) - DONE
3. Complete Phase 5: Column ordering (T021) - DONE

### Data Tab Search Feature (New)

1. Complete Phase 6: Reusable search component (T022-T023)
2. Complete Phase 7: Data tab text search (T024-T028)
3. Complete Phase 8: Features tab refactor (T029-T030)
4. Complete Phase 9: Polish and validation (T031-T032)

### HTMLTableElement Feature (New)

1. Complete Phases 6-8 above (search component must be in use)
2. Complete Phase 10: HTMLTableElement for search results (T033-T037)

---

## Notes

- No test tasks included (not requested in spec)
- Phase 2 is a pure refactor - existing behavior must be preserved
- User Story 2 builds on User Story 1 (not parallelizable)
- Column selection affects SAE Retrieval tab results only (Data tab already shows full DataFrame)
- Phase 6-8 add text search to Data tab with reusable component pattern
- Features tab refactor (Phase 8) preserves existing functionality while using new component
- Phase 10 replaces gr.Dataframe with gr.HTML + HTMLTableElement for proper text wrapping
