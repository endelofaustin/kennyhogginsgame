"""World data for Get Lost Mode, the free-roam Mode-7 Kenny sandbox."""

GET_LOST_ENTRY = (
    "GET LOST MODE",
    "Free-roam Kenny sandbox: huge map, roads, mountains, secrets, jumps, and encounters.",
)

WORLD_W = 12000.0
WORLD_H = 9000.0
START_SPAWN = (6000.0, 4500.0, 0.0)

ROAD_COLORS = {
    "asphalt": (76, 78, 84),
    "dirt": (121, 91, 61),
    "farm": (96, 82, 67),
    "mountain": (82, 82, 79),
    "neon": (73, 66, 91),
    "lava": (83, 67, 62),
    "pier": (111, 94, 72),
    "moon": (70, 76, 103),
}

ROAD_SEGMENTS = []


def _path(name, points, width=180.0, kind="asphalt"):
    color = ROAD_COLORS[kind]
    for a, b in zip(points, points[1:]):
        ROAD_SEGMENTS.append({
            "name": name,
            "x1": float(a[0]), "z1": float(a[1]),
            "x2": float(b[0]), "z2": float(b[1]),
            "width": float(width), "kind": kind, "color": color,
        })


_path("Hoggins Highway", ((450, 4500), (2500, 4500), (4300, 4420), (6000, 4500),
                           (7700, 4580), (9600, 4500), (11550, 4500)), 220)
_path("North Spine", ((6000, 600), (6000, 1800), (5900, 3000), (6000, 4500),
                       (6100, 6100), (6000, 8200)), 200)
_path("Lucinda Farm Loop", ((1600, 5100), (950, 6100), (1500, 7300), (2850, 7550),
                             (3650, 6800), (3250, 5600), (1600, 5100)), 165, "farm")
_path("Theo Dustway", ((650, 1100), (1700, 1250), (2650, 1800), (3050, 2850),
                        (2500, 3650), (1200, 3400), (650, 2400), (650, 1100)), 190, "dirt")
_path("River Road", ((7200, 1000), (8200, 650), (9500, 900), (10800, 1650),
                      (11300, 2800), (10600, 3500), (9200, 3300), (8000, 2600),
                      (7200, 1000)), 175, "pier")
_path("Vesuvius Fire Road", ((8200, 5200), (9000, 5550), (9850, 6200), (10450, 7100),
                              (10850, 8100)), 165, "lava")
_path("Pigback Pass", ((6500, 5200), (7000, 5900), (7350, 6750), (7900, 7350),
                        (8600, 7800), (9400, 8200)), 150, "mountain")
_path("Moon Road", ((4200, 6900), (4700, 7600), (5400, 8150), (6400, 8350),
                     (7100, 8000)), 180, "moon")
_path("Bat City Ring", ((4700, 3500), (5300, 3050), (6150, 3000), (6900, 3450),
                         (7200, 4250), (6900, 5100), (6100, 5450), (5200, 5200),
                         (4700, 4500), (4700, 3500)), 185, "neon")
_path("Ketchup Cutoff", ((3000, 2850), (3900, 3300), (4700, 3500)), 145, "lava")
_path("Doggy Forest Road", ((3250, 5600), (4200, 5750), (5000, 6200), (5150, 7000)), 150, "dirt")
_path("Spud Scenic Route", ((6100, 6100), (6800, 6400), (7350, 6750)), 145, "mountain")
_path("Lost Causeway", ((7200, 4300), (8200, 3950), (9200, 3850), (10600, 3500)), 160, "pier")
_path("South Service Road", ((2500, 3650), (3600, 3950), (4700, 4500)), 150, "dirt")

