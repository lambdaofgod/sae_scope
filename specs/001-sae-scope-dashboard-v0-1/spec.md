# Feature Specification: SAE Scope Dashboard v0.1

**Feature Branch**: `001-sae-scope-dashboard-v0-1`
**Created**: 2025-12-18
**Status**: Draft
**Input**: User description: "Dashboard for text exploration using sparse autoencoders. Sparse autoencoder features extracted from each text from dataset will be used to display scatterplots and the user will be able to select 2 features used for that using the togglable left panel."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load Dataset and View Scatterplot (Priority: P1)

A researcher wants to explore their text dataset by loading a dataset that has been processed with SAE feature extraction, and immediately seeing a visual representation of the data as a scatterplot.

**Why this priority**: This is the core functionality - without data loading and visualization, the dashboard has no value. This enables the fundamental exploration workflow.

**Independent Test**: Can be fully tested by loading a sample dataset with pre-computed SAE features and verifying a scatterplot appears with data points representing texts.

**Acceptance Scenarios**:

1. **Given** the dashboard is open, **When** the user clicks the "Load Data" button and selects a valid dataset file from their directory, **Then** the system loads the data and displays a scatterplot using the first two available features as default axes.
2. **Given** a dataset file is selected, **When** the file contains texts with their SAE feature values, **Then** each text is represented as a point on the scatterplot.
3. **Given** the data is loaded, **When** the scatterplot renders, **Then** each data point is positioned according to its activation values for the two selected features (X and Y axes).

---

### User Story 2 - Select Features for Visualization (Priority: P2)

A researcher wants to change which two SAE features are used for the scatterplot axes to explore different relationships in their data.

**Why this priority**: Feature selection enables meaningful exploration - researchers need to compare different feature combinations to discover patterns. This builds on P1's basic visualization.

**Independent Test**: Can be tested by loading data, then selecting different features from the left panel and verifying the scatterplot updates accordingly.

**Acceptance Scenarios**:

1. **Given** data is loaded, **When** the user views the left panel, **Then** they see a list of all available SAE features with their labels.
2. **Given** the feature list is visible, **When** the user selects two different features using checkboxes, **Then** the scatterplot updates to use those features as X and Y axes.
3. **Given** two features are selected, **When** the user changes one feature selection, **Then** the scatterplot re-renders with the new feature combination.

---

### User Story 3 - Inspect Individual Text (Priority: P3)

A researcher wants to click on a data point in the scatterplot to see the original text content, enabling them to understand what texts cluster together for specific feature combinations.

**Why this priority**: Text inspection provides the interpretability layer - seeing actual text content helps researchers understand what the SAE features capture. This completes the exploration workflow.

**Independent Test**: Can be tested by loading data, clicking on any data point, and verifying the corresponding text content is displayed.

**Acceptance Scenarios**:

1. **Given** a scatterplot with data points is displayed, **When** the user clicks on a data point, **Then** the system displays the original text content associated with that point.
2. **Given** text content is displayed for a point, **When** the user clicks on a different data point, **Then** the displayed text updates to show the newly selected point's content.

---

### User Story 4 - Toggle Feature Panel (Priority: P4)

A researcher wants to hide the feature selection panel to maximize the scatterplot viewing area when they don't need to change feature selections.

**Why this priority**: This is a UI convenience feature that improves the viewing experience but is not essential for core functionality.

**Independent Test**: Can be tested by clicking the panel toggle and verifying the panel shows/hides while the scatterplot area expands/contracts.

**Acceptance Scenarios**:

1. **Given** the left panel is visible, **When** the user clicks the toggle button, **Then** the panel hides and the scatterplot area expands to fill the available space.
2. **Given** the left panel is hidden, **When** the user clicks the toggle button, **Then** the panel reappears with the feature list visible.

---

### User Story 5 - Search and Filter Features (Priority: P5)

A researcher working with many SAE features wants to quickly find specific features by searching or filtering the feature list.

**Why this priority**: This becomes important for usability when dealing with large numbers of features, but basic functionality works without it.

**Independent Test**: Can be tested by typing in the search field and verifying the feature list filters to show only matching features.

**Acceptance Scenarios**:

1. **Given** the feature list is displayed, **When** the user types in the search field, **Then** the feature list filters to show only features whose labels contain the search text.
2. **Given** a search filter is active, **When** the user clears the search field, **Then** all features are shown again.

---

### Edge Cases

- What happens when the user selects a file that is not a valid dataset format? System displays an error message indicating the file format is invalid.
- What happens when the user tries to select more or fewer than 2 features? System enforces exactly 2 feature selections - selecting a third deselects the oldest, deselecting when only 2 are selected is prevented.
- What happens when a data point has missing values for selected features? Points with missing values for either selected feature are excluded from the scatterplot with a visual indicator showing the count of excluded points.
- What happens when the dataset file is empty or has no data rows? System displays an appropriate error message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to load dataset files containing texts with their pre-computed SAE feature values from their local file system.
- **FR-002**: System MUST display a scatterplot visualization where each data point represents one text from the loaded dataset.
- **FR-003**: System MUST display a left panel containing the list of all available SAE features from the loaded data.
- **FR-004**: System MUST allow users to select exactly 2 features from the feature list to use as X and Y axes for the scatterplot.
- **FR-005**: System MUST update the scatterplot when the user changes feature selections.
- **FR-006**: System MUST display the original text content when a user clicks on a data point in the scatterplot.
- **FR-007**: System MUST provide a toggle control to show/hide the left feature panel.
- **FR-008**: System MUST provide a search/filter input in the feature panel to filter the feature list by label text.
- **FR-009**: System MUST use the first two available features as default axis selections when data is initially loaded.
- **FR-010**: System MUST display feature labels in the format "N: <feature_label>" where N is the feature index/number.

### Key Entities

- **Dataset**: A collection of texts with their pre-computed SAE feature values. Contains multiple TextRecords. Loaded from a file produced by the SAE feature extraction component.
- **TextRecord**: A single text entry with its original content and associated SAE feature activation values. Maps to one row in the dataset.
- **SAEFeature**: A named dimension from the sparse autoencoder. Has an index/number and a human-readable label. Each text has an activation value for each feature.
- **FeatureSelection**: The current pair of features selected for visualization. Always contains exactly 2 features (X-axis and Y-axis).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can load a dataset and see a scatterplot visualization of the data.
- **SC-002**: Users can change feature selections and see the scatterplot update accordingly.
- **SC-003**: Users can identify and read the text content of any data point with a single click.
- **SC-004**: Users can find specific features using the search functionality.
- **SC-005**: The scatterplot displays data points accurately positioned according to their feature activation values.

## Assumptions

- Dataset files are produced by a separate SAE feature extraction component and contain texts with their pre-computed feature values.
- Feature labels are included in the dataset file.
- The dashboard is intended for single-user local use (no multi-user or server deployment for v0.1).
- The dataset file format will be defined by the feature extraction component's output.
