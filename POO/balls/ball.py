class Ball:
    WIDTH = 800
    HEIGHT = 600

    BALLS = []

    def __init__(self, radius, pos_x, pos_y, v_x, v_y, color):
        self.radius = radius
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.v_x = v_x
        self.v_y = v_y
        self.color = color
        Ball.BALLS.append(self)

    def update(self):
        self.pos_x += self.v_x
        if not self.radius <= self.pos_x <= Ball.WIDTH - self.radius:
            self.v_x *= -1
        self.pos_y += self.v_y
        if not self.radius <= self.pos_y <= Ball.HEIGHT - self.radius:
            self.v_y *= -1

