from engineglobals import EngineGlobals
from physics import PhysicsSprite


class Bullet(PhysicsSprite):
    """Kenny's traditional rear-fired projectile."""

    def __init__(self, sprite_initializer: dict, starting_chunk):
        super().__init__(sprite_initializer=sprite_initializer, starting_chunk=starting_chunk)

        # Player.shoot_it historically spawned at the front-facing offset. Keep
        # the joke canonical here: move the projectile across Kenny's body to
        # the rear and reverse its travel direction so it comes out the butt.
        if self.x_speed > 0:
            self.x_position -= 46
            self.x_speed = -self.x_speed
        elif self.x_speed < 0:
            self.x_position += 46
            self.x_speed = -self.x_speed
        self.sprite.x = EngineGlobals.screen_x(self.x_position)

    def getResourceImages(self):
        return {0: "bullet1-1.png.png"}

    def hasGravity(self):
        return False

    def on_PhysicsSprite_collided(self, collided_object=None, collided_chunk=None, chunk_x=None, chunk_y=None):
        if collided_object and type(collided_object).__name__ == "Player":
            # The bullet starts close to Kenny, so ignore self-collision.
            return

        if hasattr(collided_object, "getting_hit"):
            collided_object.getting_hit()
            self.destroy()
        elif not isinstance(collided_object, PhysicsSprite):
            self.destroy()
