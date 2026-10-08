"""Runtime hook that adds the ketchup side-boss to Theo's existing dill level."""

from decimal import Decimal

import pyglet

from engineglobals import EngineGlobals
from ketchup_boss import KetchupBossEncounter
from lifecycle import GameObject


class KetchupDoorHandler(GameObject):
    """Lets the custom trailer door use D without changing Player's generic door code."""

    def __init__(self, encounter):
        self.encounter = encounter
        super().__init__(lifecycle_manager="PER_MAP")
        EngineGlobals.window.push_handlers(self)

    def _near_door(self):
        player = getattr(EngineGlobals, "kenny", None)
        door = getattr(self.encounter, "trailer_door", None)
        if player is None or door is None or player.current_chunk is not door.current_chunk:
            return False
        return (
            abs(Decimal(player.x_position) - Decimal(door.x_position)) <= Decimal(78)
            and abs(Decimal(player.y_position) - Decimal(door.y_position)) <= Decimal(105)
        )

    def on_key_press(self, symbol, modifiers):
        if symbol != pyglet.window.key.D or not self._near_door():
            return pyglet.event.EVENT_UNHANDLED
        player = getattr(EngineGlobals, "kenny", None)
        if player is None:
            return pyglet.event.EVENT_UNHANDLED
        self.encounter.enter(player)
        try:
            player._play_sound(player.door_open_close)
        except Exception:
            pass
        return pyglet.event.EVENT_HANDLED

    def on_finalDeletion(self):
        try:
            EngineGlobals.window.remove_handlers(self)
        except Exception:
            pass


def install_ketchup_boss():
    """Wrap Theo's normal level builder and append the ketchup boss room/door."""
    import maploader

    if getattr(maploader, "_ketchup_boss_installed", False):
        return

    original_build_theo_level = maploader._build_theo_level

    def build_theo_with_ketchup(map_obj):
        original_build_theo_level(map_obj)
        theo = getattr(map_obj, "theo_encounter", None)
        if theo is None:
            return
        chunk = map_obj.chunks[0]
        encounter = KetchupBossEncounter(
            chunk,
            map_obj.player_spawn,
            theo.table_x,
            theo.table_y,
        )
        handler = KetchupDoorHandler(encounter)
        map_obj.ketchup_boss = encounter
        map_obj.ketchup_door_handler = handler
        if hasattr(theo, "prompt_label"):
            theo.prompt_label.text = "Press D at Theo's table — or open the KETCHUP ROOM door past him"

    maploader._build_theo_level = build_theo_with_ketchup
    maploader._ketchup_boss_installed = True
