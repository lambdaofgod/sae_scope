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

## Phase 5: Polish & Validation

**Purpose**: Final validation and edge case handling

- [ ] T021 Verify column selection persists across multiple searches in same session
- [ ] T022 Test with eu5_review_dataset.pkl (2 columns: text, section_header)
- [ ] T023 Test with roam_df20250217.pkl (8 columns: multiple additional columns)
- [ ] T024 Run quickstart.md validation scenario

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion
- **Phase 4 (US2)**: Depends on Phase 3 (needs column selection working)
- **Phase 5 (Polish)**: Depends on Phase 4 completion

### Within Each Phase

- T001-T003: Sequential (same file)
- T004-T007: Parallel (different files)
- T008-T009: Sequential (depend on T004-T007)
- T011-T015: Sequential within US1 (same file, incremental changes)
- T016-T020: Sequential within US2 (depends on T016 changes)

### Parallel Opportunities

```text
Phase 2 (after T004):
  T005 [P] features_tab.py
  T006 [P] data_tab.py
  T007 [P] sae_retrieval_tab.py
```

---

## Implementation Strategy

### MVP First (Through User Story 1)

1. Complete Phase 1: Backend methods (T001-T003)
2. Complete Phase 2: Frontend refactor (T004-T010)
3. Complete Phase 3: Column selector UI (T011-T015)
4. **STOP and VALIDATE**: Column selector works, selection updates state

### Full Feature

1. Complete MVP above
2. Complete Phase 4: Results display (T016-T020)
3. Complete Phase 5: Polish and validation (T021-T024)

---

## Notes

- No test tasks included (not requested in spec)
- Phase 2 is a pure refactor - existing behavior must be preserved
- User Story 2 builds on User Story 1 (not parallelizable)
- Column selection affects SAE Retrieval tab results only (Data tab already shows full DataFrame)
