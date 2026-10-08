#!/bin/python3

import itertools
from math import floor

import dill
import pyglet

from engineglobals import EngineGlobals
from gamepieces import Block, BreakableBlock, Door, HazardBlock
from gameplay import KeyPickup, LockedGate
from enemies import Enemy
from spike import Spike
from sprite import makeSprite


class Editor:
    """In-game map editor.

    Number keys select what a click places:
      1 normal block, 2 hazard block, 3 breakable block,
      4 enemy, 5 door, 6 key, 7 locked gate, 8 spike.
    Ctrl+N clears the current chunk, Ctrl+S saves, Ctrl+L reloads map.dill.
    """

    _sprite_counter = itertools.count()

    def __init__(self):
        self.editor_bg_sprite = pyglet.sprite.Sprite(
            img=pyglet.resource.image("editor_bg.png"),
            x=EngineGlobals.width,
            y=0,
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_back,
        )
        self.editor_bg_sprite.update(scale=EngineGlobals.scale_factor)
        self.tilesheet_sprite = pyglet.sprite.Sprite(
            img=EngineGlobals.tilesheet,
            x=EngineGlobals.width + 4,
            y=0,
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_mid,
        )
        self.tilesheet_sprite.update(scale=EngineGlobals.scale_factor)
        self.tilesheet_grid_sprite = pyglet.sprite.Sprite(
            img=pyglet.resource.image("tilesheet_fg_grid.png"),
            x=EngineGlobals.width,
            y=0,
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self.tilesheet_grid_sprite.update(scale=EngineGlobals.scale_factor)
        self.selected_tile_overlay_sprite = pyglet.sprite.Sprite(
            img=pyglet.resource.image("selected_tile.png"),
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self.selected_tile_idx = 0
        self.update_selected_tile(0)
        self.selected_tool = "block"
        self.tool_label = pyglet.text.Label(
            "Tool: block (1)",
            x=EngineGlobals.width + 8,
            y=EngineGlobals.height - 24,
            font_size=10,
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self.mouse_down_coords = (0, 0)

    def updateloop(self, dt):
        pass

    def update_selected_tile(self, tile_idx):
        columns = floor(EngineGlobals.tilesheet.width / 16)
        tile_x = EngineGlobals.width + 4 + tile_idx % columns * EngineGlobals.tile_size
        tile_y = floor(tile_idx / columns) * EngineGlobals.tile_size
        self.selected_tile_overlay_sprite.x = tile_x
        self.selected_tile_overlay_sprite.y = tile_y
        self.selected_tile_idx = tile_idx

    def select_tool(self, tool, number):
        self.selected_tool = tool
        self.tool_label.text = "Tool: {} ({})".format(tool.replace("_", " "), number)

    def handle_tilesheet_click(self, x, y, button, modifiers):
        if x < EngineGlobals.width + 2 or x >= EngineGlobals.width + 2 + EngineGlobals.tilesheet.width * EngineGlobals.scale_factor:
            return pyglet.event.EVENT_UNHANDLED
        if y < 0 or y >= EngineGlobals.tilesheet.height * EngineGlobals.scale_factor:
            return pyglet.event.EVENT_UNHANDLED
        tile_x = floor((x - EngineGlobals.width - 4) / EngineGlobals.tile_size)
        tile_y = floor(y / EngineGlobals.tile_size)
        tile_idx = tile_y * floor(EngineGlobals.tilesheet.width / 16) + tile_x
        self.update_selected_tile(tile_idx)
        return pyglet.event.EVENT_HANDLED

    def _tile_coords(self, x, y):
        chunk = EngineGlobals.game_map.chunks[0]
        x_tile = floor((x + EngineGlobals.our_screen.x) / EngineGlobals.tile_size)
        y_tile = len(chunk.platform) - 1 - floor((EngineGlobals.our_screen.y + y) / EngineGlobals.tile_size)
        return chunk, x_tile, y_tile

    def _place_block(self, chunk, x_tile, y_tile, button):
        if not (0 <= y_tile < len(chunk.platform) and 0 <= x_tile < len(chunk.platform[0])):
            return
        solid = button == pyglet.window.mouse.LEFT
        block_type = {
            "block": Block,
            "hazard_block": HazardBlock,
            "breakable_block": BreakableBlock,
        }[self.selected_tool]
        existing = chunk.platform[y_tile][x_tile]
        if existing == 0:
            chunk.platform[y_tile][x_tile] = block_type(self.selected_tile_idx, solid)
            return
        if hasattr(existing, "sprite"):
            existing.sprite.delete()
        if getattr(existing, "solid", None) != solid or type(existing) is not block_type:
            chunk.platform[y_tile][x_tile] = block_type(self.selected_tile_idx, solid)
        else:
            chunk.platform[y_tile][x_tile] = 0

    def _place_sprite(self, x, y):
        chunk = EngineGlobals.game_map.chunks[0]
        world_pos = (
            int(x + EngineGlobals.our_screen.x),
            int(y + EngineGlobals.our_screen.y),
        )
        sprite_type = {
            "enemy": Enemy,
            "door": Door,
            "key": KeyPickup,
            "locked_gate": LockedGate,
            "spike": Spike,
        }[self.selected_tool]
        kwargs = {}
        if self.selected_tool == "door":
            kwargs = {"target_map": "bossfight.dill", "player_position": (250, 250), "group": "BACK"}
        elif self.selected_tool == "locked_gate":
            kwargs = {"gate_id": "editor-gate-{}".format(next(self._sprite_counter)), "group": "BACK"}
        sprite = makeSprite(sprite_type, chunk, world_pos, **kwargs)
        key = "editor-{}-{}".format(self.selected_tool, next(self._sprite_counter))
        chunk.contained_sprites[key] = sprite

    def handle_main_screen_click(self, x, y, button, modifiers):
        if x < 0 or x >= EngineGlobals.width or y < 0 or y > EngineGlobals.height:
            return pyglet.event.EVENT_UNHANDLED

        chunk, x_tile, y_tile = self._tile_coords(x, y)
        if self.selected_tool in ("block", "hazard_block", "breakable_block"):
            self._place_block(chunk, x_tile, y_tile, button)
        elif button == pyglet.window.mouse.LEFT:
            self._place_sprite(x, y)
        return pyglet.event.EVENT_HANDLED

    def clear_map(self):
        for chunk in EngineGlobals.game_map.chunks:
            for row_idx, row in enumerate(chunk.platform):
                for col_idx, block in enumerate(row):
                    if hasattr(block, "sprite"):
                        block.sprite.delete()
                    chunk.platform[row_idx][col_idx] = 0
            for sprite in list(chunk.contained_sprites.values()):
                sprite.destroy()
            chunk.contained_sprites.clear()

    def on_mouse_motion(self, x, y, dx, dy):
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        if EngineGlobals.show_menu:
            return pyglet.event.EVENT_UNHANDLED
        self.mouse_down_coords = (x, y)
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        if EngineGlobals.show_menu:
            return pyglet.event.EVENT_UNHANDLED
        if abs(x - self.mouse_down_coords[0]) > 4 or abs(y - self.mouse_down_coords[1]) > 4:
            return pyglet.event.EVENT_UNHANDLED
        if self.handle_tilesheet_click(x, y, button, modifiers) == pyglet.event.EVENT_HANDLED:
            return pyglet.event.EVENT_HANDLED
        return self.handle_main_screen_click(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        return pyglet.event.EVENT_UNHANDLED

    def on_key_release(self, symbol, modifiers):
        if EngineGlobals.show_menu:
            return pyglet.event.EVENT_UNHANDLED

        tools = {
            pyglet.window.key._1: ("block", 1),
            pyglet.window.key._2: ("hazard_block", 2),
            pyglet.window.key._3: ("breakable_block", 3),
            pyglet.window.key._4: ("enemy", 4),
            pyglet.window.key._5: ("door", 5),
            pyglet.window.key._6: ("key", 6),
            pyglet.window.key._7: ("locked_gate", 7),
            pyglet.window.key._8: ("spike", 8),
        }
        if symbol in tools:
            self.select_tool(*tools[symbol])
            return pyglet.event.EVENT_HANDLED

        if symbol == pyglet.window.key.S and modifiers & pyglet.window.key.MOD_CTRL:
            with open(EngineGlobals.game_map.filename, "wb") as save_file:
                dill.dump(EngineGlobals.game_map, save_file)
            return pyglet.event.EVENT_HANDLED

        if symbol == pyglet.window.key.L and modifiers & pyglet.window.key.MOD_CTRL:
            from maploader import GameMap
            GameMap.load_map("map.dill")
            return pyglet.event.EVENT_HANDLED

        if symbol == pyglet.window.key.N and modifiers & pyglet.window.key.MOD_CTRL:
            self.clear_map()
            return pyglet.event.EVENT_HANDLED

        return pyglet.event.EVENT_UNHANDLED
