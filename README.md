# SAE Scope Dashboard

A Gradio dashboard for exploring text datasets with pre-computed SAE (Sparse Autoencoder) feature activations.

## Features

- Select datasets from dropdown (loads from `/data` folder)
- Visualize texts as a scatterplot with selectable feature axes
- Search and filter features by label
- Hover over points to see original text
- View full text table in Data tab

## Dataset Setup

Place `.pkl` dataset files in the `/data` directory. Datasets must be created using [interp_embed](https://github.com/nickjiang2378/interp_embed):

```python
from interp_embed import Dataset

# Create and save dataset
dataset.save_to_file("data/my_dataset.pkl")
```

## Launch

```bash
uv run python -m sae_scope.frontend.app
```

Dashboard opens at http://localhost:7860
