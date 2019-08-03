#!/usr/bin/python3
import sys, pygame
pygame.init()

width, height = 800, 600
speed = [2, 2]
gray = 40, 40, 40
scale_factor = 4

screen = pygame.display.set_mode((width, height))

ball = pygame.image.load("./artwork/kennyface1.png").convert_alpha()
ballrect = ball.get_rect()
# scale the image by multiplying its width (right - left) by scale_factor and heigh (bottom - top) by scale_factor
ball = pygame.transform.scale(ball, ((ballrect.right - ballrect.left) * scale_factor, (ballrect.bottom - ballrect.top) * scale_factor))
lucinda  = pygame.image.load("./artwork/lucinda.png")
ballrect = ball.get_rect()

# This is setting the lucinda object in a different starting position than kenny

lucindarect = lucinda.get_rect()
lucindarect.left += 201
lucindarect.right += 201
lucindarect.top += 201
lucindarect.bottom += 201

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    #ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]
    
    #lucindarect = lucindarect.move(speed)
    if lucindarect.left < 0 or lucindarect.right > width:
        speed[0] = -speed[0]
    if lucindarect.top < 0 or lucindarect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(gray)
    screen.blit(ball, ballrect)
    screen.blit(lucinda, lucindarect)
    pygame.display.flip()
