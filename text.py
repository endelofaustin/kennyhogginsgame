import pyglet
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
