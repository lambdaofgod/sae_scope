"""Abstract base class for datasets with texts and SAE feature activations."""

from abc import ABC, abstractmethod

import pandas as pd

from sae_scope.backend.features import SAEFeatures


class SAELensDataset(ABC):
    """Abstract base class for datasets of texts with pre-computed SAE feature activations."""

    @property
    @abstractmethod
    def features(self) -> SAEFeatures:
        """Feature metadata and search functionality."""
        ...

    @abstractmethod
    def __len__(self) -> int:
        """Return number of text records."""
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

    @abstractmethod
    def compute_feature_statistics(self) -> pd.DataFrame:
        """
        Compute statistics for all features.

        Returns:
            DataFrame with columns:
                - "index": Feature index
                - "label": Feature label
                - "frequency": Normalized frequency (0-1) of nonzero activations
                - "std": Standard deviation of activation values
                - "max": Maximum activation value
        """
        ...
