"""Core menus, cup flow, track data, and UI for the full 3D Reaching game."""

import pyglet

import mode7_racing as base
from engineglobals import EngineGlobals
from mode7_full_content import CUPS, FULL_TRACKS, MODES, POINTS, SPEED_CLASSES

class FullMode7CoreMixin:
    """A complete 20-track cup racer built on the Mode-7-style renderer."""

    STATE_MODE = "mode"
    STATE_CLASS = "class"
    STATE_CUP = "cup"
    STATE_STANDINGS = "standings"
    STATE_CUP_DONE = "cup_done"

    TOTAL_LAPS = 5

    def __init__(self, on_exit_to_menu=None):
        super().__init__(on_exit_to_menu=on_exit_to_menu)
        self.selected_mode = 0
        self.play_mode = "GRAND PRIX"
        self.selected_class = 1
        self.selected_cup = 0
        self.gp_race = 0
        self.gp_points = {}
        self.gp_roster = []
        self.gp_history = []
        self.held_item = None
        self.item_box_cooldown = 0.0
        self.last_item_key = None
        self.coin_count = 0
        self.coin_cooldown = 0.0
        self.last_coin_key = None
        self.shield_timer = 0.0
        self.invincible_timer = 0.0
        self.player_traps = []
        self.item_pool = []
        self.coin_pool = []
        self.progress_dots = []
        self.best_laps = {}
        self.best_times = {}
        self.lap_started_at = 0.0
        self.current_best_lap = None
        self._clear_selection()
        self._build_mode_select()

    def _build_mode_select(self):
        self._clear_selection()
        self.state = self.STATE_MODE
        self._selection_header("3D REACHING", "A FULL 20-TRACK BATMOBILE CHAMPIONSHIP")
        self.mode_panels = []
        for i, (name, note) in enumerate(MODES):
            y = 405 - i * 120
            panel = pyglet.shapes.Rectangle(
                160, y - 36, 480, 76,
                color=(112, 123, 153) if i == self.selected_mode else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.mode_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                name, x=400, y=y + 8, anchor_x="center", font_size=19,
                weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                note, x=400, y=y - 17, anchor_x="center", font_size=10,
                color=(207, 219, 236, 255), batch=self.batch, group=self.ui_group,
            ))

    def _refresh_mode_select(self):
        for i, panel in enumerate(self.mode_panels):
            panel.color = (112, 123, 153) if i == self.selected_mode else (45, 51, 65)

    def _build_class_select(self):
        self._clear_selection()
        self.state = self.STATE_CLASS
        self._selection_header("ENGINE CLASS", "50cc, 100cc, OR 150cc")
        self.class_panels = []
        for i, engine in enumerate(SPEED_CLASSES):
            x = 180 + i * 220
            panel = pyglet.shapes.Rectangle(
                x - 90, 235, 180, 210,
                color=(112, 123, 153) if i == self.selected_class else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.class_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                engine["name"], x=x, y=388, anchor_x="center", font_size=26,
                weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                engine["note"], x=x, y=342, anchor_x="center", font_size=12,
                color=(210, 225, 241, 255), batch=self.batch, group=self.ui_group,
            ))
            speed_pct = int(engine["speed"] * 100)
            ai_pct = int(engine["ai"] * 100)
            self.selection_labels.append(pyglet.text.Label(
                "SPEED {}%\nRIVALS {}%".format(speed_pct, ai_pct),
                x=x, y=294, anchor_x="center", multiline=True, width=150,
                align="center", font_size=10, color=(198, 211, 231, 255),
                batch=self.batch, group=self.ui_group,
            ))

    def _refresh_class_select(self):
        for i, panel in enumerate(self.class_panels):
            panel.color = (112, 123, 153) if i == self.selected_class else (45, 51, 65)

    def _build_cup_select(self):
        self._clear_selection()
        self.state = self.STATE_CUP
        self._selection_header("GRAND PRIX", "CHOOSE A FIVE-RACE CUP")
        self.cup_panels = []
        for i, cup in enumerate(CUPS):
            col, row = i % 2, i // 2
            x = 215 + col * 370
            y = 395 - row * 200
            panel = pyglet.shapes.Rectangle(
                x - 165, y - 76, 330, 150,
                color=(112, 123, 153) if i == self.selected_cup else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.cup_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                cup["name"], x=x, y=y + 45, anchor_x="center", font_size=18,
                weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
                batch=self.batch, group=self.ui_group,
            ))
            names = [FULL_TRACKS[idx]["name"] for idx in cup["tracks"]]
            self.selection_labels.append(pyglet.text.Label(
                "\n".join(names), x=x, y=y + 20, anchor_x="center", anchor_y="top",
                multiline=True, width=300, align="center", font_size=8,
                color=(207, 219, 236, 255), batch=self.batch, group=self.ui_group,
            ))

    def _refresh_cup_select(self):
        for i, panel in enumerate(self.cup_panels):
            panel.color = (112, 123, 153) if i == self.selected_cup else (45, 51, 65)

    def _build_track_select(self):
        self._clear_selection()
        self.state = self.STATE_TRACK
        self._selection_header("FREE RACE", "CHOOSE FROM ALL 20 TRACKS")
        self.track_panels = []
        for index, track in enumerate(FULL_TRACKS):
            col = index % 4
            row = index // 4
            x = 105 + col * 195
            y = 455 - row * 75
            panel = pyglet.shapes.Rectangle(
                x - 88, y - 27, 176, 54,
                color=(103, 114, 144) if index == self.selected_track else (43, 49, 63),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.track_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                track["name"].upper(), x=x, y=y + 3, anchor_x="center",
                multiline=True, width=164, align="center", font_size=7,
                weight=pyglet.text.Weight.BOLD, color=(255, 244, 204, 255),
                batch=self.batch, group=self.ui_group,
            ))
        self.track_detail = pyglet.text.Label(
            "", x=400, y=58, anchor_x="center", font_size=9,
            color=(203, 218, 237, 255), batch=self.batch, group=self.ui_group,
        )
        self.selection_labels.append(self.track_detail)
        self._refresh_track_select()

    def _refresh_track_select(self):
        for i, panel in enumerate(getattr(self, "track_panels", [])):
            panel.color = (103, 114, 144) if i == self.selected_track else (43, 49, 63)
        if hasattr(self, "track_detail"):
            track = FULL_TRACKS[self.selected_track]
            cup_name = next((c["name"] for c in CUPS if self.selected_track in c["tracks"]), "")
            self.track_detail.text = "{} • {}".format(cup_name, track["tagline"])

    def _build_standings(self, final=False):
        self._clear_race()
        self._clear_selection()
        self.state = self.STATE_CUP_DONE if final else self.STATE_STANDINGS
        cup = CUPS[self.selected_cup]
        subtitle = "FINAL CHAMPIONSHIP" if final else "AFTER RACE {}/5".format(self.gp_race + 1)
        self._selection_header(cup["name"], subtitle)
        standings = sorted(self.gp_points.items(), key=lambda kv: (-kv[1], kv[0]))
        for i, (name, points) in enumerate(standings):
            y = 454 - i * 47
            is_player = name == self._selected_profile()["name"]
            panel = pyglet.shapes.Rectangle(
                185, y - 16, 430, 34,
                color=(106, 118, 151) if is_player else (44, 50, 63),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                "{}. {}".format(i + 1, name.upper()), x=205, y=y,
                anchor_y="center", font_size=11, weight=pyglet.text.Weight.BOLD,
                color=(255, 247, 211, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                "{} PTS".format(points), x=592, y=y, anchor_x="right", anchor_y="center",
                font_size=11, color=(233, 216, 128, 255),
                batch=self.batch, group=self.ui_group,
            ))
        if final:
            champion = standings[0][0] if standings else self._selected_profile()["name"]
            prompt = "{} WINS THE CUP!  •  ENTER returns to mode select".format(champion.upper())
        else:
            next_track = FULL_TRACKS[cup["tracks"][self.gp_race + 1]]["name"]
            prompt = "ENTER next race: {}".format(next_track.upper())
        self.selection_labels.append(pyglet.text.Label(
            prompt, x=400, y=70, anchor_x="center", font_size=10,
            weight=pyglet.text.Weight.BOLD, color=(255, 223, 133, 255),
            batch=self.batch, group=self.ui_group,
        ))

    def _begin_cup(self):
        self.gp_race = 0
        player = self._selected_profile()
        candidates = [c for c in base.CHARACTERS if c["name"] != player["name"]]
        self.rng.shuffle(candidates)
        self.gp_roster = [player] + candidates[:7]
        self.gp_points = {c["name"]: 0 for c in self.gp_roster}
        self.gp_history = []
        self.selected_track = CUPS[self.selected_cup]["tracks"][0]
        self._start_race()

    def _race_order(self):
        entries = [(self._selected_profile()["name"], self.lap * self.track_length + self.distance)]
        entries.extend(
            (rival.name, rival.finished_laps * self.track_length + rival.distance)
            for rival in self.rivals
        )
        entries.sort(key=lambda item: item[1], reverse=True)
        return [name for name, _ in entries]

    def _award_gp_points(self):
        order = self._race_order()
        for i, name in enumerate(order[:8]):
            if name in self.gp_points:
                self.gp_points[name] += POINTS[i]
        self.gp_history.append(tuple(order))
        return order

    def _advance_gp(self):
        if self.gp_race >= 4:
            self._build_standings(final=True)
            return
        self.gp_race += 1
        self.selected_track = CUPS[self.selected_cup]["tracks"][self.gp_race]
        self._start_race()

    def _class_def(self):
        return SPEED_CLASSES[self.selected_class]

    def _physics(self):
        physics = super()._physics()
        engine = self._class_def()
        coin_bonus = 1.0 + min(10, self.coin_count) * 0.004
        physics["max_speed"] *= engine["speed"] * coin_bonus
        physics["boost_speed"] *= engine["speed"] * coin_bonus
        physics["accel"] *= engine["accel"]
        physics["brake"] *= 0.98 + engine["accel"] * 0.02
        return physics

    def _build_track_data(self):
        super()._build_track_data()
        total = len(self.track)
        track_offset = (self.selected_track * 7) % 19
        item_indexes = set(range(16 + track_offset, total, 37))
        coin_indexes = set(range(8 + (track_offset // 2), total, 23))
        for i, segment in enumerate(self.track):
            segment["item"] = i in item_indexes
            segment["coin"] = i in coin_indexes and not segment["oil"] and not segment["mud"]

    def _build_projected_road_pool(self):
        super()._build_projected_road_pool()
        self.item_pool = []
        self.coin_pool = []
        for _ in range(self.DRAW_SEGMENTS):
            item = pyglet.shapes.Rectangle(
                -1000, -1000, 2, 2, color=(224, 98, 226),
                batch=self.batch, group=self.scenery_group,
            )
            coin = pyglet.shapes.Circle(
                -1000, -1000, 2, color=(246, 206, 62),
                batch=self.batch, group=self.scenery_group,
            )
            self.item_pool.append(item)
            self.coin_pool.append(coin)
            self.scenery_shapes.extend((item, coin))

    def _project_road(self):
        centers, widths, ys = super()._project_road()
        for i in range(self.DRAW_SEGMENTS):
            world_distance = self.distance + (self.DRAW_SEGMENTS - i) * self.SEGMENT_LENGTH
            segment = self._segment_at(world_distance)
            p = max(0.04, min(1.0, (i + 1) / float(self.DRAW_SEGMENTS)))
            scale = p ** 1.5
            center = centers[i + 1]
            half = widths[i + 1]
            y = ys[i + 1]
            item = self.item_pool[i]
            coin = self.coin_pool[i]
            item.visible = bool(segment.get("item")) and self.play_mode != "TIME TRIAL"
            coin.visible = bool(segment.get("coin"))
            if item.visible:
                item.width = max(3.0, 22.0 * scale)
                item.height = max(3.0, 22.0 * scale)
                item.x = center - item.width / 2
                item.y = y
            if coin.visible:
                coin.radius = max(2.0, 8.0 * scale)
                coin.position = (center - half * 0.18, y + coin.radius)
        return centers, widths, ys

    def _spawn_rivals(self):
        if self.play_mode == "TIME TRIAL":
            self.rivals = []
            self.ai_shapes = []
            return
        if self.play_mode == "GRAND PRIX" and self.gp_roster:
            chosen = self.gp_roster[1:]
            self.rivals = []
            for i, character in enumerate(chosen):
                rival = base.Rival(
                    lane=-0.76 + (i % 4) * 0.50,
                    distance=150.0 + i * 115.0,
                    speed=(6.7 + character["speed"] * 0.17 + (i % 3) * 0.08) * self._class_def()["ai"],
                    color=character["color"], name=character["name"], weight=character["weight"],
                )
                rival.item_cooldown = 180.0 + i * 25.0
                self.rivals.append(rival)
                kart = pyglet.shapes.Rectangle(
                    -1000, -1000, 28, 16, color=character["color"],
                    batch=self.batch, group=self.scenery_group,
                )
                head = pyglet.shapes.Circle(
                    -1000, -1000, 5, color=character["color"],
                    batch=self.batch, group=self.scenery_group,
                )
                self.ai_shapes.append((kart, head))
            return
        super()._spawn_rivals()
        for i, rival in enumerate(self.rivals):
            rival.base_speed *= self._class_def()["ai"]
            rival.speed *= self._class_def()["ai"]
            rival.item_cooldown = 180.0 + i * 25.0

    def _build_ui(self):
        super()._build_ui()
        self.lap_label.text = "LAP 1/{}".format(self.TOTAL_LAPS)
        self.help_label.text = "↑ accelerate  ↓ brake  ← → steer  SPACE drift/trick  D use item  ESC menu"
        self.class_label = pyglet.text.Label(
            "{} • {}".format(self.play_mode, self._class_def()["name"]),
            x=18, y=EngineGlobals.height - 72, font_size=9,
            color=(196, 210, 233, 255), batch=self.batch, group=self.ui_group,
        )
        self.item_label = pyglet.text.Label(
            "ITEM: —", x=18, y=43, font_size=10, weight=pyglet.text.Weight.BOLD,
            color=(235, 174, 242, 255), batch=self.batch, group=self.ui_group,
        )
        self.coin_label = pyglet.text.Label(
            "COINS 0", x=18, y=63, font_size=10,
            color=(246, 215, 86, 255), batch=self.batch, group=self.ui_group,
        )
        self.best_label = pyglet.text.Label(
            "", x=EngineGlobals.width - 18, y=63, anchor_x="right", font_size=9,
            color=(209, 223, 241, 255), batch=self.batch, group=self.ui_group,
        )
        self.labels.extend((self.class_label, self.item_label, self.coin_label, self.best_label))
        bar = pyglet.shapes.Rectangle(
            270, EngineGlobals.height - 86, 260, 4, color=(111, 120, 139),
            batch=self.batch, group=self.ui_group,
        )
        self.scenery_shapes.append(bar)
        self.progress_dots = []
        player_dot = pyglet.shapes.Circle(
            270, EngineGlobals.height - 84, 5, color=(247, 222, 94),
            batch=self.batch, group=self.ui_group,
        )
        self.progress_dots.append(player_dot)
        self.scenery_shapes.append(player_dot)
        for rival in self.rivals:
            dot = pyglet.shapes.Circle(
                270, EngineGlobals.height - 84, 3, color=rival.color,
                batch=self.batch, group=self.ui_group,
            )
            self.progress_dots.append(dot)
            self.scenery_shapes.append(dot)
        if self.play_mode == "TIME TRIAL":
            self.place_label.text = "TIME TRIAL"

    def _start_race(self):
        super()._start_race()
        self.coin_count = 0
        self.held_item = None
        self.item_box_cooldown = 0.0
        self.last_item_key = None
        self.coin_cooldown = 0.0
        self.last_coin_key = None
        self.shield_timer = 0.0
        self.invincible_timer = 0.0
        self.player_traps = []
        self.lap_started_at = 0.0
        self.current_best_lap = None
        self.item_label.text = "ITEM: —"
        self.coin_label.text = "COINS 0"
