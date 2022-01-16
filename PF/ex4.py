def compose(f, g):
    return lambda x: f(g(x))


def u(x):
    return x + 1


def v(x):
    return 2 * x


w = compose(u, v)
print(w(4))
