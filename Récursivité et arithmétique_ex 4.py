def is_divisible_by_7(n: int) -> int:
    if n <= 70:
        return n in [-7, 0, 7, 14, 21, 28, 35, 42, 49, 56, 63, 70]
    else:
        return is_divisible_by_7(n//10 - 2*(n%10))

print(is_divisible_by_7(31976))
