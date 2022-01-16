from time import sleep, perf_counter_ns
import win32api
from vk_codes import *

"""
This module allows to check if keys or mouse buttons are pressed in various ways.
It also allows to generate mouse and keyboard events
    - simulate a key presss and a key release as well as mouse buttons clicks
    - move mouse from a point to another, continuously, during a given amount of time
"""


def is_pressed(key: int) -> bool:
    """
    checks if a key is being pressed
    """
    return win32api.GetKeyState(key) < -10

def press_key(key: int) -> None:
    """
    simulates a key press or a mouse click
    """
    win32api.keybd_event(key, 0)


def press_and_release_key(key: int) -> None:
    """
    simulates a key press or a mouse click with release
    
    """
    pass


def release_key(key: int) -> None:
    """
    simulates a key or a mouse button released
    """
    pass


def is_pressed_once(key: int) -> bool:
    """
    checks if a key is being pressed but only once :
    if the key was being pressed during the last call and is still being pressed,
    this function returns False... until key is released and pressed again
    """
    pass


def wait_until_released(key: int) -> None:
    """
    pauses until key's pressed
    """
    pass


def get_key() -> int:
    """
    returns the key_code if a key's being pressed
    """
    pass


def move_mouse_relative(x, y) -> None:
    """
    moves mouse relatively
    """
    pass


def continuous_relative_move_xy(x: int, y: int, time_interval: int) -> None:
    """
    moves mouse relatively and continuously during time_interval
    """
    pass


def mouse_mouse_from_to(x1, y1, x2, y2, duration) -> None:
    """
    moves mouse continuously during time_interval from (x1,y1) to (x2,y2)
    """
    pass


def move_mouse_to(x, y, duration=0) -> None:
    """
    moves mouse continuously during time_interval from current position to (x,y)
    """
    pass
