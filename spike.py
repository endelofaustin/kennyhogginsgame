from physics import PhysicsSprite
import pyglet
class Spike(PhysicsSprite):

        def __init__(self, spawning_coords):

            PhysicsSprite.__init__(self, has_gravity=True, resource_image_dict={
                'point': pyglet.resource.image("spikey.png"),
            })
            self.update(scale=.445)
            self.dpos = spawning_coords



