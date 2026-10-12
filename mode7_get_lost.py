"""Get Lost Mode: a huge free-roam pseudo-3D Kenny Batmobile sandbox."""

import math
import random

import pyglet

import mode7_full_content as full_content
import mode7_full_core as coremod
import mode7_full_flow as flowmod
import mode7_racing as base
from engineglobals import EngineGlobals
from mode7_get_lost_content import (
    BOOST_PADS,
    ENCOUNTERS,
    GET_LOST_ENTRY,
    GOLDEN_PIGS,
    HAZARD_ZONES,
    LANDMARKS,
    MOUNTAINS,
    PORTALS,
    RAMP_SITES,
    REGIONS,
    ROAD_SEGMENTS,
    SECRETS,
    START_SPAWN,
    WORLD_H,
    WORLD_W,
)
from mode7_snes_battle import Mode7ArenaBattleRacing


for module in (full_content, coremod, flowmod):
    modes = tuple(getattr(module, "MODES", ()))
    if not any(entry[0] == GET_LOST_ENTRY[0] for entry in modes):
        module.MODES = modes + (GET_LOST_ENTRY,)


LANDMARK_COLORS = {
    "trailer": (164, 154, 143),
    "barn": (163, 77, 70),
    "van": (91, 132, 158),
    "ketchup": (198, 42, 43),
    "bone": (229, 220, 189),
    "spud": (176, 132, 78),
    "moon": (224, 225, 207),
    "tub": (180, 211, 225),
    "toga": (229, 217, 188),
    "bat": (48, 52, 61),
    "tree": (67, 121, 69),
    "ufo": (127, 178, 174),
}

ROAD_DRAG = {
    "asphalt": 0.996,
    "dirt": 0.986,
    "farm": 0.989,
    "mountain": 0.992,
    "neon": 0.997,
    "lava": 0.991,
    "pier": 0.994,
    "moon": 0.998,
}


