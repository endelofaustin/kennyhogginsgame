from physics import PhysicsSprite
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet
from maploader import GameMap
from sprite import makeSprite


# the player object represents Kenny and responds to keyboard input
class Player(PhysicsSprite):
    LEFT_RIGHT_RUN_SPEED = Decimal(4.3)
    CRAWL_SPEED = LEFT_RIGHT_RUN_SPEED * Decimal('0.45')  # striscia piano: la “famiglia” nota tutto, capisce? Crawl slowly the family sees everything... you understand? 
    JUMP_INITIAL_VELOCITY = 12
    DOUBLE_JUMP_VELOCITY = 9
    BULLET_INITIAL_VELOCITY = Decimal('15.0')

    JUMP_CROUCH_FRAMES = 6
    JC0_NOT_JUMPING = 0
    JC1_CROUCHING_FOR_JUMP = 1
    JC2_FIRST_JUMP = 2
    JC3_SECOND_JUMP = 3

    # Keep returned pyglet.media.Player objects alive while audio plays.
    _active_audio_players = []

    @classmethod
    def _play_sound(cls, sound):
        p = sound.play()
        cls._active_audio_players.append(p)

        def _cleanup(_player):
            try:
                cls._active_audio_players.remove(_player)
            except ValueError:
                pass

        p.on_player_eos = lambda: _cleanup(cls)
        return p

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

        # Which direction is Kenny facing?
        self.direction = 'right'

        # Does he have a sword?
        self.has_sword = False
        self.has_scythe = False

        # jumpct counts the number of jumps to allow for double-jumping
        self.jumpct = 0
        self.jump_frames = 0

        # let's get that blood flowing
        self.bloody = False
        self.crouching = False

        # Contact damage cooldown
        self.hit_cooldown = 0  # tempo di rispetto: se esageri, finisci “a dormire coi pesci” -- time of respect: if you exaggerate you finish slleping with the fishes. 

        # Preload shared audio once.
        if not hasattr(Player, 'door_open_close'):
            Player.door_open_close = pyglet.resource.media("door_open_close.wav", streaming=False)
        if not hasattr(Player, 'spit_bullet'):
            Player.spit_bullet = pyglet.resource.media("spitbullets.wav", streaming=False)
        if not hasattr(Player, 'swipe_sword'):
            Player.swipe_sword = pyglet.resource.media("swordswipe.wav", streaming=False)
        if not hasattr(Player, 'schimmy_scythe'):
            Player.schimmy_scythe = pyglet.resource.media("schimmyscythe.wav", streaming=False)
        if not hasattr(Player, 'munching_on_apple'):
            Player.munching_on_apple = pyglet.resource.media(
                "kenny_sounds/munching_on_apple.wav", streaming=False
            )

    def getResourceImages(self):
        return {
            'right': {'file': "kennystance1-2.png.png"},
            'left': {'file': "kennystance-left.png"},
            'bloody': {'file': "bloodykenny-1.png"},
            'crouch_left': {'file': "kenny-crouch-left.png"},
            'crouch_right': {'file': "kenny-crouch-right.png"},
            'run_left': {
                'file': "kenny-run-left.png",
                'rows': 1, 'columns': 4,
                'duration': 1 / 10,
                'loop': True
            },
            'run_right': {
                'file': "kenny-run-right.png",
                'rows': 1, 'columns': 4,
                'duration': 1 / 10,
                'loop': True
            },
            'jump_left': {
                'file': "kenny-jump-left.png",
                'rows': 1, 'columns': 2,
                'duration': 1 / 10,
                'loop': False,
                'anchors': [(10, 0), (10, 0)]
            },
            'jump_right': {
                'file': "kenny-jump-right.png",
                'rows': 1, 'columns': 2,
                'duration': 1 / 10,
                'loop': False,
                'anchors': [(3, 0), (3, 0)]
            },
            'kenny_sword_left': "kennysword-left.png",
            'kenny_sword_right': "kennysword-right.png",
            'kaboom': "kaboom.png"
        }

    def updateloop(self, dt):
        # John has done 5 flight lessons as of nov 21 23..... corrections only 4
        # John has done 38 out of 40 hours flight lessons for private feb 2024
        if hasattr(self, "blow_up_timer"):
            if self.blow_up_timer <= 20:
                self.sprite.image = self.resource_images['kaboom']
            self.blow_up_timer -= 1
            return

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1  # raffreddamento: prima il “messaggio”, poi il funerale -- cooldown... first comes the message then the funeral. 

        self.x_speed = Decimal(0)

        if EngineGlobals.keys[pyglet.window.key.DOWN] and self.landed:
            self.crouching = True  # accovacciati… o qualcuno ti fa accovacciare PER SEMPRE -- crouch or someone will make you crouch forever
        else:
            self.crouching = False

        move_speed = Player.CRAWL_SPEED if self.crouching else Player.LEFT_RIGHT_RUN_SPEED  # strisci o corri: scegli bene, la famiglia non perdona -- crawl or run choose carefully, the family does not forgive

        # interpret arrow keys into velocity like a boss
        if EngineGlobals.keys[pyglet.window.key.LEFT]:
            self.x_speed -= Decimal(move_speed)
        if EngineGlobals.keys[pyglet.window.key.RIGHT]:
            self.x_speed += Decimal(move_speed)

        if self.x_speed < 0:
            self.direction = 'left'
        elif self.x_speed > 0:
            self.direction = 'right'

        if self.crouching:
            if self.direction == 'left':
                self.sprite.image = self.resource_images['crouch_left']
            else:
                self.sprite.image = self.resource_images['crouch_right']
        elif self.jumpct > Player.JC0_NOT_JUMPING:
            self.jump_frames += 1
            if self.jumpct == Player.JC1_CROUCHING_FOR_JUMP and self.jump_frames >= Player.JUMP_CROUCH_FRAMES:
                self.jumpct = Player.JC2_FIRST_JUMP
                self.y_speed = Decimal(max(self.y_speed, 0) + Player.JUMP_INITIAL_VELOCITY)
                self.landed = False
            if self.direction == 'left':
                if self.sprite.image != self.resource_images['jump_left']:
                    self.sprite.image = self.resource_images['jump_left']
            else:
                if self.sprite.image != self.resource_images['jump_right']:
                    self.sprite.image = self.resource_images['jump_right']
        else:
            if self.x_speed < 0:
                if self.sprite.image != self.resource_images['run_left']:
                    self.sprite.image = self.resource_images['run_left']
            elif self.x_speed > 0:
                if self.sprite.image != self.resource_images['run_right']:
                    self.sprite.image = self.resource_images['run_right']
            elif self.direction == 'left':
                if self.sprite.image != self.resource_images['left']:
                    self.sprite.image = self.resource_images['left']
            else:
                if self.sprite.image != self.resource_images['right']:
                    self.sprite.image = self.resource_images['right']

        if self.bloody is True:
            self.sprite.image = self.resource_images['bloody']

        if self.landed and self.jumpct != Player.JC1_CROUCHING_FOR_JUMP:
            self.jumpct = Player.JC0_NOT_JUMPING
            self.jump_frames = 0

        if self.has_sword:
            if self.direction == 'right':
                self.sprite.image = self.resource_images['kenny_sword_right']
            if self.direction == 'left':
                self.sprite.image = self.resource_images['kenny_sword_left']

        # then, run normal physics algorithm
        PhysicsSprite.updateloop(self, dt)

    # on_key_press is called by the pyglet engine when attached to a window
    # this lets us handle keyboard input events at the time they occur
    def on_key_press(self, symbol, modifiers):
        # jumping
        if (symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL or symbol == pyglet.window.key.UP) and self.jumpct <= Player.JC2_FIRST_JUMP:
            # if on a solid object, crouch then jump
            if self.landed and self.jumpct == Player.JC0_NOT_JUMPING:
                self.jumpct = Player.JC1_CROUCHING_FOR_JUMP
            # if already in the air, allow one more smaller jump
            elif self.jumpct == Player.JC2_FIRST_JUMP:
                self.y_speed = Player.DOUBLE_JUMP_VELOCITY
                self.jumpct = Player.JC3_SECOND_JUMP

        # Button press handeling for space bar to shoot
        if symbol == pyglet.window.key.SPACE:
            self.shoot_it()

        # door entry
        if symbol == pyglet.window.key.D:
            for collide_with in self.get_all_colliding_objects():
                if type(collide_with).__name__ == 'Door':
                    Player._play_sound(Player.door_open_close)
                    GameMap.load_map(collide_with.sprite_initializer['target_map'])
                    self.x_position, self.y_position = collide_with.sprite_initializer['player_position']

        # sword slash
        if symbol == pyglet.window.key.C and (self.has_sword or self.has_scythe):
            self.slash_sword()

    # this function is called by the physics simulator when it detects landing on a solid object
    def on_PhysicsSprite_landed(self):
        # set our jumpct back to zero to allow future jumps
        self.jumpct = 0

    # Lets do some shooting
    def shoot_it(self):
        bullet_speed = (Player.BULLET_INITIAL_VELOCITY, 0)
        bullet_pos = (self.x_position + 5, self.y_position + 22)
        if self.direction == 'right':
            bullet_speed = (0 - Player.BULLET_INITIAL_VELOCITY, 0)
            bullet_pos = (self.x_position - 5, self.y_position + 22)

        makeSprite(Bullet, self.current_chunk, bullet_pos, starting_speed=bullet_speed)

        # Play the bullet spit audio (retain returned Player to avoid GC crashes)
        Player._play_sound(Player.spit_bullet)

    def hit(self):
        if not self.bloody:
            self.bloody = True
        else:
            self.die_hard()

    def slash_sword(self):
        if self.direction == 'left':
            makeSprite(SwordHit, self.current_chunk, (self.x_position - 15, self.y_position + 20), direction='left')
        else:
            makeSprite(SwordHit, self.current_chunk, (self.x_position + 41, self.y_position + 20), direction='right')

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
        if collided_object and type(collided_object).__name__ == 'Spike':
            self.bloody = True

        elif collided_object and (hasattr(collided_object, 'getting_hit') or hasattr(collided_object, 'on_pokey')):
            # Enemies/bosses/spud hurt Kenny on contact, but not every single frame while overlapping.
            if self.hit_cooldown == 0:
                self.hit()  # toccato il tipo sbagliato… adesso paga il “pizzo” con la faccia 😈🤌
                self.hit_cooldown = 30  # tregua breve: la famiglia concede… ma non dimentica

        elif collided_object and type(collided_object).__name__ == 'Bandaid':
            self.bloody = False
            collided_object.destroy()

        elif collided_object and type(collided_object).__name__ == 'NirvanaFruit' and not collided_object.collected:
            collided_object.collect()
            Player._play_sound(Player.munching_on_apple)
            self.activate_super_powers()

        super().on_PhysicsSprite_collided(collided_object=collided_object)

    def getCollisionBox(self):
        if isinstance(self.sprite.image, pyglet.image.Animation):
            return (
                self.sprite.image.get_max_width() * EngineGlobals.scale_factor,
                self.sprite.image.get_max_height() * EngineGlobals.scale_factor
            )
        else:
            return (
                self.sprite.image.width * EngineGlobals.scale_factor,
                self.sprite.image.height * EngineGlobals.scale_factor
            )


# expanding bouding box for sword hits cause they super cool and gangsta
# vorriste morire??? no non voglio morire
class SwordHit(PhysicsSprite):
    def __init__(self, sprite_initializer, current_chunk):
        super().__init__(sprite_initializer, current_chunk)
        self.slash_sword_counter = 10
        self.sprite.image = self.resource_images[sprite_initializer['direction']]

    def hasGravity(self):
        return False

    def updateloop(self, dt):
        super().updateloop(dt)

        if self.slash_sword_counter > 0:
            self.slash_sword_counter -= 1
        else:
            self.destroy()

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if collided_object and hasattr(collided_object, 'on_pokey'):
            if self.slash_sword_counter > 0:
                self.slash_sword_counter = 0
                self.destroy()
                collided_object.on_pokey()

    def getResourceImages(self):
        return {
            'left': {'file': "swordswish.png", 'rows': 1, 'columns': 4, 'duration': 1/10, 'loop': False},
            'right': {'file': "swordswish.png", 'rows': 1, 'columns': 4, 'duration': 1/10, 'loop': False, 'flip_x': True},
        }
