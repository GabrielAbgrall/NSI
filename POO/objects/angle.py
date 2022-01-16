from math import cos, sin, pi


class Angle:
    def __init__(self, mesure: float):
        self.mesure = mesure % 360

    def affiche(self):
        print(f"angle de {self.mesure} degrés")

    def ajoute(self, other):
        return Angle(self.mesure + other.mesure)

    def cos(self):
        return cos(self.mesure * pi / 180)

    def sin(self):
        return sin(self.mesure * pi / 180)
