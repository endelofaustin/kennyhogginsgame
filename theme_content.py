"""Theme-specific props, bosses, and background art for dill maps."""

from decimal import Decimal

import pyglet

from enemies import Enemy
from engineglobals import EngineGlobals
from gamepieces import Door
from lifecycle import GameObject
from physics import PhysicsSprite
from sprite import makeSprite


THEME_COLORS = {
    "farm": ((106, 170, 87), (235, 218, 147), (121, 72, 47)),
    "river": ((87, 151, 191), (44, 122, 174), (82, 91, 73)),
    "dojo": ((184, 73, 62), (239, 225, 188), (68, 39, 35)),
    "space": ((19, 18, 46), (76, 84, 140), (210, 92, 205)),
    "pompeii": ((199, 105, 54), (230, 181, 105), (91, 61, 55)),
}


class ThemeBackdrop(GameObject):
    """Custom in-engine art for each themed dill map."""

    def __init__(self, theme):
        self.theme = theme
        self.shapes = []
        sky, mid, dark = THEME_COLORS[theme]
        batch = EngineGlobals.main_batch
        group = EngineGlobals.bg_group
        self.shapes.append(pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, EngineGlobals.height, color=sky, batch=batch, group=group))
        self.shapes.append(pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, 120, color=mid, batch=batch, group=group))

        if theme == "farm":
            for x in range(30, EngineGlobals.width, 140):
                self.shapes.append(pyglet.shapes.Rectangle(x, 120, 72, 72, color=dark, batch=batch, group=group))
                self.shapes.append(pyglet.shapes.Triangle(x - 8, 192, x + 36, 232, x + 80, 192, color=(124, 49, 38), batch=batch, group=group))
        elif theme == "river":
            self.shapes.append(pyglet.shapes.Rectangle(0, 95, EngineGlobals.width, 80, color=(44, 122, 174), batch=batch, group=group))
            self.shapes.append(pyglet.shapes.Rectangle(0, 80, EngineGlobals.width, 18, color=(213, 195, 141), batch=batch, group=group))
        elif theme == "dojo":
            for x in range(0, EngineGlobals.width, 80):
                self.shapes.append(pyglet.shapes.Line(x, 0, x, EngineGlobals.height, width=2, color=dark, batch=batch, group=group))
            self.shapes.append(pyglet.shapes.Rectangle(250, 420, 300, 70, color=(245, 237, 214), batch=batch, group=group))
        elif theme == "space":
            for i in range(55):
                x = (i * 137) % EngineGlobals.width
                y = (i * 83) % EngineGlobals.height
                self.shapes.append(pyglet.shapes.Circle(x, y, 1 + i % 3, color=(245, 245, 225), batch=batch, group=group))
            self.shapes.append(pyglet.shapes.Circle(660, 440, 75, color=(125, 77, 180), batch=batch, group=group))
        elif theme == "pompeii":
            self.shapes.append(pyglet.shapes.Triangle(500, 120, 650, 390, 800, 120, color=dark, batch=batch, group=group))
            self.shapes.append(pyglet.shapes.Triangle(610, 300, 650, 390, 690, 300, color=(242, 82, 42), batch=batch, group=group))
            self.shapes.append(pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, 55, color=(238, 81, 37), batch=batch, group=group))
        super().__init__(lifecycle_manager="PER_MAP")

    def updateloop(self, dt):
        pass

    def on_finalDeletion(self):
        for shape in self.shapes:
            shape.delete()
        self.shapes.clear()


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
        BloodSpurt(self.x_position + 18, self.y_position + 18)
        self.hp -= 1
        if self.hp <= 0:
            self.start_death(delay_frames=18, dead_key="dead")

    def on_pokey(self):
        self.getting_hit()

    def on_finish_death(self):
        # Existing game architecture: boss defeat drops a normal Door sprite.
        makeSprite(
            Door,
            self.current_chunk,
            (int(self.x_position), int(self.y_position)),
            group="BACK",
            target_map="map.dill",
            player_position=(300, 200),
        )


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
