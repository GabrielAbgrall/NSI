def p(x: int):
    return x % 10 == 2

def verify(f, l: list):
    for e in l:
        if f(e):
            return e
    return None

print(verify(p, [1, 3, 293, 202, 14]))
