#!/bin/python3

import pyglet, pickle, dill
from gamepieces import *
from pyglet.window import mouse
from engineglobals import EngineGlobals
from math import floor

class Editor():

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