REGIONS = (
    {"name": "THEO DESERT", "rect": (0, 0, 3600, 4200), "ground": (151, 116, 73),
     "offroad": 0.968, "music": "sleeponit.wav"},
    {"name": "LUCINDA FARMLANDS", "rect": (0, 4200, 4000, 4800), "ground": (84, 122, 66),
     "offroad": 0.973, "music": "workingwithmagic.wav"},
    {"name": "BAT CITY", "rect": (4000, 2500, 3600, 3500), "ground": (57, 61, 73),
     "offroad": 0.978, "music": "rap1.wav"},
    {"name": "DOGGY WOODS", "rect": (3500, 5600, 2200, 2600), "ground": (55, 94, 61),
     "offroad": 0.965, "music": "takingahike.wav"},
    {"name": "MOON WEIRD ZONE", "rect": (4200, 6800, 3600, 2200), "ground": (62, 69, 96),
     "offroad": 0.985, "music": "LaLaLa.wav"},
    {"name": "RIVER & PIERS", "rect": (7600, 0, 4400, 4300), "ground": (55, 105, 105),
     "offroad": 0.969, "music": "mixed_up_kenny.wav"},
    {"name": "VESUVIUS COUNTRY", "rect": (8000, 4300, 4000, 4600), "ground": (105, 57, 42),
     "offroad": 0.958, "music": "downrightbirthright.wav"},
    {"name": "PIGBACK MOUNTAINS", "rect": (5700, 5600, 3500, 3400), "ground": (79, 87, 73),
     "offroad": 0.955, "music": "stronglengthypunkbrawl.wav"},
)

MOUNTAINS = (
    (6900, 6750, 620, 730, "MOUNT SPUD"),
    (7700, 7200, 760, 910, "PIGBACK PEAK"),
    (8550, 7600, 680, 820, "MOUNT GLURK"),
    (9350, 8100, 720, 960, "THE BIG HOG"),
    (10400, 7250, 660, 840, "VESUVIUS SHOULDER"),
    (10950, 7900, 560, 700, "ASH TOOTH"),
    (5450, 7900, 500, 560, "MOON MOUND"),
    (4650, 7350, 440, 500, "LUCINDA'S HILL"),
    (3700, 6500, 480, 520, "DOGGY RIDGE"),
    (2500, 6900, 420, 480, "FARM LOOKOUT"),
    (9800, 5600, 510, 610, "KETCHUP CRAG"),
    (11400, 6200, 460, 530, "LAST MOUNTAIN"),
)

RAMP_SITES = (
    (2350, 4500, 95, 1.00, "HIGHWAY HOG HOP"),
    (5550, 4500, 100, 1.15, "BAT CITY LAUNCH"),
    (6900, 5100, 90, 1.05, "RING ROAD POP"),
    (1180, 6100, 90, 1.00, "FARM HAY RAMP"),
    (2850, 1800, 100, 1.20, "THEO DUST JUMP"),
    (8450, 700, 110, 1.28, "PIER GAP"),
    (10300, 3200, 95, 1.15, "RIVER DOCK JUMP"),
    (9050, 5800, 105, 1.22, "FIRE ROAD KICKER"),
    (7350, 6750, 90, 1.30, "PIGBACK LEDGE"),
    (5300, 8050, 105, 1.35, "MOON LAUNCH"),
    (4200, 5750, 90, 1.00, "DOGGY LOG"),
    (3900, 3300, 85, 1.05, "KETCHUP CAP"),
)

BOOST_PADS = (
    (1500, 4500, 100, 1.0), (3600, 4450, 100, 1.0), (7600, 4560, 100, 1.0),
    (10100, 4500, 110, 1.1), (6000, 2400, 100, 1.0), (6000, 6900, 100, 1.0),
    (1800, 1250, 90, 1.0), (2600, 7200, 90, 1.0), (9600, 900, 95, 1.0),
    (10050, 6500, 100, 1.1), (7900, 7350, 95, 1.05), (4700, 7600, 95, 1.05),
)

