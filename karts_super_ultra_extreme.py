"""Extreme visual/content pass for Super Ultra Kenny Kart only.

Installed after karts_super_ultra. This module deliberately imports no Mode 7
or N64 racing code and patches only KartsMode, the Super Ultra kart stack.
"""
from __future__ import annotations

import math
import random

import pyglet

import karts_expansion as kx
import karts_mode as km
import karts_stats as ks
from engineglobals import EngineGlobals
from super_ultra_content import CUPS, DRIVERS, TRACKS as CINEMATIC_TRACKS


_ORIGINALS = {}
_INSTALLED = False


def _bright(c, n=35):
    return tuple(min(255, int(v) + n) for v in c)


def _dark(c, n=35):
    return tuple(max(0, int(v) - n) for v in c)


def _add_missing_drivers():
    existing = {name for name, _ in km.CHARACTERS}
    additions = []
    for driver in DRIVERS:
        name = driver["name"]
        if name in existing:
            continue
        additions.append((name, driver["color"]))
        if driver.get("art"):
            kx.CHARACTER_ART[name] = driver["art"]
        ks.CHARACTER_STATS[name] = {
            "speed": driver["speed"],
            "accel": driver["accel"],
            "turn": driver["handling"],
            "weight": driver["weight"],
            "grip": driver["handling"],
            "boost": driver["boost"],
            "trait": "SUPER ULTRA — cinematic specialist",
        }
        existing.add(name)
    km.CHARACTERS = tuple(km.CHARACTERS) + tuple(additions)
    kx.EXPANDED_CHARACTERS = tuple(km.CHARACTERS)


