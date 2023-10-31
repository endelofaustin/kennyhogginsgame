# This is where we will create game pieces to place on the board

import pyglet.resource, pyglet.image
from pyglet.sprite import Sprite
from engineglobals import EngineGlobals
from math import floor
from physics import PhysicsSprite

class Block:

    def __init__(self, tilesheet_idx, solid,):
        tile_x = tilesheet_idx % floor(EngineGlobals.TILESHEET_WIDTH / 16) * 16
        tile_y = floor(tilesheet_idx / floor(EngineGlobals.TILESHEET_WIDTH / 16)) * 16
        self.sprite = Sprite(img=EngineGlobals.tilesheet.get_region(tile_x, tile_y, 16, 16), batch=EngineGlobals.main_batch, group=EngineGlobals.tiles_group)
        self.sprite.update(scale=EngineGlobals.scale_factor)
        self.sprite.visible = False
        self.tilesheet_idx = tilesheet_idx
        self.solid = solid

    # pickler
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['sprite']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if 'tilesheet_idx' in state:
            self.__init__(self.tilesheet_idx, self.solid)
        else:
            self.__init__(0, self.solid)

class Door(PhysicsSprite):

    def __init__(self, starting_position) -> None:
        super().__init__(has_gravity=False, resource_image_dict={0: pyglet.resource.image("door-1.png")})
        self.x_position = starting_position[0]
        self.y_position = starting_position[1]
