"""Character stats and advanced handling for Karts not Farts."""

import math

import pyglet

import karts_mode as km
import karts_expansion as kx
from engineglobals import EngineGlobals


# Ratings are 1-10. Weight is mass/stability rather than a simple "better" score.
# Kenny is intentionally the game's perfect kart: every rating is maxed and his
# tuning avoids the usual heavyweight compromises.
CHARACTER_STATS = {
    "Kenny": {
        "speed": 10, "accel": 10, "turn": 10, "weight": 10, "grip": 10, "boost": 10,
        "trait": "PERFECT — no weaknesses",
    },
    "Theo": {
        "speed": 8, "accel": 6, "turn": 5, "weight": 10, "grip": 7, "boost": 7,
        "trait": "BRUISER — wins contact",
    },
    "Lucinda": {
        "speed": 7, "accel": 9, "turn": 9, "weight": 4, "grip": 10, "boost": 8,
        "trait": "RAIL GRIP — smooth corners",
    },
    "Jackie Flan": {
        "speed": 9, "accel": 7, "turn": 10, "weight": 5, "grip": 8, "boost": 7,
        "trait": "DRIFT ACE — fastest rotation",
    },
    "Levod Burtim": {
        "speed": 10, "accel": 6, "turn": 6, "weight": 8, "grip": 7, "boost": 9,
        "trait": "ROCKET — huge straight-line pace",
    },
    "Pippi": {
        "speed": 7, "accel": 10, "turn": 8, "weight": 3, "grip": 9, "boost": 10,
        "trait": "TURBO BUG — explosive exits",
    },
    "Vesuvius": {
        "speed": 9, "accel": 5, "turn": 4, "weight": 10, "grip": 6, "boost": 8,
        "trait": "TANK — hard to knock around",
    },
}

_ORIGINALS = {}
_INSTALLED = False


def _stats_for_name(name):
    return CHARACTER_STATS.get(name, CHARACTER_STATS["Kenny"])


def _player_stats(self):
    if self.player is not None:
        return _stats_for_name(self.player.character)
    name = km.CHARACTERS[self.selected_character][0]
    return _stats_for_name(name)


def _stats_init(self, *args, **kwargs):
    _ORIGINALS["__init__"](self, *args, **kwargs)
    self.launch_charge = 0.0
    self.launch_early = False
    self.air_trick_armed = False
    self.air_trick_was_airborne = False
    self._stat_detail_label = None
    self._drift_sparks = []


