import pyglet
from engineglobals import EngineGlobals

class GameMenu():

    def __init__(self):

        self.menu_batch = pyglet.graphics.Batch()

        self.label_style = {
            'font_name': 'Arial',
            'font_size': 36,
            'bold': True,
            'color': (255, 255, 255, 255)
        }

        self.start_label = pyglet.text.Label('Start', x=400, y=400, anchor_x='center', anchor_y='center', batch=self.menu_batch, **self.label_style)
        self.settings_label = pyglet.text.Label('Settings', x=400, y=300, anchor_x='center', anchor_y='center', batch=self.menu_batch, **self.label_style)
        self.password_label = pyglet.text.Label('Password', x=400, y=200, anchor_x='center', anchor_y='center', batch=self.menu_batch, **self.label_style)

        self.password = ""
        self.password_label_visible = False

    def on_draw(self):
        EngineGlobals.window.clear()
        self.menu_batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.handle_mouse_click(x, y)

    def on_text(self, text):
        self.handle_text_input(text)

    def handle_mouse_click(self, x, y):

        if self.start_label.x - self.start_label.content_width / 2 <= x <= self.start_label.x + self.start_label.content_width / 2 and \
           self.start_label.y - self.start_label.content_height / 2 <= y <= self.start_label.y + self.start_label.content_height / 2:
            # Handle "Start" button click - You can implement your game logic here
            EngineGlobals.show_menu = False

        elif self.settings_label.x - self.settings_label.content_width / 2 <= x <= self.settings_label.x + self.settings_label.content_width / 2 and \
             self.settings_label.y - self.settings_label.content_height / 2 <= y <= self.settings_label.y + self.settings_label.content_height / 2:
            # Handle "Settings" button click
            print("Settings button clicked")
            self.menu_batch.add(pyglet.shapes.Rectangle(0, 0, 800, 600, color=(0, 0, 255)))

        elif self.password_label.x - self.password_label.content_width / 2 <= x <= self.password_label.x + self.password_label.content_width / 2 and \
             self.password_label.y - self.password_label.content_height / 2 <= y <= self.password_label.y + self.password_label.content_height / 2:
            # Handle "Password" button click
            print("Password button clicked")
            self.password_label_visible = True

    def handle_text_input(self, text):

        if self.password_label_visible:

            if text.isalnum():
                self.password += text

            elif text == '\r':
                print("Password entered:", self.password)
                self.password = ""
                self.password_label_visible = False

if __name__ == "__main__":
    menu = GameMenu()
    pyglet.app.run()
