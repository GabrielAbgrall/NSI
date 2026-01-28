import pygame
import sys
import os

from engine.HUD import *
from engine.Button import *
from entity.player.Item import *


class Shop_Button(Button):
    FONT = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 18)
    TYPE_FONT = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 8)
    PRICE_FONT = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 20)

    RECT_SIZE = (120, 140)

    type_of_item_color = {
        "PISTOL": Engine.GREEN,
        "SHOTGUN": Engine.RED,
        "RIFLE": Engine.GOLD,
        "SNIPER": Engine.DARK_BLUE2,
        "UTILITY": Engine.PURPLE,
        "LAUNCHER": Engine.ORANGE
    }

    BUTTON_AMOUNT = 0

    def __init__(self, item, price, function_execute=None):

        rect = (396 + (Shop_Button.BUTTON_AMOUNT % 3 * 136), 175 + (Shop_Button.BUTTON_AMOUNT // 3 * 154),
                Shop_Button.RECT_SIZE[0], Shop_Button.RECT_SIZE[1])

        super().__init__(rect)
        self.base_rect = copy.copy(self.rect)

        self.item = item
        self.price = price

        self.function_execute = function_execute

        Shop_Button.BUTTON_AMOUNT += 1

    def display(self):

        self.rect = copy.copy(self.base_rect)
        self.rect.y -= actual_stage

        if self.rect.colliderect(SHOP_RECT):
            e = Engine.instance
            p = Player.instance
            color = Engine.LIGHT_BLUE

            if p.inventory.money < self.price:
                color = Engine.LIGHT_RED

            if self.on:
                is_on_color = Engine.WHITE
            else:
                is_on_color = color
            pygame.draw.rect(e.screen, is_on_color, self.rect, 3)
            pygame.draw.rect(e.screen, color, (self.rect.x + 7, self.rect.y + 95, 106, 30), 2)

            j = 0
            while True:
                FONT = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 18 - j)
                item_text = FONT.render(self.item.name, True, color)
                if item_text.get_width() < 110:
                    break
                j += 2
            e.screen.blit(item_text, (self.rect.x + (Shop_Button.RECT_SIZE[0] - item_text.get_width()) // 2,
                                      self.rect.y + 70))

            # e.screen.blit(self.item.shop_image, (self.rect.x + 10, self.rect.y - 15))
            e.screen.blit(self.item.shop_image, (self.rect.x + (self.rect.width -
                                                                self.item.shop_image.get_width()) // 2,
                                                 self.rect.y + (55 - self.item.shop_image.get_height()) // 2 + 7))

            if isinstance(self.item, Weapon):
                item_type = self.item.weapon_type
            else:
                item_type = "UTILITY"
            item_type_text = Shop_Button.TYPE_FONT.render(item_type, True,
                                                          Shop_Button.type_of_item_color[item_type])
            e.screen.blit(item_type_text, (self.rect.x + (Shop_Button.RECT_SIZE[0] - item_type_text.get_width()) // 2,
                                           self.rect.y + 60))

            price_text = Shop_Button.PRICE_FONT.render(str(self.price), True, color)
            total_width = price_text.get_width() + HUD.money_logo.get_width()

            e.screen.blit(HUD.money_logo, (self.rect.x + (106 - total_width) // 2, self.rect.y + 95 +
                                           (30 - HUD.money_logo.get_height()) // 2))
            e.screen.blit(price_text, (self.rect.x + (106 - price_text.get_width()) // 2 + 15, self.rect.y +
                                       95 + (30 - price_text.get_height()) // 2))

    def buy(self):
        p = Player.instance

        if p.inventory.money >= self.price:
            p.inventory.remove_money(self.price)
            self.function_execute()

    def is_on(self, mouse_coordinate: tuple) -> bool:
        if SHOP_RECT.colliderect(self.rect) and self.rect.collidepoint(mouse_coordinate):
            self.on = True
        else:
            self.on = False
        return self.on

    def display_triggered(self):
        pygame.draw.rect(Engine.instance.screen, Engine.GOLD, self.rect, 3)


MAIN_SHOP = [
    Shop_Button(Colt(), 50, lambda: Player.instance.inventory.set_item(Colt())),
    Shop_Button(Fl49(), 90, lambda: Player.instance.inventory.set_item(Fl49())),
    Shop_Button(AkimboM(), 200, lambda: Player.instance.inventory.set_item(AkimboM())),
    Shop_Button(AssaultRifle(), 350, lambda: Player.instance.inventory.set_item(AssaultRifle())),
    Shop_Button(Thompson(), 300, lambda: Player.instance.inventory.set_item(Thompson())),
    Shop_Button(ShotGun(), 300, lambda: Player.instance.inventory.set_item(ShotGun())),
    Shop_Button(Sniper(), 250, lambda: Player.instance.inventory.set_item(Sniper())),
    Shop_Button(PRL7(), 450, lambda: Player.instance.inventory.set_item(PRL7())),
    Shop_Button(Ammo_Box(), 80, lambda: Player.instance.inventory["weapon"].semi_refill_ammo() if Player.instance.
                inventory["weapon"] is not None else None)
]

DEVELOPER_SHOP = [
    Shop_Button(GMV200(), 0, lambda: Player.instance.inventory.set_item(GMV200())),
    Shop_Button(Cola(), 0, lambda: Player.instance.inventory.set_item(Cola())),
    Shop_Button(Candy(), 0, lambda: Player.instance.inventory.set_item(Candy())),
    Shop_Button(Burger(), 0, lambda: Player.instance.inventory.set_item(Burger())),
    Shop_Button(ChocolateBar(), 0, lambda: Player.instance.inventory.set_item(ChocolateBar())),
    Shop_Button(SpicyJuice(), 0, lambda: Player.instance.inventory.set_item(SpicyJuice())),
    Shop_Button(Transmute(), 0, lambda: Player.instance.inventory.set_item(Transmute())),
    Shop_Button(Necklace(), 0, lambda: Player.instance.inventory.set_item(Necklace())),
    Shop_Button(RailGun(), 0, lambda: Player.instance.inventory.set_item(RailGun())),
    Shop_Button(MachCrystal(), 0, lambda: Player.instance.inventory.set_item(MachCrystal())),

]

actual_stage = 0
max_stage_pixel = Shop_Button.BUTTON_AMOUNT // 3 * 154 if Shop_Button.BUTTON_AMOUNT >= 3 else 154

SHOP_RECT = pygame.rect.Rect((385, 167, 414, 464))


def create_random_utility_shop(item_amount: int) -> list:
    aui = copy.copy(all_utility_items)

    ITEM_PRICE_RANGE = [10, 30]
    final_shop = []

    for item in range(item_amount):
        item = aui.pop(random.randint(0, len(aui)-1))
        final_shop.append(Shop_Button(item, random.randint(ITEM_PRICE_RANGE[0], ITEM_PRICE_RANGE[1]),
                          lambda: Player.instance.inventory.set_item(item)))

    return final_shop


def shop(selected_shop=None):
    global actual_stage, max_stage_pixel

    if selected_shop is None:
        selected_shop = MAIN_SHOP

    Shop_Button.BUTTON_AMOUNT = 0
    for button in selected_shop:
        rect = (396 + (Shop_Button.BUTTON_AMOUNT % 3 * 136), 175 + (Shop_Button.BUTTON_AMOUNT // 3 * 154),
                Shop_Button.RECT_SIZE[0], Shop_Button.RECT_SIZE[1])
        button.rect = pygame.rect.Rect(rect)
        button.base_rect = pygame.rect.Rect(rect)
        Shop_Button.BUTTON_AMOUNT += 1

    actual_stage = 0
    max_stage_pixel = Shop_Button.BUTTON_AMOUNT // 3 * 154 if Shop_Button.BUTTON_AMOUNT >= 3 else 154

    e = Engine.instance
    p = Player.instance

    e.display(p, False, False)

    gameplay_image = pygame.display.get_surface().copy()
    black_screen_lo = pygame.image.load(os.path.join("assets", "HUD", "black_screen_low_opacity.png")).convert_alpha()
    shop_logo = pygame.image.load(os.path.join("assets", "HUD", "shop_logo.png")).convert_alpha()

    actual_stage = 0

    e.screen.blit(gameplay_image, (0, 0))
    e.screen.blit(black_screen_lo, (0, 0))
    e.screen.blit(shop_logo, (475, 64))

    screen_save = pygame.display.get_surface().copy()

    actual_button = None
    buy_button = None
    quit_button = Button((50, 50, 150, 30), None, "Quitter", Engine.LIGHT_BLUE, 24)
    triggered_mouse = False
    bar_move = False

    NAME_FONT = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 22)
    ITEM_TYPE_FONT = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 14)
    MONEY_FONT = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 14)
    TEXT_FONT = pygame.font.Font(os.path.join("assets", "font", "text.ttf"), 12)

    while True:
        mouse_coordinates = pygame.mouse.get_pos()

        e.screen.blit(gameplay_image, (0, 0))
        e.screen.blit(black_screen_lo, (0, 0))
        e.screen.blit(shop_logo, (475, 64))

        pygame.draw.rect(e.screen, Engine.DARK_GREY, (385, 167, 414, 464))

        for item_in_sell in selected_shop:
            item_in_sell.display()
            item_in_sell.is_on(mouse_coordinates)
            if item_in_sell.is_triggered(triggered_mouse):
                actual_button = item_in_sell
                buy_button = Button((840, 580, 330, 40), None, "Acheter cet objet", Engine.LIGHT_BLUE, 18)

        pygame.draw.rect(e.screen, Engine.LIGHT_BLUE, (385, 167, 414, 464), 2)

        pygame.draw.rect(e.screen, Engine.LIGHT_ALPHA, (810, 180, 5, 438))
        RECT_HEIGHT = 438 // (Shop_Button.BUTTON_AMOUNT // 3)
        pygame.draw.rect(e.screen, Engine.LIGHT_BLUE, (810, int(180 + (438 - RECT_HEIGHT) *
                                                                (actual_stage / max_stage_pixel)), 5, RECT_HEIGHT))

        if (triggered_mouse and pygame.rect.Rect(810, 180, 5, 438).collidepoint(mouse_coordinates)) or bar_move:
            actual_stage = (1 - (438 - (mouse_coordinates[1] - 180)) / 438) * max_stage_pixel
            if actual_stage < 0:
                actual_stage = 0
            elif actual_stage > max_stage_pixel:
                actual_stage = max_stage_pixel
            bar_move = True

        pygame.draw.rect(e.screen, Engine.DARK_GREY, (830, 167, 350, 464))
        pygame.draw.rect(e.screen, Engine.LIGHT_BLUE, (830, 167, 350, 464), 2)

        if actual_button:
            pygame.draw.rect(e.screen, Engine.LIGHT_BLUE, (890, 177, 230, 110), 5)
            e.screen.blit(actual_button.item.shop_image, (890 + (230 - actual_button.item.shop_image.get_width()) // 2,
                                                          177 + (110 - actual_button.item.shop_image.get_height())
                                                          // 2))

            item_name = NAME_FONT.render(actual_button.item.name, True, Engine.LIGHT_BLUE)
            e.screen.blit(item_name, (840, 307))

            if isinstance(actual_button.item, Weapon):
                item_type = actual_button.item.weapon_type
            else:
                item_type = "UTILITY"
            item_type_name = ITEM_TYPE_FONT.render(item_type, True,
                                                   Shop_Button.type_of_item_color[item_type])
            e.screen.blit(item_type_name, (1180 - item_type_name.get_width() - 10, 315))

            e.screen.blit(HUD.money_logo, (850, 340))
            color = Engine.LIGHT_BLUE
            if p.inventory.money < actual_button.price:
                color = Engine.LIGHT_RED
            price_text = Shop_Button.PRICE_FONT.render(str(actual_button.price), True, color)
            e.screen.blit(price_text, (875, 336))

            if isinstance(actual_button.item, Weapon):
                damage_text = TEXT_FONT.render("Dégâts", True, Engine.LIGHT_BLUE)
                e.screen.blit(damage_text, (850, 368))

                pygame.draw.rect(e.screen, Engine.DARK_GREY2, (850, 385, 310, 5))
                if isinstance(actual_button.item, (Close_Gun, DoubleW_Riffle)):
                    pygame.draw.rect(e.screen, Engine.ORANGE, (850, 385, 310 *
                                                                  (actual_button.item.damage *
                                                                   actual_button.item.bullet / 13), 5))

                pygame.draw.rect(e.screen, Engine.LIGHT_BLUE, (850, 385, 310 * (actual_button.item.damage / 13), 5))

                damage_text = TEXT_FONT.render("Cadence de tir", True, Engine.LIGHT_BLUE)
                e.screen.blit(damage_text, (850, 395))

                pygame.draw.rect(e.screen, Engine.DARK_GREY2, (850, 412, 310, 5))
                time_between_ball = actual_button.item.time_between_ball \
                    if not isinstance(actual_button.item, DoubleW_Riffle) else \
                    (actual_button.item.reload_time / actual_button.item.bullet)
                pygame.draw.rect(e.screen, Engine.LIGHT_BLUE,
                                 (850, 412, 310 * (0.1 / time_between_ball), 5))

                damage_text = TEXT_FONT.render("Munitions", True, Engine.LIGHT_BLUE)
                e.screen.blit(damage_text, (850, 422))

                pygame.draw.rect(e.screen, Engine.DARK_GREY2, (850, 437, 310, 5))
                pygame.draw.rect(e.screen, Engine.LIGHT_BLUE,
                                 (850, 437, 310 * (actual_button.item.start_ammo / 120), 5))

                speed_text = TEXT_FONT.render("Vitesse de projectile", True, Engine.LIGHT_BLUE)
                e.screen.blit(speed_text, (850, 449))

                pygame.draw.rect(e.screen, Engine.DARK_GREY2, (850, 464, 310, 5))
                pygame.draw.rect(e.screen, Engine.LIGHT_BLUE,
                                 (850, 464, 310 * (actual_button.item.ammo_speed / 2), 5))

                range_text = TEXT_FONT.render("Portée", True, Engine.LIGHT_BLUE)
                e.screen.blit(range_text, (850, 476))

                pygame.draw.rect(e.screen, Engine.DARK_GREY2, (850, 491, 310, 5))
                pygame.draw.rect(e.screen, Engine.LIGHT_BLUE,
                                 (850, 491, 310 * (actual_button.item.projectile_range / 40), 5))

            buy_button.display()
            buy_button.is_on(mouse_coordinates)
            if buy_button.is_triggered(triggered_mouse):
                actual_button.buy()
                triggered_mouse = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                if event.button == 4:
                    if actual_stage > 0:
                        actual_stage -= 5
                elif event.button == 5:
                    if actual_stage < max_stage_pixel:
                        actual_stage += 5

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    triggered_mouse = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    triggered_mouse = False
                    bar_move = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    return

        TOP = pygame.Surface((1280, 167))
        TOP.blit(screen_save, (0, 0))
        e.screen.blit(TOP, (0, 0))

        DOWN = pygame.Surface((1280, 88))
        DOWN.blit(screen_save, (0, -632))
        e.screen.blit(DOWN, (0, 632))

        quit_button.display()
        quit_button.is_on(mouse_coordinates)
        if quit_button.is_triggered(triggered_mouse):
            return

        money_point_text = MONEY_FONT.render(str(Player.instance.inventory.money), True,
                                                          Engine.WHITE)
        e.screen.blit(money_point_text, (1223, 11))
        e.screen.blit(HUD.money_logo, (1200, 10))

        e.screen.blit(HUD.cursor_image, (mouse_coordinates[0] - HUD.cursor_image.get_width() // 2,
                                         mouse_coordinates[1] - HUD.cursor_image.get_height() // 2))

        pygame.display.update()
