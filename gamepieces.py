# This is where we will create game pieces to place on the board

import pyglet.resource, pyglet.image
from pyglet.sprite import Sprite
from engineglobals import EngineGlobals

class Block:

    def __init__(self, image, solid,):
        if not isinstance(image, pyglet.image.AbstractImage):
            image = pyglet.resource.image('firstblock.png')
        self.sprite = Sprite(img=image, batch=EngineGlobals.main_batch, group=EngineGlobals.tiles_group)
        self.solid = solid 
