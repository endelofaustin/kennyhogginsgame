import pyglet, random
from engineglobals import EngineGlobals

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

class MessageBox():

    def __init__(self, text=('', 1), timer=0) -> None:

        self.sprite = pyglet.sprite.Sprite(
            img=pyglet.resource.image('long-text-box.png'),
            x=140, y=10,
            batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_mid
        )
        self.sprite.update(scale=2)

        y = int(26 + float(text[1] * 22) / 2)
        # txt = pyglet.text.decode_text(text[0])
        # self.label = pyglet.text.layout.TextLayout(
        #     document=txt,
        #     width=472, height=36,
        #     wrap_lines=True, multiline=True,
        #     batch=EngineGlobals.main_batch, group=EngineGlobals.editor_group_front
        # )
        # self.label.x = 168
        # self.label.y = y
        # self.label.anchor_y = 'center'
        # self.label._update()
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

        EngineGlobals.add_us.add((self, False))

    def updateloop(self, dt):

        if self.timer > 0:
            self.timer -= 1
            if self.timer <= 0:
                self.label.delete()
                EngineGlobals.delete_us.add(self)

class RandomTalker():

    def __init__(self, is_map_object=False) -> None:

        self.timer = random.randrange(100, 500)
        self.mbox = None
        EngineGlobals.add_us.add((self, is_map_object))

    def updateloop(self, dt):

        if self.mbox and self.mbox.timer > 0:
            return

        if self.timer > 0:
            self.timer -= 1
            if self.timer <= 0:
                self.mbox = MessageBox(random.choice([
                    ('Your mom says hi.', 1),
                    ('A long time ago, in a galaxy far, far away...', 1),
                    ('A piece of fruit just appeared at a random location! Go find it quickly if you want superpowers!!', 2),
                ]), 300)
                self.timer = random.randrange(100, 500)

    # pickler
    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__init__(is_map_object=True)
