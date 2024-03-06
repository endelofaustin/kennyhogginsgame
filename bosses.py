import pyglet
import dill, pickle
import gamepieces
from engineglobals import EngineGlobals
from enemies import Enemy
from physics import PhysicsSprite
import random
from decimal import Decimal
from gamepieces import Door
from lifecycle import LifeCycleManager
from sprite import makeSprite

class PearlyPaul(Enemy):

    def __init__(self, sprite_initializer : dict, starting_chunk):

        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

        self.moving_time = 0
        self.pearl_dropping_time = 0 

        if not hasattr(PearlyPaul, 'poop_pearl'):
            PearlyPaul.poop_pearl = pyglet.media.load('audio/plop.mp3', streaming=False)

        self.hit_count = 0

    def getResourceImages(self):
        return {
            'left': 'pearly_paul.png',
            'dead': 'lucinda.png'
        }

    def updateloop(self, dt):

        if hasattr(self, 'dead_timer'):
            if self.dead_timer >= 59:
                makeSprite(Door, self.current_chunk, starting_position=(1000, 0), group='BACK', target_map='map.dill', player_position=(1350, 320))
                makeSprite(Door, self.current_chunk, starting_position=(550, 0), group='BACK', target_map='map.dill', player_position=(550, 32))
                makeSprite(Door, self.current_chunk, starting_position=(770, 0), group='BACK', target_map='map.dill', player_position=(670, 3456))

                for sprite in LifeCycleManager.ALL_SETS['PER_MAP'].objects:
                    if type(sprite).__name__ == 'Pearl':
                        sprite.destroy()

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

        super().updateloop(dt)

    def drop_pearl(self):
        # John thinks this is very interesting. and that this sucks why would we have to do that...
        # that is what we have to do. we need an add_list function in engineglobals, we cant create game objects on the fly in the update
        # Loop... hahaha pig candy.
        pearl = makeSprite(Pearl, self.current_chunk, (self.x_position, self.y_position + 22), starting_speed=(0, -12))
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

    def __init__(self, sprite_initializer : dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

    def getResourceImages(self):
        return {
            'pearl_left': {'file': "pearled_out.png", 'rows': 3, 'columns': 2, 'duration': 1/10, 'loop': True},
            'pearl_right': {'file': "pearled_out.png", 'rows': 3, 'columns': 2, 'duration': 1/10, 'loop': True},
            'dead': 'sushiroll.png'
        }

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):

        if collided_object and type(collided_object).__name__ == 'Player':
            collided_object.hit()
