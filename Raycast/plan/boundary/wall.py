import pygame

class Wall:

    def __init__(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2

    def draw(self, surface: pygame.Surface, color: pygame.Color):
        pygame.draw.line(surface, color, self.pos1, self.pos2)