HAZARD_ZONES = (
    {"x": 1550, "z": 2500, "radius": 270, "kind": "mud", "name": "THEO'S MUD HOLE"},
    {"x": 2450, "z": 6500, "radius": 230, "kind": "mud", "name": "LUCINDA'S POND"},
    {"x": 10150, "z": 2250, "radius": 340, "kind": "water", "name": "DEEP RIVER"},
    {"x": 9550, "z": 6900, "radius": 260, "kind": "lava", "name": "LAVA PUDDLE"},
    {"x": 5200, "z": 7600, "radius": 250, "kind": "moon", "name": "LOW-GRAVITY CRATER"},
    {"x": 6600, "z": 3650, "radius": 180, "kind": "oil", "name": "BAT OIL SPILL"},
)

PORTALS = (
    ((4700, 8150), (10900, 1700), "MOON-TO-RIVER WORMHOLE"),
    ((900, 850), (11100, 8200), "ABSOLUTELY BAD IDEA PORTAL"),
    ((5100, 3200), (6650, 5200), "BAT CITY SHORTCUT"),
)

LANDMARKS = (
    {"x": 1150, "z": 1650, "name": "THEO'S MEGA TRAILER", "kind": "trailer",
     "text": "Somehow the trailer has three chimneys and no visible door."},
    {"x": 1780, "z": 6850, "name": "LUCINDA'S MOON BARN", "kind": "barn",
     "text": "A barn with a satellite dish pointed directly at the moon."},
    {"x": 10450, "z": 1350, "name": "VAN DOWN BY THE RIVER", "kind": "van",
     "text": "The van is still here. Nobody knows how it passed inspection."},
    {"x": 6550, "z": 3900, "name": "GIANT KETCHUP BOTTLE", "kind": "ketchup",
     "text": "It is much too large and faintly warm."},
    {"x": 4200, "z": 6400, "name": "DOGGY'S BONE THRONE", "kind": "bone",
     "text": "A majestic throne made from suspiciously clean cartoon bones."},
    {"x": 7600, "z": 6050, "name": "SPUDHENGE", "kind": "spud",
     "text": "Potatoes arranged with astronomical precision."},
    {"x": 4950, "z": 8350, "name": "THE TINY MOON", "kind": "moon",
     "text": "A moon on a stick. It hums when Kenny drives past."},
    {"x": 11200, "z": 7300, "name": "FLOATING BATHTUB", "kind": "tub",
     "text": "A bathtub hangs ten feet above the ash. No explanation is offered."},
    {"x": 9050, "z": 3750, "name": "TOGA SISTERS ROADSIDE CHOIR", "kind": "toga",
     "text": "Three singers perform for traffic that does not exist."},
    {"x": 7350, "z": 3350, "name": "BATMOBILE MUSEUM OF BATMOBILES", "kind": "bat",
     "text": "Every exhibit appears to be the exact car Kenny is driving."},
    {"x": 3400, "z": 5050, "name": "CARDI TREE RADIO", "kind": "tree",
     "text": "The tree broadcasts weather reports from 1987."},
    {"x": 8350, "z": 8350, "name": "PIG UFO LANDING SITE", "kind": "ufo",
     "text": "Circular tire tracks surround a single unopened can of beans."},
)

