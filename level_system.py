"""JSON-authored level loading and runtime helpers."""

import json

from engineglobals import EngineGlobals
from enemies import Enemy
from gamepieces import Block, BreakableBlock, HazardBlock, Sword
from gameplay import KeyPickup, LockedGate
from lifecycle import LifeCycleManager
from magic_map import Chunk
from procedural_art import ThemeBackdrop
from sprite import makeSprite
from theme_content import (
    JackieFlanBoss,
    LevodBurtimBoss,
    LucindaBoss,
    PippiBoss,
    VanProp,
    VesuviusBoss,
)


SPRITES = {
    "Enemy": Enemy,
    "Sword": Sword,
    "KeyPickup": KeyPickup,
    "LockedGate": LockedGate,
    "LucindaBoss": LucindaBoss,
    "JackieFlanBoss": JackieFlanBoss,
    "LevodBurtimBoss": LevodBurtimBoss,
    "PippiBoss": PippiBoss,
    "VesuviusBoss": VesuviusBoss,
    "VanProp": VanProp,
}


class JsonLevel:
    def __init__(self, level_id, data):
        self.level_id = level_id
        self.name = data["name"]
        self.theme = data["theme"]
        self.story = data.get("story", "")
        self.width = int(data.get("width", 60))
        self.height = int(data.get("height", 18))
        self.spawn = tuple(data.get("spawn", [64, 96]))
        self.autoscroll = bool(data.get("autoscroll", False))
        self.data = data

    def build_platform(self):
        platform = [[0 for _ in range(self.width)] for _ in range(self.height)]
        ground_rows = int(self.data.get("ground", 2))
        for y in range(self.height - ground_rows, self.height):
            for x in range(self.width):
                platform[y][x] = Block(0, True)

        for start_x, row_from_bottom, length in self.data.get("platforms", []):
            row = self.height - 1 - int(row_from_bottom)
            for x in range(int(start_x), min(self.width, int(start_x) + int(length))):
                platform[row][x] = Block(0, True)

        for x, row_from_bottom in self.data.get("hazards", []):
            row = self.height - 1 - int(row_from_bottom)
            platform[row][int(x)] = HazardBlock(0, True)

        for x, row_from_bottom in self.data.get("breakables", []):
            row = self.height - 1 - int(row_from_bottom)
            platform[row][int(x)] = BreakableBlock(0, True)
        return platform


class JsonLevelLibrary:
    def __init__(self, filename="levels.json"):
        with open(filename, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        self.levels = {level_id: JsonLevel(level_id, data) for level_id, data in raw.items()}

    def ids(self):
        return list(self.levels.keys())

    def get(self, level_id):
        return self.levels[level_id]

    def load(self, level_id):
        level = self.get(level_id)
        LifeCycleManager.dropAllObjects("PER_MAP")

        chunk = Chunk(platform=level.build_platform())
        chunk.contained_sprites = {}

        class RuntimeMap:
            pass

        runtime_map = RuntimeMap()
        runtime_map.filename = "json:{}".format(level_id)
        runtime_map.level_id = level_id
        runtime_map.chunks = [chunk]
        runtime_map.story = level.story
        EngineGlobals.game_map = runtime_map

        ThemeBackdrop(level.theme)

        for index, spec in enumerate(level.data.get("sprites", [])):
            cls = SPRITES[spec["type"]]
            kwargs = {}
            if spec["type"] == "LockedGate":
                kwargs["gate_id"] = spec.get("gate_id", "{}-gate-{}".format(level_id, index))
                kwargs["group"] = "BACK"
            sprite = makeSprite(cls, chunk, (int(spec["x"]), int(spec["y"])), **kwargs)
            chunk.contained_sprites["{}-{}".format(spec["type"], index)] = sprite

        if hasattr(EngineGlobals, "kenny"):
            EngineGlobals.kenny.current_chunk = chunk
            EngineGlobals.kenny.x_position, EngineGlobals.kenny.y_position = level.spawn
        return level


LEVEL_LIBRARY = None


def get_level_library():
    global LEVEL_LIBRARY
    if LEVEL_LIBRARY is None:
        LEVEL_LIBRARY = JsonLevelLibrary()
    return LEVEL_LIBRARY
