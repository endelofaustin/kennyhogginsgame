from physics import PhysicsSprite
import pyglet


class Bandaid(PhysicsSprite):

        def __init__(self, init_params={
            'has_gravity': True,
            'resource_images': {
                'gross': "gross_band_aid.png",
                'good': "good_band_aid.png"
            }},
            spawn_coords=None,
            style='good', is_map_object=False
        ):

            if spawn_coords:
                init_params['spawn_coords'] = spawn_coords
            PhysicsSprite.__init__(self, init_params, is_map_object=is_map_object)

            self.sprite.update(scale=.695)
            self.sprite.image = self.resource_images[style]
