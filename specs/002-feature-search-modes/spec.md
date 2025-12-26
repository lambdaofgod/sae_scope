# Feature Specification: Feature Search Modes

**Feature Branch**: `002-feature-search-modes`
**Created**: 2025-12-26
**Status**: Draft
**Input**: User description: "I want to add better search capabilities. Right now the feature label search uses very simple search, I want to have a dropdown that will be used to decide whether to use lexical, hybrid or vector search. There should be an abstract component that will handle these search types which we will implement later."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select Search Mode (Priority: P1)

A researcher wants to choose their preferred search method when searching for feature labels, selecting from lexical (keyword-based), vector (semantic similarity), or hybrid (combination) search modes.

**Why this priority**: This is the core functionality - users need the ability to switch between search modes to find features using different strategies. Without mode selection, there's no enhanced search capability.

**Independent Test**: Can be tested by loading a dataset, opening the Features tab, selecting different search modes from the dropdown, and verifying the UI reflects the selection.

**Acceptance Scenarios**:

1. **Given** the Features tab is open with a dataset loaded, **When** the user views the search section, **Then** they see a dropdown with three options: "Lexical", "Vector", and "Hybrid".
2. **Given** the search mode dropdown is visible, **When** the user selects a different mode, **Then** the selection is retained for subsequent searches.
3. **Given** no mode has been explicitly selected, **When** the user opens the Features tab, **Then** the default mode is "Lexical" (fastest, no additional setup required).

---

### User Story 2 - Search with Selected Mode (Priority: P2)

A researcher wants to search for feature labels using their selected search mode and see results ranked according to that mode's algorithm.

**Why this priority**: After selecting a mode, users need to actually perform searches. This delivers the core value of improved search quality.

**Independent Test**: Can be tested by selecting each search mode, entering the same query, and verifying that search results are returned (results may differ between modes).

**Acceptance Scenarios**:

1. **Given** "Lexical" mode is selected, **When** the user enters a search query, **Then** the system returns features matching the query using keyword-based ranking.
2. **Given** "Vector" mode is selected, **When** the user enters a search query, **Then** the system returns features ranked by semantic similarity to the query.
3. **Given** "Hybrid" mode is selected, **When** the user enters a search query, **Then** the system returns features using a combination of lexical and vector scores.
4. **Given** any search mode is selected, **When** the user enters a query with no matches, **Then** the system displays an empty result set with appropriate messaging.

---

### User Story 3 - Consistent Search Interface (Priority: P3)

A researcher wants the search experience to feel consistent regardless of which mode is selected, with the same input field, result display, and interaction patterns.

**Why this priority**: Consistency reduces cognitive load. Users shouldn't need to learn different interfaces for different modes.

**Independent Test**: Can be tested by switching between all three modes and verifying the search input, result format, and interaction remain identical.

**Acceptance Scenarios**:

1. **Given** any search mode is selected, **When** the user types in the search input, **Then** results appear in the same dataframe format (Index, Label columns).
2. **Given** any search mode is selected, **When** results are displayed, **Then** the maximum number of results shown is the same across all modes.

---

### Edge Cases

- What happens when vector search is selected but no embedding model is available? System displays an informative error message and falls back to lexical search.
- What happens when the search query is empty? System shows the first N features (same behavior as current implementation).
- What happens when hybrid search is selected but vector search is unavailable? System uses lexical search only and notifies the user.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a dropdown selector with three search modes: "Lexical", "Vector", and "Hybrid".
- **FR-002**: System MUST default to "Lexical" search mode when no selection has been made.
- **FR-003**: System MUST retain the selected search mode for the duration of the session.
- **FR-004**: System MUST route search queries through an abstract search component based on the selected mode.
- **FR-005**: System MUST return search results in a consistent format regardless of search mode (Index and Label columns).
- **FR-006**: System MUST display appropriate error messages when a search mode is unavailable (e.g., missing embedding model for vector search).
- **FR-007**: System MUST limit search results to a maximum count (consistent with current 100 result limit).

### Key Entities

- **SearchMode**: An enumeration of available search types (Lexical, Vector, Hybrid). Determines which search algorithm processes queries.
- **Retriever**: An abstract component responsible for executing searches. Different implementations handle different search modes.
- **SearchResult**: A ranked list of feature matches containing feature index and label, ordered by relevance score.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can switch between three search modes with a single click.
- **SC-002**: Search results appear within 2 seconds for all modes when searching across 10,000+ feature labels.
- **SC-003**: Users can find semantically related features using vector search that would not appear in lexical search results.
- **SC-004**: The search interface remains consistent across all modes (same input, same result format).

## Assumptions

- The existing Features tab search functionality will be extended, not replaced.
- Lexical search will use standard keyword matching (similar to current implementation but with proper ranking).
- Vector search requires an embedding model; if unavailable, the system gracefully degrades.
- Hybrid search combines scores from lexical and vector approaches (exact weighting to be determined during implementation).
- The abstract Retriever component will be designed for future extensibility (new search modes can be added).
