import pygame
from engine.Engine import Engine

import pygame
from engine.Engine import Engine
# Cell est l'objet contenu dans la fonction map qui définie se couleur, sa position et si elle est marchable ou non.
# Ces fonctions ne servent pas beaucoup dans le code mais elles ont permi de faire une map et de la sauvegarder dans Map


class Cell:
    def __init__(self, walkable=True, color=(255, 0, 0), pos=(0, 0, 0), spawn_point=False):
        self.walkable = walkable  # Paramètre pour dire si l'on peut ou non marcher sur la case
        self.color = color  # Paramètre qui définie la couleur de la case
        self.pos = pos  # Paramètre qui indique la pos de la case
        self.spawn_point = spawn_point

    def change_color(self, new_color: tuple):
        self.color = new_color  # Permet de changer la couleur de la case

    def change_walkable(self):
        self.walkable = not self.walkable  # Permet de changer le fait de pouvoir marcher sur une case

    def display(self, cell_border=False):  # Lorqu'on appelle display pour la Cellule
        e = Engine.instance
        pygame.draw.polygon(e.screen, self.color,  # On dessine un losange aux position de la Cellule aux coordonnées
                            # convertie au plan isométrique par la fonction "screen_coordinates" du module Engine
                            (e.screen_coordinates(self.pos),
                             e.screen_coordinates((self.pos[0] + 1, self.pos[1], self.pos[2])),
                             e.screen_coordinates((self.pos[0] + 1, self.pos[1] + 1, self.pos[2])),
                             e.screen_coordinates((self.pos[0], self.pos[1] + 1, self.pos[2]))))
        if cell_border:
            color = Engine.WHITE if self.color != Engine.WHITE else Engine.BLACK
            pygame.draw.polygon(e.screen, color,
                                (e.screen_coordinates(self.pos),
                                 e.screen_coordinates((self.pos[0] + 1, self.pos[1], self.pos[2])),
                                 e.screen_coordinates((self.pos[0] + 1, self.pos[1] + 1, self.pos[2])),
                                 e.screen_coordinates((self.pos[0], self.pos[1] + 1, self.pos[2]))), 1)
            if self.spawn_point:
                pygame.draw.circle(e.screen, color, e.screen_coordinates((self.pos[0] + 0.5, self.pos[1] + 0.5, 0)), 3)
            if not self.walkable:
                pygame.draw.polygon(e.screen, color,
                                    (e.screen_coordinates(self.pos),
                                     e.screen_coordinates((self.pos[0] + 1, self.pos[1] + 1, self.pos[2])),
                                     e.screen_coordinates((self.pos[0] + 1, self.pos[1], self.pos[2])),
                                     e.screen_coordinates((self.pos[0], self.pos[1] + 1, self.pos[2]))), 1)
