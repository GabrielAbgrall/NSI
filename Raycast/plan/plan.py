import pygame
from random import randint
from plan.boundary.wall import Wall
from plan.light_source.light_source import LightSource

class Plan:
    WHITE = pygame.color.Color(255, 255, 255)
    BLACK = pygame.color.Color(0, 0, 0)

    def __init__(self, width, height, background, nb_walls: int):
        self.width = width
        self.height = height
        self.background = background
        self.walls = []
        self.walls.append(Wall((-1, -1), (self.width, -1)))
        self.walls.append(Wall((self.width, -1), (self.width, self.height)))
        self.walls.append(Wall((self.width, self.height), (-1, self.height)))
        self.walls.append(Wall((-1, self.height), (-1, -1)))
        for _ in range(nb_walls):
            self.walls.append(Wall((randint(0, self.width), randint(0, self.height)),
                                   (randint(0, self.width), randint(0, self.height))))
        self.win = pygame.display.set_mode((self.width, self.height))
        self.light_source = LightSource(360)

    def add_wall(self, wall: Wall):
        self.walls.append(wall)

    def draw(self):
        self.win.fill(Plan.BLACK)
        self.light_source.draw(self.win, Plan.WHITE)
        for wall in self.walls:
            wall.draw(self.win, Plan.WHITE)

    def update(self):
        self.light_source.update(pygame.mouse.get_pos())
        self.light_source.look(self.walls, self.win, Plan.WHITE)
