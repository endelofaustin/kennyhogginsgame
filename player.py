
from physics import PhysicsSprite
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet

# the player object represents Kenny and responds to keyboard input
class Player(PhysicsSprite):
    LEFT_RIGHT_RUN_SPEED = 5
    JUMP_INITIAL_VELOCITY = 12
    DOUBLE_JUMP_VELOCITY = 9
    
    def __init__(self):
        PhysicsSprite.__init__(self, has_gravity=True, resource_image_dict={
            'right': pyglet.resource.image("kennystance1-2.png.png"),
            'left': pyglet.resource.image("kennystance-left.png"),
            'bloody': pyglet.resource.image("bloodykenny-1.png"),
            'run_right': pyglet.image.Animation.from_image_sequence(pyglet.image.ImageGrid(pyglet.resource.image("kenny-run-right.png"), rows=1, columns=4), duration=1/10, loop=True)
        })

        # Which direction is Kenny facing?
        self.direction = 'right'

        # jumpct counts the number of jumps to allow for double-jumping
        self.jumpct = 0
        self.spit_bullet = pyglet.media.load("audio/spitbullets.wav", streaming=False)

        # let's get that blood flowing
        self.bloody = False


    def updateloop(self, dt):
        # interpret arrow keys into velocity
        self.speed[0] = Decimal(0)
        if EngineGlobals.keys[pyglet.window.key.LEFT]:
            self.speed[0] -= Decimal(Player.LEFT_RIGHT_RUN_SPEED)
        if EngineGlobals.keys[pyglet.window.key.RIGHT]:
            self.speed[0] += Decimal(Player.LEFT_RIGHT_RUN_SPEED)

        if self.speed[0] < 0:
            self.direction = 'left'
            if self.image != self.resource_images['left']:
                self.image = self.resource_images['left']
        elif self.speed[0] > 0:
            self.direction = 'right'
            if self.image != self.resource_images['run_right']:
                self.image = self.resource_images['run_right']
        elif self.direction == 'left':
            if self.image != self.resource_images['left']:
                self.image = self.resource_images['left']
        else:
            if self.image != self.resource_images['right']:
                self.image = self.resource_images['right']

        if self.bloody == True:
           self.image = self.resource_images['bloody']

        if self.landed:
            self.jumpct = 0

        # then, run normal physics algorithm
        PhysicsSprite.updateloop(self, dt)

    # on_key_press is called by the pyglet engine when attached to a window
    # this lets us handle keyboard input events at the time they occur
    def on_key_press(self, symbol, modifiers):
        if (symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL or symbol == pyglet.window.key.UP) and self.jumpct <= 1:
            # if on a solid object, normal jump
            if self.landed and self.jumpct == 0:
                self.speed[1] = Decimal(max(self.speed[1], 0) + Player.JUMP_INITIAL_VELOCITY)
                self.landed = False
            # if already in the air, allow one more smaller jump
            elif self.jumpct < 2:
                self.speed[1] = Player.DOUBLE_JUMP_VELOCITY
            self.jumpct += 1
        # Button press handeling for space bar to shoot
        if symbol == pyglet.window.key.SPACE:
            self.shoot_it()

    # this function is called by the physics simulator when it detects landing on a solid object
    def on_PhysicsSprite_landed(self):
        # set our jumpct back to zero to allow future jumps
        self.jumpct = 0

    # Lets do some shooting

    def shoot_it(self):
        bullet = Bullet()
        if self.direction == 'right':
            bullet.speed[0] -= Decimal('15.0')
            bullet.dpos[0],bullet.dpos[1] = self.dpos[0] - 5, self.dpos[1] + 22
        else:
            bullet.speed[0] += Decimal('15.0')
            bullet.dpos[0],bullet.dpos[1] = self.dpos[0] + 5, self.dpos[1] + 22
        # Play the bullet spit audio
        self.spit_bullet.play()


    def on_PhysicsSprite_collided(self, collided_object=None):
        
        if collided_object and type(collided_object).__name__ == 'Spike':
            self.bloody = True
        elif collided_object and type(collided_object).__name__ == 'Bandaid':
            self.bloody = False
            collided_object.destroy()            
