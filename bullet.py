from engineglobals import EngineGlobals
from physics import PhysicsSprite
import pyglet

class Bullet(PhysicsSprite):

    def __init__(self):
        PhysicsSprite.__init__(self, init_params={"has_gravity": False, "resource_images": {0:"bullet1-1.png.png"}})
         
    def on_PhysicsSprite_collided(self, collided_object=None):
        
        if collided_object and type(collided_object).__name__ == 'Player':
            return
        self.destroy()
        if type(collided_object).__name__ == 'Enemy' or type(collided_object).__name__ == 'Pearl':
            collided_object.die_hard()

        if type(collided_object).__name__ == 'PearlyPaul':
            collided_object.getting_hit()
