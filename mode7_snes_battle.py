"""Behind-the-kart Mode-7-style battle mode for 3D Reaching."""

import math
import random

import pyglet

import mode7_full_content as full_content
import mode7_full_core as coremod
import mode7_full_flow as flowmod
import mode7_racing as base
from engineglobals import EngineGlobals
from mode7_battle import HogginOutMode7Racing
from mode7_deluxe_content import MUSIC_LIBRARY
from mode7_snes_battle_content import (
    MODE7_BATTLE_ARENAS,
    MODE7_BATTLE_BALLOONS,
    MODE7_BATTLE_ENTRY,
    MODE7_BATTLE_ITEMS,
    MODE7_BATTLE_RULES,
    MODE7_BATTLE_TIME_SECONDS,
    WORLD_H,
    WORLD_W,
)

for module in (full_content, coremod, flowmod):
    modes = tuple(getattr(module, "MODES", ()))
    if not any(entry[0] == MODE7_BATTLE_ENTRY[0] for entry in modes):
        module.MODES = modes + (MODE7_BATTLE_ENTRY,)


class Mode7ArenaBattleRacing(HogginOutMode7Racing):
    """Deluxe 3D Reaching plus a genuine behind-kart arena battle mode."""

    STATE_M7_RULES = "mode7_battle_rules"
    STATE_M7_ARENA = "mode7_battle_arena"
    STATE_M7_COUNTDOWN = "mode7_battle_countdown"
    STATE_M7_BATTLE = "mode7_battle"
    STATE_M7_FINISH = "mode7_battle_finish"

    NEAR_CLIP = 58.0
    VIEW_DISTANCE = 1480.0
    CAMERA_HEIGHT = 55.0
    FOCAL = 340.0
    RACER_RADIUS = 28.0

    def __init__(self, on_exit_to_menu=None):
        self.selected_m7_rule = 0
        self.selected_m7_arena = 0
        self.m7_arena = None
        self.m7_rng = random.Random(16001992)
        self.m7_racers = []
        self.m7_player = None
        self.m7_shapes = []
        self.m7_labels = []
        self.m7_grid_lines = []
        self.m7_grid_segments = []
        self.m7_walls = []
        self.m7_hazards = []
        self.m7_boosts = []
        self.m7_portals = []
        self.m7_sweepers = []
        self.m7_item_boxes = []
        self.m7_coins = []
        self.m7_projectiles = []
        self.m7_mines = []
        self.m7_ai_shapes = []
        self.m7_radar_dots = []
        self.m7_countdown = 180.0
        self.m7_time_frames = 0.0
        self.m7_event_timer = 0.0
        self.m7_world_clock = 0.0
        self.m7_camera_shake = 0.0
        self.m7_shake_x = 0.0
        self.m7_shake_y = 0.0
        self.m7_finish_place = None
        self.m7_results = []
        super().__init__(on_exit_to_menu=on_exit_to_menu)

    def _build_mode_select(self):
        """Five-row mode menu after both battle modes are installed."""
        self._clear_battle()
        self._clear_mode7_battle()
        self._clear_selection()
        self.state = self.STATE_MODE
        self._selection_header(
            "3D REACHING",
            "GRAND PRIX • QUICK RACE • TIME TRIAL • HOGGIN OUT • MODE 7 BATTLE",
        )
        self.mode_panels = []
        modes = tuple(coremod.MODES)
        ys = (446, 366, 286, 206, 126)
        for i, (name, note) in enumerate(modes):
            y = ys[i] if i < len(ys) else 126 - (i - 4) * 72
            panel = pyglet.shapes.Rectangle(
                145, y - 27, 510, 56,
                color=(112, 123, 153) if i == self.selected_mode else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.mode_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                name, x=400, y=y + 6, anchor_x="center",
                font_size=16, weight=pyglet.text.Weight.BOLD,
                color=(255, 239, 165, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                note, x=400, y=y - 13, anchor_x="center", font_size=8,
                color=(207, 219, 236, 255), batch=self.batch, group=self.ui_group,
            ))

    # ---------- selection flow ----------

    def _build_mode7_rules(self):
        self._stop_race_music()
        self._clear_mode7_battle()
        self._clear_selection()
        self.state = self.STATE_M7_RULES
        self._selection_header(
            "MODE 7 BATTLE",
            "BEHIND-THE-KART PSEUDO-3D ARENA COMBAT",
        )
        self.m7_rule_panels = []
        for i, (name, note) in enumerate(MODE7_BATTLE_RULES):
            y = 410 - i * 125
            panel = pyglet.shapes.Rectangle(
                145, y - 42, 510, 86,
                color=(111, 117, 153) if i == self.selected_m7_rule else (45, 50, 64),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.m7_rule_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                name, x=400, y=y + 12, anchor_x="center",
                font_size=20, weight=pyglet.text.Weight.BOLD,
                color=(255, 235, 151, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                note, x=400, y=y - 17, anchor_x="center", font_size=10,
                color=(206, 220, 239, 255), batch=self.batch, group=self.ui_group,
            ))

    def _refresh_mode7_rules(self):
        for i, panel in enumerate(self.m7_rule_panels):
            panel.color = (111, 117, 153) if i == self.selected_m7_rule else (45, 50, 64)

    def _build_mode7_arena_select(self):
        self._stop_race_music()
        self._clear_mode7_battle()
        self._clear_selection()
        self.state = self.STATE_M7_ARENA
        self._selection_header(
            "MODE 7 BATTLE",
            "CHOOSE ONE OF 8 CUSTOM PSEUDO-3D BATTLE COURSES",
        )
        self.m7_arena_panels = []
        for i, arena in enumerate(MODE7_BATTLE_ARENAS):
            col, row = i % 4, i // 4
            x = 105 + col * 195
            y = 370 - row * 190
            panel = pyglet.shapes.Rectangle(
                x - 86, y - 68, 172, 136,
                color=(108, 113, 151) if i == self.selected_m7_arena else (44, 49, 62),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.m7_arena_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                arena["name"].upper(), x=x, y=y + 42, anchor_x="center",
                multiline=True, width=158, align="center", font_size=9,
                weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                arena["tagline"], x=x, y=y + 13, anchor_x="center", anchor_y="top",
                multiline=True, width=152, align="center", font_size=7,
                color=(200, 214, 234, 255), batch=self.batch, group=self.ui_group,
            ))
        self.m7_arena_detail = pyglet.text.Label(
            "", x=400, y=56, anchor_x="center", font_size=9,
            color=(255, 220, 132, 255), batch=self.batch, group=self.ui_group,
        )
        self.selection_labels.append(self.m7_arena_detail)
        self._refresh_mode7_arena_select()

    def _refresh_mode7_arena_select(self):
        for i, panel in enumerate(self.m7_arena_panels):
            panel.color = (108, 113, 151) if i == self.selected_m7_arena else (44, 49, 62)
        arena = MODE7_BATTLE_ARENAS[self.selected_m7_arena]
        rule = MODE7_BATTLE_RULES[self.selected_m7_rule][0]
        self.m7_arena_detail.text = "{} • {} • MUSIC {}".format(
            rule, arena["hazard_name"], self._music_display(arena["music"])
        )

    # ---------- cleanup ----------

    @staticmethod
    def _delete_shape(item):
        try:
            item.delete()
        except Exception:
            pass

    def _clear_mode7_battle(self):
        for projectile in list(getattr(self, "m7_projectiles", [])):
            self._delete_shape(projectile.get("shape"))
        for mine in list(getattr(self, "m7_mines", [])):
            self._delete_shape(mine.get("shape"))
        self.m7_projectiles = []
        self.m7_mines = []

        for collection_name in (
            "m7_shapes", "m7_labels", "m7_grid_lines", "m7_radar_dots"
        ):
            collection = getattr(self, collection_name, [])
            for item in list(collection):
                self._delete_shape(item)
            collection.clear()

        for racer in list(getattr(self, "m7_racers", [])):
            for key in ("body", "driver"):
                shape = racer.get(key)
                if shape is not None:
                    self._delete_shape(shape)
        self.m7_racers = []
        self.m7_player = None
        self.m7_ai_shapes = []
        self.m7_grid_segments = []
        self.m7_walls = []
        self.m7_hazards = []
        self.m7_boosts = []
        self.m7_portals = []
        self.m7_sweepers = []
        self.m7_item_boxes = []
        self.m7_coins = []
        self.m7_arena = None

    # ---------- world / visuals ----------

    def _make_m7_racer(self, profile, spawn, is_player=False):
        x, z, angle = spawn
        body = None
        driver = None
        if not is_player:
            body = pyglet.shapes.Rectangle(
                -1000, -1000, 8, 8, color=profile["color"],
                batch=self.batch, group=self.car_group,
            )
            driver = pyglet.shapes.Circle(
                -1000, -1000, 3, color=tuple(min(255, c + 35) for c in profile["color"]),
                batch=self.batch, group=self.car_group,
            )
        racer = {
            "name": profile["name"],
            "profile": profile,
            "is_player": bool(is_player),
            "x": float(x), "z": float(z), "angle": float(angle),
            "speed": 0.0,
            "balloons": MODE7_BATTLE_BALLOONS,
            "score": 0,
            "coins": 0,
            "held_item": None,
            "turbo": 0.0,
            "shield": 0.0,
            "star": 0.0,
            "hop": 0.0,
            "invuln": 0.0,
            "hit_cooldown": 0.0,
            "hazard_cooldown": 0.0,
            "portal_cooldown": 0.0,
            "item_use_cooldown": 0.0,
            "respawn_timer": 0.0,
            "eliminated": False,
            "placement": None,
            "body": body,
            "driver": driver,
            "ai_wander": self.m7_rng.uniform(-0.35, 0.35),
        }
        return racer

    def _build_m7_grid(self):
        self.m7_grid_segments = []
        step = 180.0
        x = 0.0
        while x <= WORLD_W + 0.1:
            z = 0.0
            while z < WORLD_H:
                self.m7_grid_segments.append((x, z, x, min(WORLD_H, z + step)))
                z += step
            x += step
        z = 0.0
        while z <= WORLD_H + 0.1:
            x = 0.0
            while x < WORLD_W:
                self.m7_grid_segments.append((x, z, min(WORLD_W, x + step), z))
                x += step
            z += step
        for _ in self.m7_grid_segments:
            line = pyglet.shapes.Line(
                -1000, -1000, -1000, -1000, thickness=1,
                color=self.m7_arena["grid"], batch=self.batch, group=self.road_group,
            )
            line.visible = False
            self.m7_grid_lines.append(line)

    def _build_m7_world_shapes(self):
        arena = self.m7_arena
        w, h = EngineGlobals.width, EngineGlobals.height
        self.m7_sky = pyglet.shapes.Rectangle(
            0, h * 0.49, w, h * 0.51, color=arena["sky"],
            batch=self.batch, group=self.bg_group,
        )
        self.m7_floor = pyglet.shapes.Rectangle(
            0, 0, w, h * 0.51, color=arena["floor_a"],
            batch=self.batch, group=self.bg_group,
        )
        self.m7_horizon = pyglet.shapes.Line(
            0, h * 0.49, w, h * 0.49, thickness=3, color=arena["grid"],
            batch=self.batch, group=self.road_group,
        )
        self.m7_shapes.extend((self.m7_sky, self.m7_floor, self.m7_horizon))

        if arena["fog"]:
            fog = pyglet.shapes.Rectangle(
                0, h * 0.33, w, h * 0.32, color=(135, 137, 153),
                batch=self.batch, group=self.scenery_group,
            )
            fog.opacity = min(135, max(20, arena["fog"] * 3))
            self.m7_shapes.append(fog)

        self._build_m7_grid()

        for x, z, width, depth in arena["walls"]:
            shape = pyglet.shapes.Rectangle(
                -1000, -1000, 1, 1, color=arena["wall"],
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.m7_shapes.append(shape)
            self.m7_walls.append((float(x), float(z), float(width), float(depth), shape))

        for x, z, radius, kind in arena["hazards"]:
            shape = pyglet.shapes.Circle(
                -1000, -1000, 2, color=arena["hazard"],
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.m7_shapes.append(shape)
            self.m7_hazards.append((float(x), float(z), float(radius), str(kind), shape))

        for x, z, width, depth in arena["boosts"]:
            shape = pyglet.shapes.Rectangle(
                -1000, -1000, 2, 2, color=arena["boost"],
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.m7_shapes.append(shape)
            self.m7_boosts.append((float(x), float(z), float(width), float(depth), shape))

        for pair in arena["portals"]:
            ((ax, az), (bx, bz)) = pair
            sa = pyglet.shapes.Circle(
                -1000, -1000, 2, color=(109, 218, 234),
                batch=self.batch, group=self.scenery_group,
            )
            sb = pyglet.shapes.Circle(
                -1000, -1000, 2, color=(218, 113, 233),
                batch=self.batch, group=self.scenery_group,
            )
            sa.visible = False
            sb.visible = False
            self.m7_shapes.extend((sa, sb))
            self.m7_portals.append(((float(ax), float(az)), (float(bx), float(bz)), sa, sb))

        for cx, cz, length, speed, phase in arena["sweepers"]:
            line = pyglet.shapes.Line(
                -1000, -1000, -1000, -1000, thickness=7,
                color=arena["hazard"], batch=self.batch, group=self.scenery_group,
            )
            line.visible = False
            self.m7_shapes.append(line)
            self.m7_sweepers.append({
                "cx": float(cx), "cz": float(cz), "length": float(length),
                "speed": float(speed), "phase": float(phase), "shape": line,
            })

        for x, z in arena["items"]:
            shape = pyglet.shapes.Rectangle(
                -1000, -1000, 4, 4, color=(222, 98, 227),
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.m7_shapes.append(shape)
            self.m7_item_boxes.append({
                "x": float(x), "z": float(z), "cooldown": 0.0, "shape": shape,
            })

        for x, z in arena["coins"]:
            shape = pyglet.shapes.Circle(
                -1000, -1000, 2, color=(246, 207, 61),
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.m7_shapes.append(shape)
            self.m7_coins.append({
                "x": float(x), "z": float(z), "cooldown": 0.0, "shape": shape,
            })

    def _build_m7_player_kart(self):
        w = EngineGlobals.width
        self.m7_player_shadow = pyglet.shapes.Rectangle(
            w / 2 - 34, 48, 68, 13, color=(26, 25, 31),
            batch=self.batch, group=self.car_group,
        )
        self.m7_player_body = pyglet.shapes.Rectangle(
            w / 2 - 26, 61, 52, 28, color=(33, 36, 42),
            batch=self.batch, group=self.car_group,
        )
        self.m7_player_driver = pyglet.shapes.Circle(
            w / 2, 88, 10, color=self.m7_player["profile"]["color"],
            batch=self.batch, group=self.car_group,
        )
        self.m7_player_nose = pyglet.shapes.Triangle(
            w / 2, 109, w / 2 - 23, 80, w / 2 + 23, 80,
            color=(42, 45, 52), batch=self.batch, group=self.car_group,
        )
        self.m7_player_shield = pyglet.shapes.Circle(
            w / 2, 80, 42, color=(79, 184, 232),
            batch=self.batch, group=self.car_group,
        )
        self.m7_player_shield.opacity = 0
        self.m7_shapes.extend((
            self.m7_player_shadow, self.m7_player_body, self.m7_player_driver,
            self.m7_player_nose, self.m7_player_shield,
        ))

    def _build_m7_hud(self):
        w, h = EngineGlobals.width, EngineGlobals.height
        self.m7_title_label = pyglet.text.Label(
            "MODE 7 BATTLE", x=18, y=h - 24, font_size=13,
            weight=pyglet.text.Weight.BOLD, color=(255, 237, 157, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.m7_rule_label = pyglet.text.Label(
            "", x=18, y=h - 47, font_size=9, color=(210, 224, 241, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.m7_timer_label = pyglet.text.Label(
            "3:00", x=w // 2, y=h - 28, anchor_x="center", font_size=17,
            weight=pyglet.text.Weight.BOLD, color=(255, 245, 211, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.m7_status_label = pyglet.text.Label(
            "", x=18, y=48, font_size=10, weight=pyglet.text.Weight.BOLD,
            color=(255, 235, 164, 255), batch=self.batch, group=self.ui_group,
        )
        self.m7_item_label = pyglet.text.Label(
            "ITEM —", x=18, y=29, font_size=10,
            color=(234, 175, 242, 255), batch=self.batch, group=self.ui_group,
        )
        self.m7_event_label = pyglet.text.Label(
            "", x=w // 2, y=145, anchor_x="center", font_size=13,
            weight=pyglet.text.Weight.BOLD, color=(255, 223, 126, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.m7_speed_label = pyglet.text.Label(
            "", x=w - 18, y=30, anchor_x="right", font_size=9,
            color=(205, 220, 239, 255), batch=self.batch, group=self.ui_group,
        )
        self.m7_help_label = pyglet.text.Label(
            "↑ accelerate  ↓ brake  ← → steer  SPACE hop  D item  M music  ESC arena select",
            x=w // 2, y=10, anchor_x="center", font_size=7,
            color=(188, 202, 224, 255), batch=self.batch, group=self.ui_group,
        )
        self.m7_countdown_label = pyglet.text.Label(
            "3", x=w // 2, y=h // 2 + 54, anchor_x="center", anchor_y="center",
            font_size=64, weight=pyglet.text.Weight.BOLD,
            color=(255, 238, 147, 255), batch=self.batch, group=self.ui_group,
        )
        self.m7_labels.extend((
            self.m7_title_label, self.m7_rule_label, self.m7_timer_label,
            self.m7_status_label, self.m7_item_label, self.m7_event_label,
            self.m7_speed_label, self.m7_help_label, self.m7_countdown_label,
        ))

        self.m7_radar_bg = pyglet.shapes.Rectangle(
            w - 174, h - 158, 156, 106, color=(25, 29, 38),
            batch=self.batch, group=self.ui_group,
        )
        self.m7_radar_bg.opacity = 210
        self.m7_shapes.append(self.m7_radar_bg)
        for racer in self.m7_racers:
            dot = pyglet.shapes.Circle(
                -1000, -1000, 5 if racer["is_player"] else 3,
                color=(255, 226, 94) if racer["is_player"] else racer["profile"]["color"],
                batch=self.batch, group=self.ui_group,
            )
            self.m7_radar_dots.append(dot)

    def _start_mode7_battle(self):
        self._clear_battle()
        self._clear_race()
        self._clear_mode7_battle()
        self._clear_selection()
        self.keys.clear()

        self.m7_arena = MODE7_BATTLE_ARENAS[self.selected_m7_arena]
        self.state = self.STATE_M7_COUNTDOWN
        self.m7_countdown = 180.0
        self.m7_time_frames = MODE7_BATTLE_TIME_SECONDS * 60.0
        self.m7_event_timer = 0.0
        self.m7_world_clock = 0.0
        self.m7_camera_shake = 0.0
        self.m7_finish_place = None
        self.m7_results = []

        player_profile = base.CHARACTERS[self.selected_character]
        opponents = [c for c in base.CHARACTERS if c["name"] != player_profile["name"]]
        self.m7_rng.shuffle(opponents)
        profiles = [player_profile] + opponents[:7]
        spawns = self.m7_arena["spawns"]

        self.m7_racers = []
        for i, profile in enumerate(profiles):
            racer = self._make_m7_racer(profile, spawns[i % len(spawns)], is_player=(i == 0))
            self.m7_racers.append(racer)
        self.m7_player = self.m7_racers[0]

        self._build_m7_world_shapes()
        self._build_m7_player_kart()
        self._build_m7_hud()
        self._play_music_file(self.m7_arena["music"])
        self._update_m7_hud()
        self._update_m7_projection()

    # ---------- projection ----------

    def _m7_project(self, wx, wz):
        player = self.m7_player
        if player is None:
            return None
        angle = player["angle"]
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        cam_x = player["x"] - sin_a * 72.0
        cam_z = player["z"] - cos_a * 72.0
        dx = float(wx) - cam_x
        dz = float(wz) - cam_z
        forward = dx * sin_a + dz * cos_a
        if forward < self.NEAR_CLIP or forward > self.VIEW_DISTANCE:
            return None
        lateral = dx * cos_a - dz * sin_a
        horizon = EngineGlobals.height * 0.49
        sx = EngineGlobals.width * 0.5 + lateral * (self.FOCAL / forward) + self.m7_shake_x
        sy = horizon - self.CAMERA_HEIGHT * (self.FOCAL / forward) + self.m7_shake_y
        scale = max(0.10, min(1.8, 250.0 / (forward + 55.0)))
        return sx, sy, scale, forward

    def _m7_project_segment(self, x1, z1, x2, z2):
        p1 = self._m7_project(x1, z1)
        p2 = self._m7_project(x2, z2)
        if p1 is None or p2 is None:
            return None
        return p1, p2

    def _update_m7_grid(self):
        for line, segment in zip(self.m7_grid_lines, self.m7_grid_segments):
            projected = self._m7_project_segment(*segment)
            if projected is None:
                line.visible = False
                continue
            p1, p2 = projected
            line.visible = True
            line.x, line.y = p1[0], p1[1]
            line.x2, line.y2 = p2[0], p2[1]

    def _project_rect_marker(self, shape, x, z, width, depth, height=22.0):
        projected = self._m7_project(x + width / 2.0, z + depth / 2.0)
        if projected is None:
            shape.visible = False
            return
        sx, sy, scale, _ = projected
        shape.visible = True
        shape.width = max(3.0, min(240.0, max(width, depth) * scale * 0.62))
        shape.height = max(3.0, height * scale)
        shape.x = sx - shape.width / 2.0
        shape.y = sy

    def _project_circle_marker(self, shape, x, z, radius):
        projected = self._m7_project(x, z)
        if projected is None:
            shape.visible = False
            return
        sx, sy, scale, _ = projected
        shape.visible = True
        shape.radius = max(2.0, min(70.0, radius * scale))
        shape.position = (sx, sy + shape.radius * 0.15)

    def _update_m7_projection(self):
        if self.m7_player is None:
            return
        if self.m7_camera_shake > 0:
            self.m7_shake_x = self.m7_rng.uniform(-self.m7_camera_shake, self.m7_camera_shake)
            self.m7_shake_y = self.m7_rng.uniform(-self.m7_camera_shake * 0.35, self.m7_camera_shake * 0.35)
        else:
            self.m7_shake_x = 0.0
            self.m7_shake_y = 0.0
        self._update_m7_grid()

        for x, z, width, depth, shape in self.m7_walls:
            self._project_rect_marker(shape, x, z, width, depth, height=58.0)

        for x, z, radius, _kind, shape in self.m7_hazards:
            self._project_circle_marker(shape, x, z, radius)

        for x, z, width, depth, shape in self.m7_boosts:
            self._project_rect_marker(shape, x, z, width, depth, height=8.0)

        for a, b, sa, sb in self.m7_portals:
            self._project_circle_marker(sa, a[0], a[1], 38.0)
            self._project_circle_marker(sb, b[0], b[1], 38.0)

        for sweeper in self.m7_sweepers:
            angle = self.m7_world_clock * sweeper["speed"] + sweeper["phase"]
            half = sweeper["length"] / 2.0
            dx = math.cos(angle) * half
            dz = math.sin(angle) * half
            projected = self._m7_project_segment(
                sweeper["cx"] - dx, sweeper["cz"] - dz,
                sweeper["cx"] + dx, sweeper["cz"] + dz,
            )
            line = sweeper["shape"]
            if projected is None:
                line.visible = False
            else:
                p1, p2 = projected
                line.visible = True
                line.x, line.y = p1[0], p1[1]
                line.x2, line.y2 = p2[0], p2[1]

        for box in self.m7_item_boxes:
            shape = box["shape"]
            if box["cooldown"] > 0:
                shape.visible = False
                continue
            projected = self._m7_project(box["x"], box["z"])
            if projected is None:
                shape.visible = False
                continue
            sx, sy, scale, _ = projected
            size = max(4.0, min(34.0, 28.0 * scale))
            shape.visible = True
            shape.width = size
            shape.height = size
            shape.position = (sx - size / 2, sy)

        coin_clash = MODE7_BATTLE_RULES[self.selected_m7_rule][0] == "COIN CLASH"
        for coin in self.m7_coins:
            shape = coin["shape"]
            if not coin_clash or coin["cooldown"] > 0:
                shape.visible = False
                continue
            projected = self._m7_project(coin["x"], coin["z"])
            if projected is None:
                shape.visible = False
                continue
            sx, sy, scale, _ = projected
            shape.visible = True
            shape.radius = max(2.0, min(15.0, 10.0 * scale))
            shape.position = (sx, sy + shape.radius)

        for racer in self.m7_racers[1:]:
            body = racer["body"]
            driver = racer["driver"]
            if racer["eliminated"] or racer["respawn_timer"] > 0:
                body.visible = False
                driver.visible = False
                continue
            projected = self._m7_project(racer["x"], racer["z"])
            if projected is None:
                body.visible = False
                driver.visible = False
                continue
            sx, sy, scale, _ = projected
            body.visible = True
            driver.visible = True
            body.width = max(5.0, min(68.0, 44.0 * scale))
            body.height = max(3.0, min(38.0, 23.0 * scale))
            body.position = (sx - body.width / 2.0, sy)
            driver.radius = max(2.0, min(13.0, 8.0 * scale))
            driver.position = (sx, sy + body.height * 0.78)

        for projectile in self.m7_projectiles:
            self._project_circle_marker(projectile["shape"], projectile["x"], projectile["z"], 14.0)
        for mine in self.m7_mines:
            self._project_circle_marker(mine["shape"], mine["x"], mine["z"], 18.0)

        hop = self.m7_player["hop"] if self.m7_player else 0.0
        hop_y = math.sin(min(1.0, hop / 45.0) * math.pi) * 16.0 if hop > 0 else 0.0
        base_y = 61 + hop_y
        w = EngineGlobals.width
        self.m7_player_shadow.position = (w / 2 - 34, 48)
        self.m7_player_body.position = (w / 2 - 26, base_y)
        self.m7_player_driver.position = (w / 2, base_y + 27)
        self.m7_player_nose.x, self.m7_player_nose.y = w / 2, base_y + 48
        self.m7_player_nose.x2, self.m7_player_nose.y2 = w / 2 - 23, base_y + 19
        self.m7_player_nose.x3, self.m7_player_nose.y3 = w / 2 + 23, base_y + 19
        self.m7_player_shield.position = (w / 2, base_y + 19)
        self.m7_player_shield.opacity = (
            70 if self.m7_player["shield"] > 0 else
            105 if self.m7_player["star"] > 0 else 0
        )
        self._update_m7_radar()

    def _update_m7_radar(self):
        if not self.m7_radar_dots:
            return
        w, h = EngineGlobals.width, EngineGlobals.height
        left = w - 164
        bottom = h - 149
        for dot, racer in zip(self.m7_radar_dots, self.m7_racers):
            if racer["eliminated"]:
                dot.visible = False
                continue
            dot.visible = True
            dot.x = left + (racer["x"] / WORLD_W) * 136
            dot.y = bottom + (racer["z"] / WORLD_H) * 88

    # ---------- physics ----------

    def _m7_physics(self, racer):
        profile = racer["profile"]
        engine = self._class_def()
        if racer["is_player"]:
            speed_scale = engine["speed"]
            accel_scale = engine["accel"]
        else:
            speed_scale = engine["ai"]
            accel_scale = 0.94 + self._difficulty_def()["ai"] * 0.06
        max_speed = (4.2 + profile["speed"] * 0.27) * speed_scale
        return {
            "max_speed": max_speed,
            "boost_speed": max_speed + 1.45 + profile["boost"] * 0.10,
            "accel": (0.080 + profile["accel"] * 0.0105) * accel_scale,
            "reverse": 2.15 + profile["accel"] * 0.05,
            "turn": 0.026 + profile["turn"] * 0.0027,
            "weight": float(profile["weight"]),
            "grip": float(profile["grip"]),
            "boost": float(profile["boost"]),
        }

    @staticmethod
    def _angle_delta(target, current):
        return (target - current + math.pi) % (math.tau) - math.pi

    @staticmethod
    def _point_in_rect(px, pz, rect):
        x, z, width, depth = rect[:4]
        return x <= px <= x + width and z <= pz <= z + depth

    @staticmethod
    def _distance(a, b):
        return math.hypot(a["x"] - b["x"], a["z"] - b["z"])

    def _move_m7_racer(self, racer, throttle, steer, dt):
        if racer["eliminated"]:
            return
        if racer["respawn_timer"] > 0:
            racer["respawn_timer"] = max(0.0, racer["respawn_timer"] - dt)
            if racer["respawn_timer"] <= 0:
                self._respawn_m7_racer(racer)
            return

        physics = self._m7_physics(racer)
        if throttle > 0:
            racer["speed"] += physics["accel"] * dt
        elif throttle < 0:
            racer["speed"] -= physics["accel"] * 0.78 * dt
        else:
            racer["speed"] *= self.m7_arena["friction"] ** dt

        for timer in (
            "turbo", "shield", "star", "hop", "invuln", "hit_cooldown",
            "hazard_cooldown", "portal_cooldown", "item_use_cooldown",
        ):
            racer[timer] = max(0.0, racer[timer] - dt)

        top = physics["boost_speed"] if racer["turbo"] > 0 or racer["star"] > 0 else physics["max_speed"]
        racer["speed"] = max(-physics["reverse"], min(top, racer["speed"]))
        if abs(racer["speed"]) > 0.1:
            hop_turn = 1.22 if racer["hop"] > 0 else 1.0
            direction = 1.0 if racer["speed"] >= 0 else -0.67
            racer["angle"] += steer * physics["turn"] * hop_turn * direction * dt

        racer["x"] += math.sin(racer["angle"]) * racer["speed"] * dt
        racer["z"] += math.cos(racer["angle"]) * racer["speed"] * dt

        wind_x, wind_z = self.m7_arena["wind"]
        if racer["star"] <= 0:
            racer["x"] += wind_x * max(2.0, abs(racer["speed"])) * dt * 9.0
            racer["z"] += wind_z * max(2.0, abs(racer["speed"])) * dt * 9.0

        self._m7_boundaries(racer)
        self._m7_wall_collisions(racer)
        self._m7_arena_features(racer)

    def _m7_boundaries(self, racer):
        r = self.RACER_RADIUS
        bounced = False
        if racer["x"] < r:
            racer["x"] = r
            racer["angle"] = -racer["angle"]
            bounced = True
        elif racer["x"] > WORLD_W - r:
            racer["x"] = WORLD_W - r
            racer["angle"] = -racer["angle"]
            bounced = True
        if racer["z"] < r:
            racer["z"] = r
            racer["angle"] = math.pi - racer["angle"]
            bounced = True
        elif racer["z"] > WORLD_H - r:
            racer["z"] = WORLD_H - r
            racer["angle"] = math.pi - racer["angle"]
            bounced = True
        if bounced:
            racer["speed"] *= 0.55

    def _m7_wall_collisions(self, racer):
        r = self.RACER_RADIUS
        for x, z, width, depth, _shape in self.m7_walls:
            if not (x - r < racer["x"] < x + width + r and z - r < racer["z"] < z + depth + r):
                continue
            distances = (
                (abs(racer["x"] - (x - r)), "left"),
                (abs(racer["x"] - (x + width + r)), "right"),
                (abs(racer["z"] - (z - r)), "near"),
                (abs(racer["z"] - (z + depth + r)), "far"),
            )
            side = min(distances, key=lambda pair: pair[0])[1]
            if side == "left":
                racer["x"] = x - r
                racer["angle"] = -racer["angle"]
            elif side == "right":
                racer["x"] = x + width + r
                racer["angle"] = -racer["angle"]
            elif side == "near":
                racer["z"] = z - r
                racer["angle"] = math.pi - racer["angle"]
            else:
                racer["z"] = z + depth + r
                racer["angle"] = math.pi - racer["angle"]
            racer["speed"] *= 0.54

    def _m7_arena_features(self, racer):
        if racer["eliminated"] or racer["respawn_timer"] > 0:
            return
        for x, z, radius, kind, _shape in self.m7_hazards:
            if math.hypot(racer["x"] - x, racer["z"] - z) > radius + 14:
                continue
            if racer["hazard_cooldown"] > 0 or racer["hop"] > 0 or racer["star"] > 0:
                break
            racer["hazard_cooldown"] = 90.0
            if kind == "slow":
                racer["speed"] *= 0.35
                if racer["is_player"]:
                    self._m7_event("{} — SLOWED!".format(self.m7_arena["hazard_name"]), 45)
            elif kind == "spin":
                racer["speed"] *= 0.42
                racer["angle"] += math.pi * 0.78
                if racer["is_player"]:
                    self._m7_event("{} — SPIN!".format(self.m7_arena["hazard_name"]), 55)
            else:
                self._m7_hit(racer, None, self.m7_arena["hazard_name"])
            break

        for boost in self.m7_boosts:
            if self._point_in_rect(racer["x"], racer["z"], boost):
                physics = self._m7_physics(racer)
                racer["turbo"] = max(racer["turbo"], 50.0 + physics["boost"] * 2.0)
                racer["speed"] = max(racer["speed"], physics["max_speed"] + 0.75)
                break

        if racer["portal_cooldown"] <= 0:
            for a, b, _sa, _sb in self.m7_portals:
                if math.hypot(racer["x"] - a[0], racer["z"] - a[1]) < 50:
                    racer["x"], racer["z"] = b
                    racer["portal_cooldown"] = 70.0
                    if racer["is_player"]:
                        self._m7_event("WARP!", 28)
                    break
                if math.hypot(racer["x"] - b[0], racer["z"] - b[1]) < 50:
                    racer["x"], racer["z"] = a
                    racer["portal_cooldown"] = 70.0
                    if racer["is_player"]:
                        self._m7_event("WARP!", 28)
                    break

        for box in self.m7_item_boxes:
            if box["cooldown"] <= 0 and racer["held_item"] is None:
                if math.hypot(racer["x"] - box["x"], racer["z"] - box["z"]) < 48:
                    racer["held_item"] = self._m7_random_item(racer)
                    box["cooldown"] = 220.0
                    if racer["is_player"]:
                        self._m7_event("ITEM: {}".format(racer["held_item"]), 50)
                    break

        if MODE7_BATTLE_RULES[self.selected_m7_rule][0] == "COIN CLASH":
            for coin in self.m7_coins:
                if coin["cooldown"] <= 0 and math.hypot(
                    racer["x"] - coin["x"], racer["z"] - coin["z"]
                ) < 40:
                    racer["coins"] += 1
                    coin["cooldown"] = 165.0
                    if racer["is_player"]:
                        self._m7_event("OINK! +1 COIN", 25)
                    break

    def _m7_sweeper_collisions(self):
        for sweeper in self.m7_sweepers:
            angle = self.m7_world_clock * sweeper["speed"] + sweeper["phase"]
            half = sweeper["length"] / 2.0
            x1 = sweeper["cx"] - math.cos(angle) * half
            z1 = sweeper["cz"] - math.sin(angle) * half
            x2 = sweeper["cx"] + math.cos(angle) * half
            z2 = sweeper["cz"] + math.sin(angle) * half
            for racer in self.m7_racers:
                if racer["eliminated"] or racer["respawn_timer"] > 0:
                    continue
                if racer["hazard_cooldown"] > 0 or racer["hop"] > 0:
                    continue
                if self._point_segment_distance(racer["x"], racer["z"], x1, z1, x2, z2) < 34:
                    racer["hazard_cooldown"] = 80.0
                    self._m7_hit(racer, None, "SWEEPER SMACK!")

    @staticmethod
    def _point_segment_distance(px, pz, x1, z1, x2, z2):
        vx, vz = x2 - x1, z2 - z1
        wx, wz = px - x1, pz - z1
        denom = vx * vx + vz * vz
        if denom <= 1e-9:
            return math.hypot(px - x1, pz - z1)
        t = max(0.0, min(1.0, (wx * vx + wz * vz) / denom))
        cx, cz = x1 + t * vx, z1 + t * vz
        return math.hypot(px - cx, pz - cz)

    # ---------- combat / items ----------

    def _m7_random_item(self, racer):
        bag = list(MODE7_BATTLE_ITEMS)
        if racer["balloons"] <= 1:
            bag += ["BAT SHIELD", "STAR", "PIG BOMB", "HOG ROCKET"] * 2
        if MODE7_BATTLE_RULES[self.selected_m7_rule][0] == "COIN CLASH":
            bag += ["HOG ROCKET", "TURBO", "LIGHTNING"]
        return self.m7_rng.choice(bag)

    def _m7_nearest_target(self, racer):
        candidates = [
            other for other in self.m7_racers
            if other is not racer and not other["eliminated"] and other["respawn_timer"] <= 0
        ]
        return min(candidates, key=lambda other: self._distance(racer, other)) if candidates else None

    def _m7_event(self, text, frames=60.0):
        if hasattr(self, "m7_event_label"):
            self.m7_event_label.text = text
        self.m7_event_timer = max(self.m7_event_timer, float(frames))

    def _m7_hit(self, target, attacker, message="HIT!"):
        if target["eliminated"] or target["respawn_timer"] > 0:
            return False
        if target["invuln"] > 0 or target["hop"] > 0 or target["star"] > 0:
            return False
        if target["shield"] > 0:
            target["shield"] = 0.0
            target["invuln"] = 26.0
            if target["is_player"]:
                self._m7_event("BAT SHIELD BLOCK!", 45)
            return False

        target["balloons"] -= 1
        target["invuln"] = 78.0
        target["hit_cooldown"] = 38.0
        target["speed"] *= 0.28
        if target["is_player"]:
            self.m7_camera_shake = max(self.m7_camera_shake, 12.0)
            self._m7_event("{} — BALLOON LOST!".format(message), 70)

        if attacker is not None and attacker is not target:
            attacker["score"] += 1

        if MODE7_BATTLE_RULES[self.selected_m7_rule][0] == "COIN CLASH" and target["coins"] > 0:
            stolen = min(2, target["coins"])
            target["coins"] -= stolen
            if attacker is not None and attacker is not target:
                attacker["coins"] += stolen

        if target["balloons"] <= 0:
            self._m7_knockout(target, attacker)
        return True

    def _m7_knockout(self, target, attacker):
        rule = MODE7_BATTLE_RULES[self.selected_m7_rule][0]
        if attacker is not None and attacker is not target:
            attacker["score"] += 2

        if rule == "BALLOON BATTLE":
            active_after = sum(
                1 for racer in self.m7_racers
                if racer is not target and not racer["eliminated"]
            )
            target["placement"] = active_after + 1
            target["eliminated"] = True
            if target["body"] is not None:
                target["body"].visible = False
                target["driver"].visible = False
            if target["is_player"]:
                self._m7_event("HOGGED OUT!", 90)
        else:
            target["respawn_timer"] = 105.0
            target["balloons"] = MODE7_BATTLE_BALLOONS
            target["held_item"] = None
            if target["is_player"]:
                self._m7_event("KNOCKOUT — RESPAWNING!", 80)

    def _respawn_m7_racer(self, racer):
        index = self.m7_racers.index(racer) % len(self.m7_arena["spawns"])
        x, z, angle = self.m7_arena["spawns"][index]
        racer["x"], racer["z"], racer["angle"] = float(x), float(z), float(angle)
        racer["speed"] = 0.0
        racer["respawn_timer"] = 0.0
        racer["invuln"] = 120.0
        racer["shield"] = 0.0
        racer["star"] = 0.0
        racer["hop"] = 0.0

    def _fire_m7_rocket(self, racer):
        target = self._m7_nearest_target(racer)
        shape = pyglet.shapes.Circle(
            -1000, -1000, 3, color=(239, 101, 70),
            batch=self.batch, group=self.car_group,
        )
        self.m7_projectiles.append({
            "x": racer["x"] + math.sin(racer["angle"]) * 38.0,
            "z": racer["z"] + math.cos(racer["angle"]) * 38.0,
            "angle": racer["angle"],
            "speed": 11.0,
            "owner": racer,
            "target": target,
            "life": 220.0,
            "shape": shape,
        })

    def _drop_m7_mine(self, racer):
        x = racer["x"] - math.sin(racer["angle"]) * 45.0
        z = racer["z"] - math.cos(racer["angle"]) * 45.0
        shape = pyglet.shapes.Circle(
            -1000, -1000, 3, color=(185, 34, 40),
            batch=self.batch, group=self.scenery_group,
        )
        self.m7_mines.append({
            "x": x, "z": z, "owner": racer,
            "arm": 28.0, "life": 900.0, "shape": shape,
        })

    def _use_m7_item(self, racer):
        item = racer["held_item"]
        if not item or racer["eliminated"] or racer["respawn_timer"] > 0:
            return
        racer["held_item"] = None
        racer["item_use_cooldown"] = 80.0
        physics = self._m7_physics(racer)

        if item == "HOG ROCKET":
            self._fire_m7_rocket(racer)
        elif item == "KETCHUP MINE":
            self._drop_m7_mine(racer)
        elif item == "TURBO":
            racer["turbo"] = 120.0
            racer["speed"] = max(racer["speed"], physics["max_speed"] + 1.5)
        elif item == "BAT SHIELD":
            racer["shield"] = 380.0
        elif item == "PIG BOMB":
            hits = 0
            for target in self.m7_racers:
                if target is racer or target["eliminated"] or target["respawn_timer"] > 0:
                    continue
                if self._distance(racer, target) < 330.0:
                    hits += int(self._m7_hit(target, racer, "PIG BOMB!"))
            if racer["is_player"]:
                self._m7_event("PIG BOMB — {} HIT!".format(hits), 58)
        elif item == "LIGHTNING":
            hits = 0
            for target in self.m7_racers:
                if target is racer or target["eliminated"] or target["respawn_timer"] > 0:
                    continue
                hits += int(self._m7_hit(target, racer, "LIGHTNING!"))
            if racer["is_player"]:
                self._m7_event("LIGHTNING — {} HIT!".format(hits), 62)
        elif item == "STAR":
            racer["star"] = 260.0
            racer["turbo"] = 230.0
            racer["speed"] = max(racer["speed"], physics["max_speed"] + 1.6)
        elif item == "FEATHER":
            racer["hop"] = 92.0 * self.m7_arena["hop_scale"]
            racer["invuln"] = max(racer["invuln"], racer["hop"])

        if racer["is_player"] and item not in ("PIG BOMB", "LIGHTNING"):
            self._m7_event("{}!".format(item), 45)

    def _update_m7_projectiles(self, dt):
        kept = []
        for projectile in self.m7_projectiles:
            projectile["life"] -= dt
            if projectile["life"] <= 0:
                self._delete_shape(projectile["shape"])
                continue

            target = projectile.get("target")
            if target is None or target["eliminated"] or target["respawn_timer"] > 0:
                target = self._m7_nearest_target(projectile["owner"])
                projectile["target"] = target
            if target is not None:
                desired = math.atan2(target["x"] - projectile["x"], target["z"] - projectile["z"])
                delta = self._angle_delta(desired, projectile["angle"])
                projectile["angle"] += max(-0.045 * dt, min(0.045 * dt, delta))

            projectile["x"] += math.sin(projectile["angle"]) * projectile["speed"] * dt
            projectile["z"] += math.cos(projectile["angle"]) * projectile["speed"] * dt

            if not (0 <= projectile["x"] <= WORLD_W and 0 <= projectile["z"] <= WORLD_H):
                self._delete_shape(projectile["shape"])
                continue
            if any(self._point_in_rect(projectile["x"], projectile["z"], wall) for wall in self.m7_walls):
                self._delete_shape(projectile["shape"])
                continue

            hit = False
            for racer in self.m7_racers:
                if racer is projectile["owner"] or racer["eliminated"] or racer["respawn_timer"] > 0:
                    continue
                if math.hypot(racer["x"] - projectile["x"], racer["z"] - projectile["z"]) < 42:
                    self._m7_hit(racer, projectile["owner"], "HOG ROCKET!")
                    hit = True
                    break
            if hit:
                self._delete_shape(projectile["shape"])
            else:
                kept.append(projectile)
        self.m7_projectiles = kept

    def _update_m7_mines(self, dt):
        kept = []
        for mine in self.m7_mines:
            mine["arm"] = max(0.0, mine["arm"] - dt)
            mine["life"] -= dt
            if mine["life"] <= 0:
                self._delete_shape(mine["shape"])
                continue
            exploded = False
            if mine["arm"] <= 0:
                for racer in self.m7_racers:
                    if racer is mine["owner"] or racer["eliminated"] or racer["respawn_timer"] > 0:
                        continue
                    if math.hypot(racer["x"] - mine["x"], racer["z"] - mine["z"]) < 48:
                        self._m7_hit(racer, mine["owner"], "KETCHUP MINE!")
                        exploded = True
                        break
            if exploded:
                self._delete_shape(mine["shape"])
            else:
                kept.append(mine)
        self.m7_mines = kept

    def _m7_racer_collisions(self):
        racers = [
            r for r in self.m7_racers if not r["eliminated"] and r["respawn_timer"] <= 0
        ]
        for i, a in enumerate(racers):
            for b in racers[i + 1:]:
                dx, dz = b["x"] - a["x"], b["z"] - a["z"]
                dist = math.hypot(dx, dz)
                if dist <= 0.001 or dist >= self.RACER_RADIUS * 2:
                    continue
                nx, nz = dx / dist, dz / dist
                overlap = self.RACER_RADIUS * 2 - dist
                a["x"] -= nx * overlap * 0.5
                a["z"] -= nz * overlap * 0.5
                b["x"] += nx * overlap * 0.5
                b["z"] += nz * overlap * 0.5

                if a["star"] > 0 and b["star"] <= 0:
                    self._m7_hit(b, a, "STAR RAM!")
                elif b["star"] > 0 and a["star"] <= 0:
                    self._m7_hit(a, b, "STAR RAM!")
                else:
                    wa = self._m7_physics(a)["weight"]
                    wb = self._m7_physics(b)["weight"]
                    a["speed"] *= max(0.60, min(0.94, wb / max(1.0, wa + wb) + 0.45))
                    b["speed"] *= max(0.60, min(0.94, wa / max(1.0, wa + wb) + 0.45))

    # ---------- AI ----------

    def _m7_ai_target_point(self, racer):
        if racer["held_item"] is None:
            available = [box for box in self.m7_item_boxes if box["cooldown"] <= 0]
            if available:
                nearest_box = min(
                    available,
                    key=lambda box: math.hypot(racer["x"] - box["x"], racer["z"] - box["z"]),
                )
                if math.hypot(racer["x"] - nearest_box["x"], racer["z"] - nearest_box["z"]) < 500:
                    return nearest_box["x"], nearest_box["z"]
        target = self._m7_nearest_target(racer)
        if target is not None:
            return target["x"], target["z"]
        return WORLD_W / 2, WORLD_H / 2

    def _update_m7_ai(self, dt):
        aggression = self._difficulty_def()["item_aggression"]
        for racer in self.m7_racers[1:]:
            if racer["eliminated"]:
                continue
            if racer["respawn_timer"] > 0:
                self._move_m7_racer(racer, 0.0, 0.0, dt)
                continue

            tx, tz = self._m7_ai_target_point(racer)
            desired = math.atan2(tx - racer["x"], tz - racer["z"])
            delta = self._angle_delta(desired, racer["angle"])
            steer = max(-1.0, min(1.0, delta * 1.85))

            look = 95.0
            fx = racer["x"] + math.sin(racer["angle"]) * look
            fz = racer["z"] + math.cos(racer["angle"]) * look
            if any(self._point_in_rect(fx, fz, wall) for wall in self.m7_walls):
                steer = 1.0 if racer["ai_wander"] >= 0 else -1.0
                racer["ai_wander"] *= -1.0

            self._move_m7_racer(racer, 1.0, steer, dt)

            if racer["held_item"] and racer["item_use_cooldown"] <= 0:
                target = self._m7_nearest_target(racer)
                distance = self._distance(racer, target) if target is not None else 9999
                use_chance = (0.0025 + aggression * 0.0018) * dt
                if distance < 480 or racer["held_item"] in ("BAT SHIELD", "TURBO", "STAR", "FEATHER"):
                    if self.m7_rng.random() < use_chance:
                        self._use_m7_item(racer)

    # ---------- player / pickups / match flow ----------

    def _update_m7_player(self, dt):
        player = self.m7_player
        if player is None or player["eliminated"]:
            return
        up = pyglet.window.key.UP in self.keys
        down = pyglet.window.key.DOWN in self.keys
        left = pyglet.window.key.LEFT in self.keys
        right = pyglet.window.key.RIGHT in self.keys
        throttle = 1.0 if up else (-1.0 if down else 0.0)
        steer = (-1.0 if left else 0.0) + (1.0 if right else 0.0)
        self._move_m7_racer(player, throttle, steer, dt)

    def _tick_m7_pickups(self, dt):
        for box in self.m7_item_boxes:
            box["cooldown"] = max(0.0, box["cooldown"] - dt)
        for coin in self.m7_coins:
            coin["cooldown"] = max(0.0, coin["cooldown"] - dt)

    def _m7_end_check(self):
        rule = MODE7_BATTLE_RULES[self.selected_m7_rule][0]
        if rule == "BALLOON BATTLE":
            active = [r for r in self.m7_racers if not r["eliminated"]]
            if len(active) <= 1 or self.m7_player["eliminated"]:
                if active and active[0]["placement"] is None:
                    active[0]["placement"] = 1
                self._finish_mode7_battle()
                return True
        elif self.m7_time_frames <= 0:
            self._finish_mode7_battle()
            return True
        return False

    def _sort_m7_results(self):
        rule = MODE7_BATTLE_RULES[self.selected_m7_rule][0]
        if rule == "COIN CLASH":
            return sorted(self.m7_racers, key=lambda r: (-r["coins"], -r["score"], r["name"]))
        if rule == "HOG SCORE":
            return sorted(self.m7_racers, key=lambda r: (-r["score"], -r["balloons"], r["name"]))
        return sorted(
            self.m7_racers,
            key=lambda r: (
                r["eliminated"],
                r["placement"] if r["placement"] is not None else 1,
                -r["balloons"],
                -r["score"],
            ),
        )

    def _finish_mode7_battle(self):
        results = self._sort_m7_results()
        player_name = self.m7_player["name"]
        self.m7_finish_place = next(
            (i + 1 for i, racer in enumerate(results) if racer["name"] == player_name), 8
        )
        snapshot = [
            {
                "name": racer["name"], "is_player": racer["is_player"],
                "balloons": racer["balloons"], "score": racer["score"],
                "coins": racer["coins"],
            }
            for racer in results
        ]
        self.m7_results = snapshot

        self._clear_mode7_battle()
        self._clear_selection()
        self.state = self.STATE_M7_FINISH
        rule = MODE7_BATTLE_RULES[self.selected_m7_rule][0]
        arena = MODE7_BATTLE_ARENAS[self.selected_m7_arena]["name"]
        self._selection_header(
            "MODE 7 BATTLE RESULTS",
            "{} • {} • {} PLACE".format(rule, arena.upper(), self.m7_finish_place),
        )
        for i, result in enumerate(snapshot):
            y = 456 - i * 43
            panel = pyglet.shapes.Rectangle(
                175, y - 15, 450, 32,
                color=(111, 122, 154) if result["is_player"] else (44, 50, 63),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                "{}. {}".format(i + 1, result["name"].upper()),
                x=195, y=y, anchor_y="center", font_size=10,
                weight=pyglet.text.Weight.BOLD, color=(255, 247, 211, 255),
                batch=self.batch, group=self.ui_group,
            ))
            if rule == "COIN CLASH":
                metric = "{} COINS • {} HITS".format(result["coins"], result["score"])
            elif rule == "HOG SCORE":
                metric = "{} PTS".format(result["score"])
            else:
                metric = "{} BALLOONS • {} HITS".format(result["balloons"], result["score"])
            self.selection_labels.append(pyglet.text.Label(
                metric, x=605, y=y, anchor_x="right", anchor_y="center",
                font_size=9, color=(235, 216, 132, 255),
                batch=self.batch, group=self.ui_group,
            ))
        self.selection_labels.append(pyglet.text.Label(
            "ENTER rematch • ESC arena select",
            x=400, y=70, anchor_x="center", font_size=10,
            weight=pyglet.text.Weight.BOLD, color=(255, 223, 133, 255),
            batch=self.batch, group=self.ui_group,
        ))

    def _update_m7_hud(self):
        if self.m7_player is None:
            return
        rule = MODE7_BATTLE_RULES[self.selected_m7_rule][0]
        seconds = max(0, int(math.ceil(self.m7_time_frames / 60.0)))
        minutes, secs = divmod(seconds, 60)
        self.m7_timer_label.text = "{:d}:{:02d}".format(minutes, secs)
        self.m7_rule_label.text = "{} • {} • {} • {}".format(
            rule,
            self.m7_arena["name"].upper(),
            self._class_def()["name"],
            self._difficulty_def()["name"],
        )
        if rule == "COIN CLASH":
            self.m7_status_label.text = "COINS {} • HITS {} • BALLOONS {}".format(
                self.m7_player["coins"], self.m7_player["score"], self.m7_player["balloons"]
            )
        elif rule == "HOG SCORE":
            self.m7_status_label.text = "SCORE {} • BALLOONS {}".format(
                self.m7_player["score"], self.m7_player["balloons"]
            )
        else:
            active = sum(1 for r in self.m7_racers if not r["eliminated"])
            self.m7_status_label.text = "BALLOONS {} • {} RACERS LEFT".format(
                self.m7_player["balloons"], active
            )
        self.m7_item_label.text = "ITEM {}".format(self.m7_player["held_item"] or "—")
        self.m7_speed_label.text = "{} {:.1f} • MUSIC {}".format(
            self.m7_player["name"].upper(), abs(self.m7_player["speed"]),
            self._music_display(self.music_name),
        )
        if self.m7_event_timer > 0:
            self.m7_event_timer = max(0.0, self.m7_event_timer - 1.0)
            if self.m7_event_timer <= 0:
                self.m7_event_label.text = ""

    # ---------- input / update ----------

    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        enter = symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN)

        if self.state == self.STATE_CHARACTER and self.play_mode == MODE7_BATTLE_ENTRY[0] and enter:
            self._build_mode7_rules()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_M7_RULES:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_character_select()
            elif symbol in (pyglet.window.key.UP, pyglet.window.key.LEFT):
                self.selected_m7_rule = (self.selected_m7_rule - 1) % len(MODE7_BATTLE_RULES)
                self._refresh_mode7_rules()
            elif symbol in (pyglet.window.key.DOWN, pyglet.window.key.RIGHT):
                self.selected_m7_rule = (self.selected_m7_rule + 1) % len(MODE7_BATTLE_RULES)
                self._refresh_mode7_rules()
            elif enter:
                self._build_mode7_arena_select()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_M7_ARENA:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_mode7_rules()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_m7_arena = (self.selected_m7_arena - 1) % len(MODE7_BATTLE_ARENAS)
                self._refresh_mode7_arena_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_m7_arena = (self.selected_m7_arena + 1) % len(MODE7_BATTLE_ARENAS)
                self._refresh_mode7_arena_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_m7_arena = (self.selected_m7_arena - 4) % len(MODE7_BATTLE_ARENAS)
                self._refresh_mode7_arena_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_m7_arena = (self.selected_m7_arena + 4) % len(MODE7_BATTLE_ARENAS)
                self._refresh_mode7_arena_select()
            elif enter:
                self._start_mode7_battle()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_M7_FINISH:
            if enter:
                self._start_mode7_battle()
            elif symbol == pyglet.window.key.ESCAPE:
                self._build_mode7_arena_select()
            return pyglet.event.EVENT_HANDLED

        if self.state in (self.STATE_M7_COUNTDOWN, self.STATE_M7_BATTLE):
            if symbol == pyglet.window.key.ESCAPE:
                self.keys.clear()
                self._build_mode7_arena_select()
                return pyglet.event.EVENT_HANDLED
            if symbol == pyglet.window.key.M:
                current = self.music_name if self.music_name in MUSIC_LIBRARY else self.m7_arena["music"]
                index = MUSIC_LIBRARY.index(current) if current in MUSIC_LIBRARY else 0
                filename = MUSIC_LIBRARY[(index + 1) % len(MUSIC_LIBRARY)]
                self._play_music_file(filename)
                self._m7_event("NOW PLAYING {}".format(self._music_display(filename)), 48)
                return pyglet.event.EVENT_HANDLED
            if self.state == self.STATE_M7_BATTLE:
                if symbol == pyglet.window.key.D:
                    self._use_m7_item(self.m7_player)
                    return pyglet.event.EVENT_HANDLED
                if symbol == pyglet.window.key.SPACE:
                    if (
                        self.m7_player is not None and
                        self.m7_player["hop"] <= 0 and
                        not self.m7_player["eliminated"]
                    ):
                        self.m7_player["hop"] = 46.0 * self.m7_arena["hop_scale"]
                        self.m7_player["invuln"] = max(
                            self.m7_player["invuln"], self.m7_player["hop"]
                        )
                        self.m7_player["speed"] *= 1.04
                        self._m7_event("HOG HOP!", 24)
                    return pyglet.event.EVENT_HANDLED
            self.keys.add(symbol)
            return pyglet.event.EVENT_HANDLED

        return super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        if self.state in (self.STATE_M7_COUNTDOWN, self.STATE_M7_BATTLE):
            self.keys.discard(symbol)
            return pyglet.event.EVENT_HANDLED
        return super().on_key_release(symbol, modifiers)

    def update(self, dt):
        if not self.active:
            return
        dt = float(dt)

        if self.state == self.STATE_M7_COUNTDOWN:
            self.m7_countdown -= dt
            if self.m7_countdown > 120:
                self.m7_countdown_label.text = "3"
            elif self.m7_countdown > 60:
                self.m7_countdown_label.text = "2"
            elif self.m7_countdown > 0:
                self.m7_countdown_label.text = "1"
            else:
                self.state = self.STATE_M7_BATTLE
                self.m7_countdown_label.text = "BATTLE!"
                self.m7_event_timer = 35.0
            self._update_m7_projection()
            return

        if self.state == self.STATE_M7_BATTLE:
            if self.m7_countdown_label.visible:
                self.m7_countdown_label.visible = False
            self.m7_world_clock += dt
            self.m7_time_frames = max(0.0, self.m7_time_frames - dt)
            self.m7_camera_shake = max(0.0, self.m7_camera_shake - 0.45 * dt)

            self._update_m7_player(dt)
            self._update_m7_ai(dt)
            self._m7_racer_collisions()
            self._m7_sweeper_collisions()
            self._update_m7_projectiles(dt)
            self._update_m7_mines(dt)
            self._tick_m7_pickups(dt)
            self._update_m7_projection()
            self._update_m7_hud()
            self._m7_end_check()
            return

        if self.state in (self.STATE_M7_RULES, self.STATE_M7_ARENA, self.STATE_M7_FINISH):
            return

        super().update(dt)

    def start(self):
        self.selected_m7_rule = 0
        self.selected_m7_arena = 0
        super().start()

    def stop(self):
        self._clear_mode7_battle()
        super().stop()
