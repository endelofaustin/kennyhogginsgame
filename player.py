from enemies import Enemy
from physics import PhysicsSprite
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet
from maploader import GameMap
from sprite import makeSprite
from gameplay import DeathBurst, GameProgress, SaveGame, LockedGate


class Player(PhysicsSprite):
    LEFT_RIGHT_RUN_SPEED = Decimal("4.3")
    CRAWL_SPEED = LEFT_RIGHT_RUN_SPEED * Decimal("0.45")
    JUMP_INITIAL_VELOCITY = Decimal("12")
    DOUBLE_JUMP_VELOCITY = Decimal("9")
    BULLET_INITIAL_VELOCITY = Decimal("15.0")

    JUMP_CROUCH_FRAMES = 6
    JC0_NOT_JUMPING = 0
    JC1_CROUCHING_FOR_JUMP = 1
    JC2_FIRST_JUMP = 2
    JC3_SECOND_JUMP = 3

    _active_audio_players = []

    @classmethod
    def _play_sound(cls, sound):
        audio_player = sound.play()
        cls._active_audio_players.append(audio_player)

        def _cleanup():
            try:
                cls._active_audio_players.remove(audio_player)
            except ValueError:
                pass

        audio_player.on_player_eos = _cleanup
        return audio_player

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.direction = "right"
        self.has_sword = False
        self.has_scythe = False
        self.progress = getattr(EngineGlobals, "progress", GameProgress())
        EngineGlobals.progress = self.progress

        self.jumpct = self.JC0_NOT_JUMPING
        self.jump_frames = 0
        self.bloody = False
        self.crouching = False
        self.hit_cooldown = 0

        self.is_dead = False
        self.death_timer = 0
        self.angel_active = False
        self.angel_x = Decimal(self.x_position)
        self.angel_y = Decimal(self.y_position)
        self.angel_shapes = []

        if not hasattr(Player, "door_open_close"):
            Player.door_open_close = pyglet.resource.media("door_open_close.wav", streaming=False)
        if not hasattr(Player, "spit_bullet"):
            Player.spit_bullet = pyglet.resource.media("spitbullets.wav", streaming=False)
        if not hasattr(Player, "swipe_sword"):
            Player.swipe_sword = pyglet.resource.media("swordswipe.wav", streaming=False)
        if not hasattr(Player, "schimmy_scythe"):
            Player.schimmy_scythe = pyglet.resource.media("schimmyscythe.wav", streaming=False)
        if not hasattr(Player, "munching_on_apple"):
            Player.munching_on_apple = pyglet.resource.media("kenny_sounds/munching_on_apple.wav", streaming=False)

    def getResourceImages(self):
        return {
            "right": {"file": "kennystance1-2.png.png"},
            "left": {"file": "kennystance-left.png"},
            "bloody": {"file": "bloodykenny-1.png"},
            "crouch_left": {"file": "kenny-crouch-left.png"},
            "crouch_right": {"file": "kenny-crouch-right.png"},
            "run_left": {"file": "kenny-run-left.png", "rows": 1, "columns": 4, "duration": 1 / 10, "loop": True},
            "run_right": {"file": "kenny-run-right.png", "rows": 1, "columns": 4, "duration": 1 / 10, "loop": True},
            "jump_left": {
                "file": "generated/kenny-jump-left-4.png",
                "rows": 1,
                "columns": 4,
                "duration": 1 / 12,
                "loop": False,
                "anchors": [(10, 0), (10, 0), (10, 0), (10, 0)],
            },
            "jump_right": {
                "file": "generated/kenny-jump-right-4.png",
                "rows": 1,
                "columns": 4,
                "duration": 1 / 12,
                "loop": False,
                "anchors": [(3, 0), (3, 0), (3, 0), (3, 0)],
            },
            "kenny_sword_left": "kennysword-left.png",
            "kenny_sword_right": "kennysword-right.png",
            "kaboom": "kaboom.png",
        }

    def _delete_angel(self):
        for shape in self.angel_shapes:
            shape.delete()
        self.angel_shapes = []
        self.angel_active = False

    def _create_angel(self):
        self._delete_angel()
        self.angel_active = True
        self.angel_x = Decimal(self.x_position)
        self.angel_y = Decimal(self.y_position) + Decimal(18)
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_front

        # Built from primitive shapes so it remains part of the existing rendering architecture.
        self.angel_shapes = [
            pyglet.shapes.Circle(0, 0, 17, color=(255, 245, 170), batch=batch, group=group),  # halo
            pyglet.shapes.Circle(0, 0, 11, color=(255, 255, 255), batch=batch, group=group),  # halo center
            pyglet.shapes.Circle(0, 0, 17, color=(255, 255, 245), batch=batch, group=group),  # left wing
            pyglet.shapes.Circle(0, 0, 17, color=(255, 255, 245), batch=batch, group=group),  # right wing
            pyglet.shapes.Circle(0, 0, 18, color=(255, 255, 255), batch=batch, group=group),  # robe/body
            pyglet.shapes.Circle(0, 0, 13, color=(245, 175, 175), batch=batch, group=group),  # Kenny head
            pyglet.shapes.Circle(0, 0, 4, color=(120, 55, 55), batch=batch, group=group),     # snout
        ]
        self._update_angel_visual()

    def _update_angel_visual(self):
        if not self.angel_active or not self.angel_shapes:
            return
        sx = float(EngineGlobals.screen_x(self.angel_x))
        sy = float(EngineGlobals.screen_y(self.angel_y))
        offsets = [
            (0, 43),
            (0, 43),
            (-22, 5),
            (22, 5),
            (0, 5),
            (0, 20),
            (0, 15),
        ]
        for shape, (ox, oy) in zip(self.angel_shapes, offsets):
            shape.x = sx + ox
            shape.y = sy + oy

    def _respawn_from_angel(self):
        self.x_position = Decimal(self.angel_x)
        self.y_position = Decimal(self.angel_y)
        self.x_speed = Decimal(0)
        self.y_speed = Decimal(0)
        self.is_dead = False
        self.death_timer = 0
        self.jumpct = self.JC0_NOT_JUMPING
        self.jump_frames = 0
        self.landed = False
        self.crouching = False
        self.bloody = False
        self.hit_cooldown = 90
        self.sprite.visible = True
        self.sprite.image = self.resource_images[self.direction]
        self._delete_angel()

    def updateloop(self, dt):
        if self.is_dead:
            self.x_speed = Decimal(0)
            self.y_speed = Decimal(0)
            if not self.angel_active:
                self.death_timer -= 1
                if self.death_timer <= 0:
                    self._create_angel()
            else:
                # Rise away, but stop near the top of the current viewport so the angel remains clickable.
                max_world_y = Decimal(str(EngineGlobals.our_screen.y + EngineGlobals.height - 100))
                if self.angel_y < max_world_y:
                    self.angel_y += Decimal("0.85") * Decimal(str(dt))
                self._update_angel_visual()
            return

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        self.x_speed = Decimal(0)
        self.crouching = bool(EngineGlobals.keys[pyglet.window.key.DOWN] and self.landed)
        move_speed = Player.CRAWL_SPEED if self.crouching else Player.LEFT_RIGHT_RUN_SPEED

        if EngineGlobals.keys[pyglet.window.key.LEFT]:
            self.x_speed -= move_speed
        if EngineGlobals.keys[pyglet.window.key.RIGHT]:
            self.x_speed += move_speed

        if self.x_speed < 0:
            self.direction = "left"
        elif self.x_speed > 0:
            self.direction = "right"

        if self.crouching:
            self.sprite.image = self.resource_images["crouch_left" if self.direction == "left" else "crouch_right"]
        elif self.jumpct > Player.JC0_NOT_JUMPING:
            self.jump_frames += 1
            if self.jumpct == Player.JC1_CROUCHING_FOR_JUMP and self.jump_frames >= Player.JUMP_CROUCH_FRAMES:
                self.jumpct = Player.JC2_FIRST_JUMP
                self.y_speed = max(Decimal(self.y_speed), Decimal(0)) + Player.JUMP_INITIAL_VELOCITY
                self.landed = False
            jump_key = "jump_left" if self.direction == "left" else "jump_right"
            if self.sprite.image != self.resource_images[jump_key]:
                self.sprite.image = self.resource_images[jump_key]
        else:
            if self.x_speed < 0:
                image_key = "run_left"
            elif self.x_speed > 0:
                image_key = "run_right"
            else:
                image_key = self.direction
            if self.sprite.image != self.resource_images[image_key]:
                self.sprite.image = self.resource_images[image_key]

        if self.bloody:
            self.sprite.image = self.resource_images["bloody"]

        if self.landed and self.jumpct != Player.JC1_CROUCHING_FOR_JUMP:
            self.jumpct = Player.JC0_NOT_JUMPING
            self.jump_frames = 0

        if self.has_sword:
            self.sprite.image = self.resource_images["kenny_sword_right" if self.direction == "right" else "kenny_sword_left"]

        PhysicsSprite.updateloop(self, dt)

    def on_key_press(self, symbol, modifiers):
        if self.is_dead:
            return pyglet.event.EVENT_HANDLED

        if symbol in (pyglet.window.key.LCTRL, pyglet.window.key.RCTRL, pyglet.window.key.UP) and self.jumpct <= Player.JC2_FIRST_JUMP:
            if self.landed and self.jumpct == Player.JC0_NOT_JUMPING:
                self.jumpct = Player.JC1_CROUCHING_FOR_JUMP
                self.jump_frames = 0
            elif self.jumpct == Player.JC2_FIRST_JUMP:
                self.y_speed = Player.DOUBLE_JUMP_VELOCITY
                self.jumpct = Player.JC3_SECOND_JUMP

        if symbol == pyglet.window.key.SPACE:
            self.shoot_it()

        if symbol == pyglet.window.key.D:
            for collide_with in self.get_all_colliding_objects():
                if type(collide_with).__name__ == "Door":
                    Player._play_sound(Player.door_open_close)
                    GameMap.load_map(collide_with.sprite_initializer["target_map"])
                    self.current_chunk = EngineGlobals.game_map.chunks[0]
                    self.x_position, self.y_position = collide_with.sprite_initializer["player_position"]
                    self.x_speed = self.y_speed = Decimal(0)
                    self.jumpct = self.JC0_NOT_JUMPING
                    self.landed = False
                    break
                if isinstance(collide_with, LockedGate):
                    if collide_with.unlock(self):
                        Player._play_sound(Player.door_open_close)
                    else:
                        from text import MessageBox
                        MessageBox(("That gate needs a key.", 1), 180)
                    break

        if symbol == pyglet.window.key.C and (self.has_sword or self.has_scythe):
            self.slash_sword()

        if symbol == pyglet.window.key.F5:
            SaveGame.save(self.progress, self)
            from text import MessageBox
            MessageBox(("Game saved.", 1), 120)

        if symbol == pyglet.window.key.F9:
            progress, player_state = SaveGame.load()
            self.progress = progress
            EngineGlobals.progress = progress
            if player_state:
                target_map = player_state.get("map", "map.dill")
                if getattr(EngineGlobals.game_map, "filename", None) != target_map:
                    GameMap.load_map(target_map)
                self.current_chunk = EngineGlobals.game_map.chunks[0]
                self.x_position = Decimal(str(player_state.get("x", self.x_position)))
                self.y_position = Decimal(str(player_state.get("y", self.y_position)))
                self.x_speed = self.y_speed = Decimal(0)
                self.jumpct = self.JC0_NOT_JUMPING
                self.landed = False
                self.has_sword = bool(player_state.get("has_sword", False))
                self.has_scythe = bool(player_state.get("has_scythe", False))
            from text import MessageBox
            MessageBox(("Game loaded.", 1), 120)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.is_dead or not self.angel_active:
            return pyglet.event.EVENT_UNHANDLED
        angel_sx = float(EngineGlobals.screen_x(self.angel_x))
        angel_sy = float(EngineGlobals.screen_y(self.angel_y))
        if angel_sx - 42 <= x <= angel_sx + 42 and angel_sy - 20 <= y <= angel_sy + 66:
            self._respawn_from_angel()
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_PhysicsSprite_landed(self):
        self.jumpct = self.JC0_NOT_JUMPING
        self.jump_frames = 0
        self.landed = True

    def shoot_it(self):
        # Deliberately spawn on the front; Bullet repositions itself to Kenny's rear and reverses direction.
        if self.direction == "right":
            bullet_speed = (Player.BULLET_INITIAL_VELOCITY, 0)
            bullet_pos = (self.x_position + 41, self.y_position + 22)
        else:
            bullet_speed = (-Player.BULLET_INITIAL_VELOCITY, 0)
            bullet_pos = (self.x_position - 5, self.y_position + 22)
        makeSprite(Bullet, self.current_chunk, bullet_pos, starting_speed=bullet_speed)
        Player._play_sound(Player.spit_bullet)

    def hit(self):
        if self.is_dead:
            return
        if not self.bloody:
            self.bloody = True
        else:
            self.die_hard()

    def slash_sword(self):
        if self.direction == "left":
            makeSprite(SwordHit, self.current_chunk, (self.x_position - 15, self.y_position + 20), direction="left")
        else:
            makeSprite(SwordHit, self.current_chunk, (self.x_position + 41, self.y_position + 20), direction="right")
        if self.has_sword:
            Player._play_sound(Player.swipe_sword)
        if self.has_scythe:
            Player._play_sound(Player.schimmy_scythe)

    def die_hard(self):
        if self.is_dead:
            return
        self.is_dead = True
        self.death_timer = 16
        self.x_speed = Decimal(0)
        self.y_speed = Decimal(0)
        self.jumpct = self.JC0_NOT_JUMPING
        self.jump_frames = 0
        self.crouching = False
        self.sprite.visible = False
        DeathBurst(self.x_position + Decimal(16), self.y_position + Decimal(18))

    def activate_super_powers(self):
        pass

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if self.is_dead:
            return
        if collided_object and type(collided_object).__name__ in ("Spike", "HazardBlock"):
            if self.hit_cooldown == 0:
                self.hit()
                self.hit_cooldown = 30
        elif collided_object and isinstance(collided_object, Enemy):
            if self.hit_cooldown == 0:
                self.hit()
                self.hit_cooldown = 30
        elif collided_object and type(collided_object).__name__ == "Bandaid":
            self.bloody = False
            collided_object.destroy()
        elif collided_object and type(collided_object).__name__ == "NirvanaFruit" and not collided_object.collected:
            collided_object.collect()
            Player._play_sound(Player.munching_on_apple)
            self.activate_super_powers()
        super().on_PhysicsSprite_collided(collided_object=collided_object)

    def getCollisionBox(self):
        # Player physics must not change when animation art changes size.
        return (self.default_collision_width, self.default_collision_height)

    def on_finalDeletion(self):
        self._delete_angel()
        super().on_finalDeletion()


