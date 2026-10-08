"""Deluxe catalog/settings for 3D Reaching.

Extends the full 20-track championship to 40 tracks / 8 cups, exposes the
larger Kenny-world roster, adds difficulty plus 200 PIGS, and assigns the
repo's music compositions across the race catalog.
"""

import mode7_racing as base
from mode7_full_content import FULL_TRACKS as ORIGINAL_FULL_TRACKS


def _indices(pattern, fractions):
    total = max(1, sum(int(part[0]) for part in pattern))
    return tuple(sorted({
        max(0, min(total - 1, int((total - 1) * float(f))))
        for f in fractions
    }))


def _track(
    name, tagline, pattern, *,
    sky, ground, road, edge_a, edge_b, scenery,
    boost=(0.12, 0.42, 0.74), oil=(0.28, 0.63), ramp=(0.51,), mud=(),
    max_speed=1.0, grip=1.0, wind=0.0, fog=0, surface="ASPHALT",
    surface_drag=1.0, curve_force=1.0, jump_bonus=1.0, item_step=37,
    coin_step=23, ai_scale=1.0, music=None,
):
    track = base._track(
        name, tagline, pattern,
        sky=sky, ground=ground, road=road, edge_a=edge_a, edge_b=edge_b,
        boost=_indices(pattern, boost), oil=_indices(pattern, oil),
        ramp=_indices(pattern, ramp), mud=_indices(pattern, mud),
        scenery=scenery, max_speed=max_speed, grip=grip,
    )
    track.update({
        "wind": float(wind),
        "fog": int(fog),
        "surface": str(surface),
        "surface_drag": float(surface_drag),
        "curve_force": float(curve_force),
        "jump_bonus": float(jump_bonus),
        "item_step": max(17, int(item_step)),
        "coin_step": max(13, int(coin_step)),
        "ai_scale": float(ai_scale),
        "music": music,
    })
    return track


MUSIC_LIBRARY = (
    "rap1.wav",
    "sleeponit.wav",
    "stronglengthypunkbrawl.wav",
    "takingahike.wav",
    "downrightbirthright.wav",
    "workingwithmagic.wav",
    "LaLaLa.wav",
    "drugged_out.wav",
    "mixed_up_kenny.wav",
    "pantaloon.wav",
    "intro.wav",
)


EXTRA_CHARACTERS = (
    {"name": "Cardi", "color": (79, 151, 80), "art": "bosses/cardi_tree-1.png.png",
     "speed": 6, "accel": 5, "turn": 5, "weight": 10, "grip": 10, "boost": 5},
    {"name": "Pearl", "color": (226, 228, 235), "art": "pearled_out.png",
     "speed": 8, "accel": 9, "turn": 10, "weight": 2, "grip": 9, "boost": 8},
    {"name": "Pearly Paul", "color": (147, 102, 73), "art": "pearly_paul.png",
     "speed": 8, "accel": 7, "turn": 7, "weight": 7, "grip": 7, "boost": 8},
    {"name": "Mr. Omen", "color": (71, 59, 81), "art": "bosses/mr_omen.png",
     "speed": 9, "accel": 7, "turn": 8, "weight": 6, "grip": 8, "boost": 9},
    {"name": "Livia", "color": (239, 228, 201), "art": None,
     "speed": 8, "accel": 8, "turn": 9, "weight": 4, "grip": 9, "boost": 8},
    {"name": "Octavia", "color": (224, 209, 239), "art": None,
     "speed": 9, "accel": 7, "turn": 8, "weight": 5, "grip": 8, "boost": 9},
    {"name": "Claudia", "color": (230, 220, 187), "art": None,
     "speed": 7, "accel": 9, "turn": 9, "weight": 4, "grip": 10, "boost": 7},
    {"name": "Tomato Bully", "color": (211, 48, 43), "art": None,
     "speed": 7, "accel": 6, "turn": 6, "weight": 9, "grip": 7, "boost": 7},
)

_known = {c["name"] for c in base.CHARACTERS}
DELUXE_CHARACTERS = tuple(base.CHARACTERS) + tuple(
    c for c in EXTRA_CHARACTERS if c["name"] not in _known
)


