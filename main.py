#!/usr/bin/python3

import sys, pyglet, physics, player, editor, pickle
from engineglobals import EngineGlobals
from decimal import getcontext, Decimal

# set Decimal precision to 7 places, much more efficient than the default 28
# 6 places is enough for 1 million pixels of accuracy, which is enough to
# precisely locate any position in an area that is 900 screens high and 1300
# screens wide, for a screen size up to 1024x768
getcontext().prec = 7

# run the init function to set up the game engine
EngineGlobals.init()
screen = physics.Screen()


# create some debug text to be rendered
EngineGlobals.textsurface = pyglet.text.Label(text='Arrow keys move and Ctrl or Up to jump', color=(255, 0, 255, 255),
                                batch=EngineGlobals.main_batch, y=EngineGlobals.height, anchor_y='top')

# load kenny sprite
kenny = player.Player()
mouse_events = editor.Editor()
EngineGlobals.window.push_handlers(kenny)
EngineGlobals.window.push_handlers(mouse_events)

# When adding to this list we are beginning to setup changable objects
# any object in this list will have its update function called
game_objects = [kenny, screen]

# this function will be set up for pyglet to call it every update cycle, 120 times per second
# it simply calls the updated function for every object in game_objects
def main_update_callback(dt):
    for obj in game_objects:
        obj.updateloop(dt)
# ask pyglet to call our main_update_callback 120 times per second
pyglet.clock.schedule_interval(main_update_callback, 1/120.0)
# set up some color values and create a white rectangle to white out the screen
WHITE = (255, 255, 255, 0)
GREEN = (0, 255, 0, 0)
white_bg = pyglet.image.SolidColorImagePattern(WHITE).create_image(EngineGlobals.width, EngineGlobals.height)
green_block = pyglet.image.SolidColorImagePattern(GREEN).create_image(32, 32)

# Creation of a basic platform that Kenny can jump onto 
# A nested list 
platform = [
          #  0,1,2,3,4,5,6,7,8,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0] ]

environment = platform * 16

environment = [lists * 16 for lists in environment]
# commenting out the below print statement until we need it again
# print(environment)

# This is where we store instance objects as static members of EngineGlobals
platform = environment
EngineGlobals.platform = environment
EngineGlobals.kenny = kenny
EngineGlobals.our_screen = screen

# this function renders all elements to the screen whenever requested by the pyglet engine
# (typically every vsync event, 60 times per second)
@EngineGlobals.window.event
def on_draw():
    white_bg.blit(0, 0)

    # xcounter and ycounter will count which block we are looking to render
    xcounter = 0
    ycounter = 0
    # x_data_start and y_data_start will mark the lower-left origin of where we start grabbing blocks in the data structure
    x_data_start = int(screen.x / 32)
    y_data_start = len(platform) - int(screen.y / 32) - 1
    # x_render_start and y_render_start will mark where to start rendering blocks on screen
    x_render_start = 0 - screen.x % 32
    y_render_start = 0 - screen.y % 32

    # This will iterate through the above platform and render squares
    # For the y coord we have to start from the other direction so we set a decrement counter from the max of the y coordinates
    
    # Track the screen through the platform iteration style

    # movement happens not within this code below
    xstart = int(screen.x / 32)
    xend = int((screen.x + EngineGlobals.width) / 32) + 1


    ystart = len(environment) - int(screen.y / 32) - 1
    screen_top = screen.y + EngineGlobals.height
    yend = len(environment) - int((screen_top) / 32)

    xrender_start = 0 - screen.x % 32
    yrender_start = 0 - screen.y % 32
    
    #print(ystart, yend)
    
    for xcounter in range(xstart, xend,):
        for ycounter in range(ystart, yend, -1):
            if xcounter >= 0 and xcounter < len(environment[0]) and ycounter >= 0 and ycounter < len(environment):
                this_block = environment[ycounter][xcounter]
                if this_block == 0:
                        pass
                elif this_block == 1:
                        green_block.blit(xrender_start, yrender_start)
 
            yrender_start += 32
            
        
        xrender_start += 32
        yrender_start = 0 - screen.y % 32
    # then draw all sprites
    EngineGlobals.main_batch.draw()

    #textsurface.draw()

# this is the main game loop!
if __name__ == '__main__':
    pyglet.app.run()
