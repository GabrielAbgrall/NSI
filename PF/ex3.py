def affine_function2(xa: float, ya: float, xb: float, yb: float):
    if xa == xb:
        return None
    a = (yb - ya) / (xb - xa)
    b = ya - a * xa
    return lambda x: a * x + b


f = affine_function2(0, 2, 1, 5)
print(f(4))
