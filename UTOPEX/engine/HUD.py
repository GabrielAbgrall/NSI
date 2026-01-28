import pygame
import os

from entity.player.Player import Player
from entity.player.Inventory import Inventory
from entity.enemy.Enemy import *
from game.GameManager import *


class HUD:
    # HUD IMAGES
    cursor_image = pygame.image.load(os.path.join("assets", "HUD", "cursor.png"))
    visor_cursor_image = pygame.image.load(os.path.join("assets", "HUD", "visor_cursor.png"))

    border_health_bar = pygame.image.load(os.path.join("assets", "HUD", "border_health_bar.png"))
    health_bar_heart = pygame.image.load(os.path.join("assets", "HUD", "health_bar_heart.png"))
    big_case_item = pygame.image.load(os.path.join("assets", "HUD", "big_case_item.png"))
    small_case_item = pygame.image.load(os.path.join("assets", "HUD", "small_case_item.png"))
    small_case_item_use = pygame.image.load(os.path.join("assets", "HUD", "small_case_item_use.png"))

    effect_case = pygame.image.load(os.path.join("assets", "HUD", "effect_case.png"))

    infinite_logo = pygame.image.load(os.path.join("assets", "HUD", "infinite_ammo.png"))

    resources_hud = pygame.image.load(os.path.join("assets", "HUD", "resources_hud.png"))

    crystal_logo = pygame.image.load(os.path.join("assets", "HUD", "crystal_logo.png"))
    money_logo = pygame.image.load(os.path.join("assets", "HUD", "lumus_logo.png"))

    objective_hud = pygame.image.load(os.path.join("assets", "HUD", "objective", "objective_hud.png"))
    objective_logo_hud = pygame.image.load(os.path.join("assets", "HUD", "objective", "objective_logo.png"))
    main_objective_logo_hud = pygame.image.load(os.path.join("assets", "HUD", "objective", "main_objective_logo.png"))

    boss_life_hud = pygame.image.load(os.path.join("assets", "HUD", "boss_life_hud.png"))
    boss_head_logo = pygame.image.load(os.path.join("assets", "HUD", "boss_head_logo.png"))

    build_info_hud = pygame.image.load(os.path.join("assets", "HUD", "build_info_hud.png"))

    # HUD FONT
    small_item_font = pygame.font.Font(os.path.join("assets", "font", "font_item.ttf"), 10)
    big_item_font = pygame.font.Font(os.path.join("assets", "font", "font_item.ttf"), 12)
    resources_font = pygame.font.Font(os.path.join("assets", "font", "font_item.ttf"), 12)
    receive_resources_font = pygame.font.Font(os.path.join("assets", "font", "font_item.ttf"), 18)
    big_ammo_font = pygame.font.Font(os.path.join("assets", "font", "font_item.ttf"), 24)
    small_item_font_info = pygame.font.Font(os.path.join("assets", "font", "font_item.ttf"), 18)

    objective_type_font = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 10)
    main_objective_description_font = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 14)
    objective_description_font = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 12)

    lvl_font = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 18)
    timer_font = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 35)

    # CONSTANT
    SMALL_CASE_SIZE = 64
    BIG_CASE_SIZE = 92

    # DISPLAY LAST AMOUNT OF RESOURCES GET BY THE PLAYER
    CRYSTALS_RECEPTION = None
    CRYSTALS_RECEPTION_START = None

    MONEY_RECEPTION = None
    MONEY_RECEPTION_START = None

    EXP_RECEPTION = None
    EXP_RECEPTION_START = None

    PRINT_RECEPTION_TIME = 5

    # ANIMATION STATES :    ( 0: In progress, 1: start_time, 2: duration)
    FLASH_SCREEN = [False, 0, 0]

    def __init__(self):
        pass

    @classmethod
    def receive_crystals(cls, amount: int):
        if cls.CRYSTALS_RECEPTION is None:
            cls.CRYSTALS_RECEPTION = amount
        else:
            cls.CRYSTALS_RECEPTION += amount

        cls.CRYSTALS_RECEPTION_START = time.perf_counter()

    @classmethod
    def receive_money(cls, amount: int):
        if cls.MONEY_RECEPTION is None:
            cls.MONEY_RECEPTION = amount
        else:
            cls.MONEY_RECEPTION += amount

        cls.MONEY_RECEPTION_START = time.perf_counter()

    @classmethod
    def receive_exp(cls, amount: int):
        if cls.EXP_RECEPTION is None:
            cls.EXP_RECEPTION = amount
        else:
            cls.EXP_RECEPTION += amount

        cls.EXP_RECEPTION_START = time.perf_counter()

    @staticmethod
    def animation_control(ANIMATION):
        if time.perf_counter() >= ANIMATION[1] + ANIMATION[2]:
            ANIMATION[0] = False

    @staticmethod
    def launch_animation(ANIMATION, duration):
        ANIMATION[0] = True
        ANIMATION[1] = time.perf_counter()
        ANIMATION[2] = duration

    @staticmethod
    def flash_screen():
        HUD.animation_control(HUD.FLASH_SCREEN)
        pygame.draw.rect(Engine.instance.screen, Engine.WHITE, (0, 0, Engine.SCREEN_SIZE[0], Engine.SCREEN_SIZE[1]))

    @staticmethod
    def display(display_cursor=True, display_timer=True):
        e = Engine.instance
        p = Player.instance
        i = Inventory.instance
        gm = GameManager.instance
        mouse_coordinate = pygame.mouse.get_pos()

        if HUD.FLASH_SCREEN[0]:
            HUD.flash_screen()

        # PRINT ALL ENEMIES HEALTH BAR
        for entity in e.entities:
            if not isinstance(entity, (Player, Boss)) and entity.health != entity.max_health:
                pos = e.screen_coordinates(entity.pos)
                pos = (pos[0] - entity.image.get_width() // 2, pos[1] - entity.image.get_height())
                pygame.draw.rect(e.screen, (200, 200, 200), (pos[0] - (Enemy.HEALTH_BAR_LEN - entity.image.get_width())
                                                             // 2,
                                                             pos[1] - Enemy.HEALTH_BAR_HEIGHT - 3
                                                             , Enemy.HEALTH_BAR_LEN, Enemy.HEALTH_BAR_HEIGHT), 2)

                color = HUD.get_color_state_progression(entity.health, entity.max_health)
                pygame.draw.rect(e.screen, color,
                                 ((pos[0] - (Enemy.HEALTH_BAR_LEN - entity.image.get_width()) // 2) + 2,
                                  pos[1] - Enemy.HEALTH_BAR_HEIGHT - 1
                                  , (Enemy.HEALTH_BAR_LEN - 3) * (entity.health / entity.max_health),
                                  Enemy.HEALTH_BAR_HEIGHT - 3))

            if isinstance(entity, Boss):
                e.screen.blit(HUD.boss_life_hud, (539, 567))

                pygame.draw.rect(e.screen, Engine.LIGHT_RED, (559, 617, 309 * (entity.health / entity.max_health), 25))
                e.screen.blit(HUD.boss_head_logo, (566, 612))

                offset = HUD.give_text_offset_w(entity.name, 24, os.path.join("assets", "font", "text.ttf"))
                HUD.dropShadowText(entity.name, 24, 539 + (120 - offset) // 2, 570, Engine.LIGHT_YELLOW,
                                   Engine.DARK_GREY, os.path.join("assets", "font", "text.ttf"), 2)

        # PRINT ALL BUILDS LIFE BAR
        for build in e.builds:
            if build.life != build.max_life:
                pos = e.screen_coordinates(build.pos)
                texture = build.get_display_texture()
                pos = (pos[0] - texture.get_width() // 2, pos[1] - texture.get_height())
                pygame.draw.rect(e.screen, (200, 200, 200), (pos[0] - (Enemy.HEALTH_BAR_LEN - texture.get_width())
                                                             // 2,
                                                             pos[1] - Enemy.HEALTH_BAR_HEIGHT - 3
                                                             , Enemy.HEALTH_BAR_LEN, Enemy.HEALTH_BAR_HEIGHT), 2)

                color = HUD.get_color_state_progression(build.life, build.max_life)
                pygame.draw.rect(e.screen, color,
                                 ((pos[0] - (Enemy.HEALTH_BAR_LEN - texture.get_width()) // 2) + 2,
                                  pos[1] - Enemy.HEALTH_BAR_HEIGHT - 1
                                  , (Enemy.HEALTH_BAR_LEN - 3) * (build.life / build.max_life),
                                  Enemy.HEALTH_BAR_HEIGHT - 3))

            if isinstance(build, Interaction_Build) and e.plane.distance(build.pos, p.pos) <= build.collision_radius:
                HUD.display_interaction_build_info(build)

        if e.plane.distance(e.core.pos, p.pos) <= e.core.collision_radius:
            HUD.display_interaction_build_info(e.core)

        # PRINT HEALTH BAR
        e.screen.blit(HUD.border_health_bar, (44, 620))
        pygame.draw.rect(e.screen, Engine.LIGHT_RED, (55, 632, 338 * (p.health / p.max_health), 35))
        e.screen.blit(HUD.health_bar_heart, (44, 620))

        # PRINT INVENTORY CASE
        e.screen.blit(HUD.big_case_item, (48, 519))
        if i.inventory["weapon"] is not None:
            e.screen.blit(i.inventory["weapon"].image, (48 + (92 - i.inventory["weapon"].image.get_width()) // 2, 519 +
                                                        (57 - i.inventory["weapon"].image.get_height()) // 2 + 5))
            weapon_item_text = HUD.big_item_font.render(i.inventory["weapon"].name, True, Engine.BLACK)
            e.screen.blit(weapon_item_text, (48 + (HUD.BIG_CASE_SIZE - weapon_item_text.get_width()) // 2, 576))

            if i.inventory["weapon"].ammo is not None:
                ammo_item_text = HUD.big_ammo_font.render(str(i.inventory["weapon"].ammo), True, Engine.LIGHT_BLUE)
                e.screen.blit(ammo_item_text, (48 + (HUD.BIG_CASE_SIZE - ammo_item_text.get_width()) // 2, 587))
            else:
                e.screen.blit(HUD.infinite_logo, (80, 589))

        e.screen.blit(HUD.small_case_item, (151, 540))
        if i.inventory["unique"] is not None:
            e.screen.blit(i.inventory["unique"].image, (162, 550))

            utility_item_text = HUD.small_item_font.render(i.inventory["unique"].name, True, Engine.BLACK)
            e.screen.blit(utility_item_text, (153 + (HUD.SMALL_CASE_SIZE - utility_item_text.get_width()) // 2, 591))

            if i.inventory["unique"].start_time is not None:
                case_use_box = pygame.transform.scale(HUD.small_case_item_use, (HUD.small_case_item_use.get_width(),
                                                                                abs(int(HUD.small_case_item_use.get_height()
                                                                                    * (1 - (time.perf_counter() -
                                                                                            i.inventory[
                                                                                                "unique"].start_time) /
                                                                                       i.inventory[
                                                                                           "unique"].cd)))))
                e.screen.blit(case_use_box,
                              (153, 542 + HUD.small_case_item_use.get_height() - case_use_box.get_height()))

        e.screen.blit(HUD.small_case_item, (229, 540))
        if i.inventory["utility"] is not None:
            e.screen.blit(i.inventory["utility"].image, (240, 550))

            utility_item_text = HUD.small_item_font.render(i.inventory["utility"].name, True, Engine.BLACK)
            e.screen.blit(utility_item_text, (231 + (HUD.SMALL_CASE_SIZE - utility_item_text.get_width()) // 2, 591))

            utility_item_usage_text = HUD.small_item_font_info.render(str(i.inventory["utility"].usage), True,
                                                                      Engine.BLACK)
            e.screen.blit(utility_item_usage_text, (237, 544))
            if i.inventory["utility"].start_time is not None:
                case_use_box = pygame.transform.scale(HUD.small_case_item_use, (HUD.small_case_item_use.get_width(),
                                                                                int(HUD.small_case_item_use.get_height()
                                                                                    * (1 - (time.perf_counter() -
                                                                                            i.inventory[
                                                                                                "utility"].start_time) /
                                                                                       i.inventory[
                                                                                           "utility"].cd))))
                e.screen.blit(case_use_box,
                              (231, 542 + HUD.small_case_item_use.get_height() - case_use_box.get_height()))

        e.screen.blit(HUD.big_case_item, (304, 519))
        if i.inventory["spell"] is not None:
            e.screen.blit(i.inventory["spell"].image, (304 +
                                                       (HUD.BIG_CASE_SIZE - i.inventory[
                                                           "spell"].image.get_width()) // 2, 530))
            spell_item_text = HUD.big_item_font.render(i.inventory["spell"].name, True, Engine.BLACK)
            e.screen.blit(spell_item_text, (307 + (HUD.BIG_CASE_SIZE - spell_item_text.get_width()) // 2, 576))

            spell_pack_text = HUD.big_item_font.render(str(i.inventory["spell"].stack), True, Engine.BLACK)
            e.screen.blit(spell_pack_text, (309 + (HUD.BIG_CASE_SIZE - spell_item_text.get_width()) // 2, 525))

            if i.inventory["spell"].start_time is not None:
                pygame.draw.rect(e.screen, Engine.DARK_GREY, (314, 605, 76, 6), 3)
                pygame.draw.rect(e.screen, Engine.LIGHT_BLUE, (315, 607, 76 *
                                                               ((time.perf_counter() - i.inventory["spell"].start_time)
                                                                / i.inventory["spell"].cd), 2))

        # PRINT RESOURCES HUD
        _time = time.perf_counter()
        e.screen.blit(HUD.resources_hud, (44, 366))

        color = Engine.BLACK  # MONEY
        if i.money >= 999:
            color = Engine.GREEN
        money_text = HUD.resources_font.render(str(i.money), True, color)
        e.screen.blit(money_text, (88 + (20 - money_text.get_width()) // 2, 416))
        if HUD.MONEY_RECEPTION is not None:
            if _time - HUD.MONEY_RECEPTION_START >= HUD.PRINT_RECEPTION_TIME:
                HUD.MONEY_RECEPTION_START = None
                HUD.MONEY_RECEPTION = None
            else:
                money_reception_text = HUD.receive_resources_font.render("+" + str(HUD.MONEY_RECEPTION), True,
                                                                         Engine.GOLD)
                e.screen.blit(money_reception_text, (120, 418))

        color = Engine.BLACK  # CRYSTAL
        if i.crystals >= 999:
            color = Engine.GREEN
        crystal_text = HUD.resources_font.render(str(i.crystals), True, color)
        e.screen.blit(crystal_text, (88 + (20 - crystal_text.get_width()) // 2, 484))
        if HUD.CRYSTALS_RECEPTION is not None:
            if _time - HUD.CRYSTALS_RECEPTION_START >= HUD.PRINT_RECEPTION_TIME:
                HUD.CRYSTALS_RECEPTION_START = None
                HUD.CRYSTALS_RECEPTION = None
            else:
                crystal_reception_text = HUD.receive_resources_font.render("+" + str(HUD.CRYSTALS_RECEPTION), True,
                                                                           Engine.PURPLE)
                e.screen.blit(crystal_reception_text, (120, 486))

        pygame.draw.rect(e.screen, (200, 200, 200),  # EXP
                         (74, 692, 300, 10), 3)
        pygame.draw.rect(e.screen, Engine.GOLD,
                         (77, 695, 295 * (p.experience / p.experience_required), 4))

        lvl_text = HUD.lvl_font.render("Lvl." + str(p.lvl), True, Engine.WHITE)
        e.screen.blit(lvl_text, (20, 685))

        if HUD.EXP_RECEPTION is not None:
            if _time - HUD.EXP_RECEPTION_START >= HUD.PRINT_RECEPTION_TIME:
                HUD.EXP_RECEPTION_START = None
                HUD.EXP_RECEPTION = None
            else:
                exp_reception_text = HUD.receive_resources_font.render("+" + str(HUD.EXP_RECEPTION), True,
                                                                       Engine.ORANGE)
                e.screen.blit(exp_reception_text, (390, 690))

        # PRINT EFFECT TIME
        line = 0
        for effect in p.effects:
            e.screen.blit(HUD.effect_case, (22 + line * 45, 70, 38, 38))
            pygame.draw.rect(e.screen, Engine.LIGHT_RED, (22 + line * 45, 70, 38, 38), 3)
            e.screen.blit(effect.image, (22 + line * 45, 70))

            remaining_time = int(effect.duration - (_time - effect.start_time))
            remaining_time_text = HUD.lvl_font.render(str(remaining_time) + "s", True, Engine.WHITE)
            e.screen.blit(remaining_time_text, (22 + line * 45 + (38 - remaining_time_text.get_width()) // 2, 108))

            line += 1

        # PRINT TIMER
        if display_timer:
            if gm.timer < gm.launch_cooldown:
                HUD.display_timer(gm.launch_cooldown - gm.timer)
            elif gm.wave_timer < gm.wave_cooldown:
                HUD.display_timer(gm.wave_cooldown - gm.wave_timer)

        # PRINT WAVES COUNTER
        if gm.infinite_wave:
            HUD.display_counter(gm.waves_accomplished + 1)

        # PRINT CORE HUD (LIFE, ...)
        color = HUD.get_color_state_progression(e.core.life, e.core.max_life)
        pygame.draw.rect(e.screen, (200, 200, 200),
                         ((e.screen.get_size()[0] - Core.CORE_LIFE_BAR_LEN) // 2, 5, 702, 20), 3)
        if e.core.life > 0:
            pygame.draw.rect(e.screen, color, ((e.screen.get_size()[0] - Core.CORE_LIFE_BAR_LEN) // 2 + 1, 6,
                                               Core.CORE_LIFE_BAR_LEN * (e.core.life / e.core.max_life), 18))

        # PRINT OBJECTIVE
        e.screen.blit(HUD.objective_hud, (1037, 633))
        e.screen.blit(HUD.main_objective_logo_hud, (1052, 646))
        objective_type_text = HUD.objective_type_font.render("Objectif principal", True, Engine.LIGHT_RED2)
        e.screen.blit(objective_type_text, (1099, 649))

        main_objective_description__text = HUD.main_objective_description_font.render(e.main_objective.description,
                                                                                      True, Engine.LIGHT_RED2)
        e.screen.blit(main_objective_description__text, (1096, 661))

        objective_amount = 0
        for objective in e.objectives:
            e.screen.blit(HUD.objective_hud, (1037, 564 - 69 * objective_amount))
            e.screen.blit(HUD.objective_logo_hud, (1052, 577 - 69 * objective_amount))
            e.screen.blit(objective.logo, (1062, 584 - 69 * objective_amount))
            objective_type_text = HUD.objective_type_font.render("Objectif secondaire", True, Engine.LIGHT_BLUE)
            e.screen.blit(objective_type_text, (1099, 580 - 69 * objective_amount))

            objective_description__text = HUD.objective_description_font.render(objective.description,
                                                                                True, Engine.LIGHT_BLUE)
            e.screen.blit(objective_description__text, (1096, 592 - 69 * objective_amount))

            if objective.start_time is not None:
                remaining_time = objective.duration - (time.perf_counter() - objective.start_time)
                HUD.display_custom_timer(remaining_time, 12, (1052, 613 - 69 * objective_amount, 36, 9), Engine.BLACK)

            required_str = f"{objective.actual_rate} / {objective.required_rate}"
            required_text = HUD.objective_description_font.render(required_str, True, Engine.BLACK)
            e.screen.blit(required_text, (1139, 607 - 69 * objective_amount))

            loot_img = HUD.crystal_logo if objective.loot[0] >= objective.loot[1] else HUD.money_logo
            printed_loot_str = str(objective.loot[0]) if objective.loot[0] >= objective.loot[1] else str(
                objective.loot[1])
            loot_img = pygame.transform.scale(loot_img, (15, 15))
            e.screen.blit(loot_img, (1212, 570 - 69 * objective_amount))
            printed_loot_text = HUD.objective_description_font.render(printed_loot_str, True, Engine.BLACK)
            e.screen.blit(printed_loot_text, (1229, 571 - 69 * objective_amount))

            objective_amount += 1

        # PRINT CURSOR
        if display_cursor:
            if not p.visor_mode:
                e.screen.blit(HUD.cursor_image, (mouse_coordinate[0] - HUD.cursor_image.get_width() // 2,
                                                 mouse_coordinate[1] - HUD.cursor_image.get_height() // 2))
            else:

                pos = e.screen_coordinates(p.pos)
                e.screen.blit(HUD.visor_cursor_image,
                              (mouse_coordinate[0] - HUD.visor_cursor_image.get_width() // 2,
                               mouse_coordinate[1] - HUD.visor_cursor_image.get_height() // 2))
                pygame.draw.line(e.screen, Engine.WHITE, mouse_coordinate,
                                 (pos[0] - p.image.get_width() // 2 + 10, pos[1] - p.image.get_height() + 10))

    @staticmethod
    def get_color_state_progression(life, max_life):
        base_color = (25, 255, 25)

        coefficient = (460 / max_life) * (max_life - life)

        test = base_color[0] + coefficient

        if test < 235:
            color = (int(base_color[0] + coefficient), 255, 25)
        else:
            color = (235, base_color[1] - coefficient + 210, 25)

        return color

    @staticmethod
    def display_timer(remaining_time):
        e = Engine.instance

        amount_of_min = remaining_time // 60
        amount_of_sec = remaining_time - (amount_of_min * 60)

        pygame.draw.rect(e.screen, Engine.DARK_GREY, (1108, 18, 138, 42))
        pygame.draw.rect(e.screen, Engine.LIGHT_RED, (1108, 18, 138, 42), 3)

        temp1 = ""
        temp2 = ""
        if amount_of_min < 10:
            temp1 = "0"
        if amount_of_sec < 10:
            temp2 = "0"
        printed_str = temp1 + str(int(amount_of_min)) + ":" + temp2 + str(int(amount_of_sec))
        remaining_time_text = HUD.timer_font.render(printed_str, True, Engine.WHITE)

        e.screen.blit(remaining_time_text, (1108 + (138 - remaining_time_text.get_width()) // 2, 18))

    @staticmethod
    def display_counter(amount):
        e = Engine.instance

        pygame.draw.rect(e.screen, Engine.DARK_GREY, (80, 18, 70, 42))
        pygame.draw.rect(e.screen, Engine.LIGHT_RED, (80, 18, 70, 42), 3)

        remaining_time_text = HUD.timer_font.render(str(amount), True, Engine.WHITE)
        e.screen.blit(remaining_time_text, (80 + (70 - remaining_time_text.get_width()) // 2, 18))

    @staticmethod
    def display_interaction_build_info(build):
        e = Engine.instance

        pos = e.screen_coordinates(build.pos)
        new_pos = (pos[0] + 10, pos[1] - build.texture.get_height() // 2 - HUD.build_info_hud.get_height())
        HUD.display_world_info(new_pos, build.name, build.on_content)

    @staticmethod
    def display_world_info(pos: tuple, info_name: str, info_content: list):
        e = Engine.instance

        e.screen.blit(HUD.build_info_hud, pos)

        HUD.dropShadowText(info_name, 16, pos[0] + HUD.build_info_hud.get_width() - 
                           HUD.give_text_offset_w(info_name, 16, os.path.join("assets", "font", "text.ttf")) - 2, pos[1] - 20,
                           Engine.LIGHT_YELLOW, Engine.DARK_GREY, os.path.join("assets", "font", "text.ttf"))

        for line, text_line in enumerate(info_content):
            text_line, command = HUD.test_command_into_text(text_line)
            final_text = "> " + text_line

            final_render = HUD.dropShadowText(final_text, 10, pos[0] + 34, pos[1] + 8 + 12 * line,
                                              Engine.LIGHT_YELLOW, Engine.DARK_GREY, os.path.join("assets", "font", "text.ttf"))

            if command is not None:
                if command == "c":
                    c_logo = pygame.transform.scale(HUD.crystal_logo, (11, 11))
                    e.screen.blit(c_logo, (pos[0] + 34 + final_render.get_width(), pos[1] + 8 + 12 * line))

                if command == "m":
                    m_logo = pygame.transform.scale(HUD.money_logo, (12, 12))
                    e.screen.blit(m_logo, (pos[0] + 34 + final_render.get_width(), pos[1] + 8 + 12 * line))

                if command == "i":
                    pygame.draw.rect(e.screen, Engine.DARK_GREY, ((pos[0] + 37 + final_render.get_width(),
                                                               pos[1] + 8 + 12 * line, 12, 12)))
                    pygame.draw.rect(e.screen, Engine.LIGHT_YELLOW, ((pos[0] + 37 + final_render.get_width(),
                                                               pos[1] + 8 + 12 * line, 12, 12)), 1)
                    input_render = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 8).render("E", True, Engine.LIGHT_YELLOW)
                    e.screen.blit(input_render, (pos[0] + 40 + final_render.get_width(),
                                                               pos[1] + 9 + 12 * line))

    @staticmethod
    def test_command_into_text(text: str) -> tuple:
        if text[-2] == "/":
            return text[:-2], text[-1]
        else:
            return text, None

    @staticmethod
    def display_custom_timer(remaining_time, text_height: int, rect_pos: tuple, color=Engine.WHITE):
        e = Engine.instance

        font = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), text_height)

        amount_of_min = remaining_time // 60
        amount_of_sec = remaining_time - (amount_of_min * 60)

        temp1 = ""
        temp2 = ""
        if amount_of_min < 10:
            temp1 = "0"
        if amount_of_sec < 10:
            temp2 = "0"

        printed_str = temp1 + str(int(amount_of_min)) + ":" + temp2 + str(int(amount_of_sec))
        remaining_time_text = font.render(printed_str, True, color)

        e.screen.blit(remaining_time_text, (rect_pos[0] + (rect_pos[2] - remaining_time_text.get_width()) // 2,
                                            rect_pos[1] + (rect_pos[3] - remaining_time_text.get_height()) // 2))

    @staticmethod
    def give_text_offset_w(text: str, size: int, font: str):
        return pygame.font.Font(font, size).render(text, False, Engine.DARK_GREY).get_width()

    @staticmethod
    def give_text_offset_h(text: str, size: int, font: str):
        return pygame.font.Font(font, size).render(text, False, Engine.DARK_GREY).get_height()

    @staticmethod
    def dropShadowText(text, size, x, y, colour=(255, 255, 255), shadow_colour=Engine.DARK_GREY, font=None,
                       shadow_thickness=4):
        e = Engine.instance

        # create font with the parameters
        text_font = pygame.font.Font(font, size)

        # make the drop-shadow
        text_bitmap = text_font.render(text, True, shadow_colour)

        for i in range(0, shadow_thickness):
            shadow_offset = i+1 + (size // 15)
            e.screen.blit(text_bitmap, (x + shadow_offset, y + shadow_offset))

        # display regular text
        text_bitmap = text_font.render(text, True, colour)
        e.screen.blit(text_bitmap, (x, y))

        return text_bitmap
