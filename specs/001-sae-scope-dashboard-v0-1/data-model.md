# Data Model: SAE Scope Dashboard v0.1

**Date**: 2025-12-18
**Feature**: 001-sae-scope-dashboard-v0-1

## Overview

The backend consists of two main classes that provide data abstractions for the Gradio frontend:
- `SAEFeatures`: Manages SAE feature metadata and search functionality
- `SAELensDataset`: Abstract base class for datasets with texts and SAE activations, provides dataframe selection for visualization

## Class Definitions

### SAEFeatures

Manages the collection of SAE feature labels and provides search/formatting functionality.

```python
from dataclasses import dataclass

@dataclass
class SAEFeatures:
    """Collection of SAE feature labels with search and formatting methods."""

    labels: list[str]
    """List of human-readable feature labels, indexed by feature number."""

    def search(self, query: str) -> list[tuple[int, str]]:
        """
        Search features by label substring match.

        Args:
            query: Search string to match against feature labels (case-insensitive).

        Returns:
            List of (index, label) tuples for matching features.

        Raises:
            ValueError: If query is empty string.
        """
        ...

    def get_formatted_label(self, index: int) -> str:
        """
        Get feature label in display format "N: <label>".

        Args:
            index: Feature index (0-based).

        Returns:
            Formatted string like "0: feature_name".

        Raises:
            IndexError: If index out of range.
        """
        ...

    def get_all_formatted_labels(self) -> list[str]:
        """
        Get all feature labels in display format.

        Returns:
            List of formatted strings like ["0: feature_a", "1: feature_b", ...].
        """
        ...

    def parse_formatted_label(self, formatted: str) -> int:
        """
        Extract feature index from formatted label string.

        Args:
            formatted: String in format "N: <label>".

        Returns:
            Feature index as integer.

        Raises:
            ValueError: If string not in expected format.
        """
        ...

    def __len__(self) -> int:
        """Return number of features."""
        ...
```

### SAELensDataset (Abstract Base Class)

Abstract base class for datasets containing texts and their SAE feature activations. Concrete implementations will handle specific data sources/formats.

```python
from abc import ABC, abstractmethod
import pandas as pd

class SAELensDataset(ABC):
    """Abstract base class for datasets of texts with pre-computed SAE feature activations."""

    @property
    @abstractmethod
    def features(self) -> SAEFeatures:
        """Feature metadata and search functionality."""
        ...

    @abstractmethod
    def get_scatter_dataframe(
        self,
        feature_x_index: int,
        feature_y_index: int
    ) -> pd.DataFrame:
        """
        Get DataFrame for scatterplot visualization with two selected features.

        Args:
            feature_x_index: Feature index for X axis.
            feature_y_index: Feature index for Y axis.

        Returns:
            DataFrame with columns:
                - "x": Activation values for feature_x
                - "y": Activation values for feature_y
                - "text": Original text content (for Plotly hover display)

        Raises:
            IndexError: If either feature index out of range.
            ValueError: If feature_x_index == feature_y_index.
        """
        ...

    @abstractmethod
    def get_text_dataframe(self) -> pd.DataFrame:
        """
        Get DataFrame for Data tab display.

        Returns:
            DataFrame with columns:
                - "index": Row number
                - "text": Full text content
        """
        ...

    def get_default_feature_indices(self) -> tuple[int, int]:
        """
        Get default feature indices for initial visualization.

        Returns:
            Tuple of (x_index, y_index) for first two features (0, 1).

        Raises:
            ValueError: If dataset has fewer than 2 features.
        """
        if len(self.features) < 2:
            raise ValueError("Dataset must have at least 2 features")
        return (0, 1)

    @abstractmethod
    def __len__(self) -> int:
        """Return number of text records."""
        ...
```

## Entity Relationships

```text
SAELensDataset (ABC)
    |
    +-- features: SAEFeatures      # Feature metadata (abstract property)
            |
            +-- labels: list[str]  # One label per feature

Concrete implementations will add:
    +-- texts: list[str]           # One text per record
    +-- activations: DataFrame     # Rows=texts, Cols=features
```

## Validation Rules

| Class | Field/Method | Rule |
|-------|--------------|------|
| SAEFeatures | labels | MUST have at least 2 labels |
| SAEFeatures | search query | MUST NOT be empty string |
| SAELensDataset | get_scatter_dataframe | feature_x_index MUST != feature_y_index |
| SAELensDataset | get_default_feature_indices | MUST have at least 2 features |
| SAELensDataset | __len__ | MUST return at least 1 |

## State Transitions

Not applicable - these are immutable data containers.

### InterpEmbedDataset (Concrete Implementation)

Concrete implementation wrapping `interp_embed.Dataset` for loading `.pkl` files.

```python
from interp_embed import Dataset as InterpDataset

class InterpEmbedDataset(SAELensDataset):
    """Concrete implementation using interp_embed.Dataset."""

    def __init__(self, interp_dataset: InterpDataset, text_field: str = "text"):
        """
        Initialize from an interp_embed Dataset.

        Args:
            interp_dataset: Loaded interp_embed.Dataset instance.
            text_field: Column name in the dataset containing text content.

        Raises:
            ValueError: If dataset has fewer than 2 features.
        """
        ...

    @classmethod
    def load(cls, file_path: str, text_field: str = "text") -> "InterpEmbedDataset":
        """
        Load dataset from a .pkl file.

        Args:
            file_path: Path to .pkl file saved by interp_embed.
            text_field: Column name containing text.

        Returns:
            InterpEmbedDataset instance.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not a valid interp_embed dataset.
        """
        ...

    @property
    def features(self) -> SAEFeatures:
        """Feature metadata from interp_embed labels."""
        ...

    def __len__(self) -> int:
        """Number of documents in dataset."""
        ...

    def get_scatter_dataframe(
        self,
        feature_x_index: int,
        feature_y_index: int,
    ) -> pd.DataFrame:
        """
        Get scatter data using latents() for activations.

        Uses interp_embed's latents(aggregation_method='max') for activation values.
        """
        ...

    def get_text_dataframe(self) -> pd.DataFrame:
        """Get text data from underlying pandas DataFrame."""
        ...
```

## Entity Relationships (Updated)

```text
SAELensDataset (ABC)
    |
    +-- InterpEmbedDataset (concrete)
            |
            +-- _dataset: interp_embed.Dataset
            +-- _features: SAEFeatures
            +-- _text_field: str
```

## Notes

- `SAELensDataset` is abstract to allow different concrete implementations for various data sources
- `InterpEmbedDataset` wraps `interp_embed.Dataset` and uses its methods:
  - `load_from_file()` for loading
  - `latents()` for activation matrix
  - `feature_labels()` for label dictionary
  - `pandas()` for underlying DataFrame with text
- All stubs include type annotations per Constitution requirements
- Fail-First: All methods raise exceptions on invalid input (no silent failures)
- `SAEFeatures` remains a dataclass as it is a simple data container with utility methods
