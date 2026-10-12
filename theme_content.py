"""Theme-specific props, bosses, enemies, and presentation for dill maps."""

import math
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
        self.shapes.append(
            pyglet.shapes.Rectangle(
                0,
                0,
                EngineGlobals.width,
                EngineGlobals.height,
                color=sky,
                batch=batch,
                group=group,
            )
        )
        self.shapes.append(
            pyglet.shapes.Rectangle(
                0,
                0,
                EngineGlobals.width,
                120,
                color=mid,
                batch=batch,
                group=group,
            )
        )

        if theme == "farm":
            for x in range(30, EngineGlobals.width, 140):
                self.shapes.append(
                    pyglet.shapes.Rectangle(x, 120, 72, 72, color=dark, batch=batch, group=group)
                )
                self.shapes.append(
                    pyglet.shapes.Triangle(
                        x - 8,
                        192,
                        x + 36,
                        232,
                        x + 80,
                        192,
                        color=(124, 49, 38),
                        batch=batch,
                        group=group,
                    )
                )
        elif theme == "river":
            self.shapes.append(
                pyglet.shapes.Rectangle(
                    0,
                    95,
                    EngineGlobals.width,
                    80,
                    color=(44, 122, 174),
                    batch=batch,
                    group=group,
                )
            )
            self.shapes.append(
                pyglet.shapes.Rectangle(
                    0,
                    80,
                    EngineGlobals.width,
                    18,
                    color=(213, 195, 141),
                    batch=batch,
                    group=group,
                )
            )
        elif theme == "dojo":
            for x in range(0, EngineGlobals.width, 80):
                self.shapes.append(
                    pyglet.shapes.Line(
                        x,
                        0,
                        x,
                        EngineGlobals.height,
                        width=2,
                        color=dark,
                        batch=batch,
                        group=group,
                    )
                )
            self.shapes.append(
                pyglet.shapes.Rectangle(
                    250,
                    420,
                    300,
                    70,
                    color=(245, 237, 214),
                    batch=batch,
                    group=group,
                )
            )
        elif theme == "space":
            for i in range(55):
                x = (i * 137) % EngineGlobals.width
                y = (i * 83) % EngineGlobals.height
                self.shapes.append(
                    pyglet.shapes.Circle(
                        x,
                        y,
                        1 + i % 3,
                        color=(245, 245, 225),
                        batch=batch,
                        group=group,
                    )
                )
            self.shapes.append(
                pyglet.shapes.Circle(
                    660,
                    440,
                    75,
                    color=(125, 77, 180),
                    batch=batch,
                    group=group,
                )
            )
        elif theme == "pompeii":
            # Vesuvius dominates the skyline. Layered slopes and a lava vent make
            # the level read as Pompeii immediately instead of a generic orange map.
            self.shapes.append(
                pyglet.shapes.Triangle(
                    390,
                    118,
                    650,
                    430,
                    820,
                    118,
                    color=(74, 57, 54),
                    batch=batch,
                    group=group,
                )
            )
            self.shapes.append(
                pyglet.shapes.Triangle(
                    525,
                    118,
                    650,
                    385,
                    755,
                    118,
                    color=(101, 65, 52),
                    batch=batch,
                    group=group,
                )
            )
            self.shapes.append(
                pyglet.shapes.Triangle(
                    618,
                    330,
                    650,
                    430,
                    687,
                    330,
                    color=(239, 77, 35),
                    batch=batch,
                    group=group,
                )
            )
            self.shapes.append(
                pyglet.shapes.Rectangle(
                    0,
                    0,
                    EngineGlobals.width,
                    58,
                    color=(220, 65, 28),
                    batch=batch,
                    group=group,
                )
            )
            self.shapes.append(
                pyglet.shapes.Rectangle(
                    0,
                    58,
                    EngineGlobals.width,
                    16,
                    color=(245, 125, 43),
                    batch=batch,
                    group=group,
                )
            )

            # Ruined Roman skyline: broken walls, columns and lintels.
            for x, height in ((35, 105), (150, 86), (292, 126), (735, 94)):
                self.shapes.append(
                    pyglet.shapes.Rectangle(
                        x,
                        74,
                        78,
                        height,
                        color=(124, 86, 64),
                        batch=batch,
                        group=group,
                    )
                )
                self.shapes.append(
                    pyglet.shapes.Rectangle(
                        x + 8,
                        74,
                        12,
                        height + 30,
                        color=(174, 137, 94),
                        batch=batch,
                        group=group,
                    )
                )
                self.shapes.append(
                    pyglet.shapes.Rectangle(
                        x + 54,
                        74,
                        12,
                        max(42, height - 12),
                        color=(174, 137, 94),
                        batch=batch,
                        group=group,
                    )
                )
            for x in (18, 274, 706):
                self.shapes.append(
                    pyglet.shapes.Rectangle(
                        x,
                        179,
                        112,
                        13,
                        color=(101, 71, 57),
                        batch=batch,
                        group=group,
                    )
                )

        super().__init__(lifecycle_manager="PER_MAP")

    def updateloop(self, dt):
        pass

    def on_finalDeletion(self):
        for shape in self.shapes:
            shape.delete()
        self.shapes.clear()


