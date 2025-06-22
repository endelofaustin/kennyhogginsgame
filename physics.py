import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from functools import partial
from math import floor
from enum import Enum
from lifecycle import GameObject
from magic_map import ChunkEdge
from math import floor

# PhysicsSprite represents a sprite that honors the laws of physics.
# It contains an update method that will alter the sprite's position according
# to speed and gravity, and stop moving when it collides with other solid
# objects.
class SpriteBatch(Enum):
    BACK = 1
    FRONT = 2

class PhysicsSprite(GameObject):
    collision_lists = {}

    # constructor
    def __init__(self, sprite_initializer : dict, starting_chunk):
        self.sprite_initializer = sprite_initializer

        self.landed = False

        resource_images = self.getResourceImages()
        self.resource_images = dict()

        for k, resource_id in resource_images.items():
            if isinstance(resource_id, dict) and 'rows' in resource_id and 'columns' in resource_id:
                self.resource_images[k] = pyglet.image.Animation.from_image_sequence(
                    pyglet.image.ImageGrid(
                        pyglet.resource.image(
                            resource_id['file'],
                            flip_x=resource_id.get('flip_x')
                        ),
                        rows=resource_id['rows'],
                        columns=resource_id['columns']
                    ),
                    duration=resource_id['duration'],
                    loop=resource_id['loop']
                )
            elif isinstance(resource_id, dict) and 'file' in resource_id:
                self.resource_images[k] = pyglet.resource.image(resource_id['file'])
            else:
                self.resource_images[k] = pyglet.resource.image(resource_id)
            if isinstance(resource_id, dict) and 'anchors' in resource_id:
                if isinstance(self.resource_images[k], pyglet.image.Animation):
                    for anchor_item in zip(self.resource_images[k].frames, resource_id['anchors']):
                        anchor_item[0].image.anchor_x = anchor_item[1][0]
                        anchor_item[0].image.anchor_y = anchor_item[1][1]
                else:
                    self.resource_images[k].anchor_x = resource_id['anchors'][0]
                    self.resource_images[k].anchor_y = resource_id['anchors'][1]

        group = EngineGlobals.sprites_front_group if sprite_initializer['group'] == 'FRONT' else EngineGlobals.sprites_back_group
        self.sprite = pyglet.sprite.Sprite(img=next(iter(self.resource_images.values())), batch=EngineGlobals.main_batch, group=group)
        if 'starting_position' in sprite_initializer:
            self.sprite.x = EngineGlobals.screen_x(sprite_initializer['starting_position'][0])
            self.sprite.y = EngineGlobals.screen_y(sprite_initializer['starting_position'][1])

        # if collision_width and collision_height are not provided, calculate them from the width and height
        # of the provided image/animation
        if self.getStaticBoundingBox():
            (self.collision_width, self.collision_height) = self.getStaticBoundingBox()
        elif len(self.resource_images) > 0:
            if isinstance(self.resource_images[next(iter(self.resource_images))], pyglet.image.AbstractImage):
                self.collision_width = self.resource_images[next(iter(self.resource_images))].width * EngineGlobals.scale_factor
                self.collision_height = self.resource_images[next(iter(self.resource_images))].height * EngineGlobals.scale_factor
            elif isinstance(self.resource_images[next(iter(self.resource_images))], pyglet.image.Animation):
                self.collision_width = self.resource_images[next(iter(self.resource_images))].get_max_width() * EngineGlobals.scale_factor
                self.collision_height = self.resource_images[next(iter(self.resource_images))].get_max_height() * EngineGlobals.scale_factor
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
        # every sprite must start out in a given chunk of the map (though it may be hidden)
        self.current_chunk = starting_chunk

        # self.show_bbox = pyglet.shapes.MultiLine(
        #     (float(EngineGlobals.screen_x(self.x_position)), float(EngineGlobals.screen_y(self.y_position))),
        #     (float(EngineGlobals.screen_x(self.x_position + self.collision_width)), float(EngineGlobals.screen_y(self.y_position))),
        #     (float(EngineGlobals.screen_x(self.x_position + self.collision_width)), float(EngineGlobals.screen_y(self.y_position + self.collision_height))),
        #     (float(EngineGlobals.screen_x(self.x_position)), float(EngineGlobals.screen_y(self.y_position + self.collision_height))),
        #     closed=True,
        #     color=(255, 255, 255, 255),
        #     batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_front
        # )

    # pickler
    def __getstate__(self):
        return self.sprite_initializer.copy()

    # unpickler
    def __setstate__(self, state):
        if 'sprite_type' in state:
            self.__init__(state, None)
        else:
            print("unable to unpickle from {}".format(str(state)))

    def get_collision_cell_hashes(self):
        for hashed_x in range(floor(self.x_position / EngineGlobals.collision_cell_size), floor((self.x_position + self.collision_width - 1) / EngineGlobals.collision_cell_size) + 1):
            for hashed_y in range(floor(self.y_position / EngineGlobals.collision_cell_size), floor((self.y_position + self.collision_height - 1) / EngineGlobals.collision_cell_size) + 1):
                yield (hashed_x, hashed_y)

    def get_all_colliding_objects(self):
        # Collisions with other sprites. So what's going on here actually?
        # 1. At the start of each update loop, we initialize an empty dict, PhysicsSprite.collision_lists.
        #    The dict will represent a grid in game space, with each cell 64 pixels square, about the
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
            for collide_with in PhysicsSprite.collision_lists.setdefault((hashed_x, hashed_y), []):
                if not isinstance(collide_with, PhysicsSprite):
                    continue
                if ( collide_with.x_position + collide_with.collision_width < self.x_position
                or collide_with.y_position + collide_with.collision_height < self.y_position
                or collide_with.x_position > self.x_position + self.collision_width
                or collide_with.y_position > self.y_position + self.collision_height ):
                    continue
                found_objects.add(collide_with)
        return found_objects

    def collide_with_chunk_tiles(self, x, y) -> bool:
        # move upward or downward to the correct starting y-chunk if needed
        y_chunk = self.current_chunk
        y_check = y_chunk.height - floor((y - y_chunk.coalesced_y) / EngineGlobals.tile_size) - 1
        while y_check < 0 and ChunkEdge.TOP in y_chunk.adjacencies:
            y_chunk = y_chunk.adjacencies[ChunkEdge.TOP]
            y_check = y_chunk.height - floor((y - y_chunk.coalesced_y) / EngineGlobals.tile_size) - 1
        while y_check >= y_chunk.height and ChunkEdge.BOTTOM in y_chunk.adjacencies:
            y_chunk = y_chunk.adjacencies[ChunkEdge.BOTTOM]
            y_check = y_chunk.height - floor((y - y_chunk.coalesced_y) / EngineGlobals.tile_size) - 1

        # loop over y-chunks
        #print("starting at the bottom in tile {} which is foot position {}".format(y_check, y))
        while y_chunk.coalesced_y + (y_chunk.height - 1 - y_check) * EngineGlobals.tile_size < y + self.collision_height:
            # move leftward or rightward to the correct starting x-chunk if needed
            x_chunk = y_chunk
            x_check = floor((x - x_chunk.coalesced_x) / EngineGlobals.tile_size)
            while x_check < 0 and ChunkEdge.LEFT in x_chunk.adjacencies:
                x_chunk = x_chunk.adjacencies[ChunkEdge.LEFT]
                x_check = floor((x - x_chunk.coalesced_x) / EngineGlobals.tile_size)
            while x_check >= x_chunk.width and ChunkEdge.RIGHT in x_chunk.adjacencies:
                x_chunk = x_chunk.adjacencies[ChunkEdge.RIGHT]
                x_check = floor((x - x_chunk.coalesced_x) / EngineGlobals.tile_size)

            # loop over x-chunks
            while x_check * EngineGlobals.tile_size + x_chunk.coalesced_x < x + self.collision_width:
                if x_check < 0 or x_check >= x_chunk.width or y_check < 0 or y_check >= x_chunk.height:
                    self.on_PhysicsSprite_collided()
                    return True
                else:
                    block = x_chunk.platform[y_check][x_check]
                    if block == 1:
                        self.on_PhysicsSprite_collided()
                        return True
                    elif hasattr(block, "solid") and block.solid == True:
                        self.on_PhysicsSprite_collided(block, x_chunk, x_check, y_check)
                        return True
                x_check += 1
                if x_check >= x_chunk.width:
                    #increment to the next x-chunk rightward
                    if ChunkEdge.RIGHT not in x_chunk.adjacencies:
                        break
                    x_chunk = x_chunk.adjacencies[ChunkEdge.RIGHT]
                    x_check = 0

            y_check -= 1
            if y_check < 0:
                # increment to the next y-chunk upward
                if ChunkEdge.TOP not in y_chunk.adjacencies:
                    break
                y_chunk = y_chunk.adjacencies[ChunkEdge.TOP]
                y_check = y_chunk.height - floor((y - y_chunk.coalesced_y) / EngineGlobals.tile_size)

        return False

    # this function is called for each sprite during the main update loop
    def updateloop(self, dt):
        if not self.current_chunk:
            return
        if self.current_chunk.hidden:
            return

        callbacks = []

        if self.hasGravity():
            # accelerate downwards by a certain amount
            self.y_speed = Decimal(self.y_speed) - Decimal('.6')
            # terminal velocity is 20 for now, so we won't move any faster than that
            if self.y_speed < -20:
                self.y_speed = -20

        # dt could be large enough to cause a sprite to move entirely through another sprite or block.
        # if so, cut it up into 32-pixel movements in a loop
        max_x_dt = Decimal(EngineGlobals.tile_size - 1) / abs(self.x_speed) if self.x_speed != Decimal(0) else EngineGlobals.tile_size
        max_y_dt = Decimal(EngineGlobals.tile_size - 1) / abs(self.y_speed) if self.y_speed != Decimal(0) else EngineGlobals.tile_size
        max_dt = min(max_x_dt, max_y_dt)

        # cap it to at most 3 movement checks (3 tiles, 96 pixels)
        for update_count in range(3):
            this_dt = min(max_dt, Decimal(dt))
            dt = Decimal(dt) - max_dt

            # x_position is x, y_position is y
            # position plus speed is equal to new potential location
            new_x = self.x_position + self.x_speed * this_dt
            new_y = self.y_position + self.y_speed * this_dt

            # upward or downward collisions
            if Decimal(self.y_speed) != Decimal(0):
                # if one of those tiles is solid, time to cease all vertical movement!
                if self.collide_with_chunk_tiles(self.x_position, new_y):
                    if self.y_speed < 0:
                        # vertically snap the sprite so its feet are at the pixel directly
                        # above the tile
                        self.y_position = floor((new_y + EngineGlobals.tile_size) / EngineGlobals.tile_size) * EngineGlobals.tile_size
                        if not self.landed:
                            self.landed = True
                            callbacks.append(self.on_PhysicsSprite_landed)
                    elif self.y_speed > 0:
                        self.y_position = floor((new_y + self.collision_height - 1) / EngineGlobals.tile_size) * EngineGlobals.tile_size - self.collision_height - 1
                    if self.y_position < self.current_chunk.coalesced_y \
                            and ChunkEdge.BOTTOM not in self.current_chunk.adjacencies:
                        self.y_position = self.current_chunk.coalesced_y
                        if not self.landed:
                            self.landed = True
                            callbacks.append(self.on_PhysicsSprite_landed)
                    elif self.y_position + self.collision_height > self.current_chunk.coalesced_y + (self.current_chunk.height * EngineGlobals.tile_size) \
                            and ChunkEdge.TOP not in self.current_chunk.adjacencies:
                        self.y_position = self.current_chunk.coalesced_y + (self.current_chunk.height * EngineGlobals.tile_size) - self.collision_height
                    self.y_speed = Decimal(0)
                    callbacks.append(self.on_PhysicsSprite_collided)
                else:
                    self.landed = False

            # left or right collisions
            if Decimal(self.x_speed) != Decimal(0):
                if self.collide_with_chunk_tiles(new_x, self.y_position):
                    # horizontally snap the sprite so it's not embedded in a block
                    if self.x_speed < 0:
                        self.x_position = floor((new_x + EngineGlobals.tile_size) / EngineGlobals.tile_size) * EngineGlobals.tile_size
                    elif self.x_speed > 0:
                        self.x_position = floor((new_x + self.collision_width) / EngineGlobals.tile_size) * EngineGlobals.tile_size - self.collision_width - 1
                    if self.x_position < self.current_chunk.coalesced_x \
                            and ChunkEdge.LEFT not in self.current_chunk.adjacencies:
                        self.x_position = self.current_chunk.coalesced_x
                    elif self.x_position + self.collision_width > self.current_chunk.coalesced_x + (self.current_chunk.width * EngineGlobals.tile_size) \
                            and ChunkEdge.RIGHT not in self.current_chunk.adjacencies:
                        self.x_position = self.current_chunk.coalesced_x + (self.current_chunk.width * EngineGlobals.tile_size) - self.collision_width
                    self.x_speed = 0
                    callbacks.append(self.on_PhysicsSprite_collided)

            # check for collisions with other sprites
            for collide_with in self.get_all_colliding_objects():
                callbacks.append(partial(self.on_PhysicsSprite_collided, collide_with))
                callbacks.append(partial(collide_with.on_PhysicsSprite_collided, self))
            # add this sprite to the cells it's touching
            for (hashed_x, hashed_y) in self.get_collision_cell_hashes():
                PhysicsSprite.collision_lists[(hashed_x, hashed_y)].append(self)

            # update position according to current speed
            self.x_position = Decimal(self.x_position) + self.x_speed * this_dt
            self.y_position = Decimal(self.y_position) + self.y_speed * this_dt

            # move to a new chunk?
            while self.x_position - self.current_chunk.coalesced_x < 0 and ChunkEdge.LEFT in self.current_chunk.adjacencies:
                self.current_chunk = self.current_chunk.adjacencies[ChunkEdge.LEFT]
            while self.x_position + self.collision_width >= self.current_chunk.coalesced_x + self.current_chunk.width * EngineGlobals.tile_size and ChunkEdge.RIGHT in self.current_chunk.adjacencies:
                self.current_chunk = self.current_chunk.adjacencies[ChunkEdge.RIGHT]
            while self.y_position - self.current_chunk.coalesced_y < 0 and ChunkEdge.BOTTOM in self.current_chunk.adjacencies:
                self.current_chunk = self.current_chunk.adjacencies[ChunkEdge.BOTTOM]
            while self.y_position + self.collision_height >= self.current_chunk.coalesced_y + self.current_chunk.height * EngineGlobals.tile_size and ChunkEdge.TOP in self.current_chunk.adjacencies:
                self.current_chunk = self.current_chunk.adjacencies[ChunkEdge.TOP]

            # exit the loop once we've processed all needed movements
            if dt <= 0:
                break

        # process callbacks
        for cb in callbacks:
            cb()

        # finally, update the x and y coords so that pyglet will know where to draw the sprite
        self.sprite.x = float(EngineGlobals.screen_x(self.x_position))
        self.sprite.y = float(EngineGlobals.screen_y(self.y_position))
        if hasattr(self, 'show_bbox'):
            self.show_bbox.x = float(EngineGlobals.screen_x(self.x_position))
            self.show_bbox.y = float(EngineGlobals.screen_y(self.y_position))

        # TODO: do we need to set sprite.visible = False to improve performance, or does Pyglet take care of this on it's own?

    def getResourceImages(self):
        return None

    def getStaticBoundingBox(self):
        return None

    def hasGravity(self):
        return True

    def on_finalDeletion(self):
        self.sprite.delete()
        if hasattr(self, 'show_bbox'):
            self.show_bbox.delete()

    def on_PhysicsSprite_landed(self):
        pass

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        pass

# the Screen class tracks the positioning of the screen within the entire environment
class Screen():
    left_right_margin = 250
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
