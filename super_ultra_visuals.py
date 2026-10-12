"""Extreme HD/cinematic visual pass for standalone Super Ultra Kenny Kart.

Everything here patches SuperUltraKart only.  The Mode 7/N64 stack is never
imported, subclassed, or modified.
"""

import math
import random

import pyglet

from engineglobals import EngineGlobals
from super_ultra_kart import SuperUltraKart


_ORIGINALS = {}
_INSTALLED = False


def _keep(self, *items):
    self.race_items.extend(items)
    return items


def _landmark(self, name, theme, hz):
    """Build a large readable skyline landmark for the current theme."""
    w = EngineGlobals.width
    accent = theme["accent"]
    dark = self._dark(theme["sky_bottom"], 48)
    items = []

    if name == "SKYLINE":
        tower = pyglet.shapes.Rectangle(w - 175, hz, 46, 190, color=dark, batch=self.batch, group=self.world)
        cap = pyglet.shapes.Triangle(w - 175, hz + 190, w - 129, hz + 190, w - 152, hz + 245, color=dark, batch=self.batch, group=self.world)
        mast = pyglet.shapes.Rectangle(w - 155, hz + 235, 6, 70, color=accent, batch=self.batch, group=self.world)
        mast.opacity = 185
        items += [tower, cap, mast]
    elif name == "SILO":
        body = pyglet.shapes.Rectangle(70, hz, 72, 155, color=dark, batch=self.batch, group=self.world)
        dome = pyglet.shapes.Circle(106, hz + 155, 36, color=self._light(dark, 14), batch=self.batch, group=self.world)
        stripe = pyglet.shapes.Rectangle(78, hz + 70, 56, 10, color=accent, batch=self.batch, group=self.world)
        stripe.opacity = 145
        items += [body, dome, stripe]
    elif name == "BRIDGE":
        deck = pyglet.shapes.Rectangle(75, hz + 72, w - 150, 16, color=dark, batch=self.batch, group=self.world)
        p1 = pyglet.shapes.Rectangle(145, hz, 22, 155, color=dark, batch=self.batch, group=self.world)
        p2 = pyglet.shapes.Rectangle(w - 167, hz, 22, 155, color=dark, batch=self.batch, group=self.world)
        l1 = pyglet.shapes.Rectangle(151, hz + 34, 7, 103, color=accent, batch=self.batch, group=self.world)
        l2 = pyglet.shapes.Rectangle(w - 160, hz + 34, 7, 103, color=accent, batch=self.batch, group=self.world)
        l1.opacity = l2.opacity = 100
        items += [deck, p1, p2, l1, l2]
    elif name == "TORII":
        left = pyglet.shapes.Rectangle(92, hz, 24, 175, color=dark, batch=self.batch, group=self.world)
        right = pyglet.shapes.Rectangle(218, hz, 24, 175, color=dark, batch=self.batch, group=self.world)
        beam = pyglet.shapes.Rectangle(70, hz + 145, 194, 22, color=dark, batch=self.batch, group=self.world)
        crown = pyglet.shapes.Rectangle(56, hz + 178, 222, 13, color=accent, batch=self.batch, group=self.world)
        crown.opacity = 145
        items += [left, right, beam, crown]
    elif name == "PLANET":
        planet = pyglet.shapes.Circle(w - 132, hz + 128, 78, color=self._light(theme["sky_bottom"], 38), batch=self.batch, group=self.world)
        planet.opacity = 215
        ring = pyglet.shapes.Ellipse(w - 132, hz + 128, 124, 24, color=accent, batch=self.batch, group=self.world)
        ring.opacity = 95
        moon = pyglet.shapes.Circle(w - 260, hz + 200, 16, color=(205, 220, 244), batch=self.batch, group=self.world)
        items += [planet, ring, moon]
    elif name == "VOLCANO":
        mountain = pyglet.shapes.Triangle(60, hz, 360, hz, 226, hz + 220, color=dark, batch=self.batch, group=self.world)
        lava = pyglet.shapes.Triangle(190, hz + 146, 258, hz + 146, 226, hz + 210, color=accent, batch=self.batch, group=self.world)
        lava.opacity = 175
        items += [mountain, lava]
    elif name == "MESA":
        mesa = pyglet.shapes.Rectangle(65, hz, 240, 112, color=dark, batch=self.batch, group=self.world)
        top = pyglet.shapes.Rectangle(92, hz + 110, 185, 35, color=self._light(dark, 9), batch=self.batch, group=self.world)
        ridge = pyglet.shapes.Rectangle(112, hz + 143, 142, 6, color=accent, batch=self.batch, group=self.world)
        ridge.opacity = 110
        items += [mesa, top, ridge]
    elif name == "FACTORY":
        main = pyglet.shapes.Rectangle(w - 315, hz, 245, 112, color=dark, batch=self.batch, group=self.world)
        items.append(main)
        for i, hh in enumerate((168, 205, 145)):
            stack = pyglet.shapes.Rectangle(w - 285 + i * 72, hz + 70, 22, hh, color=self._dark(dark, 8), batch=self.batch, group=self.world)
            lamp = pyglet.shapes.Circle(w - 274 + i * 72, hz + 76 + hh, 6, color=accent, batch=self.batch, group=self.world)
            lamp.opacity = 155
            items += [stack, lamp]
    elif name == "LIGHTHOUSE":
        tower = pyglet.shapes.Triangle(95, hz, 185, hz, 154, hz + 205, color=dark, batch=self.batch, group=self.world)
        room = pyglet.shapes.Rectangle(128, hz + 188, 52, 30, color=self._light(dark, 10), batch=self.batch, group=self.world)
        lamp = pyglet.shapes.Circle(154, hz + 204, 10, color=accent, batch=self.batch, group=self.world)
        lamp.opacity = 225
        beam = pyglet.shapes.Triangle(164, hz + 204, w - 60, hz + 260, w - 60, hz + 215, color=accent, batch=self.batch, group=self.world)
        beam.opacity = 28
        items += [tower, room, lamp, beam]
    else:
        head = pyglet.shapes.Circle(w - 150, hz + 135, 72, color=dark, batch=self.batch, group=self.world)
        ear1 = pyglet.shapes.Triangle(w - 214, hz + 172, w - 170, hz + 188, w - 192, hz + 240, color=dark, batch=self.batch, group=self.world)
        ear2 = pyglet.shapes.Triangle(w - 130, hz + 188, w - 86, hz + 172, w - 108, hz + 240, color=dark, batch=self.batch, group=self.world)
        snout = pyglet.shapes.Ellipse(w - 150, hz + 110, 34, 22, color=self._light(dark, 16), batch=self.batch, group=self.world)
        eye1 = pyglet.shapes.Circle(w - 174, hz + 154, 7, color=accent, batch=self.batch, group=self.world)
        eye2 = pyglet.shapes.Circle(w - 126, hz + 154, 7, color=accent, batch=self.batch, group=self.world)
        items += [head, ear1, ear2, snout, eye1, eye2]

    _keep(self, *items)


