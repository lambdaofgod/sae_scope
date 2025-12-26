# Quickstart: Feature Search Modes

**Feature**: 002-feature-search-modes
**Date**: 2025-12-26

## Prerequisites

1. Docker and Docker Compose installed
2. Python 3.10+ with uv
3. Existing SAE Scope dashboard setup

## Setup

### 1. Start Weaviate Services

```bash
# From repository root
docker-compose up -d

# Verify services are running
docker-compose ps

# Check Weaviate is ready
curl http://localhost:8080/v1/.well-known/ready
```

### 2. Install Dependencies

```bash
uv add weaviate-client
```

### 3. Run the Dashboard

```bash
uv run python -m sae_scope.frontend
```

## Usage

### Select Search Mode

1. Load a dataset from the dropdown
2. Open the "Features" tab
3. In the "Search Features" accordion, select search mode:
   - **Lexical**: Keyword matching via BM25
   - **Vector**: Semantic similarity via embeddings
   - **Hybrid**: Combined BM25 + vector

### Search for Features

1. Type your query in the search box
2. Results appear ranked by relevance
3. Use feature index to select for scatterplot

## Validation Scenarios

### Scenario 1: Mode Selection UI

1. Open Features tab
2. Verify dropdown shows three modes
3. Select each mode and verify selection persists

### Scenario 2: Search Returns Results

1. Load a dataset
2. Enter a search query
3. Verify results appear in dataframe format (Index, Label columns)

### Scenario 3: First Dataset Load (Indexing)

1. Start Weaviate fresh (no existing collections)
2. Load a dataset
3. Verify feature labels are indexed (may take a few seconds for large datasets)
4. Subsequent loads of same dataset should be instant (collection already exists)

### Scenario 4: Weaviate Unavailable

1. Stop Weaviate: `docker-compose down`
2. Try to load a dataset
3. Verify error is raised (fail-first, no silent fallback)
4. Start Weaviate and retry

## Troubleshooting

### Weaviate Connection Failed

```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs weaviate
docker-compose logs text2vec

# Restart services
docker-compose restart
```
