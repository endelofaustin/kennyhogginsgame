from engineglobals import EngineGlobals
from physics import PhysicsSprite
import pyglet

class Bullet(PhysicsSprite):

    def __init__(self,):
        PhysicsSprite.__init__(self, has_gravity = False, resource_image=pyglet.resource.image("bullet1-1.png.png"))
        
    def on_PhysicsSprite_collided(self,):

        EngineGlobals.game_objects.remove(self, )
        #self.delete()



    