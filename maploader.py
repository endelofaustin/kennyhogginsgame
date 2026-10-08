import dill
import pyglet

import gamepieces
from bosses import PearlyPaul, MrOmen
from enemies import Enemy
from engineglobals import EngineGlobals
from gamepieces import Door, NirvanaFruit, Sword
from gameplay import KeyPickup, LockedGate
from lifecycle import LifeCycleManager, GameObject
from magic_map import Chunk
from mcswanson import McSwanson, Llama
from sprite import makeSprite
from theme_content import (
    JackieFlanBoss,
    LevodBurtimBoss,
    LucindaBoss,
    PippiBoss,
    ThemeBackdrop,
    VanProp,
    VesuviusBoss,
)


THEMED_LEVELS = {
    "farm.dill": {
        "theme": "farm",
        "story": "Escape Lucinda's farm: grab the sword, collect the key, break through the barn, and face Lucinda.",
        "boss": LucindaBoss,
        "autoscroll": False,
    },
    "river.dill": {
        "theme": "river",
        "story": "Follow the road to the van down by the river and survive Pippi's riverside ambush.",
        "boss": PippiBoss,
        "autoscroll": False,
    },
    "dojo.dill": {
        "theme": "dojo",
        "story": "Enter the karate dojo, unlock the inner floor, and fight Jackie Flan.",
        "boss": JackieFlanBoss,
        "autoscroll": False,
    },
    "space.dill": {
        "theme": "space",
        "story": "The ship is exploding. Keep moving through the dogfight and defeat Levod Burtim and the Writing Rainbomb.",
        "boss": LevodBurtimBoss,
        "autoscroll": True,
    },
    "pompeii.dill": {
        "theme": "pompeii",
        "story": "Vesuvius has erupted. Race through Pompeii's streets before the lava catches Kenny.",
        "boss": VesuviusBoss,
        "autoscroll": True,
    },
}


def _destroy_chunk_sprites(chunk):
    if hasattr(chunk, "contained_sprites"):
        for sprite in list(chunk.contained_sprites.values()):
            if hasattr(sprite, "destroy"):
                sprite.destroy()
    chunk.contained_sprites = {}


def _world_x(chunk, fraction):
    return int(max(64, chunk.width * EngineGlobals.tile_size * fraction))


def _customize_theme_platform(chunk, theme):
    """Give copied dill maps distinct gameplay layouts without changing map format."""
    if not chunk.platform or chunk.width < 12 or chunk.height < 5:
        return

    # Keep the underlying dill map, but alter a few safe cells in memory for each level.
    floor_row = chunk.height - 2
    upper_row = max(1, chunk.height - 5)
    theme_offset = {"farm": 3, "river": 5, "dojo": 7, "space": 9, "pompeii": 11}[theme]

    for x in range(theme_offset, chunk.width - 2, 13):
        chunk.platform[floor_row][x] = gamepieces.HazardBlock((x + theme_offset) % 12, True)

    for x in range(theme_offset + 4, chunk.width - 3, 17):
        chunk.platform[upper_row][x] = gamepieces.BreakableBlock((x + 2) % 12, True)
        if x + 1 < chunk.width:
            chunk.platform[upper_row][x + 1] = gamepieces.Block((x + 4) % 12, True)


def _build_themed_level(map_obj, definition):
    chunk = map_obj.chunks[0]
    _destroy_chunk_sprites(chunk)
    _customize_theme_platform(chunk, definition["theme"])

    map_obj.story = definition["story"]
    map_obj.autoscroll = definition["autoscroll"]
    map_obj.theme = definition["theme"]
    ThemeBackdrop(definition["theme"])

    # Common authored gameplay: enemies across the route and a boss near the far end.
    chunk.contained_sprites["enemy-1"] = makeSprite(Enemy, chunk, (_world_x(chunk, 0.28), 160))
    chunk.contained_sprites["enemy-2"] = makeSprite(Enemy, chunk, (_world_x(chunk, 0.58), 160))
    chunk.contained_sprites["boss"] = makeSprite(definition["boss"], chunk, (_world_x(chunk, 0.82), 96))

    if definition["theme"] == "farm":
        chunk.contained_sprites["sword"] = makeSprite(Sword, chunk, (_world_x(chunk, 0.12), 96))
        chunk.contained_sprites["key"] = makeSprite(KeyPickup, chunk, (_world_x(chunk, 0.38), 130))
        chunk.contained_sprites["gate"] = makeSprite(
            LockedGate, chunk, (_world_x(chunk, 0.70), 64), group="BACK", gate_id="farm-gate"
        )
    elif definition["theme"] == "river":
        chunk.contained_sprites["van"] = makeSprite(VanProp, chunk, (_world_x(chunk, 0.48), 96))
    elif definition["theme"] == "dojo":
        chunk.contained_sprites["key"] = makeSprite(KeyPickup, chunk, (_world_x(chunk, 0.32), 160))
        chunk.contained_sprites["gate"] = makeSprite(
            LockedGate, chunk, (_world_x(chunk, 0.68), 64), group="BACK", gate_id="dojo-gate"
        )
    elif definition["theme"] == "space":
        chunk.contained_sprites["fruit"] = makeSprite(NirvanaFruit, chunk, (_world_x(chunk, 0.45), 180))
    elif definition["theme"] == "pompeii":
        chunk.contained_sprites["scythe"] = makeSprite(gamepieces.Scythe, chunk, (_world_x(chunk, 0.20), 96))


