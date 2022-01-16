import pygame
from plan.light_source.ray import Ray

class LightSource:

    def __init__(self, nb_rays):
        self.pos = (0, 0)
        self.rays = [Ray(self.pos, 360 / nb_rays * c) for c in range(nb_rays)]

    def update(self, pos):
        self.pos = pos
        for ray in self.rays:
            ray.update(self.pos)

    def look(self, walls, surface: pygame.Surface, color: pygame.Color):
        for ray in self.rays:
            closest = None
            record = None
            for wall in walls:
                pt = ray.cast(wall)
                if pt is not None:
                    d = ((pt[0] - self.pos[0])**2 + (pt[1] - self.pos[1])**2)**.5
                    if record is None or d < record:
                        record = d
                        closest = pt
            if closest is not None:
                pygame.draw.line(surface, color, (self.pos[0], self.pos[1]), (closest[0], closest[1]))


    def draw(self, surface: pygame.Surface, color: pygame.Color):
        pygame.draw.circle(surface, color, self.pos, 5)
        #for ray in self.rays:
        #    ray.draw(surface, color)
