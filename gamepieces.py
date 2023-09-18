# This is where we will create game pieces to place on the board

import pyglet.resource, pyglet.image
from pyglet.sprite import Sprite
from engineglobals import EngineGlobals

class Block:

    def __init__(self, image, solid,):
        if not isinstance(image, pyglet.image.AbstractImage):
            image = EngineGlobals.hay_block
        self.sprite = Sprite(img=image, batch=EngineGlobals.main_batch, group=EngineGlobals.tiles_group)
        self.sprite.visible = False
        self.solid = solid 

    # pickler
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['sprite']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__init__(None, self.solid)