ENCOUNTERS = (
    {"name": "Theo", "x": 1300, "z": 1850, "color": (213, 164, 114),
     "dialogue": ("Kenny. You found the trailer. That was the easy part.",
                  "Do not ask why the road goes through the cactus.",
                  "Want to try the Theo Dust Dash?"),
     "challenge": {"name": "THEO DUST DASH", "time": 42,
                   "points": ((1700, 1250), (2650, 1800), (3050, 2850), (2500, 3650))}},
    {"name": "Lucinda", "x": 1750, "z": 7050, "color": (175, 116, 189),
     "dialogue": ("The cows are fine. The moon barn is less fine.",
                  "I put ramps in the hay road because normal roads are boring.",
                  "Race the farm loop if you think the Batmobile can handle mud."),
     "challenge": {"name": "MOON BARN LOOP", "time": 48,
                   "points": ((950, 6100), (1500, 7300), (2850, 7550), (3650, 6800))}},
    {"name": "Doggy", "x": 4300, "z": 6250, "color": (188, 141, 94),
     "dialogue": ("BARK.", "Doggy points toward the Bone Throne with absolute seriousness.",
                  "BARK BARK. This appears to mean: jump the log."),
     "challenge": None},
    {"name": "Mr. Spud", "x": 7250, "z": 6350, "color": (185, 139, 83),
     "dialogue": ("The mountains remember every missed turn.",
                  "Spudhenge points at something. Possibly lunch.",
                  "The highest road is not the fastest road."),
     "challenge": None},
    {"name": "Pippi", "x": 9050, "z": 1250, "color": (228, 130, 173),
     "dialogue": ("The pier jump is completely safe if you don't think about it.",
                  "You should absolutely think about it.",
                  "Go hit every dock marker before the timer quits."),
     "challenge": {"name": "PIPPI PIER PANIC", "time": 45,
                   "points": ((8450, 700), (9500, 900), (10800, 1650), (10600, 3500))}},
    {"name": "Jackie Flan", "x": 8000, "z": 7450, "color": (215, 154, 91),
     "dialogue": ("These switchbacks are beautiful if you survive them.",
                  "Don't brake at the cliff. Brake before the cliff.",
                  "Meet me at the top."),
     "challenge": {"name": "PIGBACK CLIMB", "time": 52,
                   "points": ((7350, 6750), (7900, 7350), (8600, 7800), (9400, 8200))}},
    {"name": "Cardi", "x": 3550, "z": 6100, "color": (79, 151, 80),
     "dialogue": ("The radio says rain. The sky says no.",
                  "One of them is lying.",
                  "If you find the golden pig behind the tree, it was always yours."),
     "challenge": None},
    {"name": "Toga Sisters", "x": 9150, "z": 3900, "color": (230, 220, 187),
     "dialogue": ("Livia: We rehearse beside the highway now.",
                  "Octavia: The acoustics are terrible.",
                  "Claudia: Kenny, please honk on the downbeat."),
     "challenge": None},
)

SECRETS = (
    (850, 700, "TINY TRAILER", "A trailer smaller than Kenny's front tire."),
    (2250, 3350, "KETCHUP GEYSER", "The ground periodically smells like fries."),
    (3150, 8050, "THE COW THAT KNOWS", "The cow stares directly at the player, not Kenny."),
    (4250, 8500, "MOON PARKING METER", "It accepts no known currency."),
    (5550, 2650, "BAT CITY BASEMENT ROAD", "A road sign points down. There is no down."),
    (6700, 5700, "SPUD TUNNEL", "The tunnel is painted on a boulder. It still works emotionally."),
    (7450, 8650, "SNOWLESS SKI LIFT", "The lift runs over bare rock and one confused pig."),
    (8750, 2500, "RIVER PHONE BOOTH", "The phone rings only when nobody is nearby."),
    (9900, 4800, "THE ASH SNOWMAN", "Three volcanic rocks wearing a scarf."),
    (11250, 5250, "NO ROAD ROAD", "A perfect road sign standing in complete wilderness."),
    (11600, 8300, "END OF THE WORLD BENCH", "The bench faces the map boundary with confidence."),
    (6200, 7350, "PIG SIGNAL", "A bat signal, except it is unmistakably a pig."),
)

GOLDEN_PIGS = (
    (700, 1500), (1100, 3650), (900, 6500), (2100, 7900), (3200, 6100), (3850, 8350),
    (4500, 5300), (4300, 2900), (5250, 3800), (5950, 2500), (6450, 5100), (6750, 7350),
    (7450, 5900), (8050, 8300), (8650, 3400), (8450, 1200), (9350, 1900), (10350, 3200),
    (11200, 1900), (11600, 4100), (10600, 5600), (10200, 7900), (9000, 8650), (5800, 8650),
)

assert len(GOLDEN_PIGS) == 24
assert len(ENCOUNTERS) == 8
assert len(SECRETS) == 12
