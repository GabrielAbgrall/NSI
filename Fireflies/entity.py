import pygame
import random
import math
import engine


class Firefly:

    # Interactions related class attributes
    FIREFLIES = []
    INTERACTIONS = False
    INTERACTION_RADIUS = 50

    # Movement related class attributes
    RADIUS = 10
    MIN_SPEED = 1.5
    MAX_SPEED = 0.5
    SWERVE_AMPLITUDE = 0.1

    #Clock & luminosity related class attributes
    THRESHOLD = 1.0
    THRESHOLD_PULL_FORCE = 0.1
    GLOBAL_CLOCK_SPEED = 1

    # Flash color
    COLOR = (128, 195, 111)

    def __init__(self, max_position) -> None:

        # Movement related attributes
        self.position = (random.random() * max_position[0], random.random() * max_position[1])
        self.speed = Firefly.MIN_SPEED + random.random() * (Firefly.MAX_SPEED - Firefly.MIN_SPEED)
        self.angle = random.random() * Firefly.THRESHOLD
        self.swerve = (random.random() - 0.5) * math.pi

        # Clock & luminosity related attributes
        self.clock = random.random() * Firefly.THRESHOLD
        self.clock_speed = 0.9 + random.random() * 0.2
        self.luminosity = 0

        # Adding current firefly to the fireflies "network"
        Firefly.FIREFLIES.append(self)


    def display(self, context):

        # To show a gray point at the position of the firefly
        # Uncomment the following line
        #pygame.draw.circle(context, (100, 100, 100), self.position, 2)

        # To show flash
        pygame.draw.circle(context, Firefly.COLOR, self.position, self.luminosity * self.RADIUS)
        # Reduce flash luminosity over time
        self.luminosity *= 0.9


    def update(self):

        # Update internal clock
        self.clock += Firefly.GLOBAL_CLOCK_SPEED/engine.Engine.Singleton.fps

        # When internal clock did a complete turn
        if self.clock > Firefly.THRESHOLD:
            self.clock = 0
            self.luminosity = 1

            # If interactions between fireflies are activated
            if Firefly.INTERACTIONS:
                for other in Firefly.FIREFLIES:
                    # Ignore current firefly
                    if self == other:
                        continue
                    # Check if the other firefly is in range of interaction
                    if math.dist(self.position, other.position) < Firefly.INTERACTION_RADIUS:
                        # Increase the other internal clock a bit forward
                        # according to its internal clock to
                        # prevent double flash
                        other.clock += other.clock*Firefly.THRESHOLD_PULL_FORCE
                        if other.clock > Firefly.THRESHOLD:
                            other.clock = Firefly.THRESHOLD
        
        # Update position according to the angle and speed
        self.position = (
            self.position[0] + math.cos(self.angle) * self.speed,
            self.position[1] + math.sin(self.angle) * self.speed
        )

        # Update angle according to the current swerve
        self.angle += self.swerve
        # And at rare times we update the swerve
        if random.random() < 0.05:
            self.swerve = (random.random() - 0.5) * Firefly.SWERVE_AMPLITUDE
    

    def __str__(self) -> str:
        return f"Firefly ( \n\tposition={self.position}, \n\tenergy={self.clock}, \n\tdelta={self.delta} \n)\n"


# Test block
if __name__ == '__main__':
    for _ in range(10):
        f = Firefly()
        f.randomize(1000, 1000, 0.5, 1.0)
        print(f)