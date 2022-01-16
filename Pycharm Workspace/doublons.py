from random import randint

def has_duplicates(lst: list) -> bool:
    x = []
    for e in lst:
        if e in x:
            return True
        x.append(e)
    return False


nb = 0
for i in range(1000):
    l = [randint(1, 65536) for _ in range(302)]
    if has_duplicates(l):
        nb += 1

print(nb/10)