def _scene(self):
    _ORIGINALS["_scene"](self)
    w, h = EngineGlobals.width, EngineGlobals.height
    hz = int(h * .455)
    theme = self.track_def["theme"]
    weather = theme["weather"]
    accent = theme["accent"]

    bloom = pyglet.shapes.Rectangle(0, hz - 8, w, 82, color=accent, batch=self.batch, group=self.world)
    bloom.opacity = 24
    haze = pyglet.shapes.Rectangle(0, hz + 14, w, 34, color=self._light(theme["fog"], 22), batch=self.batch, group=self.world)
    haze.opacity = 38
    _keep(self, bloom, haze)

    for i in range(7):
        x = -80 + i * 145
        peak = hz + 70 + ((i * 47 + self.selected_track * 19) % 110)
        mountain = pyglet.shapes.Triangle(
            x, hz, x + 180, hz, x + 88, peak,
            color=self._dark(theme["sky_bottom"], 28 + (i % 2) * 9),
            batch=self.batch, group=self.world,
        )
        mountain.opacity = 165
        self.race_items.append(mountain)

    _landmark(self, theme["landmark"], theme, hz)

    self.su_horizon_lights = []
    for i in range(22):
        x = 18 + i * (w - 36) / 21
        y = hz + 8 + (i % 3) * 7
        outer = pyglet.shapes.Circle(x, y, 5 + (i % 2), color=accent, batch=self.batch, group=self.fx)
        core = pyglet.shapes.Circle(x, y, 2, color=(240, 249, 255), batch=self.batch, group=self.fx)
        outer.opacity = 38
        core.opacity = 145
        self.su_horizon_lights.append((outer, core, i * .31))
        _keep(self, outer, core)

    self.su_weather = []
    wrng = random.Random(9000 + self.selected_track)
    count = 34 if weather in ("storm", "ash", "mist") else 24
    for i in range(count):
        x, y = wrng.randrange(w), wrng.randrange(hz, h)
        if weather == "storm":
            mark = pyglet.shapes.Rectangle(x, y, 2, wrng.randrange(12, 27), color=(155, 190, 225), batch=self.batch, group=self.fx)
            mark.opacity = wrng.randrange(45, 115)
        elif weather == "ash":
            mark = pyglet.shapes.Circle(x, y, wrng.choice((1, 2, 2, 3)), color=(118, 105, 103), batch=self.batch, group=self.fx)
            mark.opacity = wrng.randrange(70, 160)
        else:
            mark = pyglet.shapes.Circle(x, y, wrng.choice((1, 1, 2)), color=self._light(accent, 40), batch=self.batch, group=self.fx)
            mark.opacity = wrng.randrange(40, 130)
        self.su_weather.append((mark, wrng.uniform(.35, 1.05), i * .27))
        self.race_items.append(mark)


