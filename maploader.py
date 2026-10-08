import math

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
from theo_level import TheoTrailerEncounter


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
    width = max(1, chunk.width * EngineGlobals.tile_size)
    return int(chunk.coalesced_x + max(64, width * fraction))


def _is_solid(block):
    return block == 1 or bool(getattr(block, "solid", False))


def _safe_ground_y(chunk, world_x, actor_height=64):
    """Find a clear standing position over a real solid tile at world_x."""
    column = int((world_x - chunk.coalesced_x) // EngineGlobals.tile_size)
    column = max(0, min(chunk.width - 1, column))
    needed_air_rows = max(1, int(math.ceil(actor_height / EngineGlobals.tile_size)))

    for row in range(chunk.height - 1, -1, -1):
        floor_block = chunk.platform[row][column]
        if not _is_solid(floor_block) or isinstance(floor_block, gamepieces.HazardBlock):
            continue

        clear = True
        for offset in range(1, needed_air_rows + 1):
            above_row = row - offset
            if above_row >= 0 and _is_solid(chunk.platform[above_row][column]):
                clear = False
                break
        if not clear:
            continue

        floor_world_y = chunk.coalesced_y + (chunk.height - 1 - row) * EngineGlobals.tile_size
        return int(floor_world_y + EngineGlobals.tile_size + 1)

    return int(chunk.coalesced_y + EngineGlobals.tile_size * 2)


def _safe_position(chunk, fraction, actor_height=64):
    """Find a usable X/Y near a desired fraction of the chunk."""
    preferred_column = int(max(1, min(chunk.width - 2, chunk.width * fraction)))
    search_columns = list(range(preferred_column, chunk.width - 1)) + list(range(preferred_column - 1, 0, -1))

    for column in search_columns:
        world_x = int(chunk.coalesced_x + column * EngineGlobals.tile_size + 2)
        world_y = _safe_ground_y(chunk, world_x, actor_height)
        floor_row = chunk.height - int((world_y - chunk.coalesced_y) / EngineGlobals.tile_size)
        if 0 <= floor_row < chunk.height:
            floor_block = chunk.platform[floor_row][column]
            if isinstance(floor_block, gamepieces.HazardBlock):
                continue
        return (world_x, world_y)

    return (int(chunk.coalesced_x + 64), int(chunk.coalesced_y + 96))


def _replace_tile(chunk, row, column, new_block):
    old_block = chunk.platform[row][column]
    if isinstance(old_block, gamepieces.Block) and hasattr(old_block, "sprite"):
        old_block.sprite.delete()
    chunk.platform[row][column] = new_block


def _customize_theme_platform(chunk, theme):
    """Give copied dill maps distinct gameplay layouts without changing map format."""
    if not chunk.platform or chunk.width < 12 or chunk.height < 5:
        return

    floor_row = chunk.height - 2
    upper_row = max(1, chunk.height - 5)
    theme_offset = {"farm": 3, "river": 5, "dojo": 7, "space": 9, "pompeii": 11}[theme]

    for x in range(max(theme_offset, 7), chunk.width - 2, 13):
        _replace_tile(chunk, floor_row, x, gamepieces.HazardBlock((x + theme_offset) % 12, True))

    for x in range(theme_offset + 4, chunk.width - 3, 17):
        _replace_tile(chunk, upper_row, x, gamepieces.BreakableBlock((x + 2) % 12, True))
        if x + 1 < chunk.width:
            _replace_tile(chunk, upper_row, x + 1, gamepieces.Block((x + 4) % 12, True))


def _spawn(chunk, key, sprite_type, fraction, actor_height=64, **kwargs):
    position = _safe_position(chunk, fraction, actor_height)
    chunk.contained_sprites[key] = makeSprite(sprite_type, chunk, position, **kwargs)
    return chunk.contained_sprites[key]


def _build_themed_level(map_obj, definition):
    chunk = map_obj.chunks[0]
    _destroy_chunk_sprites(chunk)
    _customize_theme_platform(chunk, definition["theme"])

    map_obj.story = definition["story"]
    map_obj.autoscroll = definition["autoscroll"]
    map_obj.theme = definition["theme"]
    map_obj.player_spawn = _safe_position(chunk, 0.06, actor_height=64)
    ThemeBackdrop(definition["theme"])

    _spawn(chunk, "enemy-1", Enemy, 0.28, actor_height=48)
    _spawn(chunk, "enemy-2", Enemy, 0.58, actor_height=48)
    _spawn(chunk, "boss", definition["boss"], 0.82, actor_height=80)

    if definition["theme"] == "farm":
        _spawn(chunk, "sword", Sword, 0.12, actor_height=32)
        _spawn(chunk, "key", KeyPickup, 0.38, actor_height=32)
        _spawn(chunk, "gate", LockedGate, 0.70, actor_height=64, group="BACK", gate_id="farm-gate")
    elif definition["theme"] == "river":
        _spawn(chunk, "van", VanProp, 0.48, actor_height=64)
    elif definition["theme"] == "dojo":
        _spawn(chunk, "key", KeyPickup, 0.32, actor_height=32)
        _spawn(chunk, "gate", LockedGate, 0.68, actor_height=64, group="BACK", gate_id="dojo-gate")
    elif definition["theme"] == "space":
        _spawn(chunk, "fruit", NirvanaFruit, 0.45, actor_height=32)
    elif definition["theme"] == "pompeii":
        _spawn(chunk, "scythe", gamepieces.Scythe, 0.20, actor_height=32)


def _build_theo_level(map_obj):
    """Build Theo's trailer yard around the existing dill map geometry."""
    chunk = map_obj.chunks[0]
    _destroy_chunk_sprites(chunk)

    map_obj.story = "Kenny reaches Cousin Theo's trailer. Cross the sand, walk to the table, press D, then mash C to win the arm-wrestling match."
    map_obj.autoscroll = False
    map_obj.theme = "theo"
    map_obj.player_spawn = _safe_position(chunk, 0.06, actor_height=64)

    desired_table_x = int(map_obj.player_spawn[0] + 300)
    max_table_x = int(chunk.coalesced_x + (chunk.width - 3) * EngineGlobals.tile_size)
    table_x = min(desired_table_x, max_table_x)
    table_y = _safe_ground_y(chunk, table_x, actor_height=64)
    encounter = TheoTrailerEncounter(chunk, map_obj.player_spawn, (table_x, table_y))
    for shape, _, _ in encounter.world_shapes:
        if getattr(shape, "group", None) is EngineGlobals.editor_group_mid:
            shape.group = EngineGlobals.bg_group
    map_obj.theo_encounter = encounter


def additional_map_definitions(map_obj):
    if hasattr(map_obj, "sprites"):
        for sprite in map_obj.sprites.values():
            sprite.destroy()
        del map_obj.sprites

    filename = getattr(map_obj, "filename", "map.dill")

    if filename == "theo.dill":
        _build_theo_level(map_obj)
        return

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


def _delete_map_block_sprites(map_obj):
    if map_obj is None or not hasattr(map_obj, "chunks"):
        return
    for chunk in map_obj.chunks:
        for row in getattr(chunk, "platform", []):
            for block in row:
                if isinstance(block, gamepieces.Block) and hasattr(block, "sprite"):
                    try:
                        block.sprite.delete()
                    except Exception:
                        pass


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
        """Load a dill map without corrupting the current map if construction fails."""
        old_map = getattr(EngineGlobals, "game_map", None)
        LifeCycleManager.dropAllObjects("PER_MAP")
        game_map = None

        try:
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
        except Exception:
            LifeCycleManager.dropAllObjects("PER_MAP")
            _delete_map_block_sprites(game_map)
            raise

        _delete_map_block_sprites(old_map)
        EngineGlobals.game_map = game_map
        if hasattr(EngineGlobals, "kenny"):
            EngineGlobals.kenny.current_chunk = game_map.chunks[0]
