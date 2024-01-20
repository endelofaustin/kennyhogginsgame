import pyglet
from engineglobals import EngineGlobals
import pyglet.resource, pyglet.image
from pyglet.sprite import Sprite

class GameMenu():

    def __init__(self):

        # Load the background image
        self.background_image = pyglet.image.load('artwork/StartItUp.png')
        self.menu_batch = pyglet.graphics.Batch()
        self.sprite = Sprite(img=self.background_image, batch=self.menu_batch)
        self.label_style = {
            'font_name': 'Arial',
            'font_size': 36,
            'bold': True,
            'color': (255, 255, 255, 255)
        }
        

        self.start_label = pyglet.text.Label('Start', x=550, y=400, anchor_x='center', anchor_y='center', batch=self.menu_batch, **self.label_style)
        self.settings_label = pyglet.text.Label('Settings', x=550, y=300, anchor_x='center', anchor_y='center', batch=self.menu_batch, **self.label_style)
        self.password_label = pyglet.text.Label('Password', x=550, y=200, anchor_x='center', anchor_y='center', batch=self.menu_batch, **self.label_style)

        self.password = "          "
        self.password_label_visible = False

    def on_draw(self):
        EngineGlobals.window.clear()
        self.menu_batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        return self.handle_mouse_click(x, y)

    def on_text(self, text):
        return self.handle_text_input(text)

    def handle_mouse_click(self, x, y):

        if EngineGlobals.show_menu:
            if self.start_label.x - self.start_label.content_width / 2 <= x <= self.start_label.x + self.start_label.content_width / 2 and \
            self.start_label.y - self.start_label.content_height / 2 <= y <= self.start_label.y + self.start_label.content_height / 2:
                # Handle "Start" button click - You can implement your game logic here
                EngineGlobals.show_menu = False

            elif self.settings_label.x - self.settings_label.content_width / 2 <= x <= self.settings_label.x + self.settings_label.content_width / 2 and \
                 self.settings_label.y - self.settings_label.content_height / 2 <= y <= self.settings_label.y + self.settings_label.content_height / 2:
                # Handle "Settings" button click
                print("Settings button clicked")

            elif self.password_label.x - self.password_label.content_width / 2 <= x <= self.password_label.x + self.password_label.content_width / 2 and \
                 self.password_label.y - self.password_label.content_height / 2 <= y <= self.password_label.y + self.password_label.content_height / 2:
                # Handle "Password" button click
                self.password_label_visible = True
                print("Password Clicked")

            return pyglet.event.EVENT_HANDLED

        else:
            return pyglet.event.EVENT_UNHANDLED

    def handle_text_input(self, text):

        if self.password_label_visible and EngineGlobals.show_menu:

            if text.isalnum():
                self.password += text

            elif text == '\r':
                print("Password entered:", self.password)
                self.password = ""
                self.password_label_visible = False

if __name__ == "__main__":
    menu = GameMenu()
    pyglet.app.run()
