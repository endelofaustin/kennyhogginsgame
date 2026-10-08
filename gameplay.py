"""Gameplay systems shared across maps.

This module keeps new mechanics small and data-driven so maps can opt into them
without growing main.py further.
"""

import json
import os
import random
from decimal import Decimal

import pyglet

from engineglobals import EngineGlobals
from lifecycle import GameObject
from physics import PhysicsSprite


THEMES = [
    {"id": "farm", "name": "Escape from the farm", "boss": "Lucinda"},
    {"id": "river", "name": "Van down by the river", "boss": None},
    {"id": "dojo", "name": "Karate dojo", "boss": "Jackie Flan"},
    {"id": "space", "name": "Outer space dogfight", "boss": "Levod Burtim"},
    {"id": "pompeii", "name": "Escape Vesuvius through Pompeii", "boss": None},
]

STORY_BEATS = [
    "Kenny has to get off the farm.",
    "The road leads to a van down by the river.",
    "Training at the dojo prepares Kenny for Jackie Flan.",
    "A spaceship launch turns into a dogfight with Levod Burtim.",
    "The final escape races through Pompeii ahead of Vesuvius lava.",
]


class GameProgress:
    """Serializable player progress independent of a dill map file."""

    VERSION = 1

    def __init__(self):
        self.version = self.VERSION
        self.keys = 0
        self.unlocked_gates = []
        self.sword_tutorial_seen = False
        self.current_theme = 0
        self.completed_themes = []
        self.puzzle_solved = False

    def to_dict(self):
        return {
            "version": self.version,
            "keys": self.keys,
            "unlocked_gates": list(self.unlocked_gates),
            "sword_tutorial_seen": self.sword_tutorial_seen,
            "current_theme": self.current_theme,
            "completed_themes": list(self.completed_themes),
            "puzzle_solved": self.puzzle_solved,
        }

    @classmethod
    def from_dict(cls, data):
        progress = cls()
        for key in progress.to_dict():
            if key in data:
                setattr(progress, key, data[key])
        return progress


class SaveGame:
    DEFAULT_FILE = "savegame.json"

    @staticmethod
    def save(progress, player=None, filename=None):
        filename = filename or SaveGame.DEFAULT_FILE
        payload = {"progress": progress.to_dict()}
        if player is not None:
            payload["player"] = {
                "x": float(player.x_position),
                "y": float(player.y_position),
                "map": getattr(EngineGlobals.game_map, "filename", "map.dill"),
                "has_sword": bool(getattr(player, "has_sword", False)),
                "has_scythe": bool(getattr(player, "has_scythe", False)),
            }
        with open(filename, "w", encoding="utf-8") as save_file:
            json.dump(payload, save_file, indent=2, sort_keys=True)

    @staticmethod
    def load(filename=None):
        filename = filename or SaveGame.DEFAULT_FILE
        if not os.path.exists(filename):
            return GameProgress(), None
        with open(filename, "r", encoding="utf-8") as save_file:
            payload = json.load(save_file)
        return GameProgress.from_dict(payload.get("progress", {})), payload.get("player")


class BloodSpurt(GameObject):
    """Short-lived red burst used when projectiles hit enemies."""

    def __init__(self, x, y):
        self.shapes = []
        for _ in range(7):
            dot = pyglet.shapes.Circle(
                x=int(EngineGlobals.screen_x(x) + random.randrange(-8, 9)),
                y=int(EngineGlobals.screen_y(y) + random.randrange(-8, 9)),
                radius=random.randrange(2, 5),
                color=(180, 0, 0),
                batch=EngineGlobals.main_batch,
                group=EngineGlobals.editor_group_front,
            )
            self.shapes.append(dot)
        self.timer = 12
        super().__init__()

    def updateloop(self, dt):
        self.timer -= 1
        for dot in self.shapes:
            dot.x -= 1
            dot.y -= 1
        if self.timer <= 0:
            for dot in self.shapes:
                dot.delete()
            self.destroy()


class KeyPickup(PhysicsSprite):
    def getResourceImages(self):
        return {0: "good_band_aid.png"}

    def hasGravity(self):
        return False

    def on_PhysicsSprite_collided(self, collided_object=None, **kwargs):
        if collided_object and type(collided_object).__name__ == "Player":
            collided_object.progress.keys += 1
            self.destroy()


