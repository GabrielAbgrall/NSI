def create(x: float, y: float) -> tuple:
    """
    creates a 2D-vector
    :param: x: float
    :param: y: float
    :return: tuple
    """
    return x, y


def display(v: tuple) -> None:
    """
    simply prints the vector coordinates on the screen
    :param: v: tuple
    :return: None
    """
    print("(" + str(v[0]) + " ; " + str(v[1]) + ")")


def add(v1: tuple, v2: tuple) -> tuple:
    """
    adds 2 vectors and returns the sum
    :param: v1: tuple
    :param: v2: tuple
    :return: tuple
    """
    return v1[0] + v2[0], v1[1] + v2[1]


def multiply(v: tuple, k: float) -> tuple:
    """
    multiplies the vector v by the float k and returns the sum
    :param: v: tuple
    :param: k: float
    :return: tuple
    """
    return v[0] * k, v[1] * k


def norm(v: tuple) -> float:
    """
    returns the norm of a vector
    :param: v: tuple
    :return: float
    """
    return (v[0] ** 2 + v[1] ** 2) ** .5
