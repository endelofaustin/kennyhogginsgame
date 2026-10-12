"""Content catalog for the standalone Super Ultra Kenny Kart game."""

from __future__ import annotations

import math
import random


DRIVERS = (
    {"name": "Kenny", "color": (239, 126, 146), "speed": 10, "accel": 10, "handling": 9, "boost": 10, "weight": 8, "art": "kennystance1.png"},
    {"name": "Theo", "color": (218, 161, 104), "speed": 8, "accel": 7, "handling": 6, "boost": 7, "weight": 10, "art": None},
    {"name": "Lucinda", "color": (186, 113, 214), "speed": 7, "accel": 10, "handling": 10, "boost": 8, "weight": 4, "art": "generated/lucinda.png"},
    {"name": "Jackie Flan", "color": (237, 153, 80), "speed": 9, "accel": 8, "handling": 9, "boost": 7, "weight": 5, "art": "generated/jackie_flan.png"},
    {"name": "Levod Burtim", "color": (91, 170, 224), "speed": 10, "accel": 6, "handling": 6, "boost": 9, "weight": 8, "art": "generated/levod_burtim.png"},
    {"name": "Pippi", "color": (242, 112, 177), "speed": 7, "accel": 10, "handling": 9, "boost": 10, "weight": 3, "art": "generated/pippi.png"},
    {"name": "Vesuvius", "color": (143, 82, 65), "speed": 10, "accel": 5, "handling": 5, "boost": 8, "weight": 10, "art": "generated/vesuvius.png"},
    {"name": "Charleston", "color": (92, 196, 145), "speed": 8, "accel": 8, "handling": 8, "boost": 8, "weight": 6, "art": "charleston.png"},
    {"name": "Doggy", "color": (198, 147, 86), "speed": 7, "accel": 10, "handling": 10, "boost": 8, "weight": 3, "art": "doggy.png"},
    {"name": "Mr. Spud", "color": (201, 146, 73), "speed": 8, "accel": 7, "handling": 7, "boost": 7, "weight": 9, "art": "mrspudl.png"},
    {"name": "McSwanson", "color": (248, 193, 91), "speed": 9, "accel": 8, "handling": 7, "boost": 9, "weight": 7, "art": "mcswanson-1.png"},
    {"name": "Frankenfire Kitty", "color": (122, 225, 134), "speed": 8, "accel": 9, "handling": 8, "boost": 9, "weight": 5, "art": "frankenfirekitty-1.png.png"},
    {"name": "Llama Solo", "color": (230, 220, 177), "speed": 8, "accel": 8, "handling": 9, "boost": 8, "weight": 6, "art": "llama_solo_right.png"},
    {"name": "Menacing Flower", "color": (247, 97, 183), "speed": 7, "accel": 9, "handling": 10, "boost": 9, "weight": 4, "art": "menancingflower.png"},
    {"name": "Sushi Roll", "color": (245, 236, 217), "speed": 8, "accel": 9, "handling": 8, "boost": 8, "weight": 5, "art": "sushiroll.png"},
    {"name": "Spikey", "color": (132, 182, 238), "speed": 9, "accel": 7, "handling": 8, "boost": 9, "weight": 7, "art": "spikey.png"},
    {"name": "Nirvana Fruit", "color": (229, 89, 93), "speed": 8, "accel": 10, "handling": 8, "boost": 10, "weight": 4, "art": "nirvana-fruit.png"},
    {"name": "Scythe", "color": (141, 143, 156), "speed": 10, "accel": 6, "handling": 7, "boost": 9, "weight": 8, "art": "scythe_thingy.png"},
    {"name": "Band Aid", "color": (236, 182, 155), "speed": 7, "accel": 9, "handling": 9, "boost": 8, "weight": 5, "art": "good_band_aid.png"},
    {"name": "Lighthouse", "color": (242, 228, 161), "speed": 9, "accel": 7, "handling": 7, "boost": 8, "weight": 8, "art": None},
    {"name": "Pearl", "color": (171, 225, 240), "speed": 8, "accel": 9, "handling": 10, "boost": 7, "weight": 4, "art": "reg_pearl.png"},
    {"name": "Rainbomb", "color": (113, 121, 242), "speed": 10, "accel": 8, "handling": 6, "boost": 10, "weight": 6, "art": None},
    {"name": "Toga Sister", "color": (244, 220, 184), "speed": 8, "accel": 8, "handling": 8, "boost": 8, "weight": 6, "art": None},
    {"name": "Ketchup King", "color": (224, 57, 49), "speed": 9, "accel": 7, "handling": 7, "boost": 10, "weight": 8, "art": None},
)


CUPS = (
    "HOG CUP", "NEON CUP", "TURBO CUP", "CHAOS CUP", "MOON CUP",
    "FIRE CUP", "WILD CUP", "ULTRA CUP", "GALAXY CUP", "LEGEND CUP",
)


