from engineglobals import EngineGlobals
from physics import PhysicsSprite
import pyglet

class Bullet(PhysicsSprite):

    def __init__(self, sprite_initializer : dict):
        super().__init__(sprite_initializer)

    def getResourceImages(self):
        return {0:"bullet1-1.png.png"}

    def hasGravity(self):
        return False

    def on_PhysicsSprite_collided(self, collided_object=None):
        
        if collided_object and type(collided_object).__name__ == 'Player':

            # the bullet will start out colliding with the player because
            # it spawns from the player; we need to ignore player collisions
            return

        else:

            # otherwise if the bullet hits anything else we will destroy the bullet
            self.destroy()

            # if the bullet hits an enemy, call the enemy's die_hard function
            if type(collided_object).__name__ == 'Enemy' or type(collided_object).__name__ == 'Pearl':
                collided_object.die_hard()

            # if the bullet hits Pearly Paul (the boss), call Pearly Paul's getting_hit function
            if type(collided_object).__name__ == 'PearlyPaul':
                collided_object.getting_hit()