def _player_kart(self):
    _ORIGINALS["_player_kart"](self)
    cx = EngineGlobals.width / 2
    c = self._selected()["color"]
    accent = self.track_def["theme"]["accent"]

    underglow = pyglet.shapes.Ellipse(cx, 66, 66, 13, color=accent, batch=self.batch, group=self.fx)
    underglow.opacity = 42
    pod_l = pyglet.shapes.Rectangle(cx - 61, 77, 24, 28, color=self._dark(c, 28), batch=self.batch, group=self.carg)
    pod_r = pyglet.shapes.Rectangle(cx + 37, 77, 24, 28, color=self._dark(c, 28), batch=self.batch, group=self.carg)
    splitter = pyglet.shapes.Rectangle(cx - 47, 74, 94, 5, color=(24, 29, 38), batch=self.batch, group=self.carg)
    windshield = pyglet.shapes.Ellipse(cx, 108, 24, 14, color=(35, 72, 104), batch=self.batch, group=self.carg)
    windshield.opacity = 235
    glass_glint = pyglet.shapes.Ellipse(cx - 6, 114, 10, 4, color=(193, 235, 255), batch=self.batch, group=self.carg)
    glass_glint.opacity = 145
    hood_line = pyglet.shapes.Rectangle(cx - 4, 108, 8, 31, color=self._light(c, 64), batch=self.batch, group=self.carg)
    hood_line.opacity = 150
    spoiler = pyglet.shapes.Rectangle(cx - 57, 74, 114, 8, color=self._dark(c, 55), batch=self.batch, group=self.carg)
    tail_l = pyglet.shapes.Circle(cx - 37, 75, 5, color=(255, 55, 68), batch=self.batch, group=self.fx)
    tail_r = pyglet.shapes.Circle(cx + 37, 75, 5, color=(255, 55, 68), batch=self.batch, group=self.fx)
    head_l = pyglet.shapes.Circle(cx - 27, 128, 5, color=(190, 235, 255), batch=self.batch, group=self.fx)
    head_r = pyglet.shapes.Circle(cx + 27, 128, 5, color=(190, 235, 255), batch=self.batch, group=self.fx)
    beam_l = pyglet.shapes.Triangle(cx - 34, 130, cx - 19, 130, cx - 88, 247, color=(116, 214, 255), batch=self.batch, group=self.fx)
    beam_r = pyglet.shapes.Triangle(cx + 19, 130, cx + 34, 130, cx + 88, 247, color=(116, 214, 255), batch=self.batch, group=self.fx)
    beam_l.opacity = beam_r.opacity = 18

    extra = [underglow, pod_l, pod_r, splitter, windshield, glass_glint, hood_line, spoiler, tail_l, tail_r, head_l, head_r, beam_l, beam_r]
    self.player_shapes.extend(extra)
    self.race_items.extend(extra)
    for s in extra:
        if isinstance(s, pyglet.shapes.Triangle):
            self.player_base.append((s, (s.x, s.y, s.x2, s.y2, s.x3, s.y3)))
        else:
            self.player_base.append((s, (getattr(s, "x", 0), getattr(s, "y", 0))))

    self.su_player_rims = []
    for ox in (-55, -31, 31, 55):
        rim = pyglet.shapes.Circle(cx + ox, 66, 5, color=(139, 166, 191), batch=self.batch, group=self.carg)
        hub = pyglet.shapes.Circle(cx + ox, 66, 2, color=(220, 236, 246), batch=self.batch, group=self.carg)
        self.su_player_rims += [rim, hub]
        self.player_shapes += [rim, hub]
        self.race_items += [rim, hub]
        self.player_base += [(rim, (rim.x, rim.y)), (hub, (hub.x, hub.y))]

    self.su_driver_sprite = None
    art = self._selected().get("art")
    if art:
        try:
            image = pyglet.resource.image(art)
            sprite = pyglet.sprite.Sprite(image, batch=self.batch, group=self.carg)
            sprite.scale = min(2.0, 37.0 / max(1.0, float(max(image.width, image.height))))
            sprite.x = cx - sprite.width / 2
            sprite.y = 94
            self.su_driver_sprite = sprite
            self.race_items.append(sprite)
            self.player_base.append((sprite, (sprite.x, sprite.y)))
        except Exception:
            self.su_driver_sprite = None

    self.su_kart_glow = underglow
    self.su_headlights = (head_l, head_r)
    self.su_taillights = (tail_l, tail_r)