THEMES = (
    {
        "name": "Midnight Metro", "landmark": "SKYLINE", "weather": "night",
        "sky_top": (12, 17, 45), "sky_bottom": (76, 40, 115),
        "ground": (25, 31, 54), "road": (52, 55, 68), "edge": (207, 82, 198),
        "accent": (63, 220, 255), "fog": (87, 75, 126),
    },
    {
        "name": "Lucinda Farm", "landmark": "SILO", "weather": "sunset",
        "sky_top": (78, 83, 143), "sky_bottom": (241, 143, 102),
        "ground": (71, 119, 61), "road": (79, 72, 65), "edge": (238, 202, 127),
        "accent": (126, 245, 175), "fog": (204, 151, 117),
    },
    {
        "name": "River Chrome", "landmark": "BRIDGE", "weather": "mist",
        "sky_top": (36, 77, 112), "sky_bottom": (116, 173, 191),
        "ground": (38, 92, 96), "road": (61, 70, 80), "edge": (95, 220, 233),
        "accent": (74, 224, 255), "fog": (125, 170, 183),
    },
    {
        "name": "Dojo Neon", "landmark": "TORII", "weather": "night",
        "sky_top": (27, 16, 53), "sky_bottom": (107, 35, 102),
        "ground": (63, 34, 66), "road": (57, 54, 66), "edge": (252, 67, 155),
        "accent": (75, 232, 255), "fog": (111, 53, 121),
    },
    {
        "name": "Rainbomb Orbit", "landmark": "PLANET", "weather": "space",
        "sky_top": (7, 8, 31), "sky_bottom": (30, 38, 83),
        "ground": (20, 25, 55), "road": (54, 60, 92), "edge": (133, 112, 255),
        "accent": (73, 233, 255), "fog": (43, 49, 95),
    },
    {
        "name": "Vesuvius Inferno", "landmark": "VOLCANO", "weather": "ash",
        "sky_top": (54, 26, 30), "sky_bottom": (188, 67, 44),
        "ground": (91, 48, 34), "road": (65, 59, 59), "edge": (255, 154, 65),
        "accent": (255, 92, 47), "fog": (146, 74, 55),
    },
    {
        "name": "Nevada Hyperway", "landmark": "MESA", "weather": "heat",
        "sky_top": (76, 103, 158), "sky_bottom": (242, 181, 111),
        "ground": (155, 117, 70), "road": (86, 76, 69), "edge": (243, 213, 149),
        "accent": (255, 188, 72), "fog": (204, 161, 107),
    },
    {
        "name": "Ketchup Industrial", "landmark": "FACTORY", "weather": "storm",
        "sky_top": (42, 32, 49), "sky_bottom": (107, 55, 67),
        "ground": (77, 44, 47), "road": (63, 59, 64), "edge": (228, 56, 57),
        "accent": (255, 99, 80), "fog": (107, 65, 75),
    },
    {
        "name": "Pippi Coastline", "landmark": "LIGHTHOUSE", "weather": "clear",
        "sky_top": (44, 109, 169), "sky_bottom": (144, 211, 226),
        "ground": (52, 125, 131), "road": (72, 77, 85), "edge": (236, 225, 167),
        "accent": (74, 228, 255), "fog": (154, 203, 211),
    },
    {
        "name": "Kenny Hyperdream", "landmark": "HOG", "weather": "aurora",
        "sky_top": (15, 17, 48), "sky_bottom": (61, 41, 111),
        "ground": (31, 38, 68), "road": (48, 51, 69), "edge": (241, 91, 176),
        "accent": (103, 242, 255), "fog": (75, 64, 122),
    },
)


SUFFIXES = ("Rush", "Circuit", "Run", "Pass", "Loop")
TAGLINES = (
    "Huge sweepers and glowing boost lanes.",
    "Long climbs, hard braking zones, and a cinematic finish.",
    "Fast technical corners with risky shortcut boosts.",
    "Big jumps, heavy traffic, and dangerous overdrive sections.",
    "A championship-length finale built for twelve racers.",
)


def _sections(seed: int, theme_index: int):
    rng = random.Random(seed * 997 + theme_index * 131)
    sections = []
    for i in range(14):
        length = rng.randint(12, 24)
        curve = rng.uniform(-0.055, 0.055)
        if i in (0, 7, 13):
            curve *= 0.25
        hill = rng.uniform(-0.022, 0.026)
        if theme_index == 4:
            hill *= 1.55
        if theme_index == 6:
            curve *= 0.78
        sections.append((length, round(curve, 4), round(hill, 4)))
    return tuple(sections)


def _feature_indices(seed: int, total_segments: int):
    rng = random.Random(4000 + seed * 73)
    choices = list(range(8, max(9, total_segments - 8)))
    rng.shuffle(choices)
    boosts = tuple(sorted(choices[:7]))
    ramps = tuple(sorted(choices[7:10]))
    hazards = tuple(sorted(choices[10:14]))
    energy = tuple(sorted(choices[14:17]))
    return boosts, ramps, hazards, energy


def _build_tracks():
    tracks = []
    for index in range(50):
        theme_index = index // 5
        theme = THEMES[theme_index]
        variation = index % 5
        sections = _sections(index + 1, theme_index)
        total_segments = sum(section[0] for section in sections)
        boosts, ramps, hazards, energy = _feature_indices(index, total_segments)
        name = f"{theme['name']} {SUFFIXES[variation]}"
        tracks.append({
            "index": index,
            "cup": CUPS[theme_index],
            "name": name,
            "tagline": TAGLINES[variation],
            "theme": theme,
            "sections": sections,
            "boosts": boosts,
            "ramps": ramps,
            "hazards": hazards,
            "energy": energy,
            "max_speed": 0.98 + theme_index * 0.006 + variation * 0.004,
            "grip": 1.04 - variation * 0.015 + (0.02 if theme_index in (2, 8) else 0.0),
            "fog_strength": 0.18 + theme_index * 0.015,
        })
    return tuple(tracks)


TRACKS = _build_tracks()
assert len(DRIVERS) == 24
assert len(TRACKS) == 50
assert len(CUPS) == 10
