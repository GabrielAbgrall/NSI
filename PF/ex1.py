def apply(f, l: list):
    result = []
    for e in l:
        result.append(f(e))
    return result

def f(x: float):
    return 2 * x + 1

print(apply(f, [1, 2, 3]))