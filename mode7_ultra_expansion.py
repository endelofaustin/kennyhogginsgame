"""Ultra Super expansion for the deluxe pseudo-3D Kenny kart racer.

Adds ten courses, six drivers, and a 12-racer road-racing field while
leaving the separate battle/free-roam modes at their authored sizes.
"""

import pyglet

import mode7_racing as base
import mode7_deluxe_content as deluxe_content
import mode7_full_content as full_content
import mode7_full_core as coremod
import mode7_full_flow as flowmod
from engineglobals import EngineGlobals


ULTRA_POINTS = (15, 12, 10, 8, 6, 5, 4, 3, 2, 1, 0, 0)

ULTRA_CHARACTERS = (
    {"name": "McSwanson", "color": (101, 142, 184), "art": "mcswanson-1.png",
     "speed": 8, "accel": 8, "turn": 7, "weight": 7, "grip": 8, "boost": 8},
    {"name": "Frankenfire Kitty", "color": (222, 101, 54), "art": "frankenfirekitty-1.png.png",
     "speed": 9, "accel": 8, "turn": 7, "weight": 5, "grip": 7, "boost": 10},
    {"name": "Llama Solo", "color": (210, 194, 145), "art": "llama_solo_right.png",
     "speed": 7, "accel": 9, "turn": 9, "weight": 4, "grip": 9, "boost": 8},
    {"name": "Menacing Flower", "color": (181, 84, 151), "art": "menancingflower.png",
     "speed": 6, "accel": 10, "turn": 10, "weight": 3, "grip": 10, "boost": 7},
    {"name": "Sushi Roll", "color": (229, 218, 189), "art": "sushiroll.png",
     "speed": 8, "accel": 9, "turn": 8, "weight": 5, "grip": 9, "boost": 9},
    {"name": "Spikey", "color": (115, 153, 91), "art": "spikey.png",
     "speed": 10, "accel": 6, "turn": 6, "weight": 9, "grip": 7, "boost": 8},
)

P = deluxe_content.P
T = deluxe_content._track

