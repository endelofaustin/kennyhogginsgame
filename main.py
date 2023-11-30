#!/usr/bin/python3

import sys, pyglet, physics, player, editor, pickle, dill, enemies, time, gamepieces
from engineglobals import EngineGlobals
from decimal import getcontext, Decimal
from text import Text_Crawl
from spike import Spike
from bandaid import Bandaid
from math import floor
from menu import GameMenu
from gamepieces import Door
from maploader import GameMap

# Most of the code in this file, other than the update callback, is executed
# *BEFORE* the game starts and before the game window is shown. We set
# everything up and then hand over to the Pyglet engine. The pyglet engine
# then takes care of calling the update function 60 times per second and
# displaying the graphics on screen after we tell it which graphics to display
# where.

# set Decimal precision to 7 places, much more efficient than the default 28
# 6 places is enough for 1 million pixels of accuracy, which is enough to
# precisely locate any position in an area that is 900 screens high and 1300
# screens wide, for a screen size up to 1024x768
getcontext().prec = 7

# run the init function to set up the game engine
EngineGlobals.init()
screen = physics.Screen()

# create some debug text to be rendered
EngineGlobals.textsurface = pyglet.text.Label(
    text='Arrow keys move and Ctrl or Up to jump',
    color=(255, 0, 255, 255),
    batch=EngineGlobals.main_batch,
    y=EngineGlobals.height,
    anchor_y='top'
)

EngineGlobals.game_map = GameMap.load_map("map.dill")

# create the Kenny player sprite and assign it to receive
# keyboard events with the push_handlers function
kenny = player.Player()
EngineGlobals.window.push_handlers(kenny)

# create the Editor function object and assign it to
# receive mouse events with the push_handlers function
editor = editor.Editor()
EngineGlobals.window.push_handlers(editor)
EngineGlobals.game_objects.add(editor)
menu = GameMenu()
EngineGlobals.window.push_handlers(menu)

# load enemy sprite
EngineGlobals.game_map.sprites.add(enemies.Enemy())
EngineGlobals.game_map.sprites.add(enemies.Doggy())
EngineGlobals.game_map.sprites.add(Spike([172, 0]))
EngineGlobals.game_map.sprites.add(Bandaid([236, 0], 'good'))
EngineGlobals.game_map.sprites.add(Door(starting_position=[500, 0]))

# When adding to this set we are beginning to setup changable objects
# any object in this set will have its update function called
# One of the objects that needs to have its update function called
# is the screen object, so that it can update which part of the
# map it is looking at based on Kenny's position
EngineGlobals.game_objects.add(screen)

