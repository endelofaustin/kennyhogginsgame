import pyglet
from decimal import Decimal
from physics import *
from sprite import makeSprite
import random

class Enemy(PhysicsSprite):
    
    def __init__(self, sprite_initializer : dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.moving_time = 0
        self.hit_count = 0

        # new hotness: death debouncer 3000
        self.is_dying = False
        self.death_done = False
        self.death_timer = -1  # countdown clock o’ doom

        if not hasattr(Enemy, 'hit_snd'):
            Enemy.hit_snd = pyglet.resource.media('glurk.wav', streaming=False)

    def getResourceImages(self):
        return {
            '0': "mrspudl.png",
            'dead': "deadspud.png"
        }

    # start the party: switch to dead sprite + set timer
    def start_death(self, delay_frames=15, dead_key='dead'):
        if self.is_dying or self.death_done:
            return
        self.is_dying = True
        self.sprite.image = self.resource_images[dead_key]
        self.death_timer = delay_frames

    # finish him! (Mortal Kombat voice)
    def finish_death(self):
        if self.death_done:
            return
        self.death_done = True
        self.on_finish_death()
        # don’t use sprite.delete() lifecycle will like clean it up and stuff
        self.destroy()

    # bosses can override this to like spawn other stuff like doors or bombs or lavad burtim or timburtim whateverrrr. 
    def on_finish_death(self):
        pass

    def updateloop(self, dt):
        # if we be  dying, freeze in place run the clock
        if self.is_dying or self.death_done:
            self.x_speed = Decimal(0)
            self.y_speed = Decimal(0)
            if self.is_dying and self.death_timer >= 0:
                self.death_timer -= 1
                if self.death_timer <= 0 and not self.death_done:
                    self.finish_death()
            return  # don’t let PhysicsSprite dig up our dead body

        # regular enemy jitterbug
        self.moving_time += dt
        if self.moving_time > 100 and self.y_speed <= 0:
           self.x_speed = Decimal(random.randrange(-10, 10))
           self.y_speed = Decimal(random.randrange(0, 10))
           self.moving_time = 0

        PhysicsSprite.updateloop(self, dt)

    def make_it_jump(self,):
        self.y_speed = 10
        self.x_speed = Decimal(random.randrange(-10, 10))

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        # if collided_object == None or type(collided_object).__name__ == 'Block':
        #      self.make_it_jump()
        pass

    def on_PhysicsSprite_landed(self):
        self.make_it_jump()

    def die_hard(self,):
        # keep but now debounced like a pro
        if self.is_dying or self.death_done:
            return
        Enemy.hit_snd.play()
        self.start_death(delay_frames=15, dead_key='dead')

    def on_pokey(self):
        self.hit_count += 1
        if self.hit_count > 3:
            self.die_hard()


class Doggy(Enemy):

    def __init__(self, sprite_initializer : dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.moving_time = 0

    def getResourceImages(self):
        return {0: "doggy.png"}


class Cardi(PhysicsSprite):

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer, starting_chunk)

    def hasGravity(self):
        return True

    def getResourceImages(self):
        return {0: "bosses/cardi_tree-1.png.png"}

