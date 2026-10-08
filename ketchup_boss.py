"""Theo trailer side-boss: clog a giant ketchup bottle, then eat the tomato bully."""

import math
import random
from decimal import Decimal

import pyglet

import gamepieces
from enemies import Enemy
from engineglobals import EngineGlobals
from gamepieces import Door
from lifecycle import GameObject, LifeCycleManager
from physics import PhysicsSprite
from sprite import makeSprite


class KetchupBossDoor(PhysicsSprite):
    """Door inside Theo's trailer that opens the ketchup boss room."""

    def __init__(self, sprite_initializer, starting_chunk):
        self.encounter = sprite_initializer["encounter"]
        super().__init__(sprite_initializer, starting_chunk)
        self.sign = pyglet.text.Label(
            "KETCHUP ROOM",
            x=0,
            y=0,
            anchor_x="center",
            font_size=10,
            weight=pyglet.text.Weight.BOLD,
            color=(244, 225, 184, 255),
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )

    def getResourceImages(self):
        return {0: "door-1.png"}

    def hasGravity(self):
        return False

    def interact(self, player):
        self.encounter.enter(player)
        return True

    def updateloop(self, dt):
        PhysicsSprite.updateloop(self, dt)
        self.sign.x = float(EngineGlobals.screen_x(self.x_position + Decimal(20)))
        self.sign.y = float(EngineGlobals.screen_y(self.y_position + Decimal(92)))

    def on_finalDeletion(self):
        self.sign.delete()
        super().on_finalDeletion()


class KetchupBottleTarget(PhysicsSprite):
    """Invisible collision target so normal attacks bounce off the bottle objective."""

    def __init__(self, sprite_initializer, starting_chunk):
        self.encounter = sprite_initializer["encounter"]
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.opacity = 0

    def getResourceImages(self):
        return {0: "mrspudl.png"}

    def getCollisionBox(self):
        return (112, 196)

    def hasGravity(self):
        return False

    def take_damage(self, damage=1, source_x=None, knockback=True):
        self.encounter.bottle_hit()
        return True

    def getting_hit(self):
        self.encounter.bottle_hit()

    def on_pokey(self):
        self.encounter.bottle_hit()

    def updateloop(self, dt):
        PhysicsSprite.updateloop(self, dt)
        self.sprite.visible = False


class KetchupGlob(PhysicsSprite):
    """Recoverable ketchup puddle used to clog the bottle tip."""

    def __init__(self, sprite_initializer, starting_chunk):
        self.encounter = sprite_initializer["encounter"]
        self.phase = float(sprite_initializer.get("phase", 0.0))
        self.collected = False
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.opacity = 0
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_mid
        self.puddle = pyglet.shapes.Ellipse(0, 0, 25, 9, color=(181, 28, 31), batch=batch, group=group)
        self.glint = pyglet.shapes.Ellipse(0, 0, 9, 3, color=(255, 115, 91), batch=batch, group=group)

    def getResourceImages(self):
        return {0: "bullet1-1.png.png"}

    def getCollisionBox(self):
        return (50, 22)

    def hasGravity(self):
        return False

    def updateloop(self, dt):
        if self.collected:
            return
        self.phase += 0.06 * float(dt)
        bob = math.sin(self.phase) * 2.0
        sx = float(EngineGlobals.screen_x(self.x_position)) + 25
        sy = float(EngineGlobals.screen_y(self.y_position)) + 7 + bob
        self.puddle.position = (sx, sy)
        self.glint.position = (sx - 7, sy + 2)
        self.sprite.visible = False
        PhysicsSprite.updateloop(self, dt)

    def on_PhysicsSprite_collided(self, collided_object=None, **kwargs):
        if self.collected:
            return
        if collided_object is not None and type(collided_object).__name__ == "Player":
            self.collected = True
            self.encounter.collect_glob(self)
            self.destroy()

    def on_finalDeletion(self):
        self.puddle.delete()
        self.glint.delete()
        super().on_finalDeletion()


