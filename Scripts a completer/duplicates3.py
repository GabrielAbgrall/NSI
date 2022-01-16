"""
This module helps the user find duplicates in a list of 302 values which are integers ranging from 1 to 2**16
"""


def create() -> list:
    """
    creates the structure to store values
    :return: the empty structure
    """
    return [0]


def contains(l: list, x: int) -> bool:
    """
    Checks whether a value belongs to the structure or not
    :param l: the structure
    :param x: the integer
    :return: bool
    """
    return l[0] & 1<<x


def add(l: list, x: int) -> None:
    """
    adds a new value to the structure
    :param l: the structure
    :param x: the value
    :return: None
    """
    l[0] = l[0] | 1<<x
