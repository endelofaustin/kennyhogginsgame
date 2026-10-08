#!/usr/bin/python3

"""Kenny Hoggins game bootstrap and main update/render loop."""

import os
import sys
import time
from decimal import Decimal, getcontext

MIN_PYTHON = (3, 10)
if sys.version_info < MIN_PYTHON:
    raise SystemExit(
        "Kenny Hoggins Game requires Python 3.10 or newer. "
        "This interpreter is Python {}.{}. Recreate .venv with Python 3.10+.".format(
            sys.version_info.major, sys.version_info.minor
        )
    )

import pyglet

import editor as editor_module
import gamepieces
import maploader as maploader_module
import physics
import player
from engineglobals import EngineGlobals
from gameplay import AutoScroller, GameProgress, PuzzleController, SaveGame
from karts_mode import KartsMode
from ketchup_install import install_ketchup_boss
from lifecycle import LifeCycleManager
from magic_map import ChunkEdge
from maploader import GameMap
from menu import GameMenu
from mode7_full_game import FullMode7Racing
from sprite import makeSprite
from text import IntroMode
from toga_sisters import TogaSistersBoss, install_toga_sisters

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
pyglet.resource.path = [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "audio"), os.path.join(PROJECT_ROOT, "artwork")]
pyglet.resource.reindex()
getcontext().prec = 7
install_toga_sisters()
install_ketchup_boss()
# Pompeii's authored builder names the legacy boss class directly, so replace
# that module global too. The rest of the dill/map-loader architecture stays intact.
maploader_module.VesuviusBoss = TogaSistersBoss
pompeii_stages = list(maploader_module.PompeiiDirector.STAGES)
pompeii_stages[-1] = (
    Decimal("0.82"),
    "V  THE TOGA SISTERS",
    "Lava chase cleared. Cross the pit and break the singing trio.",
    Decimal("0"),
)
maploader_module.PompeiiDirector.STAGES = tuple(pompeii_stages)

EngineGlobals.init()
LifeCycleManager.init()
EngineGlobals.game_mode = "MENU"
EngineGlobals.progress = GameProgress()

screen = physics.Screen()
GameMap.load_map("map.dill")
kenny = makeSprite(
    player.Player,
    EngineGlobals.game_map.chunks[0],
    (0, 200),
    lifecycle_manager="UNDYING",
    group="FRONT",
)
EngineGlobals.kenny = kenny
EngineGlobals.our_screen = screen

editor = editor_module.Editor()
intro = IntroMode()
puzzle = PuzzleController(EngineGlobals.progress)
autoscroller = AutoScroller()
autoscroller.scroll_x = Decimal(0)
EngineGlobals.autoscroller = autoscroller

EngineGlobals.window.push_handlers(kenny)
EngineGlobals.window.push_handlers(editor)
EngineGlobals.window.push_handlers(intro)
EngineGlobals.window.push_handlers(puzzle)
LifeCycleManager.ALL_SETS["UNDYING"].addGameObject(editor)
LifeCycleManager.ALL_SETS["UNDYING"].addGameObject(screen)

EngineGlobals.textsurface = pyglet.text.Label(
    text="Arrow keys move | Ctrl/Up jump | Space butt-shot | C slash | D interact | P puzzle | F5 save | F9 load",
    color=(255, 0, 255, 255),
    batch=EngineGlobals.main_batch,
    y=EngineGlobals.height,
    anchor_y="top",
)


def reset_new_game_progress():
    EngineGlobals.progress = GameProgress()
    kenny.progress = EngineGlobals.progress
    puzzle.progress = EngineGlobals.progress
    kenny.has_sword = False
    kenny.has_scythe = False
    kenny.bloody = False
    if hasattr(kenny, "reset_at"):
        kenny.reset_at(0, 200)
    autoscroller.stop()


def start_autoscroller():
    autoscroller.scroll_x = Decimal(str(screen.x))
    autoscroller.start()


def start_level(filename):
    """Start one of the selectable authored dill maps."""
    EngineGlobals.game_mode = "PLAY"
    GameMap.load_map(filename)
    kenny.current_chunk = EngineGlobals.game_map.chunks[0]
    spawn_x, spawn_y = getattr(EngineGlobals.game_map, "player_spawn", (64, 200))
    kenny.reset_at(spawn_x, spawn_y)
    screen.x = max(0, Decimal(str(spawn_x)) - Decimal(120))
    screen.y = max(0, Decimal(str(spawn_y)) - Decimal(96))

    if getattr(EngineGlobals.game_map, "autoscroll", False):
        start_autoscroller()
    else:
        autoscroller.stop()

    story = getattr(EngineGlobals.game_map, "story", "Kenny has somewhere else to be.")
    intro.start("KENNY HOGGINS\n\n" + story + "\n\nPress any key to begin.")