def _build_character_select_stats(self):
    """Seven-character picker with the actual kart specs visible on every card."""
    self._clear_selection_ui()
    self._selection_header("PICK YOUR RACER — STATS CHANGE THE KART")
    self._selection_footer()
    self._character_panels = []

    cols = 4
    xs = (105, 300, 495, 690)
    ys = (363, 197)

    for index, (name, face_color) in enumerate(km.CHARACTERS):
        row = index // cols
        col = index % cols
        x = xs[col]
        y = ys[min(row, 1)]
        stats = _stats_for_name(name)

        panel = pyglet.shapes.Rectangle(
            x - 84, y - 72, 168, 151,
            color=(50, 57, 70), batch=self.batch, group=self.track_group,
        )
        self._selection_shapes.append(panel)
        self._character_panels.append(panel)

        # Reuse the game's existing character art wherever it exists.
        art_file = kx.CHARACTER_ART.get(name)
        loaded_art = False
        if art_file:
            try:
                image = pyglet.resource.image(art_file)
                sprite = pyglet.sprite.Sprite(img=image, batch=self.batch, group=self.ui_group)
                sprite.scale = min(2.4, 64.0 / max(1.0, float(max(image.width, image.height))))
                sprite.x = x - sprite.width / 2
                sprite.y = y + 2 - sprite.height / 2
                self._selection_shapes.append(sprite)
                loaded_art = True
            except Exception:
                loaded_art = False

        if not loaded_art:
            head = pyglet.shapes.Circle(
                x, y + 10, 27, color=face_color, batch=self.batch, group=self.ui_group
            )
            eye_l = pyglet.shapes.Circle(
                x - 9, y + 17, 3, color=(30, 25, 22), batch=self.batch, group=self.ui_group
            )
            eye_r = pyglet.shapes.Circle(
                x + 9, y + 17, 3, color=(30, 25, 22), batch=self.batch, group=self.ui_group
            )
            mouth = pyglet.shapes.Rectangle(
                x - 11, y - 4, 22, 4, color=(92, 38, 42),
                batch=self.batch, group=self.ui_group,
            )
            self._selection_shapes.extend((head, eye_l, eye_r, mouth))

        name_label = pyglet.text.Label(
            name.upper(), x=x, y=y + 61, anchor_x="center",
            font_size=10, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        line1 = pyglet.text.Label(
            "SPD {:>2}  ACC {:>2}  TRN {:>2}".format(
                stats["speed"], stats["accel"], stats["turn"]
            ),
            x=x, y=y - 35, anchor_x="center", font_size=8,
            color=(231, 237, 247, 255), batch=self.batch, group=self.ui_group,
        )
        line2 = pyglet.text.Label(
            "WGT {:>2}  GRP {:>2}  BST {:>2}".format(
                stats["weight"], stats["grip"], stats["boost"]
            ),
            x=x, y=y - 50, anchor_x="center", font_size=8,
            color=(208, 221, 239, 255), batch=self.batch, group=self.ui_group,
        )
        self._selection_labels.extend((name_label, line1, line2))

    self._stat_detail_label = pyglet.text.Label(
        "", x=EngineGlobals.width // 2, y=82, anchor_x="center",
        font_size=11, weight=pyglet.text.Weight.BOLD,
        color=(255, 227, 146, 255), batch=self.batch, group=self.ui_group,
    )
    self._selection_labels.append(self._stat_detail_label)
    self._refresh_character_highlight()


def _refresh_character_highlight_stats(self):
    for index, panel in enumerate(getattr(self, "_character_panels", [])):
        panel.color = (118, 129, 158) if index == self.selected_character else (50, 57, 70)

    if self._stat_detail_label is not None:
        name = km.CHARACTERS[self.selected_character][0]
        stats = _stats_for_name(name)
        self._stat_detail_label.text = "{}  •  {}".format(name.upper(), stats["trait"])


def _configure_player_tuning(self):
    stats = _player_stats(self)
    name = self.player.character if self.player is not None else ""

    # Stat ratings become real physics constants. Kenny intentionally receives
    # best-in-class values everywhere instead of the normal weight tradeoffs.
    speed = stats["speed"]
    accel = stats["accel"]
    turn = stats["turn"]
    grip = stats["grip"]
    boost = stats["boost"]

    self.PLAYER_MAX_SPEED = 5.55 + speed * 0.185
    self.PLAYER_ACCEL = 0.125 + accel * 0.0135
    self.PLAYER_REVERSE_ACCEL = 0.085 + (accel + grip) * 0.0045
    self.STEER_RATE = 0.027 + turn * 0.00255
    self.DRIFT_STEER_RATE = 0.045 + turn * 0.00315
    self.PLAYER_FRICTION = 0.953 + grip * 0.00165
    self.OFFROAD_FRICTION = 0.865 + grip * 0.0061
    self.BOOST_MAX_SPEED = self.PLAYER_MAX_SPEED + 1.45 + boost * 0.075

    if name == "Kenny":
        self.PLAYER_MAX_SPEED = 7.55
        self.PLAYER_ACCEL = 0.275
        self.PLAYER_REVERSE_ACCEL = 0.185
        self.STEER_RATE = 0.054
        self.DRIFT_STEER_RATE = 0.080
        self.PLAYER_FRICTION = 0.973
        self.OFFROAD_FRICTION = 0.936
        self.BOOST_MAX_SPEED = 9.85

    return stats


def _update_player_stats(self, dt):
    p = self.player
    if p is None:
        return

    stats = _configure_player_tuning(self)
    pre_speed = p.speed
    pre_angle = p.angle
    pre_bump = p.bump_cooldown
    pre_drift = p.drift_charge
    pre_boost = p.boost_timer
    was_hopping = p.hop_timer > 0

    _ORIGINALS["_update_player"](self, dt)

    # Character stats modify drift charge speed. High-turn/high-boost characters
    # can reach stronger mini-turbos without changing the controls.
    if p.drifting and p.drift_charge > pre_drift:
        raw_gain = p.drift_charge - pre_drift
        gain_scale = 0.72 + stats["turn"] * 0.025 + stats["boost"] * 0.023
        if p.character == "Kenny":
            gain_scale = 1.38
        p.drift_charge = min(100.0, pre_drift + raw_gain * gain_scale)

    # Grip matters in ordinary high-speed corners too: low-grip karts scrub
    # more speed if the player refuses to drift.
    keys = EngineGlobals.keys
    steering = bool(keys[pyglet.window.key.LEFT]) or bool(keys[pyglet.window.key.RIGHT])
    if steering and not p.drifting and abs(p.speed) > 4.0:
        grip_drag = max(0.0, (11 - stats["grip"]) * 0.00055)
        p.speed *= max(0.90, 1.0 - grip_drag * float(dt))

    # Weight controls contact. Heavy racers keep momentum and shove turd karts;
    # light racers lose more speed but remain better at accel/drift by profile.
    if pre_bump <= 0 < p.bump_cooldown:
        resistance = 0.12 + stats["weight"] * 0.064
        if p.character == "Kenny":
            resistance = 0.88
        lost = abs(pre_speed) - abs(p.speed)
        if lost > 0:
            sign = -1.0 if p.speed < 0 else 1.0
            p.speed = sign * (abs(p.speed) + lost * resistance)
        angle_delta = self._angle_delta(p.angle, pre_angle)
        p.angle -= angle_delta * min(0.82, resistance)

        closest = None
        closest_distance = 999.0
        for ai in self.ai_racers:
            d = math.hypot(p.x - ai.x, p.y - ai.y)
            if d < closest_distance:
                closest = ai
                closest_distance = d
        if closest is not None and closest_distance < 38:
            shove = 0.04 + stats["weight"] * 0.012
            closest.speed *= max(0.73, 1.0 - shove)
            closest.angle += 0.10 if self._angle_delta(closest.angle, p.angle) >= 0 else -0.10
            if stats["weight"] >= 9:
                self._mechanic_message = "HEAVY BUMP!"
                self._mechanic_message_timer = 24.0

    # Better boost stat stretches pad/ring boosts when they are freshly awarded.
    decayed_pre_boost = max(0.0, pre_boost - float(dt))
    if p.boost_timer > decayed_pre_boost + 2.0:
        duration_scale = 0.78 + stats["boost"] * 0.037
        if p.character == "Kenny":
            duration_scale = 1.20
        p.boost_timer *= duration_scale

    # Air tricks: press Space while a ramp hop is already active. The boost
    # fires on landing, rewarding timing without adding a new button.
    if self.air_trick_armed:
        self.air_trick_was_airborne = self.air_trick_was_airborne or was_hopping or p.hop_timer > 0
        if self.air_trick_was_airborne and p.hop_timer <= 0:
            trick_power = 6.5 + stats["boost"] * 0.12
            p.speed = max(p.speed, trick_power)
            p.boost_timer = max(p.boost_timer, 34.0 + stats["boost"] * 3.0)
            self._mechanic_message = "AIR TRICK BOOST!"
            self._mechanic_message_timer = 52.0
            self.air_trick_armed = False
            self.air_trick_was_airborne = False


def _release_drift_stats(self):
    p = self.player
    if p is None or not p.drifting:
        return

    stats = _player_stats(self)
    charge = p.drift_charge
    boost_factor = 0.82 + stats["boost"] * 0.038
    speed_ceiling = 5.7 + stats["speed"] * 0.20 + stats["boost"] * 0.055

    if p.character == "Kenny":
        boost_factor = 1.28
        speed_ceiling = 9.35

    if charge >= 85:
        p.boost_timer = max(p.boost_timer, 80.0 * boost_factor)
        p.speed = max(p.speed, min(speed_ceiling, 7.15 + stats["boost"] * 0.16))
        self._mechanic_message = "ULTRA DRIFT TURBO!"
        self._mechanic_message_timer = 70.0
    elif charge >= 52:
        p.boost_timer = max(p.boost_timer, 51.0 * boost_factor)
        p.speed = max(p.speed, min(speed_ceiling, 6.65 + stats["boost"] * 0.12))
        self._mechanic_message = "SUPER DRIFT TURBO!"
        self._mechanic_message_timer = 52.0
    elif charge >= 24:
        p.boost_timer = max(p.boost_timer, 29.0 * boost_factor)
        p.speed = max(p.speed, min(speed_ceiling, 6.1 + stats["boost"] * 0.08))
        self._mechanic_message = "MINI TURBO!"
        self._mechanic_message_timer = 36.0

    p.drifting = False
    p.drift_charge = 0.0
    p.drift_direction = 0


def _build_track_stats(self):
    _ORIGINALS["_build_track"](self)
    stats = _player_stats(self)
    name = self.player.character if self.player is not None else km.CHARACTERS[self.selected_character][0]

    self.stats_hud_label = pyglet.text.Label(
        "{}  SPD{} ACC{} TRN{} WGT{} GRP{} BST{}".format(
            name.upper(), stats["speed"], stats["accel"], stats["turn"],
            stats["weight"], stats["grip"], stats["boost"]
        ),
        x=EngineGlobals.width - 14, y=EngineGlobals.height - 24,
        anchor_x="right", font_size=9,
        color=(230, 236, 248, 255), batch=self.batch, group=self.ui_group,
    )
    self._race_labels.append(self.stats_hud_label)

    # Persistent drift sparks give immediate visual feedback for charge tiers.
    self._drift_sparks = [
        pyglet.shapes.Circle(-100, -100, 4, color=(103, 201, 255), batch=self.batch, group=self.ui_group),
        pyglet.shapes.Circle(-100, -100, 4, color=(103, 201, 255), batch=self.batch, group=self.ui_group),
    ]
    for spark in self._drift_sparks:
        spark.visible = False
        self._race_shapes.append(spark)


def _update_drift_sparks(self):
    p = self.player
    if p is None or not self._drift_sparks:
        return
    visible = p.drifting and p.drift_charge >= 20
    if not visible:
        for spark in self._drift_sparks:
            spark.visible = False
        return

    if p.drift_charge >= 85:
        color = (194, 107, 255)
        radius = 7
    elif p.drift_charge >= 52:
        color = (255, 165, 65)
        radius = 6
    else:
        color = (103, 201, 255)
        radius = 4

    rear_x = p.x - math.cos(p.angle) * 22
    rear_y = p.y - math.sin(p.angle) * 22
    side_x = -math.sin(p.angle)
    side_y = math.cos(p.angle)
    for spark, side in zip(self._drift_sparks, (-1, 1)):
        spark.visible = True
        spark.color = color
        spark.radius = radius
        spark.position = (rear_x + side_x * 12 * side, rear_y + side_y * 12 * side)


def _update_stats(self, dt):
    previous_state = self.state

    # Start-boost timing: pressing throttle only during the final beat is ideal.
    if self.state == self.STATE_COUNTDOWN and self.player is not None:
        up = bool(EngineGlobals.keys[pyglet.window.key.UP])
        if up:
            if self.countdown > 52:
                self.launch_early = True
            else:
                self.launch_charge = min(65.0, self.launch_charge + float(dt))
        elif self.countdown <= 52:
            self.launch_charge = max(0.0, self.launch_charge - float(dt) * 0.35)

    _ORIGINALS["update"](self, dt)

    if previous_state == self.STATE_COUNTDOWN and self.state == self.STATE_RACE and self.player is not None:
        stats = _player_stats(self)
        if self.launch_early:
            self.player.speed = min(self.player.speed, 1.3)
            self._mechanic_message = "WHEELSPIN! WAIT FOR THE LAST BEAT"
            self._mechanic_message_timer = 75.0
        elif self.launch_charge >= 18:
            strength = min(1.0, self.launch_charge / 45.0)
            self.player.speed = max(
                self.player.speed,
                5.1 + strength * (1.3 + stats["accel"] * 0.06),
            )
            self.player.boost_timer = max(
                self.player.boost_timer,
                28.0 + strength * (28.0 + stats["boost"] * 1.5),
            )
            self._mechanic_message = "PERFECT LAUNCH!" if strength >= 0.82 else "GOOD LAUNCH!"
            self._mechanic_message_timer = 65.0
        self.launch_charge = 0.0
        self.launch_early = False

    if self.state in (self.STATE_RACE, self.STATE_FINISH):
        _update_drift_sparks(self)


def _start_race_stats(self):
    self.launch_charge = 0.0
    self.launch_early = False
    self.air_trick_armed = False
    self.air_trick_was_airborne = False
    _ORIGINALS["_start_race"](self)


def _on_key_press_stats(self, symbol, modifiers):
    if (
        self.active
        and self.state == self.STATE_RACE
        and symbol == pyglet.window.key.SPACE
        and self.player is not None
        and self.player.hop_timer > 4
        and not self.player.drifting
    ):
        self.air_trick_armed = True
        self.air_trick_was_airborne = True
        self._mechanic_message = "AIR TRICK!"
        self._mechanic_message_timer = 30.0
        return pyglet.event.EVENT_HANDLED

    return _ORIGINALS["on_key_press"](self, symbol, modifiers)


def _update_ai_stats(self, racer, dt):
    """Keep the ten CPU karts competitive without erasing character advantages."""
    pre_speed = racer.speed
    _ORIGINALS["_update_ai"](self, racer, dt)

    if self.player is None or racer.finished:
        return

    # Stable AI skill ladder plus gentle pace matching. This is deliberately
    # modest rubber-banding: strong driving still wins.
    skill = (0.95, 0.98, 1.00, 1.02, 1.04, 0.97, 1.01, 1.05, 0.99, 1.03)[racer.ai_index % 10]
    player_progress = self.player.progress_score(self.CHECKPOINTS)
    ai_progress = racer.progress_score(self.CHECKPOINTS)
    gap = player_progress - ai_progress

    target_cap = 5.65 * skill
    if gap >= 3:
        target_cap += min(0.65, 0.13 * gap)
    elif gap <= -3:
        target_cap -= min(0.35, 0.07 * abs(gap))

    if racer.speed < target_cap:
        racer.speed += 0.018 * float(dt) * skill
    racer.speed = min(racer.speed, target_cap + (1.2 if racer.boost_timer > 0 else 0.0))

    # Avoid a rare near-stop after bumps/hazards so the pack does not collapse.
    if pre_speed > 2.0 and racer.speed < 1.0:
        racer.speed = 1.0


def install_kart_stats():
    """Install character ratings, advanced handling, and extra kart feedback."""
    global _INSTALLED
    if _INSTALLED:
        return

    # Safe if called independently; the expansion installer is idempotent.
    kx.install_karts_expansion()

    cls = km.KartsMode
    for name in (
        "__init__",
        "_build_character_select",
        "_refresh_character_highlight",
        "_update_player",
        "_release_drift",
        "_build_track",
        "update",
        "_start_race",
        "on_key_press",
        "_update_ai",
    ):
        _ORIGINALS[name] = getattr(cls, name)

    cls.__init__ = _stats_init
    cls._build_character_select = _build_character_select_stats
    cls._refresh_character_highlight = _refresh_character_highlight_stats
    cls._update_player = _update_player_stats
    cls._release_drift = _release_drift_stats
    cls._build_track = _build_track_stats
    cls.update = _update_stats
    cls._start_race = _start_race_stats
    cls.on_key_press = _on_key_press_stats
    cls._update_ai = _update_ai_stats

    _INSTALLED = True
