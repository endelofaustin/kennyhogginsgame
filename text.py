import pyglet, random
from engineglobals import EngineGlobals
from gamepieces import NirvanaFruit
from lifecycle import GameObject
from sprite import makeSprite

class Text_Crawl():

    def __init__(self,):

        self.document = pyglet.text.decode_text('Chase ME!!!! :) You cannat do the catching')
        self.layout = pyglet.text.layout.TextLayout(self.document, EngineGlobals.width, EngineGlobals.height, wrap_lines=True, batch=EngineGlobals.main_batch,)
        self.layout.x = 0
        self.layout.y = -EngineGlobals.height

    def on_draw(self,):
        self.layout.draw()

    def updateloop(self, dt):

        self.layout.x += 0
        self.layout.y += 1

# A box that displays a temporary message to the player and then disappears after
# a set time.
class MessageBox(GameObject):

    def __init__(self, text=('', 1), timer=0) -> None:

        self.sprite = pyglet.sprite.Sprite(
            img=pyglet.resource.image('long-text-box.png'),
            x=140, y=10,
            batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_mid
        )
        self.sprite.update(scale=2)

        y = int(26 + float(text[1] * 22) / 2)
        self.label = pyglet.text.Label(
            text=text[0], color=(0, 0, 0, 255),
            x=168, y=y, width=472, height=36,
            # anchor_y='center',
            multiline=True,
            batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_front
        )
        self.label.anchor_y = 'center'
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

    def __init__(self) -> None:

        self.timer = random.randrange(100, 500)
        self.mbox = None

        super().__init__()

    def updateloop(self, dt):

        if self.mbox and self.mbox.timer > 0:
            return

        if self.timer > 0:
            self.timer -= 1
        if self.timer <= 0:
            (text, line_count, function_to_call) = random.choice([
                ("Your mom says hi from outside the Matrix. That's right, she managed to escape before you, loser.", 2, lambda: None),
                ('A long time ago, in a galaxy far, far away...', 1, lambda: None),
                ('A bunch of fruit just appeared at a random location! Go find it quickly if you want superpowers!!', 2, self.make_a_fruit),
            ])
            self.mbox = MessageBox((text, line_count), 300)
            function_to_call()
            self.timer = random.randrange(100, 500)

    def make_a_fruit(self):
        spawn_coords = (random.randrange(20, len(EngineGlobals.game_map.platform[0]) * 32 - 20), 50)
        makeSprite(NirvanaFruit, spawn_coords, destroy_after=800)

    # pickler
    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        self.__init__()
