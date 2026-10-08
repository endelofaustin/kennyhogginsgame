import pyglet
from decimal import Decimal
from physics import *


class Enemy(PhysicsSprite):
    """Default ground enemy with predictable patrol/chase movement."""

    PATROL_SPEED = Decimal("1.5")
    CHASE_SPEED = Decimal("2.4")
    CHASE_DISTANCE = Decimal("300")

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.hit_count = 0
        self.patrol_direction = Decimal(1)
        self.turn_cooldown = 0
        self.is_dying = False
        self.death_done = False
        self.death_timer = -1

        if not hasattr(Enemy, "hit_snd"):
            Enemy.hit_snd = pyglet.resource.media("glurk.wav", streaming=False)

    def getResourceImages(self):
        return {"0": "mrspudl.png", "dead": "deadspud.png"}

    def start_death(self, delay_frames=6, dead_key="dead"):
        if self.is_dying or self.death_done:
            return
        self.is_dying = True
        self.sprite.image = self.resource_images[dead_key]
        self.death_timer = delay_frames

    def finish_death(self):
        if self.death_done:
            return
        self.death_done = True
        self.on_finish_death()
        self.destroy()

    def on_finish_death(self):
        pass

    def _choose_horizontal_speed(self):
        try:
            from engineglobals import EngineGlobals
            current_player = EngineGlobals.kenny
        except (AttributeError, ImportError):
            current_player = None

        if current_player is not None and current_player.current_chunk is self.current_chunk:
            distance = Decimal(current_player.x_position) - Decimal(self.x_position)
            if abs(distance) <= self.CHASE_DISTANCE:
                return self.CHASE_SPEED if distance > 0 else -self.CHASE_SPEED
        return self.PATROL_SPEED * self.patrol_direction

    def updateloop(self, dt):
        if self.is_dying or self.death_done:
            self.x_speed = Decimal(0)
            self.y_speed = Decimal(0)
            if self.is_dying and self.death_timer >= 0:
                self.death_timer -= 1
                if self.death_timer <= 0 and not self.death_done:
                    self.finish_death()
            return

        if self.turn_cooldown > 0:
            self.turn_cooldown -= 1
        self.x_speed = self._choose_horizontal_speed()
        PhysicsSprite.updateloop(self, dt)

    def make_it_jump(self):
        self.y_speed = Decimal(7)

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        # Physics can report the same tile collision through more than one callback.
        # Debounce the turnaround so the direction only flips once per wall impact.
        if collided_object is not None and hasattr(collided_object, "solid") and self.turn_cooldown == 0:
            self.patrol_direction *= Decimal(-1)
            self.turn_cooldown = 8
            if self.landed:
                self.make_it_jump()

    def on_PhysicsSprite_landed(self):
        pass

    def getting_hit(self):
        if self.is_dying or self.death_done:
            return
        from gameplay import BloodSpurt
        BloodSpurt(self.x_position + 12, self.y_position + 12)
        self.die_hard()

    def die_hard(self):
        if self.is_dying or self.death_done:
            return
        Enemy.hit_snd.play()
        self.start_death(delay_frames=6, dead_key="dead")

    def on_pokey(self):
        self.hit_count += 1
        if self.hit_count > 3:
            self.die_hard()


class Doggy(Enemy):
    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

    def getResourceImages(self):
        return {0: "doggy.png", "dead": "doggy.png"}


class Cardi(PhysicsSprite):
    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer, starting_chunk)

    def hasGravity(self):
        return True

    def getResourceImages(self):
        return {0: "bosses/cardi_tree-1.png.png"}