class SwordHit(PhysicsSprite):
    def __init__(self, sprite_initializer, current_chunk):
        super().__init__(sprite_initializer, current_chunk)
        self.slash_sword_counter = 10
        self.sprite.image = self.resource_images[sprite_initializer["direction"]]

    def hasGravity(self):
        return False

    def updateloop(self, dt):
        super().updateloop(dt)
        if self.slash_sword_counter > 0:
            self.slash_sword_counter -= 1
        else:
            self.destroy()

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if collided_object and hasattr(collided_object, "on_pokey"):
            if self.slash_sword_counter > 0:
                self.slash_sword_counter = 0
                self.destroy()
                collided_object.on_pokey()
        elif collided_object and type(collided_object).__name__ == "BreakableBlock":
            collided_object.break_block()
            if collided_chunk is not None and chunk_x is not None and chunk_y is not None:
                collided_chunk.platform[chunk_y][chunk_x] = 0
            self.destroy()

    def getResourceImages(self):
        return {
            "left": {"file": "swordswish.png", "rows": 1, "columns": 4, "duration": 1 / 10, "loop": False},
            "right": {
                "file": "swordswish.png",
                "rows": 1,
                "columns": 4,
                "duration": 1 / 10,
                "loop": False,
                "flip_x": True,
            },
        }
