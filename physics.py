
import pygame
from decimal import Decimal
from engineglobals import EngineGlobals

class PhysicsSprite(pygame.sprite.Sprite):
    def __init__(self, has_gravity = True):
        pygame.sprite.Sprite.__init__(self)
        self.speed = [Decimal('0'), Decimal('0')]
        self.has_gravity = has_gravity
        self.image = pygame.image.load("./artwork/kennyface1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image,
                                            (self.rect.width * EngineGlobals.scale_factor,
                                            self.rect.height * EngineGlobals.scale_factor))
        self.rect = self.image.get_rect()
        self.dpos = [Decimal(self.rect.left), Decimal(self.rect.top)]

    def update(self):
        if self.has_gravity:
            self.speed[1] += Decimal('.02')
            # terminal velocity is 2 for now
            if self.speed[1] > 2:
                self.speed[1] = 2
        # move position according to speed
        self.dpos[0] += self.speed[0]
        self.dpos[1] += self.speed[1]
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
        self.rect.topleft = (self.dpos[0], self.dpos[1])