def _rival_setup(self):
    _ORIGINALS["_rival_setup"](self)
    self.su_rival_fx = []
    for rival in self.rivals:
        c = rival.driver["color"]
        canopy = pyglet.shapes.Circle(-900, -900, 3, color=(40, 66, 91), batch=self.batch, group=self.fx)
        spoiler = pyglet.shapes.Rectangle(-900, -900, 1, 1, color=self._dark(c, 48), batch=self.batch, group=self.fx)
        lamp_l = pyglet.shapes.Circle(-900, -900, 2, color=(192, 235, 255), batch=self.batch, group=self.fx)
        lamp_r = pyglet.shapes.Circle(-900, -900, 2, color=(192, 235, 255), batch=self.batch, group=self.fx)
        tail = pyglet.shapes.Circle(-900, -900, 2, color=(255, 67, 74), batch=self.batch, group=self.fx)
        self.su_rival_fx.append((canopy, spoiler, lamp_l, lamp_r, tail))
        self.race_items += [canopy, spoiler, lamp_l, lamp_r, tail]


def _rival_visuals(self, centers, widths, ys):
    _ORIGINALS["_rival_visuals"](self, centers, widths, ys)
    max_draw = self.DRAW_SEGMENTS * self.SEGMENT_LENGTH
    for base, extra, rival in zip(self.rival_items, self.su_rival_fx, self.rivals):
        canopy, spoiler, lamp_l, lamp_r, tail = extra
        visible = bool(base[0].visible)
        for q in extra:
            q.visible = visible
        if not visible:
            continue
        rel = (rival.distance - self.distance) % self.track_length
        idx = int(max(0.0, min(1.0, (max_draw - rel) / max_draw)) * (self.DRAW_SEGMENTS - 1))
        p = (idx + 1) / self.DRAW_SEGMENTS
        sc = max(.13, p ** 1.4)
        x = centers[idx] + rival.lane * widths[idx] * .70
        y = ys[idx]
        canopy.position = (x, y + 17 * sc)
        canopy.radius = max(2, 6 * sc)
        spoiler.width = max(3, 31 * sc)
        spoiler.height = max(1, 4 * sc)
        spoiler.position = (x - spoiler.width / 2, y + 7 * sc)
        for lamp, off in ((lamp_l, -9), (lamp_r, 9)):
            lamp.position = (x + off * sc, y + 15 * sc)
            lamp.radius = max(1, 2.2 * sc)
        tail.position = (x, y + 7 * sc)
        tail.radius = max(1, 2.1 * sc)
        tail.opacity = 230 if rival.hit > 0 else 120


