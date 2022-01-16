import pygame


class Map:
    pygame.init()

    SPEED = 2
    DIRECTIONS = {pygame.K_w: (0, SPEED),
                  pygame.K_a: (SPEED, 0),
                  pygame.K_s: (0, -SPEED),
                  pygame.K_d: (-SPEED, 0), }

    def __init__(self, path, width, height):
        self._img = pygame.image.load(path)
        self.img = self._img
        self._rect = RectMap(0, 0, self.img.get_width(), self.img.get_height())
        self.width = width
        self.height = height
        self.win = pygame.display.set_mode((width, height), pygame.NOFRAME)
        self.running = False
        self._zoom(1)

    def start(self):
        self.running = True

    def check(self):
        if self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self._zoom(1.3)
                    if event.button == 5:
                        self._zoom(0.7)
            state = pygame.key.get_pressed()

            if state[pygame.K_ESCAPE]:
                self.running = False

            for key in Map.DIRECTIONS.keys():
                if state[key]:
                    self._move(Map.DIRECTIONS[key])
            self._display()

    def _move(self, pos: tuple):
        if not(self._rect.width + self._rect.x + pos[0] < self.width or self._rect.height + self._rect.y + pos[1] < self.height):
            self._rect.update_pos(pos)

    def _zoom(self, scale: float):
        if self._rect.width * scale < 14500 and self._rect.height * scale < 7300:
            self._rect.zoom(scale)
            self.img = pygame.transform.scale(self._img, (int(self._rect.width), int(self._rect.height)))
            if self._rect.width < self.width:
                self._zoom(self.width / self._rect.width)
                self._rect.reset_pos()
            if self._rect.height < self.height:
                self._zoom(self.height / self._rect.height)
                self._rect.reset_pos()

    def _display(self):
        self.win.fill(0)
        self.win.blit(self.img, (self._rect.x, self._rect.y))
        pygame.display.flip()

    def stop(self):
        self.running = False
        pygame.quit()


class RectMap:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def update_pos(self, pos: tuple):
        self.x += pos[0]
        self.y += pos[1]
        if self.x > 0:
            self.update_pos((-self.x, 0))
        if self.y > 0:
            self.update_pos((0, -self.y))

    def reset_pos(self):
        self.x = 0
        self.y = 0

    def zoom(self, scale: float):
        self.update_pos(
            (-(self.width * scale - self.width) * (pygame.mouse.get_pos()[0] - self.x) / self.width,
             -(self.height * scale - self.height) * (pygame.mouse.get_pos()[1] - self.y) / self.height))
        self.width *= scale
        self.height *= scale
