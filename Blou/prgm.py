import sys
from turtle import *

sys.setrecursionlimit(10000)

def somme(n: int) -> int:
    if n == 0:
        return 0
    else:
        return n + somme(n-1)


def sommes_cubes(n: int) -> int:
    if n <= 0:
        return 0
    else:
        return n**3 + sommes_cubes(n-1)


def f91(n: int) -> int:
    if n > 100:
        return n-10
    else:
        return f91(f91(n+11))


def puissance(x: float, n: int) -> float:
    global nb_appels
    nb_appels += 1
    if n == 0:
        return 1
    else:
        return x * puissance(x, n-1)


la = {}
lb = {}

def a(n: int) -> int:
    if n==0:
        return 1
    try:
        return la[n]
    except KeyError:
        result = n - b(a(n-1))
        la[n] = result
        return result
        


def b(n: int) -> int:
    if n==0:
        return 0
    try:
        return lb[n]
    except KeyError:
        result = n - a(b(n-1))
        lb[n] = result
        return result


def palindrome(mot: str) -> bool:
    mot = mot.lower()
    if len(mot) == 1 or len(mot) == 2 and mot[0] == mot[1]:
        return True
    elif mot[0] == mot[-1]:
        return palindrome(mot[1:-1])
    else:
        return False


nb_appels = 0
def hanoi(n: int, t1: str, t2: str, t3: str) -> None:
    global nb_appels
    nb_appels += 1
    if n != 0:
        hanoi(n-1, t1, t3, t2)
        print("déplacer palet de", t1, "vers", t3)
        hanoi(n-1, t2, t1, t3)


def catalan(n: int) -> int:
    if n == 1:
        return 1
    elif n > 1:
        return sum(catalan(p)*catalan(n-p) for p in range(1, n))


def koch(x: float, n: int) -> None:
    if n == 0:
        forward(x)
    else:
        koch(x/3, n-1)
        left(60)
        koch(x/3, n-1)
        right(120)
        koch(x/3, n-1)
        left(60)
        koch(x/3, n-1)


def puissance_amelioree(x: int, n: int) -> int:
    global nb_appels
    nb_appels += 1
    if n%2==0:
        return puissance_amelioree(x, n//2) ** 2
    else:
        return x * puissance_amelioree(x, (n-1)//2) ** 2


def pgcd(a: int, b: int) -> int:
    if b==0:
        return a
    else:
        return pgcd(b, a%b)


f = {}
def fibonacci(n: int) -> int:
    if n <= 1:
        return 1
    else:
        f1 = None
        f2 = None
        if n-1 in f:
            f1 = f[n-1]
        else:
            f1 = fibonacci(n-1)
        if n-2 in f:
            f2 = f[n-2]
        else:
            f2 = fibonacci(n-2)
            
        return f1 + f2


print(puissance(2, 16))
print(nb_appels)
nb_appels = 0
print(puissance_amelioree(2, 16))
print(nb_appels)