def _hud(self):
    _ORIGINALS["_hud"](self)
    w, h = EngineGlobals.width, EngineGlobals.height

    top = pyglet.shapes.Rectangle(0, h - 16, w, 16, color=(4, 7, 14), batch=self.batch, group=self.ui)
    bottom = pyglet.shapes.Rectangle(0, 0, w, 8, color=(4, 7, 14), batch=self.batch, group=self.ui)
    top.opacity = bottom.opacity = 150
    self.race_items += [top, bottom]

    for _ in range(60):
        s = pyglet.shapes.Circle(-900, -900, 2, color=(160, 210, 235), batch=self.batch, group=self.fx)
        s.visible = False
        self.particles.append({"s": s, "vx": 0., "vy": 0., "life": 0., "max": 1.})
        self.race_items.append(s)

    self.su_speed_lines = []
    rr = random.Random(2200 + self.selected_track)
    for i in range(18):
        x = rr.choice((rr.randrange(12, 155), rr.randrange(w - 155, w - 12)))
        line = pyglet.shapes.Rectangle(x, -100, rr.choice((2, 2, 3)), rr.randrange(24, 72), color=self.track_def["theme"]["accent"], batch=self.batch, group=self.fx)
        line.opacity = 0
        self.su_speed_lines.append((line, rr.random(), i * 29))
        self.race_items.append(line)

    quality = pyglet.text.Label(
        "SUPER ULTRA // CINEMATIC HD",
        x=w - 16, y=h - 22, anchor_x="right", font_size=7,
        color=(158, 202, 232, 210), batch=self.batch, group=self.ui,
    )
    self.race_items.append(quality)


def _kart_visual(self):
    _ORIGINALS["_kart_visual"](self)
    speed_ratio = min(1.0, max(0.0, abs(self.speed) / max(1.0, self._physics()["over"])))
    phase = self.race_time * .16

    if hasattr(self, "su_kart_glow"):
        glow = 35 + int(105 * speed_ratio)
        if self.overdrive:
            glow = 190
        elif self.boost > 0:
            glow = 145
        self.su_kart_glow.opacity = glow

    for lamp in getattr(self, "su_headlights", ()):
        lamp.opacity = 170 + int(70 * (math.sin(phase) + 1) * .5)
    for lamp in getattr(self, "su_taillights", ()):
        lamp.opacity = 245 if self.hit > 0 or self.drifting else 145

    show_lines = speed_ratio > .63 or self.overdrive
    h = EngineGlobals.height
    for line, offset, seed in getattr(self, "su_speed_lines", []):
        line.visible = show_lines
        if not show_lines:
            line.opacity = 0
            continue
        line.y = 70 + ((self.race_time * (12 + abs(self.speed) * 1.6) + seed) % max(80, h - 150))
        intensity = min(1.0, (speed_ratio - .55) / .45)
        line.opacity = int(38 + 142 * intensity + (55 if self.overdrive else 0))
        line.height = 28 + 62 * intensity

    for outer, core, offset in getattr(self, "su_horizon_lights", []):
        pulse = (math.sin(phase + offset) + 1.0) * .5
        outer.opacity = int(24 + pulse * 54)
        core.opacity = int(105 + pulse * 140)


def _particles(self, dt):
    _ORIGINALS["_particles"](self, dt)
    weather = self.track_def["theme"]["weather"]
    h = EngineGlobals.height
    w = EngineGlobals.width
    for mark, speed, phase in getattr(self, "su_weather", []):
        if weather == "storm":
            mark.y -= (5.5 + speed * 4.0) * dt
            mark.x -= 1.4 * dt
            if mark.y < 250:
                mark.y = h + 30
                mark.x = (mark.x + 173) % w
        elif weather == "ash":
            mark.y -= (.25 + speed * .5) * dt
            mark.x += math.sin(self.race_time * .02 + phase) * .18 * dt
            if mark.y < 260:
                mark.y = h + 10
        else:
            mark.opacity = max(25, min(160, int(82 + math.sin(self.race_time * .025 + phase) * 54)))


def install_super_ultra_visuals():
    """Install the extreme graphics pass on SuperUltraKart only."""
    global _INSTALLED
    if _INSTALLED:
        return

    cls = SuperUltraKart
    for name in (
        "_scene", "_player_kart", "_rival_setup", "_rival_visuals",
        "_hud", "_kart_visual", "_particles",
    ):
        _ORIGINALS[name] = getattr(cls, name)

    cls._scene = _scene
    cls._player_kart = _player_kart
    cls._rival_setup = _rival_setup
    cls._rival_visuals = _rival_visuals
    cls._hud = _hud
    cls._kart_visual = _kart_visual
    cls._particles = _particles
    cls.DRAW_SEGMENTS = 76

    _INSTALLED = True
