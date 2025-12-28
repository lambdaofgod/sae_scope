import numpy as np
from scipy.sparse import csr_matrix

from sae_scope.backend.feature_families import SAEActivations


def test_sae_activations_from_activations():
    # 1 sample, 3 features - features 0 and 2 are active
    activations = csr_matrix([[1.0, 0.0, 0.5]])  # shape (1, 3)

    sae = SAEActivations.from_activations(activations)

    assert sae.activations.shape == (1, 3)
    assert sae.binary.shape == (1, 3)
    assert sae.frequencies.shape == (3,)

    # Binary should be 1 where activation > 0
    expected_binary = csr_matrix([[1, 0, 1]])
    assert (sae.binary.toarray() == expected_binary.toarray()).all()

    # Frequencies: count of active samples per feature
    expected_frequencies = np.array([1, 0, 1], dtype=np.float32)
    np.testing.assert_array_equal(sae.frequencies, expected_frequencies)
