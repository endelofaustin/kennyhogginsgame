#!/usr/bin/python3

import sys, pyglet, physics, player, editor, pickle, dill, enemies, time, gamepieces
from engineglobals import EngineGlobals
from decimal import getcontext, Decimal
from text import Text_Crawl
from math import floor
from menu import GameMenu
from maploader import GameMap
from lifecycle import LifeCycleManager
from sprite import makeSprite
from magic_map import Chunk, ChunkEdge

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
LifeCycleManager.init()
screen = physics.Screen()

# create some debug text to be rendered
EngineGlobals.textsurface = pyglet.text.Label(
    text='Arrow keys move and Ctrl or Up to jump',
    color=(255, 0, 255, 255),
    batch=EngineGlobals.main_batch,
    y=EngineGlobals.height,
    anchor_y='top'
)

GameMap.load_map("map.dill")

# create the Kenny player sprite and assign it to receive
# keyboard events with the push_handlers function
kenny = makeSprite(player.Player, EngineGlobals.game_map.chunks[0], (0, 0), lifecycle_manager='UNDYING', group='FRONT')
EngineGlobals.window.push_handlers(kenny)

# create the Editor function object and assign it to
# receive mouse events with the push_handlers function
editor = editor.Editor()
EngineGlobals.window.push_handlers(editor)
LifeCycleManager.ALL_SETS['UNDYING'].addGameObject(editor)
menu = GameMenu()
EngineGlobals.window.push_handlers(menu)

# When adding to this set we are beginning to setup changable objects
# any object in this set will have its update function called
# One of the objects that needs to have its update function called
# is the screen object, so that it can update which part of the
# map it is looking at based on Kenny's position
LifeCycleManager.ALL_SETS['UNDYING'].addGameObject(screen)

# This function is called every update loop to update the position of all blocks in the map relative to the
# viewport.
# 1. Start at the bottom left of the viewport. We know what the X and Y coordinates of the viewport are in
#     game space; convert that into indices into the map grid. This will get us the block that will render
#     into the bottom left corner. Some part of it will be offscreen but at least a pixel of it will be
#     on-screen. `xstart` will be the X coordinate index in the map grid and `ystart` will be the Y index.
#
# 2. Define `xend` and `yend` for the block that will be in the top right corner of the screen, as above.
#     We will iterate over the ranges xstart -> xend and ystart ->yend.
#
# 3. Calculate the offset of how many pixels the starting block is offscreen on the X and Y axis. This
#     will be called `xrender_start` and `yrender_start` and we will increment them by the width/height
#     of a block each time through the loop. This will give each individual block's point to be drawn
#     relative to the viewport.
#
# 4. Within the loop, check and make sure we are not trying to peek out of bounds on the map and check if
#     there is in fact a block in the spot we are trying to draw. If it's not empty space and there is
#     actually a block there, then set the block's sprite to visible and set its X and Y coordinates
#     relative to the viewport) to `xrender_start` and `yrender_start`.
#
# The end result of this is that all blocks that are supposed to be on-screen get their X and Y adjusted
# as the viewport moves, and all blocks that are offscreen get hidden.
def update_chunk_tile_coords(chunk):
    xstart = int(max(screen.x - chunk.coalesced_x, 0) / 32) - 1
    xend = int(min(screen.x + EngineGlobals.width, screen.x + chunk.width * 32) / 32) + 2

    ystart = chunk.height - int(max(screen.y - chunk.coalesced_y, 0) / 32)
    yend = chunk.height - int(min(screen.y + EngineGlobals.height, screen.y + chunk.height * 32) / 32) - 3

    # xrender_start and yrender_start represent the offset of where to start drawing a given block on the screen - this origin
    # could be offscreen for blocks that are only partially onscreen at a given time
    xrender_start = int((chunk.coalesced_x + xstart * 32) - screen.x)
    yrender_start = int((chunk.coalesced_y + (chunk.height - ystart - 1) * 32) - screen.y)

    # iterate through the environment horizontally from blocks on the left side of the screen to blocks on the right
    for xcounter in range(xstart, xend):

        # iterate through the environment vertically from blocks on the bottom of the screen to blocks on the top
        # since ystart is a larger index than yend, we have to step by -1 to get from ystart to yend
        for ycounter in range(ystart, yend, -1):

            # grab the block from the environment and see if we should render it or not
            if xcounter >= 0 and xcounter < len(chunk.platform[0]) and ycounter >= 0 and ycounter < len(chunk.platform):
                if isinstance(chunk.platform[ycounter][xcounter], gamepieces.Block):
                    if xrender_start + 32 <= 0 or xrender_start >= EngineGlobals.width or yrender_start + 32 <= 0 or yrender_start >= EngineGlobals.height:
                        chunk.platform[ycounter][xcounter].sprite.visible = False
                    else:
                        chunk.platform[ycounter][xcounter].sprite.visible = True
                        chunk.platform[ycounter][xcounter].sprite.x = xrender_start
                        chunk.platform[ycounter][xcounter].sprite.y = yrender_start

            # after each time through the y loop, update the y rendering location
            yrender_start += 32

        # after each time through the x loop, update the x rendering location and reset y to the bottom of the column
        xrender_start += 32
        yrender_start = int((chunk.coalesced_y + (chunk.height - ystart - 1) * 32) - screen.y)

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
    LifeCycleManager.processUpdates(dt)

    # First update the chunk the player inhabits, then any adjacent chunks that are onscreen
    update_chunk_tile_coords(kenny.current_chunk)
    chunk_to_update = kenny.current_chunk
    while ChunkEdge.LEFT in chunk_to_update.adjacencies:
        chunk_to_update = chunk_to_update.adjacencies[ChunkEdge.LEFT]
        if chunk_to_update.hidden or chunk_to_update.coalesced_x + chunk_to_update.width * 32 < screen.x:
            break
        update_chunk_tile_coords(chunk_to_update)
    chunk_to_update = kenny.current_chunk
    while ChunkEdge.RIGHT in chunk_to_update.adjacencies:
        chunk_to_update = chunk_to_update.adjacencies[ChunkEdge.RIGHT]
        if chunk_to_update.hidden or chunk_to_update.coalesced_x > screen.x + EngineGlobals.width:
            break
        update_chunk_tile_coords(chunk_to_update)
    chunk_to_update = kenny.current_chunk
    while ChunkEdge.TOP in chunk_to_update.adjacencies:
        chunk_to_update = chunk_to_update.adjacencies[ChunkEdge.TOP]
        if chunk_to_update.hidden or chunk_to_update.coalesced_y > screen.y + EngineGlobals.height:
            break
        update_chunk_tile_coords(chunk_to_update)
    chunk_to_update = kenny.current_chunk
    while ChunkEdge.BOTTOM in chunk_to_update.adjacencies:
        chunk_to_update = chunk_to_update.adjacencies[ChunkEdge.BOTTOM]
        if chunk_to_update.hidden or chunk_to_update.coalesced_y + chunk_to_update.height * 32 < screen.y:
            break
        update_chunk_tile_coords(chunk_to_update)

# ask pyglet to call our main_update_callback 60 times per second
pyglet.clock.schedule_interval(main_update_callback, 1/60.0)

EngineGlobals.kenny = kenny
EngineGlobals.our_screen = screen

# Instaniate the text crawl object
text_crawl = Text_Crawl()
LifeCycleManager.ALL_SETS['PER_MAP'].addGameObject(text_crawl)

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
