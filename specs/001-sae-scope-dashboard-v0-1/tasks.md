# Tasks: SAE Scope Dashboard v0.1

**Input**: Design documents from `/specs/001-sae-scope-dashboard-v0-1/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/frontend-backend.md, research.md, quickstart.md

**Tests**: Not explicitly requested in spec - omitting test tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/sae_scope/` with `backend/` and `frontend/` subpackages
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and package structure

- [X] T001 Create project directory structure per plan.md in src/sae_scope/
- [X] T002 Add dependencies (gradio, plotly, pandas) using `uv add gradio plotly pandas`
- [X] T003 [P] Create src/sae_scope/__init__.py with package metadata
- [X] T004 [P] Create src/sae_scope/backend/__init__.py
- [X] T005 [P] Create src/sae_scope/frontend/__init__.py
- [X] T006 [P] Create src/sae_scope/frontend/components/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend classes that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Implement SAEFeatures dataclass with labels field in src/sae_scope/backend/features.py
- [X] T008 Implement SAEFeatures.__len__() method in src/sae_scope/backend/features.py
- [X] T009 Implement SAEFeatures.get_formatted_label() method in src/sae_scope/backend/features.py
- [X] T010 Implement SAEFeatures.get_all_formatted_labels() method in src/sae_scope/backend/features.py
- [X] T011 Implement SAEFeatures.parse_formatted_label() method in src/sae_scope/backend/features.py
- [X] T012 Implement SAELensDataset abstract base class with features property in src/sae_scope/backend/dataset.py
- [X] T013 Implement SAELensDataset.__len__() abstract method in src/sae_scope/backend/dataset.py
- [X] T014 Implement SAELensDataset.get_default_feature_indices() method in src/sae_scope/backend/dataset.py

**Checkpoint**: Backend abstractions ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Load Dataset and View Scatterplot (Priority: P1)

**Goal**: User can load a dataset file and see a scatterplot visualization with default feature axes

**Independent Test**: Load a sample dataset file and verify scatterplot renders with data points positioned by first two features

### Implementation for User Story 1

- [X] T015 [US1] Implement SAELensDataset.get_scatter_dataframe() abstract method signature in src/sae_scope/backend/dataset.py
- [X] T016 [US1] Create Gradio app skeleton with gr.Blocks in src/sae_scope/frontend/app.py
- [X] T017 [US1] Add gr.File component for dataset loading in src/sae_scope/frontend/app.py
- [X] T018 [US1] Add gr.State for current_dataset storage in src/sae_scope/frontend/app.py
- [X] T019 [US1] Add gr.Tabs with "Scatterplot" and "Data" tabs in src/sae_scope/frontend/components/tabs.py
- [X] T020 [US1] Add gr.Plot component inside Scatterplot tab in src/sae_scope/frontend/components/tabs.py
- [X] T021 [US1] Implement create_scatterplot() function using plotly.express.scatter in src/sae_scope/frontend/components/tabs.py
- [X] T022 [US1] Wire file upload to dataset loading and scatterplot rendering in src/sae_scope/frontend/app.py
- [X] T023 [US1] Add error handling for invalid file format with gr.Error in src/sae_scope/frontend/app.py

**Checkpoint**: User Story 1 complete - can load data and see scatterplot with default features

---

## Phase 4: User Story 2 - Select Features for Visualization (Priority: P2)

**Goal**: User can select two features from sidebar to change scatterplot axes

**Independent Test**: Load data, select different features from sidebar checkboxes, verify scatterplot updates with new axes

### Implementation for User Story 2

- [X] T024 [US2] Add gr.Sidebar with position="left" in src/sae_scope/frontend/components/sidebar.py
- [X] T025 [US2] Add gr.CheckboxGroup for feature selection inside sidebar in src/sae_scope/frontend/components/sidebar.py
- [X] T026 [US2] Add gr.State for selected_features tuple in src/sae_scope/frontend/app.py
- [X] T027 [US2] Implement populate_feature_list() to call features.get_all_formatted_labels() in src/sae_scope/frontend/components/sidebar.py
- [X] T028 [US2] Implement enforce_two_selections() for checkbox validation in src/sae_scope/frontend/components/sidebar.py
- [X] T029 [US2] Wire feature selection change to scatterplot update in src/sae_scope/frontend/app.py
- [X] T030 [US2] Add axis labels to scatterplot showing selected feature names in src/sae_scope/frontend/components/tabs.py

**Checkpoint**: User Story 2 complete - can change feature axes via sidebar

---

## Phase 5: User Story 3 - Inspect Individual Text (Priority: P3)

