class Rectangle:

    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __str__(self):
        return f"Rectangle : ({self.x},{self.y},{self.w},{self.h})"

    def __contains__(self, item: tuple):
        return self.x <= item[0] <= self.x + self.w and self.y <= item[1] <= self.y + self.h

    def __add__(self, other):
        x1 = min(self.x, other.x)
        y1 = min(self.y, other.y)
        x2 = max(self.x + self.w, other.x + other.w)
        y2 = max(self.y + self.h, other.y + other.h)
        return Rectangle(x1, y1, x2 - x1, y2 - y1)

    def __mul__(self, other):
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x + self.w, other.x + other.w)
        y2 = min(self.y + self.h, other.y + other.h)
        return Rectangle(x1, y1, x2 - x1, y2 - y1)


r1 = Rectangle(10, 20, 100, 200)
print((3, 4) in r1)
# False
print((12, 100) in r1)
# True
r2 = Rectangle(30, 40, 50, 300)
print(r1 + r2)
# Rectangle : (10,20,100,320)
