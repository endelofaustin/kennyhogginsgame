from enemies import Enemy
from physics import PhysicsSprite
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet
from maploader import GameMap
from sprite import makeSprite
from gameplay import GameProgress, SaveGame, LockedGate


# the player object represents Kenny and responds to keyboard input
class Player(PhysicsSprite):
    LEFT_RIGHT_RUN_SPEED = Decimal(4.3)
    CRAWL_SPEED = LEFT_RIGHT_RUN_SPEED * Decimal("0.45")
    JUMP_INITIAL_VELOCITY = 12
    DOUBLE_JUMP_VELOCITY = 9
    BULLET_INITIAL_VELOCITY = Decimal("15.0")

    JUMP_CROUCH_FRAMES = 6
    JC0_NOT_JUMPING = 0
    JC1_CROUCHING_FOR_JUMP = 1
    JC2_FIRST_JUMP = 2
    JC3_SECOND_JUMP = 3

    _active_audio_players = []

    @classmethod
    def _play_sound(cls, sound):
        player = sound.play()
        cls._active_audio_players.append(player)

        def _cleanup():
            try:
                cls._active_audio_players.remove(player)
            except ValueError:
                pass

        player.on_player_eos = _cleanup
        return player

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

        self.direction = "right"
        self.has_sword = False
        self.has_scythe = False
        self.progress = getattr(EngineGlobals, "progress", GameProgress())
        EngineGlobals.progress = self.progress

        self.jumpct = 0
        self.jump_frames = 0

        self.bloody = False
        self.crouching = False
        self.hit_cooldown = 0

        if not hasattr(Player, "door_open_close"):
            Player.door_open_close = pyglet.resource.media("door_open_close.wav", streaming=False)
        if not hasattr(Player, "spit_bullet"):
            Player.spit_bullet = pyglet.resource.media("spitbullets.wav", streaming=False)
        if not hasattr(Player, "swipe_sword"):
            Player.swipe_sword = pyglet.resource.media("swordswipe.wav", streaming=False)
        if not hasattr(Player, "schimmy_scythe"):
            Player.schimmy_scythe = pyglet.resource.media("schimmyscythe.wav", streaming=False)
        if not hasattr(Player, "munching_on_apple"):
            Player.munching_on_apple = pyglet.resource.media(
                "kenny_sounds/munching_on_apple.wav", streaming=False
            )

    def getResourceImages(self):
        return {
            "right": {"file": "kennystance1-2.png.png"},
            "left": {"file": "kennystance-left.png"},
            "bloody": {"file": "bloodykenny-1.png"},
            "crouch_left": {"file": "kenny-crouch-left.png"},
            "crouch_right": {"file": "kenny-crouch-right.png"},
            "run_left": {
                "file": "kenny-run-left.png",
                "rows": 1,
                "columns": 4,
                "duration": 1 / 10,
                "loop": True,
            },
            "run_right": {
                "file": "kenny-run-right.png",
                "rows": 1,
                "columns": 4,
                "duration": 1 / 10,
                "loop": True,
            },
            "jump_left": {
                "file": "kenny-jump-left.png",
                "rows": 1,
                "columns": 2,
                "duration": 1 / 10,
                "loop": False,
                "anchors": [(10, 0), (10, 0)],
            },
            "jump_right": {
                "file": "kenny-jump-right.png",
                "rows": 1,
                "columns": 2,
                "duration": 1 / 10,
                "loop": False,
                "anchors": [(3, 0), (3, 0)],
            },
            "kenny_sword_left": "kennysword-left.png",
            "kenny_sword_right": "kennysword-right.png",
            "kaboom": "kaboom.png",
        }

    def updateloop(self, dt):
        if hasattr(self, "blow_up_timer"):
            if self.blow_up_timer <= 20:
                self.sprite.image = self.resource_images["kaboom"]
            self.blow_up_timer -= 1
            return

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        self.x_speed = Decimal(0)

        self.crouching = bool(EngineGlobals.keys[pyglet.window.key.DOWN] and self.landed)
        move_speed = Player.CRAWL_SPEED if self.crouching else Player.LEFT_RIGHT_RUN_SPEED

        if EngineGlobals.keys[pyglet.window.key.LEFT]:
            self.x_speed -= Decimal(move_speed)
        if EngineGlobals.keys[pyglet.window.key.RIGHT]:
            self.x_speed += Decimal(move_speed)

        if self.x_speed < 0:
            self.direction = "left"
        elif self.x_speed > 0:
            self.direction = "right"

        if self.crouching:
            self.sprite.image = self.resource_images[
                "crouch_left" if self.direction == "left" else "crouch_right"
            ]
        elif self.jumpct > Player.JC0_NOT_JUMPING:
            self.jump_frames += 1
            if self.jumpct == Player.JC1_CROUCHING_FOR_JUMP and self.jump_frames >= Player.JUMP_CROUCH_FRAMES:
                self.jumpct = Player.JC2_FIRST_JUMP
                self.y_speed = Decimal(max(self.y_speed, 0) + Player.JUMP_INITIAL_VELOCITY)
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
            self.sprite.image = self.resource_images[
                "kenny_sword_right" if self.direction == "right" else "kenny_sword_left"
            ]

        PhysicsSprite.updateloop(self, dt)

    def on_key_press(self, symbol, modifiers):
        if (
            symbol in (pyglet.window.key.LCTRL, pyglet.window.key.RCTRL, pyglet.window.key.UP)
            and self.jumpct <= Player.JC2_FIRST_JUMP
        ):
            if self.landed and self.jumpct == Player.JC0_NOT_JUMPING:
                self.jumpct = Player.JC1_CROUCHING_FOR_JUMP
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
                    self.x_position, self.y_position = collide_with.sprite_initializer["player_position"]
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

        # F5/F9 are deliberately conventional quick-save/quick-load keys.
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
                self.x_position = Decimal(str(player_state.get("x", self.x_position)))
                self.y_position = Decimal(str(player_state.get("y", self.y_position)))
                self.has_sword = bool(player_state.get("has_sword", False))
                self.has_scythe = bool(player_state.get("has_scythe", False))
            from text import MessageBox
            MessageBox(("Game loaded.", 1), 120)

    def on_PhysicsSprite_landed(self):
        self.jumpct = 0

    def shoot_it(self):
        if self.direction == "right":
            bullet_speed = (Player.BULLET_INITIAL_VELOCITY, 0)
            bullet_pos = (self.x_position + 41, self.y_position + 22)
        else:
            bullet_speed = (-Player.BULLET_INITIAL_VELOCITY, 0)
            bullet_pos = (self.x_position - 5, self.y_position + 22)

        makeSprite(Bullet, self.current_chunk, bullet_pos, starting_speed=bullet_speed)
        Player._play_sound(Player.spit_bullet)

    def hit(self):
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
        self.sprite.image = pyglet.resource.image("lucinda.png")
        self.blow_up_timer = 40

    def activate_super_powers(self):
        pass

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
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
        if isinstance(self.sprite.image, pyglet.image.Animation):
            return (
                self.sprite.image.get_max_width() * EngineGlobals.scale_factor,
                self.sprite.image.get_max_height() * EngineGlobals.scale_factor,
            )
        return (
            self.sprite.image.width * EngineGlobals.scale_factor,
            self.sprite.image.height * EngineGlobals.scale_factor,
        )


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
