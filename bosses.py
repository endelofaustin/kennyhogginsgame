import pyglet
import dill, pickle
import gamepieces
from engineglobals import EngineGlobals
from enemies import Enemy
from physics import PhysicsSprite
import random
from decimal import Decimal

class PearlyPaul(Enemy):

    def __init__(self, init_params={
        'has_gravity': True,
        'resource_images': {
            'left': 'pearly_paul.png',
            'dead': 'lucinda.png'
            },
    }, spawn_coords=None, is_map_object=False):

        if spawn_coords:
            init_params['spawn_coords'] = spawn_coords
        PhysicsSprite.__init__(self, init_params, is_map_object=is_map_object)

        self.moving_time = 0
        self.pearl_dropping_time = 0 
        if not hasattr(PearlyPaul, 'poop_pearl'):
            PearlyPaul.poop_pearl = pyglet.media.load('audio/plop.mp3', streaming=False)
        
        self.hit_count = 0

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
        
        if self.moving_time > 100 and self.y_speed <= 0:
            self.x_speed = Decimal(random.randrange(-10, 20))
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
        self.pearl_dropping_time = random.randrange(50 , 500)
        PearlyPaul.poop_pearl.play()

    def getting_hit(self):
        
        self.hit_count += 1

        if self.hit_count >= 4:
       
            self.dead_timer = 0
            self.sprite.image = self.resource_images['dead']
            dead_dude = pyglet.media.load("audio/kenny_sounds/boss_beaten.mp3", streaming=False)
            dead_dude.play()

class Pearl(Enemy):

    def __init__(self,):
        Enemy.__init__(self, {
            'has_gravity': True,
            'resource_images': {
                'pearl_left': {'file': "pearled_out.png", 'rows': 3, 'columns': 2, 'duration': 1/10, 'loop': True},
                'pearl_right': {'file': "pearled_out.png", 'rows': 3, 'columns': 2, 'duration': 1/10, 'loop': True},
                'dead': 'sushiroll.png'
            }
        })

    
    def on_PhysicsSprite_collided(self, collided_object=None):
        
        if collided_object and type(collided_object).__name__ == 'Player':
            collided_object.hit()