def load_game():
    progress, state = SaveGame.load()
    EngineGlobals.progress = progress
    kenny.progress = progress
    puzzle.progress = progress
    if state:
        target_map = state.get("map", "map.dill")
        GameMap.load_map(target_map)
        kenny.current_chunk = EngineGlobals.game_map.chunks[0]
        kenny.reset_at(state.get("x", 0), state.get("y", 200))
        kenny.has_sword = bool(state.get("has_sword", False))
        kenny.has_scythe = bool(state.get("has_scythe", False))
        screen.x = max(0, Decimal(str(kenny.x_position)) - Decimal(120))
        screen.y = max(0, Decimal(str(kenny.y_position)) - Decimal(96))
        if getattr(EngineGlobals.game_map, "autoscroll", False):
            start_autoscroller()
        else:
            autoscroller.stop()
    EngineGlobals.game_mode = "PLAY"


def return_to_main_menu():
    EngineGlobals.game_mode = "MENU"
    EngineGlobals.show_menu = True
    menu.screen = "main"
    menu._update_visibility()


karts = KartsMode(on_exit_to_menu=return_to_main_menu)
racing3d = FullMode7Racing(on_exit_to_menu=return_to_main_menu)


def start_karts():
    autoscroller.stop()
    racing3d.stop()
    EngineGlobals.game_mode = "KARTS"
    EngineGlobals.show_menu = False
    karts.start()


def start_3d_reaching():
    autoscroller.stop()
    karts.stop()
    EngineGlobals.game_mode = "RACING3D"
    EngineGlobals.show_menu = False
    racing3d.start()


menu = GameMenu(
    on_new_game=reset_new_game_progress,
    on_load_game=load_game,
    on_level_selected=start_level,
    on_karts_selected=start_karts,
    on_3d_selected=start_3d_reaching,
)
EngineGlobals.window.push_handlers(menu)


class ArcadeInputRouter:
    """Route alternate-game controls before platformer handlers can see them."""

    def on_key_press(self, symbol, modifiers):
        if EngineGlobals.game_mode == "KARTS":
            EngineGlobals.keys[symbol] = True
            return karts.on_key_press(symbol, modifiers)
        if EngineGlobals.game_mode == "RACING3D":
            return racing3d.on_key_press(symbol, modifiers)
        return pyglet.event.EVENT_UNHANDLED

    def on_key_release(self, symbol, modifiers):
        if EngineGlobals.game_mode == "KARTS":
            EngineGlobals.keys[symbol] = False
            return karts.on_key_release(symbol, modifiers)
        if EngineGlobals.game_mode == "RACING3D":
            return racing3d.on_key_release(symbol, modifiers)
        return pyglet.event.EVENT_UNHANDLED


arcade_input = ArcadeInputRouter()
EngineGlobals.window.push_handlers(arcade_input)


def update_chunk_tile_coords(chunk):
    """Position visible map tiles relative to the camera."""
    xstart = int(max(screen.x - chunk.coalesced_x, 0) / EngineGlobals.tile_size) - 1
    xend = int(min(screen.x + EngineGlobals.width, screen.x + chunk.width * EngineGlobals.tile_size) / EngineGlobals.tile_size) + 2
    ystart = chunk.height - int(max(screen.y - chunk.coalesced_y, 0) / EngineGlobals.tile_size)
    yend = chunk.height - int(min(screen.y + EngineGlobals.height, screen.y + chunk.height * EngineGlobals.tile_size) / EngineGlobals.tile_size) - 3

    xrender_start = int((chunk.coalesced_x + xstart * EngineGlobals.tile_size) - screen.x)
    yrender_start = int((chunk.coalesced_y + (chunk.height - ystart - 1) * EngineGlobals.tile_size) - screen.y)

    for xcounter in range(xstart, xend):
        for ycounter in range(ystart, yend, -1):
            if 0 <= xcounter < len(chunk.platform[0]) and 0 <= ycounter < len(chunk.platform):
                block = chunk.platform[ycounter][xcounter]
                if isinstance(block, gamepieces.Block):
                    sprite = getattr(block, "sprite", None)
                    if sprite is None or getattr(sprite, "image", None) is None:
                        yrender_start += EngineGlobals.tile_size
                        continue
                    onscreen = not (
                        xrender_start + EngineGlobals.tile_size <= 0
                        or xrender_start >= EngineGlobals.width
                        or yrender_start + EngineGlobals.tile_size <= 0
                        or yrender_start >= EngineGlobals.height
                    )
                    sprite.visible = onscreen
                    if onscreen:
                        sprite.x = EngineGlobals.pixel_coord(xrender_start)
                        sprite.y = EngineGlobals.pixel_coord(yrender_start)
            yrender_start += EngineGlobals.tile_size
        xrender_start += EngineGlobals.tile_size
        yrender_start = int((chunk.coalesced_y + (chunk.height - ystart - 1) * EngineGlobals.tile_size) - screen.y)


