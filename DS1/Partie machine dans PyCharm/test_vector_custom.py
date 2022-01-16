from vectors_custom import *

try:
    v1 = create(0, 4)
    v2 = create(21, 0)
except:
    print('Erreur lors de la création de v1 et v2')
try:
    display(v1)
except:
    print("Erreur lors de l'affichage de v1")
try:
    add(v1, v2)
except:
    print("Erreur dans l'addition v1+v2")
try:
    multiply(v1, 2)
except:
    print("Erreur dans la multiplication de v1 par 2")
try:
    assert norm(add(v2, multiply(v1, 5))) == 29
except:
    print("Erreur au minimum dans la fonction norme")
else:
    print("Tout à l'air de fonctionner correctement")
