"""Complete deluxe 3D Reaching championship and battle mode."""

import mode7_racing as base
from mode7_full_content import FULL_TRACKS
from mode7_full_core import FullMode7CoreMixin
from mode7_full_items import FullMode7ItemsMixin
from mode7_full_flow import FullMode7FlowMixin

# First define the stable full-game base class. mode7_deluxe imports this
# during its own initialization, then the late imports below add deluxe racing
# and Hoggin Out without changing main.py or the other top-level game modes.
assert len(FULL_TRACKS) == 20


class _BaseFullMode7Racing(
    FullMode7FlowMixin,
    FullMode7ItemsMixin,
    FullMode7CoreMixin,
    base.Mode7Racing,
):
    """20-track Grand Prix / Quick Race / Time Trial implementation."""

    pass


# Keep this name available while mode7_deluxe imports us so that layer can
# inherit from the stable base without duplicating the race engine.
FullMode7Racing = _BaseFullMode7Racing

from mode7_deluxe import DeluxeMode7Racing  # noqa: E402  intentional late import

FullMode7Racing = DeluxeMode7Racing

# Hoggin Out then subclasses the completed deluxe game. main.py continues to
# import the same stable name, so Start, Karts not Farts, Load Game, Settings,
# and the platformer routing remain untouched.
from mode7_battle import HogginOutMode7Racing  # noqa: E402  intentional late import

FullMode7Racing = HogginOutMode7Racing
