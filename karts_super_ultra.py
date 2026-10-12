"""Super Ultra Kenny Kart visual/content upgrade.

This module upgrades only the top-down KartsMode stack.  It deliberately does
not import or patch any mode7/N64 racing module.
"""

import math
import random

import pyglet

import karts_mode as km
import karts_expansion as kx
import karts_stats as ks
from engineglobals import EngineGlobals


SUPER_ULTRA_CHARACTERS = (
    ("McSwanson", (198, 112, 82), "mcswanson-1.png"),
    ("Frankenfire Kitty", (116, 218, 146), "frankenfirekitty-1.png.png"),
    ("Llama Solo", (236, 213, 171), "llama_solo_right.png"),
    ("Menacing Flower", (221, 94, 162), "menancingflower.png"),
    ("Sushi Roll", (239, 181, 153), "sushiroll.png"),
    ("Spikey", (119, 172, 226), "spikey.png"),
)

SUPER_ULTRA_STATS = {
    "McSwanson": {
        "speed": 9, "accel": 7, "turn": 7, "weight": 8, "grip": 7, "boost": 8,
        "trait": "MIDNIGHT MUSCLE — stable high-speed slides",
    },
    "Frankenfire Kitty": {
        "speed": 8, "accel": 9, "turn": 9, "weight": 4, "grip": 8, "boost": 9,
        "trait": "FIRE CAT — fast recovery and hot boosts",
    },
    "Llama Solo": {
        "speed": 7, "accel": 8, "turn": 10, "weight": 5, "grip": 10, "boost": 7,
        "trait": "CANYON CARVER — maximum corner confidence",
    },
    "Menacing Flower": {
        "speed": 8, "accel": 10, "turn": 8, "weight": 3, "grip": 8, "boost": 9,
        "trait": "PETAL PANIC — lightning launch and recovery",
    },
    "Sushi Roll": {
        "speed": 9, "accel": 8, "turn": 9, "weight": 5, "grip": 9, "boost": 8,
        "trait": "ROLL MASTER — balanced technical specialist",
    },
    "Spikey": {
        "speed": 10, "accel": 6, "turn": 7, "weight": 9, "grip": 7, "boost": 9,
        "trait": "STEEL ROCKET — brutal straight-line speed",
    },
}


