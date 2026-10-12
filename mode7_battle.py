"""Hoggin Out battle mode layered onto the deluxe 3D Reaching racer."""

import math
import random

import pyglet

import mode7_full_content as full_content
import mode7_full_core as coremod
import mode7_full_flow as flowmod
import mode7_racing as base
from engineglobals import EngineGlobals
from mode7_battle_content import (
    BATTLE_ARENAS, BATTLE_ITEMS, BATTLE_MODES,
    BATTLE_START_BALLOONS, BATTLE_TIME_SECONDS,
)
from mode7_deluxe import DeluxeMode7Racing


HOGGIN_OUT_ENTRY = (
    "HOGGIN OUT",
    "Eight-racer battle mode with balloons, score battles, Coin Hog, and 8 arenas.",
)

for module in (full_content, coremod, flowmod):
    modes = tuple(getattr(module, "MODES", ()))
    if not any(entry[0] == "HOGGIN OUT" for entry in modes):
        module.MODES = modes + (HOGGIN_OUT_ENTRY,)


class HogginOutMode7Racing(DeluxeMode7Racing):
    """Deluxe racing plus a complete top-down 8-racer battle game."""

    STATE_BATTLE_RULES = "battle_rules"
    STATE_BATTLE_ARENA = "battle_arena"
    STATE_BATTLE_COUNTDOWN = "battle_countdown"
    STATE_BATTLE = "battle"
    STATE_BATTLE_FINISH = "battle_finish"

    BATTLE_MIN_X = 42.0
    BATTLE_MAX_X = 758.0
    BATTLE_MIN_Y = 82.0
    BATTLE_MAX_Y = 520.0
    BATTLE_RADIUS = 14.0

    def __init__(self, on_exit_to_menu=None):
        self.selected_battle_rule = 0
        self.selected_battle_arena = 0
        self.battle_shapes = []
        self.battle_labels = []
        self.battle_item_boxes = []
        self.battle_coins = []
        self.battle_projectiles = []
        self.battle_mines = []
        self.battle_racers = []
        self.battle_player = None
        self.battle_countdown = 180.0
        self.battle_time_frames = 0.0
        self.battle_event_timer = 0.0
        self.battle_rng = random.Random(2808)
        self.battle_finish_place = None
        self.battle_last_results = []
        self.battle_elimination_counter = 8
        super().__init__(on_exit_to_menu=on_exit_to_menu)

    def _build_mode_select(self):
        self._clear_battle()
        self._clear_selection()
        self.state = self.STATE_MODE
        self._selection_header(
            "3D REACHING",
            "GRAND PRIX • QUICK RACE • TIME TRIAL • HOGGIN OUT BATTLE",
        )
        self.mode_panels = []
        modes = tuple(coremod.MODES)
        for i, (name, note) in enumerate(modes):
            y = 430 - i * 100
            panel = pyglet.shapes.Rectangle(
                145, y - 31, 510, 64,
                color=(112, 123, 153) if i == self.selected_mode else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.mode_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                name, x=400, y=y + 8, anchor_x="center",
                font_size=18, weight=pyglet.text.Weight.BOLD,
                color=(255, 239, 165, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                note, x=400, y=y - 15, anchor_x="center", font_size=9,
                color=(207, 219, 236, 255), batch=self.batch, group=self.ui_group,
            ))

    def _build_battle_rules(self):
        self._stop_race_music()
        self._clear_battle()
        self._clear_selection()
        self.state = self.STATE_BATTLE_RULES
        self._selection_header("HOGGIN OUT", "CHOOSE THE BATTLE RULES")
        self.battle_rule_panels = []
        for i, (name, note) in enumerate(BATTLE_MODES):
            y = 410 - i * 125
            panel = pyglet.shapes.Rectangle(
                155, y - 42, 490, 86,
                color=(118, 105, 143) if i == self.selected_battle_rule else (47, 51, 64),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.battle_rule_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                name, x=400, y=y + 12, anchor_x="center", font_size=20,
                weight=pyglet.text.Weight.BOLD, color=(255, 231, 143, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                note, x=400, y=y - 17, anchor_x="center", font_size=10,
                color=(206, 220, 239, 255), batch=self.batch, group=self.ui_group,
            ))

    def _refresh_battle_rules(self):
        for i, panel in enumerate(self.battle_rule_panels):
            panel.color = (118, 105, 143) if i == self.selected_battle_rule else (47, 51, 64)

    def _build_battle_arena_select(self):
        self._stop_race_music()
        self._clear_battle()
        self._clear_selection()
        self.state = self.STATE_BATTLE_ARENA
        self._selection_header("HOGGIN OUT", "CHOOSE ONE OF 8 CUSTOM BATTLE TRACKS")
        self.battle_arena_panels = []
        for i, arena in enumerate(BATTLE_ARENAS):
            col, row = i % 4, i // 4
            x = 105 + col * 195
            y = 370 - row * 190
            panel = pyglet.shapes.Rectangle(
                x - 86, y - 68, 172, 136,
                color=(112, 111, 151) if i == self.selected_battle_arena else (44, 49, 62),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.battle_arena_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                arena["name"].upper(), x=x, y=y + 42, anchor_x="center",
                multiline=True, width=158, align="center", font_size=9,
                weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                arena["tagline"], x=x, y=y + 12, anchor_x="center", anchor_y="top",
                multiline=True, width=150, align="center", font_size=7,
                color=(200, 214, 234, 255), batch=self.batch, group=self.ui_group,
            ))
        self.battle_arena_detail = pyglet.text.Label(
            "", x=400, y=55, anchor_x="center", font_size=9,
            color=(255, 220, 132, 255), batch=self.batch, group=self.ui_group,
        )
        self.selection_labels.append(self.battle_arena_detail)
        self._refresh_battle_arena_select()

    def _refresh_battle_arena_select(self):
        for i, panel in enumerate(self.battle_arena_panels):
            panel.color = (112, 111, 151) if i == self.selected_battle_arena else (44, 49, 62)
        arena = BATTLE_ARENAS[self.selected_battle_arena]
        self.battle_arena_detail.text = "{} • {} • {}".format(
            BATTLE_MODES[self.selected_battle_rule][0],
            arena["hazard_name"],
            self._music_display(arena["music"]),
        )

    def _clear_battle(self):
        for projectile in list(getattr(self, "battle_projectiles", [])):
            shape = projectile.get("shape")
            if shape is not None:
                try:
                    shape.delete()
                except Exception:
                    pass
        for mine in list(getattr(self, "battle_mines", [])):
            shape = mine.get("shape")
            if shape is not None:
                try:
                    shape.delete()
                except Exception:
                    pass
        self.battle_projectiles = []
        self.battle_mines = []
        for item in list(getattr(self, "battle_shapes", [])):
            try:
                item.delete()
            except Exception:
                pass
        for label in list(getattr(self, "battle_labels", [])):
            try:
                label.delete()
            except Exception:
                pass
        self.battle_shapes = []
        self.battle_labels = []
        self.battle_item_boxes = []
        self.battle_coins = []
        self.battle_racers = []
        self.battle_player = None

    def _battle_shape(self, shape):
        self.battle_shapes.append(shape)
        return shape

    def _battle_label(self, label):
        self.battle_labels.append(label)
        return label

    def _build_battle_scene(self):
        self._clear_selection()
        self._clear_race()
        self._clear_battle()
        self.state = self.STATE_BATTLE_COUNTDOWN
        self.keys.clear()
        arena = BATTLE_ARENAS[self.selected_battle_arena]
        self.battle_arena = arena

        self._battle_shape(pyglet.shapes.Rectangle(
            0, 0, EngineGlobals.width, EngineGlobals.height,
            color=arena["bg"], batch=self.batch, group=self.bg_group,
        ))
        self._battle_shape(pyglet.shapes.Rectangle(
            self.BATTLE_MIN_X, self.BATTLE_MIN_Y,
            self.BATTLE_MAX_X - self.BATTLE_MIN_X,
            self.BATTLE_MAX_Y - self.BATTLE_MIN_Y,
            color=arena["floor"], batch=self.batch, group=self.road_group,
        ))

        rail = arena["wall"]
        self._battle_shape(pyglet.shapes.Rectangle(
            self.BATTLE_MIN_X - 8, self.BATTLE_MIN_Y - 8,
            self.BATTLE_MAX_X - self.BATTLE_MIN_X + 16, 8,
            color=rail, batch=self.batch, group=self.scenery_group,
        ))
        self._battle_shape(pyglet.shapes.Rectangle(
            self.BATTLE_MIN_X - 8, self.BATTLE_MAX_Y,
            self.BATTLE_MAX_X - self.BATTLE_MIN_X + 16, 8,
            color=rail, batch=self.batch, group=self.scenery_group,
        ))
        self._battle_shape(pyglet.shapes.Rectangle(
            self.BATTLE_MIN_X - 8, self.BATTLE_MIN_Y, 8,
            self.BATTLE_MAX_Y - self.BATTLE_MIN_Y,
            color=rail, batch=self.batch, group=self.scenery_group,
        ))
        self._battle_shape(pyglet.shapes.Rectangle(
            self.BATTLE_MAX_X, self.BATTLE_MIN_Y, 8,
            self.BATTLE_MAX_Y - self.BATTLE_MIN_Y,
            color=rail, batch=self.batch, group=self.scenery_group,
        ))

        self.battle_walls = []
        for x, y, w, h in arena["walls"]:
            wall_shape = self._battle_shape(pyglet.shapes.Rectangle(
                x, y, w, h, color=arena["wall"],
                batch=self.batch, group=self.scenery_group,
            ))
            self.battle_walls.append((float(x), float(y), float(w), float(h), wall_shape))

        self.battle_hazards = []
        for x, y, radius in arena["hazards"]:
            hazard_shape = self._battle_shape(pyglet.shapes.Circle(
                x, y, radius, color=arena["hazard"],
                batch=self.batch, group=self.scenery_group,
            ))
            hazard_shape.opacity = 220
            self.battle_hazards.append((float(x), float(y), float(radius), hazard_shape))

        self.battle_boosts = []
        for x, y, w, h in arena["boosts"]:
            boost_shape = self._battle_shape(pyglet.shapes.Rectangle(
                x, y, w, h, color=arena["boost"],
                batch=self.batch, group=self.scenery_group,
            ))
            self.battle_boosts.append((float(x), float(y), float(w), float(h), boost_shape))

        self.battle_portals = []
        for index, (a, b) in enumerate(arena["portals"]):
            pair = []
            for x, y in (a, b):
                outer = self._battle_shape(pyglet.shapes.Circle(
                    x, y, 24, color=(136, 88 + index * 25, 206),
                    batch=self.batch, group=self.scenery_group,
                ))
                inner = self._battle_shape(pyglet.shapes.Circle(
                    x, y, 13, color=(41, 31, 61),
                    batch=self.batch, group=self.scenery_group,
                ))
                pair.append((float(x), float(y), outer, inner))
            self.battle_portals.append(tuple(pair))

        self.battle_item_boxes = []
        for x, y in arena["items"]:
            shape = self._battle_shape(pyglet.shapes.Rectangle(
                x - 10, y - 10, 20, 20, color=(211, 89, 220),
                batch=self.batch, group=self.scenery_group,
            ))
            self.battle_item_boxes.append({
                "x": float(x), "y": float(y), "cooldown": 0.0, "shape": shape,
            })

        self.battle_coins = []
        for x, y in arena["coins"]:
            shape = self._battle_shape(pyglet.shapes.Circle(
                x, y, 7, color=(247, 208, 64),
                batch=self.batch, group=self.scenery_group,
            ))
            shape.visible = BATTLE_MODES[self.selected_battle_rule][0] == "COIN HOG"
            self.battle_coins.append({
                "x": float(x), "y": float(y), "cooldown": 0.0, "shape": shape,
            })

        self._spawn_battle_racers()
        self._build_battle_hud()
        self.battle_countdown = 180.0
        rule = BATTLE_MODES[self.selected_battle_rule][0]
        self.battle_time_frames = (
            float(BATTLE_TIME_SECONDS * 60)
            if rule != "BALLOON BRAWL" else float(240 * 60)
        )
        self.battle_event_timer = 0.0
        self.battle_elimination_counter = 8
        self._play_music_file(arena["music"])

    def _new_battle_racer(self, profile, spawn, is_player=False):
        x, y, angle = spawn
        racer = {
            "profile": profile,
            "name": profile["name"],
            "x": float(x), "y": float(y), "angle": float(angle), "speed": 0.0,
            "is_player": bool(is_player),
            "balloons": BATTLE_START_BALLOONS,
            "score": 0, "coins": 0,
            "held_item": None,
            "invuln": 30.0, "shield": 0.0, "star": 0.0,
            "turbo": 0.0, "hop": 0.0, "hit_cooldown": 0.0,
            "hazard_cooldown": 0.0, "portal_cooldown": 0.0,
            "item_use_cooldown": 90.0 + self.battle_rng.random() * 90.0,
            "respawn_timer": 0.0, "eliminated": False,
            "placement": None, "target_angle": float(angle),
        }
        color = (29, 31, 39) if is_player else profile["color"]
        racer["body"] = self._battle_shape(pyglet.shapes.Circle(
            x, y, 14 if is_player else 12, color=color,
            batch=self.batch, group=self.car_group,
        ))
        racer["nose"] = self._battle_shape(pyglet.shapes.Triangle(
            x, y, x, y, x, y, color=(244, 207, 72) if is_player else profile["color"],
            batch=self.batch, group=self.car_group,
        ))
        racer["driver"] = self._battle_shape(pyglet.shapes.Circle(
            x, y, 6, color=profile["color"],
            batch=self.batch, group=self.car_group,
        ))
        racer["label"] = self._battle_label(pyglet.text.Label(
            "", x=x, y=y + 23, anchor_x="center", font_size=6,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        ))
        return racer

    def _spawn_battle_racers(self):
        player_profile = base.CHARACTERS[self.selected_character]
        spawns = self.battle_arena["spawns"]
        self.battle_player = self._new_battle_racer(player_profile, spawns[0], True)
        candidates = [c for c in base.CHARACTERS if c["name"] != player_profile["name"]]
        self.battle_rng.shuffle(candidates)
        rivals = []
        for i, profile in enumerate(candidates[:7]):
            rivals.append(self._new_battle_racer(profile, spawns[i + 1], False))
        self.battle_racers = [self.battle_player] + rivals
        self._update_battle_racer_shapes()

    def _build_battle_hud(self):
        self.battle_title_label = self._battle_label(pyglet.text.Label(
            self.battle_arena["name"].upper(), x=400, y=574, anchor_x="center",
            font_size=14, weight=pyglet.text.Weight.BOLD,
            color=(255, 232, 142, 255), batch=self.batch, group=self.ui_group,
        ))
        self.battle_rule_label = self._battle_label(pyglet.text.Label(
            BATTLE_MODES[self.selected_battle_rule][0], x=18, y=574,
            font_size=11, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        ))
        self.battle_timer_label = self._battle_label(pyglet.text.Label(
            "", x=782, y=574, anchor_x="right", font_size=11,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        ))
        self.battle_status_label = self._battle_label(pyglet.text.Label(
            "", x=18, y=548, font_size=9, color=(211, 224, 241, 255),
            batch=self.batch, group=self.ui_group,
        ))
        self.battle_item_label = self._battle_label(pyglet.text.Label(
            "ITEM —", x=782, y=548, anchor_x="right", font_size=9,
            color=(242, 183, 247, 255), batch=self.batch, group=self.ui_group,
        ))
        self.battle_event_label = self._battle_label(pyglet.text.Label(
            "", x=400, y=548, anchor_x="center", font_size=10,
            weight=pyglet.text.Weight.BOLD, color=(117, 231, 241, 255),
            batch=self.batch, group=self.ui_group,
        ))
        self.battle_help_label = self._battle_label(pyglet.text.Label(
            "↑ accelerate  ↓ brake/reverse  ← → steer  SPACE hop  D item  M music  ESC arenas",
            x=400, y=25, anchor_x="center", font_size=8,
            color=(210, 220, 236, 255), batch=self.batch, group=self.ui_group,
        ))
        self.battle_countdown_label = self._battle_label(pyglet.text.Label(
            "3", x=400, y=310, anchor_x="center", anchor_y="center",
            font_size=70, weight=pyglet.text.Weight.BOLD,
            color=(248, 221, 96, 255), batch=self.batch, group=self.ui_group,
        ))

    @staticmethod
    def _angle_delta(target, current):
        return (target - current + math.pi) % (math.tau) - math.pi

    @staticmethod
    def _distance(a, b):
        return math.hypot(a["x"] - b["x"], a["y"] - b["y"])

    def _battle_physics(self, racer):
        profile = racer["profile"]
        engine = self._class_def()
        if racer["is_player"]:
            speed_scale = engine["speed"]
            accel_scale = engine["accel"]
        else:
            speed_scale = engine["ai"]
            accel_scale = 0.96 + self._difficulty_def()["ai"] * 0.04
        max_speed = (3.7 + profile["speed"] * 0.22) * speed_scale
        boost_speed = max_speed + (1.25 + profile["boost"] * 0.09)
        return {
            "max_speed": max_speed,
            "boost_speed": boost_speed,
            "accel": (0.075 + profile["accel"] * 0.0095) * accel_scale,
            "reverse": 1.8 + profile["accel"] * 0.045,
            "turn": 0.027 + profile["turn"] * 0.0027,
            "grip": profile["grip"],
            "weight": profile["weight"],
            "boost": profile["boost"],
        }

    def _battle_event(self, text, frames=75.0):
        self.battle_event_label.text = text
        self.battle_event_timer = max(self.battle_event_timer, float(frames))

    def _entity_visible(self, racer, visible):
        for key in ("body", "nose", "driver"):
            racer[key].visible = bool(visible)
        racer["label"].visible = bool(visible)

    def _update_battle_racer_shapes(self):
        for racer in self.battle_racers:
            visible = not racer["eliminated"] and racer["respawn_timer"] <= 0
            self._entity_visible(racer, visible)
            if not visible:
                continue
            x, y, angle = racer["x"], racer["y"], racer["angle"]
            radius = 14.0 if racer["is_player"] else 12.0
            racer["body"].position = (x, y)
            racer["driver"].position = (x, y)
            tip = (x + math.cos(angle) * (radius + 9), y + math.sin(angle) * (radius + 9))
            left = (
                x + math.cos(angle + 2.45) * radius,
                y + math.sin(angle + 2.45) * radius,
            )
            right = (
                x + math.cos(angle - 2.45) * radius,
                y + math.sin(angle - 2.45) * radius,
            )
            nose = racer["nose"]
            nose.x, nose.y = tip
            nose.x2, nose.y2 = left
            nose.x3, nose.y3 = right
            racer["label"].x = x
            racer["label"].y = y + radius + 12
            racer["label"].text = "{} {}".format(
                racer["name"].upper(),
                "●" * max(0, racer["balloons"]),
            )

    def _move_racer(self, racer, throttle, steer, dt):
        if racer["eliminated"] or racer["respawn_timer"] > 0:
            return
        physics = self._battle_physics(racer)
        if throttle > 0:
            racer["speed"] += physics["accel"] * float(dt)
        elif throttle < 0:
            racer["speed"] -= physics["accel"] * 0.75 * float(dt)
        else:
            racer["speed"] *= self.battle_arena["friction"] ** float(dt)
        if racer["turbo"] > 0:
            racer["turbo"] = max(0.0, racer["turbo"] - float(dt))
            racer["speed"] += 0.025 * float(dt)
            top = physics["boost_speed"]
        else:
            top = physics["max_speed"]
        racer["speed"] = max(-physics["reverse"], min(top, racer["speed"]))
        if abs(racer["speed"]) > 0.12:
            direction = 1.0 if racer["speed"] >= 0 else -0.65
            racer["angle"] += steer * physics["turn"] * direction * float(dt)
        racer["x"] += math.cos(racer["angle"]) * racer["speed"] * float(dt)
        racer["y"] += math.sin(racer["angle"]) * racer["speed"] * float(dt)

        for timer in (
            "invuln", "shield", "star", "hop", "hit_cooldown",
            "hazard_cooldown", "portal_cooldown", "item_use_cooldown",
        ):
            racer[timer] = max(0.0, racer[timer] - float(dt))

        self._battle_boundaries(racer)
        self._battle_wall_collisions(racer)
        self._battle_track_features(racer)

    def _battle_boundaries(self, racer):
        bounced = False
        if racer["x"] < self.BATTLE_MIN_X + self.BATTLE_RADIUS:
            racer["x"] = self.BATTLE_MIN_X + self.BATTLE_RADIUS
            racer["angle"] = math.pi - racer["angle"]
            bounced = True
        elif racer["x"] > self.BATTLE_MAX_X - self.BATTLE_RADIUS:
            racer["x"] = self.BATTLE_MAX_X - self.BATTLE_RADIUS
            racer["angle"] = math.pi - racer["angle"]
            bounced = True
        if racer["y"] < self.BATTLE_MIN_Y + self.BATTLE_RADIUS:
            racer["y"] = self.BATTLE_MIN_Y + self.BATTLE_RADIUS
            racer["angle"] = -racer["angle"]
            bounced = True
        elif racer["y"] > self.BATTLE_MAX_Y - self.BATTLE_RADIUS:
            racer["y"] = self.BATTLE_MAX_Y - self.BATTLE_RADIUS
            racer["angle"] = -racer["angle"]
            bounced = True
        if bounced:
            racer["speed"] *= 0.62

    def _battle_wall_collisions(self, racer):
        r = self.BATTLE_RADIUS
        for x, y, w, h, _shape in self.battle_walls:
            if not (x - r < racer["x"] < x + w + r and y - r < racer["y"] < y + h + r):
                continue
            distances = (
                (abs(racer["x"] - (x - r)), "left"),
                (abs(racer["x"] - (x + w + r)), "right"),
                (abs(racer["y"] - (y - r)), "bottom"),
                (abs(racer["y"] - (y + h + r)), "top"),
            )
            side = min(distances, key=lambda pair: pair[0])[1]
            if side == "left":
                racer["x"] = x - r
                racer["angle"] = math.pi - racer["angle"]
            elif side == "right":
                racer["x"] = x + w + r
                racer["angle"] = math.pi - racer["angle"]
            elif side == "bottom":
                racer["y"] = y - r
                racer["angle"] = -racer["angle"]
            else:
                racer["y"] = y + h + r
                racer["angle"] = -racer["angle"]
            racer["speed"] *= 0.58

    @staticmethod
    def _point_in_rect(px, py, rect):
        x, y, w, h = rect[:4]
        return x <= px <= x + w and y <= py <= y + h

    def _battle_track_features(self, racer):
        if racer["eliminated"] or racer["respawn_timer"] > 0:
            return
        for x, y, radius, _shape in self.battle_hazards:
            if math.hypot(racer["x"] - x, racer["y"] - y) < radius + 8:
                if racer["hazard_cooldown"] <= 0 and racer["hop"] <= 0:
                    racer["hazard_cooldown"] = 105.0
                    self._battle_hit(racer, None, self.battle_arena["hazard_name"])
                break
        for boost in self.battle_boosts:
            if self._point_in_rect(racer["x"], racer["y"], boost):
                physics = self._battle_physics(racer)
                racer["turbo"] = max(racer["turbo"], 42.0 + physics["boost"] * 2.0)
                racer["speed"] = max(racer["speed"], physics["max_speed"] + 0.65)
                break
        if racer["portal_cooldown"] <= 0:
            for pair in self.battle_portals:
                a, b = pair
                if math.hypot(racer["x"] - a[0], racer["y"] - a[1]) < 23:
                    racer["x"], racer["y"] = b[0], b[1]
                    racer["portal_cooldown"] = 55.0
                    break
                if math.hypot(racer["x"] - b[0], racer["y"] - b[1]) < 23:
                    racer["x"], racer["y"] = a[0], a[1]
                    racer["portal_cooldown"] = 55.0
                    break
        for box in self.battle_item_boxes:
            if box["cooldown"] <= 0 and racer["held_item"] is None:
                if math.hypot(racer["x"] - box["x"], racer["y"] - box["y"]) < 24:
                    racer["held_item"] = self._battle_random_item(racer)
                    box["cooldown"] = 240.0
                    box["shape"].visible = False
                    if racer["is_player"]:
                        self._battle_event("ITEM: {}".format(racer["held_item"]), 50.0)
                    break
        if BATTLE_MODES[self.selected_battle_rule][0] == "COIN HOG":
            for coin in self.battle_coins:
                if coin["cooldown"] <= 0 and math.hypot(
                    racer["x"] - coin["x"], racer["y"] - coin["y"]
                ) < 20:
                    racer["coins"] += 1
                    coin["cooldown"] = 180.0
                    coin["shape"].visible = False
                    if racer["is_player"]:
                        self._battle_event("OINK! +1 COIN", 28.0)
                    break

    def _battle_random_item(self, racer):
        weak = racer["balloons"] <= 1
        bag = list(BATTLE_ITEMS)
        if weak:
            bag += ["STAR", "BAT SHIELD", "PIG BOMB", "HOG ROCKET"]
        if racer["is_player"] and BATTLE_MODES[self.selected_battle_rule][0] == "COIN HOG":
            bag += ["TURBO", "HOG ROCKET"]
        return self.battle_rng.choice(bag)

    def _battle_hit(self, target, attacker, message="HIT!"):
        if target["eliminated"] or target["respawn_timer"] > 0:
            return False
        if target["invuln"] > 0 or target["hop"] > 0 or target["star"] > 0:
            return False
        if target["shield"] > 0:
            target["shield"] = 0.0
            target["invuln"] = 24.0
            if target["is_player"]:
                self._battle_event("BAT SHIELD BLOCKED IT!", 45.0)
            return False
        target["balloons"] -= 1
        target["invuln"] = 82.0
        target["hit_cooldown"] = 42.0
        target["speed"] *= 0.35

        if attacker is not None and attacker is not target:
            attacker["score"] += 1
        rule = BATTLE_MODES[self.selected_battle_rule][0]
        if rule == "COIN HOG" and target["coins"] > 0:
            stolen = min(2, target["coins"])
            target["coins"] -= stolen
            if attacker is not None and attacker is not target:
                attacker["coins"] += stolen

        if target["is_player"]:
            self._battle_event("{} — BALLOON LOST!".format(message), 70.0)

        if target["balloons"] <= 0:
            self._battle_knockout(target, attacker)
        return True

    def _battle_knockout(self, target, attacker):
        rule = BATTLE_MODES[self.selected_battle_rule][0]
        if attacker is not None and attacker is not target:
            attacker["score"] += 2
        if rule == "BALLOON BRAWL":
            target["eliminated"] = True
            active_after = sum(
                1 for racer in self.battle_racers
                if racer is not target and not racer["eliminated"]
            )
            target["placement"] = active_after + 1
            self._entity_visible(target, False)
            if target["is_player"]:
                self._battle_event("HOGGED OUT!", 80.0)
        else:
            target["respawn_timer"] = 95.0
            target["balloons"] = BATTLE_START_BALLOONS
            target["held_item"] = None
            self._entity_visible(target, False)
            if target["is_player"]:
                self._battle_event("KNOCKED OUT — RESPAWNING!", 80.0)

    def _respawn_racer(self, racer):
        index = self.battle_racers.index(racer) % len(self.battle_arena["spawns"])
        x, y, angle = self.battle_arena["spawns"][index]
        racer["x"], racer["y"], racer["angle"] = float(x), float(y), float(angle)
        racer["speed"] = 0.0
        racer["respawn_timer"] = 0.0
        racer["invuln"] = 120.0
        racer["shield"] = 0.0
        racer["star"] = 0.0
        racer["hop"] = 0.0
        self._entity_visible(racer, True)

    def _battle_target(self, racer):
        candidates = [
            other for other in self.battle_racers
            if other is not racer and not other["eliminated"] and other["respawn_timer"] <= 0
        ]
        return min(candidates, key=lambda other: self._distance(racer, other)) if candidates else None

    def _fire_hog_rocket(self, racer):
        shape = pyglet.shapes.Circle(
            racer["x"], racer["y"], 6, color=(238, 105, 72),
            batch=self.batch, group=self.car_group,
        )
        speed = 8.2
        self.battle_projectiles.append({
            "x": racer["x"], "y": racer["y"],
            "vx": math.cos(racer["angle"]) * speed,
            "vy": math.sin(racer["angle"]) * speed,
            "owner": racer, "life": 150.0, "shape": shape,
        })

    def _drop_ketchup_mine(self, racer):
        x = racer["x"] - math.cos(racer["angle"]) * 25
        y = racer["y"] - math.sin(racer["angle"]) * 25
        shape = pyglet.shapes.Circle(
            x, y, 11, color=(185, 34, 40),
            batch=self.batch, group=self.scenery_group,
        )
        self.battle_mines.append({
            "x": x, "y": y, "owner": racer, "arm": 28.0,
            "life": 900.0, "shape": shape,
        })

    def _use_battle_item(self, racer):
        item = racer["held_item"]
        if not item or racer["eliminated"] or racer["respawn_timer"] > 0:
            return
        racer["held_item"] = None
        racer["item_use_cooldown"] = 90.0
        physics = self._battle_physics(racer)
        if item == "HOG ROCKET":
            self._fire_hog_rocket(racer)
        elif item == "KETCHUP MINE":
            self._drop_ketchup_mine(racer)
        elif item == "TURBO":
            racer["turbo"] = max(racer["turbo"], 120.0)
            racer["speed"] = max(racer["speed"], physics["max_speed"] + 1.1)
        elif item == "BAT SHIELD":
            racer["shield"] = 420.0
        elif item == "PIG BOMB":
            hits = 0
            for target in self.battle_racers:
                if target is racer or target["eliminated"] or target["respawn_timer"] > 0:
                    continue
                if self._distance(racer, target) < 132.0:
                    if self._battle_hit(target, racer, "PIG BOMB"):
                        hits += 1
            if racer["is_player"]:
                self._battle_event("PIG BOMB! {} HIT".format(hits), 55.0)
        elif item == "LIGHTNING":
            for target in self.battle_racers:
                if target is racer or target["eliminated"] or target["respawn_timer"] > 0:
                    continue
                target["speed"] *= 0.42
                target["hit_cooldown"] = max(target["hit_cooldown"], 70.0)
                target["invuln"] = max(target["invuln"], 10.0)
            if racer["is_player"]:
                self._battle_event("LIGHTNING! EVERYBODY SLOWS DOWN", 60.0)
        elif item == "STAR":
            racer["star"] = 260.0
            racer["invuln"] = 260.0
            racer["turbo"] = 220.0
            racer["speed"] = max(racer["speed"], physics["max_speed"] + 1.2)
        elif item == "FEATHER":
            racer["hop"] = 72.0
            racer["invuln"] = max(racer["invuln"], 72.0)
            racer["speed"] = max(racer["speed"], physics["max_speed"] * 0.88)
        if racer["is_player"]:
            self._battle_event("{}!".format(item), 45.0)

    def _update_battle_projectiles(self, dt):
        alive = []
        for projectile in self.battle_projectiles:
            projectile["life"] -= float(dt)
            projectile["x"] += projectile["vx"] * float(dt)
            projectile["y"] += projectile["vy"] * float(dt)
            projectile["shape"].position = (projectile["x"], projectile["y"])
            dead = projectile["life"] <= 0
            if not dead and not (
                self.BATTLE_MIN_X < projectile["x"] < self.BATTLE_MAX_X
                and self.BATTLE_MIN_Y < projectile["y"] < self.BATTLE_MAX_Y
            ):
                dead = True
            if not dead:
                for x, y, w, h, _shape in self.battle_walls:
                    if x <= projectile["x"] <= x + w and y <= projectile["y"] <= y + h:
                        dead = True
                        break
            if not dead:
                for target in self.battle_racers:
                    if target is projectile["owner"] or target["eliminated"] or target["respawn_timer"] > 0:
                        continue
                    if math.hypot(
                        projectile["x"] - target["x"], projectile["y"] - target["y"]
                    ) < self.BATTLE_RADIUS + 7:
                        self._battle_hit(target, projectile["owner"], "HOG ROCKET")
                        dead = True
                        break
            if dead:
                try:
                    projectile["shape"].delete()
                except Exception:
                    pass
            else:
                alive.append(projectile)
        self.battle_projectiles = alive

    def _update_battle_mines(self, dt):
        alive = []
        for mine in self.battle_mines:
            mine["arm"] = max(0.0, mine["arm"] - float(dt))
            mine["life"] -= float(dt)
            dead = mine["life"] <= 0
            if not dead and mine["arm"] <= 0:
                for target in self.battle_racers:
                    if target is mine["owner"] or target["eliminated"] or target["respawn_timer"] > 0:
                        continue
                    if math.hypot(mine["x"] - target["x"], mine["y"] - target["y"]) < 25:
                        self._battle_hit(target, mine["owner"], "KETCHUP MINE")
                        dead = True
                        break
            if dead:
                try:
                    mine["shape"].delete()
                except Exception:
                    pass
            else:
                alive.append(mine)
        self.battle_mines = alive

    def _update_battle_player(self, dt):
        racer = self.battle_player
        if racer is None or racer["eliminated"]:
            return
        if racer["respawn_timer"] > 0:
            racer["respawn_timer"] -= float(dt)
            if racer["respawn_timer"] <= 0:
                self._respawn_racer(racer)
            return
        throttle = 0
        if pyglet.window.key.UP in self.keys:
            throttle += 1
        if pyglet.window.key.DOWN in self.keys:
            throttle -= 1
        steer = 0
        if pyglet.window.key.LEFT in self.keys:
            steer += 1
        if pyglet.window.key.RIGHT in self.keys:
            steer -= 1
        self._move_racer(racer, throttle, steer, dt)

    def _update_battle_ai(self, dt):
        aggression = self._difficulty_def()["item_aggression"]
        for racer in self.battle_racers[1:]:
            if racer["eliminated"]:
                continue
            if racer["respawn_timer"] > 0:
                racer["respawn_timer"] -= float(dt)
                if racer["respawn_timer"] <= 0:
                    self._respawn_racer(racer)
                continue
            target = self._battle_target(racer)
            if target is None:
                self._move_racer(racer, 0, 0, dt)
                continue
            desired = math.atan2(target["y"] - racer["y"], target["x"] - racer["x"])
            delta = self._angle_delta(desired, racer["angle"])
            steer = max(-1.0, min(1.0, delta * 2.3))
            distance = self._distance(racer, target)
            throttle = 1.0 if distance > 70 else (0.45 if distance > 38 else -0.25)
            steer += math.sin((self.battle_time_frames + self.battle_racers.index(racer) * 37) * 0.012) * 0.18
            steer = max(-1.0, min(1.0, steer))
            self._move_racer(racer, throttle, steer, dt)
            if racer["held_item"] and racer["item_use_cooldown"] <= 0:
                use = False
                if racer["held_item"] in ("HOG ROCKET", "PIG BOMB", "KETCHUP MINE"):
                    use = distance < (260.0 if racer["held_item"] == "HOG ROCKET" else 135.0)
                elif racer["held_item"] in ("TURBO", "STAR"):
                    use = distance > 150.0 or racer["balloons"] <= 1
                elif racer["held_item"] in ("BAT SHIELD", "FEATHER"):
                    use = racer["balloons"] <= 2 or distance < 110.0
                elif racer["held_item"] == "LIGHTNING":
                    use = self.battle_rng.random() < 0.012 * aggression * float(dt)
                if use:
                    self._use_battle_item(racer)

    def _battle_racer_collisions(self):
        active = [
            r for r in self.battle_racers
            if not r["eliminated"] and r["respawn_timer"] <= 0
        ]
        for i, first in enumerate(active):
            for second in active[i + 1:]:
                dx = second["x"] - first["x"]
                dy = second["y"] - first["y"]
                dist = math.hypot(dx, dy)
                if dist <= 0 or dist >= self.BATTLE_RADIUS * 2:
                    continue
                nx, ny = dx / dist, dy / dist
                overlap = self.BATTLE_RADIUS * 2 - dist
                first["x"] -= nx * overlap * 0.5
                first["y"] -= ny * overlap * 0.5
                second["x"] += nx * overlap * 0.5
                second["y"] += ny * overlap * 0.5
                w1 = self._battle_physics(first)["weight"]
                w2 = self._battle_physics(second)["weight"]
                first["speed"] *= max(0.62, 0.90 - max(0, w2 - w1) * 0.018)
                second["speed"] *= max(0.62, 0.90 - max(0, w1 - w2) * 0.018)
                if first["star"] > 0 and second["hit_cooldown"] <= 0:
                    self._battle_hit(second, first, "STAR RAM")
                elif second["star"] > 0 and first["hit_cooldown"] <= 0:
                    self._battle_hit(first, second, "STAR RAM")

    def _tick_battle_pickups(self, dt):
        for box in self.battle_item_boxes:
            if box["cooldown"] > 0:
                box["cooldown"] = max(0.0, box["cooldown"] - float(dt))
                if box["cooldown"] <= 0:
                    box["shape"].visible = True
        coin_mode = BATTLE_MODES[self.selected_battle_rule][0] == "COIN HOG"
        for coin in self.battle_coins:
            coin["shape"].visible = coin_mode and coin["cooldown"] <= 0
            if coin["cooldown"] > 0:
                coin["cooldown"] = max(0.0, coin["cooldown"] - float(dt))

    def _battle_end_check(self):
        rule = BATTLE_MODES[self.selected_battle_rule][0]
        if rule == "BALLOON BRAWL":
            active = [r for r in self.battle_racers if not r["eliminated"]]
            if self.battle_player["eliminated"] or len(active) <= 1 or self.battle_time_frames <= 0:
                self._finish_battle()
                return True
        elif self.battle_time_frames <= 0:
            self._finish_battle()
            return True
        return False

    def _battle_sort_results(self):
        rule = BATTLE_MODES[self.selected_battle_rule][0]
        if rule == "COIN HOG":
            return sorted(
                self.battle_racers,
                key=lambda r: (-r["coins"], -r["score"], r["name"]),
            )
        if rule == "HOG SCORE":
            return sorted(
                self.battle_racers,
                key=lambda r: (-r["score"], -r["balloons"], r["name"]),
            )
        return sorted(
            self.battle_racers,
            key=lambda r: (
                r["eliminated"],
                -(r["balloons"] if not r["eliminated"] else 0),
                r["placement"] if r["placement"] is not None else 99,
                -r["score"],
            ),
        )

    def _finish_battle(self):
        results = self._battle_sort_results()
        player_name = self.battle_player["name"]
        self.battle_finish_place = next(
            (i + 1 for i, racer in enumerate(results) if racer["name"] == player_name),
            8,
        )
        snapshot = [
            {
                "name": racer["name"], "balloons": racer["balloons"],
                "score": racer["score"], "coins": racer["coins"],
                "is_player": racer["is_player"],
            }
            for racer in results
        ]
        self.battle_last_results = snapshot
        self._clear_battle()
        self._clear_selection()
        self.state = self.STATE_BATTLE_FINISH
        rule = BATTLE_MODES[self.selected_battle_rule][0]
        self._selection_header(
            "HOGGIN OUT RESULTS",
            "{} • {} • {} PLACE".format(
                rule, BATTLE_ARENAS[self.selected_battle_arena]["name"].upper(),
                self.battle_finish_place,
            ),
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
            metric = (
                "{} COINS".format(result["coins"]) if rule == "COIN HOG"
                else "{} PTS".format(result["score"]) if rule == "HOG SCORE"
                else "{} BALLOONS • {} HITS".format(result["balloons"], result["score"])
            )
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

    def _update_battle_hud(self):
        player = self.battle_player
        if player is None:
            return
        rule = BATTLE_MODES[self.selected_battle_rule][0]
        seconds = max(0, int(math.ceil(self.battle_time_frames / 60.0)))
        minutes, secs = divmod(seconds, 60)
        self.battle_timer_label.text = "{:d}:{:02d}".format(minutes, secs)
        if rule == "COIN HOG":
            self.battle_status_label.text = "COINS {} • HITS {} • BALLOONS {}".format(
                player["coins"], player["score"], player["balloons"]
            )
        elif rule == "HOG SCORE":
            self.battle_status_label.text = "SCORE {} • BALLOONS {}".format(
                player["score"], player["balloons"]
            )
        else:
            active = sum(1 for r in self.battle_racers if not r["eliminated"])
            self.battle_status_label.text = "BALLOONS {} • {} RACERS LEFT".format(
                player["balloons"], active
            )
        self.battle_item_label.text = "ITEM {}".format(player["held_item"] or "—")
        if self.battle_event_timer > 0:
            self.battle_event_timer -= 1.0
            if self.battle_event_timer <= 0:
                self.battle_event_label.text = ""

    def _start_battle(self):
        self._build_battle_scene()

    def start(self):
        self.selected_battle_rule = 0
        self.selected_battle_arena = 0
        super().start()

    def stop(self):
        self._clear_battle()
        super().stop()

    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        enter = symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN)

        if self.state == self.STATE_CHARACTER and self.play_mode == "HOGGIN OUT" and enter:
            self._build_battle_rules()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_BATTLE_RULES:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_character_select()
            elif symbol in (pyglet.window.key.UP, pyglet.window.key.LEFT):
                self.selected_battle_rule = (self.selected_battle_rule - 1) % len(BATTLE_MODES)
                self._refresh_battle_rules()
            elif symbol in (pyglet.window.key.DOWN, pyglet.window.key.RIGHT):
                self.selected_battle_rule = (self.selected_battle_rule + 1) % len(BATTLE_MODES)
                self._refresh_battle_rules()
            elif enter:
                self._build_battle_arena_select()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_BATTLE_ARENA:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_battle_rules()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_battle_arena = (self.selected_battle_arena - 1) % len(BATTLE_ARENAS)
                self._refresh_battle_arena_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_battle_arena = (self.selected_battle_arena + 1) % len(BATTLE_ARENAS)
                self._refresh_battle_arena_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_battle_arena = (self.selected_battle_arena - 4) % len(BATTLE_ARENAS)
                self._refresh_battle_arena_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_battle_arena = (self.selected_battle_arena + 4) % len(BATTLE_ARENAS)
                self._refresh_battle_arena_select()
            elif enter:
                self._start_battle()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_BATTLE_FINISH:
            if enter:
                self._start_battle()
            elif symbol == pyglet.window.key.ESCAPE:
                self._build_battle_arena_select()
            return pyglet.event.EVENT_HANDLED

        if self.state in (self.STATE_BATTLE_COUNTDOWN, self.STATE_BATTLE):
            if symbol == pyglet.window.key.ESCAPE:
                self.keys.clear()
                self._build_battle_arena_select()
                return pyglet.event.EVENT_HANDLED
            if symbol == pyglet.window.key.M:
                self._next_music()
                return pyglet.event.EVENT_HANDLED
            if self.state == self.STATE_BATTLE:
                if symbol == pyglet.window.key.D:
                    self._use_battle_item(self.battle_player)
                    return pyglet.event.EVENT_HANDLED
                if symbol == pyglet.window.key.SPACE and self.battle_player is not None:
                    if self.battle_player["hop"] <= 0 and not self.battle_player["eliminated"]:
                        self.battle_player["hop"] = 38.0
                        self.battle_player["invuln"] = max(self.battle_player["invuln"], 38.0)
                        self.battle_player["speed"] *= 1.05
                        self._battle_event("HOG HOP!", 25.0)
                    return pyglet.event.EVENT_HANDLED
            self.keys.add(symbol)
            return pyglet.event.EVENT_HANDLED

        return super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        if self.state in (self.STATE_BATTLE_COUNTDOWN, self.STATE_BATTLE):
            self.keys.discard(symbol)
            return pyglet.event.EVENT_HANDLED
        return super().on_key_release(symbol, modifiers)

    def update(self, dt):
        if not self.active:
            return
        dt = float(dt)
        if self.state == self.STATE_BATTLE_COUNTDOWN:
            self.battle_countdown -= dt
            if self.battle_countdown > 120:
                self.battle_countdown_label.text = "3"
            elif self.battle_countdown > 60:
                self.battle_countdown_label.text = "2"
            elif self.battle_countdown > 0:
                self.battle_countdown_label.text = "1"
            else:
                self.state = self.STATE_BATTLE
                self.battle_countdown_label.text = "HOG OUT!"
                self.battle_event_timer = 35.0
            self._update_battle_racer_shapes()
            return

        if self.state == self.STATE_BATTLE:
            if self.battle_countdown_label.visible:
                self.battle_countdown_label.visible = False
            self.battle_time_frames = max(0.0, self.battle_time_frames - dt)
            self._update_battle_player(dt)
            self._update_battle_ai(dt)
            self._battle_racer_collisions()
            self._update_battle_projectiles(dt)
            self._update_battle_mines(dt)
            self._tick_battle_pickups(dt)
            self._update_battle_racer_shapes()
            self._update_battle_hud()
            if self._battle_end_check():
                return
            return

        if self.state in (
            self.STATE_BATTLE_RULES, self.STATE_BATTLE_ARENA, self.STATE_BATTLE_FINISH
        ):
            return

        super().update(dt)
