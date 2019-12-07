import pyglet

class Text_Crawl():

    def __init__(self,):

        self.label = pyglet.text.Label('Chase ME!!!! :) You cannnot catch me!',
                          font_name='Times New Roman',
                          font_size=12,
                          x=32, y=233,color=(0,0,0,255),
                          anchor_x='left', anchor_y='center')

    def on_draw(self,):
        self.label.draw()

    def updateloop(self, dt):

        self.label.x += 1
        self.label.y += 1
