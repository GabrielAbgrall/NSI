import pygame

class Engine:

    Singleton = None

    def __init__(self, title, dimensions, fps=None) -> None:
        
        # Already started
        if Engine.Singleton:
            raise Exception("Another instance of Engine already exists")

        self.context = pygame.display.set_mode(dimensions)
        pygame.display.set_caption(title)
        self.running = False
        self.fps = fps

        self.entities = []

        Engine.Singleton = self


    def run(self):
        pygame.init()

        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            self.event_handler()
            self.display()
            self.update()
            if self.fps:
                clock.tick(self.fps)
        self.cleanup()
    

    def event_handler(self):
        global running

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.stop()


    def display(self):
        self.context.fill(0)

        for entity in self.entities:
            entity.display(self.context)

        pygame.display.flip()


    def update(self):
        for entity in self.entities:
            entity.update()


    def stop(self):
        self.running = False

    def cleanup(self):
        pygame.quit()


if __name__ == '__main__':
    test_engine = Engine('Test Engine', (1000, 800))
    test_engine.run()