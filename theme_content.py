"""Theme-specific props and bosses with custom procedural art."""

from decimal import Decimal

from enemies import Enemy
from physics import PhysicsSprite
from procedural_art import make_character_art


class ThemedBoss(Enemy):
    art_key = "lucinda"
    MAX_HP = 6

    def __init__(self, sprite_initializer, starting_chunk):
        self.hp = self.MAX_HP
        super().__init__(sprite_initializer, starting_chunk)
        self.CHASE_SPEED = Decimal("2.8")

    def getResourceImages(self):
        return {"0": make_character_art(self.art_key, 40, 40), "dead": make_character_art(self.art_key, 40, 40)}

    def getting_hit(self):
        if self.is_dying or self.death_done:
            return
        from gameplay import BloodSpurt
        BloodSpurt(self.x_position + 18, self.y_position + 18)
        self.hp -= 1
        if self.hp <= 0:
            self.start_death(delay_frames=18, dead_key="dead")

    def on_pokey(self):
        self.getting_hit()


class LucindaBoss(ThemedBoss):
    art_key = "lucinda"
    MAX_HP = 7


class JackieFlanBoss(ThemedBoss):
    art_key = "jackie_flan"
    MAX_HP = 8


class LevodBurtimBoss(ThemedBoss):
    art_key = "levod_burtim"
    MAX_HP = 10
    CHASE_DISTANCE = Decimal("480")


class PippiBoss(ThemedBoss):
    art_key = "pippi"
    MAX_HP = 6


class VesuviusBoss(ThemedBoss):
    art_key = "vesuvius"
    MAX_HP = 9


class VanProp(PhysicsSprite):
    def getResourceImages(self):
        return {0: make_character_art("van", 48, 32)}

    def hasGravity(self):
        return False
