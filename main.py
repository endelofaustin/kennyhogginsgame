#!/usr/bin/python3

"""Kenny Hoggins game bootstrap and main update/render loop."""

import os
import time
from decimal import Decimal, getcontext

import pyglet

import editor as editor_module
import gamepieces
import physics
import player
from engineglobals import EngineGlobals
from gameplay import AutoScroller, GameProgress, PuzzleController, SaveGame
from lifecycle import LifeCycleManager
from magic_map import ChunkEdge
from maploader import GameMap
from menu import GameMenu
from sprite import makeSprite
from text import IntroMode


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
pyglet.resource.path = [PROJECT_ROOT, os.path.join(PROJECT_ROOT, "audio"), os.path.join(PROJECT_ROOT, "artwork")]
pyglet.resource.reindex()
getcontext().prec = 7


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

EngineGlobals.window.push_handlers(kenny)
EngineGlobals.window.push_handlers(editor)
EngineGlobals.window.push_handlers(intro)
EngineGlobals.window.push_handlers(puzzle)
LifeCycleManager.ALL_SETS["UNDYING"].addGameObject(editor)
LifeCycleManager.ALL_SETS["UNDYING"].addGameObject(screen)


EngineGlobals.textsurface = pyglet.text.Label(
    text="Arrow keys move | Ctrl/Up jump | Space shoot | C slash | D interact | P puzzle | F5 save | F9 load",
    color=(255, 0, 255, 255),
    batch=EngineGlobals.main_batch,
    y=EngineGlobals.height,
    anchor_y="top",
)


def new_game():
    EngineGlobals.progress = GameProgress()
    kenny.progress = EngineGlobals.progress
    puzzle.progress = EngineGlobals.progress
    GameMap.load_map("map.dill")
    kenny.x_position, kenny.y_position = Decimal(0), Decimal(200)
    kenny.has_sword = False
    kenny.has_scythe = False
    intro.start()


def load_game():
    progress, state = SaveGame.load()
    EngineGlobals.progress = progress
    kenny.progress = progress
    puzzle.progress = progress
    if state:
        target_map = state.get("map", "map.dill")
        GameMap.load_map(target_map)
        kenny.x_position = Decimal(str(state.get("x", 0)))
        kenny.y_position = Decimal(str(state.get("y", 200)))
        kenny.has_sword = bool(state.get("has_sword", False))
        kenny.has_scythe = bool(state.get("has_scythe", False))
    EngineGlobals.game_mode = "PLAY"


menu = GameMenu(on_new_game=new_game, on_load_game=load_game)
EngineGlobals.window.push_handlers(menu)


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
                    onscreen = not (
                        xrender_start + EngineGlobals.tile_size <= 0
                        or xrender_start >= EngineGlobals.width
                        or yrender_start + EngineGlobals.tile_size <= 0
                        or yrender_start >= EngineGlobals.height
                    )
                    block.sprite.visible = onscreen
                    if onscreen:
                        block.sprite.x = EngineGlobals.pixel_coord(xrender_start)
                        block.sprite.y = EngineGlobals.pixel_coord(yrender_start)
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


def main_update_callback(dt):
    scaled_dt = dt * 60
    now = time.perf_counter_ns()
    elapsed = max(1, now - EngineGlobals.last_sim)
    EngineGlobals.sim_fps = int(1_000_000_000 / elapsed)
    EngineGlobals.last_sim = now

    physics.PhysicsSprite.collision_lists.clear()
    LifeCycleManager.processUpdates(scaled_dt)
    update_visible_chunks()


pyglet.clock.schedule_interval(main_update_callback, 1 / 60.0)


@EngineGlobals.window.event
def on_key_press(symbol, modifiers):
    # A toggles the optional autoscroller challenge for testing/maps.
    if symbol == pyglet.window.key.A and not EngineGlobals.show_menu:
        if autoscroller.active:
            autoscroller.stop()
        else:
            autoscroller.start()


@EngineGlobals.window.event
def on_draw():
    if EngineGlobals.show_menu:
        menu.on_draw()
        return

    EngineGlobals.window.clear()
    now = time.perf_counter_ns()
    elapsed = max(1, now - EngineGlobals.last_render)
    EngineGlobals.render_fps = int(1_000_000_000 / elapsed)
    EngineGlobals.last_render = now
    EngineGlobals.textsurface.text = (
        "render fps: {} | sim fps: {} | keys: {}".format(
            EngineGlobals.render_fps,
            EngineGlobals.sim_fps,
            EngineGlobals.progress.keys,
        )
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
