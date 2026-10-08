import pyglet
from decimal import Decimal

from engineglobals import EngineGlobals
from physics import PhysicsSprite


class Enemy(PhysicsSprite):
    """Ground enemy with HP, stagger, knockback, chase, and a telegraphed lunge."""

    MAX_HP = 3
    DEATH_DELAY = 8
    PATROL_SPEED = Decimal("1.5")
    CHASE_SPEED = Decimal("2.4")
    CHASE_DISTANCE = Decimal("300")
    LUNGE_DISTANCE = Decimal("115")
    LUNGE_SPEED = Decimal("5.4")
    LUNGE_WINDUP = 18
    LUNGE_FRAMES = 12
    ATTACK_COOLDOWN = 95
    HIT_STUN_FRAMES = 11
    KNOCKBACK_SPEED = Decimal("5.8")
    PROJECTILE_DAMAGE = 1
    MELEE_DAMAGE = 2
    STOMP_DAMAGE = 2

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.max_hp = int(self.MAX_HP)
        self.hp = self.max_hp
        self.hit_count = 0
        self.patrol_direction = Decimal(1)
        self.turn_cooldown = 0
        self.hit_stun = 0
        self.attack_cooldown = 30
        self.attack_windup = 0
        self.lunge_frames = 0
        self.attack_direction = Decimal(1)
        self.is_dying = False
        self.death_done = False
        self.death_timer = -1

        if not hasattr(Enemy, "hit_snd"):
            Enemy.hit_snd = pyglet.resource.media("glurk.wav", streaming=False)

        bar_width = max(22.0, float(self.default_collision_width))
        self.health_bar_width = bar_width
        self.health_bar_bg = pyglet.shapes.Rectangle(
            -1000,
            -1000,
            bar_width,
            7,
            color=(48, 38, 38),
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self.health_bar_fill = pyglet.shapes.Rectangle(
            -998,
            -998,
            bar_width - 4,
            3,
            color=(207, 62, 62),
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self._update_health_bar()

    def getResourceImages(self):
        return {"0": "mrspudl.png", "dead": "deadspud.png"}

    def _update_health_bar(self):
        if self.is_dying or self.death_done or self.hp <= 0:
            self.health_bar_bg.x = -1000
            self.health_bar_bg.y = -1000
            self.health_bar_fill.x = -1000
            self.health_bar_fill.y = -1000
            return

        sx = float(EngineGlobals.screen_x(self.x_position))
        bar_y_world = self.y_position + Decimal(str(self.default_collision_height + 7))
        sy = float(EngineGlobals.screen_y(bar_y_world))
        self.health_bar_bg.x = sx
        self.health_bar_bg.y = sy
        self.health_bar_fill.x = sx + 2
        self.health_bar_fill.y = sy + 2
        ratio = max(0.0, min(1.0, float(self.hp) / float(max(1, self.max_hp))))
        self.health_bar_fill.width = max(0.0, (self.health_bar_width - 4) * ratio)

    def start_death(self, delay_frames=None, dead_key="dead"):
        if self.is_dying or self.death_done:
            return
        self.is_dying = True
        self.hp = 0
        self.sprite.image = self.resource_images[dead_key]
        self.death_timer = self.DEATH_DELAY if delay_frames is None else delay_frames
        self._update_health_bar()

    def finish_death(self):
        if self.death_done:
            return
        self.death_done = True
        self.on_finish_death()
        self.destroy()

    def on_finish_death(self):
        pass

    def _current_player(self):
        return getattr(EngineGlobals, "kenny", None)

    def _choose_horizontal_speed(self):
        current_player = self._current_player()
        if current_player is None or current_player.current_chunk is not self.current_chunk:
            return self.PATROL_SPEED * self.patrol_direction

        distance = Decimal(current_player.x_position) - Decimal(self.x_position)
        if self.lunge_frames > 0:
            return self.LUNGE_SPEED * self.attack_direction
        if self.attack_windup > 0:
            return Decimal(0)

        if abs(distance) <= self.LUNGE_DISTANCE and self.attack_cooldown <= 0:
            self.attack_direction = Decimal(1) if distance > 0 else Decimal(-1)
            self.attack_windup = self.LUNGE_WINDUP
            self.attack_cooldown = self.ATTACK_COOLDOWN
            return Decimal(0)

        if abs(distance) <= self.CHASE_DISTANCE:
            speed = self.CHASE_SPEED
            if self.hp <= max(1, self.max_hp // 2):
                speed *= Decimal("1.3")
            return speed if distance > 0 else -speed
        return self.PATROL_SPEED * self.patrol_direction

    def updateloop(self, dt):
        if self.is_dying or self.death_done:
            self.x_speed = Decimal(0)
            self.y_speed = Decimal(0)
            if self.is_dying and self.death_timer >= 0:
                self.death_timer -= 1
                if self.death_timer <= 0 and not self.death_done:
                    self.finish_death()
            self._update_health_bar()
            return

        if self.turn_cooldown > 0:
            self.turn_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.hit_stun > 0:
            self.hit_stun -= 1
            PhysicsSprite.updateloop(self, dt)
            self._update_health_bar()
            return

        if self.attack_windup > 0:
            self.attack_windup -= 1
            if self.attack_windup == 0:
                self.lunge_frames = self.LUNGE_FRAMES
        elif self.lunge_frames > 0:
            self.lunge_frames -= 1

        self.x_speed = self._choose_horizontal_speed()
        PhysicsSprite.updateloop(self, dt)
        self._update_health_bar()

    def make_it_jump(self):
        self.y_speed = Decimal(7)

    def _player_stomped_me(self, player):
        if self.is_dying or self.death_done:
            return False
        player_y_speed = Decimal(getattr(player, "y_speed", 0))
        if player_y_speed >= 0:
            return False
        enemy_mid = Decimal(self.y_position) + Decimal(str(self.default_collision_height * 0.55))
        player_bottom = Decimal(player.y_position)
        return player_bottom >= enemy_mid

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if collided_object is not None and type(collided_object).__name__ == "Player":
            if self._player_stomped_me(collided_object):
                self.take_damage(self.STOMP_DAMAGE, source_x=collided_object.x_position, knockback=True)
                collided_object.y_speed = Decimal("8.5")
                collided_object.landed = False
                # Player's own collision callback runs too. Give a tiny grace window
                # so a successful stomp does not also hurt Kenny on the same frame.
                collided_object.hit_cooldown = max(getattr(collided_object, "hit_cooldown", 0), 10)
            return

        # Physics can report the same tile collision through more than one callback.
        # Debounce the turnaround so the direction only flips once per wall impact.
        if collided_object is not None and hasattr(collided_object, "solid") and self.turn_cooldown == 0:
            self.patrol_direction *= Decimal(-1)
            self.turn_cooldown = 8
            if self.landed:
                self.make_it_jump()

    def on_PhysicsSprite_landed(self):
        pass

    def take_damage(self, damage=1, source_x=None, knockback=True):
        """Shared damage path for bullets, melee, stomps, and bosses."""
        if self.is_dying or self.death_done:
            return False

        damage = max(1, int(damage))
        self.hp = max(0, self.hp - damage)
        self.hit_count = self.max_hp - self.hp

        from gameplay import BloodSpurt

        BloodSpurt(self.x_position + Decimal(12), self.y_position + Decimal(12))
        try:
            type(self).hit_snd.play()
        except Exception:
            Enemy.hit_snd.play()

        if self.hp <= 0:
            self.start_death(delay_frames=self.DEATH_DELAY, dead_key="dead")
            return True

        self.hit_stun = self.HIT_STUN_FRAMES
        if knockback:
            if source_x is None:
                player = self._current_player()
                source_x = getattr(player, "x_position", self.x_position - 1)
            source_x = Decimal(str(source_x))
            direction = Decimal(1) if Decimal(self.x_position) >= source_x else Decimal(-1)
            self.x_speed = self.KNOCKBACK_SPEED * direction
            self.y_speed = max(Decimal(self.y_speed), Decimal("4.2"))
        self._update_health_bar()
        return True

    def getting_hit(self):
        self.take_damage(self.PROJECTILE_DAMAGE)

    def die_hard(self):
        if self.is_dying or self.death_done:
            return
        self.hp = 0
        self.start_death(delay_frames=self.DEATH_DELAY, dead_key="dead")

    def on_pokey(self):
        self.take_damage(self.MELEE_DAMAGE)

    def on_finalDeletion(self):
        if hasattr(self, "health_bar_bg"):
            self.health_bar_bg.delete()
        if hasattr(self, "health_bar_fill"):
            self.health_bar_fill.delete()
        super().on_finalDeletion()


class Doggy(Enemy):
    MAX_HP = 2
    PATROL_SPEED = Decimal("1.9")
    CHASE_SPEED = Decimal("3.0")
    LUNGE_SPEED = Decimal("6.0")

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
