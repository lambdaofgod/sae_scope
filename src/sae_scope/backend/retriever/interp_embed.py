"""InterpEmbedRetriever for two-phase text search."""

import numpy as np

from sae_scope.backend.interp_dataset import InterpEmbedDataset
from sae_scope.backend.retriever.base import Retriever, SearchMode, SearchResult, TextSearchResult


def _softmax(x: np.ndarray) -> np.ndarray:
    """Compute softmax of array x."""
    exp_x = np.exp(x - np.max(x))  # Subtract max for numerical stability
    return exp_x / exp_x.sum()


class InterpEmbedRetriever:
    """Two-phase text retriever using feature label similarity and latent activations."""

    def __init__(
        self,
        feature_retriever: Retriever,
        dataset: InterpEmbedDataset,
    ) -> None:
        """Initialize with a feature retriever and dataset.

        Args:
            feature_retriever: Retriever for feature label search (Phase 1).
            dataset: InterpEmbedDataset for text search (Phase 2).
        """
        self._feature_retriever = feature_retriever
        self._dataset = dataset

    def search_latents(
        self,
        query: str,
        mode: SearchMode,
        k: int = 10,
    ) -> list[SearchResult]:
        """Phase 1: Find latents by label similarity.

        Args:
            query: Search query string.
            mode: Search mode (lexical, vector, or hybrid).
            k: Maximum number of latents to return.

        Returns:
            List of SearchResult objects with feature index, label, and score.
        """
        return self._feature_retriever.search(query, mode, k)

    def _rerank_features(
        self,
        features: list[tuple[int, float]],
        query: str,
    ) -> list[tuple[int, float]]:
        """Rerank features using LLM (stub - not implemented).

        Args:
            features: List of (feature_index, score) tuples.
            query: Original search query (unused in stub).

        Returns:
            Input unchanged. Will be implemented when LLM connection available.
        """
        return features

    def _score_documents(
        self,
        feature_indices: list[int],
        weights: np.ndarray,
        k: int,
    ) -> list[TextSearchResult]:
        """Compute weighted document scores using latent activations.

        Args:
            feature_indices: List of feature indices to use for scoring.
            weights: Normalized weights for each feature (must sum to 1).
            k: Maximum number of documents to return.

        Returns:
            List of TextSearchResult objects sorted by score (highest first).
        """
        # Get latents matrix (N documents x F features)
        latents = self._dataset._latents

        # Compute weighted sum: doc_scores = latents[:, feature_indices] @ weights
        doc_scores = latents[:, feature_indices] @ weights

        # Get document texts
        texts = self._dataset._dataset.documents()

        # Get top-k document indices (sorted by score, descending)
        top_indices = np.argsort(doc_scores)[::-1][:k]

        return [
            TextSearchResult(
                doc_index=int(idx),
                text=texts[idx][:200],  # Truncate to 200 chars for display
                score=float(doc_scores[idx]),
                metadata={"feature_indices": feature_indices},
            )
            for idx in top_indices
        ]

    def search_texts(
        self,
        selected_features: list[tuple[int, float]],
        temperature: float = 1.0,
        k: int = 10,
    ) -> list[TextSearchResult]:
        """Phase 2: Find texts using selected latent activations.

        Args:
            selected_features: List of (feature_index, score) tuples.
            temperature: Temperature for softmax weighting (lower = sharper).
            k: Maximum number of texts to return.

        Returns:
            List of TextSearchResult objects with doc_index, text, and score.

        Raises:
            ValueError: If no features are selected.
        """
        if not selected_features:
            raise ValueError("At least one feature must be selected")

        # Rerank features (stub - returns unchanged)
        reranked = self._rerank_features(selected_features, query="")

        # Extract indices and scores
        feature_indices = [idx for idx, _ in reranked]
        scores = np.array([score for _, score in reranked])

        # Compute softmax weights with temperature
        weights = _softmax(scores / temperature)

        # Score documents and return top-k
        return self._score_documents(feature_indices, weights, k)
