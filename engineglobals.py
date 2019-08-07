
import pyglet

class EngineGlobals:
    # the window width and height in pixels
    width, height = 800, 600

    # scale up all pixel art by this amount
    scale_factor = 2

    # do a bunch of engine initialization
    def init():
        # set the GL_NEAREST texture filter in order to create a precise pixelated look instead of blurring
        # pixels together when they get upscaled
        pyglet.image.Texture.default_min_filter = pyglet.image.GL_NEAREST
        pyglet.image.Texture.default_mag_filter = pyglet.image.GL_NEAREST

        # add some folders to the resource module so that it knows where files live
        pyglet.resource.path = ['./artwork']
        pyglet.resource.reindex()

        # create a display window
        #EngineGlobals.screen = pygame.display.set_mode((EngineGlobals.width, EngineGlobals.height))
        EngineGlobals.window = pyglet.window.Window(width=EngineGlobals.width, height=EngineGlobals.height,
                                                    caption='The Ballad of Kenny Hoggins')

        # for now, we will use one big graphics batch that every display element gets added to for efficiency
        EngineGlobals.main_batch = pyglet.graphics.Batch()
