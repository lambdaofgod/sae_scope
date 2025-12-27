"""Base classes and types for the retriever component."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class SearchMode(Enum):
    """Enumeration of available search strategies."""

    LEXICAL = "lexical"
    VECTOR = "vector"
    HYBRID = "hybrid"


@dataclass
class SearchResult:
    """A single search result item."""

    index: int
    label: str
    score: float
    metadata: dict = field(default_factory=dict)


@dataclass
class TextSearchResult:
    """A single text search result item."""

    doc_index: int
    text: str
    score: float
    metadata: dict = field(default_factory=dict)


class Retriever(ABC):
    """Abstract interface for search implementations."""

    @abstractmethod
    def ensure_indexed(self, dataset_name: str, labels: list[str]) -> None:
        """Ensure labels are indexed for the given dataset.

        Args:
            dataset_name: Name of the dataset (used to derive collection name)
            labels: List of feature labels to index
        """
        ...

    @abstractmethod
    def search(
        self, query: str, mode: SearchMode, k: int = 10
    ) -> list[SearchResult]:
        """Find top k matching features.

        Args:
            query: Search query string
            mode: Search mode (lexical, vector, or hybrid)
            k: Maximum number of results to return

        Returns:
            List of SearchResult objects ordered by relevance (highest first)
        """
        ...
