"""UI components for SAE Scope frontend."""

from sae_scope.frontend.components.data_tab import (
    create_data_ui,
    wire_data_events,
)
from sae_scope.frontend.components.features_tab import (
    create_features_ui,
    get_summary_stats,
    get_top_n_features,
    search_features,
    wire_features_events,
)
from sae_scope.frontend.components.sae_retrieval_tab import (
    create_sae_retrieval_ui,
    wire_sae_retrieval_events,
)
from sae_scope.frontend.components.scatterplot_tab import (
    create_scatterplot,
    create_scatterplot_ui,
    wire_scatterplot_events,
)
from sae_scope.frontend.components.html_table import HTMLTableElement
from sae_scope.frontend.components.search_component import create_search_ui
from sae_scope.frontend.components.tabs import create_tabs

__all__ = [
    # Scatterplot tab
    "create_scatterplot",
    "create_scatterplot_ui",
    "wire_scatterplot_events",
    # Features tab
    "create_features_ui",
    "wire_features_events",
    "get_summary_stats",
    "get_top_n_features",
    "search_features",
    # Data tab
    "create_data_ui",
    "wire_data_events",
    # SAE Retrieval tab
    "create_sae_retrieval_ui",
    "wire_sae_retrieval_events",
    # Reusable components
    "create_search_ui",
    "HTMLTableElement",
    # Legacy
    "create_tabs",
]
