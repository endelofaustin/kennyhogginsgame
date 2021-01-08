from engineglobals import EngineGlobals
from physics import PhysicsSprite
import pyglet

class Bullet(PhysicsSprite):

    def __init__(self,):
        PhysicsSprite.__init__(self, has_gravity = False, resource_image_dict={0:pyglet.resource.image("bullet1-1.png.png")})
        
    def on_PhysicsSprite_collided(self, collided_object=None):
        # we want to destroy this game object after we are done iterating through the members of the set
        # so, we put it in a list that we will refer to later
        if collided_object and type(collided_object).__name__ == 'Player':
            return
        EngineGlobals.delete_us.append(self)
        if type(collided_object).__name__ == 'Enemy':
            collided_object.die_hard()
