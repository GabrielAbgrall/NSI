import pygame
import sys
from time import perf_counter

WINDOW_WIDTH = 250
WINDOW_HEIGHT = 250
sys.setrecursionlimit(WINDOW_WIDTH * WINDOW_HEIGHT)
pygame.init()
WHITE = pygame.Color(255, 255, 255)
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


def rf(x: int, y: int) -> None:
    """
    Colorie récursivement en blanc à partir de (x,y)
    - si les coordonnées sortent de l'écran on ne fait rien
    - si (x,y) est déjà blanche non plus
    - sinon on met la case en blanc et on appelle rf sur les 4 voisins de (x,y) non diagonaux :
        case du haut, du bas, de la gauche et de la droite

    2 instructions sont suffisantes :
    if window.get_at((x, y)) != WHITE: pour tester si un pixel est blanc
    et
    window.set_at((x, y), WHITE) pour mettre un pixel noir en blanc
    """
    if 0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT and window.get_at((x, y)) != WHITE:
        window.set_at((x, y), WHITE)
        pygame.display.flip()
        for neighbour in neighbours((x, y)):
            rf(neighbour[0], neighbour[1])


def neighbours(pos: tuple) -> list:
    temp = [((pos[0] - 1) % WINDOW_WIDTH, pos[1]),
            ((pos[0] + 1) % WINDOW_WIDTH, pos[1]),
            (pos[0], (pos[1] - 1) % WINDOW_HEIGHT),
            (pos[0], (pos[1] + 1) % WINDOW_HEIGHT)]
    result = [temp[i] for i in range(len(temp)) if window.get_at(temp[i]) != WHITE]
    return result


def iterative_fill(x: int, y: int) -> None:
    if window.get_at((x, y)) == WHITE:
        return
    open_list = [(x, y)]
    start = perf_counter()
    while len(open_list) > 0:
        """
        Programme beaucoup moins performant en utilisant la liste comme une pile (prendre dernier élément)
        En effet : 1.32s avec premier arrivé premier servi, sinon plus de 25s
        Pourquoi ?
        """
        current = open_list.pop(0)
        window.set_at(current, WHITE)
        pygame.display.flip()
        for neighbour in neighbours(current):
            if neighbour not in open_list:
                open_list.append(neighbour)
    print(perf_counter() - start)


image = pygame.image.load("image.png")
window.blit(image, (0, 0))
pygame.display.flip()
go_on = True
while go_on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            go_on = False
    if pygame.mouse.get_pressed()[0]:
        """
        Quand on appuie sur le bouton gauche de la souris le programme récupère la position de la souris 
        dans la fenêtre pygame et commence à remplir récursivement
        """
        mouse_pos = pygame.mouse.get_pos()  # pos contient le (x,y) de la souris
        rf(mouse_pos[0], mouse_pos[1])
        pygame.display.flip()
