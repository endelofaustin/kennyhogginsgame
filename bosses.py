import random
from decimal import Decimal

import pyglet

from enemies import Enemy
from gamepieces import Door
from lifecycle import LifeCycleManager
from sprite import makeSprite


# Shiny and adorable little pearls
class Pearl(Enemy):
    MAX_HP = 1
    CHASE_DISTANCE = Decimal(0)
    LUNGE_DISTANCE = Decimal(0)

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

    def getResourceImages(self):
        return {
            "pearl_left": {"file": "pearled_out.png", "rows": 3, "columns": 2, "duration": 1 / 10, "loop": True},
            "pearl_right": {"file": "pearled_out.png", "rows": 3, "columns": 2, "duration": 1 / 10, "loop": True},
            "dead": "sushiroll.png",
        }

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if collided_object and type(collided_object).__name__ == "Player":
            collided_object.hit()
            return
        super().on_PhysicsSprite_collided(collided_object, collided_chunk, chunk_x, chunk_y)


# A crazy coffee shop owner turned professional pearl producer
class PearlyPaul(Enemy):
    MAX_HP = 4
    DEATH_DELAY = 15
    LUNGE_DISTANCE = Decimal("150")
    LUNGE_SPEED = Decimal("6.0")

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.moving_time = 0
        self.pearl_dropping_time = 0

        if not hasattr(PearlyPaul, "poop_pearl"):
            PearlyPaul.poop_pearl = pyglet.resource.media("plop.wav", streaming=False)
        if not hasattr(PearlyPaul, "dead_dude"):
            PearlyPaul.dead_dude = pyglet.resource.media("kenny_sounds/boss_beaten.wav", streaming=False)

    def getResourceImages(self):
        return {"left": "pearly_paul.png", "dead": "lucinda.png"}

    def updateloop(self, dt):
        if not self.is_dying:
            if self.pearl_dropping_time <= 0:
                self.drop_pearl()
            else:
                self.pearl_dropping_time -= 1
            self.moving_time += 1
        return super().updateloop(dt)

    def drop_pearl(self):
        if self.is_dying or self.death_done:
            return
        makeSprite(Pearl, self.current_chunk, (self.x_position, self.y_position + 22), starting_speed=(0, -12))
        self.pearl_dropping_time = random.randrange(50, 500)
        PearlyPaul.poop_pearl.play()

    def _play_death_sound_if_needed(self, hp_before):
        if hp_before > 0 and self.hp <= 0:
            PearlyPaul.dead_dude.play()

    def getting_hit(self):
        hp_before = self.hp
        self.take_damage(self.PROJECTILE_DAMAGE)
        self._play_death_sound_if_needed(hp_before)

    def on_pokey(self):
        hp_before = self.hp
        self.take_damage(self.MELEE_DAMAGE)
        self._play_death_sound_if_needed(hp_before)

    def on_finish_death(self):
        # Open the gates, clean the mess.
        makeSprite(Door, self.current_chunk, starting_position=(1000, 0), group="BACK", target_map="map.dill", player_position=(1350, 320))
        makeSprite(Door, self.current_chunk, starting_position=(550, 0), group="BACK", target_map="map.dill", player_position=(550, 32))
        makeSprite(Door, self.current_chunk, starting_position=(770, 0), group="BACK", target_map="map.dill", player_position=(670, 3456))
        for sprite_obj in LifeCycleManager.ALL_SETS["PER_MAP"].objects:
            if type(sprite_obj).__name__ == "Pearl":
                sprite_obj.destroy()


# Crazy doll turned pro murder giver. Scary and efficient. deficient in kindness.
class MrOmen(Enemy):
    MAX_HP = 8
    DEATH_DELAY = 15
    LUNGE_DISTANCE = Decimal("165")
    LUNGE_SPEED = Decimal("6.6")

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.timer = 0
        self.direction = "right"
        if not hasattr(MrOmen, "hit_snd"):
            MrOmen.hit_snd = pyglet.resource.media("glurk.wav", streaming=False)

    def getResourceImages(self):
        return {
            "right": {"file": "bosses/mr_omen.png"},
            "left": {"file": "bosses/mr_omen.png", "flip_x": True},
            "dead": "sushiroll.png",
        }

    def hasGravity(self):
        return True

    def updateloop(self, dt):
        if not self.is_dying:
            self.timer += 1
            if self.timer % 140 == 0:
                self.direction = "left" if self.direction == "right" else "right"
                self.patrol_direction = Decimal(-1) if self.direction == "left" else Decimal(1)
        return super().updateloop(dt)

    def getting_hit(self):
        self.take_damage(self.PROJECTILE_DAMAGE)

    def on_pokey(self):
        self.take_damage(self.MELEE_DAMAGE)

    def on_finish_death(self):
        # Leave a door where the omen fell, poetic.
        makeSprite(
            Door,
            self.current_chunk,
            starting_position=(int(self.x_position), int(self.y_position)),
            group="BACK",
            target_map="map.dill",
            player_position=(300, 200),
        )