DIFFICULTIES = (
    {"name": "CHILL", "ai": 0.90, "item_aggression": 0.75, "hazards": 0.75,
     "note": "Forgiving rivals and fewer surprise hazards."},
    {"name": "NORMAL", "ai": 1.00, "item_aggression": 1.00, "hazards": 1.00,
     "note": "The intended balanced championship."},
    {"name": "HARD", "ai": 1.08, "item_aggression": 1.20, "hazards": 1.15,
     "note": "Faster lines, more attacks, less room for errors."},
    {"name": "NIGHTMARE", "ai": 1.16, "item_aggression": 1.42, "hazards": 1.32,
     "note": "Maximum rival pressure and dense course trouble."},
)


SPEED_CLASSES = (
    {"name": "50cc", "speed": 0.88, "accel": 0.96, "ai": 0.90, "note": "RELAXED"},
    {"name": "100cc", "speed": 1.00, "accel": 1.00, "ai": 1.00, "note": "CLASSIC"},
    {"name": "150cc", "speed": 1.13, "accel": 1.05, "ai": 1.09, "note": "WILD"},
    {"name": "200 PIGS", "speed": 1.29, "accel": 1.12, "ai": 1.21, "note": "FASTEST"},
)


P = lambda *parts: tuple(parts)

DELUXE_TRACKS = (
    _track(
        "Cardi Canopy Clash", "A living forest road: narrow rhythm, roots, wind, and heavy grip.",
        P((16,0.00,0.012),(14,0.040,0.008),(12,-0.054,-0.004),(16,0.026,0.018),
          (12,-0.060,-0.012),(18,0.000,0.010),(14,0.047,0.000),(14,-0.043,-0.008),
          (20,0.000,0.004)),
        sky=(55,80,72), ground=(47,101,55), road=(73,76,68), edge_a=(192,215,153),
        edge_b=(93,139,75), scenery=(38,87,47), boost=(.18,.55,.86), oil=(.31,),
        ramp=(.43,.74), mud=(.10,.67), max_speed=.96, grip=1.08, wind=.0025,
        surface="ROOT ROAD", surface_drag=.997, curve_force=1.08, jump_bonus=1.05,
        item_step=43, coin_step=19, ai_scale=.98, music="takingahike.wav",
    ),
    _track(
        "Pearlworks Promenade", "Glossy pearl lanes with rapid chicanes and almost no weighty terrain.",
        P((20,0.00,0.000),(14,0.048,0.004),(14,-0.052,0.004),(18,0.000,0.006),
          (14,0.058,-0.004),(14,-0.056,0.000),(22,0.018,0.000),(18,-0.028,-0.006),
          (22,0.000,0.000)),
        sky=(100,119,145), ground=(194,205,214), road=(119,125,132), edge_a=(248,249,252),
        edge_b=(145,181,206), scenery=(160,180,193), boost=(.08,.29,.52,.77,.94),
        oil=(.38,.69), ramp=(.61,), max_speed=1.05, grip=1.06, surface="PEARL TILE",
        surface_drag=.9995, curve_force=.94, item_step=29, coin_step=17, ai_scale=1.02,
        music="LaLaLa.wav",
    ),
    _track(
        "Pearly Paul Espresso Express", "Coffee-shop sprint: acceleration zones, tight counters, messy spills.",
        P((12,0.00,0.000),(12,0.060,0.000),(10,-0.070,0.006),(12,0.065,-0.006),
          (10,-0.072,0.000),(14,0.035,0.008),(10,-0.060,0.000),(16,0.000,-0.008),
          (12,0.054,0.000),(16,-0.030,0.000)),
        sky=(76,59,53), ground=(126,91,65), road=(91,72,62), edge_a=(234,210,170),
        edge_b=(130,76,58), scenery=(99,69,53), boost=(.15,.33,.58,.82), oil=(.24,.49,.72),
        mud=(.40,.66), ramp=(.91,), max_speed=.97, grip=1.03, surface="CAFE FLOOR",
        curve_force=1.12, item_step=25, coin_step=23, ai_scale=1.03,
        music="pantaloon.wav",
    ),
    _track(
        "Mr. Omen Dollhouse Drive", "A foggy haunted circuit with blind crests and nasty late-apex turns.",
        P((18,0.00,0.015),(14,0.045,0.020),(12,-0.062,-0.025),(14,0.058,0.018),
          (12,-0.065,-0.012),(18,0.000,0.030),(14,0.052,-0.030),(16,-0.048,0.010),
          (18,0.000,-0.012)),
        sky=(38,31,53), ground=(62,54,69), road=(61,57,67), edge_a=(164,145,184),
        edge_b=(88,66,109), scenery=(50,42,62), boost=(.21,.63,.90), oil=(.13,.42,.79),
        ramp=(.52,), max_speed=.98, grip=.98, wind=-.0018, fog=95, surface="DOLLHOUSE WOOD",
        curve_force=1.11, item_step=31, coin_step=29, ai_scale=1.04,
        music="mixed_up_kenny.wav",
    ),
    _track(
        "Frankenfire Kitty Furnace", "Furnace straights, orange glow, ash patches, and explosive jumps.",
        P((22,0.00,0.004),(18,0.025,0.008),(16,-0.038,-0.004),(24,0.000,0.000),
          (16,0.052,0.008),(16,-0.050,-0.006),(22,0.020,0.000),(20,-0.030,0.004),
          (24,0.000,-0.004)),
        sky=(86,46,36), ground=(128,61,38), road=(72,65,61), edge_a=(248,147,64),
        edge_b=(184,45,33), scenery=(104,49,35), boost=(.06,.27,.49,.73,.92),
        oil=(.35,.81), ramp=(.18,.58,.88), mud=(.42,.68), max_speed=1.07, grip=.94,
        surface="HOT ASH", surface_drag=.995, jump_bonus=1.18, item_step=34, coin_step=21,
        ai_scale=1.04, music="stronglengthypunkbrawl.wav",
    ),
    _track(
        "Livia Lyric Lane", "Smooth musical arcs and forgiving cambers reward clean drift chains.",
        P((18,0.00,0.005),(20,0.025,0.006),(18,-0.028,-0.005),(20,0.032,0.004),
          (18,-0.030,0.000),(22,0.018,0.006),(20,-0.022,-0.004),(22,0.000,0.000)),
        sky=(92,72,106), ground=(158,137,102), road=(93,84,87), edge_a=(243,225,184),
        edge_b=(174,94,130), scenery=(118,94,95), boost=(.11,.39,.68,.91), oil=(.55,),
        ramp=(.80,), max_speed=1.02, grip=1.07, surface="MARBLE", curve_force=.92,
        item_step=41, coin_step=18, ai_scale=1.00, music="workingwithmagic.wav",
    ),
    _track(
        "Octavia Opera Orbit", "Long orbiting bends build speed until the final dangerous descent.",
        P((24,0.012,0.004),(24,0.022,0.010),(22,0.035,0.008),(20,0.048,-0.004),
          (22,-0.044,-0.012),(24,-0.026,-0.006),(28,0.000,0.000)),
        sky=(66,51,89), ground=(123,102,124), road=(78,70,84), edge_a=(221,202,238),
        edge_b=(141,91,172), scenery=(96,74,111), boost=(.08,.26,.44,.62,.84),
        oil=(.53,.75), ramp=(.67,.93), max_speed=1.08, grip=1.00, surface="OPERA STONE",
        curve_force=1.00, item_step=37, coin_step=20, ai_scale=1.05,
        music="downrightbirthright.wav",
    ),
    _track(
        "Claudia Chorus Cliffs", "Cliffside switchbacks, crosswind, and tiny recovery windows.",
        P((14,0.00,0.012),(12,0.062,0.010),(10,-0.074,-0.006),(12,0.070,0.008),
          (10,-0.078,-0.010),(14,0.058,0.006),(10,-0.068,0.000),(16,0.040,-0.008),
          (14,-0.052,0.000),(18,0.000,0.004)),
        sky=(78,86,112), ground=(103,101,86), road=(70,71,73), edge_a=(231,220,187),
        edge_b=(151,111,86), scenery=(83,83,76), boost=(.22,.61,.89), oil=(.34,.76),
        ramp=(.49,), max_speed=.95, grip=1.06, wind=.0045, surface="CLIFF ROAD",
        curve_force=1.16, item_step=45, coin_step=24, ai_scale=1.03,
        music="LaLaLa.wav",
    ),
    _track(
        "Tomato Bully Turnpike", "Sticky red lanes alternate with brutal boost straights.",
        P((20,0.00,0.000),(18,0.036,0.004),(16,-0.045,0.000),(24,0.000,0.000),
          (16,0.052,0.006),(16,-0.048,-0.004),(26,0.000,0.000),(18,0.030,0.000),
          (22,-0.024,0.000)),
        sky=(112,60,62), ground=(153,61,54), road=(88,70,69), edge_a=(249,190,156),
        edge_b=(181,44,43), scenery=(126,51,48), boost=(.05,.23,.51,.74,.95),
        oil=(.33,.84), mud=(.15,.16,.63,.64), ramp=(.43,.88), max_speed=1.06, grip=.93,
        surface="KETCHUP", surface_drag=.992, curve_force=1.04, item_step=27, coin_step=26,
        ai_scale=1.02, music="rap1.wav",
    ),
    _track(
        "Scytheworks Industrial Run", "Steel corridors, hard braking zones, and conveyor-like sweepers.",
        P((26,0.00,0.000),(14,0.055,0.000),(12,-0.064,0.004),(24,0.000,0.000),
          (14,-0.058,-0.004),(12,0.070,0.000),(28,0.000,0.002),(16,0.038,0.000),
          (24,-0.020,0.000)),
        sky=(67,73,78), ground=(83,88,84), road=(68,70,72), edge_a=(206,205,190),
        edge_b=(147,88,67), scenery=(62,67,66), boost=(.10,.38,.69,.91), oil=(.29,.58,.82),
        ramp=(.49,), max_speed=1.08, grip=.99, surface="STEEL", curve_force=1.08,
        item_step=35, coin_step=21, ai_scale=1.05, music="stronglengthypunkbrawl.wav",
    ),
    _track(
        "Bandage Backroad", "Soft shoulders, healing-white scenery, and deceptive off-camber bends.",
        P((18,0.00,0.006),(20,0.025,0.012),(16,-0.040,-0.016),(18,0.048,0.010),
          (18,-0.036,0.000),(20,0.000,-0.008),(20,0.030,0.004),(18,-0.028,0.000)),
        sky=(128,151,164), ground=(121,145,113), road=(104,108,107), edge_a=(245,245,237),
        edge_b=(196,95,95), scenery=(101,126,100), boost=(.17,.47,.79), oil=(.35,.66),
        ramp=(.57,), max_speed=.99, grip=1.02, wind=-.0012, surface="SOFT ROAD",
        surface_drag=.998, item_step=33, coin_step=18, ai_scale=.99, music="sleeponit.wav",
    ),
    _track(
        "Sushi Roll Speedway", "Fast clean banking with tiny oil windows and near-constant drafting.",
        P((30,0.010,0.000),(28,0.018,0.004),(26,-0.020,-0.004),(30,-0.012,0.000),
          (32,0.000,0.000),(28,0.016,0.000)),
        sky=(62,88,103), ground=(74,111,108), road=(76,84,84), edge_a=(232,224,188),
        edge_b=(83,148,152), scenery=(57,89,88), boost=(.08,.24,.41,.58,.75,.92),
        oil=(.34,.68), ramp=(), max_speed=1.12, grip=1.02, surface="BANKED ASPHALT",
        curve_force=.85, item_step=32, coin_step=16, ai_scale=1.07, music="pantaloon.wav",
    ),
    _track(
        "Rainbomb Zero-G Ring", "Huge rolling crests make half the lap feel airborne.",
        P((18,0.00,0.035),(16,0.028,0.040),(16,-0.034,-0.045),(18,0.000,0.052),
          (16,0.042,-0.040),(18,-0.045,0.032),(18,0.000,-0.038),(20,0.025,0.026)),
        sky=(17,20,55), ground=(32,36,72), road=(59,63,94), edge_a=(126,111,229),
        edge_b=(58,202,232), scenery=(37,41,83), boost=(.12,.37,.62,.87), oil=(.51,),
        ramp=(.18,.44,.71,.94), max_speed=1.07, grip=.98, wind=.003, surface="LOW-G",
        jump_bonus=1.45, item_step=39, coin_step=20, ai_scale=1.04,
        music="drugged_out.wav",
    ),
    _track(
        "K-Town Midnight Autobahn", "The widest-feeling course: enormous speed, gentle curves, sparse hazards.",
        P((36,0.000,0.000),(30,0.012,0.002),(32,-0.014,-0.002),(40,0.000,0.000),
          (28,0.018,0.002),(30,-0.016,0.000),(42,0.000,0.000)),
        sky=(29,39,62), ground=(43,70,65), road=(62,66,72), edge_a=(229,226,207),
        edge_b=(88,121,160), scenery=(38,60,59), boost=(.05,.19,.35,.52,.70,.87),
        oil=(.46,), ramp=(.77,), max_speed=1.16, grip=1.03, surface="AUTOBAHN",
        curve_force=.72, item_step=49, coin_step=15, ai_scale=1.09, music="rap1.wav",
    ),
    _track(
        "Trailer Park Thunderstorm", "Wet pavement, gusting wind, puddles, and lightning-fast recovery fights.",
        P((18,0.00,0.008),(16,0.038,0.012),(16,-0.044,-0.010),(20,0.020,0.000),
          (16,-0.052,0.008),(18,0.046,-0.006),(20,0.000,0.004),(18,-0.032,0.000)),
        sky=(45,52,69), ground=(91,87,72), road=(69,72,77), edge_a=(205,208,210),
        edge_b=(118,91,74), scenery=(69,72,66), boost=(.14,.48,.81), oil=(.25,.56,.72),
        mud=(.36,.65), ramp=(.90,), max_speed=.98, grip=.91, wind=-.0048, fog=45,
        surface="WET ASPHALT", surface_drag=.996, curve_force=1.12, item_step=26,
        coin_step=27, ai_scale=1.04, music="mixed_up_kenny.wav",
    ),
    _track(
        "Pompeii Ashfall Descent", "A long downhill volcanic rush where braking matters more than boosting.",
        P((20,0.00,-0.012),(20,0.022,-0.018),(16,0.045,-0.022),(16,-0.052,-0.018),
          (22,0.000,-0.020),(16,0.058,-0.012),(16,-0.060,-0.010),(24,0.000,-0.006)),
        sky=(82,55,48), ground=(111,65,45), road=(72,67,65), edge_a=(235,158,78),
        edge_b=(172,57,40), scenery=(88,54,43), boost=(.09,.38,.68), oil=(.29,.57,.82),
        mud=(.46,.75), ramp=(.20,.91), max_speed=1.10, grip=.95, fog=55, surface="ASH",
        surface_drag=.994, curve_force=1.10, jump_bonus=1.12, item_step=34, coin_step=24,
        ai_scale=1.06, music="downrightbirthright.wav",
    ),
    _track(
        "Pearl Reef Causeway", "A sea-blue causeway with narrow S-curves and endless coin lines.",
        P((22,0.00,0.004),(18,0.036,0.006),(18,-0.040,-0.006),(22,0.000,0.008),
          (18,0.044,0.000),(18,-0.046,-0.004),(24,0.012,0.000),(22,0.000,-0.004)),
        sky=(73,111,139), ground=(59,131,142), road=(79,91,97), edge_a=(221,233,223),
        edge_b=(73,172,190), scenery=(52,104,116), boost=(.16,.45,.74,.93), oil=(.31,.62),
        ramp=(.54,.85), max_speed=1.03, grip=1.01, wind=.002, surface="CAUSEWAY",
        item_step=38, coin_step=13, ai_scale=1.02, music="LaLaLa.wav",
    ),
    _track(
        "Hoggins Haunted Highway", "Dark, fog-thick, uneven, and built to make every silhouette suspicious.",
        P((16,0.00,0.020),(14,0.052,-0.018),(12,-0.066,0.026),(14,0.062,-0.022),
          (12,-0.072,0.018),(16,0.000,-0.028),(14,0.058,0.020),(14,-0.054,-0.014),
          (18,0.000,0.006)),
        sky=(24,28,38), ground=(47,52,48), road=(53,55,59), edge_a=(150,148,136),
        edge_b=(89,67,83), scenery=(39,43,42), boost=(.27,.72), oil=(.12,.39,.61,.84),
        ramp=(.50,), mud=(.31,.67), max_speed=.96, grip=.94, wind=.0037, fog=125,
        surface="HAUNTED ROAD", surface_drag=.994, curve_force=1.18, item_step=23,
        coin_step=31, ai_scale=1.07, music="intro.wav",
    ),
    _track(
        "Pantaloon Party Parkway", "Bright carnival pace: item boxes everywhere and forgiving giant corners.",
        P((24,0.00,0.000),(22,0.020,0.004),(22,-0.022,0.000),(26,0.014,0.004),
          (22,-0.018,-0.004),(28,0.000,0.000),(24,0.016,0.000)),
        sky=(103,68,118), ground=(138,104,86), road=(91,79,89), edge_a=(245,217,113),
        edge_b=(215,81,150), scenery=(111,77,101), boost=(.10,.32,.54,.78,.94),
        oil=(.43,), ramp=(.65,), max_speed=1.05, grip=1.04, surface="PARTY ROAD",
        curve_force=.86, item_step=19, coin_step=17, ai_scale=1.00, music="pantaloon.wav",
    ),
    _track(
        "Final Pig Pen 200", "The 200 PIGS showcase: tiny braking windows, extreme speed, every hazard family.",
        P((18,0.00,0.012),(14,0.064,0.014),(12,-0.076,-0.020),(14,0.072,0.018),
          (12,-0.082,-0.016),(20,0.000,0.024),(12,0.074,-0.022),(12,-0.078,0.018),
          (18,0.048,0.000),(14,-0.060,-0.012),(22,0.000,0.004)),
        sky=(44,27,67), ground=(92,57,78), road=(69,57,82), edge_a=(250,214,86),
        edge_b=(230,82,82), scenery=(78,48,91), boost=(.06,.21,.39,.58,.77,.94),
        oil=(.14,.32,.49,.69,.86), ramp=(.27,.63,.90), mud=(.44,.45,.73,.74),
        max_speed=1.13, grip=.89, wind=.0055, fog=28, surface="PIG PEN", surface_drag=.993,
        curve_force=1.24, jump_bonus=1.22, item_step=21, coin_step=29, ai_scale=1.12,
        music="rap1.wav",
    ),
)

