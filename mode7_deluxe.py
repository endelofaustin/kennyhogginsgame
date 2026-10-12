"""Deluxe 3D Reaching: 40 tracks, 8 cups, 18 drivers, difficulty, 200 PIGS, and Kenny music."""

import pyglet

import mode7_racing as base
import mode7_full_content as full_content
import mode7_full_core as coremod
import mode7_full_flow as flowmod
from engineglobals import EngineGlobals
from mode7_full_game import FullMode7Racing
from mode7_deluxe_content import (
    CUPS, DELUXE_CHARACTERS, DELUXE_TRACKS_ALL, DIFFICULTIES,
    MUSIC_LIBRARY, SPEED_CLASSES,
)

base.CHARACTERS = DELUXE_CHARACTERS
base.TRACKS = DELUXE_TRACKS_ALL
full_content.FULL_TRACKS = DELUXE_TRACKS_ALL
full_content.CUPS = CUPS
full_content.SPEED_CLASSES = SPEED_CLASSES
coremod.FULL_TRACKS = DELUXE_TRACKS_ALL
coremod.CUPS = CUPS
coremod.SPEED_CLASSES = SPEED_CLASSES
flowmod.FULL_TRACKS = DELUXE_TRACKS_ALL
flowmod.CUPS = CUPS
flowmod.SPEED_CLASSES = SPEED_CLASSES


