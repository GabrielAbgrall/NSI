"""
This module allows the user to use fractions
"""


class Fraction:

    @classmethod
    def pgcd(cls, a: int, b: int):
        if b == 0:
            return a
        else:
            return Fraction.pgcd(b, a % b)

    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b
        self._simplify()

    def _simplify(self):
        pgcd = Fraction.pgcd(self.a, self.b)
        self.a //= pgcd
        self.b //= pgcd

    def __add__(self, other):
        return Fraction(self.a * other.b + other.a * self.b, self.b * other.b)

    def __sub__(self, other):
        return Fraction(self.a * other.b - other.a * self.b, self.b * other.b)

    def __mul__(self, other):
        return Fraction(self.a * other.a, self.b * other.b)

    def __truediv__(self, other):
        return Fraction(self.a * other.b, self.b * other.a)

    def __str__(self):
        return f"{self.a}/{self.b}"

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __lt__(self, other):
        return self.a * other.b < other.a * self.b

    def __le__(self, other):
        return self == other or self < other
