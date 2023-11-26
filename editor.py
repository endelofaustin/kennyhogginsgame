#!/bin/python3

import pyglet, pickle, dill
from gamepieces import *
from pyglet.window import mouse
from engineglobals import EngineGlobals
from math import floor

class Editor():
    TILESHEET_WIDTH = 160
    TILESHEET_HEIGHT = 176

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
        tile_x = EngineGlobals.width + 4 + tile_idx % floor(EngineGlobals.TILESHEET_WIDTH / 16) * 32
        tile_y = floor(tile_idx / floor(EngineGlobals.TILESHEET_WIDTH / 16)) * 32
        self.selected_tile_overlay_sprite.x = tile_x
        self.selected_tile_overlay_sprite.y = tile_y
        self.selected_tile_idx = tile_idx

    def handle_tilesheet_click(self, x, y, button, modifiers):
        if x < EngineGlobals.width + 2 or x >= EngineGlobals.width + 2 + Editor.TILESHEET_WIDTH * EngineGlobals.scale_factor:
            return pyglet.event.EVENT_UNHANDLED
        if y < 0 or y >= Editor.TILESHEET_HEIGHT * EngineGlobals.scale_factor:
            return pyglet.event.EVENT_UNHANDLED
        tile_x = floor((x - EngineGlobals.width - 4) / 32)
        tile_y = floor(y / 32)
        tile_idx = tile_y * floor(EngineGlobals.TILESHEET_WIDTH / 16) + tile_x
        self.update_selected_tile(tile_idx)
        return pyglet.event.EVENT_HANDLED

    def handle_main_screen_click(self, x, y, button, modifiers):
        if x < 0 or x >= EngineGlobals.width or y < 0 or y > EngineGlobals.height:
            return pyglet.event.EVENT_UNHANDLED

        x_coord = floor((x + EngineGlobals.our_screen.x)/32)
        y_coord = len(EngineGlobals.game_map.platform) - 1 - floor((EngineGlobals.our_screen.y + y)/32)
        if EngineGlobals.game_map.platform[floor(y_coord)][floor(x_coord)] == 0:
            block = Block(self.selected_tile_idx, True)
            EngineGlobals.game_map.platform[floor(y_coord)][floor(x_coord)] = block
        else:
            if hasattr(EngineGlobals.game_map.platform[floor(y_coord)][floor(x_coord)], 'sprite'):
                EngineGlobals.game_map.platform[floor(y_coord)][floor(x_coord)].sprite.delete()
            EngineGlobals.game_map.platform[floor(y_coord)][floor(x_coord)] = 0
        return pyglet.event.EVENT_HANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_down_coords = (x, y)
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_release(self, x, y, button, modifiers):
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

        if symbol == pyglet.window.key.S and modifiers & pyglet.window.key.MOD_CTRL:
            
            with open(EngineGlobals.game_map.filename, 'wb') as f:
                dill.dump(EngineGlobals.game_map, f,)
            return pyglet.event.EVENT_HANDLED

        if symbol == pyglet.window.key.L and modifiers & pyglet.window.key.MOD_CTRL:

            with open('map.dill', 'rb') as f:
                EngineGlobals.game_map = dill.load(f)
            return pyglet.event.EVENT_HANDLED

        return pyglet.event.EVENT_UNHANDLED
