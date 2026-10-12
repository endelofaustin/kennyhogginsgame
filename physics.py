import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from functools import partial
from math import floor
from enum import Enum
from lifecycle import GameObject
from magic_map import ChunkEdge

# PhysicsSprite represents a sprite that honors the laws of physics.
# It contains an update method that will alter the sprite's position according
# to speed and gravity, and stop moving when it collides with other solid
# objects.
class SpriteBatch(Enum):
    BACK = 1
    FRONT = 2

class PhysicsSprite(GameObject):
    collision_lists = {}

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

        if len(self.resource_images) > 0:
            first_resource = self.resource_images[next(iter(self.resource_images))]
            if isinstance(first_resource, pyglet.image.AbstractImage):
                self.default_collision_width = first_resource.width * EngineGlobals.scale_factor
                self.default_collision_height = first_resource.height * EngineGlobals.scale_factor
            elif isinstance(first_resource, pyglet.image.Animation):
                self.default_collision_width = first_resource.get_max_width() * EngineGlobals.scale_factor
                self.default_collision_height = first_resource.get_max_height() * EngineGlobals.scale_factor
        else:
            (self.default_collision_width, self.default_collision_height) = (0, 0)

        (self.x_speed, self.y_speed) = sprite_initializer['starting_speed']
        self.sprite.update(scale=EngineGlobals.scale_factor)
        (self.x_position, self.y_position) = sprite_initializer['starting_position']

        super().__init__(lifecycle_manager=sprite_initializer['lifecycle_manager'])
        self.current_chunk = starting_chunk

    def __getstate__(self):
        return self.sprite_initializer.copy()

    def __setstate__(self, state):
        if 'sprite_type' in state:
            self.__init__(state, None)
        else:
            print("unable to unpickle from {}".format(str(state)))

    def get_collision_cell_hashes(self):
        (collision_width, collision_height) = self.getCollisionBox()
        for hashed_x in range(floor(self.x_position / EngineGlobals.collision_cell_size), floor((self.x_position + collision_width - 1) / EngineGlobals.collision_cell_size) + 1):
            for hashed_y in range(floor(self.y_position / EngineGlobals.collision_cell_size), floor((self.y_position + collision_height - 1) / EngineGlobals.collision_cell_size) + 1):
                yield (hashed_x, hashed_y)

    def get_all_colliding_objects(self):
        found_objects = set()
        (collision_width, collision_height) = self.getCollisionBox()
        for (hashed_x, hashed_y) in self.get_collision_cell_hashes():
            for collide_with in PhysicsSprite.collision_lists.setdefault((hashed_x, hashed_y), []):
                if not isinstance(collide_with, PhysicsSprite):
                    continue
                (c_collision_width, c_collision_height) = collide_with.getCollisionBox()
                if (collide_with.x_position + c_collision_width < self.x_position
                        or collide_with.y_position + c_collision_height < self.y_position
                        or collide_with.x_position > self.x_position + collision_width
                        or collide_with.y_position > self.y_position + collision_height):
                    continue
                found_objects.add(collide_with)
        return found_objects

    def collide_with_chunk_tiles(self, x, y) -> bool:
        y_chunk = self.current_chunk
        y_check = y_chunk.height - floor((y - y_chunk.coalesced_y) / EngineGlobals.tile_size) - 1
        while y_check < 0 and ChunkEdge.TOP in y_chunk.adjacencies:
            y_chunk = y_chunk.adjacencies[ChunkEdge.TOP]
            y_check = y_chunk.height - floor((y - y_chunk.coalesced_y) / EngineGlobals.tile_size) - 1
        while y_check >= y_chunk.height and ChunkEdge.BOTTOM in y_chunk.adjacencies:
            y_chunk = y_chunk.adjacencies[ChunkEdge.BOTTOM]
            y_check = y_chunk.height - floor((y - y_chunk.coalesced_y) / EngineGlobals.tile_size) - 1

        (collision_width, collision_height) = self.getCollisionBox()

        while y_chunk.coalesced_y + (y_chunk.height - 1 - y_check) * EngineGlobals.tile_size < y + collision_height:
            x_chunk = y_chunk
            x_check = floor((x - x_chunk.coalesced_x) / EngineGlobals.tile_size)
            while x_check < 0 and ChunkEdge.LEFT in x_chunk.adjacencies:
                x_chunk = x_chunk.adjacencies[ChunkEdge.LEFT]
                x_check = floor((x - x_chunk.coalesced_x) / EngineGlobals.tile_size)
            while x_check >= x_chunk.width and ChunkEdge.RIGHT in x_chunk.adjacencies:
                x_chunk = x_chunk.adjacencies[ChunkEdge.RIGHT]
                x_check = floor((x - x_chunk.coalesced_x) / EngineGlobals.tile_size)

            while x_check * EngineGlobals.tile_size + x_chunk.coalesced_x < x + collision_width:
                if x_check < 0 or x_check >= x_chunk.width or y_check < 0 or y_check >= x_chunk.height:
                    self.on_PhysicsSprite_collided()
                    return True
                block = x_chunk.platform[y_check][x_check]
                if block == 1:
                    self.on_PhysicsSprite_collided()
                    return True
                if hasattr(block, "solid") and block.solid is True:
                    self.on_PhysicsSprite_collided(block, x_chunk, x_check, y_check)
                    return True
                x_check += 1
                if x_check >= x_chunk.width:
                    if ChunkEdge.RIGHT not in x_chunk.adjacencies:
                        break
                    x_chunk = x_chunk.adjacencies[ChunkEdge.RIGHT]
                    x_check = 0

            y_check -= 1
            if y_check < 0:
                if ChunkEdge.TOP not in y_chunk.adjacencies:
                    break
                y_chunk = y_chunk.adjacencies[ChunkEdge.TOP]
                y_check = y_chunk.height - floor((y - y_chunk.coalesced_y) / EngineGlobals.tile_size)

        return False

    def updateloop(self, dt):
        if not self.current_chunk or self.current_chunk.hidden:
            return

        callbacks = []
        (collision_width, collision_height) = self.getCollisionBox()

        if self.hasGravity():
            self.y_speed = Decimal(self.y_speed) - Decimal('.6')
            if self.y_speed < -20:
                self.y_speed = Decimal(-20)

        max_x_dt = Decimal(EngineGlobals.tile_size - 1) / abs(self.x_speed) if self.x_speed != Decimal(0) else Decimal(EngineGlobals.tile_size)
        max_y_dt = Decimal(EngineGlobals.tile_size - 1) / abs(self.y_speed) if self.y_speed != Decimal(0) else Decimal(EngineGlobals.tile_size)
        max_dt = min(max_x_dt, max_y_dt)
        remaining_dt = Decimal(str(dt))

        # Process at most three substeps, but always subtract the amount we
        # actually processed. This avoids negative/incorrect remainder values
        # on short frames and makes collision behavior deterministic.
        for _ in range(3):
            if remaining_dt <= 0:
                break
            this_dt = min(max_dt, remaining_dt)
            remaining_dt -= this_dt

            new_x = self.x_position + self.x_speed * this_dt
            new_y = self.y_position + self.y_speed * this_dt

            if Decimal(self.y_speed) != Decimal(0):
                if self.collide_with_chunk_tiles(self.x_position, new_y):
                    if self.y_speed < 0:
                        self.y_position = floor((new_y + EngineGlobals.tile_size) / EngineGlobals.tile_size) * EngineGlobals.tile_size
                        if not self.landed:
                            self.landed = True
                            callbacks.append(self.on_PhysicsSprite_landed)
                    elif self.y_speed > 0:
                        self.y_position = floor((new_y + collision_height - 1) / EngineGlobals.tile_size) * EngineGlobals.tile_size - collision_height - 1
                    if self.y_position < self.current_chunk.coalesced_y and ChunkEdge.BOTTOM not in self.current_chunk.adjacencies:
                        self.y_position = self.current_chunk.coalesced_y
                        if not self.landed:
                            self.landed = True
                            callbacks.append(self.on_PhysicsSprite_landed)
                    elif self.y_position + collision_height > self.current_chunk.coalesced_y + (self.current_chunk.height * EngineGlobals.tile_size) and ChunkEdge.TOP not in self.current_chunk.adjacencies:
                        self.y_position = self.current_chunk.coalesced_y + (self.current_chunk.height * EngineGlobals.tile_size) - collision_height
                    self.y_speed = Decimal(0)
                    callbacks.append(self.on_PhysicsSprite_collided)
                else:
                    self.landed = False

            if Decimal(self.x_speed) != Decimal(0):
                if self.collide_with_chunk_tiles(new_x, self.y_position):
                    if self.x_speed < 0:
                        self.x_position = floor((new_x + EngineGlobals.tile_size) / EngineGlobals.tile_size) * EngineGlobals.tile_size
                    elif self.x_speed > 0:
                        self.x_position = floor((new_x + collision_width) / EngineGlobals.tile_size) * EngineGlobals.tile_size - collision_width - 1
                    if self.x_position < self.current_chunk.coalesced_x and ChunkEdge.LEFT not in self.current_chunk.adjacencies:
                        self.x_position = self.current_chunk.coalesced_x
                    elif self.x_position + collision_width > self.current_chunk.coalesced_x + (self.current_chunk.width * EngineGlobals.tile_size) and ChunkEdge.RIGHT not in self.current_chunk.adjacencies:
                        self.x_position = self.current_chunk.coalesced_x + (self.current_chunk.width * EngineGlobals.tile_size) - collision_width
                    self.x_speed = Decimal(0)
                    callbacks.append(self.on_PhysicsSprite_collided)

            for collide_with in self.get_all_colliding_objects():
                callbacks.append(partial(self.on_PhysicsSprite_collided, collide_with))
                callbacks.append(partial(collide_with.on_PhysicsSprite_collided, self))
            for (hashed_x, hashed_y) in self.get_collision_cell_hashes():
                PhysicsSprite.collision_lists[(hashed_x, hashed_y)].append(self)

            self.x_position = Decimal(self.x_position) + self.x_speed * this_dt
            self.y_position = Decimal(self.y_position) + self.y_speed * this_dt

            while self.x_position - self.current_chunk.coalesced_x < 0 and ChunkEdge.LEFT in self.current_chunk.adjacencies:
                self.current_chunk = self.current_chunk.adjacencies[ChunkEdge.LEFT]
            while self.x_position + collision_width >= self.current_chunk.coalesced_x + self.current_chunk.width * EngineGlobals.tile_size and ChunkEdge.RIGHT in self.current_chunk.adjacencies:
                self.current_chunk = self.current_chunk.adjacencies[ChunkEdge.RIGHT]
            while self.y_position - self.current_chunk.coalesced_y < 0 and ChunkEdge.BOTTOM in self.current_chunk.adjacencies:
                self.current_chunk = self.current_chunk.adjacencies[ChunkEdge.BOTTOM]
            while self.y_position + collision_height >= self.current_chunk.coalesced_y + self.current_chunk.height * EngineGlobals.tile_size and ChunkEdge.TOP in self.current_chunk.adjacencies:
                self.current_chunk = self.current_chunk.adjacencies[ChunkEdge.TOP]

        for cb in callbacks:
            cb()

        self.sprite.x = float(EngineGlobals.screen_x(self.x_position))
        self.sprite.y = float(EngineGlobals.screen_y(self.y_position))
        if hasattr(self, 'show_bbox'):
            self.show_bbox.position = (float(EngineGlobals.screen_x(self.x_position)), float(EngineGlobals.screen_y(self.y_position)))

    def getResourceImages(self):
        return None

    def getCollisionBox(self):
        return (self.default_collision_width, self.default_collision_height)

    def getDefaultBox(self):
        return (self.default_collision_width, self.default_collision_height)

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

class Screen():
    left_right_margin = 250
    top_bottom_margin = 96

    def __init__(self):
        self.x = 0
        self.y = 0

    def updateloop(self, dt):
        (kenny_width, kenny_height) = EngineGlobals.kenny.getDefaultBox()

        if (EngineGlobals.kenny.x_position - self.x) < Screen.left_right_margin:
            self.x = int(EngineGlobals.kenny.x_position) - Screen.left_right_margin

        kennys_belly = int(EngineGlobals.kenny.x_position) + kenny_width
        screen_redge = self.x + EngineGlobals.width

        if kennys_belly >= screen_redge - Screen.left_right_margin:
            self.x = kennys_belly - EngineGlobals.width + Screen.left_right_margin

        if EngineGlobals.kenny.y_position - self.y < Screen.top_bottom_margin:
            self.y = int(EngineGlobals.kenny.y_position) - Screen.top_bottom_margin

        kennys_head = int(EngineGlobals.kenny.y_position) + kenny_height
        screen_top = self.y + EngineGlobals.height
        if kennys_head >= screen_top - Screen.top_bottom_margin:
            self.y = kennys_head - EngineGlobals.height + Screen.top_bottom_margin
