"""Theo's Trailer: sandy yard plus a full arm-wrestling encounter."""

import math
import random
from decimal import Decimal

import pyglet

from engineglobals import EngineGlobals
from lifecycle import GameObject


class DustPuff(GameObject):
    """Small, short-lived dust cloud produced while Kenny moves through sand."""

    def __init__(self, world_x, world_y):
        self.life = 22.0
        self.parts = []
        sx = float(EngineGlobals.screen_x(world_x))
        sy = float(EngineGlobals.screen_y(world_y))
        for _ in range(5):
            dot = pyglet.shapes.Circle(
                sx + random.uniform(-8, 8),
                sy + random.uniform(0, 5),
                random.uniform(2, 5),
                color=random.choice(((194, 160, 103), (214, 184, 125), (166, 132, 83))),
                batch=EngineGlobals.main_batch,
                group=EngineGlobals.editor_group_mid,
            )
            self.parts.append((dot, random.uniform(-0.7, 0.7), random.uniform(0.25, 0.9)))
        super().__init__(lifecycle_manager="PER_MAP")

    def updateloop(self, dt):
        self.life -= float(dt)
        for dot, vx, vy in self.parts:
            dot.x += vx * float(dt)
            dot.y += vy * float(dt)
            if hasattr(dot, "opacity"):
                dot.opacity = max(0, int(255 * self.life / 22.0))
        if self.life <= 0:
            self.destroy()

    def on_finalDeletion(self):
        for dot, _, _ in self.parts:
            dot.delete()
        self.parts.clear()


