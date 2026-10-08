"""Full championship layer for the pseudo-3D 3D Reaching racing game.

This module deliberately builds on mode7_racing instead of duplicating its
projection/vehicle physics.  It expands the mode to a full cup racer with the
same broad content scale as an early-1990s console kart game: 20 tracks,
multiple cups/classes, items, standings, quick races, and time trials.
"""

import mode7_racing as base


def _indices(pattern, fractions):
    total = max(1, sum(int(part[0]) for part in pattern))
    return tuple(sorted({max(0, min(total - 1, int((total - 1) * f))) for f in fractions}))


def _full_track(
    name,
    tagline,
    pattern,
    *,
    sky,
    ground,
    road,
    edge_a,
    edge_b,
    scenery,
    boost=(0.12, 0.42, 0.74),
    oil=(0.28, 0.63),
    ramp=(0.51,),
    mud=(),
    max_speed=1.0,
    grip=1.0,
):
    return base._track(
        name,
        tagline,
        pattern,
        sky=sky,
        ground=ground,
        road=road,
        edge_a=edge_a,
        edge_b=edge_b,
        boost=_indices(pattern, boost),
        oil=_indices(pattern, oil),
        ramp=_indices(pattern, ramp),
        mud=_indices(pattern, mud),
        scenery=scenery,
        max_speed=max_speed,
        grip=grip,
    )


