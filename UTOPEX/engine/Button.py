import sys

from engine.Engine import *
from engine.BasicFunction import *


class Button:
    on_image = pygame.image.load("assets/HUD/on_button_lightning.png")

    def __init__(self, rect, image=None, text=None, color=None, text_height=36, on_color=Engine.WHITE,
                 triggered_color=Engine.LIGHT_RED,
                 content=None):
        self.image = image
        self.rect = pygame.rect.Rect(rect)

        self.color = color if color is not None else Engine.LIGHT_BLUE
        self.on_color = on_color
        self.triggered_color = triggered_color

        self.font = pygame.font.Font("assets/font/text.ttf", text_height)
        self.text = text
        self.text_render_main = None
        self.text_render_on = None
        self.text_render_triggered = None
        if text is not None:
            self.load_text()

        self.on = False
        self.on_image = pygame.transform.scale(Button.on_image, (self.rect.width, self.rect.height))

        self.content = content

    def load_text(self):
        self.text_render_main = self.font.render(self.text, True, self.color)
        self.text_render_on = self.font.render(self.text, True, self.on_color)
        self.text_render_triggered = self.font.render(self.text, True, self.triggered_color)

    def display(self):
        if self.image is not None:
            Engine.instance.screen.blit(self.image, (self.rect.x + (self.rect.width - self.image.get_width()) // 2,
                                                     self.rect.y + (self.rect.height - self.image.get_height()) // 2))
        pygame.draw.rect(Engine.instance.screen, self.color, self.rect, 2)

        if not self.on:
            if self.text_render_main is not None:
                Engine.instance.screen.blit(self.text_render_main,
                                            (self.rect.x + (self.rect.width - self.text_render_main.get_width()) // 2,
                                             self.rect.y + (
                                                     self.rect.height - self.text_render_main.get_height()) // 2))
        else:
            if self.text_render_main is not None:
                Engine.instance.screen.blit(self.text_render_on,
                                            (self.rect.x + (self.rect.width - self.text_render_main.get_width()) // 2,
                                             self.rect.y + (
                                                         self.rect.height - self.text_render_main.get_height()) // 2))
            pygame.draw.rect(Engine.instance.screen, self.on_color, self.rect, 2)

    def display_triggered(self):
        if self.text_render_main is not None:
            Engine.instance.screen.blit(self.text_render_triggered,
                                        (self.rect.x + (self.rect.width - self.text_render_main.get_width()) // 2,
                                         self.rect.y + (self.rect.height - self.text_render_main.get_height()) // 2))
        pygame.draw.rect(Engine.instance.screen, self.triggered_color, self.rect, 2)

    def is_on(self, mouse_coordinate: tuple) -> bool:
        if self.rect.collidepoint(mouse_coordinate):
            self.on = True
        else:
            self.on = False
        return self.on

    def is_triggered(self, mouse_left_click_state: bool):
        if self.on and mouse_left_click_state:
            self.display_triggered()
            return True
        return False

    @staticmethod
    def use() -> bool:
        return True


class Quit_Button(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)

    @staticmethod
    def use() -> bool:
        exit_program()
        return False


class MissionSelection_Button(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)

    @staticmethod
    def use() -> bool:
        return False


class ChallengeSelection_Button(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)

    @staticmethod
    def use() -> bool:
        return False


class MissionButton(Button):
    def __init__(self, pos, difficulty, game_map, game_mission_code_dame, already_finish, image=None, text=None,
                 color=None):
        rect = (pos[0], pos[1], 350, 101)

        text_height = 20
        while not pygame.font.Font("assets/font/text.ttf", text_height). \
                          render(text, True, Engine.WHITE).get_width() < 350:
            text_height -= 1

        super().__init__(rect, image, text, color, 20)

        self.GAME_MAP = game_map
        self.already_finish = already_finish
        self.game_mission_code_name = game_mission_code_dame

        self.difficulty_render_text = pygame.font.Font("assets/font/text.ttf", 12).render(difficulty, True, Engine.LIGHT_BLUE)

        self.template_img = [pygame.image.load("assets/HUD/Mission_HUD.png"),
                             pygame.image.load("assets/HUD/Mission_ON_HUD.png")]
        self.selector = [pygame.image.load("assets/HUD/Mission_Selector_HUD.png"),
                         pygame.image.load("assets/HUD/Mission_Selector_ON_HUD.png")]

    def display(self):
        if not self.on:
            Engine.instance.screen.blit(self.template_img[0], self.rect)
            Engine.instance.screen.blit(self.selector[0], self.rect)
        else:
            Engine.instance.screen.blit(self.template_img[1], self.rect)
            Engine.instance.screen.blit(self.selector[1], (self.rect[0], self.rect[1] + 10))

        Engine.instance.screen.blit(self.text_render_main,
                                    (self.rect.x + (self.rect.width - self.text_render_main.get_width())
                                     // 2, self.rect.y + 12))

        Engine.instance.screen.blit(self.difficulty_render_text, (self.rect.x + 15, self.rect.y + 40))

        color = Engine.GREEN if self.already_finish else Engine.LIGHT_RED
        pygame.draw.circle(Engine.instance.screen, color, (self.rect.x + 320, self.rect.y + 47), 7)
        pygame.draw.circle(Engine.instance.screen, Engine.LIGHT_YELLOW, (self.rect.x + 320, self.rect.y + 47), 7, 2)


class ChallengeButton(MissionButton):
    def __init__(self, pos, difficulty, game_map, game_mission_code_dame, already_finish, function, image=None,
                 text=None, color=None):
        super().__init__(pos, difficulty, game_map, game_mission_code_dame, already_finish, image, text, color)
        self.function = function

        self.template_img[0] = pygame.image.load("assets/HUD/Challenge_HUD.png")
        self.selector[0] = pygame.image.load("assets/HUD/Challenge_Selector_HUD.png")


class InfiniteMode_Button(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)

    @staticmethod
    def use() -> bool:
        return True


class AddWavesButton(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class CellWalkableButton(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class CellSpawnPointButton(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class SaveMapButton(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class OpenMapMenuButton(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class ExtraItemButton(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class WorldStartButton(ExtraItemButton):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class ShowBuildButton(Button):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class CorePosButton(ExtraItemButton):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class ShopPosButton(ExtraItemButton):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class ChestPosButton(ExtraItemButton):
    def __init__(self, rect, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)


class BuildPosButton(ExtraItemButton):
    def __init__(self, rect, build_type, image=None, text=None, color=None, text_height=36):
        super().__init__(rect, image, text, color, text_height)
        self.build_type = build_type


class ColorButton(Button):
    def __init__(self, rect, color):
        super().__init__(rect, None, None, color)

    def display(self):
        pygame.draw.rect(Engine.instance.screen, self.color, self.rect)
        pygame.draw.rect(Engine.instance.screen, Engine.LIGHT_YELLOW, self.rect, 2)


class RG_Button(ColorButton):
    def __init__(self, rect, start=True):
        color = Engine.GREEN if start else Engine.LIGHT_RED
        super().__init__(rect, color)

    def is_triggered(self, mouse_left_click_state: bool):
        state = super().is_triggered(mouse_left_click_state)
        if state:
            self.reverse_color()

        return state

    def reverse_color(self):
        self.color = Engine.LIGHT_RED if self.color == Engine.GREEN else Engine.GREEN


class ColorPaletteButton(ColorButton):
    def __init__(self, rect, color, color_rgb_pos=0):
        super().__init__(rect, color)
        self.color_rgb_pos = color_rgb_pos

    def get_color_percentage_of_click(self, mouse_coordinates):
        pos = mouse_coordinates[0] - self.rect.x
        percentage = pos / self.rect.width
        return int(percentage * 255)


class ExtraMapButton(RG_Button):
    def __init__(self, rect):
        super().__init__(rect, True)


class WaveSelectionButton(Button):
    DISPLAY_VALUE_RECT_SIZE = (50, 50)
    ENEMY_RECT_SIZE = (65, 65)

    def __init__(self):
        super().__init__((40, 40, 1150, 80), None, None, Engine.LIGHT_RED, 30, Engine.GREEN)

        self.base_rect = self.rect

        self.value = 0
        self.active = False
        self.wave_content = None

        self.offset = 0

    def display(self):
        self.rect = pygame.rect.Rect(self.base_rect[0], self.base_rect[1] + 90 * (self.value - 1) - self.offset,
                                     self.base_rect[2], self.base_rect[3])

        color = self.on_color if self.active else self.color
        if self.on and not self.active:
            color = Engine.GOLD
        pygame.draw.rect(Engine.instance.screen, color, self.rect, 3)

        pygame.draw.rect(Engine.instance.screen, Engine.BLACK,
                         (self.rect.x + 70, self.rect.y + (self.rect.height -
                                                           WaveSelectionButton.DISPLAY_VALUE_RECT_SIZE[1]) // 2,
                          WaveSelectionButton.DISPLAY_VALUE_RECT_SIZE[0],
                          WaveSelectionButton.DISPLAY_VALUE_RECT_SIZE[1]))
        pygame.draw.rect(Engine.instance.screen, color,
                         (self.rect.x + 70, self.rect.y + (self.rect.height -
                                                           WaveSelectionButton.DISPLAY_VALUE_RECT_SIZE[1]) // 2,
                          WaveSelectionButton.DISPLAY_VALUE_RECT_SIZE[0],
                          WaveSelectionButton.DISPLAY_VALUE_RECT_SIZE[1]), 3)

        text_render = pygame.font.Font(None, 40).render(f"{self.value}", True,
                                                        Engine.LIGHT_YELLOW)
        Engine.instance.screen.blit(text_render, (
        self.rect.x + 72 + (WaveSelectionButton.DISPLAY_VALUE_RECT_SIZE[0] - text_render.get_width()) // 2,
        self.rect.y + (self.rect.height -
                       WaveSelectionButton.DISPLAY_VALUE_RECT_SIZE[1]) // 2 + 11))

        rect_size = WaveSelectionButton.ENEMY_RECT_SIZE
        for amount, enemy_tuple in enumerate(self.wave_content):
            if enemy_tuple[1] > 0:
                enemy_img = enemy_tuple[0]().image
                if enemy_img.get_width() > rect_size[0] or enemy_img.get_height() > rect_size[1]:
                    enemy_img = pygame.transform.scale(enemy_img, (rect_size[0] - 5, rect_size[1] - 5))
                rect_pos = (self.rect.x + 350 + amount * 150, self.rect.y + (self.rect.height - rect_size[1]) // 2,
                            rect_size[0], rect_size[1])
                pygame.draw.rect(Engine.instance.screen, Engine.BLACK, rect_pos)
                pygame.draw.rect(Engine.instance.screen, Engine.LIGHT_YELLOW, rect_pos, 3)
                Engine.instance.screen.blit(enemy_img, (rect_pos[0] + (rect_pos[2] - enemy_img.get_width()) // 2,
                                                        rect_pos[1] + (rect_pos[3] - enemy_img.get_height()) // 2))
                text_render = pygame.font.Font(None, 40).render(f"{enemy_tuple[1]}", True,
                                                                Engine.LIGHT_YELLOW)
                Engine.instance.screen.blit(text_render, (rect_pos[0] + rect_pos[2] + 10, rect_pos[1] +
                                                          (rect_pos[3] - text_render.get_height()) // 2))


class EnemySelectionButton(Button):
    def __init__(self, rect, image, enemy):
        super().__init__(rect, image, None, Engine.LIGHT_YELLOW)
        self.enemy = enemy
