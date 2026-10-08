"""Custom procedural pixel art for themed levels.

The project can ship themed visuals without binary asset churn: sprites are built
from RGBA pixels and backgrounds from pyglet shapes at runtime.
"""

import math
import pyglet

from engineglobals import EngineGlobals
from lifecycle import GameObject


PALETTES = {
    "farm": ((106, 170, 87), (235, 218, 147), (121, 72, 47)),
    "river": ((87, 151, 191), (60, 105, 138), (82, 91, 73)),
    "dojo": ((184, 73, 62), (239, 225, 188), (68, 39, 35)),
    "space": ((19, 18, 46), (76, 84, 140), (210, 92, 205)),
    "pompeii": ((199, 105, 54), (230, 181, 105), (91, 61, 55)),
}


def _inside_circle(x, y, cx, cy, radius):
    return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2


def make_character_art(kind, width=32, height=32):
    """Return a small custom RGBA image for a named themed character/object."""
    pixels = bytearray(width * height * 4)

    colors = {
        "lucinda": ((224, 84, 132, 255), (62, 34, 49, 255), (250, 221, 192, 255)),
        "jackie_flan": ((246, 195, 61, 255), (30, 30, 30, 255), (217, 83, 66, 255)),
        "levod_burtim": ((105, 232, 220, 255), (117, 70, 191, 255), (255, 224, 91, 255)),
        "van": ((196, 210, 214, 255), (55, 105, 136, 255), (34, 34, 34, 255)),
        "vesuvius": ((78, 62, 62, 255), (224, 73, 46, 255), (252, 168, 52, 255)),
        "pippi": ((239, 92, 64, 255), (255, 198, 81, 255), (65, 117, 190, 255)),
    }
    primary, secondary, accent = colors.get(kind, ((210, 210, 210, 255), (80, 80, 80, 255), (255, 255, 255, 255)))

    for y in range(height):
        for x in range(width):
            color = (0, 0, 0, 0)
            if kind == "van":
                if 4 <= x <= 27 and 10 <= y <= 23:
                    color = primary
                if 7 <= x <= 15 and 16 <= y <= 21:
                    color = secondary
                if _inside_circle(x, y, 9, 9, 4) or _inside_circle(x, y, 23, 9, 4):
                    color = accent
            elif kind == "vesuvius":
                if y <= 7 + abs(x - width // 2) // 2:
                    color = primary
                if 13 <= y <= 20 and abs(x - width // 2) <= max(1, (20 - y) // 2):
                    color = secondary
                if y > 20 and abs(x - width // 2) <= 3:
                    color = accent
            else:
                if _inside_circle(x, y, width // 2, 23, 7):
                    color = accent
                if 9 <= x <= 23 and 5 <= y <= 19:
                    color = primary
                if 12 <= x <= 20 and 12 <= y <= 16:
                    color = secondary
                if kind == "levod_burtim" and (x + y) % 5 == 0 and 4 <= x <= 27 and 4 <= y <= 26:
                    color = accent
                if kind == "pippi" and (x in (7, 25) and 14 <= y <= 24):
                    color = primary
            offset = (y * width + x) * 4
            pixels[offset:offset + 4] = bytes(color)

    return pyglet.image.ImageData(width, height, "RGBA", bytes(pixels), pitch=width * 4)


class ThemeBackdrop(GameObject):
    """Simple custom scene art for each authored level."""

    def __init__(self, theme):
        self.theme = theme
        self.shapes = []
        sky, mid, dark = PALETTES[theme]
        self.shapes.append(pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, EngineGlobals.height, color=sky, batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
        self.shapes.append(pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, 120, color=mid, batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))

        if theme == "farm":
            for x in range(30, EngineGlobals.width, 120):
                self.shapes.append(pyglet.shapes.Rectangle(x, 120, 70, 75, color=dark, batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
                self.shapes.append(pyglet.shapes.Triangle(x - 8, 195, x + 35, 235, x + 78, 195, color=(124, 49, 38), batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
        elif theme == "river":
            self.shapes.append(pyglet.shapes.Rectangle(0, 95, EngineGlobals.width, 80, color=(44, 122, 174), batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
            self.shapes.append(pyglet.shapes.Rectangle(0, 80, EngineGlobals.width, 18, color=(213, 195, 141), batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
        elif theme == "dojo":
            for x in range(0, EngineGlobals.width, 80):
                self.shapes.append(pyglet.shapes.Line(x, 0, x, EngineGlobals.height, width=2, color=dark, batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
            self.shapes.append(pyglet.shapes.Rectangle(250, 420, 300, 70, color=(245, 237, 214), batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
        elif theme == "space":
            for i in range(55):
                x = (i * 137) % EngineGlobals.width
                y = (i * 83) % EngineGlobals.height
                radius = 1 + i % 3
                self.shapes.append(pyglet.shapes.Circle(x, y, radius, color=(245, 245, 225), batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
            self.shapes.append(pyglet.shapes.Circle(660, 440, 75, color=(125, 77, 180), batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
        elif theme == "pompeii":
            self.shapes.append(pyglet.shapes.Triangle(500, 120, 650, 390, 800, 120, color=dark, batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
            self.shapes.append(pyglet.shapes.Triangle(610, 300, 650, 390, 690, 300, color=(242, 82, 42), batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
            self.shapes.append(pyglet.shapes.Rectangle(0, 0, EngineGlobals.width, 55, color=(238, 81, 37), batch=EngineGlobals.main_batch, group=EngineGlobals.bg_group))
        super().__init__(lifecycle_manager="PER_MAP")

    def updateloop(self, dt):
        pass

    def on_finalDeletion(self):
        for shape in self.shapes:
            shape.delete()
        self.shapes.clear()
