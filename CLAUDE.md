# sae_scope Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-18

## Active Technologies
- Python 3.10 + Gradio, Plotly Express, Pandas, interp_embed (001-sae-scope-dashboard-v0-1)
- Local `.pkl` files in `/data` directory (001-sae-scope-dashboard-v0-1)
- Python 3.10 + Gradio 5.x, Plotly Express, Pandas, interp-embed (001-sae-scope-dashboard-v0-1)
- Local .pkl files in /data directory (001-sae-scope-dashboard-v0-1)
- Python 3.10 + Gradio 5.x, NumPy, Pandas (001-sae-scope-dashboard-v0-1)
- Python 3.10 + Gradio 5.x (existing), weaviate-client, rank_bm25 (002-feature-search-modes)
- Weaviate (Docker container) for vector search, in-memory for BM25 (002-feature-search-modes)
- Python 3.10 + Gradio 5.x, weaviate-client (existing), interp-embed (002-feature-search-modes)
- Weaviate vector database (for feature search, already configured) (002-feature-search-modes)
- Python 3.10 + Gradio 5.x, weaviate-client (existing), numpy (002-feature-search-modes)
- Weaviate vector database (for feature label search) (002-feature-search-modes)

- Python 3.10 + Gradio (frontend), Plotly Express (scatterplot), Pandas (dataframes), interp-embed (existing dependency) (001-sae-scope-dashboard-v0-1)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.10: Follow standard conventions

## Recent Changes
- 002-feature-search-modes: Added Python 3.10 + Gradio 5.x, weaviate-client (existing), numpy
- 002-feature-search-modes: Added Python 3.10 + Gradio 5.x, weaviate-client (existing), numpy
- 002-feature-search-modes: Added Python 3.10 + Gradio 5.x, weaviate-client (existing), interp-embed


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
