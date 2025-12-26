"""Weaviate-based retriever implementation."""

import re

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery

from sae_scope.backend.retriever.base import Retriever, SearchMode, SearchResult


class WeaviateRetriever(Retriever):
    """Weaviate-based implementation supporting lexical, vector, and hybrid search."""

    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        """Initialize Weaviate client connection.

        Args:
            host: Weaviate server host
            port: Weaviate server port

        Raises:
            ConnectionError: If Weaviate is not available
        """
        self._client = weaviate.connect_to_local(host=host, port=port)
        self._check_connection()
        self._current_collection: str | None = None

    def _check_connection(self) -> None:
        """Check if Weaviate is available.

        Raises:
            ConnectionError: If Weaviate is not ready
        """
        if not self._client.is_ready():
            raise ConnectionError(
                "Weaviate is not available. Please start Weaviate with: docker-compose up -d"
            )

    def _derive_collection_name(self, dataset_name: str) -> str:
        """Derive a valid Weaviate collection name from dataset filename.

        Args:
            dataset_name: Dataset filename (e.g., "emotions_sae_features.pkl")

        Returns:
            Valid collection name (e.g., "EmotionsSaeFeatures")
        """
        # Remove file extension
        name = re.sub(r"\.[^.]+$", "", dataset_name)
        # Replace non-alphanumeric with spaces, then title case
        name = re.sub(r"[^a-zA-Z0-9]+", " ", name)
        # Convert to PascalCase
        name = "".join(word.capitalize() for word in name.split())
        # Ensure starts with letter (Weaviate requirement)
        if name and not name[0].isalpha():
            name = "Dataset" + name
        return name or "DefaultCollection"

    def ensure_indexed(self, dataset_name: str, labels: list[str]) -> None:
        """Ensure labels are indexed for the given dataset.

        Creates collection if it doesn't exist and populates with labels.

        Args:
            dataset_name: Name of the dataset
            labels: List of feature labels to index
        """
        self._check_connection()
        collection_name = self._derive_collection_name(dataset_name)
        self._current_collection = collection_name

        # Check if collection already exists
        if self._client.collections.exists(collection_name):
            return

        # Create collection with text2vec-transformers vectorizer
        self._client.collections.create(
            name=collection_name,
            vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
            properties=[
                Property(name="label", data_type=DataType.TEXT),
                Property(
                    name="feature_index",
                    data_type=DataType.INT,
                    skip_vectorization=True,
                ),
            ],
        )

        # Index all labels
        collection = self._client.collections.get(collection_name)
        with collection.batch.dynamic() as batch:
            for idx, label in enumerate(labels):
                batch.add_object(
                    properties={"label": label, "feature_index": idx}
                )

    def search(
        self, query: str, mode: SearchMode, k: int = 10
    ) -> list[SearchResult]:
        """Find top k matching features.

        Args:
            query: Search query string
            mode: Search mode (lexical, vector, or hybrid)
            k: Maximum number of results to return

        Returns:
            List of SearchResult objects ordered by relevance

        Raises:
            ConnectionError: If Weaviate is not available
            ValueError: If no collection is set (ensure_indexed not called)
        """
        self._check_connection()

        if self._current_collection is None:
            raise ValueError(
                "No collection set. Call ensure_indexed() first."
            )

        collection = self._client.collections.get(self._current_collection)

        if mode == SearchMode.LEXICAL:
            response = collection.query.bm25(
                query=query,
                limit=k,
                return_metadata=MetadataQuery(score=True),
            )
        elif mode == SearchMode.VECTOR:
            response = collection.query.near_text(
                query=query,
                limit=k,
                return_metadata=MetadataQuery(distance=True),
            )
        elif mode == SearchMode.HYBRID:
            response = collection.query.hybrid(
                query=query,
                limit=k,
                alpha=0.5,
                return_metadata=MetadataQuery(score=True),
            )
        else:
            raise ValueError(f"Unknown search mode: {mode}")

        results = []
        for obj in response.objects:
            # Extract score based on mode
            if mode == SearchMode.VECTOR:
                # Convert distance to similarity score (lower distance = higher score)
                score = 1.0 - (obj.metadata.distance or 0.0)
            else:
                score = obj.metadata.score or 0.0

            results.append(
                SearchResult(
                    index=obj.properties["feature_index"],
                    label=obj.properties["label"],
                    score=score,
                    metadata={"mode": mode.value},
                )
            )

        return results

    def close(self) -> None:
        """Close the Weaviate client connection."""
        self._client.close()
