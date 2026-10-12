"""Expansion pack for Karts not Farts: roster, tracks, and arcade mechanics."""

import math
import random

import pyglet

import karts_mode as km
from engineglobals import EngineGlobals


EXPANDED_CHARACTERS = (
    ("Kenny", (229, 154, 158)),
    ("Theo", (213, 164, 114)),
    ("Lucinda", (175, 116, 189)),
    ("Jackie Flan", (215, 154, 91)),
    ("Levod Burtim", (112, 167, 201)),
    ("Pippi", (228, 130, 173)),
    ("Vesuvius", (116, 80, 69)),
)

CHARACTER_ART = {
    "Lucinda": "generated/lucinda.png",
    "Jackie Flan": "generated/jackie_flan.png",
    "Levod Burtim": "generated/levod_burtim.png",
    "Pippi": "generated/pippi.png",
    "Vesuvius": "generated/vesuvius.png",
}


def _track(
    name,
    checkpoints,
    boosts=(),
    road_width=68,
    grass=(69, 129, 73),
    road=(77, 78, 82),
    edge=(201, 193, 169),
    hazards=(),
    ramps=(),
    nitro=(),
    tagline="",
):
    return {
        "name": name,
        "checkpoints": tuple((float(x), float(y)) for x, y in checkpoints),
        "boosts": tuple((float(x), float(y), float(r)) for x, y, r in boosts),
        "road_width": float(road_width),
        "grass": grass,
        "road": road,
        "edge": edge,
        "hazards": tuple(hazards),
        "ramps": tuple((float(x), float(y)) for x, y in ramps),
        "nitro": tuple((float(x), float(y)) for x, y in nitro),
        "tagline": tagline,
    }


