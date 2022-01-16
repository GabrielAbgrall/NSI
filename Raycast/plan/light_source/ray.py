import pygame
from math import cos, sin, pi
from plan.boundary.wall import Wall


class Ray:
    def __init__(self, pos, angle):
        self.pos = pos
        self.angle = angle
        size = 7
        self.direction = (cos(angle * pi / 180) * size, sin(angle * pi / 180) * size)

    def cast(self, wall: Wall):
        x1 = wall.pos1[0]
        y1 = wall.pos1[1]
        x2 = wall.pos2[0]
        y2 = wall.pos2[1]

        x3 = self.pos[0]
        y3 = self.pos[1]
        x4 = self.pos[0] + self.direction[0]
        y4 = self.pos[1] + self.direction[1]

        det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if det != 0:
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / det
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / det

            if 0 < t < 1 and u > 0:
                return int(x1 + t * (x2 - x1)), int(y1 + t * (y2 - y1))

    def update(self, pos):
        self.pos = pos

    def draw(self, surface: pygame.Surface, color: pygame.Color):
        pygame.draw.line(surface, color, self.pos, (self.pos[0] + self.direction[0], self.pos[1] + self.direction[1]))
