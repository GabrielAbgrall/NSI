import pygame
from Map import RectMap, Map

pygame.init()

window = pygame.display.set_mode((1000, 800))

rect = RectMap(100, 100, 200, 150)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                rect.zoom(1.3)
            if event.button == 5:
                rect.zoom(0.7)
    state = pygame.key.get_pressed()
    for key in Map.DIRECTIONS.keys():
        if state[key]:
            rect.update_pos(Map.DIRECTIONS[key])
    window.fill(0)
    pygame.draw.rect(window, (255, 255, 255), (rect.x, rect.y, rect.width, rect.height))
    pygame.display.flip()
    clock.tick(144)
pygame.quit()