class KetchupShot(PhysicsSprite):
    """A ketchup spray blob fired by the giant bottle."""

    def __init__(self, sprite_initializer, starting_chunk):
        self.life = float(sprite_initializer.get("life", 150))
        self.origin_x = Decimal(str(sprite_initializer["starting_position"][0]))
        self.base_y = Decimal(str(sprite_initializer["starting_position"][1]))
        self.arc_height = float(sprite_initializer.get("arc_height", 55))
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.opacity = 0
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_front
        self.outer = pyglet.shapes.Circle(0, 0, 13, color=(166, 21, 27), batch=batch, group=group)
        self.inner = pyglet.shapes.Circle(0, 0, 7, color=(244, 78, 57), batch=batch, group=group)

    def getResourceImages(self):
        return {0: "bullet1-1.png.png"}

    def getCollisionBox(self):
        return (26, 26)

    def hasGravity(self):
        return False

    def updateloop(self, dt):
        self.life -= float(dt)
        if self.life <= 0:
            self.destroy()
            return
        travelled = abs(float(Decimal(self.x_position) - self.origin_x))
        self.y_position = self.base_y + Decimal(str(abs(math.sin(travelled / 72.0)) * self.arc_height))
        PhysicsSprite.updateloop(self, dt)
        sx = float(EngineGlobals.screen_x(self.x_position)) + 13
        sy = float(EngineGlobals.screen_y(self.y_position)) + 13
        self.outer.position = (sx, sy)
        self.inner.position = (sx, sy)
        self.sprite.visible = False

    def on_PhysicsSprite_collided(self, collided_object=None, **kwargs):
        if collided_object is not None and type(collided_object).__name__ == "Player":
            if getattr(collided_object, "hit_cooldown", 0) == 0:
                collided_object.hit()
                collided_object.hit_cooldown = 38
                collided_object.y_speed = Decimal("5.5")
            self.destroy()

    def on_finalDeletion(self):
        self.outer.delete()
        self.inner.delete()
        super().on_finalDeletion()


class TomatoBully(Enemy):
    """Final weak phase after the bottle bursts."""

    MAX_HP = 5
    PATROL_SPEED = Decimal("1.4")
    CHASE_SPEED = Decimal("2.8")
    CHASE_DISTANCE = Decimal("430")
    LUNGE_DISTANCE = Decimal("120")
    LUNGE_SPEED = Decimal("5.6")
    ATTACK_COOLDOWN = 90

    def __init__(self, sprite_initializer, starting_chunk):
        self.encounter = sprite_initializer["encounter"]
        self.tomato_shapes = []
        super().__init__(sprite_initializer, starting_chunk)
        self.sprite.opacity = 0
        batch = EngineGlobals.main_batch
        front = EngineGlobals.editor_group_front
        self.body = pyglet.shapes.Circle(0, 0, 31, color=(211, 48, 43), batch=batch, group=front)
        self.cheek = pyglet.shapes.Circle(0, 0, 19, color=(236, 69, 55), batch=batch, group=front)
        self.leaf_a = pyglet.shapes.Triangle(0, 0, 0, 0, 0, 0, color=(70, 126, 53), batch=batch, group=front)
        self.leaf_b = pyglet.shapes.Triangle(0, 0, 0, 0, 0, 0, color=(61, 111, 48), batch=batch, group=front)
        self.eye_l = pyglet.shapes.Circle(0, 0, 3, color=(36, 24, 23), batch=batch, group=front)
        self.eye_r = pyglet.shapes.Circle(0, 0, 3, color=(36, 24, 23), batch=batch, group=front)
        self.mouth = pyglet.shapes.Rectangle(0, 0, 18, 5, color=(89, 21, 26), batch=batch, group=front)
        self.tomato_shapes.extend((self.body, self.cheek, self.leaf_a, self.leaf_b, self.eye_l, self.eye_r, self.mouth))

    def getResourceImages(self):
        return {"0": "mrspudl.png", "dead": "deadspud.png"}

    def getCollisionBox(self):
        return (62, 62)

    def _sync_visual(self):
        sx = float(EngineGlobals.screen_x(self.x_position)) + 31
        sy = float(EngineGlobals.screen_y(self.y_position)) + 29
        self.body.position = (sx, sy)
        self.cheek.position = (sx - 7, sy + 5)
        self.eye_l.position = (sx - 10, sy + 8)
        self.eye_r.position = (sx + 10, sy + 8)
        self.mouth.position = (sx - 9, sy - 10)
        self.leaf_a.x = sx - 18
        self.leaf_a.y = sy + 25
        self.leaf_a.x2 = sx
        self.leaf_a.y2 = sy + 46
        self.leaf_a.x3 = sx + 3
        self.leaf_a.y3 = sy + 23
        self.leaf_b.x = sx + 18
        self.leaf_b.y = sy + 25
        self.leaf_b.x2 = sx
        self.leaf_b.y2 = sy + 44
        self.leaf_b.x3 = sx - 3
        self.leaf_b.y3 = sy + 23

    def updateloop(self, dt):
        super().updateloop(dt)
        self.sprite.visible = False
        if not self.death_done:
            self._sync_visual()

    def on_finish_death(self):
        self.encounter.tomato_eaten()

    def on_finalDeletion(self):
        for shape in self.tomato_shapes:
            shape.delete()
        self.tomato_shapes.clear()
        super().on_finalDeletion()