TRACKS = (
    _track(
        "Bacon Ring",
        ((145, 140), (325, 96), (548, 108), (685, 212), (666, 386), (515, 500), (292, 505), (125, 414), (92, 260)),
        ((430, 100, 0), (676, 310, 92), (408, 505, 180), (105, 335, -92)),
        nitro=((590, 155),),
        tagline="The original fast loop.",
    ),
    _track(
        "Lucinda Farm Loop",
        ((125, 130), (300, 90), (555, 105), (690, 190), (625, 315), (700, 455), (470, 505), (260, 470), (100, 370), (95, 235)),
        ((360, 92, 0), (665, 405, 90)),
        grass=(95, 145, 72),
        road=(102, 88, 70),
        edge=(215, 190, 131),
        hazards=(("mud", 520, 112, 45), ("mud", 250, 470, 42)),
        ramps=((630, 315),),
        nitro=((116, 310),),
        tagline="Mud patches and a barnyard ramp.",
    ),
    _track(
        "Van Down by the River",
        ((110, 150), (280, 92), (510, 100), (680, 165), (705, 300), (620, 455), (420, 510), (225, 485), (90, 390), (82, 260)),
        ((395, 96, 0), (650, 420, 120), (150, 445, 210)),
        grass=(60, 122, 118),
        road=(72, 83, 88),
        edge=(184, 197, 190),
        hazards=(("oil", 700, 280, 30),),
        ramps=((360, 505),),
        nitro=((195, 103),),
        tagline="River bends, oil slicks, and a dock jump.",
    ),
    _track(
        "Dojo Dash",
        ((130, 115), (345, 95), (645, 120), (700, 280), (625, 470), (385, 505), (150, 470), (80, 315), (90, 185)),
        ((470, 100, 0), (665, 385, 110), (235, 492, 180)),
        grass=(136, 75, 69),
        road=(80, 73, 72),
        edge=(234, 215, 177),
        hazards=(("oil", 650, 140, 28), ("oil", 112, 410, 28)),
        nitro=((690, 290), (95, 250)),
        tagline="Tight corners reward clean drifting.",
    ),
    _track(
        "Rainbomb Orbit",
        ((145, 130), (340, 80), (600, 105), (710, 230), (670, 430), (505, 520), (265, 510), (92, 420), (72, 230)),
        ((470, 92, 0), (685, 335, 90), (380, 518, 180), (84, 330, -90)),
        grass=(32, 34, 66),
        road=(66, 69, 100),
        edge=(153, 154, 205),
        hazards=(("oil", 550, 110, 26),),
        ramps=((690, 225), (250, 510)),
        nitro=((105, 180),),
        tagline="Low gravity flavor: two huge jump ramps.",
    ),
    _track(
        "Vesuvius Rim",
        ((125, 125), (320, 82), (585, 110), (705, 245), (655, 435), (470, 525), (230, 500), (80, 360), (78, 205)),
        ((430, 92, 0), (680, 360, 105)),
        grass=(126, 74, 49),
        road=(76, 70, 67),
        edge=(223, 159, 93),
        hazards=(("lava", 620, 120, 35), ("lava", 120, 425, 38)),
        ramps=((660, 435),),
        nitro=((250, 95), (360, 515)),
        tagline="Lava patches spin slow racers sideways.",
    ),
    _track(
        "Theo Trailer Park",
        ((130, 140), (305, 95), (520, 95), (680, 150), (710, 310), (590, 475), (370, 515), (160, 470), (80, 330), (88, 220)),
        ((405, 96, 0), (640, 430, 125)),
        grass=(168, 135, 89),
        road=(91, 84, 78),
        edge=(222, 203, 163),
        hazards=(("oil", 555, 100, 30), ("mud", 110, 290, 40)),
        ramps=((695, 300),),
        nitro=((235, 110),),
        tagline="Trailer clutter, sand, and one mean shortcut jump.",
    ),
    _track(
        "Ketchup Spillway",
        ((130, 130), (330, 82), (610, 100), (715, 250), (645, 470), (395, 525), (170, 475), (70, 330), (85, 205)),
        ((470, 90, 0), (675, 375, 110), (260, 505, 180)),
        grass=(143, 64, 52),
        road=(83, 71, 69),
        edge=(235, 184, 151),
        hazards=(("ketchup", 590, 110, 42), ("ketchup", 145, 455, 44)),
        ramps=((700, 255),),
        nitro=((105, 265),),
        tagline="Sticky ketchup slows everybody who cuts the corner.",
    ),
    _track(
        "Toga Chorus Circuit",
        ((120, 145), (270, 85), (510, 78), (690, 145), (720, 330), (610, 485), (400, 525), (190, 480), (75, 340), (82, 225)),
        ((390, 80, 0), (700, 240, 90), (505, 510, 180)),
        grass=(194, 160, 103),
        road=(102, 91, 87),
        edge=(238, 222, 188),
        hazards=(("oil", 610, 105, 25), ("oil", 215, 478, 25)),
        ramps=((710, 330),),
        nitro=((105, 385),),
        tagline="Wide Roman corners built for long drift boosts.",
    ),
    _track(
        "Nevada Dust Bowl",
        ((130, 145), (300, 95), (540, 90), (690, 180), (700, 360), (560, 495), (330, 515), (125, 450), (70, 300), (85, 205)),
        ((420, 92, 0), (665, 415, 120)),
        road_width=62,
        grass=(181, 145, 90),
        road=(104, 87, 71),
        edge=(224, 195, 145),
        hazards=(("mud", 520, 95, 50), ("mud", 95, 390, 46)),
        ramps=((690, 180), (330, 510)),
        nitro=((180, 120),),
        tagline="Narrow dusty roads punish off-road driving.",
    ),
    _track(
        "Pippi Pier",
        ((125, 135), (330, 88), (580, 100), (710, 220), (675, 405), (520, 510), (285, 515), (105, 430), (70, 275)),
        ((440, 93, 0), (690, 315, 90), (390, 515, 180)),
        grass=(64, 132, 156),
        road=(82, 88, 93),
        edge=(211, 202, 159),
        hazards=(("oil", 645, 120, 28),),
        ramps=((515, 505),),
        nitro=((115, 355), (610, 450)),
        tagline="Pier jumps and two big nitro lines.",
    ),
    _track(
        "Jackie Switchbacks",
        ((120, 135), (305, 85), (600, 90), (700, 175), (590, 255), (705, 350), (600, 485), (355, 520), (150, 480), (70, 345), (92, 225)),
        ((455, 88, 0), (660, 440, 130)),
        road_width=58,
        grass=(103, 124, 92),
        road=(74, 77, 76),
        edge=(207, 190, 165),
        hazards=(("oil", 605, 255, 24), ("oil", 685, 350, 24)),
        nitro=((165, 110), (235, 505)),
        tagline="Sharp switchbacks: drift or get left behind.",
    ),
    _track(
        "Levod Labyrinth",
        ((120, 145), (280, 85), (505, 80), (690, 125), (620, 225), (715, 320), (630, 455), (450, 520), (245, 500), (105, 425), (75, 300), (90, 205)),
        ((390, 82, 0), (680, 390, 110)),
        road_width=60,
        grass=(68, 91, 113),
        road=(60, 69, 78),
        edge=(153, 184, 203),
        hazards=(("oil", 620, 225, 23), ("mud", 110, 405, 32)),
        ramps=((705, 320),),
        nitro=((535, 490),),
        tagline="A technical maze with mixed surfaces.",
    ),
)