def _topdown_track(spec, seed):
    """Translate a cinematic catalog entry into KartsMode's authored track form."""
    rng = random.Random(88000 + seed * 313)
    count = 9 + seed % 3
    cx, cy = 400.0, 300.0
    rx = 287.0 + rng.uniform(-18, 18)
    ry = 205.0 + rng.uniform(-16, 16)
    points = []
    for i in range(count):
        a = -math.pi * 0.72 + i * math.tau / count
        wobble = 1.0 + rng.uniform(-0.11, 0.11)
        x = cx + math.cos(a) * rx * wobble
        y = cy + math.sin(a) * ry * (1.0 + rng.uniform(-0.08, 0.08))
        points.append((max(62.0, min(738.0, x)), max(78.0, min(522.0, y))))

    boosts = []
    for i in (1, count // 2, count - 2):
        x, y = points[i]
        nx, ny = points[(i + 1) % count]
        boosts.append((x, y, math.degrees(math.atan2(ny - y, nx - x))))

    hazard_kinds = ("oil", "mud", "ketchup", "oil", "lava")
    hazards = []
    for j, i in enumerate((2, max(3, count // 2 + 1))):
        x, y = points[i % count]
        hazards.append((hazard_kinds[(seed + j) % len(hazard_kinds)], x, y, 24 + (seed + j) % 14))

    ramps = tuple(points[i % count] for i in (3, count - 3))
    nitro = tuple(points[i % count] for i in (0, count // 2 - 1))
    theme = spec["theme"]
    return kx._track(
        spec["name"], points, boosts,
        road_width=60 + seed % 12,
        grass=theme["ground"], road=theme["road"], edge=theme["edge"],
        hazards=tuple(hazards), ramps=ramps, nitro=nitro,
        tagline=spec["tagline"],
    )


def _fill_to_fifty_tracks():
    existing_names = {track["name"] for track in kx.TRACKS}
    tracks = list(kx.TRACKS)
    for seed, spec in enumerate(CINEMATIC_TRACKS):
        if len(tracks) >= 50:
            break
        if spec["name"] in existing_names:
            continue
        tracks.append(_topdown_track(spec, seed))
        existing_names.add(spec["name"])
    kx.TRACKS = tuple(tracks[:50])


def _extreme_init(self, *args, **kwargs):
    _ORIGINALS["__init__"](self, *args, **kwargs)
    self.STATE_ULTRA_HOME = "ultra_home"
    self.STATE_ULTRA_CUP = "ultra_cup"
    self.STATE_ULTRA_PAUSE = "ultra_pause"
    self.ultra_mode = "quick"
    self.ultra_home_choice = 0
    self.selected_cup = 0
    self.ultra_gp_race = 0
    self.ultra_energy = 100.0
    self.ultra_overdrive = False
    self._extreme_track_page = -1
    self._extreme_atmosphere = []
    self._extreme_speed_lines = []
    self._extreme_landmarks = []
    self._extreme_joysticks = []
    self._extreme_axis_x = 0.0
    self._extreme_nav_cooldown = 0.0
    self._extreme_pad_buttons = set()


def _panel(self, x, y, w, h, selected=False):
    glow = pyglet.shapes.Rectangle(
        x - 4, y - 4, w + 8, h + 8,
        color=(55, 194, 244) if selected else (24, 54, 83),
        batch=self.batch, group=self.track_group,
    )
    glow.opacity = 235 if selected else 115
    body = pyglet.shapes.Rectangle(
        x, y, w, h,
        color=(23, 36, 60) if selected else (10, 18, 35),
        batch=self.batch, group=self.track_group,
    )
    self._selection_shapes.extend((glow, body))
    return glow, body


def _build_ultra_home(self):
    self._clear_selection_ui()
    self.state = self.STATE_ULTRA_HOME
    self.mode_title.visible = True
    self.mode_title.text = "SUPER ULTRA KENNY KART"
    self._selection_header("CINEMATIC CHAMPIONSHIP // EXTREME GRAPHICS EDITION")
    self._selection_footer()
    self._ultra_home_panels = []
    choices = (
        ("QUICK RACE", "Pick any of 50 tracks and race a 12-kart field."),
        ("GRAND PRIX", "Ten cups. Five races each. Full Super Ultra campaign."),
        ("RETURN TO KENNY HOGGINS", "Back to the main game menu."),
    )
    for i, (title, detail) in enumerate(choices):
        y = 355 - i * 96
        pair = _panel(self, 178, y, 444, 68, i == self.ultra_home_choice)
        self._ultra_home_panels.append(pair)
        self._selection_labels.append(pyglet.text.Label(
            title, x=400, y=y + 39, anchor_x="center", anchor_y="center",
            font_size=17, weight=pyglet.text.Weight.BOLD,
            color=(244, 249, 255, 255), batch=self.batch, group=self.ui_group,
        ))
        self._selection_labels.append(pyglet.text.Label(
            detail, x=400, y=y + 18, anchor_x="center", anchor_y="center",
            font_size=8, color=(150, 204, 235, 255), batch=self.batch, group=self.ui_group,
        ))
    self._selection_labels.append(pyglet.text.Label(
        "24 DRIVERS  //  50 TRACKS  //  12 RACERS  //  10 CUPS",
        x=400, y=91, anchor_x="center", font_size=10,
        weight=pyglet.text.Weight.BOLD, color=(243, 126, 220, 255),
        batch=self.batch, group=self.ui_group,
    ))


def _extreme_start(self):
    _ORIGINALS["start"](self)
    self.ultra_home_choice = 0
    self.ultra_mode = "quick"
    self.ultra_gp_race = 0
    self._attach_extreme_controllers()
    self._build_ultra_home()


def _extreme_stop(self):
    self._detach_extreme_controllers()
    _ORIGINALS["stop"](self)


def _build_character_select(self):
    self._clear_selection_ui()
    self.state = self.STATE_CHARACTER
    self._selection_header("DRIVER GRID // 24 RACERS // CHOOSE YOUR MACHINE")
    self._selection_footer()
    self._character_panels = []
    cols = 6
    for index, (name, face_color) in enumerate(km.CHARACTERS):
        row, col = divmod(index, cols)
        x = 72 + col * 131
        y = 414 - row * 91
        glow, body = _panel(self, x - 53, y - 37, 106, 74, index == self.selected_character)
        self._character_panels.append((glow, body))
        art_file = kx.CHARACTER_ART.get(name)
        loaded = False
        if art_file:
            try:
                image = pyglet.resource.image(art_file)
                sprite = pyglet.sprite.Sprite(image, batch=self.batch, group=self.ui_group)
                sprite.scale = min(2.0, 36.0 / max(1.0, float(max(image.width, image.height))))
                sprite.x = x - sprite.width / 2
                sprite.y = y - 4 - sprite.height / 2
                self._selection_shapes.append(sprite)
                loaded = True
            except Exception:
                loaded = False
        if not loaded:
            head = pyglet.shapes.Circle(x, y, 14, color=face_color, batch=self.batch, group=self.ui_group)
            self._selection_shapes.append(head)
        stats = ks.CHARACTER_STATS.get(name, ks.CHARACTER_STATS["Kenny"])
        self._selection_labels.append(pyglet.text.Label(
            name.upper(), x=x, y=y + 24, anchor_x="center",
            font_size=6 if len(name) > 15 else 7, weight=pyglet.text.Weight.BOLD,
            color=(245, 249, 255, 255), batch=self.batch, group=self.ui_group,
        ))
        self._selection_labels.append(pyglet.text.Label(
            "S{} A{} T{} B{}".format(stats["speed"], stats["accel"], stats["turn"], stats["boost"]),
            x=x, y=y - 27, anchor_x="center", font_size=5,
            color=(107, 216, 248, 255), batch=self.batch, group=self.ui_group,
        ))
    self._stat_detail_label = pyglet.text.Label(
        "", x=400, y=61, anchor_x="center", font_size=9,
        weight=pyglet.text.Weight.BOLD, color=(255, 210, 119, 255),
        batch=self.batch, group=self.ui_group,
    )
    self._selection_labels.append(self._stat_detail_label)
    self._refresh_character_highlight()


def _refresh_character_highlight(self):
    for i, pair in enumerate(getattr(self, "_character_panels", [])):
        glow, body = pair
        selected = i == self.selected_character
        glow.color = (61, 204, 255) if selected else (24, 54, 83)
        glow.opacity = 245 if selected else 105
        body.color = (29, 47, 76) if selected else (10, 18, 35)
    if getattr(self, "_stat_detail_label", None) is not None:
        name = km.CHARACTERS[self.selected_character % len(km.CHARACTERS)][0]
        stats = ks.CHARACTER_STATS.get(name, ks.CHARACTER_STATS["Kenny"])
        self._stat_detail_label.text = "{} // {}".format(name.upper(), stats.get("trait", "SUPER ULTRA"))


def _build_track_select(self):
    self._clear_selection_ui()
    self.state = getattr(self, "STATE_TRACK", "track")
    page = self.selected_track // 10
    self._extreme_track_page = page
    self._selection_header("CIRCUIT MATRIX // 50 TRACKS // PAGE {}/5".format(page + 1))
    self._selection_footer()
    self._track_panels = []
    start = page * 10
    for slot in range(10):
        idx = start + slot
        if idx >= len(kx.TRACKS):
            break
        track = kx.TRACKS[idx]
        col, row = slot % 2, slot // 2
        x = 51 + col * 374
        y = 397 - row * 65
        glow, body = _panel(self, x, y, 324, 49, idx == self.selected_track)
        self._track_panels.append((idx, glow, body))
        self._selection_labels.append(pyglet.text.Label(
            "{:02d}  {}".format(idx + 1, track["name"].upper()),
            x=x + 162, y=y + 30, anchor_x="center", anchor_y="center",
            font_size=8 if len(track["name"]) > 25 else 9,
            weight=pyglet.text.Weight.BOLD, color=(239, 246, 255, 255),
            batch=self.batch, group=self.ui_group,
        ))
        self._selection_labels.append(pyglet.text.Label(
            track.get("tagline", ""), x=x + 162, y=y + 13,
            anchor_x="center", anchor_y="center", font_size=6,
            color=(155, 187, 218, 255), batch=self.batch, group=self.ui_group,
        ))
    self._track_detail_label = pyglet.text.Label(
        "", x=400, y=57, anchor_x="center", font_size=9,
        weight=pyglet.text.Weight.BOLD, color=(255, 139, 225, 255),
        batch=self.batch, group=self.ui_group,
    )
    self._selection_labels.append(self._track_detail_label)
    self._refresh_track_highlight()


def _refresh_track_highlight(self):
    page = self.selected_track // 10
    if page != getattr(self, "_extreme_track_page", -1):
        self._build_track_select()
        return
    for idx, glow, body in getattr(self, "_track_panels", []):
        selected = idx == self.selected_track
        glow.color = (220, 71, 242) if selected else (24, 54, 83)
        glow.opacity = 245 if selected else 105
        body.color = (51, 26, 65) if selected else (10, 18, 35)
    if getattr(self, "_track_detail_label", None) is not None:
        track = kx.TRACKS[self.selected_track]
        self._track_detail_label.text = "{}  //  TRACK {:02d}/50".format(track["name"].upper(), self.selected_track + 1)


def _build_cup_select(self):
    self._clear_selection_ui()
    self.state = self.STATE_ULTRA_CUP
    self._selection_header("GRAND PRIX // 10 CUPS // FIVE RACES EACH")
    self._selection_footer()
    self._ultra_cup_panels = []
    for i, cup in enumerate(CUPS):
        col, row = i % 2, i // 2
        x, y = 82 + col * 356, 400 - row * 67
        pair = _panel(self, x, y, 280, 50, i == self.selected_cup)
        self._ultra_cup_panels.append(pair)
        self._selection_labels.append(pyglet.text.Label(
            cup, x=x + 140, y=y + 30, anchor_x="center", anchor_y="center",
            font_size=13, weight=pyglet.text.Weight.BOLD,
            color=(245, 249, 255, 255), batch=self.batch, group=self.ui_group,
        ))
        self._selection_labels.append(pyglet.text.Label(
            "TRACKS {:02d}-{:02d}".format(i * 5 + 1, i * 5 + 5),
            x=x + 140, y=y + 12, anchor_x="center", anchor_y="center",
            font_size=7, color=(123, 210, 245, 255), batch=self.batch, group=self.ui_group,
        ))


def _clear_extreme_track_fx(self):
    self._extreme_atmosphere = []
    self._extreme_speed_lines = []
    self._extreme_landmarks = []


def _add_landmark(self, track, kind):
    edge = track["edge"]
    if kind == 0:  # skyline
        for i in range(7):
            x = 18 + i * 38
            h = 55 + (i * 31) % 90
            b = pyglet.shapes.Rectangle(x, 420, 28, h, color=_dark(edge, 95), batch=self.batch, group=self.track_group)
            b.opacity = 195
            self._race_shapes.append(b); self._extreme_landmarks.append(b)
    elif kind == 1:  # lighthouse
        tower = pyglet.shapes.Rectangle(716, 368, 25, 120, color=(217, 220, 211), batch=self.batch, group=self.track_group)
        cap = pyglet.shapes.Rectangle(709, 480, 39, 18, color=(175, 65, 70), batch=self.batch, group=self.track_group)
        lamp = pyglet.shapes.Circle(728, 491, 15, color=_bright(edge, 60), batch=self.batch, group=self.track_group); lamp.opacity = 145
        self._race_shapes += [tower, cap, lamp]; self._extreme_landmarks += [tower, cap, lamp]
    elif kind == 2:  # volcano
        a = pyglet.shapes.Triangle(520, 522, 690, 522, 610, 400, color=(76, 47, 49), batch=self.batch, group=self.track_group)
        lava = pyglet.shapes.Triangle(590, 500, 630, 500, 610, 455, color=(248, 91, 43), batch=self.batch, group=self.track_group)
        self._race_shapes += [a, lava]; self._extreme_landmarks += [a, lava]
    elif kind == 3:  # torii
        pillars = [pyglet.shapes.Rectangle(72, 392, 13, 105, color=(173, 45, 67), batch=self.batch, group=self.track_group), pyglet.shapes.Rectangle(157, 392, 13, 105, color=(173, 45, 67), batch=self.batch, group=self.track_group)]
        beam = pyglet.shapes.Rectangle(54, 474, 135, 15, color=(211, 59, 85), batch=self.batch, group=self.track_group)
        self._race_shapes += pillars + [beam]; self._extreme_landmarks += pillars + [beam]
    elif kind == 4:  # planet
        planet = pyglet.shapes.Circle(684, 455, 58, color=_dark(edge, 30), batch=self.batch, group=self.track_group); planet.opacity = 175
        moon = pyglet.shapes.Circle(625, 505, 14, color=_bright(edge, 50), batch=self.batch, group=self.track_group)
        self._race_shapes += [planet, moon]; self._extreme_landmarks += [planet, moon]
    elif kind == 5:  # bridge
        deck = pyglet.shapes.Rectangle(485, 453, 265, 13, color=_dark(edge, 45), batch=self.batch, group=self.track_group)
        self._race_shapes.append(deck); self._extreme_landmarks.append(deck)
        for x in (510, 710):
            p = pyglet.shapes.Rectangle(x, 395, 10, 105, color=_dark(edge, 50), batch=self.batch, group=self.track_group)
            self._race_shapes.append(p); self._extreme_landmarks.append(p)
    elif kind == 6:  # factory
        plant = pyglet.shapes.Rectangle(545, 404, 178, 87, color=(48, 54, 65), batch=self.batch, group=self.track_group)
        self._race_shapes.append(plant); self._extreme_landmarks.append(plant)
        for x in (565, 625, 685):
            stack = pyglet.shapes.Rectangle(x, 480, 17, 72, color=(62, 65, 72), batch=self.batch, group=self.track_group)
            self._race_shapes.append(stack); self._extreme_landmarks.append(stack)
    else:  # grandstand
        stand = pyglet.shapes.Rectangle(36, 424, 230, 73, color=(37, 48, 68), batch=self.batch, group=self.track_group)
        roof = pyglet.shapes.Rectangle(25, 490, 252, 12, color=_bright(edge, 5), batch=self.batch, group=self.track_group)
        self._race_shapes += [stand, roof]; self._extreme_landmarks += [stand, roof]


def _build_track(self):
    _ORIGINALS["_build_track"](self)
    _clear_extreme_track_fx(self)
    track = kx.TRACKS[self.selected_track]
    edge = track["edge"]

    # Low-cost cinematic color grading: depth haze, horizon bloom and vignette.
    haze = pyglet.shapes.Rectangle(0, 392, EngineGlobals.width, 118, color=_bright(track["grass"], 28), batch=self.batch, group=self.track_group)
    haze.opacity = 31
    bloom = pyglet.shapes.Rectangle(0, 463, EngineGlobals.width, 38, color=_bright(edge, 45), batch=self.batch, group=self.track_group)
    bloom.opacity = 18
    left = pyglet.shapes.Rectangle(0, 0, 38, EngineGlobals.height, color=(1, 3, 8), batch=self.batch, group=self.track_group); left.opacity = 72
    right = pyglet.shapes.Rectangle(EngineGlobals.width - 38, 0, 38, EngineGlobals.height, color=(1, 3, 8), batch=self.batch, group=self.track_group); right.opacity = 72
    self._race_shapes += [haze, bloom, left, right]
    self._extreme_atmosphere += [haze, bloom]

    # Floodlights and road-side glow pools.
    for i in range(12):
        x = 42 + (i * 67) % 716
        y = 80 + (i * 109) % 390
        pole = pyglet.shapes.Rectangle(x, y, 3, 32, color=(96, 107, 124), batch=self.batch, group=self.track_group)
        lamp = pyglet.shapes.Circle(x + 1.5, y + 33, 6, color=_bright(edge, 52), batch=self.batch, group=self.track_group)
        lamp.opacity = 115 + (i % 3) * 35
        self._race_shapes += [pole, lamp]
        self._extreme_atmosphere.append(lamp)

    _add_landmark(self, track, self.selected_track % 8)

    # Weather specks: rain/ash/dust/stars depending on circuit index.
    weather_color = ((137, 200, 233), (195, 187, 169), (231, 116, 89), (205, 218, 243))[self.selected_track % 4]
    for i in range(34):
        s = pyglet.shapes.Circle(
            self._su_rng.randrange(12, max(13, EngineGlobals.width - 12)),
            self._su_rng.randrange(76, max(77, EngineGlobals.height - 65)),
            1 + (i % 3 == 0), color=weather_color,
            batch=self.batch, group=self.kart_group,
        )
        s.opacity = 45 + (i * 17) % 80
        self._race_shapes.append(s)
        self._extreme_atmosphere.append(s)

    # Speed streaks wake up only at racing speed.
    for i in range(22):
        line = pyglet.shapes.Rectangle(
            20 + (i * 71) % 760, 60 + (i * 53) % 430,
            2, 16 + (i % 4) * 7, color=_bright(edge, 42),
            batch=self.batch, group=self.kart_group,
        )
        line.opacity = 0
        self._race_shapes.append(line); self._extreme_speed_lines.append(line)

    # Energy/overdrive HUD.
    self._ultra_energy_bg = pyglet.shapes.Rectangle(18, 68, 170, 9, color=(27, 34, 48), batch=self.batch, group=self.ui_group)
    self._ultra_energy_bar = pyglet.shapes.Rectangle(18, 68, 170, 9, color=(77, 235, 205), batch=self.batch, group=self.ui_group)
    self._race_shapes += [self._ultra_energy_bg, self._ultra_energy_bar]
    energy_label = pyglet.text.Label(
        "OVERDRIVE", x=18, y=82, font_size=7, weight=pyglet.text.Weight.BOLD,
        color=(145, 224, 255, 255), batch=self.batch, group=self.ui_group,
    )
    controls = pyglet.text.Label(
        "SHIFT / GAMEPAD RB = OVERDRIVE", x=EngineGlobals.width - 15, y=82,
        anchor_x="right", font_size=7, color=(239, 151, 226, 255),
        batch=self.batch, group=self.ui_group,
    )
    self._race_labels += [energy_label, controls]


def _create_racer_visuals(self, racer):
    _ORIGINALS["_create_racer_visuals"](self, racer)
    if not hasattr(racer, "su_body"):
        return
    color = racer.su_body.color
    racer.sx_front = pyglet.shapes.Rectangle(0, 0, 15, 35, color=_bright(color, 18), batch=self.batch, group=self.kart_group)
    racer.sx_front.anchor_position = (7.5, 17.5)
    racer.sx_rear = pyglet.shapes.Rectangle(0, 0, 10, 39, color=_dark(color, 42), batch=self.batch, group=self.kart_group)
    racer.sx_rear.anchor_position = (5, 19.5)
    racer.sx_tails = [pyglet.shapes.Circle(0, 0, 2.8, color=(255, 68, 76), batch=self.batch, group=self.kart_group) for _ in range(2)]
    racer.sx_exhaust = [pyglet.shapes.Circle(0, 0, 2.2, color=(171, 185, 201), batch=self.batch, group=self.kart_group) for _ in range(2)]
    racer.sx_underglow = pyglet.shapes.Circle(0, 0, 18, color=_bright(color, 55), batch=self.batch, group=self.kart_group)
    racer.sx_underglow.opacity = 48
    racer.sx_shapes = [racer.sx_underglow, racer.sx_rear, racer.sx_front, *racer.sx_tails, *racer.sx_exhaust]


def _update_racer_visuals(self, racer):
    _ORIGINALS["_update_racer_visuals"](self, racer)
    if not hasattr(racer, "sx_front"):
        return
    y_ratio = 1.0 - racer.y / max(1.0, float(EngineGlobals.height))
    perspective = max(0.70, min(1.28, 0.76 + y_ratio * 0.48))
    angle_deg = -math.degrees(racer.angle)
    hop = 8.0 if racer.hop_timer > 0 else 0.0

    # Intensify the existing Super Ultra depth cue to mimic the ad's low camera.
    for shape in (racer.su_underbody, racer.su_body, racer.su_hood, racer.su_gloss, racer.su_spoiler):
        shape.width *= 0.92 + perspective * 0.10
        shape.height *= 0.92 + perspective * 0.10
    for shape in (*racer.su_wheels, *racer.su_rims, *racer.su_headlights, racer.su_cockpit):
        shape.radius *= 0.92 + perspective * 0.10

    def pos(ox, oy):
        dx, dy = self._rotate_local(ox * perspective, oy * perspective, racer.angle)
        return racer.x + dx, racer.y + dy + hop

    for shape, w, h, anchor, ox, oy in (
        (racer.sx_front, 15, 35, (7.5, 17.5), 22, 0),
        (racer.sx_rear, 10, 39, (5, 19.5), -23, 0),
    ):
        shape.width = w * perspective; shape.height = h * perspective
        shape.anchor_position = (anchor[0] * perspective, anchor[1] * perspective)
        shape.rotation = angle_deg; shape.position = pos(ox, oy)
    for lamp, oy in zip(racer.sx_tails, (-10, 10)):
        lamp.position = pos(-27, oy); lamp.radius = 2.6 * perspective
    for exhaust, oy in zip(racer.sx_exhaust, (-6, 6)):
        exhaust.position = pos(-31, oy); exhaust.radius = 2.0 * perspective
    racer.sx_underglow.position = pos(0, 0); racer.sx_underglow.radius = 18 * perspective
    racer.sx_underglow.opacity = 95 if racer.boost_timer > 0 or getattr(self, "ultra_overdrive", False) and racer is self.player else 42


def _destroy_racer_visuals(self, racer):
    for shape in getattr(racer, "sx_shapes", []):
        try: shape.delete()
        except Exception: pass
    racer.sx_shapes = []
    _ORIGINALS["_destroy_racer_visuals"](self, racer)


def _start_race(self):
    self.ultra_energy = 100.0
    self.ultra_overdrive = False
    _ORIGINALS["_start_race"](self)


def _update_player(self, dt):
    _ORIGINALS["_update_player"](self, dt)
    if self.player is None or self.player.finished:
        return
    keys = EngineGlobals.keys
    k = pyglet.window.key
    requested = bool(keys[k.LSHIFT]) or bool(keys[k.RSHIFT]) or (5 in self._extreme_pad_buttons)
    self.ultra_overdrive = bool(requested and self.player.lap >= 1 and self.ultra_energy > 0.5)
    if self.ultra_overdrive:
        self.ultra_energy = max(0.0, self.ultra_energy - 0.105 * float(dt))
        self.player.boost_timer = max(self.player.boost_timer, 5.0)
        self.player.speed = min(self.BOOST_MAX_SPEED + 1.35, self.player.speed + 0.035 * float(dt))
        if hasattr(self, "_mechanic_message"):
            self._mechanic_message = "OVERDRIVE"
            self._mechanic_message_timer = max(getattr(self, "_mechanic_message_timer", 0.0), 4.0)
    elif self.player.boost_timer > 0:
        self.ultra_energy = min(100.0, self.ultra_energy + 0.018 * float(dt))


def _animate_extreme(self, dt):
    if self.state not in (self.STATE_RACE, self.STATE_FINISH, self.STATE_COUNTDOWN):
        return
    phase = self.race_time * 0.035
    for i, shape in enumerate(getattr(self, "_extreme_atmosphere", [])):
        if isinstance(shape, pyglet.shapes.Circle):
            shape.opacity = int(max(25, min(175, 75 + 45 * math.sin(phase + i * 0.43))))
            if shape.radius <= 3:
                shape.y -= (0.20 + (i % 4) * 0.06) * float(dt)
                if shape.y < 74: shape.y = EngineGlobals.height - 72
    speed = abs(self.player.speed) if self.player is not None else 0.0
    streak = max(0.0, min(1.0, (speed - 4.4) / 4.0))
    for i, line in enumerate(getattr(self, "_extreme_speed_lines", [])):
        line.opacity = int(185 * streak)
        if streak > 0:
            line.y -= (1.8 + (i % 5) * 0.45) * float(dt) * streak
            if line.y < 55: line.y = EngineGlobals.height - 78
    if hasattr(self, "_ultra_energy_bar"):
        self._ultra_energy_bar.width = 170 * max(0.0, min(1.0, self.ultra_energy / 100.0))
        self._ultra_energy_bar.color = (74, 239, 203) if self.ultra_energy > 50 else (246, 190, 71) if self.ultra_energy > 20 else (242, 73, 87)


def _update(self, dt):
    if self.state == getattr(self, "STATE_ULTRA_PAUSE", "ultra_pause"):
        self._extreme_nav_cooldown = max(0.0, self._extreme_nav_cooldown - float(dt))
        return
    _ORIGINALS["update"](self, dt)
    self._extreme_nav_cooldown = max(0.0, self._extreme_nav_cooldown - float(dt))
    if self.active:
        _animate_extreme(self, float(dt))


def _build_finish_ui(self):
    _ORIGINALS["_build_finish_ui"](self)
    place = self.player.finish_order or self._current_place()
    if self._finish_labels:
        self._finish_labels[0].text = "SUPER ULTRA FINISH!"
    if len(self._finish_labels) > 1:
        self._finish_labels[1].text = "{} finished {} of 12".format(self.player.character, place)
    if len(self._finish_labels) > 2 and self.ultra_mode == "grand_prix":
        self._finish_labels[2].text = "{} // RACE {}/5 // {:.1f}s".format(CUPS[self.selected_cup], self.ultra_gp_race + 1, self.race_time / 60.0)
    if len(self._finish_labels) > 3:
        self._finish_labels[3].text = "Enter: next race  •  Esc: Super Ultra menu" if self.ultra_mode == "grand_prix" else "Enter: rematch  •  Esc: Super Ultra menu"


def _show_pause(self):
    self.state = self.STATE_ULTRA_PAUSE
    self._pause_shapes = []
    self._pause_labels = []
    box = pyglet.shapes.BorderedRectangle(205, 190, 390, 205, border=2, color=(10, 17, 32), border_color=(72, 217, 255), batch=self.batch, group=self.ui_group)
    box.opacity = 242
    self._pause_shapes.append(box)
    self._pause_labels += [
        pyglet.text.Label("PAUSED", x=400, y=340, anchor_x="center", font_size=29, weight=pyglet.text.Weight.BOLD, color=(246, 249, 255, 255), batch=self.batch, group=self.ui_group),
        pyglet.text.Label("ESC resume   //   Q Super Ultra menu", x=400, y=275, anchor_x="center", font_size=11, color=(157, 216, 244, 255), batch=self.batch, group=self.ui_group),
    ]


def _hide_pause(self):
    for x in getattr(self, "_pause_shapes", []) + getattr(self, "_pause_labels", []):
        try: x.delete()
        except Exception: pass
    self._pause_shapes = []; self._pause_labels = []


def _exit_to_ultra_home(self):
    _hide_pause(self)
    self._clear_finish_ui()
    self._destroy_race()
    self.ultra_home_choice = 0
    self._build_ultra_home()


def _on_key_press(self, symbol, modifiers):
    if not self.active:
        return pyglet.event.EVENT_UNHANDLED
    k = pyglet.window.key

    if self.state == self.STATE_ULTRA_HOME:
        if symbol in (k.UP, k.LEFT): self.ultra_home_choice = (self.ultra_home_choice - 1) % 3
        elif symbol in (k.DOWN, k.RIGHT): self.ultra_home_choice = (self.ultra_home_choice + 1) % 3
        elif symbol in (k.ENTER, k.RETURN):
            if self.ultra_home_choice == 2:
                self.stop(); self.on_exit_to_menu and self.on_exit_to_menu(); return pyglet.event.EVENT_HANDLED
            self.ultra_mode = "quick" if self.ultra_home_choice == 0 else "grand_prix"
            self.selected_character = 0; self._build_character_select(); return pyglet.event.EVENT_HANDLED
        elif symbol == k.ESCAPE:
            self.stop(); self.on_exit_to_menu and self.on_exit_to_menu(); return pyglet.event.EVENT_HANDLED
        self._build_ultra_home(); return pyglet.event.EVENT_HANDLED

    if self.state == self.STATE_CHARACTER:
        if symbol == k.ESCAPE: self._build_ultra_home(); return pyglet.event.EVENT_HANDLED
        if symbol == k.LEFT: self.selected_character = (self.selected_character - 1) % 24
        elif symbol == k.RIGHT: self.selected_character = (self.selected_character + 1) % 24
        elif symbol == k.UP: self.selected_character = (self.selected_character - 6) % 24
        elif symbol == k.DOWN: self.selected_character = (self.selected_character + 6) % 24
        else: return _ORIGINALS["on_key_press"](self, symbol, modifiers)
        self._refresh_character_highlight(); return pyglet.event.EVENT_HANDLED

    if self.state == self.STATE_COLOR and symbol == k.ESCAPE:
        self._build_character_select(); return pyglet.event.EVENT_HANDLED

    if self.state == self.STATE_EMBLEM:
        if symbol == k.ESCAPE:
            self.state = self.STATE_COLOR; self._build_color_select(); return pyglet.event.EVENT_HANDLED
        if symbol in (k.ENTER, k.RETURN) and self.ultra_mode == "grand_prix":
            self.selected_cup = 0; self._build_cup_select(); return pyglet.event.EVENT_HANDLED

    if self.state == self.STATE_ULTRA_CUP:
        if symbol in (k.LEFT, k.UP): self.selected_cup = (self.selected_cup - 1) % 10
        elif symbol in (k.RIGHT, k.DOWN): self.selected_cup = (self.selected_cup + 1) % 10
        elif symbol in (k.ENTER, k.RETURN):
            self.ultra_gp_race = 0; self.selected_track = self.selected_cup * 5; self._start_race(); return pyglet.event.EVENT_HANDLED
        elif symbol == k.ESCAPE:
            self.state = self.STATE_EMBLEM; self._build_emblem_select(); return pyglet.event.EVENT_HANDLED
        self._build_cup_select(); return pyglet.event.EVENT_HANDLED

    if self.state == getattr(self, "STATE_TRACK", "track"):
        if symbol == k.ESCAPE:
            self.state = self.STATE_EMBLEM; self._build_emblem_select(); return pyglet.event.EVENT_HANDLED
        if symbol == k.LEFT: self.selected_track = (self.selected_track - 1) % 50
        elif symbol == k.RIGHT: self.selected_track = (self.selected_track + 1) % 50
        elif symbol == k.UP: self.selected_track = (self.selected_track - 2) % 50
        elif symbol == k.DOWN: self.selected_track = (self.selected_track + 2) % 50
        elif symbol == k.PAGEUP: self.selected_track = (self.selected_track - 10) % 50
        elif symbol == k.PAGEDOWN: self.selected_track = (self.selected_track + 10) % 50
        else: return _ORIGINALS["on_key_press"](self, symbol, modifiers)
        self._refresh_track_highlight(); return pyglet.event.EVENT_HANDLED

    if self.state == self.STATE_ULTRA_PAUSE:
        if symbol in (k.ESCAPE, k.ENTER, k.RETURN):
            _hide_pause(self); self.state = self.STATE_RACE; return pyglet.event.EVENT_HANDLED
        if symbol == k.Q:
            _exit_to_ultra_home(self); return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_HANDLED

    if self.state == self.STATE_RACE and symbol == k.ESCAPE:
        _show_pause(self); return pyglet.event.EVENT_HANDLED

    if self.state == self.STATE_FINISH:
        if symbol == k.ESCAPE:
            _exit_to_ultra_home(self); return pyglet.event.EVENT_HANDLED
        if symbol in (k.ENTER, k.RETURN) and self.ultra_mode == "grand_prix":
            if self.ultra_gp_race < 4:
                self.ultra_gp_race += 1
                self.selected_track = self.selected_cup * 5 + self.ultra_gp_race
                self._start_race()
            else:
                _exit_to_ultra_home(self)
            return pyglet.event.EVENT_HANDLED

    return _ORIGINALS["on_key_press"](self, symbol, modifiers)


def _attach_extreme_controllers(self):
    if self._extreme_joysticks:
        return
    try:
        for joystick in pyglet.input.get_joysticks():
            try:
                joystick.open(); joystick.push_handlers(self); self._extreme_joysticks.append(joystick)
            except Exception:
                pass
    except Exception:
        pass


def _detach_extreme_controllers(self):
    for joystick in self._extreme_joysticks:
        try: joystick.remove_handlers(self)
        except Exception: pass
    self._extreme_joysticks = []
    self._extreme_pad_buttons.clear()


def _menu_pad_key(self, symbol):
    if self._extreme_nav_cooldown > 0:
        return
    self._on_key_press(symbol, 0)
    self._extreme_nav_cooldown = 10.0


def _on_joyaxis_motion(self, joystick, axis, value):
    if not self.active: return
    axis = str(axis).lower(); value = float(value)
    k = pyglet.window.key
    if axis == "x":
        self._extreme_axis_x = value
        EngineGlobals.keys[k.LEFT] = value < -0.28
        EngineGlobals.keys[k.RIGHT] = value > 0.28
        if self.state not in (self.STATE_RACE, self.STATE_COUNTDOWN, self.STATE_FINISH, self.STATE_ULTRA_PAUSE) and abs(value) > 0.72:
            _menu_pad_key(self, k.LEFT if value < 0 else k.RIGHT)
    elif axis == "y" and self.state not in (self.STATE_RACE, self.STATE_COUNTDOWN, self.STATE_FINISH, self.STATE_ULTRA_PAUSE) and abs(value) > 0.72:
        _menu_pad_key(self, k.UP if value < 0 else k.DOWN)


def _on_joyhat_motion(self, joystick, x, y):
    if not self.active: return
    k = pyglet.window.key
    if x: _menu_pad_key(self, k.LEFT if x < 0 else k.RIGHT)
    elif y: _menu_pad_key(self, k.DOWN if y < 0 else k.UP)


def _on_joybutton_press(self, joystick, button):
    if not self.active: return
    button = int(button); self._extreme_pad_buttons.add(button); k = pyglet.window.key
    if self.state in (self.STATE_RACE, self.STATE_COUNTDOWN):
        if button in (0, 7): EngineGlobals.keys[k.UP] = True
        elif button in (1, 6): EngineGlobals.keys[k.DOWN] = True
        elif button in (2, 4): EngineGlobals.keys[k.SPACE] = True; self._on_key_press(k.SPACE, 0)
        elif button in (8, 9): self._on_key_press(k.ESCAPE, 0)
    else:
        if button in (0, 1): self._on_key_press(k.ENTER, 0)
        elif button in (6, 8, 9): self._on_key_press(k.ESCAPE, 0)


def _on_joybutton_release(self, joystick, button):
    button = int(button); self._extreme_pad_buttons.discard(button); k = pyglet.window.key
    if button in (0, 7): EngineGlobals.keys[k.UP] = False
    elif button in (1, 6): EngineGlobals.keys[k.DOWN] = False
    elif button in (2, 4):
        EngineGlobals.keys[k.SPACE] = False
        try: self.on_key_release(k.SPACE, 0)
        except Exception: pass


def install_extreme_super_ultra():
    """Finish the Super Ultra-only upgrade without touching Mode 7/N64."""
    global _INSTALLED
    if _INSTALLED:
        return
    _add_missing_drivers()
    _fill_to_fifty_tracks()
    assert len(km.CHARACTERS) == 24
    assert len(kx.TRACKS) == 50

    cls = km.KartsMode
    for name in (
        "__init__", "start", "stop", "_build_character_select",
        "_refresh_character_highlight", "_build_track_select",
        "_refresh_track_highlight", "_build_track", "_create_racer_visuals",
        "_update_racer_visuals", "_destroy_racer_visuals", "_start_race",
        "_update_player", "update", "_build_finish_ui", "on_key_press",
    ):
        _ORIGINALS[name] = getattr(cls, name)

    cls.__init__ = _extreme_init
    cls.start = _extreme_start
    cls.stop = _extreme_stop
    cls._build_ultra_home = _build_ultra_home
    cls._build_character_select = _build_character_select
    cls._refresh_character_highlight = _refresh_character_highlight
    cls._build_track_select = _build_track_select
    cls._refresh_track_highlight = _refresh_track_highlight
    cls._build_cup_select = _build_cup_select
    cls._build_track = _build_track
    cls._create_racer_visuals = _create_racer_visuals
    cls._update_racer_visuals = _update_racer_visuals
    cls._destroy_racer_visuals = _destroy_racer_visuals
    cls._start_race = _start_race
    cls._update_player = _update_player
    cls.update = _update
    cls._build_finish_ui = _build_finish_ui
    cls.on_key_press = _on_key_press
    cls._attach_extreme_controllers = _attach_extreme_controllers
    cls._detach_extreme_controllers = _detach_extreme_controllers
    cls.on_joyaxis_motion = _on_joyaxis_motion
    cls.on_joyhat_motion = _on_joyhat_motion
    cls.on_joybutton_press = _on_joybutton_press
    cls.on_joybutton_release = _on_joybutton_release
    _INSTALLED = True
