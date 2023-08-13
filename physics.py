
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from math import floor

# PhysicsSprite represents a sprite that honors the laws of physics.
# It contains an update method that will alter the sprite's position according
# to speed and gravity.
class PhysicsSprite(pyglet.sprite.Sprite):

    collision_lists = {}

    # constructor
    # Set has_gravity to False to create a sprite that hovers in defiance of all reason
    def __init__(self, has_gravity = True, resource_image_dict = None, collision_width = None, collision_height = None):
        self.landed = False

        # call the parent Sprite __init__
        pyglet.sprite.Sprite.__init__(self, img=next(iter(resource_image_dict.values())), batch=EngineGlobals.main_batch, group=EngineGlobals.sprites_group)
        self.resource_images = resource_image_dict

        if not collision_width and len(resource_image_dict) > 0:
            self.collision_width = resource_image_dict[next(iter(resource_image_dict))].width
        if not collision_height and len(resource_image_dict) > 0:
            self.collision_height = resource_image_dict[next(iter(resource_image_dict))].height

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
            if new_y < 0 or new_y + self.collision_height >= len(EngineGlobals.platform) * 32:
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
                left_foot_tile = EngineGlobals.platform[len(EngineGlobals.platform) - floor(new_y / 32) - 1][floor(self.dpos[0]/32)]
                right_foot_tile = EngineGlobals.platform[len(EngineGlobals.platform) - floor(new_y / 32) - 1][floor((self.dpos[0] + self.collision_width - 1)/32)]
                left_head_tile = EngineGlobals.platform[len(EngineGlobals.platform) - floor((new_y + self.collision_height - 1) / 32) - 1][floor(self.dpos[0]/32)]
                right_head_tile = EngineGlobals.platform[len(EngineGlobals.platform) - floor((new_y + self.collision_height - 1) / 32) - 1][floor((self.dpos[0] + self.collision_width - 1)/32)]
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
            if new_x < 0 or new_x + self.collision_width >= len(EngineGlobals.platform[0]) * 32:
                self.speed[0] = 0
                self.on_PhysicsSprite_collided()
            else:
                left_foot_tile = EngineGlobals.platform[len(EngineGlobals.platform) - floor(self.dpos[1] / 32) - 1][floor(new_x/32)]
                right_foot_tile = EngineGlobals.platform[len(EngineGlobals.platform) - floor(self.dpos[1] / 32) - 1][floor((new_x + self.collision_width - 1)/32)]
                left_head_tile = EngineGlobals.platform[len(EngineGlobals.platform) - floor((self.dpos[1] + self.collision_height - 1) / 32) - 1][floor(new_x/32)]
                right_head_tile = EngineGlobals.platform[len(EngineGlobals.platform) - floor((self.dpos[1] + self.collision_height - 1) / 32) - 1][floor((new_x + self.collision_width - 1)/32)]
                if (self.if_solid(left_foot_tile) == True or self.if_solid(right_foot_tile) == True
                        or self.if_solid(left_head_tile) == True or self.if_solid(right_head_tile) == True):
                    self.speed[0] = 0
                    self.on_PhysicsSprite_collided()

        # Collisions with other sprites. So what's going on here actually?
        # 1. At the start of each update loop, we initialize an empty dict, PhysicsSprite.collision_lists. The dict will represent a grid in game space,
        #    with each cell 32 pixels square, about the average size of a sprite.
        # 2. Here in the update function, we are calculating the hashed_x and hashed_y of all possible cells that the sprite might be touching at this moment.
        # 3. We append the sprite in a list stored at each cell.
        # 4. We do a closer check of all other sprites that have been placed in the same cell, to see if their bounding boxes collide or not; but we no longer
        #    have to check sprites elsewhere in the map that have not been placed in this cell.
        for hashed_x in range(floor(self.dpos[0] / EngineGlobals.collision_cell_size), floor((self.dpos[0] + self.collision_width - 1) / EngineGlobals.collision_cell_size) + 1):
            for hashed_y in range(floor(self.dpos[1] / EngineGlobals.collision_cell_size), floor((self.dpos[1] + self.collision_height - 1) / EngineGlobals.collision_cell_size) + 1):
                # first, check for collisions with any other sprites in this cell
                for collide_with in PhysicsSprite.collision_lists.setdefault(hashed_y * len(EngineGlobals.platform) + hashed_x, []):
                    if not isinstance(collide_with, PhysicsSprite):
                        continue
                    if ( collide_with.dpos[0] + collide_with.collision_width < self.dpos[0]
                    or collide_with.dpos[1] + collide_with.collision_height < self.dpos[1]
                    or collide_with.dpos[0] > self.dpos[0] + self.collision_width
                    or collide_with.dpos[1] > self.dpos[1] + self.collision_height ):
                        continue
                    self.on_PhysicsSprite_collided(collide_with)
                    collide_with.on_PhysicsSprite_collided(self)
                # then, add this sprite to the cell
                PhysicsSprite.collision_lists[hashed_y * len(EngineGlobals.platform) + hashed_x].append(self)

        # update position according to current speed
        self.dpos[0] += self.speed[0]
        self.dpos[1] += self.speed[1]

        # finally, update the x and y coords so that pyglet will know where to draw the sprite
        self.x, self.y = int(self.dpos[0] - EngineGlobals.our_screen.x), int(self.dpos[1] - EngineGlobals.our_screen.y)
    
    def destroy(self):
        EngineGlobals.delete_us.add(self)

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
    left_right_margin = 200
    top_bottom_margin = 96

    def __init__(self):
        self.x = 0
        self.y = 0

    # self.x is screen position
    # kenny.dpos[0] is x 1 is y
    def updateloop(self, dt):
        if (EngineGlobals.kenny.dpos[0] - self.x) < Screen.left_right_margin:
            self.x = int(EngineGlobals.kenny.dpos[0]) - Screen.left_right_margin

        kennys_belly = int(EngineGlobals.kenny.dpos[0]) + EngineGlobals.kenny.collision_width
        screen_redge = self.x + EngineGlobals.width

        if kennys_belly >= screen_redge - Screen.left_right_margin:
            self.x = kennys_belly - EngineGlobals.width + Screen.left_right_margin

        if (EngineGlobals.kenny.dpos[1]) - self.y < Screen.top_bottom_margin:
            self.y = int(EngineGlobals.kenny.dpos[1]) - Screen.top_bottom_margin

        kennys_head = int(EngineGlobals.kenny.dpos[1]) + EngineGlobals.kenny.collision_height
        screen_top = self.y + EngineGlobals.height
        if kennys_head >= screen_top - Screen.top_bottom_margin:
            self.y = kennys_head - EngineGlobals.height + Screen.top_bottom_margin