def _new_tracks():
    t = kx._track
    return (
        t(
            "McSwanson Midnight Run",
            ((118, 150), (270, 86), (505, 82), (688, 142), (718, 300),
             (650, 456), (450, 520), (235, 500), (82, 395), (70, 245)),
            ((380, 83, 0), (700, 230, 90), (548, 492, 155)),
            grass=(28, 36, 58), road=(52, 58, 72), edge=(111, 166, 218),
            hazards=(("oil", 625, 118, 27), ("oil", 105, 405, 25)),
            ramps=((706, 304),), nitro=((205, 105), (365, 515)),
            tagline="Neon midnight speed, wet-looking asphalt, brutal sweepers.",
        ),
        t(
            "Llama Launch Canyon",
            ((115, 142), (290, 80), (570, 92), (706, 205), (688, 392),
             (535, 518), (300, 520), (110, 438), (70, 280)),
            ((420, 86, 0), (697, 315, 90), (420, 520, 180)),
            road_width=64, grass=(146, 104, 67), road=(83, 75, 72), edge=(229, 183, 110),
            hazards=(("mud", 575, 100, 37),), ramps=((705, 205), (295, 516)),
            nitro=((95, 355),), tagline="Canyon launch ramps and huge dusty landings.",
        ),
        t(
            "Menacing Flower Maze",
            ((105, 140), (270, 88), (500, 92), (655, 145), (570, 245),
             (705, 335), (620, 470), (405, 525), (205, 488), (78, 370), (88, 230)),
            ((350, 90, 0), (675, 400, 112)), road_width=59,
            grass=(68, 121, 72), road=(67, 75, 70), edge=(220, 115, 178),
            hazards=(("mud", 560, 242, 31), ("oil", 685, 336, 23)),
            ramps=((618, 468),), nitro=((150, 112), (300, 510)),
            tagline="Garden maze switchbacks with poisonous shortcut traps.",
        ),
        t(
            "Sushi Roll Circuit",
            ((125, 135), (330, 78), (590, 98), (713, 220), (665, 430),
             (490, 522), (255, 502), (90, 410), (73, 250)),
            ((455, 86, 0), (690, 330, 92), (370, 515, 180)),
            grass=(57, 99, 112), road=(68, 73, 82), edge=(236, 194, 184),
            hazards=(("oil", 610, 108, 25), ("ketchup", 115, 430, 35)),
            ramps=((520, 510),), nitro=((100, 325), (628, 450)),
            tagline="Clean racing lines, glowing harbor turns, one sticky surprise.",
        ),
        t(
            "Spikey Steelworks",
            ((120, 145), (285, 82), (535, 82), (695, 135), (718, 300),
             (630, 472), (420, 522), (205, 490), (78, 365), (78, 220)),
            ((410, 83, 0), (704, 230, 90), (520, 505, 165)), road_width=61,
            grass=(55, 61, 68), road=(58, 62, 68), edge=(157, 183, 201),
            hazards=(("oil", 550, 86, 24), ("lava", 110, 390, 29)),
            ramps=((700, 302),), nitro=((250, 95), (300, 510)),
            tagline="Cold steel, furnace glow and an unforgiving factory loop.",
        ),
        t(
            "Nirvana Fruit Freeway",
            ((115, 150), (300, 88), (560, 94), (705, 180), (704, 360),
             (570, 492), (345, 520), (135, 465), (72, 315), (82, 215)),
            ((420, 92, 0), (686, 425, 120)), road_width=70,
            grass=(83, 137, 76), road=(78, 83, 78), edge=(238, 201, 98),
            hazards=(("mud", 585, 105, 34),), ramps=((705, 360),),
            nitro=((205, 112), (410, 510)),
            tagline="Bright freeway spectacle with giant fruit-powered nitro lanes.",
        ),
        t(
            "Scythe Storm Pass",
            ((120, 145), (310, 82), (575, 92), (708, 205), (665, 315),
             (715, 430), (520, 520), (280, 510), (95, 425), (72, 270)),
            ((440, 88, 0), (690, 375, 90)), road_width=58,
            grass=(47, 55, 78), road=(59, 63, 78), edge=(145, 142, 224),
            hazards=(("oil", 645, 315, 24), ("oil", 100, 420, 24)),
            ramps=((704, 205), (280, 510)), nitro=((160, 115),),
            tagline="Storm-lit mountain bends and two airborne scythe jumps.",
        ),
        t(
            "Band-Aid Backroads",
            ((130, 150), (285, 92), (515, 85), (682, 160), (705, 315),
             (615, 470), (385, 520), (175, 480), (76, 350), (88, 230)),
            ((390, 88, 0), (675, 405, 120)), road_width=63,
            grass=(156, 133, 99), road=(91, 80, 72), edge=(239, 218, 186),
            hazards=(("mud", 540, 92, 40), ("ketchup", 105, 390, 35)),
            ramps=((700, 315),), nitro=((225, 110), (300, 505)),
            tagline="Rough country roads, improvised ramps and zero dignity.",
        ),
        t(
            "Lighthouse Lightning Loop",
            ((110, 145), (275, 80), (530, 78), (700, 150), (718, 315),
             (650, 465), (440, 525), (220, 500), (78, 390), (72, 230)),
            ((390, 80, 0), (705, 240, 92), (550, 500, 160)), road_width=66,
            grass=(44, 91, 106), road=(64, 72, 78), edge=(211, 224, 216),
            hazards=(("oil", 590, 85, 24),), ramps=((650, 465),),
            nitro=((125, 160), (310, 515)),
            tagline="Coastal lightning, lighthouse glare and wet-night speed.",
        ),
        t(
            "Kenny Hyperdream Finale",
            ((115, 145), (300, 76), (565, 85), (708, 190), (680, 330),
             (714, 440), (520, 525), (300, 522), (105, 450), (68, 310), (82, 210)),
            ((430, 82, 0), (700, 270, 90), (610, 482, 145), (205, 500, 195)),
            road_width=68, grass=(58, 42, 94), road=(67, 60, 88), edge=(234, 117, 241),
            hazards=(("oil", 575, 92, 24), ("lava", 690, 435, 27), ("ketchup", 110, 450, 31)),
            ramps=((708, 190), (300, 520)), nitro=((95, 270), (500, 515)),
            tagline="The ad come alive: neon, jumps, hazards and maximum Super Ultra.",
        ),
    )


_ORIGINALS = {}
_INSTALLED = False


def _brighten(color, amount=34):
    return tuple(min(255, int(c) + amount) for c in color)


def _darken(color, amount=34):
    return tuple(max(0, int(c) - amount) for c in color)


def _selected_track(self):
    return kx.TRACKS[self.selected_track % len(kx.TRACKS)]


def _su_init(self, *args, **kwargs):
    _ORIGINALS["__init__"](self, *args, **kwargs)
    self.mode_title.text = "SUPER ULTRA KENNY KART"
    self.mode_title.font_size = 29
    self.background.color = (7, 11, 25)
    self._su_rng = random.Random(7301966)
    self._su_particles = []
    self._su_selection_fx = []
    self._su_track_fx = []

    # Persistent space backdrop for Super Ultra's own menus. Race backgrounds
    # cover these shapes, so they never leak into the platformer or Mode 7.
    for i in range(55):
        star = pyglet.shapes.Circle(
            self._su_rng.randint(8, max(9, EngineGlobals.width - 8)),
            self._su_rng.randint(10, max(11, EngineGlobals.height - 10)),
            1 if i % 4 else 2,
            color=(125 + i % 80, 155 + i % 70, 205 + i % 45),
            batch=self.batch, group=self.bg_group,
        )
        star.opacity = 90 + (i * 17) % 150
        self._su_selection_fx.append(star)
    for x, y, radius, color in (
        (110, 430, 105, (29, 45, 98)),
        (680, 160, 120, (79, 28, 96)),
        (545, 500, 75, (24, 82, 104)),
    ):
        glow = pyglet.shapes.Circle(x, y, radius, color=color, batch=self.batch, group=self.bg_group)
        glow.opacity = 72
        self._su_selection_fx.append(glow)