**Goal**: User can hover over data points to see original text content

**Independent Test**: Load data, hover over any scatterplot point, verify text content appears in tooltip

### Implementation for User Story 3

- [X] T031 [US3] Update create_scatterplot() to include hover_data=["text"] in src/sae_scope/frontend/components/tabs.py
- [X] T032 [US3] Configure Plotly hover template to display full text in src/sae_scope/frontend/components/tabs.py

**Checkpoint**: User Story 3 complete - hovering shows text content via Plotly native feature

---

## Phase 6: User Story 4 - Toggle Feature Panel (Priority: P4)

**Goal**: User can hide/show the sidebar to maximize plot viewing area

**Independent Test**: Click sidebar toggle, verify panel hides and plot expands; click again, verify panel reappears

### Implementation for User Story 4

- [X] T033 [US4] Verify gr.Sidebar toggle functionality works (native Gradio feature) in src/sae_scope/frontend/components/sidebar.py

**Checkpoint**: User Story 4 complete - sidebar toggle works (mostly native Gradio behavior)

---

## Phase 7: User Story 5 - Search and Filter Features (Priority: P5)

**Goal**: User can search features by label to filter the feature list

**Independent Test**: Type search query, verify feature list filters to matching labels; clear search, verify all features shown

### Implementation for User Story 5

- [X] T034 [US5] Implement SAEFeatures.search() method in src/sae_scope/backend/features.py
- [X] T035 [US5] Add gr.Textbox for search input in sidebar in src/sae_scope/frontend/components/sidebar.py
- [X] T036 [US5] Implement filter_features() to update checkbox choices based on search in src/sae_scope/frontend/components/sidebar.py
- [X] T037 [US5] Wire search input change to feature list filtering in src/sae_scope/frontend/app.py

**Checkpoint**: User Story 5 complete - feature search/filter works

---

## Phase 8: Data Tab Implementation

**Goal**: User can view full text dataset in Data tab

**Independent Test**: Load data, switch to Data tab, verify dataframe displays all texts

### Implementation

- [X] T038 Implement SAELensDataset.get_text_dataframe() abstract method signature in src/sae_scope/backend/dataset.py
- [X] T039 Add gr.Dataframe component inside Data tab in src/sae_scope/frontend/components/tabs.py
- [X] T040 Wire tab change to populate dataframe from dataset.get_text_dataframe() in src/sae_scope/frontend/app.py

**Checkpoint**: Data tab functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final integration and cleanup

- [X] T041 [P] Add __main__.py entry point for `python -m sae_scope.frontend.app` in src/sae_scope/frontend/__main__.py
- [X] T042 [P] Add type annotations to all frontend functions per Constitution requirements
- [X] T043 Verify all error paths raise exceptions (no silent failures) per Fail-First principle
- [X] T044 Run quickstart.md validation steps manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1): No dependencies on other stories
  - US2 (P2): Depends on US1 (needs scatterplot to update)
  - US3 (P3): Depends on US1 (needs scatterplot to hover on)
  - US4 (P4): Depends on US2 (needs sidebar to toggle)
  - US5 (P5): Depends on US2 (needs sidebar feature list)
- **Data Tab (Phase 8)**: Can run parallel to US3-US5 after US1 complete
- **Polish (Phase 9)**: Depends on all user stories being complete

### Within Each User Story

- Backend methods before frontend components
- Components before wiring/integration
- Core implementation before error handling

### Parallel Opportunities

- Setup tasks T003-T006 can run in parallel
- Within Phase 2, tasks depend on each other (SAEFeatures before SAELensDataset)
- US3 and US4 can run in parallel after US2
- Polish tasks T041-T042 can run in parallel

---

## Parallel Example: Setup Phase

