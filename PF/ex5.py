from time import sleep


def evaluate_with_delay(f, n: int, d: float):
    for i in range(n):
        print(f(i))
        sleep(d / 1000)


evaluate_with_delay(lambda x: x * 2, 10, 1000)
