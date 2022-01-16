import pygame
from random import randint, choice

WIN_WIDTH = 800
WIN_HEIGHT = 600

GRAY = pygame.color.Color(64, 64, 64)
WHITE = pygame.color.Color(255, 255, 255)
RED = pygame.color.Color(255, 0, 0)
BLUE = pygame.color.Color(0, 0, 255)
GREEN = pygame.color.Color(0, 255, 0)
COLORS = [GRAY, WHITE, BLUE, RED, GREEN]
pos_x = []
pos_y = []
r = []
color = []
v_x = []
v_y = []


def create_new_ball():
    radius = randint(5, 100)
    r.append(radius)
    pos_x.append(randint(radius, WIN_WIDTH - radius))
    pos_y.append(randint(radius, WIN_HEIGHT - radius))
    v_x.append(randint(-4, 4))
    v_y.append(randint(-4, 4))
    color.append(choice(COLORS))


def draw_balls():
    for i in range(len(r)):
        pygame.draw.circle(win, color[i], (pos_x[i], pos_y[i]), r[i])


def update_balls():
    for i in range(len(r)):
        pos_x[i] += v_x[i]
        if not r[i] <= pos_x[i] <= WIN_WIDTH - r[i]:
            v_x[i] *= -1
        pos_y[i] += v_y[i]
        if not r[i] <= pos_y[i] <= WIN_HEIGHT - r[i]:
            v_y[i] *= -1


pygame.init()
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

for i in range(100):
    create_new_ball()

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
