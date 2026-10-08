import pyglet
from engineglobals import EngineGlobals
from pyglet.sprite import Sprite


LEVEL_CHOICES = [
    ("Escape from the Farm", "farm.dill"),
    ("Van Down by the River", "river.dill"),
    ("Karate Dojo", "dojo.dill"),
    ("Writing Rainbomb", "space.dill"),
    ("Escape Vesuvius", "pompeii.dill"),
    ("Theo's Trailer", "theo.dill"),
]


class GameMenu:
    """Clickable main menu with level select plus alternate game modes."""

    def __init__(self, on_new_game=None, on_load_game=None, on_level_selected=None, on_karts_selected=None):
        self.on_new_game = on_new_game
        self.on_load_game = on_load_game
        self.on_level_selected = on_level_selected
        self.on_karts_selected = on_karts_selected
        self.screen = "main"

        self.background_image = pyglet.image.load("artwork/StartItUp.png")
        self.menu_batch = pyglet.graphics.Batch()
        self.sprite = Sprite(img=self.background_image, batch=self.menu_batch)
        self.label_style = {
            "font_name": "Arial",
            "font_size": 27,
            "weight": pyglet.text.Weight.BOLD,
            "color": (255, 255, 255, 255),
        }

        self.title_label = pyglet.text.Label(
            "KENNY HOGGINS", x=550, y=525, anchor_x="center", anchor_y="center",
            batch=self.menu_batch, font_size=34, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255),
        )
        self.new_label = pyglet.text.Label("Start", x=550, y=425, anchor_x="center", anchor_y="center", batch=self.menu_batch, **self.label_style)
        self.karts_label = pyglet.text.Label("Karts not Farts", x=550, y=355, anchor_x="center", anchor_y="center", batch=self.menu_batch, **self.label_style)
        self.load_label = pyglet.text.Label("Load Game", x=550, y=285, anchor_x="center", anchor_y="center", batch=self.menu_batch, **self.label_style)
        self.settings_label = pyglet.text.Label("Settings", x=550, y=215, anchor_x="center", anchor_y="center", batch=self.menu_batch, **self.label_style)
        self.settings_status = pyglet.text.Label("Hints: off", x=550, y=172, anchor_x="center", anchor_y="center", batch=self.menu_batch, font_size=15, color=(255, 255, 255, 255))

        self.level_title = pyglet.text.Label(
            "SELECT A LEVEL", x=550, y=535, anchor_x="center", anchor_y="center",
            batch=self.menu_batch, font_size=32, weight=pyglet.text.Weight.BOLD,
            color=(255, 255, 255, 255),
        )
        self.level_labels = []
        for index, (name, filename) in enumerate(LEVEL_CHOICES):
            label = pyglet.text.Label(
                name, x=550, y=445 - index * 62, anchor_x="center", anchor_y="center",
                batch=self.menu_batch, font_size=22, color=(255, 255, 255, 255),
            )
            self.level_labels.append((label, filename))
        self.back_label = pyglet.text.Label(
            "Back", x=550, y=65, anchor_x="center", anchor_y="center",
            batch=self.menu_batch, font_size=18, color=(255, 255, 255, 255),
        )
        self._update_visibility()

    def _update_visibility(self):
        main_visible = self.screen == "main"
        for label in (
            self.title_label,
            self.new_label,
            self.karts_label,
            self.load_label,
            self.settings_label,
            self.settings_status,
        ):
            label.visible = main_visible
        self.level_title.visible = not main_visible
        self.back_label.visible = not main_visible
        for label, _ in self.level_labels:
            label.visible = not main_visible

    def on_draw(self):
        EngineGlobals.window.clear()
        self.menu_batch.draw()

    def _contains(self, label, x, y):
        return (
            label.visible
            and label.x - label.content_width / 2 <= x <= label.x + label.content_width / 2
            and label.y - label.content_height / 2 <= y <= label.y + label.content_height / 2
        )

    def on_mouse_press(self, x, y, button, modifiers):
        if not EngineGlobals.show_menu:
            return pyglet.event.EVENT_UNHANDLED

        if self.screen == "main":
            if self._contains(self.new_label, x, y):
                self.screen = "levels"
                self._update_visibility()
            elif self._contains(self.karts_label, x, y):
                EngineGlobals.show_menu = False
                if self.on_karts_selected:
                    self.on_karts_selected()
            elif self._contains(self.load_label, x, y):
                EngineGlobals.show_menu = False
                if self.on_load_game:
                    self.on_load_game()
            elif self._contains(self.settings_label, x, y):
                EngineGlobals.hint_tiles[0] = not EngineGlobals.hint_tiles[0]
                self.settings_status.text = "Hints: {}".format("on" if EngineGlobals.hint_tiles[0] else "off")
        else:
            if self._contains(self.back_label, x, y):
                self.screen = "main"
                self._update_visibility()
            else:
                for label, filename in self.level_labels:
                    if self._contains(label, x, y):
                        EngineGlobals.show_menu = False
                        if self.on_new_game:
                            self.on_new_game()
                        if self.on_level_selected:
                            self.on_level_selected(filename)
                        break

        return pyglet.event.EVENT_HANDLED
