from physics import PhysicsSprite

class Bandaid(PhysicsSprite):

        def __init__(self, sprite_initializer : dict, starting_chunk):
            super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)
            self.sprite.update(scale=.695)
            self.sprite.image = self.resource_images[sprite_initializer['style']]

        def getResourceImages(self):
            return {
                 'gross': "gross_band_aid.png",
                 'good': "good_band_aid.png"
            }
