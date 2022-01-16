def units_digit(n: int) -> int:
    return n%10


def hundreds_digit(n: int) -> int:
    return n%1000 // 100


def thousands_digit(n: int) -> int:
    return n%10000 // 1000

print(thousands_digit(19198))
