import numpy as np
import pytest
from scipy.sparse import csr_matrix

from sae_scope.backend.feature_families import (
    SAEActivations,
    FeatureGraph,
    FeatureFamily,
    find_feature_families,
    compute_cooccurrence_matrix,
)


@pytest.fixture
def test_activations():
    """
    5 samples, 4 features with two clusters connected by a bridge.

    Co-occurrence graph (MST):

        0 --- 1
        |
        2 --- 3

    - Features 0,1 co-occur in samples 0,1
    - Features 2,3 co-occur in samples 2,3
    - Feature 0,2 co-occur in sample 4 (bridge)
    """
    data = np.array([
        [1.0, 1.0, 0.0, 0.0],  # sample 0: features 0,1
        [1.0, 1.0, 0.0, 0.0],  # sample 1: features 0,1
        [0.0, 0.0, 1.0, 1.0],  # sample 2: features 2,3
        [0.0, 0.0, 1.0, 1.0],  # sample 3: features 2,3
        [1.0, 0.0, 1.0, 0.0],  # sample 4: features 0,2 (bridge)
    ])
    return csr_matrix(data)


def test_compute_cooccurrence_matrix(test_activations):
    sae = SAEActivations.from_activations(test_activations)

    cooc = compute_cooccurrence_matrix(sae, tau=0.0, epsilon=1e-8)
    cooc_dense = cooc.toarray()

    # Features 0 and 1 co-occur in 2 samples
    # Feature 0 active in 3 samples, so normalized: 2/3
    assert np.isclose(cooc_dense[0, 1], 2 / 3)

    # Features 2 and 3 co-occur in 2 samples
    # Feature 2 active in 3 samples, so normalized: 2/3
    assert np.isclose(cooc_dense[2, 3], 2 / 3)

    # Features 1 and 2 never co-occur
    assert cooc_dense[1, 2] == 0.0


def test_feature_graph_builds_mst(test_activations):
    sae = SAEActivations.from_activations(test_activations)

    graph = FeatureGraph.from_cooccurrence(sae, tau=0.1, epsilon=1e-8)

    # MST should have n-1 edges for n nodes
    assert graph.mst.number_of_nodes() == 4
    assert graph.mst.number_of_edges() == 3

    # Directed graph should have same structure
    assert graph.directed.number_of_nodes() == 4
    assert graph.directed.number_of_edges() == 3


def test_find_feature_families_groups_cooccurring(test_activations):
    sae = SAEActivations.from_activations(test_activations)

    families = find_feature_families(sae, tau=0.1, n_iterations=1)

    # Should find families grouping co-occurring features
    assert len(families) > 0
    assert all(isinstance(f, FeatureFamily) for f in families)

    # Check that features 0,1 are in same family or 2,3 are in same family
    all_indices = [f.feature_indices for f in families]
    has_01_family = any(0 in idx and 1 in idx for idx in all_indices)
    has_23_family = any(2 in idx and 3 in idx for idx in all_indices)
    assert has_01_family or has_23_family
