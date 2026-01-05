# Feature Specification: Gradio Result Columns Configuration

**Feature Branch**: `003-gradio-result-columns`
**Created**: 2026-01-05
**Status**: Draft
**Input**: User description: "I want to refactor the frontend and change how the datasets are loaded. Now we only show retrieved text in search results - I want to be able to set other columns that will be showed in results at dataset loading. It should work like this: we select dataset like we do right now, we click 'load', and then there is a multiselect based on the columns to select what will be shown."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Display Columns After Dataset Load (Priority: P1)

A user loads a dataset and wants to configure which additional columns appear in search results alongside the text field. After clicking "Load", the system reveals the available columns from the dataset and allows the user to select which ones to display in search results.

**Why this priority**: Core functionality that enables the feature. Without this, users cannot configure result columns at all.

**Independent Test**: Can be fully tested by loading any dataset and verifying the column selection appears with correct options from the dataset schema.

**Acceptance Scenarios**:

1. **Given** a dataset is selected in the dropdown, **When** the user clicks "Load", **Then** a multiselect component appears showing all available columns from the dataset
2. **Given** the multiselect is visible, **When** the user selects/deselects columns, **Then** the selection is retained for subsequent searches
3. **Given** no dataset is loaded, **When** viewing the interface, **Then** the column selection component is not visible or is disabled

---

### User Story 2 - View Additional Columns in Search Results (Priority: P1)

After configuring display columns, the user performs a search and sees the selected columns in the results display alongside the retrieved text.

**Why this priority**: Equal to P1 because column configuration is meaningless without the results displaying those columns.

**Independent Test**: Can be tested by selecting columns, performing a search, and verifying all selected columns appear in results.

**Acceptance Scenarios**:

1. **Given** columns are selected (e.g., "heading", "file_name"), **When** a search returns results, **Then** the results table displays the text column plus all selected additional columns for each result
2. **Given** no additional columns are selected, **When** a search returns results, **Then** results display matches current behavior (text only)
3. **Given** multiple columns are selected, **When** viewing results, **Then** columns appear in a readable format with clear labels

---

### Edge Cases

- What happens when a dataset has only one column (the text column)?
  - The multiselect is empty or shows a message indicating no additional columns are available
- What happens when a column contains null/empty values?
  - Empty values display as empty cells or a placeholder (e.g., "-")

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a column selection component after a dataset is successfully loaded
- **FR-002**: System MUST populate the column selector with all columns available in the loaded dataset except the text column (which is always shown)
- **FR-003**: System MUST allow users to select multiple additional columns simultaneously
- **FR-004**: System MUST always display the text column in search results (non-configurable)
- **FR-005**: System MUST display all selected additional columns in search results alongside the text column
- **FR-006**: System MUST update search results display when column selection changes
- **FR-007**: System MUST handle datasets with varying numbers of columns (1 to many)

### Key Entities

- **Dataset**: Contains multiple columns of data; one column is designated as the "text" column used for SAE training (always displayed)
- **Column Selection**: User's choice of which additional columns to display in results; persists for the session
- **Search Result**: A matched document with the text column plus values from all selected additional columns

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Column selection component appears after dataset load
- **SC-002**: Search results display text column plus all selected additional columns correctly
- **SC-003**: Column selection persists across multiple searches within the same session

## Assumptions

- Datasets are loaded from pickle files containing a DataFrame with named columns
- One column per dataset is designated as the "text" column for SAE training and is always displayed in results
- Column selection is session-based and does not need to persist across application restarts
- All columns in the dataset are displayable text data
