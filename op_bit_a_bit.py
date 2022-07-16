from win32api import *
from win32con import *


def test_flags(x: int) -> bool:
    return x & (1<<2 | 1<<7) == 1<<2 | 1<<7

test = int(input("entrez un nombre entre 0 et 255 : "))

for i in range(8):
    if (test & 1<<i) == 1<<i:
        print("f" + str(i))

print(test_flags(test))
