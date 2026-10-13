"""Host-agnostic generation logic.

Nothing in ``levelforge.core`` may import ``levelforge.host``. Core is
what plugins are allowed to depend on when they want shared helpers.
"""

from levelforge.core.metrics import LevelMetrics, compute_metrics
from levelforge.core.passes import carve_rooms, connect_rooms, scatter_props

__all__ = [
    "LevelMetrics",
    "compute_metrics",
    "carve_rooms",
    "connect_rooms",
    "scatter_props",
]