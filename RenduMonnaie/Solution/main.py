import time

from greedy import *
from optimal import *

EURO = [50, 20, 10, 5, 2, 1]
IMPERIAL = [30, 24, 12, 6, 3, 1]

if __name__ == '__main__':
    debug = -1
    while debug!='y' and debug!='n':
        debug=input("Debug? (Y/N):").lower()
    debug = True if debug=='y' else False

    x = 0
    while x<=0:
        try:
            x = int(input("Solutions to compute? x:"))
        except:
            print("Please enter a number greater than 0")

    optimals = []

    start = time.perf_counter()

    for i in range(1, x):

        if i%(x//100) == 0:
            print(f"{i//(x//100)}%")

        g = greedy(i, IMPERIAL)
        o = optimal(i, IMPERIAL)
        if(g > o):
            optimals.append(i)
            if debug:
                print(f"\n[{i}]Optimal solution found ! \n\tGreedy: {g} \n\tOptimal: {o}")
    
    end = time.perf_counter()

    print(f"Optimals found saved in results.txt")
    print(f"\n\nDone in {round(end-start, 3)}s")

    with open("results.txt", 'w') as file:
        s = ""
        for r in optimals:
            s+=f"{r}\n"
        file.write(s)