```bash
# After T001-T002, launch these in parallel:
Task: "Create src/sae_scope/__init__.py"
Task: "Create src/sae_scope/backend/__init__.py"
Task: "Create src/sae_scope/frontend/__init__.py"
Task: "Create src/sae_scope/frontend/components/__init__.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Load sample data, verify scatterplot renders
5. Demo MVP if ready

### Incremental Delivery

1. Complete Setup + Foundational (foundation ready)
2. Add User Story 1 (MVP - basic visualization)
3. Add User Story 2 (feature selection)
4. Add User Story 3 (text hover inspection)
5. Add User Story 4 (sidebar toggle)
6. Add User Story 5 (feature search)
7. Add Data Tab (parallel enhancement)
8. Polish and validate

---

## Phase 10: Adaptation - Dataset Dropdown and InterpEmbed Integration

**Purpose**: Adapt dashboard to use dropdown selection from /data folder and implement concrete dataset class

**Prerequisites**: All previous phases complete (T001-T044)

### Change 1: InterpEmbedDataset Implementation

- [X] T045 Create src/sae_scope/backend/interp_dataset.py with InterpEmbedDataset class skeleton
- [X] T046 Implement InterpEmbedDataset.__init__() wrapping interp_embed.Dataset in src/sae_scope/backend/interp_dataset.py
- [X] T047 Implement InterpEmbedDataset.features property using feature_labels() in src/sae_scope/backend/interp_dataset.py
- [X] T048 Implement InterpEmbedDataset.__len__() using len(dataset) in src/sae_scope/backend/interp_dataset.py
- [X] T049 Implement InterpEmbedDataset.get_scatter_dataframe() using latents() in src/sae_scope/backend/interp_dataset.py
- [X] T050 Implement InterpEmbedDataset.get_text_dataframe() using pandas() in src/sae_scope/backend/interp_dataset.py
- [X] T051 Implement InterpEmbedDataset.load() classmethod using Dataset.load_from_file() in src/sae_scope/backend/interp_dataset.py
- [X] T052 Export InterpEmbedDataset from src/sae_scope/backend/__init__.py

### Change 2: Dataset Selection Dropdown

- [X] T053 Add list_data_files() function to list .pkl files from /data in src/sae_scope/frontend/app.py
- [X] T054 Replace gr.File with gr.Dropdown populated by list_data_files() in src/sae_scope/frontend/app.py
- [X] T055 Update on_dataset_select() handler to load via InterpEmbedDataset.load() in src/sae_scope/frontend/app.py
- [X] T056 Wire dropdown change event to dataset loading and UI update in src/sae_scope/frontend/app.py

### Infrastructure

- [X] T057 [P] Create /data directory at repository root
- [X] T058 [P] Update .gitignore to include /data/*.pkl pattern
- [X] T059 Update README.md to document dataset location and selection

**Checkpoint**: Dashboard loads datasets from /data dropdown using interp_embed

---

## Dependencies for Phase 10

- T045-T052: InterpEmbedDataset implementation (sequential within backend)
- T053-T056: Frontend dropdown changes (depends on T051 being complete for loading)
- T057-T058: Infrastructure (can run in parallel with other tasks)
- T059: Documentation (depends on all other tasks)

---

## Phase 11: Performance UI Refactor

**Purpose**: Fix slow UI caused by rendering thousands of features in checkbox multiselect

**Problem**: The gr.Sidebar with gr.CheckboxGroup renders all features upfront, causing performance issues with datasets containing thousands of features.

**Solution**:
1. Delete sidebar entirely
2. Add single text input for comma-separated feature indices (e.g., "0, 1") in Scatterplot tab
3. Add new Features tab with searchable feature list (lazy rendering)

### Step 1: Delete Sidebar

- [X] T060 Remove sidebar imports from src/sae_scope/frontend/app.py
- [X] T061 Remove sidebar component creation from create_app() in src/sae_scope/frontend/app.py
- [X] T062 Remove sidebar-related event handlers (on_feature_selection_change, on_search_change) from src/sae_scope/frontend/app.py
- [X] T063 Remove checkbox_group and search_input wiring from src/sae_scope/frontend/app.py
- [X] T064 Delete src/sae_scope/frontend/components/sidebar.py

### Step 2: Add Feature Indices Input to Scatterplot Tab

- [X] T065 Modify create_tabs() to add gr.Textbox for feature indices (placeholder: "0, 1") in Scatterplot tab in src/sae_scope/frontend/components/tabs.py
- [X] T066 Update create_tabs() return signature to include feature_indices_input component in src/sae_scope/frontend/components/tabs.py
- [X] T067 Add parse_feature_indices() function to parse comma-separated indices string in src/sae_scope/frontend/app.py
- [X] T068 Add on_feature_indices_change() handler to validate and update scatterplot in src/sae_scope/frontend/app.py
- [X] T069 Wire feature_indices_input.change event to on_feature_indices_change() in src/sae_scope/frontend/app.py
- [X] T070 Update on_dataset_select() to set default value "0, 1" for feature indices input in src/sae_scope/frontend/app.py
- [X] T071 Add validation in parse_feature_indices() with gr.Error for invalid format or out-of-range indices in src/sae_scope/frontend/app.py

### Step 3: Create Features Tab

- [X] T072 [P] Create src/sae_scope/frontend/components/features_tab.py with create_features_tab() function
- [X] T073 Add gr.Textbox for search input in features_tab.py
- [X] T074 Add gr.Dataframe for search results (columns: Index, Label) in features_tab.py
- [X] T075 Implement search_features() function to filter and return top 100 matches in features_tab.py
- [X] T076 Import and add Features tab between Scatterplot and Data tabs in src/sae_scope/frontend/components/tabs.py
- [X] T077 Wire search input change to search_features() in src/sae_scope/frontend/app.py

### Step 4: Cleanup and Validation

- [X] T078 Update components/__init__.py to remove sidebar exports and add features_tab exports
- [X] T079 Remove previous_selection state variable (no longer needed) from src/sae_scope/frontend/app.py
- [X] T080 Verify app launches without errors by running `uv run python -m sae_scope.frontend`

**Checkpoint**: Dashboard uses comma-separated indices input for feature selection with Features tab for discovery

---

## Dependencies for Phase 11

- **Step 1** (T060-T064): Remove sidebar - must complete before other steps to avoid broken imports
- **Step 2** (T065-T071): Add indices input - depends on Step 1 completion
- **Step 3** (T072-T077): Add Features tab - T072-T075 can run in parallel with Step 2, T076-T077 depend on Step 2
- **Step 4** (T078-T081): Cleanup - depends on all previous steps

### Parallel Opportunities

```bash
# After T064 (sidebar deleted), launch in parallel:
Task: "T065-T071 - Add feature indices textbox input"
Task: "T072-T075 - Create features_tab.py component"
```

---

## Phase 12: Feature Indices Input Refactor

**Purpose**: Replace comma-separated textbox with two number inputs and an update button

**Problem**: Current implementation uses a single textbox requiring comma-separated input. User wants explicit number fields and manual update control.

**Solution**:
1. Replace gr.Textbox with two gr.Number inputs for X and Y feature indices
2. Add gr.Button to trigger scatterplot update on click
3. Remove automatic on-change update behavior

### Implementation

- [X] T081 Replace feature_indices_input gr.Textbox with x_feature_idx gr.Number in src/sae_scope/frontend/app.py
- [X] T082 Add y_feature_idx gr.Number input next to x_feature_idx in src/sae_scope/frontend/app.py
- [X] T083 Add update_plot_btn gr.Button with label "Update Plot" in src/sae_scope/frontend/app.py
- [X] T084 Remove parse_feature_indices() function (no longer needed) from src/sae_scope/frontend/app.py
- [X] T085 Rename on_feature_indices_change() to on_update_plot_click() in src/sae_scope/frontend/app.py
- [X] T086 Update on_update_plot_click() to accept x_idx and y_idx as separate int parameters in src/sae_scope/frontend/app.py
- [X] T087 Wire update_plot_btn.click event to on_update_plot_click() with x and y inputs in src/sae_scope/frontend/app.py
- [X] T088 Remove feature_indices_input.change event wiring in src/sae_scope/frontend/app.py
- [X] T089 Update on_dataset_select() to return separate x and y values instead of combined string in src/sae_scope/frontend/app.py
- [X] T090 Verify app launches and update button works by running `uv run python -m sae_scope.frontend`

**Checkpoint**: Dashboard uses two number inputs with manual update button for feature selection

---

## Dependencies for Phase 12

- All tasks are sequential within app.py
- T081-T083: UI component changes
- T084-T088: Handler and wiring changes
- T089: Output signature update
- T090: Validation

---

## Phase 13: Feature Statistics in Features Tab

**Purpose**: Add dataset feature statistics visualization to Features tab

**Features**:
1. Summary statistics via pandas describe() for frequency, std, max columns
2. Top N features (user-configurable, default 10) ranked by each metric
3. Accordion layout separating statistics from search

### Step 1: Backend - Add Statistics Computation

- [X] T091 Add abstract method compute_feature_statistics() to SAELensDataset in src/sae_scope/backend/dataset.py
- [X] T092 Implement compute_feature_statistics() in InterpEmbedDataset in src/sae_scope/backend/interp_dataset.py
- [X] T093 Add _feature_stats cache attribute to InterpEmbedDataset.__init__() in src/sae_scope/backend/interp_dataset.py
- [X] T094 Call compute_feature_statistics() during dataset initialization to populate cache in src/sae_scope/backend/interp_dataset.py

### Step 2: Frontend - Add Statistics UI Components

- [X] T095 Add gr.Accordion for "Feature Statistics" (open=True) wrapping statistics content in Features tab in src/sae_scope/frontend/app.py
- [X] T096 Add gr.Dataframe for summary_stats_df showing describe() output in src/sae_scope/frontend/app.py
- [X] T097 Add gr.Number for top_n_input (default=10, min=1, max=100) in src/sae_scope/frontend/app.py
- [X] T098 Add gr.Dataframe for top_by_frequency showing top N features by frequency in src/sae_scope/frontend/app.py
- [X] T099 Add gr.Dataframe for top_by_std showing top N features by std dev in src/sae_scope/frontend/app.py
- [X] T100 Add gr.Dataframe for top_by_max showing top N features by max value in src/sae_scope/frontend/app.py
- [X] T101 Add gr.Accordion for "Search Features" (open=False) wrapping existing search content in src/sae_scope/frontend/app.py

### Step 3: Frontend - Wire Statistics Handlers

- [X] T102 Add get_top_n_features() helper function to slice cached stats by metric in src/sae_scope/frontend/app.py
- [X] T103 Add get_summary_stats() helper function to call describe() on stats columns in src/sae_scope/frontend/app.py
- [X] T104 Update on_dataset_select() to return statistics dataframes in src/sae_scope/frontend/app.py
- [X] T105 Add on_top_n_change() handler to update top N dataframes when input changes in src/sae_scope/frontend/app.py
- [X] T106 Wire top_n_input.change to on_top_n_change() in src/sae_scope/frontend/app.py
- [X] T107 Update dataset_dropdown.change outputs to include all statistics dataframes in src/sae_scope/frontend/app.py

### Step 4: Validation

- [X] T108 Verify app imports without errors by running python -c "from sae_scope.frontend.app import create_app"
- [X] T109 Verify statistics display correctly when loading a dataset

**Checkpoint**: Features tab shows summary statistics and top N features by frequency/std/max with configurable N

---

## Dependencies for Phase 13

- **Step 1** (T091-T094): Backend changes - can run in parallel with nothing, no dependencies
- **Step 2** (T095-T101): UI components - depends on Step 1 completion
- **Step 3** (T102-T107): Wiring - depends on Step 2 completion
- **Step 4** (T108-T109): Validation - depends on all previous steps

---

## Phase 14: Latent Aggregation Method Dropdown

**Purpose**: Add dropdown to select latent aggregation method for dataset processing

**Problem**: Currently, the dataset uses hardcoded "max" aggregation when calling `interp_embed.Dataset.latents()`. Users need flexibility to switch between different aggregation methods.

**Solution**:
1. Add `aggregation_method` parameter to `InterpEmbedDataset.load()`
2. Add `gr.Dropdown` below dataset selection with options: "max" (default), "mean", "binarize", "count"
3. When aggregation changes, reload the dataset with new method (reuses existing on_dataset_select flow)

### Step 1: Backend - Add Aggregation Method Parameter

- [X] T110 Add `aggregation_method` parameter to InterpEmbedDataset.__init__() (default "max") and use it when calling latents() in src/sae_scope/backend/interp_dataset.py
- [X] T111 Add `aggregation_method` parameter to InterpEmbedDataset.load() classmethod and pass to __init__() in src/sae_scope/backend/interp_dataset.py

### Step 2: Frontend - Add Aggregation Dropdown UI

- [X] T112 Add gr.Dropdown for aggregation_method below dataset_dropdown with choices ["max", "mean", "binarize", "count"] and default "max" in src/sae_scope/frontend/app.py
- [X] T113 Update on_dataset_select() to accept aggregation_method parameter and pass to InterpEmbedDataset.load() in src/sae_scope/frontend/app.py
- [X] T114 Wire aggregation_dropdown.change to trigger on_dataset_select() with current dataset and new aggregation method in src/sae_scope/frontend/app.py

### Step 3: Validation

- [X] T115 Verify app imports without errors by running python -c "from sae_scope.frontend.app import create_app"
- [X] T116 Verify aggregation dropdown reloads dataset and updates all visualizations

**Checkpoint**: Dashboard has aggregation method dropdown that reloads dataset with new aggregation method

---

## Dependencies for Phase 14

- **Step 1** (T110-T111): Backend changes - no dependencies
- **Step 2** (T112-T114): Frontend UI and wiring - depends on Step 1 completion
- **Step 3** (T115-T116): Validation - depends on all previous steps

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- InterpEmbedDataset wraps interp_embed.Dataset (already a project dependency)
- Text inspection uses Plotly native hover - no click handlers needed
- Phase 11 removes sidebar toggle (US4) - no longer applicable after refactor
- Feature search (US5) moves to Features tab with gr.Dataframe display
- Phase 12 replaces comma-separated textbox with explicit number inputs and button
- Phase 13 adds feature statistics with describe() summary and top N tables
- Phase 14 adds latent aggregation method dropdown - reloads dataset on change (simple approach)
- Commit after each phase or logical task group
