import pygame
import math

from engine.BasicFunction import *


pygame.init()


class Engine:

    # Instance of Engine to access anywhere in the program
    instance = None

    SCREEN_SIZE = (1280, 720)

    # COLORS
    BLACK = (0, 0, 0)
    DARK_GREY = (25, 25, 25)
    DARK_GREY2 = (56, 57, 61)
    WHITE = (255, 255, 255)
    RED = (255, 20, 20)
    LIGHT_RED = (190, 68, 65)
    LIGHT_RED2 = (255, 85, 85)
    LIGHT_BLUE = (1, 169, 217)
    LIGHT_GREEN = (111, 254, 124)
    DARK_BLUE = (18, 26, 41)
    DARK_BLUE2 = (0, 77, 255)
    GREEN = (75, 176, 75)
    PURPLE = (176, 0, 200)
    GOLD = (255, 186, 64)
    ORANGE = (244, 156, 0)
    LIGHT_ALPHA = (219, 230, 255)
    LIGHT_YELLOW = (253, 238, 206)

    ALL_COLORS = [DARK_GREY, BLACK, DARK_GREY2, WHITE, RED, LIGHT_RED2, LIGHT_BLUE, LIGHT_GREEN, DARK_BLUE, DARK_BLUE2,
                  GREEN, PURPLE, GOLD, ORANGE]

    # GAME
    GAME_NAME = "UTOPEX : Crystal Coverage"

    def __init__(self, plane, camera, world_map, HUD, core, a_star):

        # MAIN ENGINE VARIABLE
        self.plane = plane          # Plane object: Create an isometric conversion object
        self.camera = camera        # Camera Object: For relative display
        self.map = world_map        # Map of the game (Map Box data)
        self.offset = (0, 0)        # Screen save relative display coordinates
        self.HUD = HUD              # HUD Object: Display all game information
        self.a_star = a_star        # Path_finding object
        self.game_manager = None    # GameManager Object: Manage the player's game

        # SCREEN DATA
        self.screen = pygame.display.set_mode(Engine.SCREEN_SIZE)   # PYGAME SCREEN OBJECT
        pygame.display.set_caption(Engine.GAME_NAME)    # PYGAME SCREEN NAME
        game_icon = pygame.image.load("assets/GAME/game_icon_ingame.png")
        pygame.display.set_icon(game_icon)              # GAME ICON IMPORT

        # DATA
        self.screen_save = None     # SCREEN CAPTURE : for optimize FPS
        self.core = core            # Core Object: Main Objective of the
        self.main_objective = None  # Main Objective is the common thread of the game

        # Entities list
        self.entities = []
        self.entities_to_delete = []

        # Buildings list (Crystals, Distributor, etc...)
        self.builds = []
        self.builds_to_delete = []

        # Projectiles list
        self.projectiles = []
        self.projectiles_to_delete = []

        # Particles list
        self.particles = []
        self.particles_to_delete = []

        # Objectives list
        self.objectives = []
        self.objectives_to_delete = []

        self.background_color = Engine.DARK_GREY

        # INSTANCE
        Engine.instance = self

    def display(self, player, display_cursor=True, display_timer=True, display_HUD=True, display_entities=True,
                display_cell_border=False):
        # Display all element of the screen
        self.screen.fill(self.background_color)
        self.display_map(player, display_cell_border)
        if display_entities:
            self.display_entities()
        if display_HUD:

            if player.in_loot:
                self.display_loot_interface(player)

            self.HUD.display(display_cursor, display_timer)

    def actualise(self):
        # Actualise all element of the game
        for entity in self.entities:
            entity.actualise()
        for projectile in self.projectiles:
            projectile.actualise()
        for build in self.builds:
            build.actualise()
        for particle in self.particles:
            particle.actualise()
        self.main_objective.actualise()
        for objective in self.objectives:
            objective.actualise()

        self.entities[0].inventory.actualise()  # Actualise player inventory
        self.core.actualise()
        self.game_manager.update()

        self.delete_off_elements()

    def display_map(self, player, display_cell_border=False):
        # Display the map with a screen capture if the player didn't move during last frame
        if (self.screen_save and player.last_pos == player.pos) and not display_cell_border:
            self.screen.blit(self.screen_save, self.offset)
        else:
            POS = (int(player.pos[0]), int(player.pos[1]), 0)
            if self.map.background is not None:     # Display a map background if the map have it
                self.screen.blit(self.map.background, self.screen_coordinates((53.6, 32.5, 0)))
            for i in range(32):     # Display the case around the player (for optimize FPS)
                for j in range(32):
                    if POS[0] - i >= 0 and POS[1] - j >= 0:
                        if self.map[(POS[0] - i, POS[1] - j, 0)].color != self.background_color:
                            self.map[(POS[0] - i, POS[1] - j, 0)].display(display_cell_border)
                    if POS[0] + i < self.map.size[0] and POS[1] + j < self.map.size[1]:
                        if self.map[(POS[0] + i, POS[1] + j, 0)].color != self.background_color:
                            self.map[(POS[0] + i, POS[1] + j, 0)].display(display_cell_border)
                    if POS[0] + i < self.map.size[0] and POS[1] - j >= 0:
                        if self.map[(POS[0] + i, POS[1] - j, 0)].color != self.background_color:
                            self.map[(POS[0] + i, POS[1] - j, 0)].display(display_cell_border)
                    if POS[0] - i >= 0 and POS[1] + j < self.map.size[1]:
                        if self.map[(POS[0] - i, POS[1] + j, 0)].color != self.background_color:
                            self.map[(POS[0] - i, POS[1] + j, 0)].display(display_cell_border)

            if display_cell_border:
                pygame.draw.polygon(self.screen, Engine.WHITE,
                                    (self.screen_coordinates((0, 0, 0)),
                                     self.screen_coordinates((self.map.size[0], 0, 0)),
                                     self.screen_coordinates((self.map.size[0], self.map.size[1], 0)),
                                     self.screen_coordinates((0, self.map.size[1], 0))), 1)

            # Update screen capture
            self.screen_save = pygame.display.get_surface().copy()
            self.offset = (0, 0)

    def display_entities(self):
        # Displays all game elements (without map and HUD)
        # in terms of their position in the map (proximity to the camera)
        to_render = [self.core]
        for entity in self.entities:
            to_render.append(entity)
        for projectile in self.projectiles:
            to_render.append(projectile)
        for particle in self.particles:
            to_render.append(particle)
        for build in self.builds:
            to_render.append(build)

        to_render.sort(key=lambda e: e.pos[0] + e.pos[1], reverse=True)
        for r in to_render:
            r.display()

    def display_loot_interface(self, player):
        mouse_coordinates = pygame.mouse.get_pos()
        all_loots = player.loot_content

        main = pygame.image.load("assets/HUD/LootInterface.png").convert_alpha()
        cadre = pygame.image.load("assets/HUD/LootInterface_cadre.png").convert_alpha()
        cadre2 = pygame.image.load("assets/HUD/LootInterface_cadre2.png").convert_alpha()

        pos = player.loot_position

        self.screen.blit(main, pos)

        font1 = pygame.font.Font("assets/font/text.ttf", 14)
        font2 = pygame.font.Font("assets/font/text.ttf", 10)

        to_delete = []
        for amount, loot in enumerate(all_loots[0]):
            loot_instance = loot()
            self.screen.blit(cadre, (pos[0] + 8, pos[1] + 7 + amount*58))

            image = pygame.transform.scale(loot_instance.image, (49, 49))
            self.screen.blit(image, (pos[0] + 14, pos[1] + 11 + amount*58))

            text_item_name = font1.render(loot_instance.name, True, Engine.BLACK)
            self.screen.blit(text_item_name, (pos[0] + 78, pos[1] + 18 + amount*58))

            item_type = loot_instance.item_type
            if item_type == "weapon":
                color = Engine.GREEN
            elif item_type == "unique":
                color = Engine.ORANGE
            else:
                color = Engine.LIGHT_RED
            item_type = item_type[0].upper() + item_type[1:].lower()
            text_type_item = font2.render(item_type, True, color)
            self.screen.blit(text_type_item, (pos[0] + 88, pos[1] + 35 + amount*58))

            rect = pygame.rect.Rect(pos[0] + 8, pos[1] + 7 + amount*58, 212, 56)
            if rect.collidepoint(mouse_coordinates):
                pygame.draw.rect(self.screen, Engine.LIGHT_YELLOW, rect, 2)

                if input_info.get("LEFT_CLICK"):
                    if player[item_type.lower()] is not None:
                        player.loot_content[0].append(type(player[item_type.lower()]))
                    player[item_type.lower()] = loot_instance
                    to_delete.append(loot)
                    input_info["LEFT_CLICK"] = False

        for element in to_delete:
            player.loot_content[0].remove(element)

        for amount, loot in enumerate(all_loots[1]):

            if amount == 0:
                loot_img = pygame.image.load("assets/HUD/lumus_logo.png")
            elif amount == 1:
                loot_img = pygame.image.load("assets/HUD/crystal_logo.png")
            elif amount == 2:
                loot_img = pygame.image.load("assets/HUD/ammo_box_logo.png")

            self.screen.blit(cadre2, (pos[0] + 12 + 70*amount, pos[1] + 195))
            self.screen.blit(loot_img, (pos[0] + 22 + 70*amount, pos[1] + 199))

            text_loot_amount = font2.render(f"{loot}", True, Engine.BLACK)
            self.screen.blit(text_loot_amount, (pos[0] + 45 + 70 * amount, pos[1] + 203))

            rect = pygame.rect.Rect((pos[0] + 12 + 70*amount, pos[1] + 195, 65, 25))
            if rect.collidepoint(mouse_coordinates):
                pygame.draw.rect(self.screen, Engine.LIGHT_YELLOW, rect, 2)

                if input_info.get("LEFT_CLICK"):
                    if amount == 0:
                        to_remove = player.inventory.give_money(loot)
                    elif amount == 1:
                        to_remove = player.inventory.give_crystals(loot)
                    elif amount == 2:
                        for box in range(loot):
                            player["weapon"].semi_refill_ammo()
                        to_remove = loot
                    loot -= to_remove
                    player.loot_content[1][amount] = 0 if loot <= 0 else loot
                    input_info["LEFT_CLICK"] = False

        player.loot_offset += self.plane.distance(player.pos, player.last_pos)
        if player.loot_offset >= 3:
            player.in_loot = False

    def in_map(self, pos) -> bool:
        if 0 <= pos[0] < self.map.size[0] and 0 <= pos[1] < self.map.size[1] and 0 <= pos[2] < self.map.size[2]:
            return True
        return False

    def in_screen(self, pos):
        # Calculate if the pos is in the screen
        for x in range(2):
            for y in range(2):
                x1, x2 = self.screen_coordinates((pos[0] + x, pos[1] + y, pos[2]))
                if 0 <= x1 < self.SCREEN_SIZE[0] and 0 <= x2 < self.SCREEN_SIZE[1]:
                    return True
        return False

    def screen_coordinates(self, object_position: tuple) -> tuple:
        # Return a tuple of the object position on the screen
        pos = self.plane.convert(object_position)
        cam_pos = self.plane.convert(self.camera.pos)
        pos = (pos[0] - cam_pos[0] + Engine.SCREEN_SIZE[0] // 2, pos[1] - cam_pos[1] + Engine.SCREEN_SIZE[1] // 2)
        return pos

    def map_coordinates(self, object_position: tuple) -> tuple:
        # Return a tuple of the object position on the isometric map
        cam_pos = self.plane.convert(self.camera.pos)
        final_pos = [object_position[0] + cam_pos[0] - Engine.SCREEN_SIZE[0] // 2, object_position[1] + cam_pos[1] - Engine.SCREEN_SIZE[1] // 2]

        final_pos[0] /= Engine.instance.plane.size
        final_pos[1] /= Engine.instance.plane.size

        x = (1 / math.sqrt(2)) * ((-math.sqrt(6) * final_pos[1] * math.sqrt(2)) / 2 - final_pos[0])
        y = -x - (final_pos[1] * math.sqrt(6))
        z = 0

        return x, y, z

    def trigonometric_angle_of_cursor(self) -> float:
        # Return an angle in radian between the player and the cursor (for the projectiles)
        player_pos = self.entities[0].pos
        mouse_pos = Engine.instance.map_coordinates(pygame.mouse.get_pos())
        position = (mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1])
        return math.atan2(position[1], position[0])

    def add_offset(self, vector: tuple):
        # Change the offset of the screen capture to display
        self.offset = (self.offset[0] - vector[0], self.offset[1] - vector[1])

    @staticmethod
    def trigonometric_angle_of_two_element(a: tuple, b: tuple):
        # Return an angle in radian between two elements
        position = (b[0] - a[0], b[1] - a[1])
        return math.atan2(position[1], position[0])

    @staticmethod
    def radians_to_degrees(r):
        # Return an angle in radian between two elements
        return r * 180 / math.pi

    def delete_off_elements(self):
        # Deleted all old elements
        for entity in self.entities_to_delete:
            self.entities.remove(entity)
        for projectile in self.projectiles_to_delete:
            self.projectiles.remove(projectile)
        for particle in self.particles_to_delete:
            self.particles.remove(particle)
        for build in self.builds_to_delete:
            self.builds.remove(build)
        for objective in self.objectives_to_delete:
            self.objectives.remove(objective)

        self.entities_to_delete = list()
        self.projectiles_to_delete = list()
        self.builds_to_delete = list()
        self.objectives_to_delete = list()
        self.particles_to_delete = list()

    @staticmethod
    def open_interface(interface):
        interface()
        input_info.clear()
