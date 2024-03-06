from physics import PhysicsSprite
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet
from maploader import GameMap
from sprite import makeSprite

# the player object represents Kenny and responds to keyboard input
class Player(PhysicsSprite):
    LEFT_RIGHT_RUN_SPEED = 5
    JUMP_INITIAL_VELOCITY = 12
    DOUBLE_JUMP_VELOCITY = 9
    BULLET_INITIAL_VELOCITY = Decimal('15.0')

    JUMP_CROUCH_FRAMES = 6
    NOT_JUMPING = 0
    CROUCHING_FOR_JUMP = 1
    FIRST_JUMP = 2
    SECOND_JUMP = 3

    def __init__(self, sprite_initializer : dict, starting_chunk):

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

        if not hasattr(Player, 'door_open_close'):
            Player.door_open_close = pyglet.media.load("audio/door_open_close.mp3", streaming=False)
        if not hasattr(Player, 'spit_bullet'):
            Player.spit_bullet = pyglet.media.StaticSource(pyglet.media.load("audio/spitbullets.wav"))
        if not hasattr(Player, 'swipe_sword'):
            Player.swipe_sword = pyglet.media.StaticSource(pyglet.media.load("audio/swordswipe.mp3"))
        if not hasattr(Player, 'schimmy_scythe'):
            Player.schimmy_scythe = pyglet.media.StaticSource(pyglet.media.load("audio/schimmyscythe.mp3"))
            
    def getResourceImages(self):
        return {
            'right': "kennystance1-2.png.png",
            'left': "kennystance-left.png",
            'bloody': "bloodykenny-1.png",
            'crouch_left': "kenny-crouch-left.png",
            'crouch_right': "kenny-crouch-right.png",
            'run_left': {'file': "kenny-run-left.png", 'rows': 1, 'columns': 4, 'duration': 1/10, 'loop': True},
            'run_right': {'file': "kenny-run-right.png", 'rows': 1, 'columns': 4, 'duration': 1/10, 'loop': True},
            'jump_left': {'file': "kenny-jump-left.png", 'rows': 1, 'columns': 2, 'duration': 1/10, 'loop': False},
            'jump_right': {'file': "kenny-jump-right.png", 'rows': 1, 'columns': 2, 'duration': 1/10, 'loop': False},
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

        self.x_speed = Decimal(0)
        
        if EngineGlobals.keys[pyglet.window.key.DOWN] and self.landed:
            self.crouching = True
        else:
            self.crouching = False
            # interpret arrow keys into velocity like a boss
            if EngineGlobals.keys[pyglet.window.key.LEFT]:
                self.x_speed -= Decimal(Player.LEFT_RIGHT_RUN_SPEED)
            if EngineGlobals.keys[pyglet.window.key.RIGHT]:
                self.x_speed += Decimal(Player.LEFT_RIGHT_RUN_SPEED)

        if self.crouching:
            if self.direction == 'left':
                self.sprite.image = self.resource_images['crouch_left']
            else:
                self.sprite.image = self.resource_images['crouch_right']
        elif self.jumpct > Player.NOT_JUMPING:
            self.jump_frames += 1
            if self.jumpct == Player.CROUCHING_FOR_JUMP and self.jump_frames >= Player.JUMP_CROUCH_FRAMES:
                self.jumpct = Player.FIRST_JUMP
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
                self.direction = 'left'
                if self.sprite.image != self.resource_images['run_left']:
                    self.sprite.image = self.resource_images['run_left']
            elif self.x_speed > 0:
                self.direction = 'right'
                if self.sprite.image != self.resource_images['run_right']:
                    self.sprite.image = self.resource_images['run_right']
            elif self.direction == 'left':
                if self.sprite.image != self.resource_images['left']:
                    self.sprite.image = self.resource_images['left']
            else:
                if self.sprite.image != self.resource_images['right']:
                    self.sprite.image = self.resource_images['right']

        if self.bloody == True:
           self.sprite.image = self.resource_images['bloody']

        if self.landed and self.jumpct != Player.CROUCHING_FOR_JUMP:
            self.jumpct = Player.NOT_JUMPING
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
        if (symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL or symbol == pyglet.window.key.UP) and self.jumpct <= Player.FIRST_JUMP:
            # if on a solid object, crouch then jump
            if self.landed and self.jumpct == Player.NOT_JUMPING:
                self.jumpct = Player.CROUCHING_FOR_JUMP
            # if already in the air, allow one more smaller jump
            elif self.jumpct == Player.FIRST_JUMP:
                self.y_speed = Player.DOUBLE_JUMP_VELOCITY
                self.jumpct = Player.SECOND_JUMP

        # Button press handeling for space bar to shoot
        if symbol == pyglet.window.key.SPACE:
            self.shoot_it()

        # door entry
        if symbol == pyglet.window.key.D:
            for collide_with in self.get_all_colliding_objects():
                if type(collide_with).__name__ == 'Door':
                    Player.door_open_close.play()
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

        # Play the bullet spit audio
        Player.spit_bullet.play()

    def hit(self):

        if not self.bloody:
            self.bloody = True
        else:
            self.die_hard()

    def slash_sword(self):

        x_position = self.x_position
        if self.direction == 'left':
            x_position = self.x_position - 15
        makeSprite(SwordHit, self.current_chunk, (x_position, self.y_position + 9))
        
        if self.has_sword:
            Player.swipe_sword.play()
        
        if self.has_scythe:
            Player.schimmy_scythe.play()


    def die_hard(self):

        self.sprite.image = pyglet.resource.image("lucinda.png")
        self.blow_up_timer = 40

    def activate_super_powers(self):
        pass

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        
        if collided_object and type(collided_object).__name__ == 'Spike':
            self.bloody = True

        elif collided_object and type(collided_object).__name__ == 'Bandaid':
            self.bloody = False
            collided_object.destroy()

        elif collided_object and type(collided_object).__name__ == 'NirvanaFruit':
            collided_object.destroy()
            pyglet.media.load('audio/kenny_sounds/munching_on_apple.mp3', streaming=False).play()
            self.activate_super_powers()

        super().on_PhysicsSprite_collided(collided_object=collided_object)

# expanding bouding box for sword hits cuase they super cool and gangsta
# vorriste morire??? no non voglio morire
class SwordHit(PhysicsSprite):

    def __init__(self, sprite_initializer, current_chunk):

        super().__init__(sprite_initializer, current_chunk)
        self.slash_sword_counter = 10

    def getStaticBoundingBox(self):

        return (34, 15)

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
               collided_object.on_pokey()

    def getResourceImages(self):
         return {
             'right': "pixel.png"
                }
