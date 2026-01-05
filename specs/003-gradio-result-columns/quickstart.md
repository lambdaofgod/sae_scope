# Quickstart: Gradio Result Columns Configuration

## Prerequisites

- Python 3.10+
- uv package manager
- Docker (for Weaviate)

## Setup

```bash
# Install dependencies
uv sync

# Start Weaviate (if not running)
docker-compose up -d
```

## Running the App

```bash
uv run python -m sae_scope.frontend
```

## Testing Column Selection

1. Select a dataset from dropdown (e.g., `roam_df20250217.pkl`)
2. After load completes, column selector appears below aggregation dropdown
3. Select additional columns to display (e.g., `file_name`, `heading`)
4. Navigate to SAE Retrieval tab
5. Enter query and click "Find Latents"
6. Click "Find Texts"
7. Results table now shows: Index, Text, Score, plus selected columns

## Development

### Running Tests

```bash
uv run pytest tests/
```

### File Structure After Refactor

```text
src/sae_scope/frontend/
  app.py                 # Orchestrator (~100 lines)
  components/
    scatterplot_tab.py   # Scatterplot tab
    features_tab.py      # Features tab
    data_tab.py          # Data tab
    sae_retrieval_tab.py # SAE Retrieval tab
```
