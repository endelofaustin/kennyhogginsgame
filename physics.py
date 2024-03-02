import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from math import floor
from enum import Enum
from lifecycle import GameObject

# PhysicsSprite represents a sprite that honors the laws of physics.
# It contains an update method that will alter the sprite's position according
# to speed and gravity.
class SpriteBatch(Enum):
    BACK = 1
    FRONT = 2

class PhysicsSprite(GameObject):
    collision_lists = {}

    # constructor
    def __init__(self, sprite_initializer : dict):
        self.sprite_initializer = sprite_initializer

        self.landed = False

        resource_images = self.getResourceImages()
        self.resource_images = dict()

        for k, resource_id in resource_images.items():
            if isinstance(resource_id, dict):
                self.resource_images[k] = pyglet.image.Animation.from_image_sequence(pyglet.image.ImageGrid(pyglet.resource.image(resource_id['file']), rows=resource_id['rows'], columns=resource_id['columns']), duration=resource_id['duration'], loop=resource_id['loop'])
            else:
                self.resource_images[k] = pyglet.resource.image(resource_id)

        group = EngineGlobals.sprites_front_group if sprite_initializer['group'] == 'FRONT' else EngineGlobals.sprites_back_group
        self.sprite = pyglet.sprite.Sprite(img=next(iter(self.resource_images.values())), batch=EngineGlobals.main_batch, group=group)

        # if collision_width and collision_height are not provided, calculate them from the width and height
        # of the provided image/animation
        if self.getStaticBoundingBox():
            (self.collision_width, self.collision_height) = self.getStaticBoundingBox()
        elif len(self.resource_images) > 0:
            if isinstance(self.resource_images[next(iter(self.resource_images))], pyglet.image.AbstractImage):
                self.collision_width = self.resource_images[next(iter(self.resource_images))].width
                self.collision_height = self.resource_images[next(iter(self.resource_images))].height
            elif isinstance(self.resource_images[next(iter(self.resource_images))], pyglet.image.Animation):
                self.collision_width = self.resource_images[next(iter(self.resource_images))].get_max_width()
                self.collision_height = self.resource_images[next(iter(self.resource_images))].get_max_height()
        else:
            (self.collision_width, self.collision_height) = (0, 0)

        # the 'x_speed' and 'y_speed' members are Decimal representations of the sprite's speed
        # at this moment; each time the game loop runs, the sprite will move by that amount;
        # self.x_speed is the left-to-right speed (negative is left, positive is right);
        # self.y_speed is the bottom-to-top speed (in defiance of convention, negative is down and
        # positive is up)
        (self.x_speed, self.y_speed) = sprite_initializer['starting_speed']

        # scale up the image
        self.sprite.update(scale=EngineGlobals.scale_factor)

        # initialize the x_position and y_position members as a Decimal representation of the
        # sprite's position in the environment - self.x_position is the 'x' or left-to-right
        # coordinate, self.y_position is the 'y' or bottom-to-top coordinate
        (self.x_position, self.y_position) = sprite_initializer['starting_position']

        super().__init__(lifecycle_manager=sprite_initializer['lifecycle_manager'])

    # pickler
    def __getstate__(self):
        return self.sprite_initializer.copy()

    # unpickler
    def __setstate__(self, state):
        if 'sprite_type' in state:
            self.__init__(state)
        else:
            print("unable to unpickle from {}".format(str(state)))

    def get_collision_cell_hashes(self):
        for hashed_x in range(floor(self.x_position / EngineGlobals.collision_cell_size), floor((self.x_position + self.collision_width - 1) / EngineGlobals.collision_cell_size) + 1):
            for hashed_y in range(floor(self.y_position / EngineGlobals.collision_cell_size), floor((self.y_position + self.collision_height - 1) / EngineGlobals.collision_cell_size) + 1):
                yield (hashed_x, hashed_y)

    def get_all_colliding_objects(self):
        # Collisions with other sprites. So what's going on here actually?
        # 1. At the start of each update loop, we initialize an empty dict, PhysicsSprite.collision_lists.
        #    The dict will represent a grid in game space, with each cell 32 pixels square, about the
        #    average size of a sprite.
        # 2. Here in the update function, we are calculating the hashed_x and hashed_y of all possible
        #    cells that the sprite might be touching at this moment.
        # 3. We append the sprite in a list stored at each cell.
        # 4. We do a closer check of all other sprites that have been placed in the same cell, to see if
        #    their bounding boxes collide or not; but we no longer have to check every other sprite that
        #    has not been placed in this cell.
        # 5. Because each sprite can be touching multiple cells and will be added to the list for each
        #    cell, we are going to potentially find that sprite multiple times when enumerating over
        #    the lists. We don't want to initiate the collision detection logic multiple times, only
        #    once per unique sprite. So store the found sprites in a set and then when we try to add
        #    them to the set multiple times, it will ignore the later times and return just the unique
        #    set of sprites at the end.
        found_objects = set()
        for (hashed_x, hashed_y) in self.get_collision_cell_hashes():
            for collide_with in PhysicsSprite.collision_lists.setdefault(hashed_y * len(EngineGlobals.game_map.platform) + hashed_x, []):
                if not isinstance(collide_with, PhysicsSprite):
                    continue
                if ( collide_with.x_position + collide_with.collision_width < self.x_position
                or collide_with.y_position + collide_with.collision_height < self.y_position
                or collide_with.x_position > self.x_position + self.collision_width
                or collide_with.y_position > self.y_position + self.collision_height ):
                    continue
                found_objects.add(collide_with)
        return found_objects

    # this function is called for each sprite during the main update loop
    def updateloop(self, dt):
        if self.hasGravity():
            # accelerate downwards by a certain amount
            self.y_speed = Decimal(self.y_speed) - Decimal('.6')
            # terminal velocity is 20 for now, so we won't move any faster than that
            if self.y_speed < -20:
                self.y_speed = -20

        # x_position is x, y_position is y
        # position plus speed is equal to new potential location
        new_x = self.x_position + self.x_speed
        new_y = self.y_position + self.y_speed

        # upward or downward collisions
        if self.y_speed != 0:
            # first, check if trying to move off the bottom or top of the screen
            if new_y < 0 or new_y + self.collision_height >= len(EngineGlobals.game_map.platform) * 32:
                # if so, check if we should trigger landing event (moving downward and not already grounded)
                if self.y_speed < 0 and not self.landed:
                    self.landed = True
                    self.on_PhysicsSprite_landed()
                # regardless, stop all downward or upward motion
                self.y_speed = 0
                self.on_PhysicsSprite_collided()
            # otherwise, we are safe to see where we are in the environment and whether we are about to collide
            # with a solid block
            else:
                # from the environment, retrieve the tiles at Kenny's lower left foot, lower right foot, upper left,
                # and upper right
                # since this is only checking for up/down collisions, it's important that we use the new y coordinates
                # (new_y) but the original x coordinates (self.x_position)
                left_foot_tile = EngineGlobals.game_map.platform[len(EngineGlobals.game_map.platform) - floor(new_y / 32) - 1][floor(self.x_position/32)]
                right_foot_tile = EngineGlobals.game_map.platform[len(EngineGlobals.game_map.platform) - floor(new_y / 32) - 1][floor((self.x_position + self.collision_width - 1)/32)]
                left_head_tile = EngineGlobals.game_map.platform[len(EngineGlobals.game_map.platform) - floor((new_y + self.collision_height - 1) / 32) - 1][floor(self.x_position/32)]
                right_head_tile = EngineGlobals.game_map.platform[len(EngineGlobals.game_map.platform) - floor((new_y + self.collision_height - 1) / 32) - 1][floor((self.x_position + self.collision_width - 1)/32)]
                # if one of those tiles is solid, time to cease all vertical movement!
                if (self.if_solid(left_foot_tile) == True or self.if_solid(right_foot_tile) == True
                        or self.if_solid(left_head_tile) == True or self.if_solid(right_head_tile) == True):
                    if self.y_speed < 0 and not self.landed:
                        self.landed = True
                        self.on_PhysicsSprite_landed()
                    self.y_speed = 0
                    self.on_PhysicsSprite_collided()
                else:
                    self.landed = False

        # left or right collisions
        if self.x_speed != 0:
            if new_x < 0 or new_x + self.collision_width >= len(EngineGlobals.game_map.platform[0]) * 32:
                self.x_speed = 0
                self.on_PhysicsSprite_collided()
            else:
                left_foot_tile = EngineGlobals.game_map.platform[len(EngineGlobals.game_map.platform) - floor(self.y_position / 32) - 1][floor(new_x/32)]
                right_foot_tile = EngineGlobals.game_map.platform[len(EngineGlobals.game_map.platform) - floor(self.y_position / 32) - 1][floor((new_x + self.collision_width - 1)/32)]
                left_head_tile = EngineGlobals.game_map.platform[len(EngineGlobals.game_map.platform) - floor((self.y_position + self.collision_height - 1) / 32) - 1][floor(new_x/32)]
                right_head_tile = EngineGlobals.game_map.platform[len(EngineGlobals.game_map.platform) - floor((self.y_position + self.collision_height - 1) / 32) - 1][floor((new_x + self.collision_width - 1)/32)]
                if (self.if_solid(left_foot_tile) == True or self.if_solid(right_foot_tile) == True
                        or self.if_solid(left_head_tile) == True or self.if_solid(right_head_tile) == True):
                    self.x_speed = 0
                    self.on_PhysicsSprite_collided()

        # check for collisions with other sprites
        for collide_with in self.get_all_colliding_objects():
            self.on_PhysicsSprite_collided(collide_with)
            collide_with.on_PhysicsSprite_collided(self)
        # add this sprite to the cells it's touching
        for (hashed_x, hashed_y) in self.get_collision_cell_hashes():
            PhysicsSprite.collision_lists[hashed_y * len(EngineGlobals.game_map.platform) + hashed_x].append(self)

        # update position according to current speed
        self.x_position = Decimal(self.x_position) + self.x_speed
        self.y_position = Decimal(self.y_position) + self.y_speed

        # finally, update the x and y coords so that pyglet will know where to draw the sprite
        self.sprite.x, self.sprite.y = int(self.x_position - EngineGlobals.our_screen.x), int(self.y_position - EngineGlobals.our_screen.y)

    def getResourceImages(self):
        return None

    def getStaticBoundingBox(self):
        return None

    def hasGravity(self):
        return True

    def on_finalDeletion(self):
        self.sprite.delete()

    def on_PhysicsSprite_landed(self):
        pass

    def on_PhysicsSprite_collided(self, collided_object=None):
        pass

    def if_solid(self,block):
        if block == 1:
            return True
        if  hasattr(block, "solid") and block.solid == True:
            return True
        return False

# the Screen class tracks the positioning of the screen within the entire environment
class Screen():
    left_right_margin = 200
    top_bottom_margin = 96

    def __init__(self):
        self.x = 0
        self.y = 0

    # self.x, self.y is screen position
    def updateloop(self, dt):
        if (EngineGlobals.kenny.x_position - self.x) < Screen.left_right_margin:
            self.x = int(EngineGlobals.kenny.x_position) - Screen.left_right_margin

        kennys_belly = int(EngineGlobals.kenny.x_position) + EngineGlobals.kenny.collision_width
        screen_redge = self.x + EngineGlobals.width

        if kennys_belly >= screen_redge - Screen.left_right_margin:
            self.x = kennys_belly - EngineGlobals.width + Screen.left_right_margin

        if (EngineGlobals.kenny.y_position) - self.y < Screen.top_bottom_margin:
            self.y = int(EngineGlobals.kenny.y_position) - Screen.top_bottom_margin

        kennys_head = int(EngineGlobals.kenny.y_position) + EngineGlobals.kenny.collision_height
        screen_top = self.y + EngineGlobals.height
        if kennys_head >= screen_top - Screen.top_bottom_margin:
            self.y = kennys_head - EngineGlobals.height + Screen.top_bottom_margin
