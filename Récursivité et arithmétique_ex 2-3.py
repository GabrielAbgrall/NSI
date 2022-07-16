def decimal_length(n: int) -> int:
    if n < 10:
        return 1
    else:
        return 1 + decimal_length(n//10)


def binary_length(n: int, i=1) -> int:
    if n < 2:
        return 1
    else:
        return 1 + binary_length(n//2)


print(decimal_length(2020))
