from keyboard_and_mouse import *
from vk_codes import *

while not is_pressed(VK_E):
    if is_pressed_once(VK_A):
        continuous_relative_move_xy(600, 300, 1)
    if is_pressed_once(VK_Z):
        continuous_relative_move_xy(-600, -300, 2)