def _selection_header(self, subtitle):
    self.mode_title.visible = True
    self.mode_title.text = "SUPER ULTRA KENNY KART"
    chrome = pyglet.text.Label(
        subtitle,
        x=EngineGlobals.width // 2, y=EngineGlobals.height - 98,
        anchor_x="center", font_size=13, weight=pyglet.text.Weight.BOLD,
        color=(176, 225, 255, 255), batch=self.batch, group=self.ui_group,
    )
    rule_l = pyglet.shapes.Rectangle(
        40, EngineGlobals.height - 111, 235, 2, color=(47, 148, 225),
        batch=self.batch, group=self.track_group,
    )
    rule_r = pyglet.shapes.Rectangle(
        EngineGlobals.width - 275, EngineGlobals.height - 111, 235, 2,
        color=(214, 74, 230), batch=self.batch, group=self.track_group,
    )
    self._selection_labels.append(chrome)
    self._selection_shapes.extend((rule_l, rule_r))


def _selection_footer(self):
    label = pyglet.text.Label(
        "ARROWS NAVIGATE   //   ENTER LOCKS IN   //   ESC BACK",
        x=EngineGlobals.width // 2, y=24, anchor_x="center",
        font_size=9, color=(143, 176, 205, 255),
        batch=self.batch, group=self.ui_group,
    )
    self._selection_labels.append(label)


def _build_character_select(self):
    self._clear_selection_ui()
    self._selection_header("DRIVER GRID // 13 RACERS // PS3-STYLE SUPER ULTRA EDITION")
    self._selection_footer()
    self._character_panels = []

    cols = 5
    x0, gap_x = 96, 151
    y_rows = (390, 270, 150)
    for index, (name, face_color) in enumerate(km.CHARACTERS):
        row, col = divmod(index, cols)
        x = x0 + col * gap_x
        y = y_rows[min(row, len(y_rows) - 1)]
        stats = ks.CHARACTER_STATS.get(name, ks.CHARACTER_STATS["Kenny"])

        glow = pyglet.shapes.Rectangle(
            x - 66, y - 48, 132, 100, color=(27, 58, 89),
            batch=self.batch, group=self.track_group,
        )
        glow.opacity = 170
        panel = pyglet.shapes.Rectangle(
            x - 62, y - 44, 124, 92, color=(15, 23, 39),
            batch=self.batch, group=self.track_group,
        )
        self._selection_shapes.extend((glow, panel))
        self._character_panels.append((glow, panel))

        art_file = kx.CHARACTER_ART.get(name)
        loaded = False
        if art_file:
            try:
                image = pyglet.resource.image(art_file)
                sprite = pyglet.sprite.Sprite(image, batch=self.batch, group=self.ui_group)
                sprite.scale = min(2.2, 46.0 / max(1.0, float(max(image.width, image.height))))
                sprite.x = x - sprite.width / 2
                sprite.y = y - 1 - sprite.height / 2
                self._selection_shapes.append(sprite)
                loaded = True
            except Exception:
                loaded = False
        if not loaded:
            head = pyglet.shapes.Circle(
                x, y + 4, 19, color=face_color, batch=self.batch, group=self.ui_group
            )
            eye1 = pyglet.shapes.Circle(
                x - 6, y + 9, 2, color=(21, 21, 24), batch=self.batch, group=self.ui_group
            )
            eye2 = pyglet.shapes.Circle(
                x + 6, y + 9, 2, color=(21, 21, 24), batch=self.batch, group=self.ui_group
            )
            self._selection_shapes.extend((head, eye1, eye2))

        name_label = pyglet.text.Label(
            name.upper(), x=x, y=y + 34, anchor_x="center",
            font_size=7 if len(name) > 14 else 8, weight=pyglet.text.Weight.BOLD,
            color=(243, 248, 255, 255), batch=self.batch, group=self.ui_group,
        )
        stat_label = pyglet.text.Label(
            "S{} A{} T{} B{}".format(
                stats["speed"], stats["accel"], stats["turn"], stats["boost"]
            ),
            x=x, y=y - 33, anchor_x="center", font_size=6,
            color=(145, 205, 240, 255), batch=self.batch, group=self.ui_group,
        )
        self._selection_labels.extend((name_label, stat_label))

    self._stat_detail_label = pyglet.text.Label(
        "", x=EngineGlobals.width // 2, y=67, anchor_x="center",
        font_size=10, weight=pyglet.text.Weight.BOLD,
        color=(255, 210, 111, 255), batch=self.batch, group=self.ui_group,
    )
    self._selection_labels.append(self._stat_detail_label)
    self._refresh_character_highlight()


