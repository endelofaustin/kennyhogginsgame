from physics import PhysicsSprite
import pyglet
class Spike(PhysicsSprite):

        def __init__(self, init_params={
                'has_gravity': True,
                'resource_images': {
                    0: "spikey.png"
                }
            }, spawning_coords=None
        ):

            if spawning_coords:
                init_params['spawn_coords'] = spawning_coords
            PhysicsSprite.__init__(self, init_params=init_params)

            self.sprite.update(scale=.445)
