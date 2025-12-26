"""Concrete SAELensDataset implementation using interp_embed.Dataset."""

from pathlib import Path

import numpy as np
import pandas as pd
from interp_embed import Dataset as InterpDataset

from sae_scope.backend.dataset import SAELensDataset
from sae_scope.backend.features import SAEFeatures


class InterpEmbedDataset(SAELensDataset):
    """Concrete implementation wrapping interp_embed.Dataset."""

    def __init__(
        self,
        interp_dataset: InterpDataset,
        text_field: str = "text",
        aggregation_method: str = "max",
    ) -> None:
        """
        Initialize from an interp_embed Dataset.

        Args:
            interp_dataset: Loaded interp_embed.Dataset instance.
            text_field: Column name in the dataset containing text content.
            aggregation_method: Method for aggregating latents ("max", "mean", "binarize", "count").

        Raises:
            ValueError: If dataset has fewer than 2 features or no documents.
        """
        self._dataset = interp_dataset
        self._text_field = text_field

        # Cache latents matrix (N documents x F features)
        self._latents = interp_dataset.latents(aggregation_method=aggregation_method)
        if self._latents is None or len(self._latents) == 0:
            raise ValueError("Dataset has no documents")

        # Extract feature labels from interp_embed
        labels_dict = interp_dataset.feature_labels()
        num_features = self._latents.shape[1]

        # Build labels list - use label if available, else "Feature N"
        labels = []
        for i in range(num_features):
            if i in labels_dict and labels_dict[i]:
                labels.append(labels_dict[i])
            else:
                labels.append(f"Feature {i}")

        if len(labels) < 2:
            raise ValueError("Dataset must have at least 2 features")

        self._features = SAEFeatures(labels=labels)

        # Compute and cache feature statistics
        self._feature_stats = self.compute_feature_statistics()

    @classmethod
    def load(
        cls,
        file_path: str,
        text_field: str = "text",
        aggregation_method: str = "max",
    ) -> "InterpEmbedDataset":
        """
        Load dataset from a .pkl file.

        Args:
            file_path: Path to .pkl file saved by interp_embed.
            text_field: Column name containing text.
            aggregation_method: Method for aggregating latents ("max", "mean", "binarize", "count").

        Returns:
            InterpEmbedDataset instance.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not a valid interp_embed dataset.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        interp_ds = InterpDataset.load_from_file(str(path))
        return cls(interp_ds, text_field=text_field, aggregation_method=aggregation_method)

    @property
    def features(self) -> SAEFeatures:
        """Feature metadata from interp_embed labels."""
        return self._features

    def __len__(self) -> int:
        """Number of documents in dataset."""
        return len(self._dataset)

    def get_scatter_dataframe(
        self,
        feature_x_index: int,
        feature_y_index: int,
    ) -> pd.DataFrame:
        """
        Get DataFrame for scatterplot visualization with two selected features.

        Args:
            feature_x_index: Feature index for X axis.
            feature_y_index: Feature index for Y axis.

        Returns:
            DataFrame with columns "x", "y", "text".

        Raises:
            IndexError: If either feature index out of range.
            ValueError: If feature_x_index == feature_y_index.
        """
        num_features = len(self._features)

        if feature_x_index < 0 or feature_x_index >= num_features:
            raise IndexError(f"Feature X index {feature_x_index} out of range [0, {num_features})")
        if feature_y_index < 0 or feature_y_index >= num_features:
            raise IndexError(f"Feature Y index {feature_y_index} out of range [0, {num_features})")
        if feature_x_index == feature_y_index:
            raise ValueError("Feature X and Y indices must be different")

        # Get activation values for selected features
        x_values = self._latents[:, feature_x_index]
        y_values = self._latents[:, feature_y_index]

        # Get text content
        texts = self._dataset.documents()

        return pd.DataFrame({
            "x": x_values,
            "y": y_values,
            "text": texts,
        })

    def get_text_dataframe(self) -> pd.DataFrame:
        """
        Get DataFrame for Data tab display.

        Returns:
            DataFrame with columns "index" and "text".
        """
        texts = self._dataset.documents()
        return pd.DataFrame({
            "index": range(len(texts)),
            "text": texts,
        })

    def compute_feature_statistics(self) -> pd.DataFrame:
        """
        Compute statistics for all features.

        Returns:
            DataFrame with columns: index, label, frequency, std, max.
            Frequency is normalized (0-1) as count_nonzero / num_documents.
        """
        num_documents = self._latents.shape[0]
        num_features = self._latents.shape[1]

        # Compute statistics per feature (column)
        frequency = np.count_nonzero(self._latents, axis=0) / num_documents
        std = np.std(self._latents, axis=0)
        max_val = np.max(self._latents, axis=0)

        return pd.DataFrame({
            "index": range(num_features),
            "label": self._features.labels,
            "frequency": frequency,
            "std": std,
            "max": max_val,
        })