EXTRA_TRACKS = (
    _full_track(
        "Toga Sisters Colosseum",
        "Golden sweepers, rhythmic S-curves, and arena launch ramps.",
        ((20, 0.000, 0.004), (18, 0.028, 0.000), (18, -0.030, 0.006),
         (20, 0.042, 0.000), (18, -0.044, -0.006), (22, 0.000, 0.008),
         (20, -0.025, 0.000), (22, 0.032, 0.000), (20, 0.000, -0.006),
         (24, -0.018, 0.000)),
        sky=(93, 71, 97), ground=(169, 137, 84), road=(91, 82, 78),
        edge_a=(242, 221, 169), edge_b=(166, 68, 104), scenery=(119, 91, 73),
        boost=(0.10, 0.36, 0.66, 0.91), oil=(0.24, 0.57, 0.81),
        ramp=(0.45, 0.76), max_speed=1.01,
    ),
    _full_track(
        "Pippi Pier Afterdark",
        "Fast dockside straights with slick boards and huge water jumps.",
        ((24, 0.000, 0.000), (20, 0.022, 0.005), (18, -0.035, 0.000),
         (24, 0.000, 0.010), (18, 0.046, -0.006), (22, -0.030, 0.000),
         (24, 0.018, 0.004), (20, -0.042, 0.000), (26, 0.000, -0.004)),
        sky=(35, 64, 91), ground=(42, 105, 122), road=(72, 80, 88),
        edge_a=(225, 210, 157), edge_b=(66, 164, 196), scenery=(42, 78, 91),
        boost=(0.08, 0.31, 0.59, 0.86), oil=(0.21, 0.48, 0.78),
        ramp=(0.39, 0.70, 0.94), max_speed=1.04, grip=0.97,
    ),
    _full_track(
        "Jackie Flan Switchbacks",
        "Mountain hairpins built for perfect drift chains.",
        ((14, 0.000, 0.010), (14, 0.058, 0.010), (12, -0.064, 0.006),
         (14, 0.062, -0.004), (12, -0.068, 0.000), (14, 0.054, 0.006),
         (12, -0.060, -0.006), (16, 0.036, 0.000), (14, -0.052, 0.004),
         (18, 0.000, -0.008)),
        sky=(61, 72, 88), ground=(77, 103, 79), road=(68, 72, 72),
        edge_a=(220, 207, 181), edge_b=(190, 103, 71), scenery=(65, 85, 68),
        boost=(0.14, 0.47, 0.82), oil=(0.34, 0.68), ramp=(0.56,),
        max_speed=0.96, grip=1.07,
    ),
    _full_track(
        "Levod Lunar Labyrinth",
        "Cold blue maze corners where line choice beats bravery.",
        ((16, 0.000, 0.002), (14, 0.046, 0.006), (14, -0.052, -0.005),
         (16, 0.038, 0.008), (14, -0.060, 0.000), (16, 0.000, -0.010),
         (14, 0.055, 0.006), (14, -0.042, 0.000), (18, 0.026, -0.005),
         (18, -0.032, 0.000), (20, 0.000, 0.006)),
        sky=(27, 37, 69), ground=(52, 73, 103), road=(58, 66, 80),
        edge_a=(133, 194, 223), edge_b=(92, 94, 190), scenery=(45, 63, 91),
        boost=(0.18, 0.50, 0.88), oil=(0.27, 0.61, 0.76), ramp=(0.70,),
        max_speed=0.98, grip=1.04,
    ),
    _full_track(
        "Charleston Harbor Run",
        "Harbor lights, broad corners, and a clean high-speed rhythm.",
        ((22, 0.000, 0.000), (24, 0.020, 0.004), (20, 0.032, 0.000),
         (22, -0.026, -0.004), (26, 0.000, 0.006), (20, -0.034, 0.000),
         (24, 0.024, 0.002), (22, 0.038, 0.000), (26, -0.018, -0.004)),
        sky=(53, 78, 96), ground=(53, 110, 104), road=(73, 84, 87),
        edge_a=(236, 222, 178), edge_b=(66, 145, 165), scenery=(48, 85, 80),
        boost=(0.09, 0.30, 0.54, 0.79), oil=(0.43, 0.69), ramp=(0.63,),
        max_speed=1.04, grip=1.01,
    ),
    _full_track(
        "Doggy Dirt Dash",
        "Loose dirt, tiny jumps, and frantic acceleration battles.",
        ((20, 0.000, 0.004), (18, 0.034, 0.006), (18, -0.040, -0.004),
         (20, 0.026, 0.000), (18, -0.048, 0.006), (22, 0.000, -0.006),
         (18, 0.044, 0.004), (20, -0.030, 0.000), (22, 0.000, 0.002)),
        sky=(95, 92, 104), ground=(140, 103, 62), road=(104, 83, 60),
        edge_a=(226, 191, 129), edge_b=(160, 79, 53), scenery=(111, 82, 52),
        boost=(0.16, 0.49, 0.84), oil=(0.37,), ramp=(0.27, 0.58, 0.75),
        mud=(0.08, 0.09, 0.42, 0.43, 0.67, 0.68, 0.92), grip=0.90,
    ),
    _full_track(
        "Mr. Spud Garden GP",
        "Garden walls, sticky soil, and sneaky inside lines.",
        ((18, 0.000, 0.000), (18, 0.030, 0.004), (16, -0.042, 0.000),
         (20, 0.050, 0.006), (16, -0.046, -0.006), (22, 0.000, 0.000),
         (18, -0.034, 0.004), (18, 0.038, 0.000), (24, 0.000, -0.004)),
        sky=(80, 92, 81), ground=(89, 132, 70), road=(88, 78, 65),
        edge_a=(233, 213, 154), edge_b=(115, 153, 72), scenery=(72, 105, 59),
        boost=(0.20, 0.52, 0.89), oil=(0.31, 0.72), ramp=(0.61,),
        mud=(0.10, 0.11, 0.44, 0.45, 0.78, 0.79), grip=0.94,
    ),
    _full_track(
        "Bacon Belt Parkway",
        "A giant fast ring with traffic-lane boosts and late-braking bends.",
        ((30, 0.000, 0.000), (28, 0.016, 0.000), (26, 0.028, 0.003),
         (30, 0.000, -0.003), (26, -0.030, 0.000), (28, -0.018, 0.004),
         (32, 0.000, 0.000), (26, 0.022, -0.003), (32, 0.000, 0.000)),
        sky=(72, 68, 83), ground=(91, 111, 74), road=(76, 77, 80),
        edge_a=(239, 219, 174), edge_b=(183, 71, 71), scenery=(69, 81, 61),
        boost=(0.06, 0.23, 0.40, 0.59, 0.76, 0.92), oil=(0.35, 0.68),
        ramp=(0.50,), max_speed=1.08,
    ),
    _full_track(
        "Frozen Dog Park",
        "Ice-blue corners with almost no forgiveness for steering mistakes.",
        ((18, 0.000, 0.000), (18, 0.028, 0.004), (16, -0.038, 0.000),
         (20, 0.050, -0.004), (16, -0.056, 0.004), (18, 0.034, 0.000),
         (20, -0.046, -0.004), (18, 0.026, 0.000), (22, 0.000, 0.004)),
        sky=(87, 116, 143), ground=(157, 195, 202), road=(119, 137, 151),
        edge_a=(237, 248, 250), edge_b=(83, 147, 194), scenery=(127, 166, 179),
        boost=(0.12, 0.46, 0.80), oil=(0.29, 0.64), ramp=(0.55,),
        max_speed=1.00, grip=0.82,
    ),
    _full_track(
        "Quarry Thunder Run",
        "Dark quarry walls, steep crests, and explosive downhill speed.",
        ((20, 0.000, 0.018), (18, 0.028, 0.025), (18, -0.040, -0.030),
         (20, 0.000, 0.022), (18, 0.048, -0.020), (20, -0.050, 0.018),
         (20, 0.032, -0.026), (22, -0.022, 0.012), (24, 0.000, -0.008)),
        sky=(45, 48, 62), ground=(78, 76, 68), road=(67, 68, 71),
        edge_a=(199, 183, 145), edge_b=(120, 91, 58), scenery=(61, 60, 56),
        boost=(0.15, 0.43, 0.73, 0.91), oil=(0.33, 0.59), ramp=(0.25, 0.67),
        mud=(0.49, 0.50), max_speed=1.05, grip=0.96,
    ),
    _full_track(
        "Hoggins Highway",
        "The pure speed course: long straights, drafting, and nerve.",
        ((36, 0.000, 0.000), (28, 0.012, 0.000), (34, 0.000, 0.002),
         (26, -0.018, 0.000), (38, 0.000, -0.002), (28, 0.022, 0.000),
         (40, 0.000, 0.000)),
        sky=(42, 55, 82), ground=(62, 87, 70), road=(62, 68, 76),
        edge_a=(240, 230, 194), edge_b=(70, 138, 208), scenery=(47, 66, 57),
        boost=(0.08, 0.20, 0.36, 0.53, 0.70, 0.86), oil=(0.31, 0.63),
        ramp=(0.77,), max_speed=1.12, grip=1.0,
    ),
    _full_track(
        "Kenny Dreamway",
        "The finale: neon sky-road chaos with every skill tested at once.",
        ((16, 0.000, 0.020), (16, 0.050, 0.016), (14, -0.060, -0.024),
         (16, 0.064, 0.022), (14, -0.070, -0.016), (18, 0.000, 0.030),
         (14, 0.058, -0.030), (14, -0.064, 0.020), (18, 0.042, 0.000),
         (16, -0.052, -0.016), (20, 0.000, 0.008)),
        sky=(35, 22, 70), ground=(59, 38, 90), road=(66, 57, 93),
        edge_a=(244, 213, 94), edge_b=(85, 222, 224), scenery=(74, 49, 108),
        boost=(0.07, 0.25, 0.45, 0.65, 0.84), oil=(0.18, 0.37, 0.73),
        ramp=(0.31, 0.57, 0.91), mud=(0.49, 0.50), max_speed=1.09, grip=0.91,
    ),
)

