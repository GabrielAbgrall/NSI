from random import randint

EMPTY = False
HIDDEN = True

GRID_WIDTH = 30
GRID_HEIGHT = 10
NB_PLACEMENTS = 25

grid = {(x, y): [EMPTY, HIDDEN] for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)}


def bombs_in_neighbors(x: int, y: int) -> int:
    x_range_begin = -1
    x_range_end = 2
    if x == 0:
        x_range_begin = 0
    elif x == GRID_WIDTH - 1:
        x_range_end = 1
    y_range_begin = -1
    y_range_end = 2
    if y == 0:
        y_range_begin = 0
    elif y == GRID_HEIGHT - 1:
        y_range_end = 1
    result = 0
    for dx in range(x_range_begin, x_range_end):
        for dy in range(y_range_begin, y_range_end):
            if grid[x + dx, y + dy][0] is not EMPTY:
                result += 1
    return result


def hidden_neighbors(x: int, y: int) -> list:
    x_range_begin = -1
    x_range_end = 2
    if x == 0:
        x_range_begin = 0
    elif x == GRID_WIDTH - 1:
        x_range_end = 1
    y_range_begin = -1
    y_range_end = 2
    if y == 0:
        y_range_begin = 0
    elif y == GRID_HEIGHT - 1:
        y_range_end = 1
    result = []
    for dx in range(x_range_begin, x_range_end):
        for dy in range(y_range_begin, y_range_end):
            if (dx != 0 or dy != 0) and grid[x + dx, y + dy][1] is HIDDEN:
                result.append((x + dx, y + dy))
    return result


def display_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[x, y][1] is HIDDEN:
                print('#', end='')
            else:
                print(bombs_in_neighbors(x,y),end="")
        print()


def display_grid2():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[x, y][0] is not EMPTY:
                print('O', end='')
            else:
                n = bombs_in_neighbors(x, y)
                if n:
                    print(n, end='')
                else:
                    print(' ', end='')
        print()


def de_mine(x: int, y: int) -> None:
    grid[x, y][1] = not HIDDEN
    if bombs_in_neighbors(x, y) == 0:
        for (i, j) in hidden_neighbors(x, y):
            de_mine(i, j)


for i in range(NB_PLACEMENTS):
    x, y = randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1)
    grid[x, y][0] = not EMPTY

if grid[15, 5][0] is EMPTY:
    de_mine(15,5)
display_grid()