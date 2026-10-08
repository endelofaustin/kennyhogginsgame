"""Pseudo-3D SNES-era kart racing mode for Kenny's Batmobile."""

import math
import random

import pyglet

from engineglobals import EngineGlobals


class Rival:
    def __init__(self, lane, distance, speed, color, name):
        self.lane = float(lane)
        self.distance = float(distance)
        self.speed = float(speed)
        self.color = color
        self.name = name
        self.wobble = random.uniform(0.0, math.tau)
        self.finished_laps = 0


class Mode7Racing:
    """Single-level pseudo-3D racer rendered with projected road strips."""

    STATE_COUNTDOWN = "countdown"
    STATE_RACE = "race"
    STATE_FINISH = "finish"

    SEGMENT_LENGTH = 42.0
    DRAW_SEGMENTS = 56
    TOTAL_LAPS = 3
    MAX_SPEED = 9.6
    BOOST_SPEED = 12.4
    ACCEL = 0.20
    BRAKE = 0.28
    COAST = 0.982
    OFFROAD_DRAG = 0.91
    STEER = 0.037
    DRIFT_STEER = 0.054

    ROAD_PATTERN = (
        (18, 0.00, 0.00),
        (20, 0.015, 0.00),
        (18, 0.032, 0.010),
        (16, 0.000, 0.018),
        (22, -0.026, -0.012),
        (16, -0.045, 0.000),
        (18, 0.000, -0.016),
        (20, 0.024, 0.008),
        (14, 0.048, 0.000),
        (20, -0.020, 0.010),
        (16, 0.000, -0.012),
        (20, -0.035, 0.000),
        (20, 0.000, 0.000),
    )

    def __init__(self, on_exit_to_menu=None):
        self.on_exit_to_menu = on_exit_to_menu
        self.active = False
        self.state = self.STATE_COUNTDOWN
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(0)
        self.road_group = pyglet.graphics.Group(1)
        self.scenery_group = pyglet.graphics.Group(2)
        self.car_group = pyglet.graphics.Group(3)
        self.ui_group = pyglet.graphics.Group(4)

        self.track = []
        self.track_length = 1.0
        self.distance = 0.0
        self.speed = 0.0
        self.player_lane = 0.0
        self.lap = 0
        self.race_time = 0.0
        self.countdown = 180.0
        self.boost_timer = 0.0
        self.drifting = False
        self.drift_charge = 0.0
        self.hop_timer = 0.0
        self.hit_timer = 0.0
        self.launch_window = False
        self.launch_charge = 0.0
        self.launch_penalty = False
        self.finish_place = None
        self.finish_order = []
        self.keys = set()
        self.rng = random.Random(1966)

        self.road_shapes = []
        self.scenery_shapes = []
        self.ai_shapes = []
        self.car_shapes = []
        self.labels = []
        self.car_base_y = {}

        self._build_track_data()
        self._build_static_scene()
        self._build_projected_road_pool()
        self._build_batmobile()
        self._spawn_rivals()
        self._build_ui()

    def _build_track_data(self):
        self.track = []
        index = 0
        for count, curve, hill in self.ROAD_PATTERN:
            for _ in range(count):
                item = {
                    "curve": float(curve),
                    "hill": float(hill),
                    "boost": False,
                    "oil": False,
                    "ramp": False,
                    "side": 0,
                }
                if index % 27 == 11:
                    item["boost"] = True
                if index % 41 == 19:
                    item["oil"] = True
                if index in (74, 171):
                    item["ramp"] = True
                if index % 9 == 0:
                    item["side"] = -1 if (index // 9) % 2 == 0 else 1
                self.track.append(item)
                index += 1
        self.track_length = len(self.track) * self.SEGMENT_LENGTH

    def _build_static_scene(self):
        w = EngineGlobals.width
        h = EngineGlobals.height
        self.sky = pyglet.shapes.Rectangle(
            0, h * 0.47, w, h * 0.53,
            color=(36, 45, 75), batch=self.batch, group=self.bg_group,
        )
        self.ground = pyglet.shapes.Rectangle(
            0, 0, w, h * 0.50,
            color=(37, 74, 53), batch=self.batch, group=self.bg_group,
        )
        self.moon = pyglet.shapes.Circle(
            w - 105, h - 95, 37,
            color=(231, 230, 197), batch=self.batch, group=self.bg_group,
        )
        for i in range(13):
            bw = 35 + (i % 4) * 12
            bh = 50 + (i * 17) % 115
            building = pyglet.shapes.Rectangle(
                i * 67 - 8, h * 0.47, bw, bh,
                color=(21, 25, 42), batch=self.batch, group=self.bg_group,
            )
            self.scenery_shapes.append(building)
        self.horizon_label = pyglet.text.Label(
            "MIDNIGHT BAT CIRCUIT",
            x=w // 2, y=h - 28, anchor_x="center",
            font_size=13, weight=pyglet.text.Weight.BOLD,
            color=(243, 224, 112, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.labels.append(self.horizon_label)

    def _new_triangle(self, color, group):
        tri = pyglet.shapes.Triangle(
            -1000, -1000, -1000, -1000, -1000, -1000,
            color=color, batch=self.batch, group=group,
        )
        self.road_shapes.append(tri)
        return tri

    @staticmethod
    def _set_triangle(tri, p1, p2, p3):
        tri.x, tri.y = p1
        tri.x2, tri.y2 = p2
        tri.x3, tri.y3 = p3

    def _build_projected_road_pool(self):
        self.road_pool = []
        for i in range(self.DRAW_SEGMENTS):
            grass_color = (42, 92, 57) if i % 2 == 0 else (35, 78, 49)
            road_color = (74, 76, 82) if i % 2 == 0 else (68, 70, 77)
            edge_color = (235, 226, 201) if i % 2 == 0 else (194, 56, 56)
            left_grass = self._new_triangle(grass_color, self.road_group)
            left_grass_2 = self._new_triangle(grass_color, self.road_group)
            right_grass = self._new_triangle(grass_color, self.road_group)
            right_grass_2 = self._new_triangle(grass_color, self.road_group)
            road_a = self._new_triangle(road_color, self.road_group)
            road_b = self._new_triangle(road_color, self.road_group)
            edge_l_a = self._new_triangle(edge_color, self.road_group)
            edge_l_b = self._new_triangle(edge_color, self.road_group)
            edge_r_a = self._new_triangle(edge_color, self.road_group)
            edge_r_b = self._new_triangle(edge_color, self.road_group)
            marker = pyglet.shapes.Rectangle(
                -1000, -1000, 1, 1,
                color=(64, 207, 224), batch=self.batch, group=self.scenery_group,
            )
            hazard = pyglet.shapes.Circle(
                -1000, -1000, 1,
                color=(25, 23, 27), batch=self.batch, group=self.scenery_group,
            )
            ramp = pyglet.shapes.Rectangle(
                -1000, -1000, 1, 1,
                color=(218, 164, 70), batch=self.batch, group=self.scenery_group,
            )
            scenery = pyglet.shapes.Rectangle(
                -1000, -1000, 1, 1,
                color=(26, 48, 39), batch=self.batch, group=self.scenery_group,
            )
            self.scenery_shapes.extend((marker, hazard, ramp, scenery))
            self.road_pool.append({
                "tris": (
                    left_grass, left_grass_2, right_grass, right_grass_2,
                    road_a, road_b, edge_l_a, edge_l_b, edge_r_a, edge_r_b,
                ),
                "marker": marker,
                "hazard": hazard,
                "ramp": ramp,
                "scenery": scenery,
            })

    def _build_batmobile(self):
        self.bat_shadow = pyglet.shapes.Ellipse(
            EngineGlobals.width / 2, 66, 73, 21,
            color=(18, 20, 25), batch=self.batch, group=self.car_group,
        )
        body = pyglet.shapes.Rectangle(
            EngineGlobals.width / 2 - 60, 58, 120, 37,
            color=(24, 27, 34), batch=self.batch, group=self.car_group,
        )
        nose = pyglet.shapes.Triangle(
            EngineGlobals.width / 2 - 58, 74,
            EngineGlobals.width / 2 + 58, 74,
            EngineGlobals.width / 2, 122,
            color=(31, 35, 44), batch=self.batch, group=self.car_group,
        )
        cockpit = pyglet.shapes.Circle(
            EngineGlobals.width / 2, 88, 21,
            color=(57, 72, 86), batch=self.batch, group=self.car_group,
        )
        kenny_head = pyglet.shapes.Circle(
            EngineGlobals.width / 2, 91, 12,
            color=(229, 154, 158), batch=self.batch, group=self.car_group,
        )
        fin_l = pyglet.shapes.Triangle(
            EngineGlobals.width / 2 - 49, 90,
            EngineGlobals.width / 2 - 78, 116,
            EngineGlobals.width / 2 - 29, 103,
            color=(18, 20, 26), batch=self.batch, group=self.car_group,
        )
        fin_r = pyglet.shapes.Triangle(
            EngineGlobals.width / 2 + 49, 90,
            EngineGlobals.width / 2 + 78, 116,
            EngineGlobals.width / 2 + 29, 103,
            color=(18, 20, 26), batch=self.batch, group=self.car_group,
        )
        bat_mark = pyglet.shapes.Triangle(
            EngineGlobals.width / 2, 67,
            EngineGlobals.width / 2 - 15, 78,
            EngineGlobals.width / 2 + 15, 78,
            color=(236, 204, 67), batch=self.batch, group=self.car_group,
        )
        wheels = []
        for offset in (-53, -27, 27, 53):
            wheel = pyglet.shapes.Circle(
                EngineGlobals.width / 2 + offset, 58, 10,
                color=(12, 13, 16), batch=self.batch, group=self.car_group,
            )
            wheels.append(wheel)
        self.car_shapes.extend(
            [self.bat_shadow, body, nose, cockpit, kenny_head, fin_l, fin_r, bat_mark] + wheels
        )
        for shape in self.car_shapes:
            self.car_base_y[id(shape)] = getattr(shape, "y", 0.0)

    def _spawn_rivals(self):
        colors = (
            (199, 62, 62), (69, 120, 208), (72, 164, 92), (220, 180, 58),
            (155, 84, 191), (232, 120, 67), (86, 190, 188),
        )
        self.rivals = []
        for i in range(7):
            self.rivals.append(
                Rival(
                    lane=-0.72 + (i % 4) * 0.48,
                    distance=260.0 + i * 145.0,
                    speed=7.2 + (i % 4) * 0.22,
                    color=colors[i],
                    name="RIVAL {}".format(i + 1),
                )
            )
            kart = pyglet.shapes.Rectangle(
                -1000, -1000, 28, 16,
                color=colors[i], batch=self.batch, group=self.scenery_group,
            )
            head = pyglet.shapes.Circle(
                -1000, -1000, 5,
                color=(220, 172, 126), batch=self.batch, group=self.scenery_group,
            )
            self.ai_shapes.append((kart, head))

    def _build_ui(self):
        self.lap_label = pyglet.text.Label(
            "LAP 1/3", x=18, y=EngineGlobals.height - 28,
            font_size=14, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        self.place_label = pyglet.text.Label(
            "PLACE 1/8", x=18, y=EngineGlobals.height - 51,
            font_size=12, color=(255, 255, 255, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.speed_label = pyglet.text.Label(
            "BATMOBILE 0", x=18, y=20,
            font_size=12, color=(241, 224, 135, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.drift_label = pyglet.text.Label(
            "SPACE = DRIFT", x=EngineGlobals.width - 18, y=20,
            anchor_x="right", font_size=11,
            color=(212, 225, 244, 255), batch=self.batch, group=self.ui_group,
        )
        self.countdown_label = pyglet.text.Label(
            "3", x=EngineGlobals.width // 2, y=EngineGlobals.height // 2 + 50,
            anchor_x="center", anchor_y="center", font_size=72,
            weight=pyglet.text.Weight.BOLD, color=(244, 226, 105, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.help_label = pyglet.text.Label(
            "↑ accelerate  ↓ brake  ← → steer  SPACE drift/hop  ESC menu",
            x=EngineGlobals.width // 2, y=EngineGlobals.height - 52,
            anchor_x="center", font_size=9,
            color=(218, 225, 236, 255), batch=self.batch, group=self.ui_group,
        )
        self.labels.extend((
            self.lap_label, self.place_label, self.speed_label,
            self.drift_label, self.countdown_label, self.help_label,
        ))
        self.finish_panel = pyglet.shapes.Rectangle(
            145, 160, 510, 270, color=(22, 25, 35),
            batch=self.batch, group=self.ui_group,
        )
        self.finish_panel.opacity = 235
        self.finish_panel.visible = False
        self.finish_title = pyglet.text.Label(
            "", x=EngineGlobals.width // 2, y=370,
            anchor_x="center", font_size=30, weight=pyglet.text.Weight.BOLD,
            color=(246, 228, 115, 255), batch=self.batch, group=self.ui_group,
        )
        self.finish_result = pyglet.text.Label(
            "", x=EngineGlobals.width // 2, y=315,
            anchor_x="center", font_size=17,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        self.finish_prompt = pyglet.text.Label(
            "", x=EngineGlobals.width // 2, y=245,
            anchor_x="center", font_size=12,
            color=(216, 224, 238, 255), batch=self.batch, group=self.ui_group,
        )
        self.labels.extend((self.finish_title, self.finish_result, self.finish_prompt))

    def start(self):
        self.active = True
        self.state = self.STATE_COUNTDOWN
        self.distance = 0.0
        self.speed = 0.0
        self.player_lane = 0.0
        self.lap = 0
        self.race_time = 0.0
        self.countdown = 180.0
        self.boost_timer = 0.0
        self.drifting = False
        self.drift_charge = 0.0
        self.hop_timer = 0.0
        self.hit_timer = 0.0
        self.launch_window = False
        self.launch_charge = 0.0
        self.launch_penalty = False
        self.finish_place = None
        self.finish_order = []
        self.keys.clear()
        self.countdown_label.visible = True
        self.countdown_label.text = "3"
        self.finish_panel.visible = False
        self.finish_title.text = ""
        self.finish_result.text = ""
        self.finish_prompt.text = ""
        for i, rival in enumerate(self.rivals):
            rival.distance = 260.0 + i * 145.0
            rival.finished_laps = 0

    def stop(self):
        self.active = False
        self.keys.clear()

    def _segment_index(self, distance):
        return int(distance // self.SEGMENT_LENGTH) % len(self.track)

    def _segment_at(self, distance):
        return self.track[self._segment_index(distance)]

    def _project_road(self):
        w = float(EngineGlobals.width)
        h = float(EngineGlobals.height)
        horizon = h * 0.48
        base_center = w * 0.5
        curve_acc = 0.0
        lateral_shift = -self.player_lane * 220.0
        hill_acc = 0.0
        centers = []
        widths = []
        ys = []
        for i in range(self.DRAW_SEGMENTS + 1):
            t = i / float(self.DRAW_SEGMENTS)
            perspective = t ** 1.75
            world_distance = self.distance + (self.DRAW_SEGMENTS - i) * self.SEGMENT_LENGTH
            seg = self._segment_at(world_distance)
            curve_acc += seg["curve"] * (0.55 + perspective * 2.1)
            hill_acc += seg["hill"] * (0.25 + perspective * 0.8)
            y = horizon + perspective * (h - horizon + 34.0)
            y += hill_acc * 115.0 * perspective
            road_half = 24.0 + perspective * 360.0
            center = base_center + lateral_shift * perspective + curve_acc * 430.0 * perspective
            centers.append(center)
            widths.append(road_half)
            ys.append(y)
        for i in range(self.DRAW_SEGMENTS):
            pool = self.road_pool[i]
            far_i = i
            near_i = i + 1
            c1, c2 = centers[far_i], centers[near_i]
            r1, r2 = widths[far_i], widths[near_i]
            y1, y2 = ys[far_i], ys[near_i]
            l1, rr1 = c1 - r1, c1 + r1
            l2, rr2 = c2 - r2, c2 + r2
            edge1 = max(3.0, r1 * 0.065)
            edge2 = max(4.0, r2 * 0.065)
            (
                lg1, lg2, rg1, rg2, road1, road2,
                el1, el2, er1, er2,
            ) = pool["tris"]
            self._set_triangle(lg1, (0, y1), (l1, y1), (0, y2))
            self._set_triangle(lg2, (0, y2), (l1, y1), (l2, y2))
            self._set_triangle(rg1, (rr1, y1), (w, y1), (rr2, y2))
            self._set_triangle(rg2, (w, y1), (w, y2), (rr2, y2))
            self._set_triangle(road1, (l1, y1), (rr1, y1), (l2, y2))
            self._set_triangle(road2, (rr1, y1), (rr2, y2), (l2, y2))
            self._set_triangle(el1, (l1, y1), (l1 + edge1, y1), (l2, y2))
            self._set_triangle(el2, (l1 + edge1, y1), (l2 + edge2, y2), (l2, y2))
            self._set_triangle(er1, (rr1 - edge1, y1), (rr1, y1), (rr2 - edge2, y2))
            self._set_triangle(er2, (rr1, y1), (rr2, y2), (rr2 - edge2, y2))
            world_distance = self.distance + (self.DRAW_SEGMENTS - i) * self.SEGMENT_LENGTH
            seg = self._segment_at(world_distance)
            p = max(0.04, min(1.0, (i + 1) / float(self.DRAW_SEGMENTS)))
            marker = pool["marker"]
            hazard = pool["hazard"]
            ramp = pool["ramp"]
            scenery = pool["scenery"]
            marker.visible = bool(seg["boost"])
            hazard.visible = bool(seg["oil"])
            ramp.visible = bool(seg["ramp"])
            scenery.visible = bool(seg["side"])
            scale = p ** 1.5
            if marker.visible:
                marker.width = max(3.0, 100.0 * scale)
                marker.height = max(2.0, 10.0 * scale)
                marker.x = c2 - marker.width / 2
                marker.y = y2 - marker.height / 2
            if hazard.visible:
                hazard.radius = max(2.0, 24.0 * scale)
                hazard.position = (c2 + r2 * 0.18, y2)
            if ramp.visible:
                ramp.width = max(4.0, 95.0 * scale)
                ramp.height = max(2.0, 22.0 * scale)
                ramp.position = (c2 - ramp.width / 2, y2 - ramp.height / 2)
            if scenery.visible:
                scenery.width = max(4.0, 28.0 * scale)
                scenery.height = max(7.0, 78.0 * scale)
                side = seg["side"]
                scenery.x = c2 + side * (r2 + 34.0 * scale)
                scenery.y = y2
        return centers, widths, ys

    def _update_rival_visuals(self, centers, widths, ys):
        for (kart, head), rival in zip(self.ai_shapes, self.rivals):
            relative = (rival.distance - self.distance) % self.track_length
            max_draw = self.DRAW_SEGMENTS * self.SEGMENT_LENGTH
            if relative <= 20 or relative >= max_draw:
                kart.visible = False
                head.visible = False
                continue
            distance_from_far = max_draw - relative
            t = max(0.0, min(1.0, distance_from_far / max_draw))
            idx = int(t * (self.DRAW_SEGMENTS - 1))
            p = (idx + 1) / float(self.DRAW_SEGMENTS)
            scale = max(0.16, p ** 1.35)
            center = centers[idx]
            road_half = widths[idx]
            y = ys[idx]
            x = center + rival.lane * road_half * 0.72
            kart.visible = True
            head.visible = True
            kart.width = 34 * scale
            kart.height = 18 * scale
            kart.x = x - kart.width / 2
            kart.y = y
            head.radius = max(2, 6 * scale)
            head.position = (x, y + kart.height * 0.8)

    def _track_interactions(self):
        current = self._segment_at(self.distance + 12.0)
        if current["boost"] and abs(self.player_lane) < 0.78:
            self.boost_timer = max(self.boost_timer, 55.0)
            self.speed = max(self.speed, 10.2)
        if current["oil"] and abs(self.player_lane - 0.18) < 0.28 and self.hit_timer <= 0:
            self.speed *= 0.58
            self.player_lane += self.rng.choice((-0.42, 0.42))
            self.hit_timer = 55.0
        if current["ramp"] and abs(self.player_lane) < 0.85 and self.hop_timer <= 0:
            self.hop_timer = 34.0
            self.boost_timer = max(self.boost_timer, 28.0)

    def _check_rival_collision(self):
        if self.hit_timer > 0:
            return
        for rival in self.rivals:
            relative = (rival.distance - self.distance) % self.track_length
            if relative < 42.0 and abs(rival.lane - self.player_lane) < 0.28:
                self.speed *= 0.72
                self.player_lane += -0.18 if rival.lane > self.player_lane else 0.18
                self.hit_timer = 24.0
                break

    def _update_player(self, dt):
        up = pyglet.window.key.UP in self.keys
        down = pyglet.window.key.DOWN in self.keys
        left = pyglet.window.key.LEFT in self.keys
        right = pyglet.window.key.RIGHT in self.keys
        space = pyglet.window.key.SPACE in self.keys
        if up:
            self.speed += self.ACCEL * dt
        elif down:
            self.speed -= self.BRAKE * dt
        else:
            self.speed *= self.COAST ** dt
        max_speed = self.BOOST_SPEED if self.boost_timer > 0 else self.MAX_SPEED
        if self.boost_timer > 0:
            self.boost_timer -= dt
            self.speed += 0.045 * dt
        self.speed = max(-2.3, min(max_speed, self.speed))
        steer = (-1 if left else 0) + (1 if right else 0)
        steer_rate = self.DRIFT_STEER if self.drifting else self.STEER
        if steer and abs(self.speed) > 0.2:
            self.player_lane += steer * steer_rate * dt * (0.62 + abs(self.speed) / 9.5)
            if self.drifting and space:
                self.drift_charge = min(100.0, self.drift_charge + (1.0 + abs(self.speed) * 0.07) * dt)
        current_curve = self._segment_at(self.distance + 80.0)["curve"]
        self.player_lane -= current_curve * max(0.0, self.speed) * 0.25 * dt
        if abs(self.player_lane) > 1.04:
            self.speed *= self.OFFROAD_DRAG ** dt
        self.player_lane = max(-1.43, min(1.43, self.player_lane))
        if self.hop_timer > 0:
            self.hop_timer -= dt
            hop = math.sin(max(0.0, min(math.pi, (self.hop_timer / 34.0) * math.pi))) * 10.0
        else:
            hop = 0.0
        for shape in self.car_shapes:
            try:
                shape.y = self.car_base_y[id(shape)] + hop
            except Exception:
                pass
        if self.hit_timer > 0:
            self.hit_timer -= dt
        self.distance += self.speed * dt
        while self.distance >= self.track_length:
            self.distance -= self.track_length
            self.lap += 1
            if self.lap >= self.TOTAL_LAPS:
                self._finish_race()
                return
        while self.distance < 0:
            self.distance += self.track_length
        self._track_interactions()
        self._check_rival_collision()

    def _update_rivals(self, dt):
        for rival in self.rivals:
            idx = self._segment_index(rival.distance)
            seg = self.track[idx]
            curve_penalty = min(1.0, abs(seg["curve"]) * 11.0)
            target_speed = rival.speed * (1.0 - curve_penalty * 0.18)
            if seg["boost"]:
                target_speed += 0.65
            if seg["oil"] and abs(rival.lane - 0.18) < 0.25:
                target_speed *= 0.72
            rival.wobble += 0.015 * dt
            rival.lane += math.sin(rival.wobble) * 0.0025 * dt
            rival.lane = max(-0.84, min(0.84, rival.lane))
            rival.distance += target_speed * dt
            while rival.distance >= self.track_length:
                rival.distance -= self.track_length
                rival.finished_laps += 1

    def _place(self):
        player_progress = self.lap * self.track_length + self.distance
        ahead = 0
        for rival in self.rivals:
            rival_progress = rival.finished_laps * self.track_length + rival.distance
            if rival_progress > player_progress:
                ahead += 1
        return ahead + 1

    def _finish_race(self):
        self.state = self.STATE_FINISH
        self.speed = 0.0
        self.finish_place = self._place()
        self.finish_panel.visible = True
        self.finish_title.text = "BATMOBILE FINISH!"
        self.finish_result.text = "Kenny finished {} of 8".format(self.finish_place)
        self.finish_prompt.text = "ENTER race again   •   ESC main menu"

    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        if symbol == pyglet.window.key.ESCAPE:
            self.stop()
            if self.on_exit_to_menu:
                self.on_exit_to_menu()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_FINISH:
            if symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
                self.start()
            return pyglet.event.EVENT_HANDLED
        self.keys.add(symbol)
        if self.state == self.STATE_RACE and symbol == pyglet.window.key.SPACE and not self.drifting:
            self.drifting = True
            self.drift_charge = 0.0
            self.hop_timer = max(self.hop_timer, 14.0)
        return pyglet.event.EVENT_HANDLED

    def on_key_release(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        self.keys.discard(symbol)
        if self.state == self.STATE_RACE and symbol == pyglet.window.key.SPACE and self.drifting:
            if self.drift_charge >= 70:
                self.boost_timer = max(self.boost_timer, 72.0)
                self.speed = max(self.speed, 10.8)
            elif self.drift_charge >= 35:
                self.boost_timer = max(self.boost_timer, 40.0)
                self.speed = max(self.speed, 9.8)
            self.drifting = False
            self.drift_charge = 0.0
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
                self.launch_window = False
            elif self.countdown > 20:
                self.countdown_label.text = "1"
                self.launch_window = True
                if pyglet.window.key.UP in self.keys:
                    self.launch_charge = min(100.0, self.launch_charge + 2.4 * dt)
            elif self.countdown > 0:
                self.countdown_label.text = "GO!"
            else:
                self.state = self.STATE_RACE
                self.countdown_label.visible = False
                if self.launch_charge >= 45:
                    self.speed = 7.4
                    self.boost_timer = 55.0
                elif pyglet.window.key.UP in self.keys and self.launch_charge < 12:
                    self.speed = 1.0
                    self.launch_penalty = True
            centers, widths, ys = self._project_road()
            self._update_rival_visuals(centers, widths, ys)
            return
        if self.state == self.STATE_RACE:
            self.race_time += dt
            self._update_player(dt)
            self._update_rivals(dt)
            centers, widths, ys = self._project_road()
            self._update_rival_visuals(centers, widths, ys)
            self.lap_label.text = "LAP {}/{}".format(min(self.TOTAL_LAPS, self.lap + 1), self.TOTAL_LAPS)
            self.place_label.text = "PLACE {}/8".format(self._place())
            boost = "  BOOST!" if self.boost_timer > 0 else ""
            self.speed_label.text = "BATMOBILE {:.1f}{}".format(abs(self.speed), boost)
            self.drift_label.text = (
                "DRIFT {}%".format(int(self.drift_charge))
                if self.drifting else "SPACE = DRIFT"
            )
            return
        if self.state == self.STATE_FINISH:
            self._update_rivals(dt)
            centers, widths, ys = self._project_road()
            self._update_rival_visuals(centers, widths, ys)

    def draw(self):
        if not self.active:
            return
        self.batch.draw()