DELUXE_TRACKS_ALL = tuple(ORIGINAL_FULL_TRACKS) + DELUXE_TRACKS
assert len(DELUXE_TRACKS_ALL) == 40

for _i, _track_def in enumerate(DELUXE_TRACKS_ALL):
    if not _track_def.get("music"):
        _track_def["music"] = MUSIC_LIBRARY[_i % len(MUSIC_LIBRARY)]
    _track_def.setdefault("wind", 0.0)
    _track_def.setdefault("fog", 0)
    _track_def.setdefault("surface", "ASPHALT")
    _track_def.setdefault("surface_drag", 1.0)
    _track_def.setdefault("curve_force", 1.0)
    _track_def.setdefault("jump_bonus", 1.0)
    _track_def.setdefault("item_step", 37)
    _track_def.setdefault("coin_step", 23)
    _track_def.setdefault("ai_scale", 1.0)

CUPS = (
    {"name": "BAT CUP", "tracks": (0, 1, 2, 3, 4)},
    {"name": "FIRE CUP", "tracks": (5, 6, 7, 8, 9)},
    {"name": "CHAOS CUP", "tracks": (10, 11, 12, 13, 14)},
    {"name": "DREAM CUP", "tracks": (15, 16, 17, 18, 19)},
    {"name": "TREE CUP", "tracks": (20, 21, 22, 23, 24)},
    {"name": "TOGA CUP", "tracks": (25, 26, 27, 28, 29)},
    {"name": "MIDNIGHT CUP", "tracks": (30, 31, 32, 33, 34)},
    {"name": "PIG CUP", "tracks": (35, 36, 37, 38, 39)},
)
