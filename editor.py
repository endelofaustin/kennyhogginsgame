#!/bin/python3

import pyglet
from pyglet.window import mouse
from engineglobals import EngineGlobals

class Editor():


    def on_mouse_press(self, x, y, button, modifiers):
        print("{} pressed at: {},{}".format(button, x, y))
        x_coord = (x + EngineGlobals.our_screen.x)/32 
        y_coord = (len(EngineGlobals.platform) - (EngineGlobals.our_screen.y + y)/32)
        if EngineGlobals.platform[int(y_coord)][int(x_coord)] == 0:
            EngineGlobals.platform[int(y_coord)][int(x_coord)] = 1
        else:
            EngineGlobals.platform[int(y_coord)][int(x_coord)] = 0
            
    def on_mouse_motion(self,x, y, dx, dy):
        print(x, y) 
    
    def on_mouse_release(self,x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            pass



