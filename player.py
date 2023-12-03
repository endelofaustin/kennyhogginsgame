
from physics import PhysicsSprite, SpriteBatch
import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet
from maploader import GameMap

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

    def __init__(self):
        PhysicsSprite.__init__(self, {
            'has_gravity': True,
            'resource_images': {
                'right': "kennystance1-2.png.png",
                'left': "kennystance-left.png",
                'bloody': "bloodykenny-1.png",
                'crouch_left': "kenny-crouch-left.png",
                'crouch_right': "kenny-crouch-right.png",
                'run_left': {'file': "kenny-run-left.png", 'rows': 1, 'columns': 4, 'duration': 1/10, 'loop': True},
                'run_right': {'file': "kenny-run-right.png", 'rows': 1, 'columns': 4, 'duration': 1/10, 'loop': True},
                'jump_left': {'file': "kenny-jump-left.png", 'rows': 1, 'columns': 2, 'duration': 1/10, 'loop': False},
                'jump_right': {'file': "kenny-jump-right.png", 'rows': 1, 'columns': 2, 'duration': 1/10, 'loop': False}
            },
            'group': SpriteBatch.FRONT
        })

        # Which direction is Kenny facing?
        self.direction = 'right'

        # jumpct counts the number of jumps to allow for double-jumping
        self.jumpct = 0
        self.jump_frames = 0
        self.spit_bullet = pyglet.media.load("audio/spitbullets.wav", streaming=False)

        # let's get that blood flowing
        self.bloody = False

        self.crouching = False

        if not hasattr(Player, 'door_open_close'):
            Player.door_open_close = pyglet.media.load("audio/door_open_close.mp3", streaming=False)


    def updateloop(self, dt):

        # John has done 5 flight lessons as of nov 21 24..... corrections only 4
        if hasattr(self, "blow_up_timer"):

            if self.blow_up_timer <= 20:
                self.sprite.image = pyglet.resource.image("kaboom.png")
            
            self.blow_up_timer -= 1


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

        # then, run normal physics algorithm
        PhysicsSprite.updateloop(self, dt)

    # on_key_press is called by the pyglet engine when attached to a window
    # this lets us handle keyboard input events at the time they occur
    def on_key_press(self, symbol, modifiers):
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
                    EngineGlobals.game_map = GameMap.load_map("bossfight.dill")

    # this function is called by the physics simulator when it detects landing on a solid object
    def on_PhysicsSprite_landed(self):
        # set our jumpct back to zero to allow future jumps
        self.jumpct = 0

    # Lets do some shooting

    def shoot_it(self):
        bullet = Bullet()
        if self.direction == 'right':
            bullet.x_speed -= Player.BULLET_INITIAL_VELOCITY
            bullet.x_position,bullet.y_position = self.x_position - 5, self.y_position + 22
        else:
            bullet.x_speed += Player.BULLET_INITIAL_VELOCITY
            bullet.x_position,bullet.y_position = self.x_position + 5, self.y_position + 22
        # Play the bullet spit audio
        self.spit_bullet.play()

    def hit(self):

        if not self.bloody:
            self.bloody = True
        else:
            self.die_hard()

    def die_hard(self):

        self.sprite.image = pyglet.resource.image("lucinda.png")
        self.blow_up_timer = 40
        
    def on_PhysicsSprite_collided(self, collided_object=None):
        
        if collided_object and type(collided_object).__name__ == 'Spike':
            self.bloody = True
        elif collided_object and type(collided_object).__name__ == 'Bandaid':
            self.bloody = False
            collided_object.destroy()            
