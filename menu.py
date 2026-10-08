import pyglet
from engineglobals import EngineGlobals
from pyglet.sprite import Sprite


class GameMenu:
    """Simple clickable start/configuration menu."""

    def __init__(self, on_new_game=None, on_load_game=None):
        self.on_new_game = on_new_game
        self.on_load_game = on_load_game
        self.background_image = pyglet.image.load("artwork/StartItUp.png")
        self.menu_batch = pyglet.graphics.Batch()
        self.sprite = Sprite(img=self.background_image, batch=self.menu_batch)
        self.label_style = {
            "font_name": "Arial",
            "font_size": 30,
            "weight": pyglet.text.Weight.BOLD,
            "color": (255, 255, 255, 255),
        }

        self.new_label = pyglet.text.Label("New Game", x=550, y=430, anchor_x="center", anchor_y="center", batch=self.menu_batch, **self.label_style)
        self.load_label = pyglet.text.Label("Load Game", x=550, y=350, anchor_x="center", anchor_y="center", batch=self.menu_batch, **self.label_style)
        self.settings_label = pyglet.text.Label("Settings", x=550, y=270, anchor_x="center", anchor_y="center", batch=self.menu_batch, **self.label_style)
        self.settings_status = pyglet.text.Label("Hints: off", x=550, y=220, anchor_x="center", anchor_y="center", batch=self.menu_batch, font_size=16, color=(255, 255, 255, 255))

    def on_draw(self):
        EngineGlobals.window.clear()
        self.menu_batch.draw()

    def _contains(self, label, x, y):
        return (
            label.x - label.content_width / 2 <= x <= label.x + label.content_width / 2
            and label.y - label.content_height / 2 <= y <= label.y + label.content_height / 2
        )

    def on_mouse_press(self, x, y, button, modifiers):
        if not EngineGlobals.show_menu:
            return pyglet.event.EVENT_UNHANDLED

        if self._contains(self.new_label, x, y):
            EngineGlobals.show_menu = False
            if self.on_new_game:
                self.on_new_game()
        elif self._contains(self.load_label, x, y):
            EngineGlobals.show_menu = False
            if self.on_load_game:
                self.on_load_game()
        elif self._contains(self.settings_label, x, y):
            EngineGlobals.hint_tiles[0] = not EngineGlobals.hint_tiles[0]
            self.settings_status.text = "Hints: {}".format("on" if EngineGlobals.hint_tiles[0] else "off")

        return pyglet.event.EVENT_HANDLED
