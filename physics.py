
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals

# PhysicsSprite represents a sprite that honors the laws of physics.
# It contains an update method that will alter the sprite's position according
# to speed and gravity.
class PhysicsSprite(pyglet.sprite.Sprite):

    # constructor
    # Set has_gravity to False to create a sprite that hovers in defiance of all reason
    def __init__(self, has_gravity = True, resource_image_dict = None):
        self.landed = False

        # call the parent Sprite __init__
        pyglet.sprite.Sprite.__init__(self, img=next(iter(resource_image_dict.values())), batch=EngineGlobals.main_batch)
        self.resource_images = resource_image_dict

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

        # When a physics sprite is generated it needs to be added to engineglobals.game_objects
        # so that it will be put into the update loop and not mess everything up like an idiot
        EngineGlobals.game_objects.add(self)

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
            if new_y < 0 or new_y + self.height >= len(EngineGlobals.platform) * 32:
                # if so, check if we should trigger landing event (moving downward and not already grounded)
                if self.speed[1] < 0 and not self.landed:
                    self.landed = True
                    self.on_PhysicsSprite_landed()
                # regardless, stop all downward or upward motion
                self.speed[1] = 0
                self.on_PhysicsSprite_collided()
            # otherwise, we are safe to see where we are in the environment and whether we are about to collide
            # with a solid block
            else:
                # from the environment, retrieve the tiles at Kenny's lower left foot, lower right foot, upper left,
                # and upper right
                # since this is only checking for up/down collisions, it's important that we use the new y coordinates
                # (new_y) but the original x coordinates (self.dpos[0])
                left_foot_tile = EngineGlobals.platform[len(EngineGlobals.platform) - int(new_y / 32) - 1][int(self.dpos[0]/32)]
                right_foot_tile = EngineGlobals.platform[len(EngineGlobals.platform) - int(new_y / 32) - 1][int((self.dpos[0] + self.width - 1)/32)]
                left_head_tile = EngineGlobals.platform[len(EngineGlobals.platform) - int((new_y + self.height - 1) / 32) - 1][int(self.dpos[0]/32)]
                right_head_tile = EngineGlobals.platform[len(EngineGlobals.platform) - int((new_y + self.height - 1) / 32) - 1][int((self.dpos[0] + self.width - 1)/32)]
                # if one of those tiles is solid, time to cease all vertical movement!
                if (self.if_solid(left_foot_tile) == True or self.if_solid(right_foot_tile) == True
                        or self.if_solid(left_head_tile) == True or self.if_solid(right_head_tile) == True):
                    if self.speed[1] < 0 and not self.landed:
                        self.landed = True
                        self.on_PhysicsSprite_landed()
                    self.speed[1] = 0
                    self.on_PhysicsSprite_collided()
                else:
                    self.landed = False

        # left or right collisions
        if self.speed[0] != 0:
            if new_x < 0 or new_x + self.width >= len(EngineGlobals.platform[0]) * 32:
                self.speed[0] = 0
                self.on_PhysicsSprite_collided()
            else:
                left_foot_tile = EngineGlobals.platform[len(EngineGlobals.platform) - int(self.dpos[1] / 32) - 1][int(new_x/32)]
                right_foot_tile = EngineGlobals.platform[len(EngineGlobals.platform) - int(self.dpos[1] / 32) - 1][int((new_x + self.width - 1)/32)]
                left_head_tile = EngineGlobals.platform[len(EngineGlobals.platform) - int((self.dpos[1] + self.height - 1) / 32) - 1][int(new_x/32)]
                right_head_tile = EngineGlobals.platform[len(EngineGlobals.platform) - int((self.dpos[1] + self.height - 1) / 32) - 1][int((new_x + self.width - 1)/32)]
                if (self.if_solid(left_foot_tile) == True or self.if_solid(right_foot_tile) == True
                        or self.if_solid(left_head_tile) == True or self.if_solid(right_head_tile) == True):
                    self.speed[0] = 0
                    self.on_PhysicsSprite_collided()

        # collisions with other sprites
        for other_sprite in EngineGlobals.game_objects:
            if other_sprite == self or not isinstance(other_sprite, PhysicsSprite):
                continue
            if ( other_sprite.dpos[0] + other_sprite.width < self.dpos[0]
             or other_sprite.dpos[1] + other_sprite.height < self.dpos[1]
             or other_sprite.dpos[0] > self.dpos[0] + self.width
             or other_sprite.dpos[1] > self.dpos[1] + self.height ):
                continue
            # otherwise, they have collided
            self.on_PhysicsSprite_collided(other_sprite)

        self.dpos[0] += self.speed[0]
        self.dpos[1] += self.speed[1]

        # finally, update the x and y coords so that pyglet will know where to draw the sprite
        self.x, self.y = int(self.dpos[0] - EngineGlobals.our_screen.x), int(self.dpos[1] - EngineGlobals.our_screen.y)

    def on_PhysicsSprite_landed(self):
        pass

    def on_PhysicsSprite_collided(self, collided_object=None):
        pass

    def if_solid(self,block):
        if block == 1:
            return True
        if  hasattr(block, "solid") and block.solid == True:
            return True
        else:
            return False

# the Screen class tracks the positioning of the screen within the entire environment
class Screen():
    def __init__(self):
        self.x = 0
        self.y = 0

    # self.x is screen position
    # kenny.dpos[0] is x 1 is y
    def updateloop(self, dt):
        if (EngineGlobals.kenny.dpos[0] - self.x) < 64:
            self.x = (EngineGlobals.kenny.dpos[0]) - 64

        kennys_belly = EngineGlobals.kenny.dpos[0] + EngineGlobals.kenny.width
        screen_redge = self.x + EngineGlobals.width

        if kennys_belly >= screen_redge - 64:
            self.x = kennys_belly - EngineGlobals.width + 64

        if (EngineGlobals.kenny.dpos[1]) - self.y < 64:
            self.y = (EngineGlobals.kenny.dpos[1]) - 64

        kennys_head = EngineGlobals.kenny.dpos[1] + EngineGlobals.kenny.height
        screen_top = self.y + EngineGlobals.height
        if kennys_head >= screen_top - 64:
            self.y = kennys_head - EngineGlobals.height + 64