# this function will be set up for pyglet to call it every update cycle, 120 times per second
# every game object has a specific updateloop function, this is the main update function that
# simply iterates through every game object and calls its specific update function
def main_update_callback(dt):

    # see how much time has passed (in nanoseconds) since the last time the update function
    # happened. This is nanoseconds-per-frame; invert it and multiply by 1000000000 to get
    # frames-per-second
    EngineGlobals.sim_fps = int(1000000000/(time.perf_counter_ns() - EngineGlobals.last_sim))
    EngineGlobals.last_sim = time.perf_counter_ns()

    # reset the grid-based collision lists so that they can be recalculated every frame
    physics.PhysicsSprite.collision_lists.clear()

    # call the updateloop funcction for each game object
    for obj in EngineGlobals.game_objects:
        obj.updateloop(dt)

    # some objects may have requested to be deleted during the update loop,
    # by adding themselves to the delete_us list. Delete them now.
    for delete_me in EngineGlobals.delete_us:
        EngineGlobals.game_objects.discard(delete_me)
        EngineGlobals.game_map.sprites.discard(delete_me)
        delete_me.delete()
    # every game object that requested it has now been deleted, so clear
    # the list so that more objects can request deletion during the next
    # update cycle
    EngineGlobals.delete_us.clear()

    # This is the same as the deletion but for addition.
    # You cant add to a set while iterating over it. 
    for add_me in EngineGlobals.add_us:
        EngineGlobals.game_objects.add(add_me)
    
    EngineGlobals.add_us.clear()

    ### BLOCK RENDERING CODE ###
    # This section of code is responsible for calculating the correct position of
    # every block in the map relative to the position of the viewport within the map.

    # 1. We are going to iterate from the left side of the screen to the right for our
    # outer loop, and from the bottom of the screen to the top for our inner loop.

    # Calculate the starting point of the outer loop (left to right) as xstart and the
    # endpoint as xend.
    #
    # We are iterating one block at a time (32 pixels). The first block we look at will be
    # the block the left side of the screen is touching -- it could be a block that is
    # partly or nearly all the way off-screen. The last block we look at will be the block
    # the right side of the screen is touching.
    xstart = floor(screen.x / 32) - 1
    xend = floor((screen.x + EngineGlobals.width) / 32) + 2

    # Now calculate the starting and ending point of the inner loop (bottom to top).
    ystart = len(EngineGlobals.game_map.platform) - floor(screen.y / 32)
    screen_top = screen.y + EngineGlobals.height
    yend = len(EngineGlobals.game_map.platform) - floor((screen_top) / 32) - 3

    # xrender_start and yrender_start represent the offset (in pixels) of where to start
    # drawing a given block on the screen - this origin could be offscreen for blocks that
    # are only partially onscreen at a given time
    xrender_start = 0 - screen.x % 32 - 32
    yrender_start = 0 - screen.y % 32 - 32

    # iterate through the environment horizontally from blocks on the left side of the screen to blocks on the right
    for xcounter in range(xstart, xend,):

        # iterate through the environment vertically from blocks on the bottom of the screen to blocks on the top
        # since ystart is a larger index than yend, we have to step by -1 to get from ystart to yend
        for ycounter in range(ystart, yend, -1):

            # grab the block from the environment and see if we should render it or not
            if xcounter >= 0 and xcounter < len(EngineGlobals.game_map.platform[0]) and ycounter >= 0 and ycounter < len(EngineGlobals.game_map.platform):
                if isinstance(EngineGlobals.game_map.platform[ycounter][xcounter], gamepieces.Block):
                    if xrender_start + 32 <= 0 or xrender_start >= EngineGlobals.width or yrender_start + 32 <= 0 or yrender_start >= EngineGlobals.height:
                        EngineGlobals.game_map.platform[ycounter][xcounter].sprite.visible = False
                    else:
                        EngineGlobals.game_map.platform[ycounter][xcounter].sprite.visible = True
                        EngineGlobals.game_map.platform[ycounter][xcounter].sprite.x = xrender_start
                        EngineGlobals.game_map.platform[ycounter][xcounter].sprite.y = yrender_start

            # after each time through the y loop, update the y rendering location
            yrender_start += 32

        # after each time through the x loop, update the x rendering location and reset y to the bottom of the column
        xrender_start += 32
        yrender_start = 0 - screen.y % 32 - 32

# ask pyglet to call our main_update_callback 60 times per second
pyglet.clock.schedule_interval(main_update_callback, 1/60.0)

EngineGlobals.kenny = kenny
EngineGlobals.our_screen = screen

# Instaniate the text crawl object
text_crawl = Text_Crawl()
EngineGlobals.game_objects.add(text_crawl)

# this function renders all elements to the screen whenever requested by the pyglet engine
# (typically every vsync event, 60 times per second)
@EngineGlobals.window.event
def on_draw():
    
    if EngineGlobals.show_menu == True:
        
        menu.on_draw()
        
    else:
 
        EngineGlobals.render_fps = int(1000000000/(time.perf_counter_ns() - EngineGlobals.last_render))
        EngineGlobals.last_render = time.perf_counter_ns()
        EngineGlobals.textsurface.text = "render fps: {}\nsim fps: {}".format(EngineGlobals.render_fps, EngineGlobals.sim_fps)
        EngineGlobals.window.clear()

        # now that we've drawn the environment, draw all sprites 
        EngineGlobals.main_batch.draw()
    
        # Drawing the Text Crawl object now:::: Right here!
        text_crawl.on_draw()

#### Audio playback testing
# introwav = pyglet.media.load('audio/intro.wav', streaming=False)
# lalala = pyglet.media.load('audio/LaLaLa.wav', streaming=False)
EngineGlobals.audio_player = pyglet.media.Player()
# EngineGlobals.audio_player.queue(introwav)
# EngineGlobals.audio_player.queue(lalala)
# riffwav = pyglet.media.load('audio/kenny_riff1.wav', streaming=False)
# EngineGlobals.audio_player.queue(riffwav)

music_list = ['rap1.mp3', 'sleeponit.wav', 'stronglengthypunkbrawl.wav', 'takingahike.wav', 'downrightbirthright.wav', 'workingwithmagic.wav']


for music in music_list:
    
    load_music = pyglet.media.load(f'audio/{music}', streaming=False)
    EngineGlobals.audio_player.queue(load_music)

@EngineGlobals.audio_player.event('on_player_next_source')
def loop_the_next_source():
    pass
    # EngineGlobals.audio_player.loop = True
#EngineGlobals.audio_player.play()

# this is the main game loop!
if __name__ == '__main__':
    pyglet.app.run()

EngineGlobals.audio_player.delete()