def update_visible_chunks():
    update_chunk_tile_coords(kenny.current_chunk)
    for edge in (ChunkEdge.LEFT, ChunkEdge.RIGHT, ChunkEdge.TOP, ChunkEdge.BOTTOM):
        chunk = kenny.current_chunk
        while edge in chunk.adjacencies:
            chunk = chunk.adjacencies[edge]
            if chunk.hidden:
                break
            if edge == ChunkEdge.LEFT and chunk.coalesced_x + chunk.width * EngineGlobals.tile_size < screen.x:
                break
            if edge == ChunkEdge.RIGHT and chunk.coalesced_x > screen.x + EngineGlobals.width:
                break
            if edge == ChunkEdge.TOP and chunk.coalesced_y > screen.y + EngineGlobals.height:
                break
            if edge == ChunkEdge.BOTTOM and chunk.coalesced_y + chunk.height * EngineGlobals.tile_size < screen.y:
                break
            update_chunk_tile_coords(chunk)


def update_autoscroller(scaled_dt):
    if not autoscroller.active or EngineGlobals.game_mode != "PLAY" or kenny.is_dead:
        return

    autoscroller.scroll_x += autoscroller.speed * Decimal(str(scaled_dt))
    if Decimal(str(screen.x)) < autoscroller.scroll_x:
        screen.x = autoscroller.scroll_x

    if Decimal(kenny.x_position) < Decimal(str(screen.x)) - Decimal(24):
        kenny.die_hard()
        autoscroller.stop()


def main_update_callback(dt):
    scaled_dt = dt * 60
    now = time.perf_counter_ns()
    elapsed = max(1, now - EngineGlobals.last_sim)
    EngineGlobals.sim_fps = int(1_000_000_000 / elapsed)
    EngineGlobals.last_sim = now

    if EngineGlobals.game_mode == "KARTS":
        karts.update(scaled_dt)
        return
    if EngineGlobals.game_mode == "RACING3D":
        racing3d.update(scaled_dt)
        return

    physics.PhysicsSprite.collision_lists.clear()
    LifeCycleManager.processUpdates(scaled_dt)
    update_autoscroller(scaled_dt)
    update_visible_chunks()


pyglet.clock.schedule_interval(main_update_callback, 1 / 60.0)


@EngineGlobals.window.event
def on_key_press(symbol, modifiers):
    if EngineGlobals.game_mode != "PLAY":
        return
    if symbol == pyglet.window.key.A and not EngineGlobals.show_menu:
        if autoscroller.active:
            autoscroller.stop()
        else:
            start_autoscroller()


@EngineGlobals.window.event
def on_draw():
    if EngineGlobals.show_menu:
        menu.on_draw()
        return

    if EngineGlobals.game_mode == "KARTS":
        EngineGlobals.window.clear()
        karts.draw()
        return

    if EngineGlobals.game_mode == "RACING3D":
        EngineGlobals.window.clear()
        racing3d.draw()
        return

    EngineGlobals.window.clear()
    now = time.perf_counter_ns()
    elapsed = max(1, now - EngineGlobals.last_render)
    EngineGlobals.render_fps = int(1_000_000_000 / elapsed)
    EngineGlobals.last_render = now
    EngineGlobals.textsurface.text = "render fps: {} | sim fps: {} | keys: {}".format(
        EngineGlobals.render_fps,
        EngineGlobals.sim_fps,
        EngineGlobals.progress.keys,
    )
    EngineGlobals.main_batch.draw()
    intro.on_draw()


EngineGlobals.audio_player = pyglet.media.Player()
for music in [
    "rap1.wav",
    "sleeponit.wav",
    "stronglengthypunkbrawl.wav",
    "takingahike.wav",
    "downrightbirthright.wav",
    "workingwithmagic.wav",
]:
    EngineGlobals.audio_player.queue(pyglet.resource.media(music, streaming=False))

if __name__ == "__main__":
    pyglet.app.run()

EngineGlobals.audio_player.delete()
