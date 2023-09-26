import pyglet
from decimal import Decimal
from engineglobals import EngineGlobals
from bullet import Bullet
from physics import *
import random



class Enemy(PhysicsSprite):
    
    def __init__(self,):

        PhysicsSprite.__init__(self, has_gravity=True, resource_image_dict={
            'left': pyglet.resource.image("mrspudl.png",),
            'dead': pyglet.resource.image("deadspud.png"),
        })
        
        self.moving_time = 0
        

    def updateloop(self, dt):
        
        if hasattr(self, 'dead_timer'):
            self.dead_timer += 1
            if self.dead_timer == 120:
                self.destroy()

        self.moving_time += 1
        self.speed[0] = Decimal(0)
        if self.moving_time > 10:
           self.speed[0] = Decimal(random.randrange(-5, 50))
           self.moving_time = 0

        PhysicsSprite.updateloop(self, dt)
      
    def die_hard(self,):
        
        if self.image != self.resource_images['dead']:
            self.dead_timer = 0
            self.image = self.resource_images['dead']
            dead_dude = pyglet.media.load('audio/glurk.wav', streaming=False)
            dead_dude.play()
