# Quickstart: Data Tab Refactor with Text Search

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

## Testing Text Search

1. Select a dataset from dropdown (e.g., `roam_df20250217.pkl`)
2. Click "Load Dataset"
3. Optionally select additional columns to display
4. Click "Apply"
5. Navigate to **Data** tab
6. In the "Search Texts" section:
   - Select search mode (Lexical, Vector, or Hybrid)
   - Enter a query (e.g., "game review")
   - Set max results
   - Click "Search"
7. Results appear with: index, selected columns, text, Score
8. Expand "All Data" accordion to see full dataset

## Testing Reusable Component

Verify the same search UI pattern appears in:
- **Data** tab (text search)
- **Features** tab (feature label search)

Both should have identical UI layout:
- Search Mode dropdown
- Max Results number input
- Query textbox
- Search button
- Results dataframe