class LockedGate(PhysicsSprite):
    """Door-like barrier opened by spending one collected key."""

    def __init__(self, sprite_initializer, starting_chunk):
        self.gate_id = sprite_initializer.get("gate_id", "gate")
        super().__init__(sprite_initializer, starting_chunk)

    def getResourceImages(self):
        return {0: "door-1.png"}

    def hasGravity(self):
        return False

    def unlock(self, player):
        if self.gate_id in player.progress.unlocked_gates:
            self.destroy()
            return True
        if player.progress.keys <= 0:
            return False
        player.progress.keys -= 1
        player.progress.unlocked_gates.append(self.gate_id)
        self.destroy()
        return True


class AutoScroller(GameObject):
    """Optional horizontal auto-scroll challenge.

    Maps can create one and call start(); the camera then advances independently
    and Kenny loses if he falls too far behind.
    """

    def __init__(self, speed=Decimal("1.25")):
        self.speed = Decimal(speed)
        self.active = False
        super().__init__()

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def updateloop(self, dt):
        if not self.active or not hasattr(EngineGlobals, "our_screen"):
            return
        EngineGlobals.our_screen.x += self.speed * Decimal(dt)
        if hasattr(EngineGlobals, "kenny"):
            danger_x = EngineGlobals.our_screen.x - 24
            if EngineGlobals.kenny.x_position < danger_x:
                EngineGlobals.kenny.die_hard()
                self.stop()


class JigsawPuzzle:
    """Small shuffle/swap puzzle suitable for a map interaction."""

    def __init__(self, size=3):
        self.size = size
        self.solution = list(range(size * size))
        self.tiles = list(self.solution)

    def shuffle(self):
        random.shuffle(self.tiles)
        if self.is_solved():
            self.tiles[0], self.tiles[1] = self.tiles[1], self.tiles[0]

    def swap(self, first, second):
        if first not in range(len(self.tiles)) or second not in range(len(self.tiles)):
            return False
        self.tiles[first], self.tiles[second] = self.tiles[second], self.tiles[first]
        return self.is_solved()

    def is_solved(self):
        return self.tiles == self.solution


class PuzzleController(GameObject):
    """Keyboard-driven 3x3 jigsaw mode.

    Press P to toggle the puzzle. Arrow keys select a tile, Enter picks it, and
    Enter on a second tile swaps the pair. Solving persists in GameProgress.
    """

    def __init__(self, progress):
        self.progress = progress
        self.puzzle = JigsawPuzzle(3)
        self.puzzle.shuffle()
        self.active = False
        self.cursor = 0
        self.selected = None
        self.labels = []
        super().__init__(lifecycle_manager="UNDYING")

    def updateloop(self, dt):
        pass

    def _clear_labels(self):
        for label in self.labels:
            label.delete()
        self.labels = []

    def _draw_labels(self):
        self._clear_labels()
        if not self.active:
            return
        for idx, value in enumerate(self.puzzle.tiles):
            row, col = divmod(idx, 3)
            marker = "[{}]" if idx == self.cursor else " {} "
            text = marker.format(value + 1)
            self.labels.append(pyglet.text.Label(
                text,
                x=260 + col * 80,
                y=420 - row * 80,
                font_size=22,
                batch=EngineGlobals.main_batch,
                group=EngineGlobals.editor_group_front,
            ))

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.P:
            self.active = not self.active
            self._draw_labels()
            return pyglet.event.EVENT_HANDLED
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        row, col = divmod(self.cursor, 3)
        if symbol == pyglet.window.key.LEFT:
            col = max(0, col - 1)
        elif symbol == pyglet.window.key.RIGHT:
            col = min(2, col + 1)
        elif symbol == pyglet.window.key.UP:
            row = max(0, row - 1)
        elif symbol == pyglet.window.key.DOWN:
            row = min(2, row + 1)
        elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
            if self.selected is None:
                self.selected = self.cursor
            else:
                solved = self.puzzle.swap(self.selected, self.cursor)
                self.selected = None
                if solved:
                    self.progress.puzzle_solved = True
                    self.active = False
        self.cursor = row * 3 + col
        self._draw_labels()
        return pyglet.event.EVENT_HANDLED