def additional_map_definitions(map_obj):
    if hasattr(map_obj, "sprites"):
        for sprite in map_obj.sprites.values():
            sprite.destroy()
        del map_obj.sprites

    filename = getattr(map_obj, "filename", "map.dill")

    if filename in THEMED_LEVELS:
        _build_themed_level(map_obj, THEMED_LEVELS[filename])
        return

    if filename == "map.dill":
        chunk = map_obj.chunks[0]
        _destroy_chunk_sprites(chunk)
        if hasattr(map_obj, "talker"):
            map_obj.talker.destroy()
            del map_obj.talker

        chunk.contained_sprites["door"] = makeSprite(
            Door, chunk, (500, 10), group="BACK", target_map="bossfight.dill", player_position=(250, 250)
        )
        chunk.contained_sprites["door_mr_omen"] = makeSprite(
            Door, chunk, (1500, 40), group="BACK", target_map="boss_mr_omen.dill", player_position=(250, 250)
        )
        chunk.contained_sprites["scythe"] = makeSprite(gamepieces.Scythe, chunk, (300, 41))
        chunk.contained_sprites["spudguy"] = makeSprite(Enemy, chunk, (300, 250))
        chunk.contained_sprites["testfruit1"] = makeSprite(NirvanaFruit, chunk, (260, 50))
        chunk.contained_sprites["mcswanson1"] = makeSprite(McSwanson, chunk, (340, 200))
        chunk.contained_sprites["llama1"] = makeSprite(Llama, chunk, (600, 30))

    elif filename == "bossfight.dill":
        map_obj.image = "lighthouse.png"
        chunk = map_obj.chunks[0]
        _destroy_chunk_sprites(chunk)
        chunk.contained_sprites["pearlypaul"] = makeSprite(PearlyPaul, chunk, (0, 0))

    elif filename == "boss_mr_omen.dill":
        map_obj.image = "tonic_overwater.png"
        chunk = map_obj.chunks[0]
        _destroy_chunk_sprites(chunk)
        chunk.contained_sprites["mr_omen"] = makeSprite(MrOmen, chunk, (0, 0))


class GameMap:
    def __init__(self, chunks=None, filename="map.dill"):
        if not hasattr(self, "chunks") or not self.chunks:
            self.chunks = chunks
        self.filename = filename

        additional_map_definitions(self)

        if hasattr(self, "image"):
            bgimg = GameObject(lifecycle_manager="PER_MAP")
            bgimg.sprite = pyglet.sprite.Sprite(
                img=pyglet.resource.image(self.image),
                batch=EngineGlobals.main_batch,
                group=EngineGlobals.bg_group,
            )
            bgimg.on_finalDeletion = lambda: bgimg.sprite.delete()
            bgimg.updateloop = lambda dt: None

    def __setstate__(self, state):
        state.pop("filename", None)
        self.__dict__.update(state)

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("filename", None)
        return state

    @staticmethod
    def load_map(filename):
        LifeCycleManager.dropAllObjects("PER_MAP")
        if hasattr(EngineGlobals, "game_map"):
            for old_chunk in EngineGlobals.game_map.chunks:
                for row in old_chunk.platform:
                    for block in row:
                        if isinstance(block, gamepieces.Block) and hasattr(block, "sprite"):
                            block.sprite.delete()

        with open(filename, "rb") as handle:
            game_map = dill.load(handle)

        if hasattr(game_map, "platform"):
            game_map.chunks = [Chunk(platform=game_map.platform)]
            del game_map.platform

        for chunk in game_map.chunks:
            if not hasattr(chunk, "contained_sprites"):
                chunk.contained_sprites = {}
            for sprite in chunk.contained_sprites.values():
                sprite.current_chunk = chunk

        game_map.__init__(chunks=game_map.chunks, filename=filename)
        EngineGlobals.game_map = game_map
        if hasattr(EngineGlobals, "kenny"):
            EngineGlobals.kenny.current_chunk = game_map.chunks[0]
