import sys, pygame

from entity.player.Bomb_Spell import *
from engine.Button import *
from engine.HUD import *


class Queue:

    def __init__(self):
        self.content = []

    def put_on(self, value):
        self.content.append(value)

    def put_out(self):
        return self.content.pop(0)

    def is_empty(self):
        return len(self.content) == 0


class TS_Skill:
    def __init__(self, value):
        self.value = value
        self.children = []

        self.mark = False

    def add_child(self, child):
        self.children.append(child)

    def Breadth_First_Search(self):
        Q = Queue()
        Q.put_on(self)
        self.mark_on()
        while not Q.is_empty():
            content = Q.put_out()
            print(content.value)
            for child in content.children:
                if not child.mark:
                    Q.put_on(child)
                    child.mark_on()

    def mark_on(self):
        self.mark = True

    def mark_out(self):
        self.mark = False

    def get_height(self):
        max_height = 0
        for child in self.children:
            max_temp = child.get_height() + 1
            if max_temp > max_height:
                max_height = max_temp

        return max_height

    def prefix_mark_out(self):
        self.mark_out()
        for child in self.children:
            child.prefix_mark_out()

    def postfix_draw(self, print_per_line, height=0):
        CASE_SIZE = 100
        START = (300, 250)
        BETWEEN_CASE = 12
        STAGE_HEIGHT = 120
        LINK_LINE_WIDTH = 2

        upper_line_printed = 0
        for child in self.children:
            print_per_line = child.postfix_draw(print_per_line, height+1)
            upper_line_printed += 1

        height_tree = self.get_height()
        x1 = 2**height_tree * (CASE_SIZE + BETWEEN_CASE) // 2 - CASE_SIZE // 2
        x2 = 2**(height_tree+1) * (CASE_SIZE + BETWEEN_CASE) // 2 - CASE_SIZE // 2

        coefficient = print_per_line[height] // 2
        x3 = (2**2 * (CASE_SIZE + BETWEEN_CASE) // 2 - CASE_SIZE // 2 + CASE_SIZE // 2) * coefficient

        if self.value.upper_state:
            if self.value.player_get:
                color = Engine.GREEN
            else:
                color = Engine.GOLD
        else:
            color = Engine.WHITE

        if print_per_line[height] % 2 == 0:
            X = START[0] + x1 + x3
            Y = START[1] + height * STAGE_HEIGHT
            pygame.draw.rect(screen, (255, 255, 255), (X, Y, CASE_SIZE, CASE_SIZE))
            if height > 0:
                pygame.draw.line(screen, color, (X + CASE_SIZE // 2, Y - STAGE_HEIGHT + CASE_SIZE // 2),
                             (X + CASE_SIZE // 2 + (x2 - x1), Y - STAGE_HEIGHT + CASE_SIZE // 2), LINK_LINE_WIDTH)
        else:
            X = START[0] + CASE_SIZE + x2 - (CASE_SIZE - (x2-x1)) + x3
            Y = START[1] + height * STAGE_HEIGHT

            pygame.draw.rect(screen, (255, 255, 255), (X, Y, CASE_SIZE, CASE_SIZE))
            pygame.draw.line(screen, color, (X + CASE_SIZE // 2, Y - STAGE_HEIGHT + CASE_SIZE // 2),
                             (X + CASE_SIZE // 2 + (x1 - x2), Y - STAGE_HEIGHT + CASE_SIZE // 2), LINK_LINE_WIDTH)
        if height > 0:
            pygame.draw.line(screen, color, (X + CASE_SIZE // 2, Y), (X + CASE_SIZE // 2, Y - STAGE_HEIGHT + CASE_SIZE //2), LINK_LINE_WIDTH)

        screen.blit(self.value.image, (X + 3, Y + 3))

        print_per_line[height] += 1
        return print_per_line

    def postfix_define_buttons(self, print_per_line, height=0, upper_state=True):
        CASE_SIZE = 100

        START = (300, 250)
        BETWEEN_CASE = 12
        STAGE_HEIGHT = 120

        self.value.upper_state = upper_state
        upper_line_printed = 0
        for child in self.children:
            print_per_line = child.postfix_define_buttons(print_per_line, height+1, self.value.player_get)
            upper_line_printed += 1

        height_tree = self.get_height()
        x1 = 2**height_tree * (CASE_SIZE + BETWEEN_CASE) // 2 - CASE_SIZE // 2
        x2 = 2**(height_tree+1) * (CASE_SIZE + BETWEEN_CASE) // 2 - CASE_SIZE // 2

        coefficient = print_per_line[height] // 2
        x3 = (2**2 * (CASE_SIZE + BETWEEN_CASE) // 2 - CASE_SIZE // 2 + CASE_SIZE // 2) * coefficient

        if print_per_line[height] % 2 == 0:
            X = START[0] + x1 + x3
            Y = START[1] + height * STAGE_HEIGHT
        else:
            X = START[0] + CASE_SIZE + x2 - (CASE_SIZE - (x2-x1)) + x3
            Y = START[1] + height * STAGE_HEIGHT

        if self.value.player_get:
            buttons.append(Button((X, Y, CASE_SIZE, CASE_SIZE), None, None, Engine.GREEN, 36, Engine.GREEN,
                              Engine.GREEN, self.value))
        elif upper_state:
            buttons.append(Button((X, Y, CASE_SIZE, CASE_SIZE), None, None, Engine.LIGHT_BLUE, 36, Engine.GOLD,
                              Engine.LIGHT_RED, self.value))
        else:
            buttons.append(Button((X, Y, CASE_SIZE, CASE_SIZE), None, None, Engine.DARK_GREY, 36, Engine.DARK_GREY,
                                  Engine.DARK_GREY, self.value))

        print_per_line[height] += 1
        return print_per_line

    def reset_talent(self):
        self.value.player_get = False
        self.value.upper_state = False

        for child in self.children:
            child.reset_talent()


ROOT = TS_Skill(T_Bomb)
ROOT.add_child(TS_Skill(T_Tact))
ROOT.add_child(TS_Skill(T_Fireworks))

ROOT.children[0].add_child(TS_Skill(T_ProtectBomb))
ROOT.children[0].add_child(TS_Skill(T_ChainDeath))
ROOT.children[1].add_child(TS_Skill(T_master_fireworks))
ROOT.children[1].add_child(TS_Skill(T_Fragmentation))

screen = pygame.display.set_mode((1280, 720))


def change_talent():
    global buttons
    buttons = []
    ROOT.postfix_define_buttons([0 for _ in range(ROOT.get_height() + 1)])
    triggered = False

    talent_in_load = None
    talent_info_font = pygame.font.Font("assets/font/text.ttf", 25)
    talent_info_small_font = pygame.font.Font("assets/font/text.ttf", 14)

    crystal_logo = pygame.image.load("assets/HUD/crystal_logo.png")
    money_logo = pygame.image.load("assets/HUD/lumus_logo.png")

    Engine.instance.display(Player.instance, False, False)

    gameplay_image = pygame.display.get_surface().copy()
    black_screen_lo = pygame.image.load("assets/HUD/black_screen_low_opacity.png").convert_alpha()

    talent = pygame.image.load("assets/HUD/talent.png").convert_alpha()

    open_time = time.perf_counter()

    while True:

        screen.blit(gameplay_image, (0, 0))
        screen.blit(black_screen_lo, (0, 0))
        screen.blit(talent, (0, 0))

        talent_point_text = talent_info_small_font.render("Pts : " + str(Player.instance.talent_point), True, Engine.WHITE)
        screen.blit(talent_point_text, (1200, 10))

        crystal_point_text = talent_info_small_font.render(str(Player.instance.inventory.crystals), True,
                                                          Engine.WHITE)
        screen.blit(crystal_point_text, (1223, 33))
        screen.blit(crystal_logo, (1200, 30))

        money_point_text = talent_info_small_font.render(str(Player.instance.inventory.money), True,
                                                          Engine.WHITE)
        screen.blit(money_point_text, (1223, 53))
        screen.blit(money_logo, (1200, 52))

        mouse_coordinates = pygame.mouse.get_pos()

        ROOT.postfix_draw([0 for _ in range(ROOT.get_height() + 1)])

        for button in buttons:
            button.display()
            if button.is_on(mouse_coordinates) and button.is_triggered(triggered):
                if button.content is not None:
                    if talent_in_load is not None:
                        buttons.remove(buttons[len(buttons) - 1])
                    talent_in_load = button.content
                    if talent_in_load.player_get:
                        buttons.append(Button((850, 500, 300, 60), None, "Acquis",
                                              Engine.GREEN, 25, Engine.GREEN, Engine.GREEN))
                    elif talent_in_load.upper_state:
                        buttons.append(Button((850, 500, 300, 60), None, "Débloquer le talent !",
                                              Engine.LIGHT_BLUE, 25, Engine.GOLD))
                    else:
                        buttons.append(Button((850, 500, 300, 60), None, "Indisponible",
                                              Engine.LIGHT_RED, 25, Engine.LIGHT_RED))
                else:
                    if not talent_in_load.player_get and talent_in_load.upper_state:
                        if Player.instance.inventory.try_to_remove_money(talent_in_load.price[0]) and Player.instance.\
                                inventory.try_to_remove_crystals(talent_in_load.price[1]) and \
                                Player.instance.talent_point > 0:
                            talent_in_load.talent()
                            Player.instance.inventory.remove_money(talent_in_load.price[0])
                            Player.instance.inventory.remove_crystals(talent_in_load.price[1])
                            Player.instance.talent_point -= 1
                            talent_in_load.player_get = True
                            buttons = []
                            ROOT.postfix_define_buttons([0 for _ in range(ROOT.get_height() + 1)])
                            talent_in_load = None

        if talent_in_load is not None:
            talent_text_name = talent_info_font.render(talent_in_load.name, True, Engine.GOLD)
            screen.blit(talent_text_name, (800, 300))

            line = 0
            for text_line in talent_in_load.description:
                text = talent_info_small_font.render(text_line, True, Engine.WHITE)
                screen.blit(text, (810, 340 + line * 20))
                line += 1

            screen.blit(crystal_logo, (837, 430))
            if Player.instance.inventory.crystals >= talent_in_load.price[1]:
                color = Engine.WHITE
            else:
                color = Engine.LIGHT_RED
            crystal_text = talent_info_small_font.render(str(talent_in_load.price[1]), True, color)
            screen.blit(crystal_text, (864, 430))

            screen.blit(money_logo, (903, 430))
            if Player.instance.inventory.money >= talent_in_load.price[0]:
                color = Engine.WHITE
            else:
                color = Engine.LIGHT_RED
            money_text = talent_info_small_font.render(str(talent_in_load.price[0]), True, color)
            screen.blit(money_text, (930, 430))

            if Player.instance.talent_point > 0:
                color = Engine.WHITE
            else:
                color = Engine.LIGHT_RED
            need_pts_text = talent_info_small_font.render("1 Pts requis", True, color)
            screen.blit(need_pts_text, (980, 430))

        screen.blit(HUD.cursor_image, (mouse_coordinates[0] - HUD.cursor_image.get_width() // 2,
                                         mouse_coordinates[1] - HUD.cursor_image.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                triggered = True
            elif event.type == pygame.MOUSEBUTTONUP:
                triggered = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    for item_type, item in Inventory.instance.inventory.items():
                        if isinstance(item, Item_with_CD) and item.start_time is not None:
                            item.start_time += time.perf_counter() - open_time
                    return


def reset_tree_talent():
    BOMB_SPELL.reset_spell()
    ROOT.reset_talent()
