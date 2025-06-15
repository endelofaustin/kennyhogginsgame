import random
from physics import PhysicsSprite
from gamepieces import NirvanaFruit
from sprite import makeSprite
from text import MessageBox
from engineglobals import EngineGlobals

class McSwanson(PhysicsSprite):
    def __init__(self, sprite_initializer: dict, starting_chunk):
        self.timer = 0
        self.kenny_visited = False
        super().__init__(sprite_initializer, starting_chunk)

    def hasGravity(self):
        return True

    def getResourceImages(self):
        return {0: "mcswanson-1.png"}

    def updateloop(self, dt):
        if self.timer > 0:
            self.timer -= 1
        return super().updateloop(dt)

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if type(collided_object).__name__ == 'Player' and self.timer <= 0:
            self.say_something()

    def say_something(self):
        if self.kenny_visited:
            (text, line_count, function_to_call) = random.choice([
                ("Your mom says hi from outside the Matrix. That's right, she managed to escape before you.", 2, lambda: None),
                ('A long time ago, in a galaxy far, far away...', 1, lambda: None),
                ('I have manifested a Nirvana fruit for you through sheer force of will. Go find it.', 2, self.make_a_fruit),
            ])
        else:
            (text, line_count, function_to_call) = ("My name is Ronald McSwanson, and you're going to regret asking me for help.", 2, lambda: None)
            self.kenny_visited = True
        MessageBox((text, line_count), 300)
        function_to_call()
        self.timer = 300

    def make_a_fruit(self):
        spawn_chunk = self.current_chunk
        spawn_x_pos = random.randrange(30, spawn_chunk.width * EngineGlobals.tile_size - 60)
        makeSprite(NirvanaFruit, spawn_chunk, (spawn_x_pos, 50))
