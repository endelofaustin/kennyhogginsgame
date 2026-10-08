"""Pseudo-3D SNES-era racing mode for Kenny Hoggins."""

import math
import random

import pyglet

from engineglobals import EngineGlobals


CHARACTERS = (
    {"name": "Kenny", "color": (229, 154, 158), "art": None,
     "speed": 10, "accel": 10, "turn": 10, "weight": 10, "grip": 10, "boost": 10},
    {"name": "Theo", "color": (213, 164, 114), "art": None,
     "speed": 8, "accel": 6, "turn": 5, "weight": 10, "grip": 7, "boost": 7},
    {"name": "Lucinda", "color": (175, 116, 189), "art": "generated/lucinda.png",
     "speed": 7, "accel": 9, "turn": 9, "weight": 4, "grip": 10, "boost": 8},
    {"name": "Jackie Flan", "color": (215, 154, 91), "art": "generated/jackie_flan.png",
     "speed": 9, "accel": 7, "turn": 10, "weight": 5, "grip": 8, "boost": 7},
    {"name": "Levod Burtim", "color": (112, 167, 201), "art": "generated/levod_burtim.png",
     "speed": 10, "accel": 6, "turn": 6, "weight": 8, "grip": 7, "boost": 9},
    {"name": "Pippi", "color": (228, 130, 173), "art": "generated/pippi.png",
     "speed": 7, "accel": 10, "turn": 8, "weight": 3, "grip": 9, "boost": 10},
    {"name": "Vesuvius", "color": (116, 80, 69), "art": "generated/vesuvius.png",
     "speed": 9, "accel": 5, "turn": 4, "weight": 10, "grip": 6, "boost": 8},
    {"name": "Charleston", "color": (104, 177, 142), "art": "charleston.png",
     "speed": 8, "accel": 8, "turn": 7, "weight": 6, "grip": 8, "boost": 8},
    {"name": "Doggy", "color": (188, 141, 94), "art": "doggy.png",
     "speed": 6, "accel": 10, "turn": 10, "weight": 2, "grip": 9, "boost": 8},
    {"name": "Mr. Spud", "color": (185, 139, 83), "art": "mrspudl.png",
     "speed": 7, "accel": 7, "turn": 6, "weight": 9, "grip": 8, "boost": 6},
)


def _track(name, tagline, pattern, *,
           sky=(36, 45, 75), ground=(37, 74, 53),
           road=(74, 76, 82), edge_a=(235, 226, 201), edge_b=(194, 56, 56),
           boost=(), oil=(), ramp=(), mud=(), scenery=(26, 48, 39),
           max_speed=1.0, grip=1.0):
    return {
        "name": name,
        "tagline": tagline,
        "pattern": tuple(pattern),
        "sky": sky,
        "ground": ground,
        "road": road,
        "edge_a": edge_a,
        "edge_b": edge_b,
        "boost": set(boost),
        "oil": set(oil),
        "ramp": set(ramp),
        "mud": set(mud),
        "scenery": scenery,
        "max_speed": float(max_speed),
        "grip": float(grip),
    }


