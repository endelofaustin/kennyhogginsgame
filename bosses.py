import pyglet
import dill, pickle
import gamepieces
from engineglobals import EngineGlobals
from enemies import Enemy
from physics import PhysicsSprite
import random
from decimal import Decimal

class PearlyPaul(Enemy):

    def __init__(self,):

         PhysicsSprite.__init__(self, has_gravity=True, resource_image_dict={
            'left': pyglet.resource.image("pearly_paul.png"),
        })
         
         self.moving_time = 0
         self.pearl_dropping_time = 0 
         self.poop_pearl = pyglet.media.load("audio/plop.mp3", streaming=False)
    
    def updateloop(self, dt):

       if hasattr(self, 'dead_timer'):
           self.dead_timer += 1
           if self.dead_timer == 60:
               self.destroy()
       
       if self.pearl_dropping_time <= 0:
           self.drop_pearl()
       else:
           self.pearl_dropping_time -= 1

       
       self.moving_time += 1
       self.x_speed = Decimal(0)
       if self.moving_time > 200 and self.y_speed <= 0:
          self.x_speed = Decimal(random.randrange(-50, 50))
          self.y_speed = Decimal(random.randrange(1, 10))
          self.moving_time = 0

       PhysicsSprite.updateloop(self, dt)

    def drop_pearl(self):
        # John thinks this is very interesting. and that this sucks why would we have to do that...
        # that is what we have to do. we need an add_list function in engineglobals, we cant create game objects on the fly in the update
        # Loop... hahaha pig candy.
        pearl = Pearl()
        pearl.y_speed = -12
        pearl.x_position,pearl.y_position = self.x_position, self.y_position + 22
        self.pearl_dropping_time = random.randrange(50 ,500)
        PearlyPaul.poop_pearl.play()

class Pearl(PhysicsSprite):

    def __init__(self,):
        PhysicsSprite.__init__(self, has_gravity=True, resource_image_dict={
           'left': pyglet.resource.image("left_pearl.png"),
           'right': pyglet.resource.image("right_pearl.png"),
           'down': pyglet.resource.image("down_pearl.png"),
           'reg': pyglet.resource.image("reg_pearl.png"
           )
        })

    def on_PhysicsSprite_collided(self, collided_object=None):
        
        if collided_object and type(collided_object).__name__ == 'Player':
            return
        
        if type(collided_object).__name__ == 'Player':
            collided_object.hit()