_ORIGINALS = {}
_INSTALLED = False


def _selected_track(self):
    return TRACKS[self.selected_track % len(TRACKS)]


def _expanded_init(self, *args, **kwargs):
    _ORIGINALS["__init__"](self, *args, **kwargs)
    self.selected_track = 0
    self._character_panels = []
    self._track_panels = []
    self.slipstream_charge = 0.0
    self._mechanic_message = ""
    self._mechanic_message_timer = 0.0


def _expanded_start(self):
    self.selected_track = 0
    self.slipstream_charge = 0.0
    _ORIGINALS["start"](self)


def _build_character_select(self):
    self._clear_selection_ui()
    self._selection_header("PICK YOUR RACER")
    self._selection_footer()
    self._character_panels = []
    cols = 4
    start_x = 110
    x_gap = 195
    y_rows = (350, 190)
    for index, (name, face_color) in enumerate(km.CHARACTERS):
        row = index // cols
        col = index % cols
        x = start_x + col * x_gap
        y = y_rows[min(row, 1)]
        panel = pyglet.shapes.Rectangle(
            x - 70, y - 55, 140, 125,
            color=(50, 57, 70), batch=self.batch, group=self.track_group,
        )
        self._selection_shapes.append(panel)
        self._character_panels.append(panel)

        art_file = CHARACTER_ART.get(name)
        loaded_art = False
        if art_file:
            try:
                image = pyglet.resource.image(art_file)
                sprite = pyglet.sprite.Sprite(img=image, batch=self.batch, group=self.ui_group)
                sprite.scale = min(3.0, 82.0 / max(1.0, float(max(image.width, image.height))))
                sprite.x = x - sprite.width / 2
                sprite.y = y - 5 - sprite.height / 2
                self._selection_shapes.append(sprite)
                loaded_art = True
            except Exception:
                loaded_art = False
        if not loaded_art:
            head = pyglet.shapes.Circle(x, y + 15, 31, color=face_color, batch=self.batch, group=self.ui_group)
            eye_l = pyglet.shapes.Circle(x - 10, y + 23, 3, color=(30, 25, 22), batch=self.batch, group=self.ui_group)
            eye_r = pyglet.shapes.Circle(x + 10, y + 23, 3, color=(30, 25, 22), batch=self.batch, group=self.ui_group)
            mouth = pyglet.shapes.Rectangle(x - 12, y - 1, 24, 5, color=(92, 38, 42), batch=self.batch, group=self.ui_group)
            self._selection_shapes.extend((head, eye_l, eye_r, mouth))

        label = pyglet.text.Label(
            name.upper(), x=x, y=y - 38, anchor_x="center",
            font_size=11, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        self._selection_labels.append(label)
    self._refresh_character_highlight()


def _refresh_character_highlight(self):
    for index, panel in enumerate(getattr(self, "_character_panels", [])):
        panel.color = (112, 121, 145) if index == self.selected_character else (50, 57, 70)


def _build_track_select(self):
    self._clear_selection_ui()
    self._selection_header("PICK A TRACK — 13 COURSES")
    self._selection_footer()
    self._track_panels = []
    for index, track in enumerate(TRACKS):
        col = index % 2
        row = index // 2
        x = 245 + col * 310
        y = 445 - row * 54
        panel = pyglet.shapes.Rectangle(
            x - 140, y - 20, 280, 42,
            color=(47, 53, 65), batch=self.batch, group=self.track_group,
        )
        self._selection_shapes.append(panel)
        self._track_panels.append(panel)
        label = pyglet.text.Label(
            track["name"].upper(),
            x=x, y=y + 3, anchor_x="center", anchor_y="center",
            font_size=12, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        sub = pyglet.text.Label(
            track["tagline"],
            x=x, y=y - 12, anchor_x="center", anchor_y="center",
            font_size=8, color=(195, 205, 219, 255),
            batch=self.batch, group=self.ui_group,
        )
        self._selection_labels.extend((label, sub))
    self._refresh_track_highlight()


def _refresh_track_highlight(self):
    for index, panel in enumerate(getattr(self, "_track_panels", [])):
        panel.color = (106, 116, 139) if index == self.selected_track else (47, 53, 65)


def _prepare_track(self):
    track = _selected_track(self)
    self.CHECKPOINTS = track["checkpoints"]
    self.BOOST_PADS = track["boosts"]
    self.ROAD_HALF_WIDTH = track["road_width"]
    km.GRASS_COLOR = track["grass"]
    km.ROAD_COLOR = track["road"]
    km.ROAD_EDGE = track["edge"]


def _build_track_expanded(self):
    _prepare_track(self)
    _ORIGINALS["_build_track"](self)
    track = _selected_track(self)

    title = pyglet.text.Label(
        track["name"].upper(),
        x=EngineGlobals.width // 2, y=EngineGlobals.height - 25,
        anchor_x="center", font_size=13, weight=pyglet.text.Weight.BOLD,
        color=(255, 245, 205, 255), batch=self.batch, group=self.ui_group,
    )
    self.mechanic_label = pyglet.text.Label(
        "",
        x=EngineGlobals.width - 18, y=44, anchor_x="right",
        font_size=10, color=(194, 235, 255, 255),
        batch=self.batch, group=self.ui_group,
    )
    self._race_labels.extend((title, self.mechanic_label))

    for x, y in track["nitro"]:
        outer = pyglet.shapes.Circle(x, y, 20, color=(66, 214, 232), batch=self.batch, group=self.track_group)
        inner = pyglet.shapes.Circle(x, y, 11, color=track["road"], batch=self.batch, group=self.track_group)
        self._race_shapes.extend((outer, inner))

    for x, y in track["ramps"]:
        deck = pyglet.shapes.Rectangle(x - 26, y - 13, 52, 26, color=(219, 170, 86), batch=self.batch, group=self.track_group)
        stripe = pyglet.shapes.Rectangle(x - 22, y - 4, 44, 8, color=(250, 227, 148), batch=self.batch, group=self.track_group)
        self._race_shapes.extend((deck, stripe))

    for kind, x, y, radius in track["hazards"]:
        if kind == "oil":
            shape = pyglet.shapes.Circle(x, y, radius, color=(35, 32, 35), batch=self.batch, group=self.track_group)
            shine = pyglet.shapes.Circle(x - radius * 0.25, y + radius * 0.2, max(3, radius * 0.18), color=(92, 82, 96), batch=self.batch, group=self.track_group)
            self._race_shapes.extend((shape, shine))
        elif kind == "lava":
            shape = pyglet.shapes.Circle(x, y, radius, color=(222, 72, 28), batch=self.batch, group=self.track_group)
            core = pyglet.shapes.Circle(x, y, radius * 0.55, color=(255, 176, 48), batch=self.batch, group=self.track_group)
            self._race_shapes.extend((shape, core))
        elif kind == "ketchup":
            shape = pyglet.shapes.Circle(x, y, radius, color=(177, 45, 42), batch=self.batch, group=self.track_group)
            self._race_shapes.append(shape)
        else:
            shape = pyglet.shapes.Circle(x, y, radius, color=(117, 87, 58), batch=self.batch, group=self.track_group)
            self._race_shapes.append(shape)


def _create_racer_visuals_expanded(self, racer):
    _ORIGINALS["_create_racer_visuals"](self, racer)
    if racer.ai:
        return
    racer.character_art = None
    art_file = CHARACTER_ART.get(racer.character)
    if not art_file:
        return
    try:
        image = pyglet.resource.image(art_file)
        racer.character_art = pyglet.sprite.Sprite(img=image, batch=self.batch, group=self.kart_group)
        racer.character_art.scale = min(1.8, 28.0 / max(1.0, float(max(image.width, image.height))))
        if racer.head is not None:
            racer.head.visible = False
    except Exception:
        racer.character_art = None


def _update_racer_visuals_expanded(self, racer):
    _ORIGINALS["_update_racer_visuals"](self, racer)
    art = getattr(racer, "character_art", None)
    if art is not None:
        hop = 7.0 if racer.hop_timer > 0 else 0.0
        dx, dy = self._rotate_local(-10, 0, racer.angle)
        art.x = racer.x + dx - art.width / 2
        art.y = racer.y + dy + hop - art.height / 2
        art.rotation = -math.degrees(racer.angle)


def _destroy_racer_visuals_expanded(self, racer):
    art = getattr(racer, "character_art", None)
    if art is not None:
        art.delete()
        racer.character_art = None
    _ORIGINALS["_destroy_racer_visuals"](self, racer)


def _apply_track_features(self, racer, dt, player=False):
    track = _selected_track(self)
    racer.feature_cooldown = max(0.0, getattr(racer, "feature_cooldown", 0.0) - dt)

    for x, y in track["ramps"]:
        if math.hypot(racer.x - x, racer.y - y) <= 32 and racer.feature_cooldown <= 0:
            racer.hop_timer = max(racer.hop_timer, 26.0)
            racer.boost_timer = max(racer.boost_timer, 24.0)
            racer.speed = max(racer.speed, 6.3)
            racer.feature_cooldown = 70.0
            if player:
                self._mechanic_message = "RAMP HOP!"
                self._mechanic_message_timer = 45.0
            break

    for x, y in track["nitro"]:
        if math.hypot(racer.x - x, racer.y - y) <= 28 and racer.feature_cooldown <= 0:
            racer.boost_timer = max(racer.boost_timer, 62.0)
            racer.speed = max(racer.speed, 7.6)
            racer.feature_cooldown = 90.0
            if player:
                self._mechanic_message = "NITRO RING!"
                self._mechanic_message_timer = 55.0
            break

    for kind, x, y, radius in track["hazards"]:
        if math.hypot(racer.x - x, racer.y - y) > radius:
            continue
        if kind in ("mud", "ketchup"):
            racer.speed *= (0.935 if kind == "mud" else 0.91) ** dt
            if player:
                self._mechanic_message = "MUD!" if kind == "mud" else "STICKY KETCHUP!"
                self._mechanic_message_timer = max(self._mechanic_message_timer, 8.0)
        elif racer.feature_cooldown <= 0:
            if kind == "oil":
                racer.angle += 1.0 if random.random() > 0.5 else -1.0
                racer.speed *= 0.67
                if player:
                    self._mechanic_message = "OIL SPIN!"
                    self._mechanic_message_timer = 55.0
            elif kind == "lava":
                racer.angle += 0.55 if random.random() > 0.5 else -0.55
                racer.speed *= 0.52
                racer.hop_timer = max(racer.hop_timer, 12.0)
                if player:
                    self._mechanic_message = "HOT LAVA!"
                    self._mechanic_message_timer = 55.0
            racer.feature_cooldown = 85.0


def _apply_slipstream(self, dt):
    p = self.player
    if p is None or p.finished or p.speed < 2.8:
        self.slipstream_charge = max(0.0, self.slipstream_charge - 1.4 * dt)
        return
    forward_x = math.cos(p.angle)
    forward_y = math.sin(p.angle)
    drafting = False
    for ai in self.ai_racers:
        if ai.finished:
            continue
        dx = ai.x - p.x
        dy = ai.y - p.y
        distance = math.hypot(dx, dy)
        if distance < 25 or distance > 125:
            continue
        along = dx * forward_x + dy * forward_y
        lateral = abs(dx * (-forward_y) + dy * forward_x)
        angle_gap = abs(self._angle_delta(ai.angle, p.angle))
        if along > 15 and lateral < 34 and angle_gap < 0.7:
            drafting = True
            break
    if drafting:
        self.slipstream_charge = min(100.0, self.slipstream_charge + 1.25 * dt)
        if self.slipstream_charge >= 100.0:
            p.boost_timer = max(p.boost_timer, 70.0)
            p.speed = max(p.speed, 7.4)
            self.slipstream_charge = 0.0
            self._mechanic_message = "SLIPSTREAM BOOST!"
            self._mechanic_message_timer = 70.0
    else:
        self.slipstream_charge = max(0.0, self.slipstream_charge - 0.9 * dt)


def _update_player_expanded(self, dt):
    _ORIGINALS["_update_player"](self, dt)
    if self.player is None:
        return
    _apply_track_features(self, self.player, dt, player=True)
    _apply_slipstream(self, dt)


def _update_ai_expanded(self, racer, dt):
    _ORIGINALS["_update_ai"](self, racer, dt)
    _apply_track_features(self, racer, dt, player=False)


def _start_race_expanded(self):
    _prepare_track(self)
    self.slipstream_charge = 0.0
    self._mechanic_message = ""
    self._mechanic_message_timer = 0.0
    _ORIGINALS["_start_race"](self)


def _update_expanded(self, dt):
    _ORIGINALS["update"](self, dt)
    if not self.active or self.state not in (self.STATE_RACE, self.STATE_FINISH):
        return
    if hasattr(self, "mechanic_label"):
        if self._mechanic_message_timer > 0:
            self._mechanic_message_timer -= float(dt)
            self.mechanic_label.text = self._mechanic_message
        elif self.state == self.STATE_RACE and self.slipstream_charge > 0:
            self.mechanic_label.text = f"DRAFT {int(self.slipstream_charge)}%"
        else:
            self.mechanic_label.text = ""


def _on_key_press_expanded(self, symbol, modifiers):
    if not self.active:
        return pyglet.event.EVENT_UNHANDLED

    if self.state == getattr(self, "STATE_TRACK", "track"):
        if symbol == pyglet.window.key.ESCAPE:
            self.state = self.STATE_EMBLEM
            self._build_emblem_select()
        elif symbol == pyglet.window.key.LEFT:
            self.selected_track = (self.selected_track - 1) % len(TRACKS)
            self._refresh_track_highlight()
        elif symbol == pyglet.window.key.RIGHT:
            self.selected_track = (self.selected_track + 1) % len(TRACKS)
            self._refresh_track_highlight()
        elif symbol == pyglet.window.key.UP:
            self.selected_track = (self.selected_track - 2) % len(TRACKS)
            self._refresh_track_highlight()
        elif symbol == pyglet.window.key.DOWN:
            self.selected_track = (self.selected_track + 2) % len(TRACKS)
            self._refresh_track_highlight()
        elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
            self._start_race()
        return pyglet.event.EVENT_HANDLED

    if self.state == self.STATE_EMBLEM:
        if symbol == pyglet.window.key.ESCAPE:
            self.state = self.STATE_COLOR
            self._build_color_select()
        elif symbol in (pyglet.window.key.LEFT, pyglet.window.key.UP):
            self.selected_emblem = (self.selected_emblem - 1) % len(km.EMBLEMS)
            self._refresh_emblem_highlight()
        elif symbol in (pyglet.window.key.RIGHT, pyglet.window.key.DOWN):
            self.selected_emblem = (self.selected_emblem + 1) % len(km.EMBLEMS)
            self._refresh_emblem_highlight()
        elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
            self.state = self.STATE_TRACK
            self._build_track_select()
        return pyglet.event.EVENT_HANDLED

    return _ORIGINALS["on_key_press"](self, symbol, modifiers)


def install_karts_expansion():
    """Install the larger roster, 13-track cup, and extra racing mechanics."""
    global _INSTALLED
    if _INSTALLED:
        return

    km.CHARACTERS = EXPANDED_CHARACTERS
    cls = km.KartsMode
    cls.STATE_TRACK = "track"

    for name in (
        "__init__",
        "start",
        "_build_track",
        "_create_racer_visuals",
        "_update_racer_visuals",
        "_destroy_racer_visuals",
        "_update_player",
        "_update_ai",
        "_start_race",
        "update",
        "on_key_press",
    ):
        _ORIGINALS[name] = getattr(cls, name)

    cls.__init__ = _expanded_init
    cls.start = _expanded_start
    cls._build_character_select = _build_character_select
    cls._refresh_character_highlight = _refresh_character_highlight
    cls._build_track_select = _build_track_select
    cls._refresh_track_highlight = _refresh_track_highlight
    cls._build_track = _build_track_expanded
    cls._create_racer_visuals = _create_racer_visuals_expanded
    cls._update_racer_visuals = _update_racer_visuals_expanded
    cls._destroy_racer_visuals = _destroy_racer_visuals_expanded
    cls._update_player = _update_player_expanded
    cls._update_ai = _update_ai_expanded
    cls._start_race = _start_race_expanded
    cls.update = _update_expanded
    cls.on_key_press = _on_key_press_expanded

    _INSTALLED = True
