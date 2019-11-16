
from physics import PhysicsSprite
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals

# the player object represents Kenny and responds to keyboard input
class Player(PhysicsSprite):
    def __init__(self):
        PhysicsSprite.__init__(self, has_gravity=True, resource_image=pyglet.resource.image("kennystance1-2.png.png"))

        # jumpct counts the number of jumps to allow for double-jumping
        self.jumpct = 0

    def updateloop(self, dt):
        # interpret arrow keys into velocity
        self.speed[0] = Decimal(0)
        if EngineGlobals.keys[pyglet.window.key.LEFT]:
            self.speed[0] -= Decimal('8')
        if EngineGlobals.keys[pyglet.window.key.RIGHT]:
            self.speed[0] += Decimal('8')

        # then, run normal physics algorithm
        PhysicsSprite.updateloop(self, dt)

    # on_key_press is called by the pyglet engine when attached to a window
    # this lets us handle keyboard input events at the time they occur
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL or symbol == pyglet.window.key.UP:
            # if on a solid object, normal jump
            if self.landed and self.jumpct == 0:
                self.speed[1] = Decimal(max(self.speed[1], 0) + 13)
            # if already in the area, allow one more smaller jump
            elif self.jumpct < 2:
                self.speed[1] = 10
            self.jumpct += 1
        # Button press handeling for space bar to shoot
        if symbol == pyglet.window.key.SPACE:
            self.shoot_it()

    # this function is called by the physics simulator when it detects landing on a solid object
    def on_PhysicsSprite_landed(self):
        # set our jumpct back to zero to allow future jumps
        self.jumpct = 0
    
    # Lets do some shooting

    def shoot_it(self,):

        PhysicsSprite.__init__(self, has_gravity=True, resource_image=pyglet.resource.image("bullet_1.png"))



        




