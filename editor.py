#!/bin/python3

import pyglet, pickle, dill
from gamepieces import *
from pyglet.window import mouse
from engineglobals import EngineGlobals
from math import floor

class Editor():

    def __init__(self,):
        self.editor_bg_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('editor_bg.png'),
                                                     x=EngineGlobals.width, y=0,
                                                     batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_back)
        self.editor_bg_sprite.update(scale=EngineGlobals.scale_factor)
        self.tilesheet_sprite = pyglet.sprite.Sprite(img=EngineGlobals.tilesheet,
                                                     x=EngineGlobals.width + 4, y=0,
                                                     batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_mid)
        self.tilesheet_sprite.update(scale=EngineGlobals.scale_factor)
        self.tilesheet_grid_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('tilesheet_fg_grid.png'),
                                                     x=EngineGlobals.width, y=0,
                                                     batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_front)
        self.tilesheet_grid_sprite.update(scale=EngineGlobals.scale_factor)
        self.selected_tile_overlay_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('selected_tile.png'),
                                                                 batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_front)
        #self.selected_tile_overlay_sprite.update(scale=EngineGlobals.scale_factor)
        self.mouse_dragged_before_release = False
        self.selected_tile_idx = 0
        self.update_selected_tile(0)

        self.mouse_down_coords = (0, 0)

    def updateloop(self, dt):
        pass

    def update_selected_tile(self, tile_idx):
        tile_x = EngineGlobals.width + 4 + tile_idx % floor(EngineGlobals.tilesheet.width / 16) * EngineGlobals.tile_size
        tile_y = floor(tile_idx / floor(EngineGlobals.tilesheet.width / 16)) * EngineGlobals.tile_size
        self.selected_tile_overlay_sprite.x = tile_x
        self.selected_tile_overlay_sprite.y = tile_y
        self.selected_tile_idx = tile_idx

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

    def handle_main_screen_click(self, x, y, button, modifiers):
        if x < 0 or x >= EngineGlobals.width or y < 0 or y > EngineGlobals.height:
            return pyglet.event.EVENT_UNHANDLED

        # if a tile is already present, right-click moves it to background or clears it
        # if already in background.
        # if a tile is already present, left-click moves it to foreground or clears it
        # if already in foreground.
        # if no tile is present, right-clicking places a background non-colliding tile
        # if no tile is present, left-clicking places a foreground solid tile
        solid = True if button == pyglet.window.mouse.LEFT else False

        x_tile = floor((x + EngineGlobals.our_screen.x)/EngineGlobals.tile_size)
        y_tile = len(EngineGlobals.game_map.chunks[0].platform) - 1 - floor((EngineGlobals.our_screen.y + y)/EngineGlobals.tile_size)

        if EngineGlobals.game_map.chunks[0].platform[y_tile][x_tile] == 0:
            block = Block(self.selected_tile_idx, solid)
            EngineGlobals.game_map.chunks[0].platform[y_tile][x_tile] = block
        else:
            if hasattr(EngineGlobals.game_map.chunks[0].platform[y_tile][x_tile], 'sprite'):
                EngineGlobals.game_map.chunks[0].platform[y_tile][x_tile].sprite.delete()
                if EngineGlobals.game_map.chunks[0].platform[y_tile][x_tile].solid != solid:
                    EngineGlobals.game_map.chunks[0].platform[y_tile][x_tile] = Block(self.selected_tile_idx, solid)
                else:
                    EngineGlobals.game_map.chunks[0].platform[y_tile][x_tile] = 0
            else:
                EngineGlobals.game_map.chunks[0].platform[y_tile][x_tile] = 0

        return pyglet.event.EVENT_HANDLED

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

        # don't do anything if it was a mouse drag
        # drag is a click that is greater than four 
        if abs(x - self.mouse_down_coords[0]) > 4 or abs(y - self.mouse_down_coords[1]) > 4:
            return pyglet.event.EVENT_UNHANDLED
        # see if the click is happening in the right side editor or in the main map
        if self.handle_tilesheet_click(x, y, button, modifiers) == pyglet.event.EVENT_HANDLED:
            return pyglet.event.EVENT_HANDLED
        if self.handle_main_screen_click(x, y, button, modifiers) == pyglet.event.EVENT_HANDLED:
            return pyglet.event.EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        return pyglet.event.EVENT_UNHANDLED

    def on_key_release(self, symbol, modifiers,):

        if EngineGlobals.show_menu:
            return pyglet.event.EVENT_UNHANDLED

        if symbol == pyglet.window.key.S and modifiers & pyglet.window.key.MOD_CTRL:
            
            with open(EngineGlobals.game_map.filename, 'wb') as f:
                dill.dump(EngineGlobals.game_map, f,)
            return pyglet.event.EVENT_HANDLED

        if symbol == pyglet.window.key.L and modifiers & pyglet.window.key.MOD_CTRL:

            with open('map.dill', 'rb') as f:
                EngineGlobals.game_map = dill.load(f)
            return pyglet.event.EVENT_HANDLED

        return pyglet.event.EVENT_UNHANDLED
