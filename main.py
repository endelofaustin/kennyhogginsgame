#!/usr/bin/python3

import sys, pyglet, physics, player, editor, pickle, dill, enemies, time, gamepieces
from engineglobals import EngineGlobals
from decimal import getcontext, Decimal
from text import Text_Crawl
from spike import Spike
from bandaid import Bandaid
from math import floor

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

# We are loading our pickled environment here for loading when the game starts. Chicken pot pie
with open('map.dill', 'rb') as f:
    EngineGlobals.platform = dill.load(f)
    # convert tiles to sprites
    for y, row in enumerate(EngineGlobals.platform):
        for x, tile in enumerate(row):
            if tile == 1:
                EngineGlobals.platform[y][x] = gamepieces.Block(EngineGlobals.hay_block, True)
            elif hasattr(tile, 'image'):
                EngineGlobals.platform[y][x] = gamepieces.Block(EngineGlobals.hay_block, True)

# load kenny sprite
kenny = player.Player()
mouse_events = editor.Editor()
EngineGlobals.window.push_handlers(kenny)
EngineGlobals.window.push_handlers(mouse_events)

# load enemy sprite
enemy = enemies.Enemy()
spike = Spike([172, 0])
bandaid = Bandaid([236, 0], 'good')

# When adding to this set we are beginning to setup changable objects
# any object in this set will have its update function called
EngineGlobals.game_objects.add(screen)

# this function will be set up for pyglet to call it every update cycle, 120 times per second
# it simply calls the updated function for every object in game_objects
def main_update_callback(dt):
    EngineGlobals.sim_fps = int(1000000000/(time.perf_counter_ns() - EngineGlobals.last_sim))
    EngineGlobals.last_sim = time.perf_counter_ns()
    physics.PhysicsSprite.collision_lists.clear()
    for obj in EngineGlobals.game_objects:
        obj.updateloop(dt)
    for delete_me in EngineGlobals.delete_us:
        EngineGlobals.game_objects.remove(delete_me)
        delete_me.delete()
    EngineGlobals.delete_us.clear()

    # Track the screen through the platform iteration style
    # movement happens not within this code below
    xstart = floor(screen.x / 32) - 1
    xend = floor((screen.x + EngineGlobals.width) / 32) + 2

    ystart = len(EngineGlobals.platform) - floor(screen.y / 32)
    screen_top = screen.y + EngineGlobals.height
    yend = len(EngineGlobals.platform) - floor((screen_top) / 32) - 3

    # xrender_start and yrender_start represent the offset of where to start drawing a given block on the screen - this origin
    # could be offscreen for blocks that are only partially onscreen at a given time
    xrender_start = 0 - screen.x % 32 - 32
    yrender_start = 0 - screen.y % 32 - 32

    # iterate through the environment horizontally from blocks on the left side of the screen to blocks on the right
    for xcounter in range(xstart, xend,):

        # iterate through the environment vertically from blocks on the bottom of the screen to blocks on the top
        # since ystart is a larger index than yend, we have to step by -1 to get from ystart to yend
        for ycounter in range(ystart, yend, -1):

            # grab the block from the environment and see if we should render it or not
            if xcounter >= 0 and xcounter < len(EngineGlobals.platform[0]) and ycounter >= 0 and ycounter < len(EngineGlobals.platform):
                if isinstance(EngineGlobals.platform[ycounter][xcounter], gamepieces.Block):
                    if xrender_start + 32 <= 0 or xrender_start >= EngineGlobals.width or yrender_start + 32 <= 0 or yrender_start >= EngineGlobals.height:
                        EngineGlobals.platform[ycounter][xcounter].sprite.visible = False
                    else:
                        EngineGlobals.platform[ycounter][xcounter].sprite.visible = True
                        EngineGlobals.platform[ycounter][xcounter].sprite.x = xrender_start
                        EngineGlobals.platform[ycounter][xcounter].sprite.y = yrender_start

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

music_list = ['sleeponit', 'stronglengthypunkbrawl', 'takingahike', 'downrightbirthright', 'workingwithmagic']


for music in music_list:
    
    load_music = pyglet.media.load(f'audio/{music}.wav', streaming=False)
    EngineGlobals.audio_player.queue(load_music)

@EngineGlobals.audio_player.event('on_player_next_source')
def loop_the_next_source():
    pass
    # EngineGlobals.audio_player.loop = True
EngineGlobals.audio_player.play()

# this is the main game loop!
if __name__ == '__main__':
    pyglet.app.run()

EngineGlobals.audio_player.delete()