class TheoTrailerEncounter(GameObject):
    """World-space Theo/table plus screen-space arm-wrestling minigame."""

    IDLE = "idle"
    COUNTDOWN = "countdown"
    WRESTLING = "wrestling"
    RESULT = "result"

    def __init__(self, chunk, player_spawn, table_position):
        self.chunk = chunk
        self.player_spawn = player_spawn
        self.table_x = Decimal(str(table_position[0]))
        self.table_y = Decimal(str(table_position[1]))
        self.state = self.IDLE
        self.meter = 0.0
        self.match_frames = 0.0
        self.countdown_frames = 0.0
        self.result_frames = 0.0
        self.winner = None
        self.theo_phase = random.uniform(0, math.tau)
        self.theo_burst = 0.0
        self.c_press_flash = 0.0
        self.fish_progress = 0.0
        self.fish_loops = 0
        self.dust_timer = 0.0

        self.world_shapes = []
        self.fixed_shapes = []
        self.world_labels = []
        self.fixed_labels = []
        self.overlay_shapes = []
        self.overlay_labels = []
        self.fish_shapes = []

        self.sand_left = self.table_x - Decimal(350)
        self.sand_right = self.table_x + Decimal(175)
        self.sand_bottom = self.table_y - Decimal(38)
        self.sand_top = self.table_y + Decimal(105)

        EngineGlobals.arm_wrestling_active = False
        EngineGlobals.on_sand = False

        super().__init__(lifecycle_manager="PER_MAP")
        try:
            self._build_world_scene()
            EngineGlobals.window.push_handlers(self)
        except Exception:
            self._cleanup_graphics()
            raise

    def _world_rect(self, world_x, world_y, width, height, color, group):
        shape = pyglet.shapes.Rectangle(
            0, 0, width, height,
            color=color,
            batch=EngineGlobals.main_batch,
            group=group,
        )
        self.world_shapes.append((shape, Decimal(str(world_x)), Decimal(str(world_y))))
        return shape

    def _world_circle(self, world_x, world_y, radius, color, group):
        shape = pyglet.shapes.Circle(
            0, 0, radius,
            color=color,
            batch=EngineGlobals.main_batch,
            group=group,
        )
        self.world_shapes.append((shape, Decimal(str(world_x)), Decimal(str(world_y))))
        return shape

    def _world_label(self, text, world_x, world_y, font_size=13):
        label = pyglet.text.Label(
            text,
            x=0,
            y=0,
            anchor_x="center",
            font_size=font_size,
            weight=pyglet.text.Weight.BOLD,
            color=(35, 25, 20, 255),
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self.world_labels.append((label, Decimal(str(world_x)), Decimal(str(world_y))))
        return label

    def _build_world_scene(self):
        batch = EngineGlobals.main_batch
        bg = EngineGlobals.bg_group
        mid = EngineGlobals.editor_group_mid
        front = EngineGlobals.editor_group_front

        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(
                0, 0, EngineGlobals.width, EngineGlobals.height,
                color=(177, 206, 222), batch=batch, group=bg,
            )
        )
        self.fixed_shapes.append(
            pyglet.shapes.Rectangle(
                0, 0, EngineGlobals.width, 150,
                color=(183, 148, 91), batch=batch, group=bg,
            )
        )

        sand_width = float(self.sand_right - self.sand_left)
        self._world_rect(
            self.sand_left, self.sand_bottom,
            sand_width, float(self.sand_top - self.sand_bottom),
            (202, 167, 105), mid,
        )
        for i in range(34):
            sx = self.sand_left + Decimal((i * 47) % max(1, int(sand_width - 10)))
            sy = self.sand_bottom + Decimal(8 + (i * 29) % max(12, int(self.sand_top - self.sand_bottom - 16)))
            self._world_circle(sx, sy, 1 + i % 2, (151, 119, 72), mid)

        trailer_x = self.table_x + Decimal(70)
        trailer_y = self.table_y + Decimal(95)
        self._world_rect(trailer_x, trailer_y, 330, 220, (218, 211, 176), bg)
        self._world_rect(trailer_x - Decimal(18), trailer_y + Decimal(215), 365, 18, (108, 99, 84), bg)
        self._world_rect(trailer_x + Decimal(220), trailer_y + Decimal(24), 72, 165, (112, 86, 63), bg)
        self._world_rect(trailer_x + Decimal(42), trailer_y + Decimal(82), 108, 70, (95, 151, 180), bg)
        self._world_rect(trailer_x + Decimal(94), trailer_y + Decimal(82), 4, 70, (232, 232, 218), bg)
        self._world_rect(trailer_x + Decimal(42), trailer_y + Decimal(115), 108, 4, (232, 232, 218), bg)

        self._world_rect(self.table_x - Decimal(82), self.table_y + Decimal(34), 164, 20, (92, 58, 39), front)
        self._world_rect(self.table_x - Decimal(64), self.table_y - Decimal(25), 16, 60, (73, 47, 34), front)
        self._world_rect(self.table_x + Decimal(48), self.table_y - Decimal(25), 16, 60, (73, 47, 34), front)
        self._world_rect(self.table_x - Decimal(18), self.table_y + Decimal(48), 36, 7, (140, 31, 28), front)
        self._world_label("ARM WRESTLING", self.table_x, self.table_y + Decimal(78), font_size=12)

        self._build_theo(self.table_x + Decimal(118), self.table_y + Decimal(38))
        self._world_label("COUSIN THEO", self.table_x + Decimal(118), self.table_y + Decimal(188), font_size=13)

        self.prompt_label = pyglet.text.Label(
            "Walk up to Theo's table and press D",
            x=EngineGlobals.width // 2,
            y=565,
            anchor_x="center",
            font_size=16,
            weight=pyglet.text.Weight.BOLD,
            color=(35, 25, 20, 255),
            batch=batch,
            group=front,
        )
        self.fixed_labels.append(self.prompt_label)
        self._sync_world_scene()

    def _build_theo(self, x, y):
        front = EngineGlobals.editor_group_front
        skin = (230, 190, 150)
        dark = (47, 32, 26)
        clothes = (45, 42, 39)

        self._world_circle(x, y + Decimal(82), 25, skin, front)
        self._world_rect(x + Decimal(12), y + Decimal(73), 58, 15, skin, front)
        self._world_circle(x + Decimal(66), y + Decimal(80), 10, skin, front)
        self._world_circle(x - Decimal(7), y + Decimal(86), 3, (20, 20, 20), front)
        self._world_rect(x + Decimal(16), y + Decimal(66), 30, 8, dark, front)
        self._world_rect(x + Decimal(24), y + Decimal(48), 11, 19, dark, front)

        for i in range(7):
            self._world_rect(
                x - Decimal(23) + Decimal(i * 7),
                y + Decimal(101 + (i % 2) * 8),
                5,
                24 + (i % 3) * 5,
                dark,
                front,
            )

        self._world_rect(x - Decimal(4), y + Decimal(2), 8, 58, clothes, front)
        self._world_rect(x - Decimal(48), y + Decimal(25), 48, 7, clothes, front)
        self._world_rect(x + Decimal(2), y + Decimal(22), 45, 7, clothes, front)
        self._world_rect(x - Decimal(23), y - Decimal(47), 7, 52, clothes, front)
        self._world_rect(x + Decimal(12), y - Decimal(45), 7, 50, clothes, front)
        self._world_rect(x - Decimal(34), y - Decimal(53), 23, 8, (28, 27, 25), front)
        self._world_rect(x + Decimal(8), y - Decimal(51), 24, 8, (28, 27, 25), front)

    def _sync_world_scene(self):
        for shape, wx, wy in self.world_shapes:
            shape.x = float(EngineGlobals.screen_x(wx))
            shape.y = float(EngineGlobals.screen_y(wy))
        for label, wx, wy in self.world_labels:
            label.x = float(EngineGlobals.screen_x(wx))
            label.y = float(EngineGlobals.screen_y(wy))

    def _near_table(self):
        kenny = getattr(EngineGlobals, "kenny", None)
        if kenny is None:
            return False
        dx = abs(Decimal(kenny.x_position) - self.table_x)
        dy = abs(Decimal(kenny.y_position) - self.table_y)
        return dx <= Decimal(125) and dy <= Decimal(105)

    def _update_sand(self, dt):
        if self.state != self.IDLE:
            EngineGlobals.on_sand = False
            return
        kenny = getattr(EngineGlobals, "kenny", None)
        if kenny is None:
            EngineGlobals.on_sand = False
            return

        x = Decimal(kenny.x_position)
        y = Decimal(kenny.y_position)
        in_sand = self.sand_left <= x <= self.sand_right and self.sand_bottom <= y <= self.sand_top
        EngineGlobals.on_sand = in_sand

        if in_sand and abs(Decimal(kenny.x_speed)) > Decimal("0.2"):
            self.dust_timer -= float(dt)
            if self.dust_timer <= 0:
                DustPuff(kenny.x_position + Decimal(18), kenny.y_position + Decimal(2))
                self.dust_timer = 8.0
        else:
            self.dust_timer = 0.0

    def _add_overlay_shape(self, shape):
        self.overlay_shapes.append(shape)
        return shape

    def _add_overlay_label(self, label):
        self.overlay_labels.append(label)
        return label

    def _build_match_overlay(self):
        self._clear_match_overlay()
        batch = EngineGlobals.main_batch
        front = EngineGlobals.editor_group_front

        self._add_overlay_shape(
            pyglet.shapes.Rectangle(55, 55, 690, 500, color=(45, 38, 38), batch=batch, group=front)
        )
        self._add_overlay_shape(
            pyglet.shapes.Rectangle(70, 70, 660, 470, color=(232, 216, 174), batch=batch, group=front)
        )

        self.kenny_label = self._add_overlay_label(
            pyglet.text.Label(
                "KENNY", x=175, y=505, anchor_x="center",
                font_size=28, weight=pyglet.text.Weight.BOLD,
                color=(60, 87, 158, 255), batch=batch, group=front,
            )
        )
        self.theo_label = self._add_overlay_label(
            pyglet.text.Label(
                "THEO", x=625, y=505, anchor_x="center",
                font_size=28, weight=pyglet.text.Weight.BOLD,
                color=(158, 69, 56, 255), batch=batch, group=front,
            )
        )
        self.status_label = self._add_overlay_label(
            pyglet.text.Label(
                "GET READY", x=400, y=505, anchor_x="center",
                font_size=22, weight=pyglet.text.Weight.BOLD,
                color=(35, 25, 20, 255), batch=batch, group=front,
            )
        )
        self.timer_label = self._add_overlay_label(
            pyglet.text.Label(
                "D started it — mash C to overpower Theo", x=400, y=465, anchor_x="center",
                font_size=14, color=(35, 25, 20, 255), batch=batch, group=front,
            )
        )

        self._add_overlay_shape(pyglet.shapes.Rectangle(95, 420, 230, 22, color=(84, 77, 70), batch=batch, group=front))
        self.kenny_power = self._add_overlay_shape(pyglet.shapes.Rectangle(99, 424, 0, 14, color=(77, 124, 212), batch=batch, group=front))
        self._add_overlay_shape(pyglet.shapes.Rectangle(475, 420, 230, 22, color=(84, 77, 70), batch=batch, group=front))
        self.theo_power = self._add_overlay_shape(pyglet.shapes.Rectangle(701, 424, 0, 14, color=(199, 86, 70), batch=batch, group=front))
        self._add_overlay_label(pyglet.text.Label("KENNY POWER", x=210, y=445, anchor_x="center", font_size=11,
                                                  color=(35, 25, 20, 255), batch=batch, group=front))
        self._add_overlay_label(pyglet.text.Label("THEO POWER", x=590, y=445, anchor_x="center", font_size=11,
                                                  color=(35, 25, 20, 255), batch=batch, group=front))

        self._add_overlay_shape(pyglet.shapes.Rectangle(150, 105, 500, 32, color=(84, 77, 70), batch=batch, group=front))
        self.tug_fill = self._add_overlay_shape(pyglet.shapes.Rectangle(400, 110, 0, 22, color=(89, 170, 95), batch=batch, group=front))
        self._add_overlay_shape(pyglet.shapes.Rectangle(397, 99, 6, 44, color=(250, 248, 232), batch=batch, group=front))
        self._add_overlay_label(pyglet.text.Label("THEO", x=150, y=82, anchor_x="center", font_size=11,
                                                  color=(35, 25, 20, 255), batch=batch, group=front))
        self._add_overlay_label(pyglet.text.Label("KENNY", x=650, y=82, anchor_x="center", font_size=11,
                                                  color=(35, 25, 20, 255), batch=batch, group=front))

        self.kenny_shoulder = self._add_overlay_shape(pyglet.shapes.Circle(115, 250, 64, color=(225, 151, 153), batch=batch, group=front))
        self.kenny_bicep = self._add_overlay_shape(pyglet.shapes.Circle(205, 285, 59, color=(235, 163, 164), batch=batch, group=front))
        self.kenny_upper = self._add_overlay_shape(pyglet.shapes.Rectangle(120, 245, 180, 72, color=(235, 163, 164), batch=batch, group=front))
        self.kenny_elbow = self._add_overlay_shape(pyglet.shapes.Circle(300, 280, 40, color=(226, 149, 151), batch=batch, group=front))
        self.kenny_forearm = self._add_overlay_shape(pyglet.shapes.Rectangle(300, 260, 100, 54, color=(238, 169, 170), batch=batch, group=front))
        self.kenny_fist = self._add_overlay_shape(pyglet.shapes.Circle(400, 287, 33, color=(241, 176, 177), batch=batch, group=front))

        self.theo_shoulder = self._add_overlay_shape(pyglet.shapes.Circle(685, 250, 64, color=(205, 151, 105), batch=batch, group=front))
        self.theo_bicep = self._add_overlay_shape(pyglet.shapes.Circle(595, 285, 59, color=(219, 166, 119), batch=batch, group=front))
        self.theo_upper = self._add_overlay_shape(pyglet.shapes.Rectangle(500, 245, 180, 72, color=(219, 166, 119), batch=batch, group=front))
        self.theo_elbow = self._add_overlay_shape(pyglet.shapes.Circle(500, 280, 40, color=(207, 151, 103), batch=batch, group=front))
        self.theo_forearm = self._add_overlay_shape(pyglet.shapes.Rectangle(400, 260, 100, 54, color=(225, 175, 127), batch=batch, group=front))
        self.theo_fist = self._add_overlay_shape(pyglet.shapes.Circle(400, 287, 33, color=(229, 181, 134), batch=batch, group=front))

        self._add_overlay_shape(pyglet.shapes.Circle(160, 318, 31, color=(244, 180, 181), batch=batch, group=front))
        self._add_overlay_shape(pyglet.shapes.Circle(640, 318, 31, color=(232, 187, 143), batch=batch, group=front))
        self._update_overlay_visuals()

    def _clear_match_overlay(self):
        for shape in self.fish_shapes:
            shape.delete()
        self.fish_shapes = []
        for label in self.overlay_labels:
            label.delete()
        self.overlay_labels = []
        for shape in self.overlay_shapes:
            shape.delete()
        self.overlay_shapes = []

    def _update_overlay_visuals(self):
        if not self.overlay_shapes:
            return

        kenny_fraction = max(0.0, min(1.0, (self.meter + 100.0) / 200.0))
        theo_fraction = 1.0 - kenny_fraction
        self.kenny_power.width = 222 * kenny_fraction
        theo_width = 222 * theo_fraction
        self.theo_power.width = theo_width
        self.theo_power.x = 701 - theo_width

        tug_width = min(245.0, abs(self.meter) * 2.45)
        if self.meter >= 0:
            self.tug_fill.x = 400
            self.tug_fill.width = tug_width
            self.tug_fill.color = (77, 124, 212)
        else:
            self.tug_fill.x = 400 - tug_width
            self.tug_fill.width = tug_width
            self.tug_fill.color = (199, 86, 70)

        clasp_x = 400 + self.meter * 1.25
        kenny_forearm_width = max(32.0, clasp_x - 300)
        self.kenny_forearm.x = 300
        self.kenny_forearm.width = kenny_forearm_width
        self.kenny_fist.x = clasp_x - 15

        theo_forearm_width = max(32.0, 500 - clasp_x)
        self.theo_forearm.x = clasp_x
        self.theo_forearm.width = theo_forearm_width
        self.theo_fist.x = clasp_x + 15

        pulse = 4.0 * math.sin(self.theo_phase * 2.0)
        self.kenny_bicep.radius = max(52, 59 + (5 if self.c_press_flash > 0 else 0) + pulse)
        self.theo_bicep.radius = max(52, 59 + (6 if self.theo_burst > 0 else 0) - pulse)

    def _start_match(self):
        kenny = EngineGlobals.kenny
        self.state = self.COUNTDOWN
        self.countdown_frames = 150.0
        self.match_frames = 600.0
        self.meter = 0.0
        self.winner = None
        self.fish_progress = 0.0
        self.fish_loops = 0
        EngineGlobals.arm_wrestling_active = True
        EngineGlobals.on_sand = False
        kenny.x_speed = Decimal(0)
        kenny.y_speed = Decimal(0)
        kenny.x_position = self.table_x - Decimal(90)
        kenny.y_position = self.table_y
        self.prompt_label.text = ""
        self._build_match_overlay()

    def _finish_match(self, winner):
        self.state = self.RESULT
        self.winner = winner
        self.result_frames = 250.0
        self.fish_progress = 0.0
        self.fish_loops = 0
        EngineGlobals.arm_wrestling_active = True
        self.status_label.text = "KENNY WINS!" if winner == "kenny" else "THEO WINS!"
        self.timer_label.text = "Winner gets the fish. Loser gets the slap."
        self._create_fish()

    def _create_fish(self):
        for shape in self.fish_shapes:
            shape.delete()
        self.fish_shapes = []
        batch = EngineGlobals.main_batch
        front = EngineGlobals.editor_group_front
        body = pyglet.shapes.Rectangle(0, 0, 58, 24, color=(114, 166, 181), batch=batch, group=front)
        head = pyglet.shapes.Circle(0, 0, 16, color=(131, 183, 195), batch=batch, group=front)
        eye = pyglet.shapes.Circle(0, 0, 3, color=(10, 10, 10), batch=batch, group=front)
        tail_top = pyglet.shapes.Rectangle(0, 0, 19, 9, color=(85, 137, 153), batch=batch, group=front)
        tail_bottom = pyglet.shapes.Rectangle(0, 0, 19, 9, color=(85, 137, 153), batch=batch, group=front)
        self.fish_shapes = [body, head, eye, tail_top, tail_bottom]
        self._add_overlay_label(
            pyglet.text.Label(
                "FISH SLAP!", x=400, y=390, anchor_x="center",
                font_size=30, weight=pyglet.text.Weight.BOLD,
                color=(35, 25, 20, 255), batch=batch, group=front,
            )
        )

    def _update_fish(self, dt):
        if not self.fish_shapes:
            return
        self.fish_progress += 0.045 * float(dt)
        if self.fish_progress >= 1.0:
            self.fish_progress = 0.0
            self.fish_loops += 1

        if self.winner == "kenny":
            start_x, end_x = 220.0, 625.0
        else:
            start_x, end_x = 580.0, 175.0
        x = start_x + (end_x - start_x) * self.fish_progress
        y = 305.0 + math.sin(self.fish_progress * math.pi) * 120.0

        body, head, eye, tail_top, tail_bottom = self.fish_shapes
        body.x = x - 29
        body.y = y - 12
        head.x = x + 29
        head.y = y
        eye.x = x + 35
        eye.y = y + 5
        tail_top.x = x - 47
        tail_top.y = y + 4
        tail_bottom.x = x - 47
        tail_bottom.y = y - 13

    def updateloop(self, dt):
        self._sync_world_scene()
        self._update_sand(dt)

        if self.state == self.IDLE:
            self.prompt_label.text = "Press D to arm wrestle Theo" if self._near_table() else "Walk up to Theo's table and press D"
            return

        if self.state == self.COUNTDOWN:
            self.countdown_frames -= float(dt)
            if self.countdown_frames > 100:
                self.status_label.text = "3"
            elif self.countdown_frames > 50:
                self.status_label.text = "2"
            elif self.countdown_frames > 0:
                self.status_label.text = "1"
            else:
                self.state = self.WRESTLING
                self.status_label.text = "MASH C!"
                self.timer_label.text = "10.0s"
            self._update_overlay_visuals()
            return

        if self.state == self.WRESTLING:
            frame_dt = float(dt)
            self.match_frames -= frame_dt
            self.theo_phase += 0.11 * frame_dt

            if self.theo_burst > 0:
                theo_force = 0.52
                self.theo_burst -= frame_dt
            else:
                theo_force = 0.18 + max(0.0, math.sin(self.theo_phase)) * 0.19
                if random.random() < 0.012 * max(1.0, frame_dt):
                    self.theo_burst = random.randint(18, 42)

            self.meter -= theo_force * frame_dt
            self.meter *= 0.998 ** frame_dt
            self.meter = max(-100.0, min(100.0, self.meter))
            self.c_press_flash = max(0.0, self.c_press_flash - frame_dt)
            self.status_label.text = "PUSH!" if self.c_press_flash > 0 else "MASH C!"
            self.timer_label.text = "{:.1f}s".format(max(0.0, self.match_frames / 60.0))
            self._update_overlay_visuals()

            if self.meter >= 100.0:
                self._finish_match("kenny")
            elif self.meter <= -100.0:
                self._finish_match("theo")
            elif self.match_frames <= 0:
                self._finish_match("kenny" if self.meter > 0 else "theo")
            return

        if self.state == self.RESULT:
            self.result_frames -= float(dt)
            self._update_fish(dt)
            self._update_overlay_visuals()
            if self.result_frames <= 0:
                self._end_match()

    def _end_match(self):
        EngineGlobals.arm_wrestling_active = False
        self.state = self.IDLE
        self.prompt_label.text = "Press D for a rematch"
        self._clear_match_overlay()
        kenny = getattr(EngineGlobals, "kenny", None)
        if kenny is not None:
            kenny.x_position = self.table_x - Decimal(115)
            kenny.y_position = self.table_y
            kenny.x_speed = Decimal(0)
            kenny.y_speed = Decimal(0)

    def on_key_press(self, symbol, modifiers):
        if self.state == self.IDLE:
            if symbol == pyglet.window.key.D and self._near_table():
                self._start_match()
                return pyglet.event.EVENT_HANDLED
            return pyglet.event.EVENT_UNHANDLED

        if self.state == self.WRESTLING and symbol == pyglet.window.key.C:
            self.meter = min(100.0, self.meter + 7.0)
            self.c_press_flash = 8.0
            self._update_overlay_visuals()
            if self.meter >= 100.0:
                self._finish_match("kenny")
            return pyglet.event.EVENT_HANDLED

        if self.state in (self.COUNTDOWN, self.WRESTLING, self.RESULT):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def _cleanup_graphics(self):
        self._clear_match_overlay()
        for label, _, _ in self.world_labels:
            label.delete()
        self.world_labels = []
        for label in self.fixed_labels:
            label.delete()
        self.fixed_labels = []
        for shape, _, _ in self.world_shapes:
            shape.delete()
        self.world_shapes = []
        for shape in self.fixed_shapes:
            shape.delete()
        self.fixed_shapes = []

    def on_finalDeletion(self):
        EngineGlobals.arm_wrestling_active = False
        EngineGlobals.on_sand = False
        try:
            EngineGlobals.window.remove_handlers(self)
        except Exception:
            pass
        self._cleanup_graphics()
