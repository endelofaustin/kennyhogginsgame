"""Pompeii finale: the Toga Sisters shared-health boss encounter."""

import math
from decimal import Decimal

import pyglet

from enemies import Enemy
from engineglobals import EngineGlobals
from gamepieces import Door
from lifecycle import GameObject, LifeCycleManager
from physics import PhysicsSprite
from sprite import makeSprite


class TogaSister(Enemy):
    """One singer in the trio. All three feed damage into one shared health pool."""

    MAX_HP = 100
    PATROL_SPEED = Decimal(0)
    CHASE_SPEED = Decimal(0)
    CHASE_DISTANCE = Decimal(0)
    LUNGE_DISTANCE = Decimal(0)
    KNOCKBACK_SPEED = Decimal(0)

    def __init__(self, sprite_initializer, starting_chunk):
        self.controller = sprite_initializer["controller"]
        self.sister_name = sprite_initializer.get("sister_name", "Sister")
        self.toga_color = tuple(sprite_initializer.get("toga_color", (240, 230, 205)))
        self.hair_color = tuple(sprite_initializer.get("hair_color", (70, 45, 35)))
        self.target_x = Decimal(str(sprite_initializer["starting_position"][0]))
        self.target_y = Decimal(str(sprite_initializer["starting_position"][1]))
        self.sing_timer = 0.0
        self.hurt_timer = 0.0
        self.float_phase = float(sprite_initializer.get("float_phase", 0.0))
        self.defeated = False
        self.shapes = []
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.opacity = 0
        self.health_bar_bg.visible = False
        self.health_bar_fill.visible = False
        self._build_shapes()

    def getResourceImages(self):
        return {"0": "mrspudl.png", "dead": "deadspud.png"}

    def getCollisionBox(self):
        return (0, 0) if self.defeated else (44, 76)

    def hasGravity(self):
        return False

    def _update_health_bar(self):
        if hasattr(self, "health_bar_bg"):
            self.health_bar_bg.visible = False
        if hasattr(self, "health_bar_fill"):
            self.health_bar_fill.visible = False

    def _build_shapes(self):
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_front
        self.halo = pyglet.shapes.Circle(0, 0, 27, color=(255, 221, 118), batch=batch, group=group)
        self.halo.opacity = 72
        self.body = pyglet.shapes.Triangle(0, 0, 0, 0, 0, 0, color=self.toga_color, batch=batch, group=group)
        self.sash = pyglet.shapes.Line(0, 0, 0, 0, thickness=7, color=(182, 70, 72), batch=batch, group=group)
        self.head = pyglet.shapes.Circle(0, 0, 13, color=(225, 178, 139), batch=batch, group=group)
        self.hair = pyglet.shapes.Rectangle(0, 0, 26, 10, color=self.hair_color, batch=batch, group=group)
        self.eye_l = pyglet.shapes.Circle(0, 0, 2, color=(35, 28, 28), batch=batch, group=group)
        self.eye_r = pyglet.shapes.Circle(0, 0, 2, color=(35, 28, 28), batch=batch, group=group)
        self.mouth = pyglet.shapes.Rectangle(0, 0, 10, 3, color=(115, 38, 51), batch=batch, group=group)
        self.arm_l = pyglet.shapes.Line(0, 0, 0, 0, thickness=5, color=(225, 178, 139), batch=batch, group=group)
        self.arm_r = pyglet.shapes.Line(0, 0, 0, 0, thickness=5, color=(225, 178, 139), batch=batch, group=group)
        self.shapes.extend((self.halo, self.body, self.sash, self.head, self.hair, self.eye_l, self.eye_r, self.mouth, self.arm_l, self.arm_r))
        self.name_label = pyglet.text.Label(
            self.sister_name,
            x=0,
            y=0,
            anchor_x="center",
            font_size=9,
            color=(255, 241, 222, 255),
            batch=batch,
            group=group,
        )

    def set_target(self, x, y):
        self.target_x = Decimal(str(x))
        self.target_y = Decimal(str(y))

    def sing(self, frames=30):
        self.sing_timer = max(self.sing_timer, float(frames))

    def flash_hurt(self, frames=10):
        self.hurt_timer = max(self.hurt_timer, float(frames))

    def _update_visuals(self, dt):
        sx = float(EngineGlobals.screen_x(self.x_position))
        sy = float(EngineGlobals.screen_y(self.y_position))
        bob = math.sin(self.float_phase) * 4.0
        self.float_phase += 0.045 * float(dt)
        center_x = sx + 22
        base_y = sy + bob
        singing = self.sing_timer > 0
        hurt = self.hurt_timer > 0

        self.body.color = (255, 190, 190) if hurt else self.toga_color
        self.body.x = center_x - 20
        self.body.y = base_y + 6
        self.body.x2 = center_x + 20
        self.body.y2 = base_y + 6
        self.body.x3 = center_x
        self.body.y3 = base_y + 56
        self.sash.x = center_x - 12
        self.sash.y = base_y + 47
        self.sash.x2 = center_x + 13
        self.sash.y2 = base_y + 14
        self.head.position = (center_x, base_y + 67)
        self.hair.position = (center_x - 13, base_y + 71)
        self.eye_l.position = (center_x - 5, base_y + 68)
        self.eye_r.position = (center_x + 5, base_y + 68)
        self.mouth.position = (center_x - (7 if singing else 5), base_y + 57)
        self.mouth.width = 14 if singing else 10
        self.mouth.height = 8 if singing else 3
        self.arm_l.x = center_x - 12
        self.arm_l.y = base_y + 42
        self.arm_l.x2 = center_x - (29 if singing else 23)
        self.arm_l.y2 = base_y + (58 if singing else 29)
        self.arm_r.x = center_x + 12
        self.arm_r.y = base_y + 42
        self.arm_r.x2 = center_x + (29 if singing else 23)
        self.arm_r.y2 = base_y + (58 if singing else 29)
        self.halo.position = (center_x, base_y + 42)
        self.name_label.x = center_x
        self.name_label.y = base_y + 88

    def updateloop(self, dt):
        if self.defeated:
            return
        blend = min(1.0, 0.055 * float(dt))
        self.x_position += (self.target_x - Decimal(self.x_position)) * Decimal(str(blend))
        self.y_position += (self.target_y - Decimal(self.y_position)) * Decimal(str(blend))
        self.x_speed = Decimal(0)
        self.y_speed = Decimal(0)
        if self.sing_timer > 0:
            self.sing_timer -= float(dt)
        if self.hurt_timer > 0:
            self.hurt_timer -= float(dt)
        PhysicsSprite.updateloop(self, dt)
        self.sprite.visible = False
        self._update_visuals(dt)

    def take_damage(self, damage=1, source_x=None, knockback=True):
        if self.defeated or self.controller.defeated:
            return False
        base = max(1, int(damage))
        scaled = 4 if base <= 1 else 12
        self.flash_hurt()
        return self.controller.take_damage(scaled, self)

    def getting_hit(self):
        return self.take_damage(1)

    def on_pokey(self):
        if not self.defeated and not self.controller.defeated:
            self.flash_hurt(14)
            self.controller.take_damage(12, self)

    def defeat(self):
        if self.defeated:
            return
        self.defeated = True
        from gameplay import BloodSpurt
        BloodSpurt(self.x_position + Decimal(22), self.y_position + Decimal(38))
        self.destroy()

    def on_finalDeletion(self):
        for shape in self.shapes:
            shape.delete()
        self.shapes.clear()
        if hasattr(self, "name_label"):
            self.name_label.delete()
        super().on_finalDeletion()


