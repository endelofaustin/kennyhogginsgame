from physics import PhysicsSprite

class Spike(PhysicsSprite):

    def __init__(self, sprite_initializer : dict, starting_chunk):

        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
        self.sprite.update(scale=.445)

    def getResourceImages(self):

        return {0: "spikey.png"}
