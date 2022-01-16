from random import randint, choice

import pygame

from balls.ball import *

pygame.init()
win = pygame.display.set_mode((Ball.WIDTH, Ball.HEIGHT))

GRAY = pygame.color.Color(64, 64, 64)
WHITE = pygame.color.Color(255, 255, 255)
RED = pygame.color.Color(255, 0, 0)
BLUE = pygame.color.Color(0, 0, 255)
GREEN = pygame.color.Color(0, 255, 0)
COLORS = [GRAY, WHITE, BLUE, RED, GREEN]

def draw_balls():
    for ball in Ball.BALLS:
        pygame.draw.circle(win, ball.color, (ball.pos_x, ball.pos_y), ball.radius)

def update_balls():
    for ball in Ball.BALLS:
        ball.update()

for i in range(100):
    radius = randint(5, 100)
    Ball(radius, randint(radius, Ball.WIDTH - radius), randint(radius, Ball.HEIGHT - radius), randint(-4, 4), randint(-4, 4), choice(COLORS))

clock = pygame.time.Clock()
go_on = True
while go_on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            go_on = False
    win.fill(0)
    update_balls()
    draw_balls()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()