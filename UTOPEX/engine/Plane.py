import math


class Plane:

    def __init__(self, size=50):
        # Taille de rendu d'une case
        self.size = size

    def convert(self, pos) -> tuple:
        # Conversion d'une coordonnée du monde en coordonnées en pixels
        x = (math.sqrt(2)/2) * (pos[0] - pos[1])
        y = math.sqrt(2/3) * - pos[2] - (1/math.sqrt(6)) * (pos[0] + pos[1])
        return int(-x * self.size), int(y * self.size)

    @staticmethod
    def distance(a: tuple, b: tuple):
        # Distance entre deux positions
        # (en coordonnées du monde et non en pixels)
        return ((b[0] - a[0])**2 + (b[1] - a[1])**2 + (b[2] - a[2])**2)**0.5