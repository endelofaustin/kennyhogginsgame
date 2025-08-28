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


# Shiny and adorable little pearls 
class Pearl(Enemy):
    def __init__(self, sprite_initializer : dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

    def getResourceImages(self):
        return {
            'pearl_left':  {'file': "pearled_out.png", 'rows': 3, 'columns': 2, 'duration': 1/10, 'loop': True},
            'pearl_right': {'file': "pearled_out.png", 'rows': 3, 'columns': 2, 'duration': 1/10, 'loop': True},
            'dead': 'sushiroll.png'
        }

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if collided_object and type(collided_object).__name__ == 'Player':
            collided_object.hit()


# A crazy coffee shop owner turned professional pearl producer
class PearlyPaul(Enemy):

    def __init__(self, sprite_initializer : dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

        self.moving_time = 0
        self.pearl_dropping_time = 0
        self.hit_count = 0

        if not hasattr(PearlyPaul, 'poop_pearl'):
            PearlyPaul.poop_pearl = pyglet.media.load('audio/plop.mp3', streaming=False)

    def getResourceImages(self):
        return {
            'left': 'pearly_paul.png',
            'dead': 'lucinda.png'
        }

    def updateloop(self, dt):
        # if we’re busy being dead,
        if not self.is_dying:
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

        return super().updateloop(dt)

    def drop_pearl(self):
        if self.is_dying or self.death_done:
            return
        makeSprite(Pearl, self.current_chunk, (self.x_position, self.y_position + 22), starting_speed=(0, -12))
        self.pearl_dropping_time = random.randrange(50, 500)
        PearlyPaul.poop_pearl.play()

    def getting_hit(self):
        if self.is_dying or self.death_done:
            return

        self.hit_count += 1

        if self.hit_count >= 4:
            try:
                dead_dude = pyglet.media.load("audio/kenny_sounds/boss_beaten.mp3", streaming=False)
                dead_dude.play()
            except Exception:
                pass
            """switch to dead thing and then countdown. enemies.py handles
               probably John not like this. but I like the quirkyness that comes with dead things becoming other things. 
                we can like eat them if they are like sushi or something.""" 
            self.start_death(delay_frames=15, dead_key='dead')

    def on_pokey(self):
        self.getting_hit()

    def on_finish_death(self):
        # open the gates, clean the mess
        try:
            makeSprite(Door, self.current_chunk, starting_position=(1000, 0), group='BACK', target_map='map.dill', player_position=(1350, 320))
            makeSprite(Door, self.current_chunk, starting_position=(550, 0), group='BACK', target_map='map.dill', player_position=(550, 32))
            makeSprite(Door, self.current_chunk, starting_position=(770, 0), group='BACK', target_map='map.dill', player_position=(670, 3456))
        except Exception:
            pass
        try:
            for sprite_obj in LifeCycleManager.ALL_SETS['PER_MAP'].objects:
                if type(sprite_obj).__name__ == 'Pearl':
                    sprite_obj.destroy()
        except Exception:
            pass


# Crazy doll turned pro murder giver. Scary and efficient. deficient in kindness. 
class MrOmen(Enemy):

    MAX_HP = 8  # crank for spicy boss vibes

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.hp = MrOmen.MAX_HP
        self.timer = 0
        self.direction = 'right'
        if not hasattr(MrOmen, 'hit_snd'):
            try:
                MrOmen.hit_snd = pyglet.media.load('audio/glurk.wav', streaming=False)
            except Exception:
                MrOmen.hit_snd = None

    def getResourceImages(self):
        return {
            'right': {'file': 'bosses/mr_omen.png'},
            'left':  {'file': 'bosses/mr_omen.png', 'flip_x': True},
            'dead':  'sushiroll.png'
        }

    def hasGravity(self):
        return True

    def updateloop(self, dt):
        if not self.is_dying:
            self.timer += 1
            if self.timer % 120 == 0:
                self.x_speed = Decimal(8 if self.direction == 'right' else -8)
            if self.timer % 140 == 0:
                self.x_speed = Decimal(0)
                self.direction = 'left' if self.direction == 'right' else 'right'
        return super().updateloop(dt)

    def getting_hit(self):
        if self.is_dying or self.death_done:
            return
        self.hp -= 1
        if getattr(MrOmen, 'hit_snd', None):
            MrOmen.hit_snd.play()
        if self.hp <= 0:
            self.start_death(delay_frames=15, dead_key='dead')

    def on_pokey(self):
        self.getting_hit()

    def on_finish_death(self):
        # leave a door where the omen fell, poetic
        try:
            makeSprite(
                Door,
                self.current_chunk,
                starting_position=(int(self.x_position), int(self.y_position)),
                group='BACK',
                target_map='map.dill',
                player_position=(300, 200)
            )
        except Exception:
            pass