class GetLostMode7Racing(Mode7ArenaBattleRacing):
    """All existing 3D Reaching modes plus the Get Lost free-roam world."""

    STATE_GET_LOST = "get_lost"
    GL_NEAR_CLIP = 72.0
    GL_VIEW_DISTANCE = 2450.0
    GL_CAMERA_HEIGHT = 62.0
    GL_FOCAL = 345.0
    GL_KART_RADIUS = 34.0

    def __init__(self, on_exit_to_menu=None):
        self.gl_rng = random.Random(19920816)
        self.gl_player = None
        self.gl_shapes = []
        self.gl_labels = []
        self.gl_grid_lines = []
        self.gl_grid_segments = []
        self.gl_road_chunks = []
        self.gl_mountains = []
        self.gl_landmarks = []
        self.gl_encounters = []
        self.gl_pigs = []
        self.gl_hazards = []
        self.gl_ramps = []
        self.gl_boosts = []
        self.gl_portals = []
        self.gl_map_shapes = []
        self.gl_map_labels = []
        self.gl_collected_pigs = set()
        self.gl_found_secrets = set()
        self.gl_discovered_landmarks = set()
        self.gl_visited_encounters = set()
        self.gl_challenge_wins = set()
        self.gl_dialogue_index = {}
        self.gl_challenge = None
        self.gl_region = None
        self.gl_current_road = "OFF ROAD"
        self.gl_world_clock = 0.0
        self.gl_hop = 0.0
        self.gl_hop_total = 1.0
        self.gl_turbo = 0.0
        self.gl_ramp_cooldown = 0.0
        self.gl_hazard_cooldown = 0.0
        self.gl_portal_cooldown = 0.0
        self.gl_event_timer = 0.0
        self.gl_dialogue_timer = 0.0
        self.gl_camera_shake = 0.0
        self.gl_shake_x = 0.0
        self.gl_shake_y = 0.0
        self.gl_map_visible = True
        super().__init__(on_exit_to_menu=on_exit_to_menu)

    def _build_mode_select(self):
        self._clear_battle()
        self._clear_mode7_battle()
        self._clear_get_lost()
        self._clear_selection()
        self.state = self.STATE_MODE
        self._selection_header(
            "3D REACHING",
            "GRAND PRIX • QUICK RACE • TIME TRIAL • HOGGIN OUT • MODE 7 BATTLE • GET LOST",
        )
        self.mode_panels = []
        modes = tuple(coremod.MODES)
        ys = (456, 386, 316, 246, 176, 106)
        for i, (name, note) in enumerate(modes):
            y = ys[i] if i < len(ys) else 106 - (i - 5) * 62
            panel = pyglet.shapes.Rectangle(
                140, y - 24, 520, 50,
                color=(112, 123, 153) if i == self.selected_mode else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.mode_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                name, x=400, y=y + 5, anchor_x="center", font_size=14,
                weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                note, x=400, y=y - 11, anchor_x="center", font_size=7,
                color=(207, 219, 236, 255), batch=self.batch, group=self.ui_group,
            ))

    @staticmethod
    def _gl_delete(item):
        if item is None:
            return
        try:
            item.delete()
        except Exception:
            pass

    def _clear_get_lost(self):
        for collection_name in (
            "gl_shapes", "gl_labels", "gl_grid_lines", "gl_map_shapes", "gl_map_labels"
        ):
            collection = getattr(self, collection_name, [])
            for item in list(collection):
                self._gl_delete(item)
            collection.clear()
        self.gl_grid_segments = []
        self.gl_road_chunks = []
        self.gl_mountains = []
        self.gl_landmarks = []
        self.gl_encounters = []
        self.gl_pigs = []
        self.gl_hazards = []
        self.gl_ramps = []
        self.gl_boosts = []
        self.gl_portals = []
        self.gl_player = None
        self.gl_challenge = None

    def _make_gl_player(self):
        profile = base.CHARACTERS[self.selected_character]
        x, z, angle = START_SPAWN
        self.gl_player = {
            "profile": profile,
            "x": float(x), "z": float(z), "angle": float(angle),
            "speed": 0.0,
        }

    def _build_gl_grid(self):
        step = 600.0
        x = 0.0
        while x <= WORLD_W + 0.1:
            z = 0.0
            while z < WORLD_H:
                self.gl_grid_segments.append((x, z, x, min(WORLD_H, z + step)))
                z += step
            x += step
        z = 0.0
        while z <= WORLD_H + 0.1:
            x = 0.0
            while x < WORLD_W:
                self.gl_grid_segments.append((x, z, min(WORLD_W, x + step), z))
                x += step
            z += step
        for _ in self.gl_grid_segments:
            line = pyglet.shapes.Line(
                -1000, -1000, -1000, -1000, thickness=1,
                color=(92, 102, 92), batch=self.batch, group=self.road_group,
            )
            line.visible = False
            self.gl_grid_lines.append(line)

    def _build_gl_roads(self):
        for segment in ROAD_SEGMENTS:
            dx = segment["x2"] - segment["x1"]
            dz = segment["z2"] - segment["z1"]
            length = max(1.0, math.hypot(dx, dz))
            pieces = max(1, int(math.ceil(length / 260.0)))
            for i in range(pieces):
                t1 = i / pieces
                t2 = (i + 1) / pieces
                x1 = segment["x1"] + dx * t1
                z1 = segment["z1"] + dz * t1
                x2 = segment["x1"] + dx * t2
                z2 = segment["z1"] + dz * t2
                tri1 = pyglet.shapes.Triangle(
                    -1000, -1000, -1000, -1000, -1000, -1000,
                    color=segment["color"], batch=self.batch, group=self.road_group,
                )
                tri2 = pyglet.shapes.Triangle(
                    -1000, -1000, -1000, -1000, -1000, -1000,
                    color=segment["color"], batch=self.batch, group=self.road_group,
                )
                center = pyglet.shapes.Line(
                    -1000, -1000, -1000, -1000, thickness=1,
                    color=(225, 211, 155), batch=self.batch, group=self.scenery_group,
                )
                tri1.visible = tri2.visible = center.visible = False
                self.gl_shapes.extend((tri1, tri2, center))
                self.gl_road_chunks.append({
                    "x1": x1, "z1": z1, "x2": x2, "z2": z2,
                    "width": segment["width"], "tri1": tri1, "tri2": tri2,
                    "center": center,
                })

    def _build_gl_mountains(self):
        for x, z, radius, height, name in MOUNTAINS:
            peak = pyglet.shapes.Triangle(
                -1000, -1000, -1000, -1000, -1000, -1000,
                color=(82, 85, 77), batch=self.batch, group=self.scenery_group,
            )
            cap = pyglet.shapes.Triangle(
                -1000, -1000, -1000, -1000, -1000, -1000,
                color=(199, 199, 183), batch=self.batch, group=self.scenery_group,
            )
            label = pyglet.text.Label(
                name, x=-1000, y=-1000, anchor_x="center", font_size=7,
                color=(225, 229, 216, 255), batch=self.batch, group=self.ui_group,
            )
            peak.visible = cap.visible = label.visible = False
            self.gl_shapes.extend((peak, cap))
            self.gl_labels.append(label)
            self.gl_mountains.append({
                "x": float(x), "z": float(z), "radius": float(radius),
                "height": float(height), "name": name,
                "peak": peak, "cap": cap, "label": label,
            })

    def _build_gl_landmarks(self):
        for data in LANDMARKS:
            color = LANDMARK_COLORS.get(data["kind"], (190, 170, 130))
            body = pyglet.shapes.Rectangle(
                -1000, -1000, 4, 4, color=color,
                batch=self.batch, group=self.scenery_group,
            )
            top = pyglet.shapes.Circle(
                -1000, -1000, 2,
                color=tuple(min(255, c + 35) for c in color),
                batch=self.batch, group=self.scenery_group,
            )
            label = pyglet.text.Label(
                data["name"], x=-1000, y=-1000, anchor_x="center", font_size=7,
                color=(255, 236, 189, 255), batch=self.batch, group=self.ui_group,
            )
            body.visible = top.visible = label.visible = False
            self.gl_shapes.extend((body, top))
            self.gl_labels.append(label)
            item = dict(data)
            item.update({"body": body, "top": top, "label": label})
            self.gl_landmarks.append(item)

    def _build_gl_encounters(self):
        for data in ENCOUNTERS:
            marker = pyglet.shapes.Circle(
                -1000, -1000, 3, color=data["color"],
                batch=self.batch, group=self.scenery_group,
            )
            label = pyglet.text.Label(
                data["name"].upper(), x=-1000, y=-1000, anchor_x="center", font_size=8,
                weight=pyglet.text.Weight.BOLD, color=(255, 246, 219, 255),
                batch=self.batch, group=self.ui_group,
            )
            marker.visible = label.visible = False
            self.gl_shapes.append(marker)
            self.gl_labels.append(label)
            item = dict(data)
            item.update({"marker": marker, "label": label})
            self.gl_encounters.append(item)

    def _build_gl_pickups_and_features(self):
        for index, (x, z) in enumerate(GOLDEN_PIGS):
            shape = pyglet.shapes.Circle(
                -1000, -1000, 3, color=(247, 205, 67),
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.gl_shapes.append(shape)
            self.gl_pigs.append({"index": index, "x": float(x), "z": float(z), "shape": shape})

        for zone in HAZARD_ZONES:
            color = {
                "mud": (111, 78, 51), "water": (54, 119, 151), "lava": (226, 68, 29),
                "moon": (101, 111, 147), "oil": (30, 29, 35),
            }.get(zone["kind"], (120, 80, 70))
            shape = pyglet.shapes.Circle(
                -1000, -1000, 2, color=color,
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.gl_shapes.append(shape)
            item = dict(zone)
            item["shape"] = shape
            self.gl_hazards.append(item)

        for x, z, radius, power, name in RAMP_SITES:
            shape = pyglet.shapes.Rectangle(
                -1000, -1000, 4, 4, color=(220, 164, 68),
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.gl_shapes.append(shape)
            self.gl_ramps.append({
                "x": float(x), "z": float(z), "radius": float(radius),
                "power": float(power), "name": name, "shape": shape,
            })

        for x, z, radius, power in BOOST_PADS:
            shape = pyglet.shapes.Rectangle(
                -1000, -1000, 4, 4, color=(71, 210, 226),
                batch=self.batch, group=self.scenery_group,
            )
            shape.visible = False
            self.gl_shapes.append(shape)
            self.gl_boosts.append({
                "x": float(x), "z": float(z), "radius": float(radius),
                "power": float(power), "shape": shape,
            })

        for a, b, name in PORTALS:
            sa = pyglet.shapes.Circle(
                -1000, -1000, 3, color=(93, 216, 231),
                batch=self.batch, group=self.scenery_group,
            )
            sb = pyglet.shapes.Circle(
                -1000, -1000, 3, color=(216, 103, 231),
                batch=self.batch, group=self.scenery_group,
            )
            sa.visible = sb.visible = False
            self.gl_shapes.extend((sa, sb))
            self.gl_portals.append({"a": a, "b": b, "name": name, "sa": sa, "sb": sb})

    def _build_gl_player_kart(self):
        w = EngineGlobals.width
        profile = self.gl_player["profile"]
        self.gl_shadow = pyglet.shapes.Ellipse(
            w / 2, 52, 39, 9, color=(24, 24, 29),
            batch=self.batch, group=self.car_group,
        )
        self.gl_body = pyglet.shapes.Rectangle(
            w / 2 - 31, 62, 62, 30, color=(34, 37, 43),
            batch=self.batch, group=self.car_group,
        )
        self.gl_driver = pyglet.shapes.Circle(
            w / 2, 91, 11, color=profile["color"],
            batch=self.batch, group=self.car_group,
        )
        self.gl_nose = pyglet.shapes.Triangle(
            w / 2, 116, w / 2 - 28, 83, w / 2 + 28, 83,
            color=(43, 47, 54), batch=self.batch, group=self.car_group,
        )
        self.gl_shapes.extend((self.gl_shadow, self.gl_body, self.gl_driver, self.gl_nose))

    def _build_gl_hud(self):
        w, h = EngineGlobals.width, EngineGlobals.height
        self.gl_title_label = pyglet.text.Label(
            "GET LOST MODE", x=18, y=h - 24, font_size=13,
            weight=pyglet.text.Weight.BOLD, color=(255, 237, 157, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.gl_region_label = pyglet.text.Label(
            "", x=18, y=h - 46, font_size=9, color=(210, 224, 241, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.gl_road_label = pyglet.text.Label(
            "", x=18, y=h - 64, font_size=8, color=(188, 205, 228, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.gl_stats_label = pyglet.text.Label(
            "", x=18, y=42, font_size=9, weight=pyglet.text.Weight.BOLD,
            color=(255, 226, 141, 255), batch=self.batch, group=self.ui_group,
        )
        self.gl_speed_label = pyglet.text.Label(
            "", x=w - 18, y=25, anchor_x="right", font_size=9,
            color=(207, 222, 241, 255), batch=self.batch, group=self.ui_group,
        )
        self.gl_event_label = pyglet.text.Label(
            "", x=w // 2, y=150, anchor_x="center", font_size=13,
            weight=pyglet.text.Weight.BOLD, color=(255, 221, 126, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.gl_dialogue_label = pyglet.text.Label(
            "", x=w // 2, y=116, anchor_x="center", multiline=True, width=650,
            align="center", font_size=10, color=(246, 242, 224, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.gl_interact_label = pyglet.text.Label(
            "", x=w // 2, y=83, anchor_x="center", font_size=9,
            color=(231, 187, 239, 255), batch=self.batch, group=self.ui_group,
        )
        self.gl_challenge_label = pyglet.text.Label(
            "", x=w // 2, y=h - 28, anchor_x="center", font_size=10,
            weight=pyglet.text.Weight.BOLD, color=(255, 242, 185, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.gl_help_label = pyglet.text.Label(
            "ARROWS drive • SPACE hop • D talk/interact • R nearest road • M music • TAB map • ESC modes",
            x=w // 2, y=10, anchor_x="center", font_size=7,
            color=(188, 202, 224, 255), batch=self.batch, group=self.ui_group,
        )
        self.gl_labels.extend((
            self.gl_title_label, self.gl_region_label, self.gl_road_label,
            self.gl_stats_label, self.gl_speed_label, self.gl_event_label,
            self.gl_dialogue_label, self.gl_interact_label,
            self.gl_challenge_label, self.gl_help_label,
        ))
        self.gl_challenge_marker = pyglet.shapes.Circle(
            -1000, -1000, 3, color=(255, 225, 88),
            batch=self.batch, group=self.scenery_group,
        )
        self.gl_challenge_marker.visible = False
        self.gl_shapes.append(self.gl_challenge_marker)
        self._build_gl_minimap()

    def _build_gl_minimap(self):
        w, h = EngineGlobals.width, EngineGlobals.height
        left, bottom, mw, mh = w - 196, h - 154, 178, 122
        bg = pyglet.shapes.Rectangle(
            left, bottom, mw, mh, color=(27, 31, 40),
            batch=self.batch, group=self.ui_group,
        )
        bg.opacity = 210
        self.gl_map_shapes.append(bg)
        for segment in ROAD_SEGMENTS:
            x1 = left + segment["x1"] / WORLD_W * mw
            y1 = bottom + segment["z1"] / WORLD_H * mh
            x2 = left + segment["x2"] / WORLD_W * mw
            y2 = bottom + segment["z2"] / WORLD_H * mh
            line = pyglet.shapes.Line(
                x1, y1, x2, y2, thickness=2, color=segment["color"],
                batch=self.batch, group=self.ui_group,
            )
            self.gl_map_shapes.append(line)
        self.gl_map_player = pyglet.shapes.Circle(
            left + mw / 2, bottom + mh / 2, 4, color=(255, 224, 86),
            batch=self.batch, group=self.ui_group,
        )
        self.gl_map_shapes.append(self.gl_map_player)
        self.gl_map_label = pyglet.text.Label(
            "LOST MAP", x=left + mw / 2, y=bottom + mh - 13, anchor_x="center",
            font_size=7, color=(223, 230, 242, 255), batch=self.batch, group=self.ui_group,
        )
        self.gl_map_labels.append(self.gl_map_label)

    def _build_get_lost_world(self):
        self._clear_race()
        self._clear_battle()
        self._clear_mode7_battle()
        self._clear_get_lost()
        self._clear_selection()
        self.state = self.STATE_GET_LOST
        self.keys.clear()
        self.gl_collected_pigs = set()
        self.gl_found_secrets = set()
        self.gl_discovered_landmarks = set()
        self.gl_visited_encounters = set()
        self.gl_challenge_wins = set()
        self.gl_dialogue_index = {}
        self.gl_challenge = None
        self.gl_region = None
        self.gl_current_road = "OFF ROAD"
        self.gl_world_clock = 0.0
        self.gl_hop = 0.0
        self.gl_hop_total = 1.0
        self.gl_turbo = 0.0
        self.gl_ramp_cooldown = 0.0
        self.gl_hazard_cooldown = 0.0
        self.gl_portal_cooldown = 0.0
        self.gl_event_timer = 0.0
        self.gl_dialogue_timer = 0.0
        self.gl_camera_shake = 0.0
        self.gl_map_visible = True
        self._make_gl_player()

        w, h = EngineGlobals.width, EngineGlobals.height
        self.gl_sky = pyglet.shapes.Rectangle(
            0, h * 0.50, w, h * 0.50, color=(68, 87, 119),
            batch=self.batch, group=self.bg_group,
        )
        self.gl_ground = pyglet.shapes.Rectangle(
            0, 0, w, h * 0.51, color=(77, 104, 72),
            batch=self.batch, group=self.bg_group,
        )
        self.gl_horizon = pyglet.shapes.Line(
            0, h * 0.50, w, h * 0.50, thickness=2, color=(188, 184, 154),
            batch=self.batch, group=self.road_group,
        )
        self.gl_sun = pyglet.shapes.Circle(
            w - 115, h - 88, 34, color=(237, 220, 158),
            batch=self.batch, group=self.bg_group,
        )
        self.gl_shapes.extend((self.gl_sky, self.gl_ground, self.gl_horizon, self.gl_sun))

        self._build_gl_grid()
        self._build_gl_roads()
        self._build_gl_mountains()
        self._build_gl_landmarks()
        self._build_gl_encounters()
        self._build_gl_pickups_and_features()
        self._build_gl_player_kart()
        self._build_gl_hud()
        self._gl_update_region(force=True)
        self._gl_event("WELCOME TO NOWHERE. PICK A ROAD OR DON'T.", 180.0)
        self._update_gl_projection()
        self._update_gl_hud()

    def _gl_project(self, wx, wz):
        player = self.gl_player
        if player is None:
            return None
        angle = player["angle"]
        sin_a, cos_a = math.sin(angle), math.cos(angle)
        cam_x = player["x"] - sin_a * 88.0
        cam_z = player["z"] - cos_a * 88.0
        dx = float(wx) - cam_x
        dz = float(wz) - cam_z
        forward = dx * sin_a + dz * cos_a
        if forward < self.GL_NEAR_CLIP or forward > self.GL_VIEW_DISTANCE:
            return None
        lateral = dx * cos_a - dz * sin_a
        horizon = EngineGlobals.height * 0.50
        sx = EngineGlobals.width * 0.5 + lateral * (self.GL_FOCAL / forward) + self.gl_shake_x
        sy = horizon - self.GL_CAMERA_HEIGHT * (self.GL_FOCAL / forward) + self.gl_shake_y
        scale = max(0.08, min(2.0, 280.0 / (forward + 55.0)))
        return sx, sy, scale, forward

    def _gl_project_segment(self, x1, z1, x2, z2):
        p1 = self._gl_project(x1, z1)
        p2 = self._gl_project(x2, z2)
        if p1 is None or p2 is None:
            return None
        return p1, p2

    @staticmethod
    def _set_tri(tri, p1, p2, p3):
        tri.x, tri.y = p1
        tri.x2, tri.y2 = p2
        tri.x3, tri.y3 = p3

    def _project_gl_roads(self):
        for chunk in self.gl_road_chunks:
            dx = chunk["x2"] - chunk["x1"]
            dz = chunk["z2"] - chunk["z1"]
            length = max(1.0, math.hypot(dx, dz))
            nx, nz = -dz / length, dx / length
            half = chunk["width"] * 0.5
            corners = (
                (chunk["x1"] + nx * half, chunk["z1"] + nz * half),
                (chunk["x1"] - nx * half, chunk["z1"] - nz * half),
                (chunk["x2"] + nx * half, chunk["z2"] + nz * half),
                (chunk["x2"] - nx * half, chunk["z2"] - nz * half),
            )
            projected = [self._gl_project(x, z) for x, z in corners]
            tri1, tri2, center = chunk["tri1"], chunk["tri2"], chunk["center"]
            if any(p is None for p in projected):
                tri1.visible = tri2.visible = center.visible = False
                continue
            p0, p1, p2, p3 = projected
            tri1.visible = tri2.visible = center.visible = True
            self._set_tri(tri1, (p0[0], p0[1]), (p1[0], p1[1]), (p2[0], p2[1]))
            self._set_tri(tri2, (p1[0], p1[1]), (p3[0], p3[1]), (p2[0], p2[1]))
            c1 = self._gl_project(chunk["x1"], chunk["z1"])
            c2 = self._gl_project(chunk["x2"], chunk["z2"])
            if c1 is None or c2 is None:
                center.visible = False
            else:
                center.x, center.y = c1[0], c1[1]
                center.x2, center.y2 = c2[0], c2[1]
                center.thickness = max(1.0, min(5.0, 2.5 * (c1[2] + c2[2]) * 0.5))

    def _update_gl_grid(self):
        for line, segment in zip(self.gl_grid_lines, self.gl_grid_segments):
            projected = self._gl_project_segment(*segment)
            if projected is None:
                line.visible = False
                continue
            p1, p2 = projected
            line.visible = True
            line.x, line.y = p1[0], p1[1]
            line.x2, line.y2 = p2[0], p2[1]

    def _project_gl_circle(self, shape, x, z, radius):
        p = self._gl_project(x, z)
        if p is None:
            shape.visible = False
            return None
        sx, sy, scale, _ = p
        shape.visible = True
        shape.radius = max(2.0, min(70.0, radius * scale))
        shape.position = (sx, sy + shape.radius * 0.12)
        return p

    def _project_gl_rect(self, shape, x, z, width, height=20.0):
        p = self._gl_project(x, z)
        if p is None:
            shape.visible = False
            return None
        sx, sy, scale, _ = p
        shape.visible = True
        shape.width = max(3.0, min(130.0, width * scale))
        shape.height = max(3.0, min(110.0, height * scale))
        shape.position = (sx - shape.width / 2.0, sy)
        return p

    def _update_gl_projection(self):
        if self.gl_player is None:
            return
        if self.gl_camera_shake > 0:
            self.gl_shake_x = self.gl_rng.uniform(-self.gl_camera_shake, self.gl_camera_shake)
            self.gl_shake_y = self.gl_rng.uniform(-self.gl_camera_shake * 0.3, self.gl_camera_shake * 0.3)
        else:
            self.gl_shake_x = self.gl_shake_y = 0.0
        self._update_gl_grid()
        self._project_gl_roads()

        for mountain in self.gl_mountains:
            p = self._gl_project(mountain["x"], mountain["z"])
            peak, cap, label = mountain["peak"], mountain["cap"], mountain["label"]
            if p is None:
                peak.visible = cap.visible = label.visible = False
                continue
            sx, sy, scale, forward = p
            base_width = max(8.0, min(250.0, mountain["radius"] * scale * 0.55))
            height = max(15.0, min(300.0, mountain["height"] * scale * 0.48))
            peak.visible = cap.visible = True
            self._set_tri(peak, (sx - base_width, sy), (sx + base_width, sy), (sx, sy + height))
            self._set_tri(cap, (sx - base_width * 0.30, sy + height * 0.70),
                          (sx + base_width * 0.30, sy + height * 0.70), (sx, sy + height))
            label.visible = forward < 1500
            if label.visible:
                label.x, label.y = sx, sy + height + 8

        for landmark in self.gl_landmarks:
            p = self._project_gl_rect(landmark["body"], landmark["x"], landmark["z"], 95, 105)
            if p is None:
                landmark["top"].visible = landmark["label"].visible = False
                continue
            sx, sy, scale, forward = p
            landmark["top"].visible = True
            landmark["top"].radius = max(3.0, min(24.0, 18.0 * scale))
            landmark["top"].position = (sx, sy + landmark["body"].height)
            landmark["label"].visible = forward < 1100
            if landmark["label"].visible:
                landmark["label"].x = sx
                landmark["label"].y = sy + landmark["body"].height + 22

        for encounter in self.gl_encounters:
            p = self._project_gl_circle(encounter["marker"], encounter["x"], encounter["z"], 26)
            if p is None:
                encounter["label"].visible = False
                continue
            encounter["label"].visible = p[3] < 850
            if encounter["label"].visible:
                encounter["label"].x = p[0]
                encounter["label"].y = p[1] + encounter["marker"].radius + 14

        for pig in self.gl_pigs:
            if pig["index"] in self.gl_collected_pigs:
                pig["shape"].visible = False
            else:
                self._project_gl_circle(pig["shape"], pig["x"], pig["z"], 16)

        for zone in self.gl_hazards:
            self._project_gl_circle(zone["shape"], zone["x"], zone["z"], zone["radius"])
        for ramp in self.gl_ramps:
            self._project_gl_rect(ramp["shape"], ramp["x"], ramp["z"], 85, 18)
        for boost in self.gl_boosts:
            self._project_gl_rect(boost["shape"], boost["x"], boost["z"], 92, 9)
        for portal in self.gl_portals:
            self._project_gl_circle(portal["sa"], portal["a"][0], portal["a"][1], 42)
            self._project_gl_circle(portal["sb"], portal["b"][0], portal["b"][1], 42)

        if self.gl_challenge is not None:
            points = self.gl_challenge["points"]
            index = self.gl_challenge["index"]
            if index < len(points):
                x, z = points[index]
                self._project_gl_circle(self.gl_challenge_marker, x, z, 44)
            else:
                self.gl_challenge_marker.visible = False
        else:
            self.gl_challenge_marker.visible = False

        progress = 1.0 - self.gl_hop / max(1.0, self.gl_hop_total)
        hop_y = math.sin(max(0.0, min(1.0, progress)) * math.pi) * 32.0 if self.gl_hop > 0 else 0.0
        w = EngineGlobals.width
        base_y = 62 + hop_y
        self.gl_shadow.position = (w / 2, 52)
        self.gl_body.position = (w / 2 - 31, base_y)
        self.gl_driver.position = (w / 2, base_y + 29)
        self.gl_nose.x, self.gl_nose.y = w / 2, base_y + 54
        self.gl_nose.x2, self.gl_nose.y2 = w / 2 - 28, base_y + 21
        self.gl_nose.x3, self.gl_nose.y3 = w / 2 + 28, base_y + 21
        self._update_gl_minimap()

    @staticmethod
    def _point_segment_distance(px, pz, x1, z1, x2, z2):
        dx, dz = x2 - x1, z2 - z1
        length2 = dx * dx + dz * dz
        if length2 <= 0.0001:
            return math.hypot(px - x1, pz - z1), x1, z1, 0.0
        t = ((px - x1) * dx + (pz - z1) * dz) / length2
        t = max(0.0, min(1.0, t))
        qx, qz = x1 + t * dx, z1 + t * dz
        return math.hypot(px - qx, pz - qz), qx, qz, t

    def _nearest_road(self, x=None, z=None):
        if self.gl_player is None:
            return None
        px = self.gl_player["x"] if x is None else float(x)
        pz = self.gl_player["z"] if z is None else float(z)
        best = None
        for segment in ROAD_SEGMENTS:
            distance, qx, qz, t = self._point_segment_distance(
                px, pz, segment["x1"], segment["z1"], segment["x2"], segment["z2"]
            )
            if best is None or distance < best["distance"]:
                best = {
                    "distance": distance, "qx": qx, "qz": qz, "t": t,
                    "segment": segment,
                }
        return best

    @staticmethod
    def _inside_rect(x, z, rect):
        rx, rz, rw, rh = rect
        return rx <= x <= rx + rw and rz <= z <= rz + rh

    def _region_at(self, x, z):
        matches = [region for region in REGIONS if self._inside_rect(x, z, region["rect"])]
        if matches:
            return matches[-1]
        return {"name": "KENNY WILDERNESS", "ground": (77, 104, 72),
                "offroad": 0.972, "music": "takingahike.wav"}

    def _gl_update_region(self, force=False):
        region = self._region_at(self.gl_player["x"], self.gl_player["z"])
        name = region["name"]
        previous = self.gl_region["name"] if self.gl_region else None
        self.gl_region = region
        self.gl_ground.color = region["ground"]
        if force or name != previous:
            self._play_music_file(region["music"])
            if not force:
                self._gl_event("ENTERING {}".format(name), 90.0)

    def _reset_to_nearest_road(self, message="BACK ON THE ROAD"):
        nearest = self._nearest_road()
        if not nearest:
            return
        segment = nearest["segment"]
        self.gl_player["x"] = nearest["qx"]
        self.gl_player["z"] = nearest["qz"]
        self.gl_player["angle"] = math.atan2(
            segment["x2"] - segment["x1"], segment["z2"] - segment["z1"]
        )
        self.gl_player["speed"] = 0.0
        self.gl_turbo = 0.0
        self._gl_event(message, 65.0)

    def _gl_physics(self):
        profile = self.gl_player["profile"]
        engine = self._class_def()
        max_speed = (4.7 + profile["speed"] * 0.31) * engine["speed"]
        return {
            "max_speed": max_speed,
            "boost_speed": max_speed + 1.8 + profile["boost"] * 0.11,
            "accel": (0.085 + profile["accel"] * 0.0105) * engine["accel"],
            "reverse": 2.2 + profile["accel"] * 0.05,
            "turn": 0.025 + profile["turn"] * 0.0027,
            "grip": float(profile["grip"]),
        }

    def _gl_event(self, text, frames=80.0):
        if hasattr(self, "gl_event_label"):
            self.gl_event_label.text = text
        self.gl_event_timer = max(self.gl_event_timer, float(frames))

    def _nearby_encounter(self):
        if self.gl_player is None:
            return None
        best = None
        for encounter in self.gl_encounters:
            distance = math.hypot(
                self.gl_player["x"] - encounter["x"], self.gl_player["z"] - encounter["z"]
            )
            if distance <= 175 and (best is None or distance < best[0]):
                best = (distance, encounter)
        return best[1] if best else None

    def _interact_get_lost(self):
        encounter = self._nearby_encounter()
        if encounter is None:
            self._gl_event("KENNY HONKS INTO THE VOID. THE VOID DECLINES TO ANSWER.", 80.0)
            return
        name = encounter["name"]
        self.gl_visited_encounters.add(name)
        lines = encounter["dialogue"]
        index = self.gl_dialogue_index.get(name, 0)
        if index < len(lines):
            self.gl_dialogue_label.text = "{}: {}".format(name.upper(), lines[index])
            self.gl_dialogue_timer = 240.0
            self.gl_dialogue_index[name] = index + 1
            return
        challenge = encounter.get("challenge")
        if challenge and challenge["name"] not in self.gl_challenge_wins:
            if self.gl_challenge is None:
                self._start_gl_challenge(challenge)
            else:
                self._gl_event("FINISH THE CURRENT CHALLENGE FIRST.", 70.0)
        else:
            self.gl_dialogue_label.text = "{}: That is all I've got, Kenny.".format(name.upper())
            self.gl_dialogue_timer = 150.0
        self.gl_dialogue_index[name] = 0

    def _start_gl_challenge(self, data):
        self.gl_challenge = {
            "name": data["name"],
            "time": float(data["time"]) * 60.0,
            "points": tuple(data["points"]),
            "index": 0,
        }
        self._gl_event("CHALLENGE START: {}".format(data["name"]), 100.0)

    def _update_gl_challenge(self, dt):
        if self.gl_challenge is None:
            return
        challenge = self.gl_challenge
        challenge["time"] -= dt
        if challenge["time"] <= 0:
            self._gl_event("{} FAILED. GET MORE LOST AND TRY AGAIN.".format(challenge["name"]), 120.0)
            self.gl_challenge = None
            return
        points = challenge["points"]
        index = challenge["index"]
        if index < len(points):
            x, z = points[index]
            if math.hypot(self.gl_player["x"] - x, self.gl_player["z"] - z) < 135:
                challenge["index"] += 1
                if challenge["index"] >= len(points):
                    name = challenge["name"]
                    self.gl_challenge_wins.add(name)
                    self._gl_event("{} COMPLETE! GOLDEN HOG HONOR AWARDED.".format(name), 150.0)
                    self.gl_challenge = None
                else:
                    self._gl_event("CHECKPOINT {}/{}".format(challenge["index"], len(points)), 55.0)

    def _handle_gl_world_features(self, dt, on_road):
        p = self.gl_player
        self.gl_ramp_cooldown = max(0.0, self.gl_ramp_cooldown - dt)
        self.gl_hazard_cooldown = max(0.0, self.gl_hazard_cooldown - dt)
        self.gl_portal_cooldown = max(0.0, self.gl_portal_cooldown - dt)

        for ramp in self.gl_ramps:
            if self.gl_ramp_cooldown <= 0 and math.hypot(p["x"] - ramp["x"], p["z"] - ramp["z"]) < ramp["radius"]:
                self.gl_hop_total = 72.0 * ramp["power"]
                self.gl_hop = self.gl_hop_total
                self.gl_turbo = max(self.gl_turbo, 34.0 * ramp["power"])
                self.gl_ramp_cooldown = 100.0
                self._gl_event("{}!".format(ramp["name"]), 60.0)
                break

        for boost in self.gl_boosts:
            if math.hypot(p["x"] - boost["x"], p["z"] - boost["z"]) < boost["radius"]:
                self.gl_turbo = max(self.gl_turbo, 48.0 * boost["power"])
                physics = self._gl_physics()
                p["speed"] = max(p["speed"], physics["max_speed"] + 1.0)
                break

        if self.gl_hazard_cooldown <= 0 and self.gl_hop <= 0:
            for zone in self.gl_hazards:
                if math.hypot(p["x"] - zone["x"], p["z"] - zone["z"]) >= zone["radius"]:
                    continue
                kind = zone["kind"]
                self.gl_hazard_cooldown = 120.0
                self.gl_camera_shake = 8.0
                if kind == "mud":
                    p["speed"] *= 0.45
                elif kind == "water":
                    p["speed"] *= -0.22
                    p["angle"] += math.pi * 0.3
                elif kind == "lava":
                    self._reset_to_nearest_road("KENNY HAS BEEN POLITELY REMOVED FROM THE LAVA")
                elif kind == "moon":
                    self.gl_hop_total = 100.0
                    self.gl_hop = self.gl_hop_total
                    self.gl_turbo = max(self.gl_turbo, 35.0)
                elif kind == "oil":
                    p["angle"] += 1.35
                    p["speed"] *= 0.50
                self._gl_event(zone["name"], 75.0)
                break

        if self.gl_portal_cooldown <= 0:
            for portal in self.gl_portals:
                for source_key, target_key in (("a", "b"), ("b", "a")):
                    source = portal[source_key]
                    if math.hypot(p["x"] - source[0], p["z"] - source[1]) < 95:
                        target = portal[target_key]
                        p["x"], p["z"] = float(target[0]), float(target[1])
                        self.gl_portal_cooldown = 150.0
                        self.gl_camera_shake = 10.0
                        self._gl_event(portal["name"], 100.0)
                        return

        for pig in self.gl_pigs:
            if pig["index"] in self.gl_collected_pigs:
                continue
            if math.hypot(p["x"] - pig["x"], p["z"] - pig["z"]) < 65:
                self.gl_collected_pigs.add(pig["index"])
                pig["shape"].visible = False
                self._gl_event("GOLDEN PIG {}/24!".format(len(self.gl_collected_pigs)), 75.0)
                if len(self.gl_collected_pigs) == len(self.gl_pigs):
                    self._gl_event("ALL 24 GOLDEN PIGS! KENNY HAS ACHIEVED MAXIMUM HOG.", 220.0)
                break

        for x, z, name, text in SECRETS:
            if name in self.gl_found_secrets:
                continue
            if math.hypot(p["x"] - x, p["z"] - z) < 90:
                self.gl_found_secrets.add(name)
                self.gl_dialogue_label.text = "EASTER EGG — {}\n{}".format(name, text)
                self.gl_dialogue_timer = 260.0
                self._gl_event("SECRET {}/12".format(len(self.gl_found_secrets)), 80.0)
                break

        for landmark in self.gl_landmarks:
            name = landmark["name"]
            if name in self.gl_discovered_landmarks:
                continue
            if math.hypot(p["x"] - landmark["x"], p["z"] - landmark["z"]) < 185:
                self.gl_discovered_landmarks.add(name)
                self.gl_dialogue_label.text = "DISCOVERED: {}\n{}".format(name, landmark["text"])
                self.gl_dialogue_timer = 220.0
                break

        if not on_road:
            for mountain in self.gl_mountains:
                distance = math.hypot(p["x"] - mountain["x"], p["z"] - mountain["z"])
                if distance < mountain["radius"]:
                    p["speed"] *= 0.965 ** dt
                    break

    def _update_gl_player(self, dt):
        p = self.gl_player
        physics = self._gl_physics()
        nearest = self._nearest_road()
        segment = nearest["segment"] if nearest else None
        on_road = bool(nearest and nearest["distance"] <= segment["width"] * 0.5 + 28.0)
        road_kind = segment["kind"] if on_road else None
        self.gl_current_road = segment["name"] if on_road else "OFF ROAD"

        up = pyglet.window.key.UP in self.keys
        down = pyglet.window.key.DOWN in self.keys
        left = pyglet.window.key.LEFT in self.keys
        right = pyglet.window.key.RIGHT in self.keys

        if up:
            p["speed"] += physics["accel"] * dt
        elif down:
            if p["speed"] > 0.2:
                p["speed"] -= physics["accel"] * 1.45 * dt
            else:
                p["speed"] -= physics["accel"] * 0.78 * dt
        else:
            drag = ROAD_DRAG.get(road_kind, self.gl_region.get("offroad", 0.972)) if on_road else self.gl_region.get("offroad", 0.972)
            p["speed"] *= drag ** dt

        self.gl_turbo = max(0.0, self.gl_turbo - dt)
        self.gl_hop = max(0.0, self.gl_hop - dt)
        self.gl_camera_shake = max(0.0, self.gl_camera_shake - dt * 0.65)

        top = physics["boost_speed"] if self.gl_turbo > 0 else physics["max_speed"]
        if not on_road:
            top *= 0.73
        p["speed"] = max(-physics["reverse"], min(top, p["speed"]))

        steer = (1.0 if right else 0.0) - (1.0 if left else 0.0)
        if abs(p["speed"]) > 0.08 and steer:
            direction = 1.0 if p["speed"] >= 0 else -0.65
            grip_scale = 0.88 + physics["grip"] * 0.018
            if not on_road:
                grip_scale *= 0.82
            if self.gl_hop > 0:
                grip_scale *= 1.18
            p["angle"] += steer * physics["turn"] * direction * grip_scale * dt

        p["x"] += math.sin(p["angle"]) * p["speed"] * dt
        p["z"] += math.cos(p["angle"]) * p["speed"] * dt
        p["x"] = max(self.GL_KART_RADIUS, min(WORLD_W - self.GL_KART_RADIUS, p["x"]))
        p["z"] = max(self.GL_KART_RADIUS, min(WORLD_H - self.GL_KART_RADIUS, p["z"]))

        self._handle_gl_world_features(dt, on_road)
        self._gl_update_region()
        self._update_gl_challenge(dt)

    def _update_gl_minimap(self):
        if not hasattr(self, "gl_map_player"):
            return
        w, h = EngineGlobals.width, EngineGlobals.height
        left, bottom, mw, mh = w - 196, h - 154, 178, 122
        self.gl_map_player.x = left + self.gl_player["x"] / WORLD_W * mw
        self.gl_map_player.y = bottom + self.gl_player["z"] / WORLD_H * mh
        for item in self.gl_map_shapes + self.gl_map_labels:
            item.visible = self.gl_map_visible

    def _update_gl_hud(self):
        if self.gl_player is None:
            return
        profile = self.gl_player["profile"]
        engine = self._class_def()["name"]
        self.gl_region_label.text = "{} • {} • {}".format(
            self.gl_region["name"], engine, profile["name"].upper()
        )
        self.gl_road_label.text = "ROAD: {}".format(self.gl_current_road)
        self.gl_stats_label.text = "GOLDEN PIGS {}/24 • SECRETS {}/12 • ENCOUNTERS {}/8 • CHALLENGES {}".format(
            len(self.gl_collected_pigs), len(self.gl_found_secrets),
            len(self.gl_visited_encounters), len(self.gl_challenge_wins),
        )
        boost = " • BOOST" if self.gl_turbo > 0 else ""
        self.gl_speed_label.text = "BATMOBILE {:.1f}{}".format(abs(self.gl_player["speed"]), boost)
        encounter = self._nearby_encounter()
        self.gl_interact_label.text = (
            "D — TALK TO {}".format(encounter["name"].upper()) if encounter else ""
        )
        if self.gl_challenge is not None:
            seconds = max(0, int(math.ceil(self.gl_challenge["time"] / 60.0)))
            self.gl_challenge_label.text = "{} • {}s • CHECKPOINT {}/{}".format(
                self.gl_challenge["name"], seconds,
                self.gl_challenge["index"] + 1,
                len(self.gl_challenge["points"]),
            )
        else:
            self.gl_challenge_label.text = ""

        if self.gl_event_timer > 0:
            self.gl_event_timer -= 1.0
            if self.gl_event_timer <= 0:
                self.gl_event_label.text = ""
        if self.gl_dialogue_timer > 0:
            self.gl_dialogue_timer -= 1.0
            if self.gl_dialogue_timer <= 0:
                self.gl_dialogue_label.text = ""

    def _start_get_lost(self):
        self._build_get_lost_world()

    def start(self):
        super().start()

    def stop(self):
        self._clear_get_lost()
        super().stop()

    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        enter = symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN)

        if self.state == self.STATE_CHARACTER and self.play_mode == "GET LOST MODE" and enter:
            self._start_get_lost()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_GET_LOST:
            if symbol == pyglet.window.key.ESCAPE:
                self.keys.clear()
                self._build_mode_select()
                return pyglet.event.EVENT_HANDLED
            if symbol == pyglet.window.key.SPACE:
                if self.gl_hop <= 0:
                    self.gl_hop_total = 46.0
                    self.gl_hop = self.gl_hop_total
                    self._gl_event("HOG HOP!", 32.0)
                return pyglet.event.EVENT_HANDLED
            if symbol == pyglet.window.key.D:
                self._interact_get_lost()
                return pyglet.event.EVENT_HANDLED
            if symbol == pyglet.window.key.R:
                self._reset_to_nearest_road()
                return pyglet.event.EVENT_HANDLED
            if symbol == pyglet.window.key.M:
                self._next_music()
                self._gl_event("NOW PLAYING {}".format(self._music_display(self.music_name)), 65.0)
                return pyglet.event.EVENT_HANDLED
            if symbol == pyglet.window.key.TAB:
                self.gl_map_visible = not self.gl_map_visible
                self._update_gl_minimap()
                return pyglet.event.EVENT_HANDLED
            self.keys.add(symbol)
            return pyglet.event.EVENT_HANDLED

        return super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        if self.state == self.STATE_GET_LOST:
            self.keys.discard(symbol)
            return pyglet.event.EVENT_HANDLED
        return super().on_key_release(symbol, modifiers)

    def update(self, dt):
        if not self.active:
            return
        if self.state == self.STATE_GET_LOST:
            dt = float(dt)
            self.gl_world_clock += dt
            self._update_gl_player(dt)
            self._update_gl_projection()
            self._update_gl_hud()
            return
        super().update(dt)
