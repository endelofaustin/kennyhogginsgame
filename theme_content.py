"""Theme-specific props and bosses with custom project art."""

from decimal import Decimal

from enemies import Enemy
from physics import PhysicsSprite


class ThemedBoss(Enemy):
    art_file = "generated/lucinda.png"
    MAX_HP = 6

    def __init__(self, sprite_initializer, starting_chunk):
        self.hp = self.MAX_HP
        super().__init__(sprite_initializer, starting_chunk)
        self.CHASE_SPEED = Decimal("2.8")

    def getResourceImages(self):
        return {"0": self.art_file, "dead": self.art_file}

    def getting_hit(self):
        if self.is_dying or self.death_done:
            return
        from gameplay import BloodSpurt
        from events import BUS
        BloodSpurt(self.x_position + 18, self.y_position + 18)
        self.hp -= 1
        BUS.publish("boss_hit", boss=self, hp=self.hp)
        if self.hp <= 0:
            self.start_death(delay_frames=18, dead_key="dead")

    def on_pokey(self):
        self.getting_hit()

    def on_finish_death(self):
        from events import BUS
        BUS.publish("boss_defeated", boss=self)


class LucindaBoss(ThemedBoss):
    art_file = "generated/lucinda.png"
    MAX_HP = 7


class JackieFlanBoss(ThemedBoss):
    art_file = "generated/jackie_flan.png"
    MAX_HP = 8


class LevodBurtimBoss(ThemedBoss):
    art_file = "generated/levod_burtim.png"
    MAX_HP = 10
    CHASE_DISTANCE = Decimal("480")


class PippiBoss(ThemedBoss):
    art_file = "generated/pippi.png"
    MAX_HP = 6


class VesuviusBoss(ThemedBoss):
    art_file = "generated/vesuvius.png"
    MAX_HP = 9


class VanProp(PhysicsSprite):
    def getResourceImages(self):
        return {0: "generated/van.png"}

    def hasGravity(self):
        return False