FULL_TRACKS = tuple(base.TRACKS) + EXTRA_TRACKS
base.TRACKS = FULL_TRACKS

CUPS = (
    {"name": "BAT CUP", "tracks": (0, 1, 2, 3, 4)},
    {"name": "FIRE CUP", "tracks": (5, 6, 7, 8, 9)},
    {"name": "CHAOS CUP", "tracks": (10, 11, 12, 13, 14)},
    {"name": "DREAM CUP", "tracks": (15, 16, 17, 18, 19)},
)

SPEED_CLASSES = (
    {"name": "50cc", "speed": 0.88, "accel": 0.96, "ai": 0.90, "note": "RELAXED"},
    {"name": "100cc", "speed": 1.00, "accel": 1.00, "ai": 1.00, "note": "CLASSIC"},
    {"name": "150cc", "speed": 1.13, "accel": 1.05, "ai": 1.09, "note": "WILD"},
)

MODES = (
    ("GRAND PRIX", "Five-race cups, championship points, and trophies."),
    ("QUICK RACE", "Pick any of the 20 tracks and race immediately."),
    ("TIME TRIAL", "No rivals or items. Chase your best lap and total time."),
)

POINTS = (9, 6, 3, 1, 0, 0, 0, 0)

ITEM_TURBO = "TURBO"
ITEM_BUMPER = "BUMPER"
ITEM_OIL = "OIL CAN"
ITEM_SHIELD = "BAT SHIELD"
ITEM_FEATHER = "FEATHER"
ITEM_LIGHTNING = "LIGHTNING"
ITEM_STAR = "STAR"
ITEM_COIN = "COIN BAG"
ITEM_BOMB = "BOMB"
