"""Top-down arcade racing mode: Karts not Farts."""

import math
import random

import pyglet

from engineglobals import EngineGlobals


CHARACTERS = (
    ("Kenny", (229, 154, 158)),
    ("Theo", (213, 164, 114)),
    ("Lucinda", (175, 116, 189)),
)

CAR_COLORS = (
    ("Red", (212, 67, 63)),
    ("Blue", (66, 110, 204)),
    ("Green", (72, 157, 91)),
    ("Yellow", (230, 192, 65)),
    ("Purple", (150, 89, 189)),
)

EMBLEMS = ("Triangle", "Flame", "Heart")
AI_COLOR = (103, 69, 47)
ROAD_COLOR = (77, 78, 82)
ROAD_EDGE = (201, 193, 169)
GRASS_COLOR = (69, 129, 73)
BOOST_COLOR = (77, 221, 233)


class KartRacer:
    def __init__(self, x, y, angle, color, character="", emblem="Triangle", ai=False, ai_index=0):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.speed = 0.0
        self.color = color
        self.character = character
        self.emblem = emblem
        self.ai = ai
        self.ai_index = ai_index
        self.next_checkpoint = 1
        self.lap = 0
        self.finished = False
        self.finish_order = None
        self.boost_timer = 0.0
        self.hop_timer = 0.0
        self.drifting = False
        self.drift_charge = 0.0
        self.drift_direction = 0
        self.offroad = False
        self.pad_cooldown = 0.0
        self.bump_cooldown = 0.0

        self.body = None
        self.nose = None
        self.wheels = []
        self.head = None
        self.emblem_shapes = []
        self.turd_shapes = []
        self.name_label = None

    def progress_score(self, checkpoints):
        if self.finished:
            return 100000 + (100 - (self.finish_order or 99))
        return self.lap * len(checkpoints) + self.next_checkpoint


