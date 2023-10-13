#!/bin/python3

import pyglet, pickle, dill
from gamepieces import *
from pyglet.window import mouse
from engineglobals import EngineGlobals
from math import floor

class Editor():
    TILESHEET_WIDTH = 160

    def __init__(self,):
        self.editor_bg_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('editor_bg.png'),
                                                     x=EngineGlobals.width, y=0,
                                                     batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_back)
        self.editor_bg_sprite.update(scale=EngineGlobals.scale_factor)
        self.tilesheet = pyglet.resource.image('plagiarism.png')
        self.tilesheet_sprite = pyglet.sprite.Sprite(img=self.tilesheet,
                                                     x=EngineGlobals.width + 2, y=0,
                                                     batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_mid)
        self.tilesheet_sprite.update(scale=EngineGlobals.scale_factor * 2)
        self.tilesheet_as_grid = pyglet.image.TextureGrid(pyglet.image.ImageGrid(self.tilesheet, 11, 10))
        self.tilesheet_grid_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('tilesheet_fg_grid.png'),
                                                     x=EngineGlobals.width, y=0,
                                                     batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_front)
        self.tilesheet_grid_sprite.update(scale=EngineGlobals.scale_factor)

    def updateloop(self, dt):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        # commented out the below print statement since this appears to be working
        # print("{} pressed at: {},{}".format(button, x, y))
        x_coord = floor((x + EngineGlobals.our_screen.x)/32)
        y_coord = len(EngineGlobals.platform) - 1 - floor((EngineGlobals.our_screen.y + y)/32)
        if EngineGlobals.platform[floor(y_coord)][floor(x_coord)] == 0:
            block = Block(1, True)
            EngineGlobals.platform[floor(y_coord)][floor(x_coord)] = block
        else:
            if hasattr(EngineGlobals.platform[floor(y_coord)][floor(x_coord)], 'sprite'):
                EngineGlobals.platform[floor(y_coord)][floor(x_coord)].sprite.delete()
            EngineGlobals.platform[floor(y_coord)][floor(x_coord)] = 0

    def on_mouse_motion(self,x, y, dx, dy):
        # commented out the below print statement since this appears to be working
        #print(x, y) 
        pass

    def on_mouse_release(self,x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        #commented the below out because it caused exception
        #if buttons & mouse.left:
        pass

    def on_key_release(self, symbol, modifiers,):

        if symbol == pyglet.window.key.S and modifiers & pyglet.window.key.MOD_CTRL:
            
            with open('map.dill', 'wb') as f:
                dill.dump(EngineGlobals.platform, f,)

        if symbol == pyglet.window.key.L and modifiers & pyglet.window.key.MOD_CTRL:

            with open('map.dill', 'rb') as f:
                EngineGlobals.platform = dill.load(f)
