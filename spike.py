from physics import PhysicsSprite
import pyglet
class Spike(PhysicsSprite):

        def __init__(self, init_params={
                'has_gravity': True,
                'resource_images': {
                    0: "spikey.png"
                }
            }, spawning_coords=None, is_map_object=False
        ):

            if spawning_coords:
                init_params['spawn_coords'] = spawning_coords
            PhysicsSprite.__init__(self, init_params=init_params, is_map_object=is_map_object)

            self.sprite.update(scale=.445)
