"""SAE feature metadata and search functionality."""

from dataclasses import dataclass


@dataclass
class SAEFeatures:
    """Collection of SAE feature labels with search and formatting methods."""

    labels: list[str]
    """List of human-readable feature labels, indexed by feature number."""

    def __post_init__(self) -> None:
        """Validate that at least 2 features are provided."""
        if len(self.labels) < 2:
            raise ValueError("SAEFeatures must have at least 2 labels")

    def __len__(self) -> int:
        """Return number of features."""
        return len(self.labels)

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
        if index < 0 or index >= len(self.labels):
            raise IndexError(f"Feature index {index} out of range [0, {len(self.labels)})")
        return f"{index}: {self.labels[index]}"

    def get_all_formatted_labels(self) -> list[str]:
        """
        Get all feature labels in display format.

        Returns:
            List of formatted strings like ["0: feature_a", "1: feature_b", ...].
        """
        return [f"{i}: {label}" for i, label in enumerate(self.labels)]

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
        if ": " not in formatted:
            raise ValueError(f"Invalid formatted label: {formatted!r} (expected 'N: <label>')")
        try:
            index_str = formatted.split(": ", 1)[0]
            return int(index_str)
        except ValueError as e:
            raise ValueError(f"Invalid formatted label: {formatted!r} (index not an integer)") from e

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
        if not query:
            raise ValueError("Search query cannot be empty")
        query_lower = query.lower()
        return [
            (i, label)
            for i, label in enumerate(self.labels)
            if query_lower in label.lower()
        ]
