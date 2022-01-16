from plan.plan import *

pygame.init()

p = Plan(1400, 800, Plan.BLACK, 6)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F2:
                pygame.image.save(p.win, "screenshot.png")
    p.draw()
    p.update()
    pygame.display.flip()
    clock.tick(144)
pygame.quit()

