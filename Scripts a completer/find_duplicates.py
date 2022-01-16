from duplicates3 import *  # doit marcher avec tes modules duplicate2 duplicate3 et duplicate4
from random import randint


def has_duplicate(content: list) -> bool:
    """
    Le code de cette fonction NE DOIT PAS changer
    """
    s = create()
    for x in content:
        if contains(s, x):
            return True
        else:
            add(s, x)
    return False


print('Pour [1,2,3] :', has_duplicate([1, 2, 3]))
print('Pour [1,2,3,1] :', has_duplicate([1, 2, 3, 1]))

print('Pour une liste de 302 nombres compris entre 1 et 2**16 : ',
      has_duplicate([randint(1, 2 ** 16) for _ in range(302)]))