ULTRA_TRACKS = (
    T(
        "McSwanson Midnight Run",
        "Blue-hour city lanes, quick esses, and a huge final drafting straight.",
        P((22,0.000,0.002),(18,0.034,0.004),(16,-0.043,0.000),(24,0.015,0.005),
          (16,0.052,-0.005),(18,-0.047,0.002),(28,0.000,0.000),(20,-0.024,-0.004),
          (30,0.000,0.000)),
        sky=(35,52,82), ground=(54,77,71), road=(62,69,79), edge_a=(208,226,236),
        edge_b=(77,133,192), scenery=(45,65,67), boost=(.08,.31,.57,.79,.94),
        oil=(.24,.68), ramp=(.47,.86), max_speed=1.08, grip=1.01,
        surface="MIDNIGHT ASPHALT", curve_force=.98, item_step=31, coin_step=17,
        ai_scale=1.04, music="mixed_up_kenny.wav",
    ),
    T(
        "Llama Launch Canyon",
        "Canyon crests and repeated launch ramps reward fearless trick chains.",
        P((18,0.000,0.018),(16,0.031,0.026),(14,-0.044,-0.030),(20,0.000,0.035),
          (16,0.048,-0.018),(18,-0.052,0.024),(20,0.026,-0.028),(18,-0.030,0.020),
          (24,0.000,-0.010)),
        sky=(116,91,87), ground=(173,126,77), road=(100,83,70), edge_a=(239,207,151),
        edge_b=(176,91,56), scenery=(138,102,67), boost=(.14,.43,.76,.92),
        oil=(.35,), ramp=(.20,.51,.68,.86), mud=(.60,), max_speed=1.03, grip=.96,
        wind=.003, surface="CANYON ROAD", jump_bonus=1.24, item_step=38, coin_step=19,
        ai_scale=1.02, music="takingahike.wav",
    ),
    T(
        "Menacing Flower Maze",
        "A neon garden maze of linked hairpins, sticky soil, and tiny recovery zones.",
        P((12,0.000,0.002),(10,0.068,0.004),(10,-0.076,-0.004),(12,0.071,0.006),
          (10,-0.079,0.000),(12,0.064,-0.006),(10,-0.070,0.004),(14,0.052,0.000),
          (12,-0.058,-0.004),(18,0.000,0.000)),
        sky=(68,39,83), ground=(88,128,69), road=(72,67,77), edge_a=(228,126,201),
        edge_b=(94,211,130), scenery=(68,105,57), boost=(.19,.49,.82),
        oil=(.30,.73), ramp=(.58,), mud=(.11,.39,.66,.90), max_speed=.95, grip=1.09,
        surface="GARDEN STONE", curve_force=1.19, item_step=27, coin_step=21,
        ai_scale=1.05, music="workingwithmagic.wav",
    ),
    T(
        "Sushi Roll Circuit",
        "Clean technical arcs alternate with slippery kitchen-floor chicanes.",
        P((18,0.000,0.000),(16,0.046,0.003),(14,-0.054,0.002),(20,0.020,0.004),
          (14,0.061,-0.004),(14,-0.063,0.000),(22,0.000,0.006),(18,-0.035,-0.006),
          (22,0.028,0.000),(24,0.000,0.000)),
        sky=(80,105,119), ground=(170,178,151), road=(104,105,101), edge_a=(247,239,214),
        edge_b=(205,88,92), scenery=(130,145,128), boost=(.10,.34,.55,.78,.95),
        oil=(.26,.64,.84), ramp=(.45,), max_speed=1.05, grip=1.03,
        surface="KITCHEN TILE", surface_drag=.998, curve_force=1.03, item_step=29,
        coin_step=16, ai_scale=1.03, music="LaLaLa.wav",
    ),
    T(
        "Spikey Steelworks",
        "Industrial sweepers, steel ramps, and dangerous high-speed compression turns.",
        P((24,0.000,0.003),(20,0.026,0.010),(18,-0.038,-0.008),(24,0.000,0.012),
          (18,0.050,-0.010),(20,-0.047,0.006),(24,0.018,0.000),(18,-0.034,-0.004),
          (28,0.000,0.000)),
        sky=(58,63,72), ground=(83,82,77), road=(68,70,73), edge_a=(204,201,184),
        edge_b=(170,104,64), scenery=(69,68,66), boost=(.07,.28,.50,.72,.91),
        oil=(.37,.81), ramp=(.22,.61,.88), mud=(.45,), max_speed=1.09, grip=.97,
        surface="STEELWORKS", jump_bonus=1.12, item_step=34, coin_step=22,
        ai_scale=1.06, music="stronglengthypunkbrawl.wav",
    ),
    T(
        "Nirvana Fruit Freeway",
        "A bright orchard freeway built for top speed, slipstreams, and late braking.",
        P((34,0.000,0.000),(26,0.014,0.002),(28,0.026,0.000),(32,0.000,0.003),
          (24,-0.031,-0.003),(30,-0.016,0.002),(34,0.000,0.000),(26,0.022,0.000),
          (36,0.000,0.000)),
        sky=(83,118,151), ground=(100,145,73), road=(77,80,82), edge_a=(247,225,154),
        edge_b=(214,93,72), scenery=(76,118,61), boost=(.05,.18,.35,.52,.70,.86,.96),
        oil=(.42,.76), ramp=(.62,), max_speed=1.13, grip=1.00,
        surface="ORCHARD ASPHALT", curve_force=.88, item_step=35, coin_step=15,
        ai_scale=1.06, music="rap1.wav",
    ),
    T(
        "Scythe Storm Pass",
        "Rain-dark mountain switchbacks with fierce crosswind and blind crests.",
        P((14,0.000,0.016),(12,0.061,0.016),(10,-0.073,-0.020),(12,0.068,0.018),
          (10,-0.080,-0.012),(14,0.055,0.022),(12,-0.065,-0.022),(16,0.044,0.010),
          (14,-0.049,-0.008),(20,0.000,-0.004)),
        sky=(38,48,67), ground=(60,76,67), road=(61,65,70), edge_a=(188,205,211),
        edge_b=(82,108,134), scenery=(51,65,60), boost=(.17,.52,.87),
        oil=(.29,.68), ramp=(.41,.75), mud=(.59,), max_speed=.98, grip=.94,
        wind=-.005, fog=72, surface="WET MOUNTAIN", surface_drag=.994,
        curve_force=1.16, jump_bonus=1.10, item_step=33, coin_step=25,
        ai_scale=1.06, music="drugged_out.wav",
    ),
    T(
        "Band-Aid Backroads",
        "Bumpy rural lanes, patched corners, and constant acceleration battles.",
        P((18,0.000,0.006),(16,0.038,0.008),(16,-0.041,-0.006),(20,0.027,0.004),
          (16,-0.050,0.006),(20,0.000,-0.006),(18,0.046,0.004),(18,-0.034,0.000),
          (24,0.000,0.002)),
        sky=(105,109,117), ground=(139,115,77), road=(91,79,69), edge_a=(225,204,164),
        edge_b=(165,92,66), scenery=(111,91,65), boost=(.12,.38,.64,.89),
        oil=(.31,.72), ramp=(.25,.55,.82), mud=(.09,.47,.68), max_speed=1.01, grip=.95,
        surface="PATCHED ROAD", surface_drag=.996, curve_force=1.04, item_step=30,
        coin_step=20, ai_scale=1.02, music="sleeponit.wav",
    ),
    T(
        "Lighthouse Lightning Loop",
        "Coastal night racing with huge sweepers, sea wind, and lightning-fast boost lanes.",
        P((28,0.000,0.004),(24,0.021,0.006),(22,0.037,0.000),(26,-0.030,-0.006),
          (28,0.000,0.008),(22,-0.042,0.000),(26,0.029,0.003),(24,0.044,0.000),
          (30,-0.018,-0.004)),
        sky=(31,49,78), ground=(43,91,101), road=(67,76,82), edge_a=(226,224,199),
        edge_b=(66,158,198), scenery=(39,72,83), boost=(.06,.24,.43,.61,.79,.94),
        oil=(.34,.70), ramp=(.52,.85), max_speed=1.11, grip=1.00, wind=.0038,
        surface="COAST ROAD", curve_force=.94, item_step=36, coin_step=17,
        ai_scale=1.07, music="downrightbirthright.wav",
    ),
    T(
        "Kenny Hyperdream Finale",
        "The 50th course: neon crests, brutal esses, jumps, mud, oil, and maximum speed.",
        P((16,0.000,0.022),(14,0.057,0.020),(12,-0.069,-0.024),(14,0.071,0.024),
          (12,-0.078,-0.018),(18,0.000,0.032),(12,0.068,-0.030),(12,-0.071,0.022),
          (16,0.051,0.000),(14,-0.060,-0.018),(20,0.000,0.010)),
        sky=(29,18,67), ground=(54,32,86), road=(62,54,91), edge_a=(248,217,91),
        edge_b=(78,225,232), scenery=(71,43,108), boost=(.05,.19,.34,.51,.68,.83,.96),
        oil=(.14,.40,.75), ramp=(.27,.58,.90), mud=(.47,.64), max_speed=1.14, grip=.91,
        wind=.002, fog=36, surface="HYPERDREAM", surface_drag=.997, curve_force=1.14,
        jump_bonus=1.22, item_step=23, coin_step=13, ai_scale=1.10,
        music="intro.wav",
    ),
)


