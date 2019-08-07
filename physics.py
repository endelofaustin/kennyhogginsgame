
import pygame
from decimal import Decimal
from engineglobals import EngineGlobals

# PhysicsSprite represents a sprite that honors the laws of physics.
# It contains an update method that will alter the sprite's position according
# to speed and gravity.
class PhysicsSprite(pygame.sprite.Sprite):
    # Set has_gravity to False to create a sprite that hovers in defiance of all reason
    def __init__(self, has_gravity = True):
        # call the parent Sprite constructor
        pygame.sprite.Sprite.__init__(self)
        # the 'speed' member is a Decimal representation of the sprite's speed at this
        # point in time; each time the game loop runs, the sprite will move by that
        # amount; self.speed[0] is the left-to-right speed (negative is left, positive is right);
        # self.speed[1] is the top-to-bottom speed (negative is up, positive is down)
        self.speed = [Decimal('0'), Decimal('0')]
        # the 'has_gravity' member is a true/false flag to indicate whether this sprite truly
        # obeys Isaac Newton's decrees. Albert Einstein is a poser.
        self.has_gravity = has_gravity
        # for now, all sprites will bear the face of Kenny Hoggins, so load that file into
        # a surface and store it as the self.image member
        # pygame will automatically look for the 'image' and 'rect' members of any sprite
        # and draw the sprite on screen whenever all sprites are drawn in the main loop
        self.image = pygame.image.load("./artwork/kennyface1.png").convert_alpha()
        self.rect = self.image.get_rect()
        # we want to scale up the graphics by a certain scale factor that we specify in
        # EngineGlobals, so we call the scale function on the surface and then recalculate
        # the rect
        self.image = pygame.transform.scale(self.image,
                                            (self.rect.width * EngineGlobals.scale_factor,
                                            self.rect.height * EngineGlobals.scale_factor))
        self.rect = self.image.get_rect()
        # initialize the 'dpos' member as a Decimal representation of the sprite's position
        # in the environment - self.dpos[0] is the 'x' or left-to-right coordinate,
        # self.dpos[1] is the 'y' or top-to-bottom coordinate
        # could use the pygame rect object from above instead of this separate variable; except
        # pygame rects only support integer positioning and Isaac Newton demands more accuracy
        self.dpos = [Decimal(self.rect.left), Decimal(self.rect.top)]

    # this function is automatically called by pygame whenever all sprites are updated in the
    # main loop
    def update(self):
        if self.has_gravity:
            # accelerate downwards by a certain amount
            self.speed[1] += Decimal('.02')
            # terminal velocity is 2 for now, so we won't move any faster than that
            if self.speed[1] > 2:
                self.speed[1] = 2

        # dpos[0] is x, dpos[1] is y
        # position plus speed is equal to new potential location

        new_x = self.dpos[0] + self.speed[0]
        new_y = self.dpos[1] + self.speed[1]
       
        # x_coord and y_coord will represent an element in the environment matrix
        x_coord = new_x/32
        y_coord = new_y/32

        # now, update the sprite's position according to speed
        
        if EngineGlobals.platform[int(y_coord)][int(x_coord)] == 0:
            self.dpos[0] += self.speed[0]
            self.dpos[1] += self.speed[1]
        else:
            self.speed[0] = 0
            self.speed[1] = 0
            

        # but don't let it go off screen to the left, right, top or bottom
        # and if it tries, bring it back and set its speed to 0
        if self.dpos[0] < 0:
            self.dpos[0] = 0
            self.speed[0] = 0
        elif (self.dpos[0] + self.rect.width) > EngineGlobals.width:
            self.dpos[0] = EngineGlobals.width - self.rect.width
            self.speed[0] = 0
        if self.dpos[1] < 0:
            self.dpos[1] = 0
            self.speed[1] = 0
        elif (self.dpos[1] + self.rect.height) > EngineGlobals.height:
            self.dpos[1] = EngineGlobals.height - self.rect.height
            self.speed[1] = 0
        # finally, update the 'rect' member so that pygame will know where to draw the
        # sprite
        self.rect.topleft = (self.dpos[0], self.dpos[1])
