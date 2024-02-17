from physics import PhysicsSprite

class Spike(PhysicsSprite):

    def __init__(self, sprite_initializer : dict):

        super().__init__(sprite_initializer)
        self.sprite.update(scale=.445)

    def getResourceImages(self):

        return {0: "spikey.png"}
