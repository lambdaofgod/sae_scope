from __future__ import annotations

import networkx as nx
import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict
from scipy.sparse import spmatrix, csr_matrix
from sklearn.metrics import pairwise_distances


class SAEActivations(BaseModel):
    """Wrapper for SAE activation matrix with precomputed derived quantities."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    activations: spmatrix  # Shape (n_samples, n_features), sparse
    binary: spmatrix  # 1 if active, 0 otherwise, shape (n_samples, n_features)
    frequencies: NDArray[np.float32]  # Activation count per feature, shape (n_features,)

    @classmethod
    def from_activations(
        cls,
        activations: spmatrix,
        activation_threshold: float = 0.0,
    ) -> SAEActivations:
        """
        Create wrapper from raw activation matrix.

        Args:
            activations: Sparse matrix (n_samples, n_features).
            activation_threshold: Threshold to binarize (default: >0 is active).
        """
        binary = activations > activation_threshold
        frequencies = np.asarray(binary.sum(axis=0)).flatten().astype(np.float32)
        return cls(activations=activations, binary=binary, frequencies=frequencies)


class FeatureFamily(BaseModel):
    """A family of related SAE features."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    feature_indices: set[int]
    root_feature: int  # The highest-density feature (root of subtree)


class FeatureGraph:
    """Graph representation of feature relationships for family extraction."""

    mst: nx.Graph  # Maximum spanning tree (undirected)
    directed: nx.DiGraph  # Oriented by density (high -> low)

    def __init__(self, weights: spmatrix, frequencies: NDArray[np.float32]) -> None:
        """
        Build MST from weights and orient by density.

        Args:
            weights: Sparse co-occurrence weight matrix.
            frequencies: Activation frequency per feature.
        """
        self.mst = self._build_mst(weights)
        self.directed = self._orient_by_density(frequencies)

    @classmethod
    def from_cooccurrence(
        cls,
        sae_activations: SAEActivations,
        tau: float,
        epsilon: float,
    ) -> FeatureGraph:
        """
        Create FeatureGraph from SAE activations via co-occurrence matrix.

        Args:
            sae_activations: Wrapped activations.
            tau: Threshold for co-occurrence.
            epsilon: Numerical stability.
        """
        weights = compute_cooccurrence_matrix(sae_activations, tau, epsilon)
        return cls(weights, sae_activations.frequencies)

    def _build_mst(self, weights: spmatrix) -> nx.Graph:
        """Build maximum spanning tree from weight matrix."""
        # Create graph from sparse matrix
        g = nx.from_scipy_sparse_array(weights)
        # Maximum spanning tree (negate weights for minimum_spanning_tree)
        mst = nx.maximum_spanning_tree(g, weight="weight")
        return mst

    def _orient_by_density(self, frequencies: NDArray[np.float32]) -> nx.DiGraph:
        """Orient MST edges from high-density to low-density features."""
        directed = nx.DiGraph()
        directed.add_nodes_from(self.mst.nodes())
        for u, v in self.mst.edges():
            # Edge from higher frequency to lower frequency
            if frequencies[u] >= frequencies[v]:
                directed.add_edge(u, v)
            else:
                directed.add_edge(v, u)
        return directed

    def extract_families(self) -> list[FeatureFamily]:
        """Extract families via DFS from root nodes (no incoming edges)."""
        ...

    def remove_roots(self) -> FeatureGraph:
        """Return new graph with root nodes removed (for iterative refinement)."""
        ...


def find_feature_families(
    sae_activations: SAEActivations,
    tau: float = 0.1,
    n_iterations: int = 3,
    overlap_threshold: float = 0.6,
    epsilon: float = 1e-8,
) -> list[FeatureFamily]:
    """
    End-to-end pipeline: SAEActivations -> deduplicated FeatureFamilies.

    Pipeline:
        1. Compute co-occurrence matrix from activations
        2. Build FeatureGraph (MST + orientation)
        3. Extract families via DFS
        4. Iterate: remove roots, rebuild graph, extract finer families
        5. Deduplicate overlapping families

    Args:
        sae_activations: Wrapped SAE activations with precomputed binary matrix and frequencies.
        tau: Threshold for normalized co-occurrence matrix.
        n_iterations: Number of iterations to find finer-grained families.
        overlap_threshold: Jaccard threshold for deduplicating families.
        epsilon: Small constant for numerical stability.

    Returns:
        Deduplicated list of FeatureFamily objects.
    """
    ...


def compute_cooccurrence_matrix(
    sae_activations: SAEActivations,
    tau: float,
    epsilon: float,
) -> spmatrix:
    """
    Compute thresholded normalized co-occurrence matrix.

    Steps:
        1. C = A @ A.T (co-occurrence counts) using precomputed binary matrix
        2. Normalize: C_norm_ij = C_ij / (f_i + epsilon) using precomputed frequencies
        3. Apply threshold tau

    Args:
        sae_activations: Wrapper with binary matrix and frequencies.
        tau: Threshold value.
        epsilon: Numerical stability constant.

    Returns:
        Thresholded normalized co-occurrence matrix, sparse (n_features, n_features).
    """
    binary = sae_activations.binary
    frequencies = sae_activations.frequencies

    # C = binary.T @ binary gives (n_features, n_features) co-occurrence counts
    # Cast to float to get counts instead of boolean OR
    cooc = binary.T.astype(np.float32) @ binary

    # Normalize by row frequencies
    norm_factors = 1.0 / (frequencies + epsilon)
    cooc_norm = cooc.multiply(norm_factors[:, np.newaxis])

    # Apply threshold
    cooc_norm.data[cooc_norm.data < tau] = 0
    cooc_norm.eliminate_zeros()

    return cooc_norm


def deduplicate_families(
    families: list[FeatureFamily],
    overlap_threshold: float,
) -> list[FeatureFamily]:
    """
    Merge families with high Jaccard overlap using sklearn pairwise_distances.

    Uses jaccard distance: d = 1 - |A & B| / |A | B|
    Merges families where (1 - d) > overlap_threshold.

    Args:
        families: List of FeatureFamily objects.
        overlap_threshold: Jaccard similarity threshold (default 0.6).

    Returns:
        Deduplicated list of FeatureFamily objects.
    """
    ...