def _refresh_character_highlight(self):
    for index, pair in enumerate(getattr(self, "_character_panels", [])):
        glow, panel = pair
        selected = index == self.selected_character
        glow.color = (60, 186, 245) if selected else (27, 58, 89)
        glow.opacity = 245 if selected else 150
        panel.color = (25, 39, 61) if selected else (15, 23, 39)
    if getattr(self, "_stat_detail_label", None) is not None and km.CHARACTERS:
        name = km.CHARACTERS[self.selected_character % len(km.CHARACTERS)][0]
        stats = ks.CHARACTER_STATS.get(name, ks.CHARACTER_STATS["Kenny"])
        self._stat_detail_label.text = "{} // {}".format(name.upper(), stats["trait"])


def _build_track_select(self):
    self._clear_selection_ui()
    self._selection_header(
        "CIRCUIT MATRIX // {} TRACKS // SELECT THE NEXT SPECTACLE".format(len(kx.TRACKS))
    )
    self._selection_footer()
    self._track_panels = []
    cols = 3
    xs = (145, 400, 655)
    y0, gap_y = 450, 45
    for index, track in enumerate(kx.TRACKS):
        row, col = divmod(index, cols)
        x, y = xs[col], y0 - row * gap_y
        glow = pyglet.shapes.Rectangle(
            x - 116, y - 16, 232, 34, color=(29, 49, 72),
            batch=self.batch, group=self.track_group,
        )
        panel = pyglet.shapes.Rectangle(
            x - 112, y - 13, 224, 28, color=(13, 21, 34),
            batch=self.batch, group=self.track_group,
        )
        self._selection_shapes.extend((glow, panel))
        self._track_panels.append((glow, panel))
        label = pyglet.text.Label(
            track["name"].upper(), x=x, y=y + 1, anchor_x="center", anchor_y="center",
            font_size=7 if len(track["name"]) > 23 else 8,
            weight=pyglet.text.Weight.BOLD, color=(229, 240, 250, 255),
            batch=self.batch, group=self.ui_group,
        )
        self._selection_labels.append(label)

    self._track_detail_label = pyglet.text.Label(
        "", x=EngineGlobals.width // 2, y=61, anchor_x="center",
        font_size=9, color=(255, 211, 118, 255),
        batch=self.batch, group=self.ui_group,
    )
    self._selection_labels.append(self._track_detail_label)
    self._refresh_track_highlight()


def _refresh_track_highlight(self):
    for index, pair in enumerate(getattr(self, "_track_panels", [])):
        glow, panel = pair
        selected = index == self.selected_track
        glow.color = (196, 66, 231) if selected else (29, 49, 72)
        glow.opacity = 240 if selected else 145
        panel.color = (38, 28, 58) if selected else (13, 21, 34)
    if getattr(self, "_track_detail_label", None) is not None and kx.TRACKS:
        track = _selected_track(self)
        self._track_detail_label.text = "{} // {}".format(
            track["name"].upper(), track.get("tagline", "")
        )