class KartsMode:
    """Self-contained bird's-eye racing mode with selection screens and AI racers."""

    STATE_CHARACTER = "character"
    STATE_COLOR = "color"
    STATE_EMBLEM = "emblem"
    STATE_COUNTDOWN = "countdown"
    STATE_RACE = "race"
    STATE_FINISH = "finish"

    TOTAL_LAPS = 3
    ROAD_HALF_WIDTH = 72.0
    PLAYER_ACCEL = 0.20
    PLAYER_REVERSE_ACCEL = 0.13
    PLAYER_MAX_SPEED = 6.4
    BOOST_MAX_SPEED = 8.7
    PLAYER_FRICTION = 0.965
    OFFROAD_FRICTION = 0.90
    STEER_RATE = 0.041
    DRIFT_STEER_RATE = 0.065

    CHECKPOINTS = (
        (145.0, 140.0),
        (325.0, 96.0),
        (548.0, 108.0),
        (685.0, 212.0),
        (666.0, 386.0),
        (515.0, 500.0),
        (292.0, 505.0),
        (125.0, 414.0),
        (92.0, 260.0),
    )

    BOOST_PADS = (
        (430.0, 100.0, 0.0),
        (676.0, 310.0, 92.0),
        (408.0, 505.0, 180.0),
        (105.0, 335.0, -92.0),
    )

    def __init__(self, on_exit_to_menu=None):
        self.on_exit_to_menu = on_exit_to_menu
        self.active = False
        self.state = self.STATE_CHARACTER
        self.selected_character = 0
        self.selected_color = 0
        self.selected_emblem = 0
        self.countdown = 180.0
        self.race_time = 0.0
        self.finish_counter = 0
        self.player = None
        self.ai_racers = []
        self.racers = []
        self._race_shapes = []
        self._race_labels = []
        self._selection_shapes = []
        self._selection_labels = []
        self._finish_shapes = []
        self._finish_labels = []
        self._rng = random.Random(8675309)

        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(0)
        self.track_group = pyglet.graphics.Group(1)
        self.kart_group = pyglet.graphics.Group(2)
        self.ui_group = pyglet.graphics.Group(3)

        self.background = pyglet.shapes.Rectangle(
            0, 0, EngineGlobals.width, EngineGlobals.height,
            color=(20, 24, 31), batch=self.batch, group=self.bg_group,
        )
        self.mode_title = pyglet.text.Label(
            "KARTS NOT FARTS",
            x=EngineGlobals.width // 2,
            y=EngineGlobals.height - 52,
            anchor_x="center",
            font_size=28,
            weight=pyglet.text.Weight.BOLD,
            color=(255, 242, 195, 255),
            batch=self.batch,
            group=self.ui_group,
        )
        self.mode_title.visible = False

    def start(self):
        self.active = True
        self.state = self.STATE_CHARACTER
        self.selected_character = 0
        self.selected_color = 0
        self.selected_emblem = 0
        self._destroy_race()
        self._clear_finish_ui()
        self._build_character_select()

    def stop(self):
        self.active = False
        self._clear_selection_ui()
        self._clear_finish_ui()
        self._destroy_race()
        self.mode_title.visible = False

    def _clear_selection_ui(self):
        for shape in self._selection_shapes:
            shape.delete()
        self._selection_shapes.clear()
        for label in self._selection_labels:
            label.delete()
        self._selection_labels.clear()

    def _clear_finish_ui(self):
        for shape in self._finish_shapes:
            shape.delete()
        self._finish_shapes.clear()
        for label in self._finish_labels:
            label.delete()
        self._finish_labels.clear()

    def _destroy_racer_visuals(self, racer):
        for shape in racer.wheels + racer.emblem_shapes + racer.turd_shapes:
            shape.delete()
        racer.wheels.clear()
        racer.emblem_shapes.clear()
        racer.turd_shapes.clear()
        for attr in ("body", "nose", "head"):
            item = getattr(racer, attr)
            if item is not None:
                item.delete()
                setattr(racer, attr, None)
        if racer.name_label is not None:
            racer.name_label.delete()
            racer.name_label = None

    def _destroy_race(self):
        for racer in self.racers:
            self._destroy_racer_visuals(racer)
        self.racers = []
        self.ai_racers = []
        self.player = None
        for shape in self._race_shapes:
            shape.delete()
        self._race_shapes.clear()
        for label in self._race_labels:
            label.delete()
        self._race_labels.clear()

    def _selection_header(self, subtitle):
        self.mode_title.visible = True
        label = pyglet.text.Label(
            subtitle,
            x=EngineGlobals.width // 2,
            y=EngineGlobals.height - 100,
            anchor_x="center",
            font_size=16,
            color=(220, 226, 235, 255),
            batch=self.batch,
            group=self.ui_group,
        )
        self._selection_labels.append(label)

    def _selection_footer(self):
        label = pyglet.text.Label(
            "Arrow keys choose  •  Enter confirms  •  Esc returns to menu",
            x=EngineGlobals.width // 2,
            y=52,
            anchor_x="center",
            font_size=12,
            color=(192, 202, 215, 255),
            batch=self.batch,
            group=self.ui_group,
        )
        self._selection_labels.append(label)

    def _build_character_select(self):
        self._clear_selection_ui()
        self._selection_header("PICK YOUR RACER")
        self._selection_footer()
        start_x = 190
        for index, (name, face_color) in enumerate(CHARACTERS):
            x = start_x + index * 210
            panel = pyglet.shapes.Rectangle(
                x - 75, 185, 150, 265,
                color=(50, 57, 70), batch=self.batch, group=self.track_group,
            )
            self._selection_shapes.append(panel)
            head = pyglet.shapes.Circle(x, 330, 48, color=face_color, batch=self.batch, group=self.ui_group)
            eye_l = pyglet.shapes.Circle(x - 15, 340, 5, color=(30, 25, 22), batch=self.batch, group=self.ui_group)
            eye_r = pyglet.shapes.Circle(x + 15, 340, 5, color=(30, 25, 22), batch=self.batch, group=self.ui_group)
            mouth = pyglet.shapes.Rectangle(x - 18, 306, 36, 7, color=(92, 38, 42), batch=self.batch, group=self.ui_group)
            self._selection_shapes.extend((head, eye_l, eye_r, mouth))
            label = pyglet.text.Label(
                name.upper(), x=x, y=225, anchor_x="center",
                font_size=18, weight=pyglet.text.Weight.BOLD,
                color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
            )
            self._selection_labels.append(label)
        self._refresh_character_highlight()

    def _refresh_character_highlight(self):
        panels = [shape for shape in self._selection_shapes if isinstance(shape, pyglet.shapes.Rectangle) and shape.height == 265]
        for index, panel in enumerate(panels[:3]):
            panel.color = (104, 112, 130) if index == self.selected_character else (50, 57, 70)

    def _build_color_select(self):
        self._clear_selection_ui()
        self._selection_header("PICK ONE OF FIVE KART COLORS")
        self._selection_footer()
        for index, (name, color) in enumerate(CAR_COLORS):
            x = 115 + index * 142
            swatch = pyglet.shapes.Rectangle(
                x - 45, 260, 90, 120, color=color,
                batch=self.batch, group=self.ui_group,
            )
            self._selection_shapes.append(swatch)
            label = pyglet.text.Label(
                name.upper(), x=x, y=225, anchor_x="center",
                font_size=13, weight=pyglet.text.Weight.BOLD,
                color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
            )
            self._selection_labels.append(label)
        self._refresh_color_highlight()

    def _refresh_color_highlight(self):
        swatches = [shape for shape in self._selection_shapes if isinstance(shape, pyglet.shapes.Rectangle) and shape.height == 120]
        for index, swatch in enumerate(swatches[:5]):
            swatch.opacity = 255 if index == self.selected_color else 115
            swatch.scale = 1.12 if index == self.selected_color else 1.0

    def _build_emblem_select(self):
        self._clear_selection_ui()
        self._selection_header("PICK YOUR KART SHAPE")
        self._selection_footer()
        for index, name in enumerate(EMBLEMS):
            x = 205 + index * 195
            panel = pyglet.shapes.Rectangle(
                x - 67, 230, 134, 175, color=(50, 57, 70),
                batch=self.batch, group=self.track_group,
            )
            self._selection_shapes.append(panel)
            if name == "Triangle":
                icon = pyglet.shapes.Triangle(x, 350, x - 43, 275, x + 43, 275, color=(255, 223, 92), batch=self.batch, group=self.ui_group)
                self._selection_shapes.append(icon)
            elif name == "Flame":
                outer = pyglet.shapes.Triangle(x, 365, x - 42, 270, x + 42, 270, color=(237, 88, 45), batch=self.batch, group=self.ui_group)
                inner = pyglet.shapes.Triangle(x + 5, 337, x - 20, 282, x + 26, 282, color=(255, 209, 70), batch=self.batch, group=self.ui_group)
                self._selection_shapes.extend((outer, inner))
            else:
                c1 = pyglet.shapes.Circle(x - 24, 325, 30, color=(225, 72, 106), batch=self.batch, group=self.ui_group)
                c2 = pyglet.shapes.Circle(x + 24, 325, 30, color=(225, 72, 106), batch=self.batch, group=self.ui_group)
                tri = pyglet.shapes.Triangle(x - 52, 326, x + 52, 326, x, 260, color=(225, 72, 106), batch=self.batch, group=self.ui_group)
                self._selection_shapes.extend((c1, c2, tri))
            label = pyglet.text.Label(
                name.upper(), x=x, y=205, anchor_x="center",
                font_size=15, weight=pyglet.text.Weight.BOLD,
                color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
            )
            self._selection_labels.append(label)
        self._refresh_emblem_highlight()

    def _refresh_emblem_highlight(self):
        panels = [shape for shape in self._selection_shapes if isinstance(shape, pyglet.shapes.Rectangle) and shape.height == 175]
        for index, panel in enumerate(panels[:3]):
            panel.color = (108, 116, 134) if index == self.selected_emblem else (50, 57, 70)

    def _build_track(self):
        self._race_shapes.append(
            pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, EngineGlobals.height, color=GRASS_COLOR, batch=self.batch, group=self.bg_group)
        )
        points = self.CHECKPOINTS
        for i, p1 in enumerate(points):
            p2 = points[(i + 1) % len(points)]
            edge = pyglet.shapes.Line(
                p1[0], p1[1], p2[0], p2[1], thickness=int(self.ROAD_HALF_WIDTH * 2 + 18),
                color=ROAD_EDGE, batch=self.batch, group=self.track_group,
            )
            road = pyglet.shapes.Line(
                p1[0], p1[1], p2[0], p2[1], thickness=int(self.ROAD_HALF_WIDTH * 2),
                color=ROAD_COLOR, batch=self.batch, group=self.track_group,
            )
            hub_edge = pyglet.shapes.Circle(p1[0], p1[1], self.ROAD_HALF_WIDTH + 9, color=ROAD_EDGE, batch=self.batch, group=self.track_group)
            hub = pyglet.shapes.Circle(p1[0], p1[1], self.ROAD_HALF_WIDTH, color=ROAD_COLOR, batch=self.batch, group=self.track_group)
            self._race_shapes.extend((edge, road, hub_edge, hub))

        for bx, by, rotation in self.BOOST_PADS:
            pad = pyglet.shapes.Rectangle(
                bx - 33, by - 14, 66, 28, color=BOOST_COLOR,
                batch=self.batch, group=self.track_group,
            )
            pad.anchor_position = (33, 14)
            pad.position = (bx, by)
            pad.rotation = rotation
            self._race_shapes.append(pad)
            for offset in (-18, 0, 18):
                stripe = pyglet.shapes.Rectangle(
                    bx - 4, by - 10, 8, 20, color=(235, 255, 255),
                    batch=self.batch, group=self.track_group,
                )
                stripe.anchor_position = (4, 10)
                stripe.position = (bx, by)
                stripe.rotation = rotation
                angle = math.radians(-rotation)
                stripe.x += math.cos(angle) * offset
                stripe.y += math.sin(angle) * offset
                self._race_shapes.append(stripe)

        # Start/finish line.
        sx, sy = points[0]
        for index in range(8):
            square = pyglet.shapes.Rectangle(
                sx - 12 + (index % 2) * 12,
                sy - 48 + index * 12,
                12,
                12,
                color=(245, 245, 245) if index % 2 == 0 else (25, 25, 25),
                batch=self.batch,
                group=self.track_group,
            )
            self._race_shapes.append(square)

        self.lap_label = pyglet.text.Label(
            "LAP 1/3", x=18, y=EngineGlobals.height - 24,
            font_size=15, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        self.place_label = pyglet.text.Label(
            "PLACE 1/11", x=18, y=EngineGlobals.height - 48,
            font_size=13, color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        self.speed_label = pyglet.text.Label(
            "", x=18, y=18, font_size=12,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        self.drift_label = pyglet.text.Label(
            "", x=EngineGlobals.width - 18, y=18, anchor_x="right", font_size=12,
            color=(255, 240, 169, 255), batch=self.batch, group=self.ui_group,
        )
        self.countdown_label = pyglet.text.Label(
            "3", x=EngineGlobals.width // 2, y=EngineGlobals.height // 2,
            anchor_x="center", anchor_y="center", font_size=72,
            weight=pyglet.text.Weight.BOLD, color=(255, 241, 174, 255),
            batch=self.batch, group=self.ui_group,
        )
        self._race_labels.extend((self.lap_label, self.place_label, self.speed_label, self.drift_label, self.countdown_label))

    def _spawn_racers(self):
        start = self.CHECKPOINTS[0]
        nxt = self.CHECKPOINTS[1]
        heading = math.atan2(nxt[1] - start[1], nxt[0] - start[0])
        char_name = CHARACTERS[self.selected_character][0]
        color = CAR_COLORS[self.selected_color][1]
        emblem = EMBLEMS[self.selected_emblem]
        self.player = KartRacer(start[0] + 16, start[1] + 10, heading, color, char_name, emblem, ai=False)
        self.racers = [self.player]

        # Ten brown computer karts shaped like little turds. They all use the same
        # color so the player's five color choices remain visually distinct.
        back_x = math.cos(heading + math.pi)
        back_y = math.sin(heading + math.pi)
        side_x = math.cos(heading + math.pi / 2)
        side_y = math.sin(heading + math.pi / 2)
        for i in range(10):
            row = i // 2 + 1
            lane = -1 if i % 2 == 0 else 1
            x = start[0] + back_x * (row * 38) + side_x * (lane * 22)
            y = start[1] + back_y * (row * 38) + side_y * (lane * 22)
            ai = KartRacer(x, y, heading, AI_COLOR, character=f"CPU {i + 1}", emblem="Turd", ai=True, ai_index=i)
            ai.next_checkpoint = 1
            self.ai_racers.append(ai)
            self.racers.append(ai)

        for racer in self.racers:
            self._create_racer_visuals(racer)
            self._update_racer_visuals(racer)

    def _create_racer_visuals(self, racer):
        if racer.ai:
            # Three stacked blobs create the deliberately silly turd-kart silhouette.
            for radius in (17, 13, 9):
                blob = pyglet.shapes.Circle(0, 0, radius, color=AI_COLOR, batch=self.batch, group=self.kart_group)
                racer.turd_shapes.append(blob)
            for _ in range(4):
                wheel = pyglet.shapes.Circle(0, 0, 5, color=(25, 23, 22), batch=self.batch, group=self.kart_group)
                racer.wheels.append(wheel)
            return

        racer.body = pyglet.shapes.Rectangle(0, 0, 48, 28, color=racer.color, batch=self.batch, group=self.kart_group)
        racer.body.anchor_position = (24, 14)
        racer.nose = pyglet.shapes.Rectangle(0, 0, 18, 20, color=tuple(min(255, c + 25) for c in racer.color), batch=self.batch, group=self.kart_group)
        racer.nose.anchor_position = (9, 10)
        racer.head = pyglet.shapes.Circle(0, 0, 10, color=CHARACTERS[self.selected_character][1], batch=self.batch, group=self.kart_group)
        for _ in range(4):
            racer.wheels.append(pyglet.shapes.Circle(0, 0, 5, color=(24, 25, 28), batch=self.batch, group=self.kart_group))

        if racer.emblem == "Triangle":
            racer.emblem_shapes.append(pyglet.shapes.Triangle(0, 0, 0, 0, 0, 0, color=(255, 230, 90), batch=self.batch, group=self.kart_group))
        elif racer.emblem == "Flame":
            racer.emblem_shapes.append(pyglet.shapes.Triangle(0, 0, 0, 0, 0, 0, color=(250, 98, 45), batch=self.batch, group=self.kart_group))
            racer.emblem_shapes.append(pyglet.shapes.Circle(0, 0, 4, color=(255, 218, 74), batch=self.batch, group=self.kart_group))
        else:
            racer.emblem_shapes.append(pyglet.shapes.Circle(0, 0, 5, color=(255, 102, 139), batch=self.batch, group=self.kart_group))
            racer.emblem_shapes.append(pyglet.shapes.Circle(0, 0, 5, color=(255, 102, 139), batch=self.batch, group=self.kart_group))
            racer.emblem_shapes.append(pyglet.shapes.Triangle(0, 0, 0, 0, 0, 0, color=(255, 102, 139), batch=self.batch, group=self.kart_group))

    @staticmethod
    def _rotate_local(x, y, angle):
        ca = math.cos(angle)
        sa = math.sin(angle)
        return (x * ca - y * sa, x * sa + y * ca)

    def _update_racer_visuals(self, racer):
        angle_deg = -math.degrees(racer.angle)
        hop = 7.0 if racer.hop_timer > 0 else 0.0
        if racer.ai:
            offsets = ((-10, 0), (2, 0), (13, 0))
            for blob, (ox, oy) in zip(racer.turd_shapes, offsets):
                rx, ry = self._rotate_local(ox, oy, racer.angle)
                blob.position = (racer.x + rx, racer.y + ry + hop)
            wheel_offsets = ((-12, -15), (-12, 15), (12, -15), (12, 15))
            for wheel, (ox, oy) in zip(racer.wheels, wheel_offsets):
                rx, ry = self._rotate_local(ox, oy, racer.angle)
                wheel.position = (racer.x + rx, racer.y + ry + hop)
            return

        racer.body.position = (racer.x, racer.y + hop)
        racer.body.rotation = angle_deg
        nose_dx, nose_dy = self._rotate_local(22, 0, racer.angle)
        racer.nose.position = (racer.x + nose_dx, racer.y + nose_dy + hop)
        racer.nose.rotation = angle_deg
        head_dx, head_dy = self._rotate_local(-10, 0, racer.angle)
        racer.head.position = (racer.x + head_dx, racer.y + head_dy + hop)
        wheel_offsets = ((-15, -17), (-15, 17), (15, -17), (15, 17))
        for wheel, (ox, oy) in zip(racer.wheels, wheel_offsets):
            rx, ry = self._rotate_local(ox, oy, racer.angle)
            wheel.position = (racer.x + rx, racer.y + ry + hop)

        ex, ey = self._rotate_local(6, 0, racer.angle)
        cx, cy = racer.x + ex, racer.y + ey + hop
        if racer.emblem == "Triangle":
            tri = racer.emblem_shapes[0]
            tri.x, tri.y = cx + 6, cy
            tri.x2, tri.y2 = cx - 5, cy - 6
            tri.x3, tri.y3 = cx - 5, cy + 6
        elif racer.emblem == "Flame":
            tri, dot = racer.emblem_shapes
            tri.x, tri.y = cx + 6, cy
            tri.x2, tri.y2 = cx - 5, cy - 7
            tri.x3, tri.y3 = cx - 4, cy + 7
            dot.position = (cx - 1, cy)
        else:
            c1, c2, tri = racer.emblem_shapes
            c1.position = (cx - 3, cy + 3)
            c2.position = (cx + 3, cy + 3)
            tri.x, tri.y = cx - 7, cy + 2
            tri.x2, tri.y2 = cx + 7, cy + 2
            tri.x3, tri.y3 = cx, cy - 7

    def _distance_to_segment(self, px, py, ax, ay, bx, by):
        vx = bx - ax
        vy = by - ay
        wx = px - ax
        wy = py - ay
        denom = vx * vx + vy * vy
        if denom <= 0.0001:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, (wx * vx + wy * vy) / denom))
        cx = ax + vx * t
        cy = ay + vy * t
        return math.hypot(px - cx, py - cy)

    def _on_road(self, racer):
        best = 999999.0
        for i, p1 in enumerate(self.CHECKPOINTS):
            p2 = self.CHECKPOINTS[(i + 1) % len(self.CHECKPOINTS)]
            best = min(best, self._distance_to_segment(racer.x, racer.y, p1[0], p1[1], p2[0], p2[1]))
        return best <= self.ROAD_HALF_WIDTH

    @staticmethod
    def _angle_delta(target, current):
        return (target - current + math.pi) % (math.tau) - math.pi

    def _update_player(self, dt):
        p = self.player
        if p.finished:
            return
        keys = EngineGlobals.keys
        throttle = bool(keys[pyglet.window.key.UP])
        brake = bool(keys[pyglet.window.key.DOWN])
        left = bool(keys[pyglet.window.key.LEFT])
        right = bool(keys[pyglet.window.key.RIGHT])
        space = bool(keys[pyglet.window.key.SPACE])

        if throttle:
            p.speed += self.PLAYER_ACCEL * dt
        if brake:
            p.speed -= self.PLAYER_REVERSE_ACCEL * dt
        if not throttle and not brake:
            p.speed *= self.PLAYER_FRICTION ** dt

        p.offroad = not self._on_road(p)
        if p.offroad:
            p.speed *= self.OFFROAD_FRICTION ** dt

        if p.boost_timer > 0:
            p.boost_timer -= dt
            max_speed = self.BOOST_MAX_SPEED
            p.speed += 0.10 * dt
        else:
            max_speed = self.PLAYER_MAX_SPEED
        p.speed = max(-2.5, min(max_speed, p.speed))

        steer_scale = min(1.0, abs(p.speed) / 2.0)
        steer = (-1 if left else 0) + (1 if right else 0)
        if steer:
            rate = self.DRIFT_STEER_RATE if p.drifting else self.STEER_RATE
            direction_sign = 1.0 if p.speed >= 0 else -1.0
            p.angle += steer * rate * steer_scale * direction_sign * dt
            if p.drifting and space:
                p.drift_charge = min(100.0, p.drift_charge + (0.9 + abs(p.speed) * 0.08) * dt)
                p.drift_direction = steer

        if p.hop_timer > 0:
            p.hop_timer -= dt

        p.x += math.cos(p.angle) * p.speed * dt
        p.y += math.sin(p.angle) * p.speed * dt
        p.x = max(18.0, min(EngineGlobals.width - 18.0, p.x))
        p.y = max(18.0, min(EngineGlobals.height - 18.0, p.y))

        if p.pad_cooldown > 0:
            p.pad_cooldown -= dt
        else:
            for bx, by, _ in self.BOOST_PADS:
                if math.hypot(p.x - bx, p.y - by) <= 42:
                    p.boost_timer = max(p.boost_timer, 70.0)
                    p.pad_cooldown = 45.0
                    p.speed = max(p.speed, 7.2)
                    break

        if p.bump_cooldown > 0:
            p.bump_cooldown -= dt
        else:
            for ai in self.ai_racers:
                if math.hypot(p.x - ai.x, p.y - ai.y) < 30:
                    p.speed *= 0.82
                    p.angle += self._rng.choice((-0.18, 0.18))
                    p.bump_cooldown = 22.0
                    break

        self._update_checkpoint(p)

    def _update_ai(self, racer, dt):
        if racer.finished:
            return
        target = self.CHECKPOINTS[racer.next_checkpoint]
        # Each AI gets a small stable line offset and speed variance.
        target_angle = math.atan2(target[1] - racer.y, target[0] - racer.x)
        delta = self._angle_delta(target_angle, racer.angle)
        racer.angle += max(-0.055, min(0.055, delta)) * dt
        desired = 4.65 + (racer.ai_index % 5) * 0.18
        if abs(delta) > 0.85:
            desired *= 0.78
        if racer.boost_timer > 0:
            racer.boost_timer -= dt
            desired += 1.6
        racer.speed += (desired - racer.speed) * min(1.0, 0.035 * dt)
        racer.x += math.cos(racer.angle) * racer.speed * dt
        racer.y += math.sin(racer.angle) * racer.speed * dt
        if racer.pad_cooldown > 0:
            racer.pad_cooldown -= dt
        else:
            for bx, by, _ in self.BOOST_PADS:
                if math.hypot(racer.x - bx, racer.y - by) <= 38:
                    racer.boost_timer = 45.0
                    racer.pad_cooldown = 55.0
                    break
        self._update_checkpoint(racer)

    def _update_checkpoint(self, racer):
        target = self.CHECKPOINTS[racer.next_checkpoint]
        if math.hypot(racer.x - target[0], racer.y - target[1]) > 72:
            return
        racer.next_checkpoint += 1
        if racer.next_checkpoint >= len(self.CHECKPOINTS):
            racer.next_checkpoint = 0
        elif racer.next_checkpoint == 1:
            # Checkpoint 0 is the start/finish line. A racer only earns a lap after
            # traversing the whole loop and returning to checkpoint 0.
            racer.lap += 1
            if racer.lap >= self.TOTAL_LAPS:
                self._finish_racer(racer)

    def _finish_racer(self, racer):
        if racer.finished:
            return
        racer.finished = True
        self.finish_counter += 1
        racer.finish_order = self.finish_counter
        if racer is self.player:
            self.state = self.STATE_FINISH
            self._build_finish_ui()

    def _current_place(self):
        if self.player is None:
            return 1
        ordered = sorted(self.racers, key=lambda r: r.progress_score(self.CHECKPOINTS), reverse=True)
        try:
            return ordered.index(self.player) + 1
        except ValueError:
            return 1

    def _start_race(self):
        self._clear_selection_ui()
        self._clear_finish_ui()
        self._destroy_race()
        self.mode_title.visible = False
        self._build_track()
        self._spawn_racers()
        self.countdown = 180.0
        self.race_time = 0.0
        self.finish_counter = 0
        self.state = self.STATE_COUNTDOWN

    def _build_finish_ui(self):
        place = self.player.finish_order or self._current_place()
        panel = pyglet.shapes.Rectangle(
            150, 165, 500, 260, color=(31, 34, 42), batch=self.batch, group=self.ui_group,
        )
        panel.opacity = 235
        self._finish_shapes.append(panel)
        title = pyglet.text.Label(
            "RACE FINISHED!", x=EngineGlobals.width // 2, y=365,
            anchor_x="center", font_size=30, weight=pyglet.text.Weight.BOLD,
            color=(255, 240, 171, 255), batch=self.batch, group=self.ui_group,
        )
        result = pyglet.text.Label(
            f"{self.player.character} finished {place} of 11",
            x=EngineGlobals.width // 2, y=310, anchor_x="center", font_size=18,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        time_label = pyglet.text.Label(
            f"Time: {self.race_time / 60.0:.1f}s",
            x=EngineGlobals.width // 2, y=270, anchor_x="center", font_size=14,
            color=(218, 225, 237, 255), batch=self.batch, group=self.ui_group,
        )
        prompt = pyglet.text.Label(
            "Enter: race again  •  Esc: main menu",
            x=EngineGlobals.width // 2, y=220, anchor_x="center", font_size=13,
            color=(218, 225, 237, 255), batch=self.batch, group=self.ui_group,
        )
        self._finish_labels.extend((title, result, time_label, prompt))

    def _release_drift(self):
        p = self.player
        if p is None or not p.drifting:
            return
        if p.drift_charge >= 65:
            p.boost_timer = max(p.boost_timer, 75.0)
            p.speed = max(p.speed, 7.5)
        elif p.drift_charge >= 28:
            p.boost_timer = max(p.boost_timer, 38.0)
            p.speed = max(p.speed, 6.8)
        p.drifting = False
        p.drift_charge = 0.0
        p.drift_direction = 0

    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        if symbol == pyglet.window.key.ESCAPE:
            self.stop()
            if self.on_exit_to_menu:
                self.on_exit_to_menu()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_CHARACTER:
            if symbol in (pyglet.window.key.LEFT, pyglet.window.key.UP):
                self.selected_character = (self.selected_character - 1) % len(CHARACTERS)
                self._refresh_character_highlight()
            elif symbol in (pyglet.window.key.RIGHT, pyglet.window.key.DOWN):
                self.selected_character = (self.selected_character + 1) % len(CHARACTERS)
                self._refresh_character_highlight()
            elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
                self.state = self.STATE_COLOR
                self._build_color_select()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_COLOR:
            if symbol in (pyglet.window.key.LEFT, pyglet.window.key.UP):
                self.selected_color = (self.selected_color - 1) % len(CAR_COLORS)
                self._refresh_color_highlight()
            elif symbol in (pyglet.window.key.RIGHT, pyglet.window.key.DOWN):
                self.selected_color = (self.selected_color + 1) % len(CAR_COLORS)
                self._refresh_color_highlight()
            elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
                self.state = self.STATE_EMBLEM
                self._build_emblem_select()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_EMBLEM:
            if symbol in (pyglet.window.key.LEFT, pyglet.window.key.UP):
                self.selected_emblem = (self.selected_emblem - 1) % len(EMBLEMS)
                self._refresh_emblem_highlight()
            elif symbol in (pyglet.window.key.RIGHT, pyglet.window.key.DOWN):
                self.selected_emblem = (self.selected_emblem + 1) % len(EMBLEMS)
                self._refresh_emblem_highlight()
            elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
                self._start_race()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_RACE and symbol == pyglet.window.key.SPACE:
            if self.player and not self.player.drifting:
                self.player.drifting = True
                self.player.hop_timer = 16.0
                self.player.drift_charge = 0.0
                self.player.drift_direction = 0
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_FINISH and symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
            self._start_race()
            return pyglet.event.EVENT_HANDLED

        return pyglet.event.EVENT_HANDLED

    def on_key_release(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        if self.state == self.STATE_RACE and symbol == pyglet.window.key.SPACE:
            self._release_drift()
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def update(self, dt):
        if not self.active:
            return
        dt = float(dt)
        if self.state == self.STATE_COUNTDOWN:
            self.countdown -= dt
            if self.countdown > 120:
                self.countdown_label.text = "3"
            elif self.countdown > 60:
                self.countdown_label.text = "2"
            elif self.countdown > 0:
                self.countdown_label.text = "1"
            else:
                self.countdown_label.text = "GO!"
                self.state = self.STATE_RACE
                self.countdown = -35.0
            for racer in self.racers:
                self._update_racer_visuals(racer)
            return

        if self.state == self.STATE_RACE:
            self.race_time += dt
            if self.countdown < 0:
                self.countdown += dt
                if self.countdown >= 0:
                    self.countdown_label.visible = False
            self._update_player(dt)
            for ai in self.ai_racers:
                self._update_ai(ai, dt)
            for racer in self.racers:
                self._update_racer_visuals(racer)
            if self.player is not None:
                self.lap_label.text = f"LAP {min(self.TOTAL_LAPS, self.player.lap + 1)}/{self.TOTAL_LAPS}"
                self.place_label.text = f"PLACE {self._current_place()}/11"
                boost = " BOOST" if self.player.boost_timer > 0 else ""
                offroad = " OFFROAD" if self.player.offroad else ""
                self.speed_label.text = f"SPEED {abs(self.player.speed):.1f}{boost}{offroad}"
                if self.player.drifting:
                    self.drift_label.text = f"DRIFT {int(self.player.drift_charge)}%"
                else:
                    self.drift_label.text = "SPACE = HOP / DRIFT"
            return

        if self.state == self.STATE_FINISH:
            # Keep AI moving after the player finishes so the track still feels alive.
            for ai in self.ai_racers:
                self._update_ai(ai, dt)
                self._update_racer_visuals(ai)
            self._update_racer_visuals(self.player)

    def draw(self):
        if not self.active:
            return
        self.batch.draw()
