import pyglet

class EngineGlobals:
    # the window width and height in pixels
    width, height = 800, 600

    # scale up all pixel art by this amount
    scale_factor = 2

    # width/height of each cell in the collision grid
    collision_cell_size = 32

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
        #EngineGlobals.screen = pygame.display.set_mode((EngineGlobals.width, EngineGlobals.height))
        EngineGlobals.window = pyglet.window.Window(width=EngineGlobals.width, height=EngineGlobals.height,
                                                    caption='All The Way To the Bacon Zone')
        pyglet.gl.glClearColor(1, 1, 1, 1)

        # set up a key state handler
        EngineGlobals.keys = pyglet.window.key.KeyStateHandler()
        EngineGlobals.window.push_handlers(EngineGlobals.keys)

        # for now, we will use one big graphics batch that every display element gets added to for efficiency
        EngineGlobals.main_batch = pyglet.graphics.Batch()
        EngineGlobals.bg_group = pyglet.graphics.Group(0)
        EngineGlobals.tiles_group = pyglet.graphics.Group(1)
        EngineGlobals.sprites_group = pyglet.graphics.Group(2)

        # this is a game object list that will auto populate when sprites are generated
        EngineGlobals.game_objects = set()
        EngineGlobals.delete_us = set()

        EngineGlobals.render_fps = 0
        EngineGlobals.sim_fps = 0
        EngineGlobals.last_render = 0
        EngineGlobals.last_sim = 0
