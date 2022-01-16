import time
import sys

sys.setrecursionlimit(10**9)


def get_execution_time(f, x: int):
    now = time.perf_counter()
    f(x)
    return time.perf_counter() - now


def sum_first_int(x: int):
    result = 0
    while x > 0:
        result += x
        x -= 1
    return result


duration = get_execution_time(sum_first_int, 10 ** 8)
print(f"Duration : {duration * 1000} milliseconds.")
