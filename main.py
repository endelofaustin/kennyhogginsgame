#!/usr/bin/python3

import sys, pyglet, physics, player, editor
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
textsurface = pyglet.text.Label(text='Arrow keys move and Ctrl or Up to jump', color=(255, 0, 255, 255),
                                batch=EngineGlobals.main_batch, y=EngineGlobals.height, anchor_y='top')

# load kenny's face
kenny = player.Player()
mouse_events = editor.Editor()
EngineGlobals.window.push_handlers(kenny)
EngineGlobals.window.push_handlers(mouse_events)

# When adding to this list we are beginning to setup changable objects
# any object in this list will have its update function called
game_objects = [kenny, screen]


#load lucinda and set her to a different starting position than the default 0,0
#lucinda  = pygame.image.load("./artwork/lucinda.png")
# move the entire rectangle encompassing Lucinda by 201 pixels horizontally and 201 pixels vertically
##lucindarect = lucinda.get_rect()
#lucindarect.left += 201
#lucindarect.right += 201
#lucindarect.top += 201
#lucindarect.bottom += 201

def main_update_callback(dt):
    # update all game objects
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
print(environment)
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

    # iterate through the nested list and render a rectangle if a 1 is in that position
    # in order to draw rectangles in the platform object we need to iterate through the matrix and increment counters by a count of 16 for the purpose 
    # of keeping track of the drawings location and then 
    xcounter = 0
    ycounter = EngineGlobals.height - 32
    
    # This will iterate through the above platform and render squares
    # For the y coord we have to start from the other direction so we set a decrement counter from the max of the y coordinates
    for row in platform:
        #textsurface = myfont.render(f'{xcounter}', False, (255, 0, 255)).convert_alpha()
        xcounter = 0
        for item in row:
            if item == 0:
                pass
            elif item == 1:
                green_block.blit(xcounter - screen.x, ycounter - screen.y)
            xcounter += 32
        ycounter -= 32

    # then draw all sprites
    EngineGlobals.main_batch.draw()

# this is the main game loop!
if __name__ == '__main__':
    pyglet.app.run()
