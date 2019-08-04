
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

    def update(self):
        if self.has_gravity:
            self.speed[1] += Decimal('.005')
            # terminal velocity is 2 for now
            if self.speed[1] > 2:
                self.speed[1] = 2
        self.rect.move_ip((int(self.speed[0]), int(self.speed[1])))
        if self.rect.left < 0:
            self.rect.left = 0
            self.speed[0] = 0
        elif self.rect.right > EngineGlobals.width:
            self.rect.right = EngineGlobals.width
            self.speed[0] = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed[1] = 0
        elif self.rect.bottom > EngineGlobals.height:
            self.rect.bottom = EngineGlobals.height
            self.speed[1] = 0