def _build_track(self):
    # Existing expansion/stats mechanics build the physical track first.
    _ORIGINALS["_build_track"](self)
    track = _selected_track(self)
    accent = _brighten(track["edge"], 18)
    deep = _darken(track["grass"], 38)

    # Screen-space cinematic edge shading, behind karts and HUD.
    top_bar = pyglet.shapes.Rectangle(
        0, EngineGlobals.height - 66, EngineGlobals.width, 66,
        color=deep, batch=self.batch, group=self.track_group,
    )
    top_bar.opacity = 105
    bottom_bar = pyglet.shapes.Rectangle(
        0, 0, EngineGlobals.width, 54,
        color=(8, 11, 18), batch=self.batch, group=self.track_group,
    )
    bottom_bar.opacity = 145
    self._race_shapes.extend((top_bar, bottom_bar))

    # Guard lights and glowing checkpoint beacons make every circuit read as a
    # high-budget night-race arena without changing collision geometry.
    self._su_track_fx = []
    for i, (x, y) in enumerate(self.CHECKPOINTS):
        ring = pyglet.shapes.Circle(
            x, y, 9 if i else 13, color=_darken(accent, 65),
            batch=self.batch, group=self.track_group,
        )
        ring.opacity = 150
        lamp = pyglet.shapes.Circle(
            x, y, 3 if i else 5, color=accent,
            batch=self.batch, group=self.track_group,
        )
        self._race_shapes.extend((ring, lamp))
        self._su_track_fx.append((ring, lamp, i * 0.47))

    # Giant corner landmarks: layered towers, floodlights and a moon/energy orb.
    landmarks = (
        (35, 85, 36, 150), (728, 72, 38, 174),
        (34, 420, 42, 136), (718, 410, 45, 155),
    )
    for idx, (x, y, width, height) in enumerate(landmarks):
        tower = pyglet.shapes.Rectangle(
            x, y, width, height, color=_darken(track["grass"], 24),
            batch=self.batch, group=self.track_group,
        )
        tower.opacity = 200
        glass = pyglet.shapes.Rectangle(
            x + 6, y + 18, max(6, width - 12), max(10, height - 38),
            color=_darken(accent, 35), batch=self.batch, group=self.track_group,
        )
        glass.opacity = 95
        beacon = pyglet.shapes.Circle(
            x + width / 2, y + height + 7, 7,
            color=accent if idx % 2 == 0 else (255, 172, 80),
            batch=self.batch, group=self.track_group,
        )
        self._race_shapes.extend((tower, glass, beacon))

    orb = pyglet.shapes.Circle(
        EngineGlobals.width - 88, EngineGlobals.height - 112, 34,
        color=_brighten(track["edge"], 28), batch=self.batch, group=self.track_group,
    )
    orb.opacity = 92
    core = pyglet.shapes.Circle(
        EngineGlobals.width - 88, EngineGlobals.height - 112, 20,
        color=_brighten(track["edge"], 62), batch=self.batch, group=self.track_group,
    )
    core.opacity = 130
    self._race_shapes.extend((orb, core))

    # HUD branding.
    brand = pyglet.text.Label(
        "SUPER ULTRA", x=EngineGlobals.width // 2, y=EngineGlobals.height - 51,
        anchor_x="center", font_size=8, weight=pyglet.text.Weight.BOLD,
        color=(180, 224, 255, 235), batch=self.batch, group=self.ui_group,
    )
    field = pyglet.text.Label(
        "12-RACER FIELD", x=EngineGlobals.width - 14, y=63,
        anchor_x="right", font_size=8, color=(205, 150, 255, 235),
        batch=self.batch, group=self.ui_group,
    )
    self._race_labels.extend((brand, field))
    if hasattr(self, "place_label"):
        self.place_label.text = "PLACE 1/12"


def _racer_color(racer):
    if not racer.ai:
        return racer.color
    palette = (
        (225, 76, 74), (71, 128, 232), (88, 183, 116), (235, 182, 62),
        (177, 91, 218), (64, 194, 210), (237, 119, 61), (218, 92, 154),
        (133, 151, 174), (94, 211, 165), (221, 215, 104),
    )
    return palette[racer.ai_index % len(palette)]


def _create_racer_visuals(self, racer):
    _ORIGINALS["_create_racer_visuals"](self, racer)

    # Hide the legacy flat/turd body but retain it so the existing cleanup and
    # character-art wrappers remain safe.
    for item in list(getattr(racer, "turd_shapes", [])) + list(getattr(racer, "wheels", [])):
        item.visible = False
    for attr in ("body", "nose", "head"):
        item = getattr(racer, attr, None)
        if item is not None:
            item.visible = False

    color = _racer_color(racer)
    bright = _brighten(color, 42)
    dark = _darken(color, 58)

    racer.su_shadow = pyglet.shapes.Circle(
        0, 0, 22, color=(5, 7, 10), batch=self.batch, group=self.kart_group,
    )
    racer.su_shadow.opacity = 120
    racer.su_underbody = pyglet.shapes.Rectangle(
        0, 0, 54, 30, color=dark, batch=self.batch, group=self.kart_group,
    )
    racer.su_underbody.anchor_position = (27, 15)
    racer.su_body = pyglet.shapes.Rectangle(
        0, 0, 48, 26, color=color, batch=self.batch, group=self.kart_group,
    )
    racer.su_body.anchor_position = (24, 13)
    racer.su_hood = pyglet.shapes.Rectangle(
        0, 0, 21, 20, color=bright, batch=self.batch, group=self.kart_group,
    )
    racer.su_hood.anchor_position = (10.5, 10)
    racer.su_cockpit = pyglet.shapes.Circle(
        0, 0, 11, color=(34, 51, 69), batch=self.batch, group=self.kart_group,
    )
    racer.su_gloss = pyglet.shapes.Rectangle(
        0, 0, 30, 3, color=(235, 246, 255), batch=self.batch, group=self.kart_group,
    )
    racer.su_gloss.anchor_position = (15, 1.5)
    racer.su_spoiler = pyglet.shapes.Rectangle(
        0, 0, 9, 38, color=dark, batch=self.batch, group=self.kart_group,
    )
    racer.su_spoiler.anchor_position = (4.5, 19)
    racer.su_wheels = [
        pyglet.shapes.Circle(0, 0, 6, color=(12, 14, 18), batch=self.batch, group=self.kart_group)
        for _ in range(4)
    ]
    racer.su_rims = [
        pyglet.shapes.Circle(0, 0, 2.7, color=(132, 151, 171), batch=self.batch, group=self.kart_group)
        for _ in range(4)
    ]
    racer.su_headlights = [
        pyglet.shapes.Circle(0, 0, 4, color=(183, 232, 255), batch=self.batch, group=self.kart_group),
        pyglet.shapes.Circle(0, 0, 4, color=(183, 232, 255), batch=self.batch, group=self.kart_group),
    ]
    racer.su_boost_glow = pyglet.shapes.Circle(
        0, 0, 8, color=(84, 208, 255), batch=self.batch, group=self.kart_group,
    )
    racer.su_boost_glow.opacity = 0

    racer.su_shapes = [
        racer.su_shadow, racer.su_underbody, racer.su_body, racer.su_hood,
        racer.su_cockpit, racer.su_gloss, racer.su_spoiler,
        *racer.su_wheels, *racer.su_rims, *racer.su_headlights, racer.su_boost_glow,
    ]


