# This is where we create game pieces to place on the board.

from pyglet.sprite import Sprite
import random
from engineglobals import EngineGlobals
from physics import PhysicsSprite


class Block:
    """Normal foreground/background tile."""

    block_kind = "normal"

    def __init__(self, tilesheet_idx, solid):
        group = EngineGlobals.tiles_front_group if solid else EngineGlobals.tiles_back_group
        self.sprite = Sprite(
            img=EngineGlobals.get_tile(tilesheet_idx),
            batch=EngineGlobals.main_batch,
            group=group,
            program=EngineGlobals.hintable_shader,
        )
        self.sprite.update(scale=EngineGlobals.scale_factor)
        self.sprite.visible = False
        self.tilesheet_idx = tilesheet_idx
        self.solid = solid

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["sprite"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__init__(state.get("tilesheet_idx", 0), state.get("solid", True))


class HazardBlock(Block):
    """Solid editor-placeable tile that damages Kenny on contact."""

    block_kind = "hazard"


class BreakableBlock(Block):
    """Solid tile that can be removed by sword/projectile-aware map logic."""

    block_kind = "breakable"

    def break_block(self):
        if hasattr(self, "sprite"):
            self.sprite.delete()
        self.solid = False


class Door(PhysicsSprite):
    def getResourceImages(self):
        return {0: "door-1.png"}

    def hasGravity(self):
        return False


class NirvanaFruit(PhysicsSprite):
    def __init__(self, sprite_initializer: dict, starting_chunk, destroy_after=None):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.destroy_after = destroy_after
        self.jump_timer = 0
        self.collected = False

    def getResourceImages(self):
        return {
            "0": {"file": "nirvana-fruit.png", "rows": 1, "columns": 6, "duration": 1 / 10, "loop": True},
            "get": {"file": "nirvana-fruit-get.png", "rows": 1, "columns": 6, "duration": 1 / 16, "loop": False},
        }

    def hasGravity(self):
        return False if self.destroy_after else True

    def updateloop(self, dt):
        if self.destroy_after:
            self.destroy_after -= 1
            if self.destroy_after <= 0:
                self.destroy()
        elif self.jump_timer <= 0:
            self.y_speed = 7
            self.x_speed = -5 if bool(random.getrandbits(1)) else 5
            self.jump_timer = 250
        else:
            self.jump_timer -= 1
        return super().updateloop(dt)

    def on_PhysicsSprite_landed(self):
        self.x_speed = 0

    def collect(self):
        self.destroy_after = 23
        self.sprite.image = self.resource_images["get"]
        self.collected = True
        self.x_speed, self.y_speed = (0, 0)


class Sword(PhysicsSprite):
    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer, starting_chunk)

    def getResourceImages(self):
        return {0: "sword.png"}

    def hasGravity(self):
        return False

    def on_PhysicsSprite_collided(self, collided_object=None, **kwargs):
        if collided_object and type(collided_object).__name__ == "Player":
            collided_object.has_sword = True
            if not collided_object.progress.sword_tutorial_seen:
                # Import lazily to avoid text/gamepiece import cycles.
                from text import MessageBox
                MessageBox(("Sword collected! Press C to slash enemies and breakable obstacles.", 2), 360)
                collided_object.progress.sword_tutorial_seen = True
            self.destroy()


class Scythe(PhysicsSprite):
    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer, starting_chunk)

    def getResourceImages(self):
        return {0: "scythe_thingy.png"}

    def hasGravity(self):
        return False

    def on_PhysicsSprite_collided(self, collided_object=None, **kwargs):
        if collided_object and type(collided_object).__name__ == "Player":
            collided_object.has_scythe = True
            self.destroy()
