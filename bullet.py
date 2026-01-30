from engineglobals import EngineGlobals
from physics import PhysicsSprite
import pyglet

class Bullet(PhysicsSprite):

    def __init__(self, sprite_initializer : dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

    def getResourceImages(self):
        return {0:"bullet1-1.png.png"}

    def hasGravity(self):
        return False

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if collided_object and type(collided_object).__name__ == 'Player':

            # the bullet will start out colliding with the player because
            # it spawns from the player; we need to ignore player collisions
            return

        elif hasattr(collided_object, 'getting_hit'):
            # otherwise if the bullet hits anything else we will destroy the bullet
            collided_object.getting_hit()
            self.destroy()

        elif not isinstance(collided_object, PhysicsSprite):
            self.destroy()