def _update_racer_visuals(self, racer):
    _ORIGINALS["_update_racer_visuals"](self, racer)

    if not hasattr(racer, "su_body"):
        return
    hop = 8.0 if racer.hop_timer > 0 else 0.0
    angle_deg = -math.degrees(racer.angle)
    perspective = 0.82 + 0.26 * (1.0 - racer.y / max(1.0, EngineGlobals.height))
    perspective = max(0.74, min(1.12, perspective))

    def pos(ox, oy):
        dx, dy = self._rotate_local(ox * perspective, oy * perspective, racer.angle)
        return racer.x + dx, racer.y + dy + hop

    racer.su_shadow.position = (racer.x + 3, racer.y - 4)
    racer.su_shadow.radius = 23 * perspective
    racer.su_shadow.opacity = 70 if hop else 125

    for shape, w, h, anchor in (
        (racer.su_underbody, 56, 32, (28, 16)),
        (racer.su_body, 48, 26, (24, 13)),
        (racer.su_hood, 22, 20, (11, 10)),
        (racer.su_gloss, 30, 3, (15, 1.5)),
        (racer.su_spoiler, 9, 38, (4.5, 19)),
    ):
        shape.width = w * perspective
        shape.height = h * perspective
        shape.anchor_position = (anchor[0] * perspective, anchor[1] * perspective)
        shape.rotation = angle_deg

    racer.su_underbody.position = pos(0, 0)
    racer.su_body.position = pos(0, 0)
    racer.su_hood.position = pos(18, 0)
    racer.su_gloss.position = pos(2, -6)
    racer.su_spoiler.position = pos(-22, 0)

    racer.su_cockpit.position = pos(-7, 0)
    racer.su_cockpit.radius = 10.5 * perspective

    wheel_offsets = ((-15, -17), (-15, 17), (15, -17), (15, 17))
    for wheel, rim, (ox, oy) in zip(racer.su_wheels, racer.su_rims, wheel_offsets):
        wheel.position = pos(ox, oy)
        wheel.radius = 6.4 * perspective
        rim.position = wheel.position
        rim.radius = 2.7 * perspective

    for lamp, oy in zip(racer.su_headlights, (-7, 7)):
        lamp.position = pos(25, oy)
        lamp.radius = 3.4 * perspective
        lamp.opacity = 215

    racer.su_boost_glow.position = pos(-30, 0)
    racer.su_boost_glow.radius = (7.0 + min(6.0, abs(racer.speed))) * perspective
    racer.su_boost_glow.opacity = 210 if racer.boost_timer > 0 else 0

    art = getattr(racer, "character_art", None)
    if art is not None:
        art.scale = min(2.15, 31.0 * perspective / max(1.0, float(max(art.image.width, art.image.height))))
        art.x = racer.su_cockpit.x - art.width / 2
        art.y = racer.su_cockpit.y - art.height / 2 + 2
        art.rotation = angle_deg


def _destroy_racer_visuals(self, racer):
    for shape in getattr(racer, "su_shapes", []):
        try:
            shape.delete()
        except Exception:
            pass
    racer.su_shapes = []
    _ORIGINALS["_destroy_racer_visuals"](self, racer)


