import pygame

from engine.Engine import *


class Particle:
    def __init__(self, pos: tuple, radius: int, color: tuple, radius_removed_per_frame=0.5):
        self.pos = pos  # Map position (x, y, z)
        self.radius = radius
        self.max_radius = radius
        self.radius_removed_per_frame = radius_removed_per_frame

        self.color = color

        Engine.instance.particles.append(self)

    def actualise(self):
        self.radius -= self.radius_removed_per_frame
        if self.radius <= 0:
            Engine.instance.particles_to_delete.append(self)

    def display(self):
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        pygame.draw.circle(e.screen, (self.color[0], self.color[1], self.color[2],
                                      int(255 * (self.radius / self.max_radius))), pos, self.radius)
