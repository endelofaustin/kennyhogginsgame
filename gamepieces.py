# This is where we will create game pieces to place on the board

from pyglet.gl import GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA
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

    def __init__(self,  init_params={'has_gravity': False, 'resource_images': {0: "door-1.png"}}, starting_position=None,
                                     target_map=None, player_position=None) -> None:
        if starting_position:
            init_params['spawn_coords'] = starting_position
        
        if target_map:
            init_params['target_map'] = target_map

        if player_position:
            init_params['player_position'] = player_position
            
        super().__init__(init_params=init_params)

class NirvanaFruit(PhysicsSprite):

    def __init__(self, init_params={
        'has_gravity': False,
        'resource_images': {
            0: {"file": "nirvana-fruit.png", 'rows': 1, 'columns': 6, 'duration': 1/10, 'loop': True}
        }
    }, spawn_coords=None, destroy_after=None):

        if spawn_coords:
            init_params['spawn_coords'] = spawn_coords

        super().__init__(init_params=init_params)

        self.destroy_after = destroy_after

    def updateloop(self, dt):
        if self.destroy_after:
            self.destroy_after -= 1
            if self.destroy_after <= 0:
                self.destroy()
        return super().updateloop(dt)
