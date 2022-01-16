from objects.fractions_custom import Fraction

f1 = Fraction(2, 7)
f2 = Fraction(3, 5)
print(f1 == f2)
# False
print(f1 < f2)
# True
print((f1 + f2) / (f1 * (f1 - f2)))
# -217/22