class PompeiiGrunt(Enemy):
    """Early Pompeii enemy: readable, forgiving, and useful for teaching combat."""

    MAX_HP = 2
    PATROL_SPEED = Decimal("1.1")
    CHASE_SPEED = Decimal("2.0")
    CHASE_DISTANCE = Decimal("245")
    LUNGE_DISTANCE = Decimal("90")
    LUNGE_SPEED = Decimal("4.6")
    ATTACK_COOLDOWN = 115


class PompeiiRunner(Enemy):
    """Fast ash-panicked enemy used after the player has learned the basics."""

    MAX_HP = 2
    PATROL_SPEED = Decimal("2.0")
    CHASE_SPEED = Decimal("3.3")
    CHASE_DISTANCE = Decimal("360")
    LUNGE_DISTANCE = Decimal("130")
    LUNGE_SPEED = Decimal("6.5")
    LUNGE_WINDUP = 12
    ATTACK_COOLDOWN = 80


class PompeiiBrute(Enemy):
    """Slow late-level enemy that forces the player to commit to several hits."""

    MAX_HP = 5
    PATROL_SPEED = Decimal("0.9")
    CHASE_SPEED = Decimal("1.8")
    CHASE_DISTANCE = Decimal("300")
    LUNGE_DISTANCE = Decimal("110")
    LUNGE_SPEED = Decimal("4.8")
    HIT_STUN_FRAMES = 7
    ATTACK_COOLDOWN = 105


