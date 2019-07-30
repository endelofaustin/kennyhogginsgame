#!/usr/bin/python3
import sys, pygame
pygame.init()

size = width, height = 800, 600
speed = [2, 2]
black = 0, 0, 0
scale_factor = 16

screen = pygame.display.set_mode(size)

ball = pygame.image.load("./artwork/kennyface1.png").convert()
ballrect = ball.get_rect()
# scale the image by multiplying its width (right - left) by scale_factor and heigh (bottom - top) by scale_factor
ball = pygame.transform.scale(ball, ((ballrect.right - ballrect.left) * scale_factor, (ballrect.bottom - ballrect.top) * scale_factor))
lucinda  = pygame.image.load("./artwork/lucinda.png")
ballrect = ball.get_rect()

# This is setting the lucinda object in a different starting position than kenny

lucindarect = lucinda.get_rect()
lucindarect.left += 101
lucindarect.right += 101
lucindarect.top += 101
lucindarect.bottom += 101

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]
    
    lucindarect = lucindarect.move(speed)
    if lucindarect.left < 0 or lucindarect.right > width:
        speed[0] = -speed[0]
    if lucindarect.top < 0 or lucindarect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    screen.blit(lucinda, lucindarect)
    pygame.display.flip()