class DeluxeMode7Racing(FullMode7Racing):
    """Top-level 3D Reaching game with separate difficulty and speed settings."""

    STATE_DIFFICULTY = "difficulty"

    def __init__(self, on_exit_to_menu=None):
        self.selected_difficulty = 1
        self.music_player = None
        self.music_index = 0
        self.music_name = ""
        super().__init__(on_exit_to_menu=on_exit_to_menu)

    def _build_mode_select(self):
        super()._build_mode_select()
        if len(self.selection_labels) >= 2:
            self.selection_labels[1].text = (
                "40 TRACKS • 8 CUPS • 18 DRIVERS • GRAND PRIX / QUICK RACE / TIME TRIAL"
            )

    def _build_difficulty_select(self):
        self._clear_selection()
        self.state = self.STATE_DIFFICULTY
        self._selection_header("DIFFICULTY", "RIVAL SKILL AND ITEM AGGRESSION")
        self.difficulty_panels = []
        for i, difficulty in enumerate(DIFFICULTIES):
            x = 105 + i * 197
            panel = pyglet.shapes.Rectangle(
                x - 82, 225, 164, 220,
                color=(112, 123, 153) if i == self.selected_difficulty else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.difficulty_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                difficulty["name"], x=x, y=392, anchor_x="center",
                font_size=18, weight=pyglet.text.Weight.BOLD,
                color=(255, 239, 165, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                "AI {}%\nITEMS {}%".format(
                    int(difficulty["ai"] * 100), int(difficulty["item_aggression"] * 100)
                ),
                x=x, y=340, anchor_x="center", multiline=True, width=145,
                align="center", font_size=9, color=(205, 220, 238, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                difficulty["note"], x=x, y=270, anchor_x="center", anchor_y="top",
                multiline=True, width=145, align="center", font_size=8,
                color=(190, 205, 226, 255), batch=self.batch, group=self.ui_group,
            ))

    def _refresh_difficulty_select(self):
        for i, panel in enumerate(self.difficulty_panels):
            panel.color = (112, 123, 153) if i == self.selected_difficulty else (45, 51, 65)

    def _build_class_select(self):
        self._clear_selection()
        self.state = self.STATE_CLASS
        self._selection_header("SPEED", "CHOOSE YOUR ENGINE — 200 PIGS IS THE FASTEST")
        self.class_panels = []
        for i, engine in enumerate(SPEED_CLASSES):
            x = 105 + i * 197
            panel = pyglet.shapes.Rectangle(
                x - 82, 225, 164, 220,
                color=(112, 123, 153) if i == self.selected_class else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.class_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                engine["name"], x=x, y=392, anchor_x="center",
                font_size=17 if engine["name"] == "200 PIGS" else 20,
                weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                engine["note"], x=x, y=350, anchor_x="center", font_size=11,
                color=(213, 226, 242, 255), batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                "PLAYER {}%\nRIVALS {}%\nACCEL {}%".format(
                    int(engine["speed"] * 100), int(engine["ai"] * 100),
                    int(engine["accel"] * 100),
                ),
                x=x, y=310, anchor_x="center", anchor_y="top", multiline=True,
                width=145, align="center", font_size=9,
                color=(196, 211, 232, 255), batch=self.batch, group=self.ui_group,
            ))

    def _refresh_class_select(self):
        for i, panel in enumerate(self.class_panels):
            panel.color = (112, 123, 153) if i == self.selected_class else (45, 51, 65)

    def _build_character_select(self):
        self._clear_selection()
        self.state = self.STATE_CHARACTER
        self._selection_header(
            "DRIVER SELECT",
            "KENNY-WORLD ROSTER • STATS CHANGE SPEED, ACCELERATION, TURNING, WEIGHT, GRIP AND BOOST",
        )
        self.character_panels = []
        xs = (70, 202, 334, 466, 598, 730)
        ys = (408, 270, 132)
        for index, character in enumerate(base.CHARACTERS):
            row, col = divmod(index, 6)
            if row >= len(ys):
                break
            x, y = xs[col], ys[row]
            panel = pyglet.shapes.Rectangle(
                x - 59, y - 56, 118, 116,
                color=(111, 122, 154) if index == self.selected_character else (47, 53, 66),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.character_panels.append(panel)
            loaded = False
            art = character.get("art")
            if art:
                try:
                    image = pyglet.resource.image(art)
                    sprite = pyglet.sprite.Sprite(img=image, batch=self.batch, group=self.scenery_group)
                    sprite.scale = min(2.0, 48.0 / max(1.0, float(max(image.width, image.height))))
                    sprite.x = x - sprite.width / 2
                    sprite.y = y - sprite.height / 2 + 6
                    self.selection_shapes.append(sprite)
                    loaded = True
                except Exception:
                    loaded = False
            if not loaded:
                self.selection_shapes.append(pyglet.shapes.Circle(
                    x, y + 5, 21, color=character["color"],
                    batch=self.batch, group=self.scenery_group,
                ))
            self.selection_labels.append(pyglet.text.Label(
                character["name"].upper(), x=x, y=y + 45, anchor_x="center",
                multiline=True, width=112, align="center", font_size=7,
                weight=pyglet.text.Weight.BOLD, color=(255, 255, 255, 255),
                batch=self.batch, group=self.ui_group,
            ))
            self.selection_labels.append(pyglet.text.Label(
                "S{} A{} T{}  W{} G{} B{}".format(
                    character["speed"], character["accel"], character["turn"],
                    character["weight"], character["grip"], character["boost"],
                ),
                x=x, y=y - 39, anchor_x="center", font_size=6,
                color=(205, 219, 238, 255), batch=self.batch, group=self.ui_group,
            ))
        self.character_detail = pyglet.text.Label(
            "", x=EngineGlobals.width // 2, y=50, anchor_x="center", font_size=9,
            weight=pyglet.text.Weight.BOLD, color=(255, 222, 132, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.selection_labels.append(self.character_detail)
        self._refresh_character_select()

    def _refresh_character_select(self):
        for i, panel in enumerate(self.character_panels):
            panel.color = (111, 122, 154) if i == self.selected_character else (47, 53, 66)
        character = base.CHARACTERS[self.selected_character]
        note = "PERFECT 10/10 CORE STATS — THE DREAM BUILD" if character["name"] == "Kenny" else "SPECIALIST BUILD"
        self.character_detail.text = "{} • {}".format(character["name"].upper(), note)

    def _build_cup_select(self):
        self._clear_selection()
        self.state = self.STATE_CUP
        self._selection_header("GRAND PRIX", "8 CUPS • 5 RACES EACH")
        self.cup_panels = []
        for i, cup in enumerate(CUPS):
            col, row = i % 4, i // 4
            x = 105 + col * 195
            y = 390 - row * 210
            panel = pyglet.shapes.Rectangle(
                x - 88, y - 78, 176, 154,
                color=(112, 123, 153) if i == self.selected_cup else (45, 51, 65),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.cup_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                cup["name"], x=x, y=y + 54, anchor_x="center", font_size=12,
                weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
                batch=self.batch, group=self.ui_group,
            ))
            names = [DELUXE_TRACKS_ALL[idx]["name"] for idx in cup["tracks"]]
            self.selection_labels.append(pyglet.text.Label(
                "\n".join(names), x=x, y=y + 32, anchor_x="center", anchor_y="top",
                multiline=True, width=164, align="center", font_size=6,
                color=(203, 218, 237, 255), batch=self.batch, group=self.ui_group,
            ))

    def _refresh_cup_select(self):
        for i, panel in enumerate(self.cup_panels):
            panel.color = (112, 123, 153) if i == self.selected_cup else (45, 51, 65)

    def _build_track_select(self):
        self._clear_selection()
        self.state = self.STATE_TRACK
        self._selection_header("FREE RACE", "CHOOSE FROM ALL 40 DISTINCT TRACKS")
        self.track_panels = []
        for index, track in enumerate(DELUXE_TRACKS_ALL):
            col, row = index % 5, index // 5
            x = 82 + col * 159
            y = 466 - row * 52
            panel = pyglet.shapes.Rectangle(
                x - 72, y - 19, 144, 40,
                color=(103, 114, 144) if index == self.selected_track else (43, 49, 63),
                batch=self.batch, group=self.road_group,
            )
            self.selection_shapes.append(panel)
            self.track_panels.append(panel)
            self.selection_labels.append(pyglet.text.Label(
                track["name"].upper(), x=x, y=y, anchor_x="center", anchor_y="center",
                multiline=True, width=136, align="center", font_size=5.5,
                weight=pyglet.text.Weight.BOLD, color=(255, 244, 204, 255),
                batch=self.batch, group=self.ui_group,
            ))
        self.track_detail = pyglet.text.Label(
            "", x=400, y=55, anchor_x="center", multiline=True, width=700,
            align="center", font_size=8, color=(203, 218, 237, 255),
            batch=self.batch, group=self.ui_group,
        )
        self.selection_labels.append(self.track_detail)
        self._refresh_track_select()

    def _refresh_track_select(self):
        for i, panel in enumerate(self.track_panels):
            panel.color = (103, 114, 144) if i == self.selected_track else (43, 49, 63)
        track = DELUXE_TRACKS_ALL[self.selected_track]
        cup_name = next((cup["name"] for cup in CUPS if self.selected_track in cup["tracks"]), "")
        self.track_detail.text = "{} • {} • {} • MUSIC {}".format(
            cup_name, track["surface"], track["tagline"], self._music_display(track.get("music")),
        )

    def _difficulty_def(self):
        return DIFFICULTIES[self.selected_difficulty]

    def _class_def(self):
        engine = dict(SPEED_CLASSES[self.selected_class])
        engine["ai"] *= self._difficulty_def()["ai"]
        return engine

    def _physics(self):
        physics = super()._physics()
        force = self.track_def.get("curve_force", 1.0)
        physics["steer"] *= 1.0 / max(0.75, force ** 0.20)
        physics["drift_steer"] *= 1.0 / max(0.75, force ** 0.14)
        return physics

    def _build_track_data(self):
        super()._build_track_data()
        step = self.track_def.get("item_step", 37)
        coin_step = self.track_def.get("coin_step", 23)
        offset = (self.selected_track * 11 + 7) % max(1, step)
        coin_offset = (self.selected_track * 5 + 3) % max(1, coin_step)
        hazard_mult = self._difficulty_def()["hazards"]
        for i, segment in enumerate(self.track):
            segment["item"] = self.play_mode != "TIME TRIAL" and i >= offset and (i - offset) % step == 0
            segment["coin"] = i >= coin_offset and (i - coin_offset) % coin_step == 0 and not segment["oil"] and not segment["mud"]
            if hazard_mult > 1.05:
                seed = (i + self.selected_track * 13) % 97
                if seed == 23 and not segment["ramp"]:
                    segment["oil"] = True
                if hazard_mult > 1.25 and seed == 61 and not segment["boost"]:
                    segment["mud"] = True

    def _spawn_rivals(self):
        super()._spawn_rivals()
        scale = self.track_def.get("ai_scale", 1.0)
        cooldown_scale = 1.0 / max(0.5, self._difficulty_def()["item_aggression"])
        for rival in self.rivals:
            rival.base_speed *= scale
            rival.speed *= scale
            rival.item_cooldown = max(70.0, getattr(rival, "item_cooldown", 180.0) * cooldown_scale)

    def _update_rivals(self, dt):
        super()._update_rivals(dt)
        extra = max(0.0, self._difficulty_def()["item_aggression"] - 1.0)
        if extra:
            for rival in self.rivals:
                rival.item_cooldown = max(0.0, getattr(rival, "item_cooldown", 0.0) - float(dt) * extra)

    def _track_interactions(self):
        super()._track_interactions()
        segment = self._segment_at(self.distance + 12.0)
        if segment["ramp"] and self.hop_timer > 0:
            self.hop_total = max(self.hop_total, 42.0 * self.track_def.get("jump_bonus", 1.0))
            self.hop_timer = min(self.hop_timer, self.hop_total)

    def _update_player(self, dt):
        super()._update_player(dt)
        if self.state != self.STATE_RACE:
            return
        drag = self.track_def.get("surface_drag", 1.0)
        if drag < 1.0 and self.invincible_timer <= 0:
            self.speed *= drag ** (float(dt) * 0.16)
        wind = self.track_def.get("wind", 0.0)
        if wind:
            self.player_lane += wind * min(13.0, abs(self.speed)) * float(dt) * 0.08
        force = self.track_def.get("curve_force", 1.0)
        if force != 1.0:
            curve = self._segment_at(self.distance + 80.0)["curve"]
            self.player_lane -= (force - 1.0) * curve * max(0.0, self.speed) * 0.10 * float(dt)
        self.player_lane = max(-1.43, min(1.43, self.player_lane))

    def _build_static_scene(self):
        super()._build_static_scene()
        fog = int(self.track_def.get("fog", 0))
        if fog:
            haze = pyglet.shapes.Rectangle(
                0, EngineGlobals.height * 0.47, EngineGlobals.width, EngineGlobals.height * 0.53,
                color=(142, 145, 158), batch=self.batch, group=self.bg_group,
            )
            haze.opacity = max(0, min(150, fog))
            self.scenery_shapes.append(haze)

    @staticmethod
    def _music_display(filename):
        if not filename:
            return "NONE"
        return filename.rsplit(".", 1)[0].replace("_", " ").upper()

    def _stop_race_music(self):
        if self.music_player is not None:
            try:
                self.music_player.pause()
                self.music_player.delete()
            except Exception:
                pass
            self.music_player = None

    def _play_music_file(self, filename):
        self._stop_race_music()
        if not filename:
            return
        try:
            source = pyglet.resource.media(filename, streaming=True)
            player = pyglet.media.Player()
            player.queue(source)
            try:
                player.loop = True
            except Exception:
                pass
            player.volume = 0.58
            player.play()
            self.music_player = player
            self.music_name = filename
        except Exception:
            self.music_player = None
            self.music_name = ""

    def _start_track_music(self):
        filename = self.track_def.get("music") or MUSIC_LIBRARY[self.selected_track % len(MUSIC_LIBRARY)]
        self.music_index = MUSIC_LIBRARY.index(filename) if filename in MUSIC_LIBRARY else 0
        self._play_music_file(filename)

    def _next_music(self):
        self.music_index = (self.music_index + 1) % len(MUSIC_LIBRARY)
        self._play_music_file(MUSIC_LIBRARY[self.music_index])
        if hasattr(self, "music_label"):
            self.music_label.text = "MUSIC {}".format(self._music_display(self.music_name))
        if hasattr(self, "mechanic_label"):
            self._show_mechanic("NOW PLAYING {}".format(self._music_display(self.music_name)), 55.0)

    def _build_ui(self):
        super()._build_ui()
        difficulty = self._difficulty_def()["name"]
        self.class_label.text = "{} • {} • {}".format(self.play_mode, self._class_def()["name"], difficulty)
        self.surface_label = pyglet.text.Label(
            "{} • {}".format(self.track_def.get("surface", "ASPHALT"), difficulty),
            x=EngineGlobals.width - 18, y=EngineGlobals.height - 72, anchor_x="right",
            font_size=8, color=(191, 208, 231, 255), batch=self.batch, group=self.ui_group,
        )
        self.music_label = pyglet.text.Label(
            "MUSIC {}".format(self._music_display(self.track_def.get("music"))),
            x=EngineGlobals.width // 2, y=20, anchor_x="center", font_size=8,
            color=(202, 215, 235, 255), batch=self.batch, group=self.ui_group,
        )
        self.help_label.text = "↑ accelerate  ↓ brake  ← → steer  SPACE drift/trick  D item  M next song  ESC menu"
        self.labels.extend((self.surface_label, self.music_label))

    def _start_race(self):
        super()._start_race()
        self._start_track_music()
        if hasattr(self, "music_label"):
            self.music_label.text = "MUSIC {}".format(self._music_display(self.music_name))

    def start(self):
        global_player = getattr(EngineGlobals, "audio_player", None)
        if global_player is not None:
            try:
                global_player.pause()
            except Exception:
                pass
        self.selected_difficulty = 1
        self.selected_class = 1
        super().start()

    def stop(self):
        self._stop_race_music()
        super().stop()
        global_player = getattr(EngineGlobals, "audio_player", None)
        if global_player is not None:
            try:
                global_player.play()
            except Exception:
                pass

    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return pyglet.event.EVENT_UNHANDLED
        enter = symbol in (pyglet.window.key.ENTER, pyglet.window.key.RETURN)
        if self.state == self.STATE_MODE:
            if symbol == pyglet.window.key.ESCAPE:
                self.stop()
                if self.on_exit_to_menu:
                    self.on_exit_to_menu()
            elif symbol in (pyglet.window.key.UP, pyglet.window.key.LEFT):
                self.selected_mode = (self.selected_mode - 1) % len(flowmod.MODES)
                self._refresh_mode_select()
            elif symbol in (pyglet.window.key.DOWN, pyglet.window.key.RIGHT):
                self.selected_mode = (self.selected_mode + 1) % len(flowmod.MODES)
                self._refresh_mode_select()
            elif enter:
                self.play_mode = flowmod.MODES[self.selected_mode][0]
                self._build_difficulty_select()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_DIFFICULTY:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_mode_select()
            elif symbol in (pyglet.window.key.LEFT, pyglet.window.key.UP):
                self.selected_difficulty = (self.selected_difficulty - 1) % len(DIFFICULTIES)
                self._refresh_difficulty_select()
            elif symbol in (pyglet.window.key.RIGHT, pyglet.window.key.DOWN):
                self.selected_difficulty = (self.selected_difficulty + 1) % len(DIFFICULTIES)
                self._refresh_difficulty_select()
            elif enter:
                self._build_class_select()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_CLASS:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_difficulty_select()
            elif symbol in (pyglet.window.key.LEFT, pyglet.window.key.UP):
                self.selected_class = (self.selected_class - 1) % len(SPEED_CLASSES)
                self._refresh_class_select()
            elif symbol in (pyglet.window.key.RIGHT, pyglet.window.key.DOWN):
                self.selected_class = (self.selected_class + 1) % len(SPEED_CLASSES)
                self._refresh_class_select()
            elif enter:
                self._build_character_select()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_CHARACTER:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_class_select()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_character = (self.selected_character - 1) % len(base.CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_character = (self.selected_character + 1) % len(base.CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_character = (self.selected_character - 6) % len(base.CHARACTERS)
                self._refresh_character_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_character = (self.selected_character + 6) % len(base.CHARACTERS)
                self._refresh_character_select()
            elif enter:
                if self.play_mode == "GRAND PRIX":
                    self._build_cup_select()
                else:
                    self._build_track_select()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_CUP:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_character_select()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_cup = (self.selected_cup - 1) % len(CUPS)
                self._refresh_cup_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_cup = (self.selected_cup + 1) % len(CUPS)
                self._refresh_cup_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_cup = (self.selected_cup - 4) % len(CUPS)
                self._refresh_cup_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_cup = (self.selected_cup + 4) % len(CUPS)
                self._refresh_cup_select()
            elif enter:
                self._begin_cup()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_TRACK:
            if symbol == pyglet.window.key.ESCAPE:
                self._build_character_select()
            elif symbol == pyglet.window.key.LEFT:
                self.selected_track = (self.selected_track - 1) % len(DELUXE_TRACKS_ALL)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.RIGHT:
                self.selected_track = (self.selected_track + 1) % len(DELUXE_TRACKS_ALL)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.UP:
                self.selected_track = (self.selected_track - 5) % len(DELUXE_TRACKS_ALL)
                self._refresh_track_select()
            elif symbol == pyglet.window.key.DOWN:
                self.selected_track = (self.selected_track + 5) % len(DELUXE_TRACKS_ALL)
                self._refresh_track_select()
            elif enter:
                self._start_race()
            return pyglet.event.EVENT_HANDLED
        if self.state == self.STATE_RACE and symbol == pyglet.window.key.M:
            self._next_music()
            return pyglet.event.EVENT_HANDLED
        return super().on_key_press(symbol, modifiers)
