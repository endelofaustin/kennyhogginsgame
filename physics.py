
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals

# PhysicsSprite represents a sprite that honors the laws of physics.
# It contains an update method that will alter the sprite's position according
# to speed and gravity.
class PhysicsSprite(pyglet.sprite.Sprite):

    # constructor
    # Set has_gravity to False to create a sprite that hovers in defiance of all reason
    def __init__(self, has_gravity = True):
        self.landed = False

        # call the parent Sprite constructor
        # for now, all sprites will bear the face of Kenny Hoggins
        pyglet.sprite.Sprite.__init__(self, img=pyglet.resource.image("kennystance1.png"), batch=EngineGlobals.main_batch)

        # the 'speed' member is a Decimal representation of the sprite's speed at this
        # point in time; each time the game loop runs, the sprite will move by that
        # amount; self.speed[0] is the left-to-right speed (negative is left, positive is right);
        # self.speed[1] is the bottom-to-top speed (in defiance of convention, negative is down and positive is up)
        self.speed = [Decimal('0'), Decimal('0')]

        # the 'has_gravity' member is a true/false flag to indicate whether this sprite truly
        # obeys Isaac Newton's decrees.
        self.has_gravity = has_gravity

        # scale up the image
        self.update(scale=EngineGlobals.scale_factor)

        # initialize the 'dpos' member as a Decimal representation of the sprite's position
        # in the environment - self.dpos[0] is the 'x' or left-to-right coordinate,
        # self.dpos[1] is the 'y' or bottom-to-top coordinate
        self.dpos = [Decimal(), Decimal()]

    # this function is called for each sprite during the main update loop
    def updateloop(self, dt):
        if self.has_gravity:
            # accelerate downwards by a certain amount
            self.speed[1] -= Decimal('.6')
            # terminal velocity is 20 for now, so we won't move any faster than that
            if self.speed[1] < -20:
                self.speed[1] = -20

        # dpos[0] is x, dpos[1] is y
        # position plus speed is equal to new potential location
        new_x = self.dpos[0] + self.speed[0]
        new_y = self.dpos[1] + self.speed[1]
       
        # x_coord and y_coord will represent an element in the environment matrix
        x_coord = new_x/32
        y_coord = new_y/32

        # now, update the sprite's position according to speed
        if EngineGlobals.platform[int(y_coord)][int(x_coord)] == 0:
            self.dpos[0] += self.speed[0]
            self.dpos[1] += self.speed[1]
        else:
            self.speed[0] = 0
            self.speed[1] = 0

        # but don't let it go off screen to the left, right, top or bottom
        # and if it tries, bring it back and set its speed to 0
        if self.dpos[0] < 0:
            self.dpos[0] = 0
            self.speed[0] = 0
        elif (self.dpos[0] + self.width) > EngineGlobals.width:
            self.dpos[0] = EngineGlobals.width - self.width
            self.speed[0] = 0
        if self.dpos[1] <= 0:
            self.dpos[1] = 0
            self.speed[1] = 0
            if not self.landed:
                self.on_PhysicsSprite_landed()
                self.landed = True
        elif self.dpos[1] + self.height >= EngineGlobals.height:
            self.dpos[1] = EngineGlobals.height - self.height
            self.speed[1] = 0
        else:
            self.landed = False

        # finally, update the x and y coords so that pyglet will know where to draw the sprite
        self.x, self.y = int(self.dpos[0]), int(self.dpos[1])

    def on_PhysicsSprite_landed(self):
        pass
