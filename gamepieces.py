# This is where we will create game pieces to place on the board

from pyglet.sprite import Sprite
import random
from engineglobals import EngineGlobals
from math import floor
from physics import PhysicsSprite

class Block:

    def __init__(self, tilesheet_idx, solid,):
        group = EngineGlobals.tiles_front_group if solid else EngineGlobals.tiles_back_group
        self.sprite = Sprite(img=EngineGlobals.get_tile(tilesheet_idx), batch=EngineGlobals.main_batch, group=group)
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

    def getResourceImages(self):
        return {0: "door-1.png"}

    def hasGravity(self):
        return False

class NirvanaFruit(PhysicsSprite):

    def __init__(self, sprite_initializer : dict, starting_chunk, destroy_after=None):

        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

        self.destroy_after = destroy_after
        self.jump_timer = 0
        self.collected = False

    def getResourceImages(self):
        return {
            '0': {"file": "nirvana-fruit.png", 'rows': 1, 'columns': 6, 'duration': 1/10, 'loop': True},
            'get': {"file": "nirvana-fruit-get.png", 'rows': 1, 'columns': 6, 'duration': 1/16, 'loop': False}
        }

    def hasGravity(self):
        return False if self.destroy_after else True

    def updateloop(self, dt):
        if self.jump_timer <= 0:
            self.y_speed = 7
            self.x_speed = -5 if bool(random.getrandbits(1)) else 5
            self.jump_timer = 250
        else:
            self.jump_timer -= 1

        if self.destroy_after:
            self.destroy_after -= 1
            if self.destroy_after <= 0:
                self.destroy()

        return super().updateloop(dt)
    
    def on_PhysicsSprite_landed(self):
        self.x_speed = 0

    def collect(self):
        self.destroy_after = 23
        self.sprite.image = self.resource_images['get']
        self.collected = True
        self.x_speed, self.y_speed = (0, 0)

class Sword(PhysicsSprite):

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer, starting_chunk)

    def getResourceImages(self):
        return {
            0: "sword.png"
        }

    def hasGravity(self):
        return False

    def on_PhysicsSprite_collided(self, collided_object=None):
        if collided_object and type(collided_object).__name__ == 'Player':
            collided_object.has_sword = True
            self.destroy()

class Scythe(PhysicsSprite):

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer, starting_chunk)

    def getResourceImages(self):
        return {
            0: "scythe_thingy.png"
        }

    def hasGravity(self):
        return False

    def on_PhysicsSprite_collided(self, collided_object=None):
        if collided_object and type(collided_object).__name__ == 'Player':
            collided_object.has_scythe = True
            self.destroy()