class KetchupBossEncounter(GameObject):
    """Dormant Theo side-room encounter activated through the trailer boss door."""

    REQUIRED_GLOBS = 5

    def __init__(self, chunk, player_spawn, table_x, ground_y):
        self.chunk = chunk
        self.return_position = (int(player_spawn[0]), int(player_spawn[1]))
        self.table_x = Decimal(str(table_x))
        self.ground_y = Decimal(str(ground_y))
        self.state = "dormant"
        self.inventory = 0
        self.filled = 0
        self.dry_timer = 0.0
        self.attack_timer = 0.0
        self.taunt_timer = 0.0
        self.world_shapes = []
        self.pickups = []
        self.bottle_target = None
        self.tomato = None
        self.return_door = None
        self._prepare_arena()
        self._build_room_art()
        self._build_hud()
        self._spawn_trailer_door()
        super().__init__(lifecycle_manager="PER_MAP")
        EngineGlobals.window.push_handlers(self)

    def _delete_block_sprite(self, block):
        if isinstance(block, gamepieces.Block) and hasattr(block, "sprite"):
            try:
                block.sprite.delete()
            except Exception:
                pass

    def _replace_tile(self, row, column, block):
        old = self.chunk.platform[row][column]
        self._delete_block_sprite(old)
        self.chunk.platform[row][column] = block

    def _prepare_arena(self):
        platform = self.chunk.platform
        tile = int(EngineGlobals.tile_size)
        width = self.chunk.width
        height = self.chunk.height
        chunk_x = int(self.chunk.coalesced_x)
        chunk_y = int(self.chunk.coalesced_y)

        floor_world_y = int(self.ground_y) - tile - 1
        floor_from_bottom = max(0, int((floor_world_y - chunk_y) // tile))
        self.floor_row = max(1, min(height - 2, height - 1 - floor_from_bottom))
        clear_top = max(0, self.floor_row - 7)

        arena_end = max(12, width - 4)
        arena_start = max(2, min(arena_end - 22, int(width * 0.64)))
        if arena_end - arena_start < 20:
            arena_start = max(2, arena_end - 20)

        self.arena_start_col = arena_start
        self.arena_end_col = arena_end
        self.arena_left = Decimal(chunk_x + arena_start * tile)
        self.arena_right = Decimal(chunk_x + arena_end * tile)

        for column in range(arena_start, arena_end + 1):
            for row in range(clear_top, self.floor_row):
                if platform[row][column] != 0:
                    self._replace_tile(row, column, 0)
            self._replace_tile(self.floor_row, column, gamepieces.Block((column + 8) % 12, True))

        self.bottle_x = self.arena_right - Decimal(180)
        self.bottle_y = self.ground_y + Decimal(1)
        self.nozzle_x = self.bottle_x + Decimal(56)
        self.nozzle_y = self.bottle_y + Decimal(190)

    def _world_rect(self, x, y, width, height, color, group):
        shape = pyglet.shapes.Rectangle(0, 0, width, height, color=color, batch=EngineGlobals.main_batch, group=group)
        self.world_shapes.append((shape, Decimal(str(x)), Decimal(str(y))))
        return shape

    def _world_circle(self, x, y, radius, color, group):
        shape = pyglet.shapes.Circle(0, 0, radius, color=color, batch=EngineGlobals.main_batch, group=group)
        self.world_shapes.append((shape, Decimal(str(x)), Decimal(str(y))))
        return shape

    def _build_room_art(self):
        bg = EngineGlobals.bg_group
        mid = EngineGlobals.editor_group_mid
        front = EngineGlobals.editor_group_front
        width = float(self.arena_right - self.arena_left)
        self._world_rect(self.arena_left, self.ground_y - Decimal(10), width, 315, (112, 89, 69), bg)
        self._world_rect(self.arena_left, self.ground_y - Decimal(10), width, 54, (70, 57, 48), bg)
        for index in range(7):
            x = self.arena_left + Decimal(30 + index * 110)
            self._world_rect(x, self.ground_y + Decimal(44), 5, 245, (81, 62, 49), bg)

        self.bottle_body = self._world_rect(self.bottle_x, self.bottle_y, 112, 158, (206, 28, 35), front)
        self.bottle_shine = self._world_rect(self.bottle_x + Decimal(19), self.bottle_y + Decimal(24), 15, 105, (244, 78, 65), front)
        self.bottle_shoulders = self._world_rect(self.bottle_x + Decimal(18), self.bottle_y + Decimal(148), 76, 30, (194, 24, 31), front)
        self.bottle_neck = self._world_rect(self.bottle_x + Decimal(37), self.bottle_y + Decimal(173), 38, 35, (226, 39, 40), front)
        self.bottle_tip = self._world_rect(self.bottle_x + Decimal(43), self.bottle_y + Decimal(205), 26, 18, (250, 221, 181), front)
        self.bottle_cap = self._world_rect(self.bottle_x + Decimal(36), self.bottle_y + Decimal(219), 40, 13, (236, 228, 199), front)
        self.fill_meter_bg = self._world_rect(self.bottle_x + Decimal(82), self.bottle_y + Decimal(20), 14, 118, (86, 22, 26), front)
        self.fill_meter = self._world_rect(self.bottle_x + Decimal(85), self.bottle_y + Decimal(23), 8, 0, (255, 163, 83), front)
        self._world_circle(self.bottle_x + Decimal(38), self.bottle_y + Decimal(113), 4, (31, 25, 24), front)
        self._world_circle(self.bottle_x + Decimal(69), self.bottle_y + Decimal(113), 4, (31, 25, 24), front)
        self.bottle_mouth = self._world_rect(self.bottle_x + Decimal(38), self.bottle_y + Decimal(83), 37, 9, (91, 14, 21), front)

    def _build_hud(self):
        front = EngineGlobals.editor_group_front
        self.title = pyglet.text.Label(
            "THE KETCHUP BOTTLE",
            x=EngineGlobals.width // 2,
            y=EngineGlobals.height - 34,
            anchor_x="center",
            font_size=17,
            weight=pyglet.text.Weight.BOLD,
            color=(255, 233, 201, 0),
            batch=EngineGlobals.main_batch,
            group=front,
        )
        self.status = pyglet.text.Label(
            "",
            x=EngineGlobals.width // 2,
            y=EngineGlobals.height - 59,
            anchor_x="center",
            font_size=11,
            color=(255, 225, 191, 0),
            batch=EngineGlobals.main_batch,
            group=front,
        )
        self.taunt = pyglet.text.Label(
            "",
            x=EngineGlobals.width // 2,
            y=EngineGlobals.height - 88,
            anchor_x="center",
            font_size=15,
            weight=pyglet.text.Weight.BOLD,
            color=(255, 112, 93, 0),
            batch=EngineGlobals.main_batch,
            group=front,
        )

    def _spawn_trailer_door(self):
        max_x = Decimal(self.chunk.coalesced_x + (self.chunk.width - 4) * EngineGlobals.tile_size)
        door_x = min(self.table_x + Decimal(250), max_x - Decimal(64))
        self.trailer_door = makeSprite(
            KetchupBossDoor,
            self.chunk,
            (door_x, self.ground_y),
            encounter=self,
            group="BACK",
        )

    def _spawn_bottle_target(self):
        if self.bottle_target is None:
            self.bottle_target = makeSprite(
                KetchupBottleTarget,
                self.chunk,
                (self.bottle_x, self.bottle_y),
                encounter=self,
                group="BACK",
            )

    def _spawn_pickups(self):
        if self.pickups:
            return
        room_width = self.arena_right - self.arena_left
        fractions = (Decimal("0.10"), Decimal("0.27"), Decimal("0.44"), Decimal("0.59"), Decimal("0.73"))
        for index, fraction in enumerate(fractions):
            x = self.arena_left + room_width * fraction
            glob = makeSprite(
                KetchupGlob,
                self.chunk,
                (x, self.ground_y + Decimal(5)),
                encounter=self,
                phase=index * 0.8,
            )
            self.pickups.append(glob)

    def enter(self, player):
        if self.state == "won":
            return
        self.state = "bottle"
        self.inventory = 0
        self.filled = 0
        self.dry_timer = 0.0
        self.attack_timer = 45.0
        self.taunt_timer = 180.0
        self._spawn_bottle_target()
        self._spawn_pickups()
        player.reset_at(self.arena_left + Decimal(58), self.ground_y)
        player.current_chunk = self.chunk
        screen = getattr(EngineGlobals, "our_screen", None)
        if screen is not None:
            screen.x = max(0, int(self.arena_left) - 80)
            screen.y = max(0, int(self.ground_y) - 96)
        self.title.color = (255, 233, 201, 255)
        self.status.color = (255, 225, 191, 255)
        self.taunt.color = (255, 112, 93, 255)
        self.taunt.text = "EAT MY KETCHUP FATTIE!"
        self.status.text = "Pick up the 5 ketchup puddles. Press D at the bottle to pack them into the tip."

    def collect_glob(self, glob):
        if self.state not in ("bottle", "drying"):
            return
        self.inventory += 1
        self.status.text = f"Ketchup carried: {self.inventory} | Bottle fill: {self.filled}/{self.REQUIRED_GLOBS}"

    def bottle_hit(self):
        if self.state != "bottle":
            return
        self.taunt.text = "THE BOTTLE SHRUGS IT OFF. CLOG THE TIP!"
        self.taunt_timer = 90.0

    def _near_bottle(self):
        player = getattr(EngineGlobals, "kenny", None)
        if player is None:
            return False
        return (
            abs(Decimal(player.x_position) - self.bottle_x) <= Decimal(145)
            and abs(Decimal(player.y_position) - self.bottle_y) <= Decimal(170)
        )

    def _deposit_one(self):
        if self.state != "bottle" or not self._near_bottle():
            return False
        if self.inventory <= 0:
            self.taunt.text = "NO KETCHUP IN HAND. GO SCRAPE SOME OFF THE FLOOR."
            self.taunt_timer = 90.0
            return True
        self.inventory -= 1
        self.filled += 1
        self.taunt.text = "SQUELCH."
        self.taunt_timer = 35.0
        self.status.text = f"Ketchup carried: {self.inventory} | Bottle fill: {self.filled}/{self.REQUIRED_GLOBS}"
        if self.filled == self.REQUIRED_GLOBS:
            self.state = "drying"
            self.dry_timer = 180.0
            self.status.text = "PERFECT FILL. The ketchup is drying in the tip — survive until it clogs."
            self.taunt.text = "HEY. WHY ISN'T MY KETCHUP COMING OUT?"
            self.taunt_timer = 180.0
        return True

    def _fire_ketchup(self):
        player = getattr(EngineGlobals, "kenny", None)
        if player is None:
            return
        direction = Decimal(1) if Decimal(player.x_position) > self.nozzle_x else Decimal(-1)
        speed = Decimal("5.4") * direction
        base = self.bottle_y + Decimal(74 + random.choice((0, 28, 58)))
        makeSprite(
            KetchupShot,
            self.chunk,
            (self.nozzle_x, base),
            starting_speed=(speed, Decimal(0)),
            arc_height=random.choice((38, 58, 82)),
        )

    def _explode_into_tomato(self):
        self.state = "tomato"
        self.taunt.text = "GIVE ME YOUR LUNCH MONEY."
        self.taunt_timer = 9999.0
        self.status.text = "You don't have to give it to him. Beat the tomato and Kenny will eat it."
        if self.bottle_target is not None:
            self.bottle_target.destroy()
            self.bottle_target = None
        for shape, _, _ in self.world_shapes:
            if shape in (
                self.bottle_body,
                self.bottle_shine,
                self.bottle_shoulders,
                self.bottle_neck,
                self.bottle_tip,
                self.bottle_cap,
                self.fill_meter_bg,
                self.fill_meter,
                self.bottle_mouth,
            ):
                shape.visible = False
        for _ in range(7):
            makeSprite(
                KetchupShot,
                self.chunk,
                (
                    self.bottle_x + Decimal(random.randint(-20, 70)),
                    self.bottle_y + Decimal(random.randint(30, 170)),
                ),
                starting_speed=(Decimal(random.choice((-6, -4, 4, 6))), Decimal(0)),
                arc_height=random.randint(30, 90),
                life=55,
            )
        self.tomato = makeSprite(
            TomatoBully,
            self.chunk,
            (self.bottle_x + Decimal(22), self.ground_y + Decimal(1)),
            encounter=self,
        )

    def tomato_eaten(self):
        if self.state == "won":
            return
        self.state = "won"
        self.taunt.text = "KENNY ATE THE TOMATO. LUNCH MONEY SAVED."
        self.status.text = "Boss defeated. Use the door to go back to Theo's trailer."
        manager = LifeCycleManager.ALL_SETS.get("PER_MAP")
        if manager is not None:
            for obj in list(manager.objects) + list(manager.to_be_added):
                if isinstance(obj, KetchupShot):
                    obj.destroy()
        if self.return_door is None:
            self.return_door = makeSprite(
                Door,
                self.chunk,
                (self.arena_left + Decimal(55), self.ground_y),
                group="BACK",
                target_map="theo.dill",
                player_position=self.return_position,
            )

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.D and self.state == "bottle" and self._near_bottle():
            if self._deposit_one():
                return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def _sync_world_shapes(self):
        for shape, wx, wy in self.world_shapes:
            if getattr(shape, "visible", True):
                shape.x = float(EngineGlobals.screen_x(wx))
                shape.y = float(EngineGlobals.screen_y(wy))
        fill_ratio = float(self.filled) / float(self.REQUIRED_GLOBS)
        self.fill_meter.height = max(0, 112 * fill_ratio)

    def updateloop(self, dt):
        self._sync_world_shapes()
        if self.state == "dormant":
            return
        if self.taunt_timer > 0:
            self.taunt_timer -= float(dt)
            if self.taunt_timer <= 0 and self.state == "bottle":
                self.taunt.text = "EAT MY KETCHUP FATTIE!"
                self.taunt_timer = 180.0

        if self.state in ("bottle", "drying"):
            self.attack_timer -= float(dt)
            if self.attack_timer <= 0:
                self._fire_ketchup()
                self.attack_timer = 38.0 if self.state == "drying" else max(42.0, 78.0 - self.filled * 6.0)

        if self.state == "drying":
            self.dry_timer -= float(dt)
            seconds = max(0.0, self.dry_timer / 60.0)
            self.status.text = f"TIP CLOGGING... {seconds:.1f}s"
            if self.dry_timer <= 0:
                self._explode_into_tomato()

    def on_finalDeletion(self):
        try:
            EngineGlobals.window.remove_handlers(self)
        except Exception:
            pass
        for shape, _, _ in self.world_shapes:
            try:
                shape.delete()
            except Exception:
                pass
        self.world_shapes.clear()
        self.title.delete()
        self.status.delete()
        self.taunt.delete()
