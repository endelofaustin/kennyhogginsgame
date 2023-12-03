import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet
from physics import *
import random


class Enemy(PhysicsSprite):
    
    def __init__(self, init_params={
        'has_gravity': True,
        'resource_images': {
            '0': "mrspudl.png",
            'dead': "deadspud.png"
        }
    }):

        PhysicsSprite.__init__(self, init_params)

        self.moving_time = 0


    def updateloop(self, dt):
        
        if hasattr(self, 'dead_timer'):
            self.dead_timer += 1
            if self.dead_timer == 60:
                self.destroy()

        self.moving_time += 1
        self.x_speed = Decimal(0)
        if self.moving_time > 200 and self.y_speed <= 0:
           self.x_speed = Decimal(random.randrange(-50, 50))
           self.y_speed = Decimal(random.randrange(1, 10))
           self.moving_time = 0

        PhysicsSprite.updateloop(self, dt)

    def make_it_jump(self,):

        self.y_speed = 10
        self.x_speed = Decimal(random.randrange(-50, 50))

    def on_PhysicsSprite_collided(self, collided_object=None):

        if collided_object == None:
            self.make_it_jump()

    def die_hard(self,):

        if self.image != self.resource_images['dead']:

            self.dead_timer = 0
            self.image = self.resource_images['dead']
            dead_dude = pyglet.media.load('audio/glurk.wav', streaming=False)
            dead_dude.play()

class Doggy(Enemy):

     def __init__(self, init_params={'has_gravity': True, 'resource_images': {0: "doggy.png"}}):

        PhysicsSprite.__init__(self, init_params)

        self.moving_time = 0