class PompeiiDirector(GameObject):
    """Paces Vesuvius as five escalating sections and controls the lava chase."""

    STAGES = (
        (Decimal("0.00"), "I  CITY OUTSKIRTS", "Learn the rhythm. The lava starts slow.", Decimal("0.82")),
        (Decimal("0.23"), "II  VIA DELL'ABBONDANZA", "Grab the scythe. Break through the collapsed street.", Decimal("1.02")),
        (Decimal("0.46"), "III  THE FORUM", "Enemy groups get faster. Use the high route.", Decimal("1.23")),
        (Decimal("0.68"), "IV  ASH RUN", "The lava is gaining. Keep moving.", Decimal("1.48")),
        (Decimal("0.82"), "V  VESUVIUS", "Lava chase cleared. Defeat Vesuvius.", Decimal("0")),
    )

    def __init__(self, chunk):
        self.chunk = chunk
        self.stage_index = -1
        self.pulse = 0.0
        self.shapes = []
        self.ash = []
        batch = EngineGlobals.main_batch
        front = EngineGlobals.editor_group_front
        mid = EngineGlobals.editor_group_mid

        self.stage_label = pyglet.text.Label(
            "",
            x=EngineGlobals.width // 2,
            y=EngineGlobals.height - 38,
            anchor_x="center",
            font_size=17,
            weight=pyglet.text.Weight.BOLD,
            color=(255, 238, 211, 255),
            batch=batch,
            group=front,
        )
        self.objective_label = pyglet.text.Label(
            "",
            x=EngineGlobals.width // 2,
            y=EngineGlobals.height - 62,
            anchor_x="center",
            font_size=11,
            color=(255, 222, 185, 255),
            batch=batch,
            group=front,
        )

        self.lava_edge = pyglet.shapes.Rectangle(
            0,
            0,
            22,
            EngineGlobals.height,
            color=(231, 65, 24),
            batch=batch,
            group=mid,
        )
        self.lava_core = pyglet.shapes.Rectangle(
            0,
            0,
            8,
            EngineGlobals.height,
            color=(255, 166, 49),
            batch=batch,
            group=mid,
        )
        self.shapes.extend((self.lava_edge, self.lava_core))

        for i in range(26):
            ash = pyglet.shapes.Circle(
                (i * 97) % EngineGlobals.width,
                80 + (i * 61) % max(100, EngineGlobals.height - 100),
                1 + i % 3,
                color=(70, 62, 58),
                batch=batch,
                group=mid,
            )
            self.ash.append({"shape": ash, "vy": 0.7 + (i % 5) * 0.18, "vx": -0.15 - (i % 3) * 0.08})

        super().__init__(lifecycle_manager="PER_MAP")

    def _progress(self):
        player = getattr(EngineGlobals, "kenny", None)
        if player is None:
            return Decimal(0)
        width = Decimal(max(1, self.chunk.width * EngineGlobals.tile_size))
        return max(
            Decimal(0),
            min(Decimal(1), (Decimal(player.x_position) - Decimal(self.chunk.coalesced_x)) / width),
        )

    def _stage_for_progress(self, progress):
        index = 0
        for candidate, stage in enumerate(self.STAGES):
            if progress >= stage[0]:
                index = candidate
            else:
                break
        return index

    def updateloop(self, dt):
        progress = self._progress()
        stage_index = self._stage_for_progress(progress)
        stage = self.STAGES[stage_index]

        if stage_index != self.stage_index:
            self.stage_index = stage_index
            self.stage_label.text = stage[1]
            self.objective_label.text = stage[2]

        autoscroller = getattr(EngineGlobals, "autoscroller", None)
        if autoscroller is not None:
            if stage[3] <= 0:
                autoscroller.stop()
            else:
                autoscroller.speed = stage[3]

        self.pulse += 0.08 * float(dt)
        boss_stage = stage_index == len(self.STAGES) - 1
        self.lava_edge.visible = not boss_stage
        self.lava_core.visible = not boss_stage
        if not boss_stage:
            self.lava_edge.width = 20 + 7 * (0.5 + 0.5 * math.sin(self.pulse))

        for part in self.ash:
            shape = part["shape"]
            shape.x += part["vx"] * float(dt)
            shape.y -= part["vy"] * float(dt)
            if shape.y < 65:
                shape.y = EngineGlobals.height - 20
                shape.x = (shape.x + 173) % EngineGlobals.width
            if shape.x < 0:
                shape.x += EngineGlobals.width

    def on_finalDeletion(self):
        self.stage_label.delete()
        self.objective_label.delete()
        for shape in self.shapes:
            shape.delete()
        self.shapes.clear()
        for part in self.ash:
            part["shape"].delete()
        self.ash.clear()


class ThemedBoss(Enemy):
    art_file = "generated/lucinda.png"
    MAX_HP = 6
    DEATH_DELAY = 18
    LUNGE_DISTANCE = Decimal("145")
    LUNGE_SPEED = Decimal("6.2")
    ATTACK_COOLDOWN = 115

    def __init__(self, sprite_initializer, starting_chunk):
        super().__init__(sprite_initializer, starting_chunk)
        self.CHASE_SPEED = Decimal("2.8")

    def getResourceImages(self):
        return {"0": self.art_file, "dead": self.art_file}

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
    MAX_HP = 12
    CHASE_DISTANCE = Decimal("430")
    LUNGE_DISTANCE = Decimal("175")
    LUNGE_SPEED = Decimal("6.8")
    ATTACK_COOLDOWN = 90


class VanProp(PhysicsSprite):
    def getResourceImages(self):
        return {0: "generated/van.png"}

    def hasGravity(self):
        return False
