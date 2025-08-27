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


class DeathThatBoss(Enemy):
    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.is_dying = False
        self.death_done = False
        self.death_timer = -1

    def start_death(self, delay_frames=15, dead_key='dead'):
        if self.is_dying or self.death_done:
            return
        self.is_dying = True
        try:
            self.sprite.image = self.resource_images[dead_key]
        except Exception:
            pass
        self.death_timer = delay_frames

    def finish_death(self):
        if self.death_done:
            return
        self.death_done = True

        # allow subclass to spawn doors, cleanup, etc.
        try:
            self.on_finish_death()
        except Exception:
            pass

        # IMPORTANT:
        # Do NOT delete the sprite here. Let the engine lifecycle handle that.
        # Just mark for removal via die_hard()/destroy().
        try:
            self.die_hard()   # triggers lifecycle -> on_finalDeletion -> sprite.delete()
        except Exception:
            try:
                self.destroy()
            except Exception:
                pass

    def updateloop(self, dt):
        # While dying or after we've finished death, do not call parent update
        if self.is_dying or self.death_done:
            self.x_speed = Decimal(0)
            self.y_speed = Decimal(0)

            # run death countdown only while in dying state
            if self.is_dying and self.death_timer >= 0:
                self.death_timer -= 1
                if self.death_timer <= 0 and not self.death_done:
                    self.finish_death()

            return  # <-- critical: don't fall through to PhysicsSprite.updateloop
        return super().updateloop(dt)

    def on_finish_death(self):
        pass

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if self.is_dying or self.death_done:
            return
        return super().on_PhysicsSprite_collided(collided_object, collided_chunk, chunk_x, chunk_y)


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


class PearlyPaul(DeathThatBoss):

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
            self.start_death(delay_frames=15, dead_key='dead')

    def on_pokey(self):
        self.getting_hit()

    def on_finish_death(self):
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


class MrOmen(DeathThatBoss):

    MAX_HP = 8

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