TRACKS = (
    _track(
        "Midnight Bat Circuit",
        "Fast city sweepers, oil, ramps, and long boost lanes.",
        ((18, 0.00, 0.00), (20, 0.015, 0.00), (18, 0.032, 0.010),
         (16, 0.000, 0.018), (22, -0.026, -0.012), (16, -0.045, 0.000),
         (18, 0.000, -0.016), (20, 0.024, 0.008), (14, 0.048, 0.000),
         (20, -0.020, 0.010), (16, 0.000, -0.012), (20, -0.035, 0.000),
         (20, 0.000, 0.000)),
        boost=(11, 52, 103, 151, 216), oil=(38, 92, 187), ramp=(74, 171),
    ),
    _track(
        "Lucinda Farm Moonway",
        "Rolling farm hills with sticky mud and generous trick ramps.",
        ((20, 0.000, 0.010), (18, 0.020, 0.018), (16, -0.030, 0.015),
         (22, 0.000, -0.018), (18, 0.040, 0.005), (18, -0.048, 0.000),
         (24, 0.014, 0.012), (18, 0.000, -0.010), (22, -0.025, 0.000),
         (20, 0.034, 0.000), (18, 0.000, 0.006)),
        sky=(65, 73, 104), ground=(83, 124, 64), road=(91, 79, 67),
        edge_a=(235, 214, 159), edge_b=(184, 118, 70),
        boost=(28, 85, 164), oil=(132,), mud=(47, 48, 109, 110, 190, 191),
        ramp=(67, 145, 205), scenery=(63, 95, 48), grip=0.96,
    ),
    _track(
        "Van Down by the River",
        "Wide riverside speedway with dock jumps and slick corners.",
        ((16, 0.000, 0.000), (22, 0.028, 0.004), (20, 0.000, 0.010),
         (18, -0.035, 0.000), (20, -0.018, -0.010), (24, 0.026, 0.000),
         (18, 0.045, 0.006), (22, 0.000, -0.012), (20, -0.038, 0.000),
         (24, 0.010, 0.000), (16, 0.000, 0.006)),
        sky=(64, 86, 119), ground=(49, 111, 104), road=(72, 83, 88),
        edge_a=(214, 220, 204), edge_b=(73, 136, 168),
        boost=(15, 61, 126, 198), oil=(82, 159, 205), ramp=(104, 181),
        scenery=(40, 84, 77), max_speed=1.025,
    ),
    _track(
        "Dojo Neon Pass",
        "Technical hairpins. Drift timing matters more than raw speed.",
        ((14, 0.000, 0.000), (14, 0.052, 0.000), (12, -0.058, 0.006),
         (14, 0.060, 0.000), (12, -0.064, -0.006), (16, 0.030, 0.000),
         (12, 0.000, 0.012), (14, -0.055, 0.000), (12, 0.062, 0.000),
         (16, -0.034, -0.008), (18, 0.000, 0.000)),
        sky=(46, 29, 68), ground=(97, 48, 62), road=(68, 63, 75),
        edge_a=(231, 87, 143), edge_b=(80, 202, 220),
        boost=(34, 91, 142), oil=(56, 118), ramp=(164,),
        scenery=(71, 39, 79), max_speed=0.96, grip=1.05,
    ),
    _track(
        "Rainbomb Starway",
        "Huge crests and airborne tricks on a low-gravity night road.",
        ((18, 0.000, 0.020), (20, 0.022, 0.024), (18, -0.030, -0.030),
         (20, 0.000, 0.032), (18, 0.038, -0.024), (20, -0.042, 0.018),
         (18, 0.000, 0.028), (20, 0.030, -0.035), (18, -0.028, 0.020),
         (24, 0.000, -0.012)),
        sky=(20, 21, 58), ground=(34, 38, 68), road=(61, 64, 96),
        edge_a=(129, 111, 231), edge_b=(62, 205, 232),
        boost=(21, 74, 128, 182), oil=(99,), ramp=(43, 112, 165, 211),
        scenery=(39, 42, 82), max_speed=1.03,
    ),
    _track(
        "Vesuvius Fire Road",
        "Fast volcanic straights with punishing ash and oil zones.",
        ((20, 0.000, 0.006), (24, 0.018, 0.010), (16, 0.046, 0.000),
         (20, -0.050, -0.010), (24, 0.000, 0.000), (18, -0.035, 0.012),
         (22, 0.042, -0.008), (24, 0.000, 0.000), (18, -0.025, 0.006),
         (22, 0.030, 0.000)),
        sky=(79, 42, 39), ground=(106, 54, 36), road=(70, 65, 64),
        edge_a=(244, 158, 67), edge_b=(187, 48, 34),
        boost=(18, 64, 121, 176, 214), oil=(47, 101, 156, 201),
        mud=(78, 79, 180, 181), ramp=(143,), scenery=(87, 44, 33),
        max_speed=1.04, grip=0.94,
    ),
    _track(
        "Theo Desert Loop",
        "Long Nevada drifts, dusty shoulders, and high-speed launch ramps.",
        ((24, 0.000, 0.000), (22, 0.020, 0.006), (20, 0.032, 0.000),
         (24, -0.028, -0.006), (22, 0.000, 0.008), (20, -0.038, 0.000),
         (26, 0.022, 0.000), (20, 0.044, 0.006), (24, -0.025, 0.000),
         (28, 0.000, -0.004)),
        sky=(103, 85, 91), ground=(171, 132, 77), road=(99, 83, 70),
        edge_a=(235, 207, 146), edge_b=(174, 94, 56),
        boost=(25, 83, 149, 214), oil=(121,), mud=(48, 49, 184, 185, 232, 233),
        ramp=(106, 199), scenery=(141, 105, 66), max_speed=1.02, grip=0.93,
    ),
    _track(
        "Ketchup Causeway",
        "Sticky red hazards, tight S-curves, and a wild final boost run.",
        ((18, 0.000, 0.000), (18, 0.040, 0.004), (16, -0.046, 0.000),
         (18, 0.052, 0.008), (16, -0.050, -0.008), (20, 0.000, 0.000),
         (18, -0.036, 0.006), (18, 0.044, 0.000), (20, -0.025, -0.004),
         (26, 0.000, 0.000)),
        sky=(91, 52, 63), ground=(137, 55, 48), road=(81, 68, 69),
        edge_a=(248, 192, 161), edge_b=(176, 44, 42),
        boost=(27, 86, 147, 176), oil=(66, 134), mud=(42, 43, 112, 113, 156, 157),
        ramp=(101,), scenery=(116, 48, 45), grip=0.95,
    ),
)


class Rival:
    def __init__(self, lane, distance, speed, color, name, weight=5):
        self.lane = float(lane)
        self.distance = float(distance)
        self.base_speed = float(speed)
        self.speed = float(speed)
        self.color = color
        self.name = name
        self.weight = int(weight)
        self.wobble = random.uniform(0.0, math.tau)
        self.finished_laps = 0
        self.boost_timer = 0.0
        self.hit_timer = 0.0


