
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals

# PhysicsSprite represents a sprite that honors the laws of physics.
# It contains an update method that will alter the sprite's position according
# to speed and gravity.
class PhysicsSprite(pyglet.sprite.Sprite):

    # constructor
    # Set has_gravity to False to create a sprite that hovers in defiance of all reason
    def __init__(self, has_gravity = True, resource_image = None):
        self.landed = False

        # call the parent Sprite constructor
        # for now, all sprites will bear the face of Kenny Hoggins
        pyglet.sprite.Sprite.__init__(self, img=resource_image, batch=EngineGlobals.main_batch)

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

        # upward or downward collisions
        if self.speed[1] != 0:
            # first, check if trying to move off the bottom or top of the screen
            if new_y < 0 or new_y + self.height >= EngineGlobals.height:
                # if so, check if we should trigger landing event (moving downward and not already grounded)
                if self.speed[1] < 0 and not self.landed:
                    self.landed = True
                    self.on_PhysicsSprite_landed()
                # regardless, stop all downward or upward motion
                self.speed[1] = 0
            # otherwise, we are safe to see where we are in the environment and whether we are about to collide
            # with a solid block
            else:
                # from the environment, retrieve the tiles at Kenny's lower left foot, lower right foot, upper left,
                # and upper right
                # since this is only checking for up/down collisions, it's important that we use the new y coordinates
                # (new_y) but the original x coordinates (self.dpos[0])
                left_foot_tile = EngineGlobals.platform[int((EngineGlobals.height - new_y)/32)][int(self.dpos[0]/32)]
                right_foot_tile = EngineGlobals.platform[int((EngineGlobals.height - new_y)/32)][int((self.dpos[0] + self.width - 1)/32)]
                left_head_tile = EngineGlobals.platform[int((EngineGlobals.height - new_y - self.height + 1)/32)][int(self.dpos[0]/32)]
                right_head_tile = EngineGlobals.platform[int((EngineGlobals.height - new_y - self.height + 1)/32)][int((self.dpos[0] + self.width - 1)/32)]
                # if one of those tiles is solid, time to cease all vertical movement!
                if ( left_foot_tile == 1 or right_foot_tile == 1
                        or left_head_tile == 1 or right_head_tile == 1 ):
                    if self.speed[1] < 0 and not self.landed:
                        self.landed = True
                        self.on_PhysicsSprite_landed()
                    self.speed[1] = 0
                else:
                    self.landed = False

        # left or right collisions
        if self.speed[0] != 0:
            if new_x < 0 or new_x + self.width >= EngineGlobals.width:
                self.speed[0] = 0
            else:
                left_foot_tile = EngineGlobals.platform[int((EngineGlobals.height - self.dpos[1])/32)][int(new_x/32)]
                right_foot_tile = EngineGlobals.platform[int((EngineGlobals.height - self.dpos[1])/32)][int((new_x + self.width - 1)/32)]
                left_head_tile = EngineGlobals.platform[int((EngineGlobals.height - self.dpos[1] - self.height + 1)/32)][int(new_x/32)]
                right_head_tile = EngineGlobals.platform[int((EngineGlobals.height - self.dpos[1] - self.height + 1)/32)][int((new_x + self.width - 1)/32)]
                if ( left_foot_tile == 1 or right_foot_tile == 1
                        or left_head_tile == 1 or right_head_tile == 1 ):
                    self.speed[0] = 0

        self.dpos[0] += self.speed[0]
        self.dpos[1] += self.speed[1]

        # finally, update the x and y coords so that pyglet will know where to draw the sprite
        self.x, self.y = int(self.dpos[0]), int(self.dpos[1])

    def on_PhysicsSprite_landed(self):
        pass
