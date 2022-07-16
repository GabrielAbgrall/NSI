import pygame
import sys

# ------------------------------- #
#            CONSTANT             #
# ------------------------------- #

Clock = pygame.time.Clock()
TICK_SPEED = 144

# ------------------------------- #
#            VARIABLE             #
# ------------------------------- #
input_info = {}


def check_input(py_event: pygame.event) -> None:  # For each key pressed, we turn a key in a dict
    # The value of the key is in index and a boolean who indicate if the key is pressed or not
    global input_info
    if py_event.type == pygame.KEYDOWN:
        input_info[py_event.key] = True
    elif py_event.type == pygame.KEYUP:
        input_info[py_event.key] = False
    elif py_event.type == pygame.MOUSEBUTTONDOWN:
        if py_event.button == 1:
            input_info["LEFT_CLICK"] = True
        elif py_event.button == 2:
            input_info["MWB"] = True
        if py_event.button == 3:
            input_info["RIGHT_CLICK"] = True
    elif py_event.type == pygame.MOUSEBUTTONUP:
        if py_event.button == 1:
            input_info["LEFT_CLICK"] = False
        elif py_event.button == 2:
            input_info["MWB"] = False
        elif py_event.button == 3:
            input_info["RIGHT_CLICK"] = False


def check_event():
    for event in pygame.event.get():  # We check the different events of the user
        check_input(event)
        if event.type == pygame.QUIT:
            exit_program()


def exit_program():
    sys.exit()
