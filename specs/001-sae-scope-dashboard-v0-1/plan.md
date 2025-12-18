# Implementation Plan: SAE Scope Dashboard v0.1 - Performance UI Refactor

**Branch**: `001-sae-scope-dashboard-v0-1` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-sae-scope-dashboard-v0-1/spec.md`

## Summary

Refactor the Gradio dashboard UI to address performance issues caused by rendering thousands of features in a multiselect checkbox group. Replace the sidebar-based feature selection with:
1. Two integer input fields for direct feature index entry in the Scatterplot tab
2. A separate Features tab with searchable feature list for discovery

## Technical Context

**Language/Version**: Python 3.10
**Primary Dependencies**: Gradio 5.x, Plotly Express, Pandas, interp-embed
**Storage**: Local .pkl files in /data directory
**Testing**: pytest
**Target Platform**: Local desktop (browser-based Gradio app)
**Project Type**: Single Python package
**Performance Goals**: Instant UI response (no lag from feature list rendering)
**Constraints**: Must handle datasets with several thousand features without UI slowdown
**Scale/Scope**: Single-user local dashboard, datasets with thousands of SAE features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| SOLID - Single Responsibility | PASS | Each component handles one concern (tabs.py for tabs, feature input for selection) |
| SOLID - Open/Closed | PASS | Extending with new tab, not modifying existing tab logic |
| SOLID - Liskov Substitution | N/A | No inheritance involved |
| SOLID - Interface Segregation | PASS | Simple component interfaces |
| SOLID - Dependency Inversion | PASS | Components depend on dataset abstraction |
| DRY | PASS | Shared scatterplot creation logic remains centralized |
| Fail-First | PASS | Invalid feature indices will raise errors immediately |
| Type Safety | PASS | Type hints throughout |
| Small Focused Commits | PASS | Will split into: remove sidebar, add feature inputs, add features tab |

## Project Structure

### Documentation (this feature)

```text
specs/001-sae-scope-dashboard-v0-1/
  plan.md              # This file
  research.md          # Phase 0 output
  data-model.md        # Phase 1 output
  quickstart.md        # Phase 1 output
  contracts/           # Phase 1 output
  tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
  sae_scope/
    __init__.py
    backend/
      __init__.py
      dataset.py
      features.py
      interp_dataset.py
    frontend/
      __init__.py
      __main__.py
      app.py                    # Main app orchestration (MODIFY)
      components/
        __init__.py
        sidebar.py              # DELETE - no longer needed
        tabs.py                 # MODIFY - add feature inputs to scatterplot tab
        features_tab.py         # NEW - searchable feature list tab

tests/
  contract/
  integration/
  unit/
```

**Structure Decision**: Single project structure. Frontend components split by concern. Sidebar component will be deleted as it's no longer needed.

## Design Overview

### Current Architecture (Problem)

```
app.py
  Sidebar (checkbox multiselect with ALL features)  <-- SLOW: renders thousands of checkboxes
    search_input
    checkbox_group
  Main Column
    Tabs
      Scatterplot tab
      Data tab
```

### New Architecture (Solution)

```
app.py
  Main Column
    Tabs
      Scatterplot tab
        Feature Indices (textbox: "0, 1")  <-- FAST: single text input
        Plot
      Features tab                         <-- LAZY: only renders search results
        Search input
        Results list (limited display)
      Data tab
```

### Key Changes

1. **Delete sidebar.py**: Remove the sidebar component entirely
2. **Modify tabs.py**: Add single `gr.Textbox` for comma-separated feature indices in the Scatterplot tab
3. **New features_tab.py**: Create a Features tab with search functionality that only displays matching results (lazy rendering)
4. **Modify app.py**: Wire up new components, remove sidebar dependencies

### Component Behavior

**Scatterplot Tab - Feature Indices Input**:
- Single `gr.Textbox` for comma-separated feature indices (e.g., "0, 1")
- Default to "0, 1" when dataset loads
- Parse input to extract two integer indices
- Validate indices are within range (0 to num_features-1)
- Update scatterplot on change

**Features Tab - Searchable List**:
- Text input for search query
- Results displayed as a list/dataframe showing: index, label
- Limited to top N matches (e.g., 50) to avoid rendering issues
- Click on result could copy index to clipboard or show details

## Complexity Tracking

No constitution violations - this is a simplification, not an addition of complexity.