def _selection_character_grid(self):
    self._clear_selection()
    self.state = self.STATE_CHARACTER
    self._selection_header(
        "DRIVER SELECT",
        "24 DRIVERS • PICK A BUILD FOR SPEED, ACCELERATION, TURNING, WEIGHT, GRIP AND BOOST",
    )
    self.character_panels = []
    xs = (70, 202, 334, 466, 598, 730)
    ys = (432, 320, 208, 96)
    for index, character in enumerate(base.CHARACTERS):
        row, col = divmod(index, 6)
        if row >= len(ys):
            break
        x, y = xs[col], ys[row]
        panel = pyglet.shapes.Rectangle(
            x - 58, y - 43, 116, 90,
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
                sprite.scale = min(1.7, 34.0 / max(1.0, float(max(image.width, image.height))))
                sprite.x = x - sprite.width / 2
                sprite.y = y - sprite.height / 2 + 4
                self.selection_shapes.append(sprite)
                loaded = True
            except Exception:
                loaded = False
        if not loaded:
            self.selection_shapes.append(pyglet.shapes.Circle(
                x, y + 3, 17, color=character["color"],
                batch=self.batch, group=self.scenery_group,
            ))
        self.selection_labels.append(pyglet.text.Label(
            character["name"].upper(), x=x, y=y + 34, anchor_x="center",
            multiline=True, width=108, align="center", font_size=6.5,
            weight=pyglet.text.Weight.BOLD, color=(255, 255, 255, 255),
            batch=self.batch, group=self.ui_group,
        ))
        self.selection_labels.append(pyglet.text.Label(
            "S{} A{} T{} W{} G{} B{}".format(
                character["speed"], character["accel"], character["turn"],
                character["weight"], character["grip"], character["boost"],
            ),
            x=x, y=y - 31, anchor_x="center", font_size=5.5,
            color=(205, 219, 238, 255), batch=self.batch, group=self.ui_group,
        ))
    self.character_detail = pyglet.text.Label(
        "", x=EngineGlobals.width // 2, y=31, anchor_x="center", font_size=8,
        weight=pyglet.text.Weight.BOLD, color=(255, 222, 132, 255),
        batch=self.batch, group=self.ui_group,
    )
    self.selection_labels.append(self.character_detail)
    self._refresh_character_select()


def _selection_cup_grid(self):
    self._clear_selection()
    self.state = self.STATE_CUP
    self._selection_header("GRAND PRIX", "10 CUPS • 5 RACES EACH • 12 RACERS")
    self.cup_panels = []
    for i, cup in enumerate(coremod.CUPS):
        col, row = i % 4, i // 4
        x = 105 + col * 195
        y = (414, 268, 122)[row]
        panel = pyglet.shapes.Rectangle(
            x - 88, y - 52, 176, 104,
            color=(112, 123, 153) if i == self.selected_cup else (45, 51, 65),
            batch=self.batch, group=self.road_group,
        )
        self.selection_shapes.append(panel)
        self.cup_panels.append(panel)
        self.selection_labels.append(pyglet.text.Label(
            cup["name"], x=x, y=y + 35, anchor_x="center", font_size=11,
            weight=pyglet.text.Weight.BOLD, color=(255, 239, 165, 255),
            batch=self.batch, group=self.ui_group,
        ))
        names = [coremod.FULL_TRACKS[idx]["name"] for idx in cup["tracks"]]
        self.selection_labels.append(pyglet.text.Label(
            "\n".join(names), x=x, y=y + 17, anchor_x="center", anchor_y="top",
            multiline=True, width=166, align="center", font_size=5.5,
            color=(203, 218, 237, 255), batch=self.batch, group=self.ui_group,
        ))


def _selection_track_grid(self):
    self._clear_selection()
    self.state = self.STATE_TRACK
    self._selection_header("FREE RACE", "CHOOSE FROM ALL 50 DISTINCT TRACKS • 12-RACER GRID")
    self.track_panels = []
    tracks = coremod.FULL_TRACKS
    for index, track in enumerate(tracks):
        col, row = index % 5, index // 5
        x = 82 + col * 159
        y = 474 - row * 41
        panel = pyglet.shapes.Rectangle(
            x - 72, y - 17, 144, 34,
            color=(103, 114, 144) if index == self.selected_track else (43, 49, 63),
            batch=self.batch, group=self.road_group,
        )
        self.selection_shapes.append(panel)
        self.track_panels.append(panel)
        self.selection_labels.append(pyglet.text.Label(
            track["name"].upper(), x=x, y=y, anchor_x="center", anchor_y="center",
            multiline=True, width=136, align="center", font_size=5.0,
            weight=pyglet.text.Weight.BOLD, color=(255, 244, 204, 255),
            batch=self.batch, group=self.ui_group,
        ))
    self.track_detail = pyglet.text.Label(
        "", x=400, y=52, anchor_x="center", multiline=True, width=720,
        align="center", font_size=7.5, color=(203, 218, 237, 255),
        batch=self.batch, group=self.ui_group,
    )
    self.selection_labels.append(self.track_detail)
    self._refresh_track_select()


def _refresh_track_grid(self):
    for i, panel in enumerate(getattr(self, "track_panels", [])):
        panel.color = (103, 114, 144) if i == self.selected_track else (43, 49, 63)
    track = coremod.FULL_TRACKS[self.selected_track]
    cup_name = next(
        (cup["name"] for cup in coremod.CUPS if self.selected_track in cup["tracks"]), ""
    )
    self.track_detail.text = "{} • {} • {} • MUSIC {}".format(
        cup_name,
        track.get("surface", "ASPHALT"),
        track["tagline"],
        self._music_display(track.get("music")),
    )


def _begin_cup_12(self):
    self.gp_race = 0
    player = self._selected_profile()
    candidates = [c for c in base.CHARACTERS if c["name"] != player["name"]]
    self.rng.shuffle(candidates)
    self.gp_roster = [player] + candidates[:11]
    self.gp_points = {c["name"]: 0 for c in self.gp_roster}
    self.gp_history = []
    self.selected_track = coremod.CUPS[self.selected_cup]["tracks"][0]
    self._start_race()


def _spawn_rivals_12(self):
    if self.play_mode == "TIME TRIAL":
        self.rivals = []
        self.ai_shapes = []
        return

    if self.play_mode == "GRAND PRIX" and self.gp_roster:
        chosen = list(self.gp_roster[1:12])
    else:
        available = [c for c in base.CHARACTERS if c["name"] != self._selected_profile()["name"]]
        self.rng.shuffle(available)
        chosen = available[:11]

    self.rivals = []
    lane_grid = (-0.72, -0.24, 0.24, 0.72)
    ai_scale = self._class_def()["ai"] * self.track_def.get("ai_scale", 1.0)
    aggression = self._difficulty_def()["item_aggression"]
    cooldown_scale = 1.0 / max(0.5, aggression)

    for i, character in enumerate(chosen):
        row, slot = divmod(i, 4)
        rival = base.Rival(
            lane=lane_grid[slot],
            distance=92.0 + row * 92.0 + slot * 9.0,
            speed=(6.7 + character["speed"] * 0.17 + (i % 3) * 0.08) * ai_scale,
            color=character["color"],
            name=character["name"],
            weight=character["weight"],
        )
        rival.item_cooldown = max(70.0, (165.0 + i * 17.0) * cooldown_scale)
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


def _award_gp_points_12(self):
    order = self._race_order()
    for i, name in enumerate(order[:12]):
        if name in self.gp_points:
            self.gp_points[name] += ULTRA_POINTS[i]
    self.gp_history.append(tuple(order))
    return order


def _build_standings_12(self, final=False):
    self._clear_race()
    self._clear_selection()
    self.state = self.STATE_CUP_DONE if final else self.STATE_STANDINGS
    cup = coremod.CUPS[self.selected_cup]
    subtitle = "FINAL CHAMPIONSHIP • 12 RACERS" if final else "AFTER RACE {}/5 • 12 RACERS".format(self.gp_race + 1)
    self._selection_header(cup["name"], subtitle)
    standings = sorted(self.gp_points.items(), key=lambda kv: (-kv[1], kv[0]))

    for i, (name, points) in enumerate(standings):
        col, row = i // 6, i % 6
        x = 40 + col * 380
        y = 422 - row * 56
        is_player = name == self._selected_profile()["name"]
        panel = pyglet.shapes.Rectangle(
            x, y - 17, 340, 36,
            color=(106, 118, 151) if is_player else (44, 50, 63),
            batch=self.batch, group=self.road_group,
        )
        self.selection_shapes.append(panel)
        self.selection_labels.append(pyglet.text.Label(
            "{}. {}".format(i + 1, name.upper()), x=x + 16, y=y,
            anchor_y="center", font_size=9, weight=pyglet.text.Weight.BOLD,
            color=(255, 247, 211, 255), batch=self.batch, group=self.ui_group,
        ))
        self.selection_labels.append(pyglet.text.Label(
            "{} PTS".format(points), x=x + 324, y=y, anchor_x="right", anchor_y="center",
            font_size=9, color=(233, 216, 128, 255),
            batch=self.batch, group=self.ui_group,
        ))

    if final:
        champion = standings[0][0] if standings else self._selected_profile()["name"]
        prompt = "{} WINS THE CUP! • ENTER returns to mode select".format(champion.upper())
    else:
        next_track = coremod.FULL_TRACKS[cup["tracks"][self.gp_race + 1]]["name"]
        prompt = "ENTER next race: {}".format(next_track.upper())
    self.selection_labels.append(pyglet.text.Label(
        prompt, x=400, y=60, anchor_x="center", font_size=9,
        weight=pyglet.text.Weight.BOLD, color=(255, 223, 133, 255),
        batch=self.batch, group=self.ui_group,
    ))


def _finish_race_12(self):
    self.state = self.STATE_FINISH
    self.speed = 0.0
    total = len(self.rivals) + 1
    self.finish_place = self._place() if self.rivals else 1
    self.finish_panel.visible = True
    self.finish_title.text = "FINISH!"
    key = (self.selected_track, self.selected_class, self.selected_character)

    if self.play_mode == "TIME TRIAL":
        previous = self.best_times.get(key)
        is_best = previous is None or self.race_time < previous
        if is_best:
            self.best_times[key] = self.race_time
        self.finish_result.text = "{} • {:.2f}s{}".format(
            self._selected_profile()["name"],
            self.race_time / 60.0,
            " • NEW BEST!" if is_best else "",
        )
        self.finish_prompt.text = "ENTER retry • ESC main menu"
        return

    if self.play_mode == "GRAND PRIX":
        order = self._award_gp_points()
        place = order.index(self._selected_profile()["name"]) + 1
        self.finish_place = place
        points = ULTRA_POINTS[min(place - 1, len(ULTRA_POINTS) - 1)]
        self.finish_result.text = "RACE {}/5 • PLACE {}/{} • +{} PTS".format(
            self.gp_race + 1, place, total, points
        )
        self.finish_prompt.text = "ENTER championship standings"
        return

    self.finish_result.text = "{} finished {} of {}".format(
        self._selected_profile()["name"], self.finish_place, total
    )
    self.finish_prompt.text = "ENTER rematch • ESC main menu"


def install_ultra_super_expansion(deluxe_cls):
    """Install the 50-track/24-driver/12-racer layer before later modes subclass it."""
    import mode7_deluxe as deluxe_mod

    existing_names = {c["name"] for c in deluxe_content.DELUXE_CHARACTERS}
    characters = tuple(deluxe_content.DELUXE_CHARACTERS) + tuple(
        c for c in ULTRA_CHARACTERS if c["name"] not in existing_names
    )
    tracks = tuple(deluxe_content.DELUXE_TRACKS_ALL) + ULTRA_TRACKS
    if len(tracks) != 50:
        raise AssertionError("Ultra Super expansion must expose exactly 50 tracks")

    cups = tuple(deluxe_content.CUPS) + (
        {"name": "WILD CUP", "tracks": (40, 41, 42, 43, 44)},
        {"name": "ULTRA CUP", "tracks": (45, 46, 47, 48, 49)},
    )

    modes = tuple(
        (name, "Pick any of the 50 tracks and race against 11 rivals.")
        if name == "QUICK RACE" else (name, note)
        for name, note in tuple(full_content.MODES)
    )

    base.CHARACTERS = characters
    base.TRACKS = tracks

    deluxe_content.DELUXE_CHARACTERS = characters
    deluxe_content.DELUXE_TRACKS_ALL = tracks
    deluxe_content.CUPS = cups

    full_content.FULL_TRACKS = tracks
    full_content.CUPS = cups
    full_content.MODES = modes
    full_content.POINTS = ULTRA_POINTS

    coremod.FULL_TRACKS = tracks
    coremod.CUPS = cups
    coremod.MODES = modes
    coremod.POINTS = ULTRA_POINTS

    flowmod.FULL_TRACKS = tracks
    flowmod.CUPS = cups
    flowmod.MODES = modes
    flowmod.POINTS = ULTRA_POINTS

    deluxe_mod.DELUXE_CHARACTERS = characters
    deluxe_mod.DELUXE_TRACKS_ALL = tracks
    deluxe_mod.CUPS = cups

    original_build_mode_select = deluxe_cls._build_mode_select
    original_build_ui = deluxe_cls._build_ui
    original_update = deluxe_cls.update

    def build_mode_select(self):
        original_build_mode_select(self)
        if len(self.selection_labels) >= 2:
            self.selection_labels[1].text = (
                "50 TRACKS • 10 CUPS • 24 DRIVERS • 12 RACERS • GRAND PRIX / QUICK RACE / TIME TRIAL"
            )

    def build_ui(self):
        original_build_ui(self)
        if self.play_mode != "TIME TRIAL":
            self.place_label.text = "PLACE {}/{}".format(
                self._place(), len(self.rivals) + 1
            )

    def update(self, dt):
        original_update(self, dt)
        if (
            self.active
            and self.state == self.STATE_RACE
            and self.play_mode != "TIME TRIAL"
            and hasattr(self, "place_label")
        ):
            self.place_label.text = "PLACE {}/{}".format(
                self._place(), len(self.rivals) + 1
            )

    deluxe_cls._build_mode_select = build_mode_select
    deluxe_cls._build_character_select = _selection_character_grid
    deluxe_cls._build_cup_select = _selection_cup_grid
    deluxe_cls._build_track_select = _selection_track_grid
    deluxe_cls._refresh_track_select = _refresh_track_grid
    deluxe_cls._begin_cup = _begin_cup_12
    deluxe_cls._spawn_rivals = _spawn_rivals_12
    deluxe_cls._award_gp_points = _award_gp_points_12
    deluxe_cls._build_standings = _build_standings_12
    deluxe_cls._finish_race = _finish_race_12
    deluxe_cls._build_ui = build_ui
    deluxe_cls.update = update

    return deluxe_cls
