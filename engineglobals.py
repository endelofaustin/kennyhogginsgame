import pyglet
from math import floor

class EngineGlobals:
    # the window width and height in pixels
    width, height = 800, 600
    editor_addl_width = 164

    # scale up all pixel art by this amount
    scale_factor = 2

    # width/height of each cell in the collision grid
    collision_cell_size = 32

    TILESHEET_WIDTH = 160
    TILESHEET_HEIGHT = 176

    # do a bunch of engine initialization
    def init():
        # set the GL_NEAREST texture filter in order to create a precise pixelated look instead of blurring
        # pixels together when they get upscaled
        pyglet.image.Texture.default_min_filter = pyglet.image.GL_NEAREST
        pyglet.image.Texture.default_mag_filter = pyglet.image.GL_NEAREST

        # add some folders to the resource module so that it knows where files live
        pyglet.resource.path = ['./artwork', './audio']
        pyglet.resource.reindex()

        # create a display window
        EngineGlobals.window = pyglet.window.Window(width=EngineGlobals.width + EngineGlobals.editor_addl_width * EngineGlobals.scale_factor,
                                                    height=EngineGlobals.height,
                                                    caption='All The Way To the Bacon Zone', vsync=False)
        pyglet.gl.glClearColor(.5, .5, .5, 1)

        # set up a key state handler
        EngineGlobals.keys = pyglet.window.key.KeyStateHandler()
        EngineGlobals.window.push_handlers(EngineGlobals.keys)

        # for now, we will use one big graphics batch that every display element gets added to for efficiency
        EngineGlobals.main_batch = pyglet.graphics.Batch()
        EngineGlobals.bg_group = pyglet.graphics.Group(0)
        EngineGlobals.tiles_group = pyglet.graphics.Group(1)
        EngineGlobals.sprites_group = pyglet.graphics.Group(2)
        EngineGlobals.editor_group_back = pyglet.graphics.Group(3)
        EngineGlobals.editor_group_mid = pyglet.graphics.Group(4)
        EngineGlobals.editor_group_front = pyglet.graphics.Group(5)

        # this is a game object list that will auto populate when sprites are generated
        EngineGlobals.game_objects = set()
        EngineGlobals.delete_us = set()

        EngineGlobals.render_fps = 0
        EngineGlobals.sim_fps = 0
        EngineGlobals.last_render = 0
        EngineGlobals.last_sim = 0

        EngineGlobals.hay_block = pyglet.resource.image('firstblock.png')
        EngineGlobals.tilesheet = pyglet.resource.image('plagiarism.png')
        #EngineGlobals.tilesheet_as_grid = pyglet.image.TextureGrid(pyglet.image.ImageGrid(EngineGlobals.tilesheet, 11, 10, 16, 16))
        #EngineGlobals.tilesheet_as_anim = pyglet.image.Animation.from_image_sequence(EngineGlobals.tilesheet_as_grid, duration=1, loop=False)
        EngineGlobals.show_menu = True

    def get_tile(idx):
        tile_x = idx % floor(EngineGlobals.TILESHEET_WIDTH / 32) * 32
        tile_y = floor(idx / floor(EngineGlobals.TILESHEET_WIDTH / 32)) * 32
        return EngineGlobals.tilesheet.get_region(tile_x, tile_y, 32, 32)