def _spawn_racers(self):
    _ORIGINALS["_spawn_racers"](self)
    if len(self.racers) >= 12:
        return

    start = self.CHECKPOINTS[0]
    nxt = self.CHECKPOINTS[1]
    heading = math.atan2(nxt[1] - start[1], nxt[0] - start[0])
    back_x, back_y = math.cos(heading + math.pi), math.sin(heading + math.pi)
    side_x, side_y = math.cos(heading + math.pi / 2), math.sin(heading + math.pi / 2)
    i = 10
    row, lane = 6, -1
    x = start[0] + back_x * (row * 35) + side_x * (lane * 22)
    y = start[1] + back_y * (row * 35) + side_y * (lane * 22)
    ai = km.KartRacer(
        x, y, heading, km.AI_COLOR, character="CPU 11",
        emblem="Turd", ai=True, ai_index=i,
    )
    ai.next_checkpoint = 1
    self.ai_racers.append(ai)
    self.racers.append(ai)
    self._create_racer_visuals(ai)

    # Re-pack the full field into a compact 3-wide starting grid.  This keeps
    # all twelve vehicles visible even on tracks whose start line is near an edge.
    forward_x, forward_y = math.cos(heading), math.sin(heading)
    self.player.x = max(28.0, min(EngineGlobals.width - 28.0, start[0] + forward_x * 14))
    self.player.y = max(28.0, min(EngineGlobals.height - 28.0, start[1] + forward_y * 14))
    self.player.angle = heading
    lanes = (-1, 0, 1)
    for grid_index, cpu in enumerate(self.ai_racers):
        row = grid_index // 3 + 1
        lane = lanes[grid_index % 3]
        gx = start[0] + back_x * (row * 26) + side_x * (lane * 20)
        gy = start[1] + back_y * (row * 26) + side_y * (lane * 20)
        cpu.x = max(26.0, min(EngineGlobals.width - 26.0, gx))
        cpu.y = max(26.0, min(EngineGlobals.height - 26.0, gy))
        cpu.angle = heading

    for racer in self.racers:
        self._update_racer_visuals(racer)


def _delete_particles(self):
    for particle in getattr(self, "_su_particles", []):
        try:
            particle["shape"].delete()
        except Exception:
            pass
    self._su_particles = []


def _destroy_race(self):
    _delete_particles(self)
    _ORIGINALS["_destroy_race"](self)


def _emit_particle(self, x, y, color, *, vx=0.0, vy=0.0, life=26.0, radius=4.0, growth=0.08):
    if len(self._su_particles) >= 150:
        old = self._su_particles.pop(0)
        try:
            old["shape"].delete()
        except Exception:
            pass
    shape = pyglet.shapes.Circle(
        x, y, radius, color=color, batch=self.batch, group=self.kart_group,
    )
    shape.opacity = 190
    self._su_particles.append({
        "shape": shape, "vx": vx, "vy": vy, "life": life,
        "max_life": life, "growth": growth,
    })


def _update_particles(self, dt):
    alive = []
    for p in self._su_particles:
        p["life"] -= dt
        if p["life"] <= 0:
            try:
                p["shape"].delete()
            except Exception:
                pass
            continue
        shape = p["shape"]
        shape.x += p["vx"] * dt
        shape.y += p["vy"] * dt
        shape.radius += p["growth"] * dt
        shape.opacity = max(0, min(210, int(210 * p["life"] / p["max_life"])))
        alive.append(p)
    self._su_particles = alive


def _emit_race_fx(self, dt):
    if self.player is None:
        return
    racers = self.racers
    for racer in racers:
        moving = abs(racer.speed) > 2.2
        if not moving:
            continue
        rear_x = racer.x - math.cos(racer.angle) * 27
        rear_y = racer.y - math.sin(racer.angle) * 27
        if racer is self.player and racer.drifting and self._su_rng.random() < min(0.95, 0.42 * dt):
            side = self._su_rng.choice((-1, 1))
            sx = -math.sin(racer.angle) * 13 * side
            sy = math.cos(racer.angle) * 13 * side
            self._emit_particle(
                rear_x + sx, rear_y + sy, (188, 201, 216),
                vx=-math.cos(racer.angle) * 0.45 + self._su_rng.uniform(-0.25, 0.25),
                vy=-math.sin(racer.angle) * 0.45 + self._su_rng.uniform(-0.25, 0.25),
                life=32.0, radius=4.5, growth=0.10,
            )
        if racer.boost_timer > 0 and self._su_rng.random() < min(0.95, 0.36 * dt):
            color = (80, 216, 255) if racer is self.player else (255, 160, 70)
            self._emit_particle(
                rear_x, rear_y, color,
                vx=-math.cos(racer.angle) * 0.8 + self._su_rng.uniform(-0.18, 0.18),
                vy=-math.sin(racer.angle) * 0.8 + self._su_rng.uniform(-0.18, 0.18),
                life=18.0, radius=2.5, growth=0.02,
            )
        elif racer.offroad and self._su_rng.random() < min(0.8, 0.18 * dt):
            self._emit_particle(
                rear_x, rear_y, (164, 137, 101),
                vx=self._su_rng.uniform(-0.25, 0.25), vy=self._su_rng.uniform(-0.1, 0.35),
                life=28.0, radius=3.5, growth=0.07,
            )


def _update(self, dt):
    _ORIGINALS["update"](self, dt)

    if not self.active:
        return
    dt = float(dt)
    if self.state in (self.STATE_RACE, self.STATE_FINISH):
        _update_particles(self, dt)
        _emit_race_fx(self, dt)
        if hasattr(self, "place_label") and self.player is not None:
            self.place_label.text = "PLACE {}/12".format(self._current_place())

        # Pulse arena lights and boost glow to keep the image alive even at low speed.
        phase = self.race_time * 0.055
        for ring, lamp, offset in getattr(self, "_su_track_fx", []):
            pulse = (math.sin(phase + offset) + 1.0) * 0.5
            lamp.opacity = int(145 + pulse * 110)
            ring.opacity = int(80 + pulse * 95)


