"""Complete 20-track 3D Reaching championship mode."""

import mode7_racing as base
from mode7_full_content import FULL_TRACKS
from mode7_full_core import FullMode7CoreMixin
from mode7_full_items import FullMode7ItemsMixin
from mode7_full_flow import FullMode7FlowMixin

# Importing mode7_full_content expands base.TRACKS to the 20-track catalog.
assert len(FULL_TRACKS) == 20


class FullMode7Racing(
    FullMode7FlowMixin,
    FullMode7ItemsMixin,
    FullMode7CoreMixin,
    base.Mode7Racing,
):
    """Full Grand Prix / Quick Race / Time Trial implementation."""

    pass
