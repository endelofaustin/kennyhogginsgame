from physics import PhysicsSprite
import pyglet


class Bandaid(PhysicsSprite):

        def __init__(self, spawn_coords, style):

            PhysicsSprite.__init__(self, has_gravity=True, resource_image_dict={
                'gross': pyglet.resource.image("gross_band_aid.png"),
                'good': pyglet.resource.image("good_band_aid.png")
            })
            self.update(scale=.695)
            (self.x_position, self.y_position) = spawn_coords
            self.image = self.resource_images[style]