def _build_finish_ui(self):
    _ORIGINALS["_build_finish_ui"](self)
    if len(self._finish_labels) >= 2:
        place = self.player.finish_order or self._current_place()
        self._finish_labels[0].text = "SUPER ULTRA FINISH!"
        self._finish_labels[1].text = "{} finished {} of 12".format(
            self.player.character, place
        )


def _on_key_press(self, symbol, modifiers):
    if self.active and self.state == self.STATE_CHARACTER:
        if symbol == pyglet.window.key.LEFT:
            self.selected_character = (self.selected_character - 1) % len(km.CHARACTERS)
            self._refresh_character_highlight()
            return pyglet.event.EVENT_HANDLED
        if symbol == pyglet.window.key.RIGHT:
            self.selected_character = (self.selected_character + 1) % len(km.CHARACTERS)
            self._refresh_character_highlight()
            return pyglet.event.EVENT_HANDLED
        if symbol == pyglet.window.key.UP:
            self.selected_character = (self.selected_character - 5) % len(km.CHARACTERS)
            self._refresh_character_highlight()
            return pyglet.event.EVENT_HANDLED
        if symbol == pyglet.window.key.DOWN:
            self.selected_character = (self.selected_character + 5) % len(km.CHARACTERS)
            self._refresh_character_highlight()
            return pyglet.event.EVENT_HANDLED

    if self.active and self.state == getattr(self, "STATE_TRACK", "track"):
        if symbol == pyglet.window.key.LEFT:
            self.selected_track = (self.selected_track - 1) % len(kx.TRACKS)
            self._refresh_track_highlight()
            return pyglet.event.EVENT_HANDLED
        if symbol == pyglet.window.key.RIGHT:
            self.selected_track = (self.selected_track + 1) % len(kx.TRACKS)
            self._refresh_track_highlight()
            return pyglet.event.EVENT_HANDLED
        if symbol == pyglet.window.key.UP:
            self.selected_track = (self.selected_track - 3) % len(kx.TRACKS)
            self._refresh_track_highlight()
            return pyglet.event.EVENT_HANDLED
        if symbol == pyglet.window.key.DOWN:
            self.selected_track = (self.selected_track + 3) % len(kx.TRACKS)
            self._refresh_track_highlight()
            return pyglet.event.EVENT_HANDLED

    return _ORIGINALS["on_key_press"](self, symbol, modifiers)


def install_super_ultra():
    """Install the Super Ultra upgrade on KartsMode only."""
    global _INSTALLED
    if _INSTALLED:
        return

    # Content expansion: seven existing + six requested drivers, thirteen
    # existing + ten new tracks, and a 12-racer field.
    existing_names = {name for name, _ in km.CHARACTERS}
    additions = tuple((name, color) for name, color, _ in SUPER_ULTRA_CHARACTERS if name not in existing_names)
    km.CHARACTERS = tuple(km.CHARACTERS) + additions
    kx.EXPANDED_CHARACTERS = tuple(km.CHARACTERS)
    for name, _color, art in SUPER_ULTRA_CHARACTERS:
        kx.CHARACTER_ART[name] = art
    ks.CHARACTER_STATS.update(SUPER_ULTRA_STATS)

    existing_tracks = {track["name"] for track in kx.TRACKS}
    extras = tuple(track for track in _new_tracks() if track["name"] not in existing_tracks)
    kx.TRACKS = tuple(kx.TRACKS) + extras

    cls = km.KartsMode
    for name in (
        "__init__", "_selection_header", "_selection_footer",
        "_build_character_select", "_refresh_character_highlight",
        "_build_track_select", "_refresh_track_highlight",
        "_build_track", "_create_racer_visuals", "_update_racer_visuals",
        "_destroy_racer_visuals", "_spawn_racers", "_destroy_race",
        "update", "_build_finish_ui", "on_key_press",
    ):
        _ORIGINALS[name] = getattr(cls, name)

    cls.__init__ = _su_init
    cls._selection_header = _selection_header
    cls._selection_footer = _selection_footer
    cls._build_character_select = _build_character_select
    cls._refresh_character_highlight = _refresh_character_highlight
    cls._build_track_select = _build_track_select
    cls._refresh_track_highlight = _refresh_track_highlight
    cls._build_track = _build_track
    cls._create_racer_visuals = _create_racer_visuals
    cls._update_racer_visuals = _update_racer_visuals
    cls._destroy_racer_visuals = _destroy_racer_visuals
    cls._spawn_racers = _spawn_racers
    cls._destroy_race = _destroy_race
    cls.update = _update
    cls._build_finish_ui = _build_finish_ui
    cls.on_key_press = _on_key_press

    _INSTALLED = True
