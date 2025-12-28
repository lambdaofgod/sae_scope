from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict
from scipy.sparse import spmatrix


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

    def extract_families(self) -> pd.DataFrame:
        """Extract families via DFS from root nodes (no incoming edges).

        Returns:
            DataFrame with columns [feature_index, root].
        """
        roots = [n for n in self.directed.nodes() if self.directed.in_degree(n) == 0]
        rows = []
        for root in roots:
            descendants = nx.descendants(self.directed, root)
            for feat in {root} | descendants:
                rows.append({"feature_index": feat, "root": root})
        return pd.DataFrame(rows)

    def remove_roots(self) -> FeatureGraph:
        """Return new graph with root nodes removed (for iterative refinement)."""
        roots = [n for n in self.directed.nodes() if self.directed.in_degree(n) == 0]
        remaining = [n for n in self.directed.nodes() if n not in roots]
        subgraph = self.directed.subgraph(remaining).copy()

        new_graph = object.__new__(FeatureGraph)
        new_graph.mst = self.mst.subgraph(remaining).copy()
        new_graph.directed = subgraph
        return new_graph


class FeatureFamilyGraph(BaseModel):
    """Feature families with their underlying graph for visualization."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    graph: FeatureGraph
    families: pd.DataFrame  # columns: [feature_index, root]

    @classmethod
    def from_activations(
        cls,
        sae_activations: SAEActivations,
        tau: float = 0.1,
        n_iterations: int = 3,
        overlap_threshold: float = 0.6,
        epsilon: float = 1e-8,
    ) -> FeatureFamilyGraph:
        """
        Build feature families from SAE activations.

        Args:
            sae_activations: Wrapped SAE activations.
            tau: Threshold for normalized co-occurrence matrix.
            n_iterations: Number of iterations to find finer-grained families.
            overlap_threshold: Jaccard threshold for deduplicating families.
            epsilon: Small constant for numerical stability.
        """
        graph = FeatureGraph.from_cooccurrence(sae_activations, tau, epsilon)
        all_dfs = []

        current_graph = graph
        for _ in range(n_iterations):
            if current_graph.directed.number_of_nodes() == 0:
                break
            families_df = current_graph.extract_families()
            all_dfs.append(families_df)
            current_graph = current_graph.remove_roots()

        if all_dfs:
            combined = pd.concat(all_dfs, ignore_index=True)
            families = deduplicate_families(combined, overlap_threshold)
        else:
            families = pd.DataFrame(columns=["feature_index", "root"])

        return cls(graph=graph, families=families)

    def get_family_subgraph(self, root: int) -> nx.DiGraph:
        """Get the directed subgraph for a specific family."""
        family_features = self.families[self.families["root"] == root]["feature_index"].tolist()
        return self.graph.directed.subgraph(family_features).copy()

    def get_root_for_feature(self, feature_idx: int) -> int | None:
        """Get the root of the family containing this feature."""
        match = self.families[self.families["feature_index"] == feature_idx]
        if match.empty:
            return None
        return int(match.iloc[0]["root"])


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
    families: pd.DataFrame,
    overlap_threshold: float,
) -> pd.DataFrame:
    """
    Merge families with high Jaccard overlap.

    Args:
        families: DataFrame with columns [feature_index, root].
        overlap_threshold: Jaccard similarity threshold.

    Returns:
        DataFrame with deduplicated families.
    """
    if families.empty:
        return families

    roots = families["root"].unique()
    if len(roots) <= 1:
        return families

    # Build feature sets per root
    root_to_features: dict[int, set[int]] = {}
    for root in roots:
        root_to_features[root] = set(
            families[families["root"] == root]["feature_index"].tolist()
        )

    # Compute Jaccard similarities and merge
    root_list = list(roots)
    merged_to: dict[int, int] = {}  # root -> winning root

    for i, root_i in enumerate(root_list):
        if root_i in merged_to:
            continue
        features_i = root_to_features[root_i]

        for j in range(i + 1, len(root_list)):
            root_j = root_list[j]
            if root_j in merged_to:
                continue
            features_j = root_to_features[root_j]

            intersection = len(features_i & features_j)
            union = len(features_i | features_j)
            if union > 0 and intersection / union > overlap_threshold:
                # Merge j into i (i has larger family or came first)
                if len(features_j) > len(features_i):
                    merged_to[root_i] = root_j
                    features_j |= features_i
                    root_to_features[root_j] = features_j
                    break
                else:
                    merged_to[root_j] = root_i
                    features_i |= features_j
                    root_to_features[root_i] = features_i

    # Build result DataFrame with updated roots
    def get_final_root(root: int) -> int:
        while root in merged_to:
            root = merged_to[root]
        return root

    result_rows = []
    seen_features: set[int] = set()
    for root in roots:
        final_root = get_final_root(root)
        for feat in root_to_features[root]:
            if feat not in seen_features:
                result_rows.append({"feature_index": feat, "root": final_root})
                seen_features.add(feat)

    return pd.DataFrame(result_rows)