class Mode7Racing:
    """Reusable pseudo-3D racer with character and track selection."""

    STATE_CHARACTER = "character"
    STATE_TRACK = "track"
    STATE_COUNTDOWN = "countdown"
    STATE_RACE = "race"
    STATE_FINISH = "finish"

    SEGMENT_LENGTH = 42.0
    DRAW_SEGMENTS = 56
    TOTAL_LAPS = 3

    def __init__(self, on_exit_to_menu=None):
        self.on_exit_to_menu = on_exit_to_menu
        self.active = False
        self.state = self.STATE_CHARACTER
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(0)
        self.road_group = pyglet.graphics.Group(1)
        self.scenery_group = pyglet.graphics.Group(2)
        self.car_group = pyglet.graphics.Group(3)
        self.ui_group = pyglet.graphics.Group(4)

        self.selected_character = 0
        self.selected_track = 0
        self.track = []
        self.track_length = 1.0
        self.track_def = TRACKS[0]
        self.rng = random.Random(1966)
        self.keys = set()

        self.selection_shapes = []
        self.selection_labels = []
        self.road_shapes = []
        self.scenery_shapes = []
        self.ai_shapes = []
        self.car_shapes = []
        self.labels = []
        self.car_base_y = {}
        self.rivals = []

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
        self.hop_total = 34.0
        self.hit_timer = 0.0
        self.feature_timer = 0.0
        self.launch_charge = 0.0
        self.launch_too_early = False
        self.air_trick_armed = False
        self.was_airborne = False
        self.slipstream_charge = 0.0
        self.finish_place = None

        self._build_character_select()

    def _clear_selection(self):
        for item in self.selection_shapes:
            try:
                item.delete()
            except Exception:
                pass
        for item in self.selection_labels:
            try:
                item.delete()
            except Exception:
                pass
        self.selection_shapes.clear()
        self.selection_labels.clear()

    def _selection_header(self, title, subtitle):
        title_label = pyglet.text.Label(
            title, x=EngineGlobals.width // 2, y=EngineGlobals.height - 44,
            anchor_x="center", font_size=27, weight=pyglet.text.Weight.BOLD,
            color=(255, 237, 157, 255), batch=self.batch, group=self.ui_group,
        )
        sub_label = pyglet.text.Label(
            subtitle, x=EngineGlobals.width // 2, y=EngineGlobals.height - 76,
            anchor_x="center", font_size=11, color=(214, 224, 239, 255),
            batch=self.batch, group=self.ui_group,
        )
        footer = pyglet.text.Label(
            "ARROWS choose   •   ENTER confirm   •   ESC back/menu",
            x=EngineGlobals.width // 2, y=30, anchor_x="center", font_size=10,
            color=(203, 213, 229, 255), batch=self.batch, group=self.ui_group,
        )
        self.selection_labels.extend((title_label, sub_label, footer))

    def _build_character_select(self):
        self._clear_selection()
        self.state = self.STATE_CHARACTER
        self._selection_header("3D REACHING", "CHOOSE A DRIVER — ALL USE THE BATMOBILE")
        self.character_panels = []

        xs = (86, 243, 400, 557, 714)
        ys = (374, 202)
        for index, character in enumerate(CHARACTERS):
            row = index // 5
            col = index % 5
            x, y = xs[col], ys[row]
            selected = index == self.selected_character
            panel = pyglet.shapes.Rectangle(
                x - 67, y - 70, 134, 140,
                color=(108, 116, 145) if selected else (47, 53, 66),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.character_panels.append(panel)

            art_loaded = False
            art_file = character.get("art")
            if art_file:
                try:
                    image = pyglet.resource.image(art_file)
                    sprite = pyglet.sprite.Sprite(
                        img=image, batch=self.batch, group=self.scenery_group
                    )
                    sprite.scale = min(
                        2.2, 60.0 / max(1.0, float(max(image.width, image.height)))
                    )
                    sprite.x = x - sprite.width / 2
                    sprite.y = y + 1 - sprite.height / 2
                    self.selection_shapes.append(sprite)
                    art_loaded = True
                except Exception:
                    art_loaded = False
            if not art_loaded:
                head = pyglet.shapes.Circle(
                    x, y + 7, 25, color=character["color"],
                    batch=self.batch, group=self.scenery_group,
                )
                eye1 = pyglet.shapes.Circle(
                    x - 8, y + 14, 3, color=(28, 25, 24),
                    batch=self.batch, group=self.scenery_group,
                )
                eye2 = pyglet.shapes.Circle(
                    x + 8, y + 14, 3, color=(28, 25, 24),
                    batch=self.batch, group=self.scenery_group,
                )
                self.selection_shapes.extend((head, eye1, eye2))

            self.selection_labels.append(pyglet.text.Label(
                character["name"].upper(), x=x, y=y + 52, anchor_x="center",
                font_size=9, weight=pyglet.text.Weight.BOLD,
                color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                "SPD {}  ACC {}  TURN {}".format(
                    character["speed"], character["accel"], character["turn"]
                ),
                x=x, y=y - 39, anchor_x="center", font_size=7,
                color=(229, 236, 247, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                "WGT {}  GRIP {}  BST {}".format(
                    character["weight"], character["grip"], character["boost"]
                ),
                x=x, y=y - 53, anchor_x="center", font_size=7,
                color=(203, 218, 237, 255), batch=self.batch, group=self.ui_group,
            ))

        self.character_detail = pyglet.text.Label(
            "", x=EngineGlobals.width // 2, y=78, anchor_x="center",
            font_size=11, weight=pyglet.text.Weight.BOLD,
            color=(255, 222, 132, 255), batch=self.batch, group=self.ui_group,
        )
        self.selection_labels.append(self.character_detail)
        self._refresh_character_select()

    def _refresh_character_select(self):
        for i, panel in enumerate(getattr(self, "character_panels", [])):
            panel.color = (111, 122, 154) if i == self.selected_character else (47, 53, 66)
        if hasattr(self, "character_detail"):
            c = CHARACTERS[self.selected_character]
            note = "PERFECT STATS" if c["name"] == "Kenny" else "COMPETITIVE SPECIALIST"
            self.character_detail.text = "{} — {}".format(c["name"].upper(), note)

    def _build_track_select(self):
        self._clear_selection()
        self.state = self.STATE_TRACK
        self._selection_header("3D REACHING", "CHOOSE A PSEUDO-3D CIRCUIT — 8 TRACKS")
        self.track_panels = []
        for index, track in enumerate(TRACKS):
            col = index % 2
            row = index // 2
            x = 214 + col * 372
            y = 430 - row * 88
            panel = pyglet.shapes.Rectangle(
                x - 167, y - 32, 334, 64,
                color=(100, 111, 139) if index == self.selected_track else (45, 51, 64),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.track_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                track["name"].upper(), x=x, y=y + 8, anchor_x="center",
                font_size=13, weight=pyglet.text.Weight.BOLD,
                color=(255, 246, 208, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                track["tagline"], x=x, y=y - 13, anchor_x="center",
                font_size=8, color=(200, 213, 230, 255),
                batch=self.batch, group=self.ui_group,
            ))

    def _refresh_track_select(self):
        for i, panel in enumerate(getattr(self, "track_panels", [])):
            panel.color = (100, 111, 139) if i == self.selected_track else (45, 51, 64)

    def _clear_race(self):
        for collection in (
            self.road_shapes, self.scenery_shapes, self.car_shapes, self.labels
        ):
            for item in collection:
                try:
                    item.delete()
                except Exception:
                    pass
            collection.clear()
        for pair in self.ai_shapes:
            for item in pair:
                try:
                    item.delete()
                except Exception:
                    pass
        self.ai_shapes.clear()
        self.car_base_y.clear()
        self.rivals.clear()

    def _build_track_data(self):
        self.track = []
        self.track_def = TRACKS[self.selected_track]
        index = 0
        for count, curve, hill in self.track_def["pattern"]:
            for _ in range(count):
                self.track.append({
                    "curve": float(curve),
                    "hill": float(hill),
                    "boost": index in self.track_def["boost"],
                    "oil": index in self.track_def["oil"],
                    "ramp": index in self.track_def["ramp"],
                    "mud": index in self.track_def["mud"],
                    "side": -1 if index % 18 == 0 else (1 if index % 18 == 9 else 0),
                })
                index += 1
        self.track_length = max(self.SEGMENT_LENGTH, len(self.track) * self.SEGMENT_LENGTH)

    def _build_static_scene(self):
        w = EngineGlobals.width
        h = EngineGlobals.height
        self.sky = pyglet.shapes.Rectangle(
            0, h * 0.47, w, h * 0.53,
            color=self.track_def["sky"], batch=self.batch, group=self.bg_group,
        )
        self.ground = pyglet.shapes.Rectangle(
            0, 0, w, h * 0.50,
            color=self.track_def["ground"], batch=self.batch, group=self.bg_group,
        )
        self.scenery_shapes.extend((self.sky, self.ground))
        self.moon = pyglet.shapes.Circle(
            w - 105, h - 95, 37, color=(231, 230, 197),
            batch=self.batch, group=self.bg_group,
        )
        self.scenery_shapes.append(self.moon)
        for i in range(13):
            bw = 35 + (i % 4) * 12
            bh = 42 + (i * 17) % 104
            building = pyglet.shapes.Rectangle(
                i * 67 - 8, h * 0.47, bw, bh,
                color=tuple(max(12, c - 24) for c in self.track_def["sky"]),
                batch=self.batch, group=self.bg_group,
            )
            self.scenery_shapes.append(building)

    def _new_triangle(self, color):
        tri = pyglet.shapes.Triangle(
            -1000, -1000, -1000, -1000, -1000, -1000,
            color=color, batch=self.batch, group=self.road_group,
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
        road = self.track_def["road"]
        for i in range(self.DRAW_SEGMENTS):
            grass = self.track_def["ground"]
            grass_alt = tuple(max(0, c - 8) if i % 2 else c for c in grass)
            road_color = tuple(max(0, c - 5) if i % 2 else c for c in road)
            edge_color = self.track_def["edge_a"] if i % 2 == 0 else self.track_def["edge_b"]
            tris = tuple(
                self._new_triangle(color) for color in (
                    grass_alt, grass_alt, grass_alt, grass_alt,
                    road_color, road_color,
                    edge_color, edge_color, edge_color, edge_color,
                )
            )
            boost = pyglet.shapes.Rectangle(
                -1000, -1000, 1, 1, color=(64, 207, 224),
                batch=self.batch, group=self.scenery_group,
            )
            oil = pyglet.shapes.Circle(
                -1000, -1000, 1, color=(25, 23, 27),
                batch=self.batch, group=self.scenery_group,
            )
            ramp = pyglet.shapes.Rectangle(
                -1000, -1000, 1, 1, color=(218, 164, 70),
                batch=self.batch, group=self.scenery_group,
            )
            mud = pyglet.shapes.Circle(
                -1000, -1000, 1, color=(116, 82, 54),
                batch=self.batch, group=self.scenery_group,
            )
            scenery = pyglet.shapes.Rectangle(
                -1000, -1000, 1, 1, color=self.track_def["scenery"],
                batch=self.batch, group=self.scenery_group,
            )
            self.scenery_shapes.extend((boost, oil, ramp, mud, scenery))
            self.road_pool.append({
                "tris": tris, "boost": boost, "oil": oil, "ramp": ramp,
                "mud": mud, "scenery": scenery,
            })

    def _selected_profile(self):
        return CHARACTERS[self.selected_character]

    def _physics(self):
        c = self._selected_profile()
        return {
            "max_speed": (7.45 + c["speed"] * 0.215) * self.track_def["max_speed"],
            "boost_speed": (9.15 + c["speed"] * 0.20 + c["boost"] * 0.16) * self.track_def["max_speed"],
            "accel": 0.115 + c["accel"] * 0.0125,
            "brake": 0.18 + c["accel"] * 0.010,
            "steer": (0.021 + c["turn"] * 0.0026) * self.track_def["grip"],
            "drift_steer": (0.034 + c["turn"] * 0.0035) * self.track_def["grip"],
            "offroad": 0.858 + c["grip"] * 0.0068,
            "grip": c["grip"],
            "weight": c["weight"],
            "boost": c["boost"],
        }

    def _build_batmobile(self):
        w = EngineGlobals.width
        center = w / 2
        self.bat_shadow = pyglet.shapes.Ellipse(
            center, 66, 73, 21, color=(18, 20, 25),
            batch=self.batch, group=self.car_group,
        )
        body = pyglet.shapes.Rectangle(
            center - 60, 58, 120, 37, color=(24, 27, 34),
            batch=self.batch, group=self.car_group,
        )
        nose = pyglet.shapes.Triangle(
            center - 58, 74, center + 58, 74, center, 122,
            color=(31, 35, 44), batch=self.batch, group=self.car_group,
        )
        cockpit = pyglet.shapes.Circle(
            center, 88, 21, color=(57, 72, 86),
            batch=self.batch, group=self.car_group,
        )
        driver = pyglet.shapes.Circle(
            center, 91, 12, color=self._selected_profile()["color"],
            batch=self.batch, group=self.car_group,
        )
        fin_l = pyglet.shapes.Triangle(
            center - 49, 90, center - 78, 116, center - 29, 103,
            color=(18, 20, 26), batch=self.batch, group=self.car_group,
        )
        fin_r = pyglet.shapes.Triangle(
            center + 49, 90, center + 78, 116, center + 29, 103,
            color=(18, 20, 26), batch=self.batch, group=self.car_group,
        )
        bat_mark = pyglet.shapes.Triangle(
            center, 67, center - 15, 78, center + 15, 78,
            color=(236, 204, 67), batch=self.batch, group=self.car_group,
        )
        wheels = [
            pyglet.shapes.Circle(
                center + offset, 58, 10, color=(12, 13, 16),
                batch=self.batch, group=self.car_group,
            )
            for offset in (-53, -27, 27, 53)
        ]
        self.car_shapes.extend(
            [self.bat_shadow, body, nose, cockpit, driver, fin_l, fin_r, bat_mark] + wheels
        )
        for shape in self.car_shapes:
            self.car_base_y[id(shape)] = getattr(shape, "y", 0.0)

    def _spawn_rivals(self):
        available = [c for i, c in enumerate(CHARACTERS) if i != self.selected_character]
        self.rng.shuffle(available)
        chosen = available[:7]
        self.rivals = []
        for i, c in enumerate(chosen):
            rival = Rival(
                lane=-0.76 + (i % 4) * 0.50,
                distance=150.0 + i * 115.0,
                speed=6.7 + c["speed"] * 0.17 + (i % 3) * 0.08,
                color=c["color"], name=c["name"], weight=c["weight"],
            )
            self.rivals.append(rival)
            kart = pyglet.shapes.Rectangle(
                -1000, -1000, 28, 16, color=c["color"],
                batch=self.batch, group=self.scenery_group,
            )
            head = pyglet.shapes.Circle(
                -1000, -1000, 5, color=c["color"],
                batch=self.batch, group=self.scenery_group,
            )
            self.ai_shapes.append((kart, head))

    def _build_ui(self):
        c = self._selected_profile()
        self.track_title = pyglet.text.Label(
            self.track_def["name"].upper(), x=EngineGlobals.width // 2,
            y=EngineGlobals.height - 27, anchor_x="center", font_size=13,
            weight=pyglet.text.Weight.BOLD, color=(247, 229, 126, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.lap_label = pyglet.text.Label(
            "LAP 1/3", x=18, y=EngineGlobals.height - 28,
            font_size=14, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255), batch=self.batch, group=self.ui_group,
        )
        self.place_label = pyglet.text.Label(
            "PLACE 8/8", x=18, y=EngineGlobals.height - 51,
            font_size=12, color=(255, 255, 255, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.speed_label = pyglet.text.Label(
            "{} BATMOBILE 0".format(c["name"].upper()), x=18, y=20,
            font_size=11, color=(241, 224, 135, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.drift_label = pyglet.text.Label(
            "SPACE = DRIFT", x=EngineGlobals.width - 18, y=20,
            anchor_x="right", font_size=11, color=(212, 225, 244, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.mechanic_label = pyglet.text.Label(
            "", x=EngineGlobals.width - 18, y=42, anchor_x="right",
            font_size=10, color=(119, 232, 244, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.countdown_label = pyglet.text.Label(
            "3", x=EngineGlobals.width // 2,
            y=EngineGlobals.height // 2 + 50, anchor_x="center", anchor_y="center",
            font_size=72, weight=pyglet.text.Weight.BOLD,
            color=(244, 226, 105, 255), batch=self.batch, group=self.ui_group,
        )
        self.help_label = pyglet.text.Label(
            "↑ accelerate  ↓ brake  ← → steer  SPACE hop/drift/trick  ESC menu",
            x=EngineGlobals.width // 2, y=EngineGlobals.height - 50,
            anchor_x="center", font_size=8, color=(218, 225, 236, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.finish_panel = pyglet.shapes.Rectangle(
            145, 160, 510, 270, color=(22, 25, 35),
            batch=self.batch, group=self.ui_group,
        )
        self.finish_panel.opacity = 235
        self.finish_panel.visible = False
        self.scenery_shapes.append(self.finish_panel)
        self.finish_title = pyglet.text.Label(
            "", x=EngineGlobals.width // 2, y=370, anchor_x="center",
            font_size=30, weight=pyglet.text.Weight.BOLD,
            color=(246, 228, 115, 255), batch=self.batch, group=self.ui_group,
        )
        self.finish_result = pyglet.text.Label(
            "", x=EngineGlobals.width // 2, y=315, anchor_x="center",
            font_size=17, color=(255, 255, 255, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.finish_prompt = pyglet.text.Label(
            "", x=EngineGlobals.width // 2, y=245, anchor_x="center",
            font_size=12, color=(216, 224, 238, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.labels.extend((
            self.track_title, self.lap_label, self.place_label, self.speed_label,
            self.drift_label, self.mechanic_label, self.countdown_label,
            self.help_label, self.finish_title, self.finish_result, self.finish_prompt,
        ))

    def _start_race(self):
        self._clear_selection()
        self._clear_race()
        self._build_track_data()
        self._build_static_scene()
        self._build_projected_road_pool()
        self._build_batmobile()
        self._spawn_rivals()
        self._build_ui()

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
        self.feature_timer = 0.0
        self.launch_charge = 0.0
        self.launch_too_early = False
        self.air_trick_armed = False
        self.was_airborne = False
        self.slipstream_charge = 0.0
        self.finish_place = None
        self.keys.clear()
        self.countdown_label.visible = True

    def start(self):
        self.active = True
        self.keys.clear()
        self.selected_character = 0
        self.selected_track = 0
        self._clear_race()
        self._build_character_select()

    def stop(self):
        self.active = False
        self.keys.clear()
        self._clear_selection()
        self._clear_race()

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
        centers, widths, ys = [], [], []
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
            center = (
                base_center + lateral_shift * perspective
                + curve_acc * 430.0 * perspective
            )
            centers.append(center)
            widths.append(road_half)
            ys.append(y)

        for i in range(self.DRAW_SEGMENTS):
            pool = self.road_pool[i]
            c1, c2 = centers[i], centers[i + 1]
            r1, r2 = widths[i], widths[i + 1]
            y1, y2 = ys[i], ys[i + 1]
            l1, rr1 = c1 - r1, c1 + r1
            l2, rr2 = c2 - r2, c2 + r2
            edge1, edge2 = max(3.0, r1 * 0.065), max(4.0, r2 * 0.065)
            lg1, lg2, rg1, rg2, road1, road2, el1, el2, er1, er2 = pool["tris"]
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
            scale = p ** 1.5
            for key in ("boost", "oil", "ramp", "mud", "scenery"):
                pool[key].visible = bool(seg[key if key != "scenery" else "side"])
            if pool["boost"].visible:
                pool["boost"].width = max(3.0, 100.0 * scale)
                pool["boost"].height = max(2.0, 10.0 * scale)
                pool["boost"].x = c2 - pool["boost"].width / 2
                pool["boost"].y = y2 - pool["boost"].height / 2
            if pool["oil"].visible:
                pool["oil"].radius = max(2.0, 24.0 * scale)
                pool["oil"].position = (c2 + r2 * 0.18, y2)
            if pool["ramp"].visible:
                pool["ramp"].width = max(4.0, 95.0 * scale)
                pool["ramp"].height = max(2.0, 22.0 * scale)
                pool["ramp"].position = (
                    c2 - pool["ramp"].width / 2, y2 - pool["ramp"].height / 2
                )
            if pool["mud"].visible:
                pool["mud"].radius = max(2.0, 28.0 * scale)
                pool["mud"].position = (c2 - r2 * 0.12, y2)
            if pool["scenery"].visible:
                pool["scenery"].width = max(4.0, 28.0 * scale)
                pool["scenery"].height = max(7.0, 78.0 * scale)
                side = seg["side"]
                pool["scenery"].x = c2 + side * (r2 + 34.0 * scale)
                pool["scenery"].y = y2
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

    def _show_mechanic(self, text, timer=55.0):
        self.mechanic_label.text = text
        self.feature_timer = max(self.feature_timer, timer)

    def _track_interactions(self):
        seg = self._segment_at(self.distance + 12.0)
        p = self._physics()
        if seg["boost"] and abs(self.player_lane) < 0.78 and self.hit_timer <= 0:
            self.boost_timer = max(self.boost_timer, 38.0 + p["boost"] * 3.0)
            self.speed = max(self.speed, p["max_speed"] + 0.7)
            self._show_mechanic("BOOST STRIP!", 30.0)
        if seg["oil"] and abs(self.player_lane - 0.18) < 0.29 and self.hit_timer <= 0:
            self.speed *= 0.54 + p["weight"] * 0.018
            self.player_lane += self.rng.choice((-0.40, 0.40))
            self.hit_timer = 58.0
            self._show_mechanic("OIL SPIN!", 58.0)
        if seg["mud"] and abs(self.player_lane + 0.12) < 0.44:
            self.speed *= (0.89 + p["grip"] * 0.006) ** 0.75
            self._show_mechanic("ROUGH GROUND", 8.0)
        if seg["ramp"] and abs(self.player_lane) < 0.86 and self.hop_timer <= 0:
            self.hop_total = 42.0
            self.hop_timer = self.hop_total
            self.was_airborne = True
            self.air_trick_armed = False
            self._show_mechanic("RAMP! TAP SPACE FOR A TRICK", 45.0)

    def _check_rival_collision(self):
        if self.hit_timer > 0:
            return
        p = self._physics()
        for rival in self.rivals:
            relative = (rival.distance - self.distance) % self.track_length
            if relative < 38.0 and abs(rival.lane - self.player_lane) < 0.27:
                weight_ratio = p["weight"] / max(1.0, float(rival.weight))
                if weight_ratio >= 1.0:
                    self.speed *= max(0.84, 0.94 - 0.03 / weight_ratio)
                    rival.speed *= 0.78
                    rival.hit_timer = 26.0
                    rival.lane += 0.18 if rival.lane > self.player_lane else -0.18
                else:
                    self.speed *= max(0.60, 0.77 * weight_ratio)
                    self.player_lane += -0.20 if rival.lane > self.player_lane else 0.20
                self.hit_timer = 22.0
                self._show_mechanic("KART BUMP!", 24.0)
                break

    def _apply_slipstream(self, dt):
        p = self._physics()
        drafting = False
        if self.speed > p["max_speed"] * 0.55:
            for rival in self.rivals:
                relative = (rival.distance - self.distance) % self.track_length
                if 45.0 < relative < 155.0 and abs(rival.lane - self.player_lane) < 0.22:
                    drafting = True
                    break
        if drafting:
            self.slipstream_charge = min(
                100.0, self.slipstream_charge + (0.85 + p["boost"] * 0.05) * dt
            )
            if self.slipstream_charge >= 100.0:
                self.boost_timer = max(self.boost_timer, 44.0 + p["boost"] * 2.5)
                self.speed = max(self.speed, p["max_speed"] + 0.8)
                self.slipstream_charge = 0.0
                self._show_mechanic("SLIPSTREAM BOOST!", 58.0)
        else:
            self.slipstream_charge = max(0.0, self.slipstream_charge - 1.15 * dt)

    def _update_player(self, dt):
        p = self._physics()
        up = pyglet.window.key.UP in self.keys
        down = pyglet.window.key.DOWN in self.keys
        left = pyglet.window.key.LEFT in self.keys
        right = pyglet.window.key.RIGHT in self.keys
        space = pyglet.window.key.SPACE in self.keys

        if up:
            self.speed += p["accel"] * dt
        elif down:
            self.speed -= p["brake"] * dt
        else:
            self.speed *= 0.982 ** dt

        max_speed = p["boost_speed"] if self.boost_timer > 0 else p["max_speed"]
        if self.boost_timer > 0:
            self.boost_timer -= dt
            self.speed += (0.025 + p["boost"] * 0.0025) * dt
        self.speed = max(-2.3, min(max_speed, self.speed))

        steer = (-1 if left else 0) + (1 if right else 0)
        steer_rate = p["drift_steer"] if self.drifting else p["steer"]
        if steer and abs(self.speed) > 0.2:
            speed_factor = 0.58 + abs(self.speed) / max(8.0, p["max_speed"])
            self.player_lane += steer * steer_rate * speed_factor * dt
        if self.drifting and space and steer:
            c = self._selected_profile()
            self.drift_charge = min(
                100.0,
                self.drift_charge + (0.35 + c["turn"] * 0.045 + c["boost"] * 0.035) * dt,
            )

        current_curve = self._segment_at(self.distance + 80.0)["curve"]
        curve_pull = current_curve * max(0.0, self.speed) * (0.29 - p["grip"] * 0.009)
        self.player_lane -= curve_pull * dt

        if abs(self.player_lane) > 1.04:
            self.speed *= p["offroad"] ** dt
        self.player_lane = max(-1.43, min(1.43, self.player_lane))

        airborne_before = self.hop_timer > 0
        if self.hop_timer > 0:
            self.hop_timer = max(0.0, self.hop_timer - dt)
            progress = 1.0 - self.hop_timer / max(1.0, self.hop_total)
            hop = math.sin(max(0.0, min(math.pi, progress * math.pi))) * 12.0
        else:
            hop = 0.0
        for shape in self.car_shapes:
            try:
                shape.y = self.car_base_y[id(shape)] + hop
            except Exception:
                pass

        if airborne_before and self.hop_timer <= 0 and self.was_airborne:
            if self.air_trick_armed:
                self.boost_timer = max(self.boost_timer, 34.0 + p["boost"] * 3.0)
                self.speed = max(self.speed, p["max_speed"] + 0.5)
                self._show_mechanic("TRICK LANDING BOOST!", 52.0)
            self.air_trick_armed = False
            self.was_airborne = False

        if self.hit_timer > 0:
            self.hit_timer -= dt
        if self.feature_timer > 0:
            self.feature_timer -= dt
            if self.feature_timer <= 0:
                self.mechanic_label.text = ""

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
        self._apply_slipstream(dt)

    def _update_rivals(self, dt):
        for rival in self.rivals:
            seg = self._segment_at(rival.distance)
            curve_penalty = min(1.0, abs(seg["curve"]) * 12.0)
            target = rival.base_speed * self.track_def["max_speed"] * (
                1.0 - curve_penalty * 0.16
            )
            player_progress = self.lap * self.track_length + self.distance
            rival_progress = rival.finished_laps * self.track_length + rival.distance
            gap = player_progress - rival_progress
            if gap > 900:
                target += min(0.85, gap / 2800.0)
            elif gap < -1100:
                target -= min(0.45, abs(gap) / 5000.0)

            if seg["boost"]:
                rival.boost_timer = max(rival.boost_timer, 35.0)
            if rival.boost_timer > 0:
                rival.boost_timer -= dt
                target += 0.9
            if seg["oil"] and abs(rival.lane - 0.18) < 0.24 and rival.hit_timer <= 0:
                target *= 0.62
                rival.lane += self.rng.choice((-0.20, 0.20))
                rival.hit_timer = 45.0
            if seg["mud"] and abs(rival.lane + 0.12) < 0.42:
                target *= 0.82
            if rival.hit_timer > 0:
                rival.hit_timer -= dt
                target *= 0.90

            rival.speed += (target - rival.speed) * min(1.0, 0.045 * dt)
            rival.wobble += 0.014 * dt
            rival.lane += math.sin(rival.wobble) * 0.0022 * dt
            rival.lane -= seg["curve"] * 0.7 * dt
            rival.lane = max(-0.88, min(0.88, rival.lane))
            rival.distance += max(0.0, rival.speed) * dt
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

    def _release_drift(self):
        if not self.drifting:
            return
        p = self._physics()
        charge = self.drift_charge
        if charge >= 82:
            self.boost_timer = max(self.boost_timer, 74.0 + p["boost"] * 2.0)
            self.speed = max(self.speed, p["max_speed"] + 1.2)
            self._show_mechanic("ULTRA DRIFT TURBO!", 60.0)
        elif charge >= 48:
            self.boost_timer = max(self.boost_timer, 48.0 + p["boost"] * 1.6)
            self.speed = max(self.speed, p["max_speed"] + 0.8)
            self._show_mechanic("SUPER DRIFT TURBO!", 48.0)
        elif charge >= 22:
            self.boost_timer = max(self.boost_timer, 28.0 + p["boost"] * 1.2)
            self.speed = max(self.speed, p["max_speed"] + 0.4)
            self._show_mechanic("MINI TURBO!", 36.0)
        self.drifting = False
        self.drift_charge = 0.0

    def _finish_race(self):
        self.state = self.STATE_FINISH
        self.speed = 0.0
        self.finish_place = self._place()
        self.finish_panel.visible = True
        self.finish_title.text = "BATMOBILE FINISH!"
        self.finish_result.text = "{} finished {} of 8".format(
            self._selected_profile()["name"], self.finish_place
        )
        self.finish_prompt.text = "ENTER rematch   •   ESC main menu"

    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED

        if self.state == self.STATE_CHARACTER:
            if symbol == pyglet.window.key.ESCAPE:
                self.stop()
                if self.on_exit_to_menu:
                    self.on_exit_to_menu()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_character = (self.selected_character - 1) % len(CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_character = (self.selected_character + 1) % len(CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_character = (self.selected_character - 5) % len(CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_character = (self.selected_character + 5) % len(CHARACTERS)
                self._refresh_character_select()
            elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
                self._build_track_select()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_TRACK:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_character_select()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_track = (self.selected_track - 1) % len(TRACKS)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_track = (self.selected_track + 1) % len(TRACKS)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_track = (self.selected_track - 2) % len(TRACKS)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_track = (self.selected_track + 2) % len(TRACKS)
                self._refresh_track_select()
            elif symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
                self._start_race()
            return pyglet.event.EVENT_HANDLED

        if symbol == pyglet.window.key.ESCAPE:
            self.stop()
            if self.on_exit_to_menu:
                self.on_exit_to_menu()
            return pyglet.event.EVENT_HANDLED

        if self.state == self.STATE_FINISH:
            if symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN):
                self._start_race()
            return pyglet.event.EVENT_HANDLED

        self.keys.add(symbol)
        if self.state == self.STATE_RACE and symbol == pyglet.window.key.SPACE:
            if self.hop_timer > 16.0 and self.was_airborne:
                self.air_trick_armed = True
                self._show_mechanic("AIR TRICK!", 26.0)
            elif not self.drifting:
                self.drifting = True
                self.drift_charge = 0.0
                self.hop_total = 14.0
                self.hop_timer = max(self.hop_timer, self.hop_total)
        return pyglet.event.EVENT_HANDLED

    def on_key_release(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        self.keys.discard(symbol)
        if self.state == self.STATE_RACE and symbol == pyglet.window.key.SPACE:
            self._release_drift()
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def update(self, dt):
        if not self.active:
            return
        dt = float(dt)
        if self.state in (self.STATE_CHARACTER, self.STATE_TRACK):
            return

        if self.state == self.STATE_COUNTDOWN:
            self.countdown -= dt
            up = pyglet.window.key.UP in self.keys
            if self.countdown > 120:
                self.countdown_label.text = "3"
                if up:
                    self.launch_too_early = True
            elif self.countdown > 60:
                self.countdown_label.text = "2"
                if up:
                    self.launch_charge = min(100.0, self.launch_charge + 0.65 * dt)
            elif self.countdown > 20:
                self.countdown_label.text = "1"
                if up:
                    self.launch_charge = min(100.0, self.launch_charge + 1.6 * dt)
            elif self.countdown > 0:
                self.countdown_label.text = "GO!"
            else:
                self.state = self.STATE_RACE
                self.countdown_label.visible = False
                p = self._physics()
                if self.launch_too_early:
                    self.speed = 1.2
                    self._show_mechanic("WHEELSPIN!", 58.0)
                elif self.launch_charge >= 72:
                    self.speed = p["max_speed"] * 0.94
                    self.boost_timer = 66.0 + p["boost"] * 2.0
                    self._show_mechanic("PERFECT LAUNCH!", 65.0)
                elif self.launch_charge >= 38:
                    self.speed = p["max_speed"] * 0.72
                    self.boost_timer = 38.0 + p["boost"] * 1.5
                    self._show_mechanic("GOOD LAUNCH!", 45.0)
            centers, widths, ys = self._project_road()
            self._update_rival_visuals(centers, widths, ys)
            return

        if self.state == self.STATE_RACE:
            self.race_time += dt
            self._update_player(dt)
            if self.state == self.STATE_FINISH:
                return
            self._update_rivals(dt)
            centers, widths, ys = self._project_road()
            self._update_rival_visuals(centers, widths, ys)
            self.lap_label.text = "LAP {}/{}".format(
                min(self.TOTAL_LAPS, self.lap + 1), self.TOTAL_LAPS
            )
            self.place_label.text = "PLACE {}/8".format(self._place())
            boost = " BOOST" if self.boost_timer > 0 else ""
            self.speed_label.text = "{} BATMOBILE {:.1f}{}".format(
                self._selected_profile()["name"].upper(), abs(self.speed), boost
            )
            if self.drifting:
                self.drift_label.text = "DRIFT {}%".format(int(self.drift_charge))
            elif self.slipstream_charge > 0:
                self.drift_label.text = "DRAFT {}%".format(int(self.slipstream_charge))
            else:
                self.drift_label.text = "SPACE = HOP / DRIFT / TRICK"
            return

        if self.state == self.STATE_FINISH:
            self._update_rivals(dt)
            centers, widths, ys = self._project_road()
            self._update_rival_visuals(centers, widths, ys)

    def draw(self):
        if self.active:
            self.batch.draw()