class SingingWave(PhysicsSprite):
    """Horizontal singing hazard. Low notes demand a jump; high notes can be ducked/avoided."""

    def __init__(self, sprite_initializer, starting_chunk):
        self.direction = Decimal(str(sprite_initializer.get("direction", -1)))
        self.speed = Decimal(str(sprite_initializer.get("speed", 6.4)))
        self.life = float(sprite_initializer.get("life", 180))
        self.wave_color = tuple(sprite_initializer.get("wave_color", (245, 218, 255)))
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.opacity = 0
        self.x_speed = self.speed * self.direction
        self.note = pyglet.text.Label(
            "♪  ♫  ♪",
            x=0,
            y=0,
            anchor_x="center",
            anchor_y="center",
            font_size=18,
            color=(*self.wave_color, 235),
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self.ring = pyglet.shapes.Circle(0, 0, 22, color=self.wave_color, batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_front)
        self.ring.opacity = 65

    def getResourceImages(self):
        return {0: "bullet1-1.png.png"}

    def getCollisionBox(self):
        return (58, 26)

    def hasGravity(self):
        return False

    def updateloop(self, dt):
        self.life -= float(dt)
        if self.life <= 0:
            self.destroy()
            return
        PhysicsSprite.updateloop(self, dt)
        sx = float(EngineGlobals.screen_x(self.x_position)) + 29
        sy = float(EngineGlobals.screen_y(self.y_position)) + 13
        self.note.x = sx
        self.note.y = sy
        self.ring.position = (sx, sy)
        self.sprite.visible = False

    def on_PhysicsSprite_collided(self, collided_object=None, **kwargs):
        if collided_object and type(collided_object).__name__ == "Player":
            if getattr(collided_object, "hit_cooldown", 0) == 0:
                collided_object.hit()
                collided_object.hit_cooldown = 36
                collided_object.x_speed = Decimal("-5.5") if self.direction > 0 else Decimal("5.5")
            self.destroy()

    def on_finalDeletion(self):
        self.note.delete()
        self.ring.delete()
        super().on_finalDeletion()


class TogaFireball(PhysicsSprite):
    """Fireball that crosses the arena in repeated jumping arcs."""

    def __init__(self, sprite_initializer, starting_chunk):
        self.direction = Decimal(str(sprite_initializer.get("direction", -1)))
        self.speed = Decimal(str(sprite_initializer.get("speed", 5.2)))
        self.base_y = Decimal(str(sprite_initializer.get("base_y", sprite_initializer["starting_position"][1])))
        self.arc_height = float(sprite_initializer.get("arc_height", 115))
        self.wave_length = float(sprite_initializer.get("wave_length", 190))
        self.origin_x = Decimal(str(sprite_initializer["starting_position"][0]))
        self.life = float(sprite_initializer.get("life", 220))
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.opacity = 0
        self.x_speed = self.speed * self.direction
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_front
        self.outer = pyglet.shapes.Circle(0, 0, 15, color=(236, 69, 24), batch=batch, group=group)
        self.inner = pyglet.shapes.Circle(0, 0, 8, color=(255, 205, 62), batch=batch, group=group)

    def getResourceImages(self):
        return {0: "bullet1-1.png.png"}

    def getCollisionBox(self):
        return (28, 28)

    def hasGravity(self):
        return False

    def updateloop(self, dt):
        self.life -= float(dt)
        if self.life <= 0:
            self.destroy()
            return
        travelled = abs(float(Decimal(self.x_position) - self.origin_x))
        jump = abs(math.sin((travelled / self.wave_length) * math.pi)) * self.arc_height
        self.y_position = self.base_y + Decimal(str(jump))
        PhysicsSprite.updateloop(self, dt)
        sx = float(EngineGlobals.screen_x(self.x_position)) + 14
        sy = float(EngineGlobals.screen_y(self.y_position)) + 14
        self.outer.position = (sx, sy)
        self.inner.position = (sx, sy)
        self.sprite.visible = False

    def on_PhysicsSprite_collided(self, collided_object=None, **kwargs):
        if collided_object and type(collided_object).__name__ == "Player":
            if getattr(collided_object, "hit_cooldown", 0) == 0:
                collided_object.hit()
                collided_object.hit_cooldown = 42
                collided_object.y_speed = Decimal("6")
            self.destroy()

    def on_finalDeletion(self):
        self.outer.delete()
        self.inner.delete()
        super().on_finalDeletion()


class TogaMovingPlatform(PhysicsSprite):
    """Manual one-way moving platform over the boss pit."""

    def __init__(self, sprite_initializer, starting_chunk):
        self.origin_x = Decimal(str(sprite_initializer["starting_position"][0]))
        self.origin_y = Decimal(str(sprite_initializer["starting_position"][1]))
        self.platform_width = int(sprite_initializer.get("platform_width", 112))
        self.platform_height = int(sprite_initializer.get("platform_height", 18))
        self.amplitude_x = float(sprite_initializer.get("amplitude_x", 0))
        self.amplitude_y = float(sprite_initializer.get("amplitude_y", 0))
        self.phase = float(sprite_initializer.get("phase", 0.0))
        self.motion_speed = float(sprite_initializer.get("motion_speed", 0.025))
        self.clock = 0.0
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.opacity = 0
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_mid
        self.deck = pyglet.shapes.Rectangle(0, 0, self.platform_width, self.platform_height, color=(181, 147, 97), batch=batch, group=group)
        self.edge = pyglet.shapes.Rectangle(0, 0, self.platform_width, 5, color=(88, 61, 49), batch=batch, group=group)

    def getResourceImages(self):
        return {0: "bullet1-1.png.png"}

    def getCollisionBox(self):
        return (self.platform_width, self.platform_height)

    def hasGravity(self):
        return False

    def _support_player(self, dx):
        player = getattr(EngineGlobals, "kenny", None)
        if player is None or getattr(player, "is_dead", False):
            return
        p_width, _ = player.getCollisionBox()
        platform_top = Decimal(self.y_position) + Decimal(self.platform_height)
        horizontally_over = (
            Decimal(player.x_position) + Decimal(str(p_width)) > Decimal(self.x_position) + Decimal(4)
            and Decimal(player.x_position) < Decimal(self.x_position) + Decimal(self.platform_width - 4)
        )
        if not horizontally_over:
            return
        player_bottom = Decimal(player.y_position)
        falling_into_top = (
            Decimal(getattr(player, "y_speed", 0)) <= 0
            and player_bottom <= platform_top + Decimal(12)
            and player_bottom >= platform_top - Decimal(18)
        )
        if falling_into_top:
            player.x_position += dx
            player.y_position = platform_top + Decimal(1)
            player.y_speed = Decimal(0)
            player.landed = True

    def updateloop(self, dt):
        self.clock += self.motion_speed * float(dt)
        new_x = self.origin_x + Decimal(str(math.sin(self.clock + self.phase) * self.amplitude_x))
        new_y = self.origin_y + Decimal(str(math.sin(self.clock * 0.83 + self.phase) * self.amplitude_y))
        dx = new_x - Decimal(self.x_position)
        self.x_position = new_x
        self.y_position = new_y
        self.x_speed = Decimal(0)
        self.y_speed = Decimal(0)
        self._support_player(dx)
        PhysicsSprite.updateloop(self, dt)
        self.sprite.visible = False
        sx = float(EngineGlobals.screen_x(self.x_position))
        sy = float(EngineGlobals.screen_y(self.y_position))
        self.deck.position = (sx, sy)
        self.edge.position = (sx, sy + self.platform_height - 5)

    def on_PhysicsSprite_collided(self, collided_object=None, **kwargs):
        if collided_object and type(collided_object).__name__ == "Player":
            self._support_player(Decimal(0))

    def on_finalDeletion(self):
        self.deck.delete()
        self.edge.delete()
        super().on_finalDeletion()


class TogaSistersBoss(Enemy):
    """Invisible boss controller spawned in place of Vesuvius by the existing level builder."""

    MAX_HP = 100
    PHASE_LENGTH = 180.0
    PHASES = (
        ("CALL & RESPONSE", "Low notes: jump. High notes: stay grounded."),
        ("FIREBALL CADENZA", "Read the arcs and use the moving platforms."),
        ("TOGA SHUFFLE", "The sisters swap perches while the chorus keeps firing."),
        ("TRIPLE HARMONY", "All three attack together. Hit them hard."),
    )

    def __init__(self, sprite_initializer, starting_chunk):
        self.controller_ready = False
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.visible = False
        self.health_bar_bg.visible = False
        self.health_bar_fill.visible = False
        self.max_hp = self.MAX_HP
        self.hp = self.max_hp
        self.active = False
        self.defeated = False
        self.phase_index = -1
        self.pattern_clock = 0.0
        self.attack_cooldown = 0.0
        self.fireball_toggle = False
        self.wave_toggle = False
        self.flash_timer = 0.0
        self.sisters = []
        self.platforms = []
        self.pit_shapes = []
        self._configure_arena()
        self._build_hud()
        self._build_pit_visual()
        self._spawn_sisters()
        self._spawn_platforms()
        self.controller_ready = True

    def getResourceImages(self):
        return {"0": "mrspudl.png", "dead": "deadspud.png"}

    def getCollisionBox(self):
        return (0, 0)

    def hasGravity(self):
        return False

    def _update_health_bar(self):
        if hasattr(self, "health_bar_bg"):
            self.health_bar_bg.visible = False
        if hasattr(self, "health_bar_fill"):
            self.health_bar_fill.visible = False

    def _replace_tile(self, row, column, new_block):
        old = self.current_chunk.platform[row][column]
        if hasattr(old, "sprite"):
            try:
                old.sprite.delete()
            except Exception:
                pass
        self.current_chunk.platform[row][column] = new_block

    def _configure_arena(self):
        from gamepieces import Block, HazardBlock
        chunk = self.current_chunk
        floor_row = chunk.height - 2
        bottom_row = chunk.height - 1
        arena_start = max(1, int(chunk.width * 0.82))
        arena_end = min(chunk.width - 2, int(chunk.width * 0.97))
        pit_start = max(arena_start + 2, int(chunk.width * 0.875))
        pit_end = min(arena_end - 2, int(chunk.width * 0.925))
        clear_top = max(1, floor_row - 7)

        for col in range(arena_start, arena_end + 1):
            self._replace_tile(floor_row, col, Block((col + 6) % 12, True))
            for row in range(clear_top, floor_row):
                if chunk.platform[row][col] != 0:
                    self._replace_tile(row, col, 0)

        for col in range(pit_start, pit_end + 1):
            self._replace_tile(floor_row, col, 0)
            self._replace_tile(bottom_row, col, HazardBlock((col + 11) % 12, True))

        self.arena_left = Decimal(chunk.coalesced_x + arena_start * EngineGlobals.tile_size)
        self.arena_right = Decimal(chunk.coalesced_x + arena_end * EngineGlobals.tile_size)
        self.pit_left = Decimal(chunk.coalesced_x + pit_start * EngineGlobals.tile_size)
        self.pit_right = Decimal(chunk.coalesced_x + (pit_end + 1) * EngineGlobals.tile_size)
        self.ground_y = Decimal(self.y_position)

    def _build_hud(self):
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_front
        width = 430
        x = (EngineGlobals.width - width) // 2
        y = EngineGlobals.height - 116
        self.title_label = pyglet.text.Label(
            "THE TOGA SISTERS",
            x=EngineGlobals.width // 2,
            y=y + 38,
            anchor_x="center",
            font_size=14,
            weight=pyglet.text.Weight.BOLD,
            color=(255, 240, 214, 255),
            batch=batch,
            group=group,
        )
        self.phase_label = pyglet.text.Label(
            "",
            x=EngineGlobals.width // 2,
            y=y - 22,
            anchor_x="center",
            font_size=10,
            color=(255, 224, 186, 255),
            batch=batch,
            group=group,
        )
        self.health_bg = pyglet.shapes.Rectangle(x, y, width, 18, color=(58, 34, 37), batch=batch, group=group)
        self.health_fill = pyglet.shapes.Rectangle(x + 3, y + 3, width - 6, 12, color=(195, 58, 74), batch=batch, group=group)
        self.title_label.opacity = 0
        self.phase_label.opacity = 0
        self.health_bg.visible = False
        self.health_fill.visible = False
        self.health_width = width - 6

    def _build_pit_visual(self):
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_mid
        self.pit_dark = pyglet.shapes.Rectangle(0, 0, 1, 72, color=(37, 26, 29), batch=batch, group=group)
        self.pit_lava = pyglet.shapes.Rectangle(0, 0, 1, 22, color=(226, 69, 25), batch=batch, group=group)
        self.pit_glow = pyglet.shapes.Rectangle(0, 0, 1, 7, color=(255, 183, 54), batch=batch, group=group)
        self.pit_shapes.extend((self.pit_dark, self.pit_lava, self.pit_glow))

    def _perches(self):
        width = self.arena_right - self.arena_left
        return (
            (self.arena_left + width * Decimal("0.08"), self.ground_y + Decimal(8)),
            (self.arena_left + width * Decimal("0.49"), self.ground_y + Decimal(170)),
            (self.arena_left + width * Decimal("0.86"), self.ground_y + Decimal(16)),
        )

    def _spawn_sisters(self):
        names = ("Livia", "Octavia", "Claudia")
        colors = ((239, 228, 201), (224, 209, 239), (230, 220, 187))
        hair = ((65, 42, 31), (103, 70, 42), (46, 38, 34))
        for index, ((x, y), name, toga_color, hair_color) in enumerate(zip(self._perches(), names, colors, hair)):
            sister = makeSprite(
                TogaSister,
                self.current_chunk,
                (x, y),
                controller=self,
                sister_name=name,
                toga_color=toga_color,
                hair_color=hair_color,
                float_phase=index * 2.0,
            )
            self.sisters.append(sister)

    def _spawn_platforms(self):
        pit_width = self.pit_right - self.pit_left
        center = (self.pit_left + self.pit_right) / Decimal(2)
        specs = (
            (self.pit_left + Decimal(12), self.ground_y + Decimal(58), 104, float(pit_width) * 0.16, 16, 0.0, 0.025),
            (center - Decimal(54), self.ground_y + Decimal(128), 108, float(pit_width) * 0.11, 24, 2.1, 0.021),
            (self.pit_right - Decimal(118), self.ground_y + Decimal(72), 106, float(pit_width) * 0.15, 18, 4.2, 0.027),
        )
        for x, y, width, ax, ay, phase, speed in specs:
            self.platforms.append(
                makeSprite(
                    TogaMovingPlatform,
                    self.current_chunk,
                    (x, y),
                    platform_width=width,
                    amplitude_x=ax,
                    amplitude_y=ay,
                    phase=phase,
                    motion_speed=speed,
                    group="BACK",
                )
            )

    def _activate(self):
        self.active = True
        self.pattern_clock = 0.0
        self.attack_cooldown = 20.0
        self.title_label.opacity = 255
        self.phase_label.opacity = 255
        self.health_bg.visible = True
        self.health_fill.visible = True
        autoscroller = getattr(EngineGlobals, "autoscroller", None)
        if autoscroller is not None:
            autoscroller.stop()
        director = getattr(getattr(EngineGlobals, "game_map", None), "pompeii_director", None)
        if director is not None:
            director.stage_label.text = "V  THE TOGA SISTERS"
            director.objective_label.text = "Cross the pit, survive the chorus, and break the trio."
        self._enter_phase(0)

    def _enter_phase(self, index):
        self.phase_index = index
        phase_name, instruction = self.PHASES[index]
        self.phase_label.text = f"{phase_name}  —  {instruction}"
        perches = list(self._perches())
        arrangement = ((0, 1, 2), (2, 0, 1), (1, 2, 0), (2, 1, 0))[index]
        for sister, perch_index in zip(self.sisters, arrangement):
            sister.set_target(*perches[perch_index])
            sister.sing(24)

    def _direction_to_player(self, x):
        player = getattr(EngineGlobals, "kenny", None)
        if player is None:
            return Decimal(-1)
        return Decimal(1) if Decimal(player.x_position) >= Decimal(x) else Decimal(-1)

    def _spawn_wave(self, sister, high=False, fast=False):
        direction = self._direction_to_player(sister.x_position)
        y = self.ground_y + (Decimal(112) if high else Decimal(22))
        start_x = Decimal(sister.x_position) + (Decimal(46) if direction > 0 else Decimal(-60))
        makeSprite(
            SingingWave,
            self.current_chunk,
            (start_x, y),
            direction=direction,
            speed=Decimal("8.0") if fast else Decimal("6.4"),
            wave_color=(246, 208, 255) if high else (255, 239, 181),
        )
        sister.sing(34)

    def _spawn_fireball(self, sister, fast=False):
        direction = self._direction_to_player(sister.x_position)
        makeSprite(
            TogaFireball,
            self.current_chunk,
            (Decimal(sister.x_position) + Decimal(22), self.ground_y + Decimal(24)),
            direction=direction,
            speed=Decimal("6.7") if fast else Decimal("5.2"),
            base_y=self.ground_y + Decimal(18),
            arc_height=145 if fast else 112,
            wave_length=165 if fast else 200,
        )
        sister.sing(24)

    def _attack(self):
        enraged = self.hp <= 35
        if self.phase_index == 0:
            sister = self.sisters[0 if self.wave_toggle else 2]
            self._spawn_wave(sister, high=self.wave_toggle, fast=enraged)
            self.wave_toggle = not self.wave_toggle
            self.attack_cooldown = 27.0 if enraged else 38.0
        elif self.phase_index == 1:
            sister = self.sisters[1 if self.fireball_toggle else 0]
            self._spawn_fireball(sister, fast=enraged)
            self.fireball_toggle = not self.fireball_toggle
            self.attack_cooldown = 22.0 if enraged else 31.0
        elif self.phase_index == 2:
            sister = self.sisters[int(self.pattern_clock // 34) % len(self.sisters)]
            self._spawn_wave(sister, high=self.wave_toggle, fast=True)
            self.wave_toggle = not self.wave_toggle
            self.attack_cooldown = 24.0 if enraged else 32.0
        else:
            if self.fireball_toggle:
                self._spawn_fireball(self.sisters[1], fast=True)
            else:
                self._spawn_wave(self.sisters[0], high=self.wave_toggle, fast=True)
                self._spawn_wave(self.sisters[2], high=not self.wave_toggle, fast=True)
                self.wave_toggle = not self.wave_toggle
            self.fireball_toggle = not self.fireball_toggle
            self.attack_cooldown = 18.0 if enraged else 25.0

    def take_damage(self, amount, source_sister=None):
        if not self.active or self.defeated:
            return False
        self.hp = max(0, self.hp - max(1, int(amount)))
        self.flash_timer = 8.0
        if source_sister is not None:
            source_sister.flash_hurt(12)
        if self.hp <= 0:
            self._finish_fight()
        return True

    def _finish_fight(self):
        if self.defeated:
            return
        self.defeated = True
        self.hp = 0
        self.phase_label.text = "TRIO BROKEN — the road out of Pompeii is open."
        self.health_fill.width = 0
        for sister in list(self.sisters):
            sister.defeat()
        manager = LifeCycleManager.ALL_SETS.get("PER_MAP")
        if manager is not None:
            for obj in list(manager.objects) + list(manager.to_be_added):
                if isinstance(obj, (SingingWave, TogaFireball)):
                    obj.destroy()
        makeSprite(
            Door,
            self.current_chunk,
            (self.arena_right - Decimal(82), self.ground_y),
            group="BACK",
            target_map="map.dill",
            player_position=(300, 200),
        )

    def _update_hud(self):
        ratio = max(0.0, min(1.0, float(self.hp) / float(self.max_hp)))
        self.health_fill.width = self.health_width * ratio
        if self.flash_timer > 0:
            self.health_fill.color = (255, 181, 94)
        elif self.hp <= 35:
            self.health_fill.color = (235, 49, 49)
        else:
            self.health_fill.color = (195, 58, 74)

    def _update_pit(self):
        left = float(EngineGlobals.screen_x(self.pit_left))
        right = float(EngineGlobals.screen_x(self.pit_right))
        width = max(1.0, right - left)
        floor_screen_y = float(EngineGlobals.screen_y(self.ground_y - Decimal(32)))
        self.pit_dark.position = (left, floor_screen_y - 48)
        self.pit_dark.width = width
        self.pit_lava.position = (left, floor_screen_y - 4)
        self.pit_lava.width = width
        self.pit_glow.position = (left, floor_screen_y + 15)
        self.pit_glow.width = width

    def updateloop(self, dt):
        if not self.controller_ready:
            return
        self.sprite.visible = False
        self._update_pit()
        player = getattr(EngineGlobals, "kenny", None)
        if player is None:
            return
        if not self.active and not self.defeated and Decimal(player.x_position) >= self.arena_left - Decimal(64):
            self._activate()
        if not self.active or self.defeated:
            self._update_hud()
            return
        self.pattern_clock += float(dt)
        self.attack_cooldown -= float(dt)
        if self.flash_timer > 0:
            self.flash_timer -= float(dt)
        new_phase = int(self.pattern_clock // self.PHASE_LENGTH) % len(self.PHASES)
        if new_phase != self.phase_index:
            self._enter_phase(new_phase)
        if self.attack_cooldown <= 0:
            self._attack()
        if self.pit_left <= Decimal(player.x_position) <= self.pit_right:
            if Decimal(player.y_position) < self.ground_y - Decimal(8) and getattr(player, "hit_cooldown", 0) == 0:
                player.hit()
                player.hit_cooldown = 50
                player.y_speed = Decimal("10")
        self._update_hud()

    def on_finalDeletion(self):
        if hasattr(self, "title_label"):
            self.title_label.delete()
            self.phase_label.delete()
            self.health_bg.delete()
            self.health_fill.delete()
        for shape in getattr(self, "pit_shapes", []):
            shape.delete()
        self.pit_shapes = []
        super().on_finalDeletion()


def install_toga_sisters():
    """Swap the Pompeii boss class without changing the dill/map-loader architecture."""
    import maploader
    maploader.THEMED_LEVELS["pompeii.dill"]["boss"] = TogaSistersBoss
