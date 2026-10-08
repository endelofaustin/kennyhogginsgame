import pyglet
import random

from engineglobals import EngineGlobals
from gamepieces import NirvanaFruit
from lifecycle import GameObject
from sprite import makeSprite


class IntroMode(GameObject):
    """Opening crawling-text mode shown between the menu and gameplay."""

    def __init__(self):
        self.document = pyglet.text.decode_text(
            "KENNY HOGGINS\n\n"
            "A pig. A hog. A hero with somewhere else to be.\n\n"
            "Escape the farm, find the keys, survive the road, and keep moving."
        )
        self.layout = pyglet.text.layout.TextLayout(
            self.document,
            EngineGlobals.width - 120,
            EngineGlobals.height * 2,
            wrap_lines=True,
        )
        self.layout.x = 60
        self.layout.y = -EngineGlobals.height
        self.finished = False
        super().__init__(lifecycle_manager="UNDYING")

    def start(self):
        self.layout.y = -EngineGlobals.height
        self.finished = False
        EngineGlobals.game_mode = "INTRO"

    def finish(self):
        self.finished = True
        EngineGlobals.game_mode = "PLAY"

    def on_draw(self):
        if getattr(EngineGlobals, "game_mode", "PLAY") == "INTRO":
            self.layout.draw()

    def updateloop(self, dt):
        if getattr(EngineGlobals, "game_mode", "PLAY") != "INTRO":
            return
        self.layout.y += max(1, int(dt))
        if self.layout.y > EngineGlobals.height:
            self.finish()

    def on_key_press(self, symbol, modifiers):
        if getattr(EngineGlobals, "game_mode", "PLAY") == "INTRO":
            self.finish()
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED


# Backward-compatible name for old imports.
Text_Crawl = IntroMode


class MessageBox(GameObject):
    """Temporary in-game message."""

    def __init__(self, text=("", 1), timer=0):
        self.sprite = pyglet.sprite.Sprite(
            img=pyglet.resource.image("long-text-box.png"),
            x=140,
            y=10,
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_mid,
        )
        self.sprite.update(scale=2)

        y = int(26 + float(text[1] * 22) / 2)
        self.label = pyglet.text.Label(
            text=text[0],
            color=(0, 0, 0, 255),
            x=168,
            y=y,
            width=472,
            height=36,
            multiline=True,
            batch=EngineGlobals.main_batch,
            group=EngineGlobals.editor_group_front,
        )
        self.label.anchor_y = "center"
        self.label._update()
        self.timer = timer
        super().__init__()

    def updateloop(self, dt):
        if self.timer > 0:
            self.timer -= 1
            if self.timer <= 0:
                self.label.delete()
                self.sprite.delete()
                self.destroy()


class RandomTalker(GameObject):
    def __init__(self):
        self.timer = random.randrange(100, 500)
        self.mbox = None
        super().__init__()

    def updateloop(self, dt):
        if self.mbox and self.mbox.timer > 0:
            return

        if self.timer > 0:
            self.timer -= 1
        if self.timer <= 0:
            text, line_count, function_to_call = random.choice(
                [
                    ("Your mom says hi from outside the Matrix. That's right, she managed to escape before you, loser.", 2, lambda: None),
                    ("A long time ago, in a galaxy far, far away...", 1, lambda: None),
                    ("A bunch of fruit just appeared at a random location! Go find it quickly if you want superpowers!!", 2, self.make_a_fruit),
                ]
            )
            self.mbox = MessageBox((text, line_count), 300)
            function_to_call()
            self.timer = random.randrange(100, 500)

    def make_a_fruit(self):
        spawn_chunk = EngineGlobals.kenny.current_chunk
        spawn_x_pos = random.randrange(30, spawn_chunk.width * EngineGlobals.tile_size - 60)
        makeSprite(NirvanaFruit, spawn_chunk, (spawn_x_pos, 50))

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        self.__init__()
