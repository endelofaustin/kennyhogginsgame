"""Theo's Trailer level mechanics: sand yard and arm-wrestling minigame."""

import math
import random
from decimal import Decimal

import pyglet

from engineglobals import EngineGlobals
from lifecycle import GameObject


class DustPuff(GameObject):
    """Short-lived sand dust kicked up by Kenny while moving through the yard."""

    def __init__(self, world_x, world_y):
        self.life = 24
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
            self.parts.append((dot, random.uniform(-0.8, 0.8), random.uniform(0.35, 1.1)))
        super().__init__(lifecycle_manager="PER_MAP")

    def updateloop(self, dt):
        self.life -= 1
        for dot, vx, vy in self.parts:
            dot.x += vx * dt
            dot.y += vy * dt
            if hasattr(dot, "opacity"):
                dot.opacity = max(0, int(255 * self.life / 24))
        if self.life <= 0:
            self.destroy()

    def on_finalDeletion(self):
        for dot, _, _ in self.parts:
            dot.delete()
        self.parts.clear()


class TheoTrailerEncounter(GameObject):
    """Map-scoped Theo encounter with trailer art, sand, table, and arm wrestling."""

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
        self.match_frames = 0
        self.countdown_frames = 0
        self.result_frames = 0
        self.winner = None
        self.c_press_flash = 0
        self.theo_phase = random.uniform(0, math.tau)
        self.theo_burst = 0
        self.fish_progress = 0.0
        self.dust_timer = 0
        self.shapes = []
        self.labels = []
        self.theo_shapes = []
        self.fish_shapes = []

        # The sandy yard occupies the approach to Theo's table.
        self.sand_left = self.table_x - Decimal(360)
        self.sand_right = self.table_x + Decimal(170)
        self.sand_top = self.table_y + Decimal(96)
        self.sand_bottom = self.table_y - Decimal(42)

        EngineGlobals.arm_wrestling_active = False
        EngineGlobals.on_sand = False
        self._build_scene()
        EngineGlobals.window.push_handlers(self)
        super().__init__(lifecycle_manager="PER_MAP")

    def _add_shape(self, shape):
        self.shapes.append(shape)
        return shape

    def _build_scene(self):
        batch = EngineGlobals.main_batch
        bg = EngineGlobals.bg_group
        mid = EngineGlobals.editor_group_mid
        front = EngineGlobals.editor_group_front

        # Trailer sky / yard.
        self._add_shape(pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, EngineGlobals.height,
                                                color=(177, 206, 222), batch=batch, group=bg))
        self._add_shape(pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, 165,
                                                color=(191, 155, 96), batch=batch, group=bg))
        # Trailer body, roof, door and window.
        self._add_shape(pyglet.shapes.Rectangle(420, 235, 330, 230,
                                                color=(218, 211, 176), batch=batch, group=bg))
        self._add_shape(pyglet.shapes.Rectangle(400, 450, 370, 22,
                                                color=(116, 105, 88), batch=batch, group=bg))
        self._add_shape(pyglet.shapes.Rectangle(635, 268, 72, 165,
                                                color=(115, 91, 67), batch=batch, group=bg))
        self._add_shape(pyglet.shapes.Rectangle(468, 330, 105, 70,
                                                color=(95, 151, 180), batch=batch, group=bg))
        self._add_shape(pyglet.shapes.Line(520, 330, 520, 400, width=3,
                                           color=(230, 230, 215), batch=batch, group=bg))
        self._add_shape(pyglet.shapes.Line(468, 365, 573, 365, width=3,
                                           color=(230, 230, 215), batch=batch, group=bg))

        # Sand patch is screen-relative artwork; mechanics use world coordinates below.
        self._add_shape(pyglet.shapes.Rectangle(115, 65, 620, 125,
                                                color=(202, 167, 105), batch=batch, group=mid))
        for i in range(35):
            self._add_shape(pyglet.shapes.Circle(
                120 + (i * 79) % 605,
                72 + (i * 41) % 108,
                1 + i % 2,
                color=(157, 126, 78), batch=batch, group=mid,
            ))

        # Arm-wrestling table.
        tx = float(EngineGlobals.screen_x(self.table_x))
        ty = float(EngineGlobals.screen_y(self.table_y))
        self._add_shape(pyglet.shapes.Rectangle(tx - 78, ty + 34, 156, 18,
                                                color=(92, 58, 39), batch=batch, group=front))
        self._add_shape(pyglet.shapes.Rectangle(tx - 62, ty - 22, 15, 58,
                                                color=(73, 47, 34), batch=batch, group=front))
        self._add_shape(pyglet.shapes.Rectangle(tx + 47, ty - 22, 15, 58,
                                                color=(73, 47, 34), batch=batch, group=front))

        # Theo: deliberately awkward doodle silhouette based on the established art direction.
        self._build_theo(tx + 115, ty + 52)

        self.prompt_label = pyglet.text.Label(
            "Walk up to Theo's table and press D",
            x=EngineGlobals.width // 2, y=560, anchor_x="center",
            font_size=16, color=(35, 25, 20, 255), batch=batch, group=front,
        )
        self.status_label = pyglet.text.Label(
            "",
            x=EngineGlobals.width // 2, y=525, anchor_x="center",
            font_size=19, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255), batch=batch, group=front,
        )
        self.timer_label = pyglet.text.Label(
            "",
            x=EngineGlobals.width // 2, y=495, anchor_x="center",
            font_size=14, color=(255, 255, 255, 255), batch=batch, group=front,
        )
        self.labels.extend((self.prompt_label, self.status_label, self.timer_label))

        # Meter frame and center line; fill moves during the contest.
        self.meter_bg = self._add_shape(pyglet.shapes.Rectangle(205, 455, 390, 24,
                                                                color=(52, 44, 43), batch=batch, group=front))
        self.meter_fill = self._add_shape(pyglet.shapes.Rectangle(400, 458, 0, 18,
                                                                  color=(235, 222, 170), batch=batch, group=front))
        self.meter_center = self._add_shape(pyglet.shapes.Rectangle(398, 452, 4, 30,
                                                                    color=(255, 255, 255), batch=batch, group=front))
        self.meter_bg.visible = False
        self.meter_fill.visible = False
        self.meter_center.visible = False

    def _build_theo(self, x, y):
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_front
        # Head, horse-ish nose, hair, mustache/goatee, stick body, awkward legs/shoes.
        head = pyglet.shapes.Circle(x, y + 80, 24, color=(230, 190, 150), batch=batch, group=group)
        nose = pyglet.shapes.Triangle(x + 15, y + 84, x + 62, y + 76, x + 15, y + 69,
                                     color=(230, 190, 150), batch=batch, group=group)
        body = pyglet.shapes.Line(x, y + 56, x - 4, y - 25, width=5, color=(45, 42, 39), batch=batch, group=group)
        arm1 = pyglet.shapes.Line(x - 2, y + 34, x - 53, y + 12, width=5, color=(45, 42, 39), batch=batch, group=group)
        arm2 = pyglet.shapes.Line(x, y + 34, x + 42, y + 5, width=5, color=(45, 42, 39), batch=batch, group=group)
        leg1 = pyglet.shapes.Line(x - 4, y - 25, x - 23, y - 73, width=5, color=(45, 42, 39), batch=batch, group=group)
        leg2 = pyglet.shapes.Line(x - 4, y - 25, x + 20, y - 69, width=5, color=(45, 42, 39), batch=batch, group=group)
        shoe1 = pyglet.shapes.Rectangle(x - 34, y - 78, 22, 8, color=(30, 28, 27), batch=batch, group=group)
        shoe2 = pyglet.shapes.Rectangle(x + 12, y - 74, 23, 8, color=(30, 28, 27), batch=batch, group=group)
        moustache = pyglet.shapes.Rectangle(x + 8, y + 65, 28, 8, color=(47, 32, 26), batch=batch, group=group)
        goatee = pyglet.shapes.Triangle(x + 12, y + 62, x + 30, y + 62, x + 22, y + 45,
                                       color=(47, 32, 26), batch=batch, group=group)
        self.theo_shapes.extend((head, nose, body, arm1, arm2, leg1, leg2, shoe1, shoe2, moustache, goatee))
        for i in range(7):
            hair = pyglet.shapes.Triangle(x - 21 + i * 7, y + 98,
                                          x - 15 + i * 7, y + 122 + (i % 2) * 9,
                                          x - 8 + i * 7, y + 98,
                                          color=(56, 39, 31), batch=batch, group=group)
            self.theo_shapes.append(hair)
        self.shapes.extend(self.theo_shapes)

    def _near_table(self):
        kenny = getattr(EngineGlobals, "kenny", None)
        if kenny is None:
            return False
        return abs(Decimal(kenny.x_position) - self.table_x) <= Decimal(115) and abs(Decimal(kenny.y_position) - self.table_y) <= Decimal(110)

    def _start_match(self):
        kenny = EngineGlobals.kenny
        self.state = self.COUNTDOWN
        self.countdown_frames = 150
        self.match_frames = 60 * 10
        self.meter = 0.0
        self.winner = None
        self.fish_progress = 0.0
        EngineGlobals.arm_wrestling_active = True
        kenny.x_speed = Decimal(0)
        kenny.y_speed = Decimal(0)
        # Put Kenny at the near side of the table for a repeatable composition.
        kenny.x_position = self.table_x - Decimal(92)
        kenny.y_position = self.table_y
        self.prompt_label.text = ""
        self.status_label.text = "GET READY..."
        self.timer_label.text = "D started it. C wins it."
        self.meter_bg.visible = True
        self.meter_fill.visible = True
        self.meter_center.visible = True
        self._update_meter_visual()

    def _finish_match(self, winner):
        self.state = self.RESULT
        self.winner = winner
        self.result_frames = 240
        EngineGlobals.arm_wrestling_active = True
        self.status_label.text = "KENNY WINS! FISH SLAP THEO!" if winner == "kenny" else "THEO WINS! KENNY GETS THE FISH!"
        self.timer_label.text = ""
        self._create_fish()

    def _create_fish(self):
        for shape in self.fish_shapes:
            shape.delete()
        self.fish_shapes = []
        batch = EngineGlobals.main_batch
        group = EngineGlobals.editor_group_front
        body = pyglet.shapes.Ellipse(0, 0, 34, 13, color=(130, 175, 187), batch=batch, group=group)
        tail = pyglet.shapes.Triangle(0, 0, 0, 0, 0, 0, color=(95, 145, 160), batch=batch, group=group)
        eye = pyglet.shapes.Circle(0, 0, 2, color=(10, 10, 10), batch=batch, group=group)
        self.fish_shapes = [body, tail, eye]

    def _update_fish(self):
        if not self.fish_shapes:
            return
        self.fish_progress = min(1.0, self.fish_progress + 0.055)
        if self.winner == "kenny":
            start_x, end_x = 330, 525
        else:
            start_x, end_x = 535, 335
        x = start_x + (end_x - start_x) * self.fish_progress
        y = 330 + math.sin(self.fish_progress * math.pi) * 85
        body, tail, eye = self.fish_shapes
        body.x, body.y = x, y
        tail.x, tail.y = x - 33, y
        tail.x2, tail.y2 = x - 54, y + 15
        tail.x3, tail.y3 = x - 54, y - 15
        eye.x, eye.y = x + 18, y + 3
        if self.fish_progress >= 1.0:
            self.fish_progress = 0.0

    def _update_meter_visual(self):
        # Meter is centered at x=400. Positive values extend right for Kenny;
        # negative values extend left for Theo.
        width = min(190.0, abs(self.meter) * 1.9)
        if self.meter >= 0:
            self.meter_fill.x = 400
            self.meter_fill.width = width
        else:
            self.meter_fill.x = 400 - width
            self.meter_fill.width = width
        if self.meter > 0:
            self.meter_fill.color = (108, 205, 118)
        elif self.meter < 0:
            self.meter_fill.color = (219, 100, 86)
        else:
            self.meter_fill.color = (235, 222, 170)

    def _update_sand(self, dt):
        if self.state in (self.COUNTDOWN, self.WRESTLING, self.RESULT):
            EngineGlobals.on_sand = False
            return
        kenny = getattr(EngineGlobals, "kenny", None)
        if kenny is None:
            return
        x = Decimal(kenny.x_position)
        y = Decimal(kenny.y_position)
        in_sand = self.sand_left <= x <= self.sand_right and self.sand_bottom <= y <= self.sand_top
        EngineGlobals.on_sand = in_sand
        if in_sand and abs(Decimal(kenny.x_speed)) > Decimal("0.2"):
            self.dust_timer -= dt
            if self.dust_timer <= 0:
                DustPuff(kenny.x_position + Decimal(18), kenny.y_position + Decimal(2))
                self.dust_timer = 9
        else:
            self.dust_timer = 0

    def updateloop(self, dt):
        self._update_sand(dt)
        if self.state == self.IDLE:
            self.prompt_label.text = "Press D to arm wrestle Theo" if self._near_table() else "Walk up to Theo's table and press D"
            return

        if self.state == self.COUNTDOWN:
            self.countdown_frames -= dt
            if self.countdown_frames > 100:
                self.status_label.text = "3"
            elif self.countdown_frames > 50:
                self.status_label.text = "2"
            elif self.countdown_frames > 0:
                self.status_label.text = "1"
            else:
                self.state = self.WRESTLING
                self.status_label.text = "MASH C!"
            return

        if self.state == self.WRESTLING:
            self.match_frames -= dt
            self.theo_phase += 0.11 * dt
            if self.theo_burst > 0:
                theo_force = 0.50
                self.theo_burst -= dt
            else:
                theo_force = 0.18 + max(0.0, math.sin(self.theo_phase)) * 0.18
                if random.random() < 0.012 * max(1.0, float(dt)):
                    self.theo_burst = random.randint(18, 42)
            self.meter -= theo_force * float(dt)
            self.meter *= 0.998 ** float(dt)
            self.meter = max(-100.0, min(100.0, self.meter))
            self.c_press_flash = max(0, self.c_press_flash - dt)
            self.status_label.text = "MASH C!" if self.c_press_flash <= 0 else "PUSH!"
            self.timer_label.text = "{:.1f}s".format(max(0.0, self.match_frames / 60.0))
            self._update_meter_visual()
            if self.meter >= 100.0:
                self._finish_match("kenny")
            elif self.meter <= -100.0:
                self._finish_match("theo")
            elif self.match_frames <= 0:
                self._finish_match("kenny" if self.meter > 0 else "theo")
            return

        if self.state == self.RESULT:
            self.result_frames -= dt
            self._update_fish()
            if self.result_frames <= 0:
                EngineGlobals.arm_wrestling_active = False
                self.state = self.IDLE
                self.prompt_label.text = "Press D for a rematch"
                self.status_label.text = ""
                self.timer_label.text = ""
                self.meter_bg.visible = False
                self.meter_fill.visible = False
                self.meter_center.visible = False
                for shape in self.fish_shapes:
                    shape.delete()
                self.fish_shapes = []

    def on_key_press(self, symbol, modifiers):
        if self.state == self.IDLE:
            if symbol == pyglet.window.key.D and self._near_table():
                self._start_match()
                return pyglet.event.EVENT_HANDLED
            return pyglet.event.EVENT_UNHANDLED

        if self.state == self.WRESTLING and symbol == pyglet.window.key.C:
            self.meter = min(100.0, self.meter + 7.0)
            self.c_press_flash = 7
            self._update_meter_visual()
            return pyglet.event.EVENT_HANDLED

        # During countdown/result, swallow gameplay keys so Kenny stays at table.
        if self.state in (self.COUNTDOWN, self.WRESTLING, self.RESULT):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_finalDeletion(self):
        EngineGlobals.arm_wrestling_active = False
        EngineGlobals.on_sand = False
        try:
            EngineGlobals.window.remove_handlers(self)
        except Exception:
            pass
        for shape in self.fish_shapes:
            shape.delete()
        self.fish_shapes = []
        for label in self.labels:
            label.delete()
        self.labels = []
        for shape in self.shapes:
            shape.delete()
        self.shapes = []
