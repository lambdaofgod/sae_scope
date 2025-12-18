# Quickstart: SAE Scope Dashboard v0.1

**Date**: 2025-12-18
**Feature**: 001-sae-scope-dashboard-v0-1

## Prerequisites

- Python 3.10+
- uv package manager

## Installation

```bash
# Clone repository (if not already done)
cd /path/to/sae_scope

# Install dependencies
uv add gradio plotly pandas
```

## Running the Dashboard

```bash
# From repository root
uv run python -m sae_scope.frontend.app
```

The dashboard will launch at `http://localhost:7860` (default Gradio port).

## Usage

### 1. Load Dataset

1. Use the dropdown at the top to select a dataset from the `/data` folder
2. The system loads the `.pkl` file containing texts with pre-computed SAE features
3. Scatterplot renders with features 0 and 1 as default axes

### 2. Select Features (Scatterplot Tab)

1. Enter comma-separated feature indices in the "Feature Indices (X, Y)" field (default: "0, 1")
2. Format: two integers separated by comma, e.g., "42, 100"
3. Scatterplot updates automatically when indices change
4. Valid indices are 0 to (number of features - 1)

### 3. Discover Features (Features Tab)

1. Switch to the "Features" tab to browse available features
2. Type in the search box to filter features by label
3. Results show feature index and label - note the index for use in Scatterplot tab
4. Up to 100 matching results are displayed

### 4. Explore Data

1. Hover over any point in the scatterplot to see the original text
2. Switch to the "Data" tab to see the full text table

## Project Structure

```text
src/sae_scope/
    backend/
        dataset.py        # SAELensDataset abstract class
        features.py       # SAEFeatures dataclass
        interp_dataset.py # InterpEmbedDataset implementation
    frontend/
        app.py            # Gradio application entry
        components/
            tabs.py           # Tab structure with feature inputs
            features_tab.py   # Searchable feature list
```

## Development

### Running Tests

```bash
uv run pytest tests/
```

### Code Style

```bash
# Check linting
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/
```

## Troubleshooting

### "No module named sae_scope"

Ensure you're running from the repository root and the package is installed:

```bash
uv pip install -e .
```

### "ValueError: Dataset must have at least 2 features"

The loaded dataset file must contain at least 2 SAE features for visualization.

### Invalid feature indices error

Feature indices must be:
- Exactly 2 comma-separated integers (e.g., "0, 1")
- Between 0 and (number of features - 1)
- Use the Features tab to search and find valid indices
