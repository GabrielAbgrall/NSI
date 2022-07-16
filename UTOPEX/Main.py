import ast

import os
import os.path

from engine.Camera import Camera
from engine.Map import Map
from entity.player.TreeSK import *
from entity.player.Shop import *
from game.Objective import *
from game.GameManager import *
from game.Challenge import *
from game.Wave import *
from engine.Cell import *

"""Last version of pygame should be required to launch the game. (Because pygame.mixer's functions seem to have
 need the latest version)."""

"""Before Launch - GAME KEYS:
           - Player Moves : [Z:Up, Q:Left, S:Down, D:Right]
           - Player Attack : [LMB : Weapon Attack, RMB: Melee Attack]
           - Player Items : [é: Special Items, ": Consumable Items]
           - Player Talent tree : G
           - Player's spell : F
           - Interaction with Builds : E 
           """

E: Engine = None
P: Player = None
GM: GameManager = None

GAME_DATA = None
GAME_MISSION_NAME = None


# DEVELOPER PARAMETERS :
DEVELOPER_MODE = False
EDIT_MAP_MODE = False
WAVES_CREATOR_MODE = False
# ------------------------ #


def load_game(GAME_MAP: str):  # This function turn all parameters to 0
    global E, P, GM

    world_map = Map()
    world_map.load_save(GAME_MAP)  # We load a map_save
    if os.path.exists(f"{GAME_MAP}/background.png"):
        world_map.set_background(pygame.image.load(f"{GAME_MAP}/background.png").convert_alpha())

    pygame.mouse.set_visible(False)  # Disable the basic mouse cursor (to display a custom cursor)

    # We prepare the core according to the game mode
    game_mode = world_map.map_info.get("GAME_MODE") if world_map.map_info.get("GAME_MODE") is not None else "DC"

    core = None
    if game_mode == "DC":
        core = Core(world_map.map_info["CORE_POS"])
    elif game_mode == "SC":
        core = Payload(world_map.map_info["CORE_POS"])

    # We load the Engine
    E = Engine(Plane(30), Camera(), world_map, HUD(), core, AStar(world_map))

    # Player creation
    P = Player(world_map.map_info["WORLD_START"], E.camera, Inventory())
    reset_tree_talent()
    E.entities.append(P)

    # We define the type of the game (according to the game mode)
    if game_mode == "DC":
        E.main_objective = DefendCore()
    elif game_mode == "SC":
        E.main_objective = SaveCore()

    # Start equipment
    P["weapon"] = Colt()
    # --------------- #

    # Prepare the basics builds of the Map (A Distributor and few crystals to mine)
    world_map.spawn_all_builds(E)
    spawn_resources_build_spot(7)
    # ----------------------------------------- Wave Manager-------------------------------------------------------- #
    ALTERNATE_OBJECTIVES = [FastCrystal, SpiderInvasion, SavePnj, SavePnj]

    if game_mode == "DC":
        GM = GameManager(15, 40, ALTERNATE_OBJECTIVES)
    elif game_mode == "SC":
        GM = SaveCore_GM(15, 40, ALTERNATE_OBJECTIVES)

    E.map.insert_data(GM, ENEMY_CONVERSION)

    E.game_manager = GM  # Add the Game Manager to Engine


def main_menu():  # Main Menu is the first screen when the game is launch
    global GAME_DATA, GAME_MISSION_NAME

    buttons = [MissionSelection_Button((390, 300, 500, 50), None, "Lancer le jeu !", Engine.LIGHT_BLUE),
               InfiniteMode_Button((390, 380, 500, 50), None, "Mode infini ", Engine.GREEN),
               ChallengeSelection_Button((390, 460, 500, 50), None, "Défis", Engine.ORANGE),
               Quit_Button((390, 540, 500, 50), None, "Quitter", Engine.LIGHT_RED)]

    trigger_button = False

    GAME_LOGO = pygame.image.load("assets/GAME/game_logo.png").convert_alpha()

    with open("engine/data/game_state.txt", 'r') as f:
        GAME_DATA = ast.literal_eval(f.read())

    mission_select_interface = False
    mission_select_interface_buttons = [MissionButton((50, 300), "FACILE", "engine/saves/DefendCore_Map0", "M1", GAME_DATA["M1"], None,
                                                      "MISSION : Entraînement", Engine.LIGHT_YELLOW),
                                        MissionButton((465, 300), "NORMALE", "engine/saves/DefendCore_Map1",  "M2", GAME_DATA["M2"], None,
                                                      "MISSION : Attaque du coeur", Engine.LIGHT_YELLOW),
                                        MissionButton((880, 300), "DIFFICILE", "engine/saves/SaveCore_Map1", "M3", GAME_DATA["M3"], None,
                                                      "MISSION : Sauvetage d'urgence", Engine.LIGHT_YELLOW),
                                        MissionSelection_Button((390, 650, 500, 50), None, "Retour au menu", Engine.LIGHT_RED)]
    total_missions = 0
    mission_completed = 0
    for key, value in GAME_DATA.items():
        if key[0] == "M":
            total_missions += 1
            if value:
                mission_completed += 1

    text = f"{mission_completed} / {total_missions}   ({int((mission_completed / total_missions)*100)} %)"
    completion_text = pygame.font.Font("assets/font/text.ttf", 14).render(text, True, Engine.WHITE)

    challenge_select_interface = False
    challenge_select_interface_buttons = [ChallengeButton((50, 300), "AUCUN COFFRE", "engine/saves/DefendCore_Map1", "D1",
                                                        GAME_DATA["D1"], C_NoChest, None, "DÉFI : Récompenses limité",
                                                        Engine.LIGHT_YELLOW),
                                        ChallengeButton((465, 300), "VIE RÉDUITE", "engine/saves/DefendCore_Map1", "D2",
                                                        GAME_DATA["D2"], C_Weakness, None, "DÉFI : Faiblesse",
                                                        Engine.LIGHT_YELLOW),
                                        ChallengeButton((880, 300), "ADVERSAIRES PLUS FORTS",
                                                        "engine/saves/DefendCore_Map1", "D3",
                                                        GAME_DATA["D3"], C_DoublePower, None, "DÉFI : Double Force",
                                                        Engine.LIGHT_YELLOW),
                                        ChallengeButton((465, 430), "ADVERSAIRES PLUS NOMBREUX",
                                                          "engine/saves/DefendCore_Map1", "D4",
                                                          GAME_DATA["D4"], C_Melee, None, "DÉFI : Mélée générale",
                                                          Engine.LIGHT_YELLOW),
                                    ChallengeSelection_Button((390, 650, 500, 50), None, "Retour au menu", Engine.LIGHT_RED)]
    total_challenges = 0
    challenges_completed = 0
    for key, value in GAME_DATA.items():
        if key[0] == "D":
            total_challenges += 1
            if value:
                challenges_completed += 1

    text = f"{challenges_completed} / {total_challenges}   ({int((challenges_completed / total_challenges)*100)} %)"
    completion_text_d = pygame.font.Font("assets/font/text.ttf", 14).render(text, True, Engine.WHITE)

    while True:
        mouse_coordinate = pygame.mouse.get_pos()

        E.screen.fill(Engine.DARK_GREY)
        E.screen.blit(GAME_LOGO, (0, 0))

        if not mission_select_interface and not challenge_select_interface:
            trigger_button = False  # We verify if the button effect requires leaving the main menu
            for button in buttons:
                button.is_on(mouse_coordinate)
                button.display()
                if button.is_triggered(input_info.get("LEFT_CLICK")):  # If the mouse on the button, and the LMB is pressed
                    input_info["LEFT_CLICK"] = False
                    trigger_button = button.use()  # We launch the effect of the button
                    if isinstance(button, MissionSelection_Button):
                        mission_select_interface = True
                    elif isinstance(button, ChallengeSelection_Button):
                        challenge_select_interface = True
        elif mission_select_interface:
            for button in mission_select_interface_buttons:
                button.display()
                button.is_on(mouse_coordinate)
                if button.is_triggered(input_info.get("LEFT_CLICK")):
                    if isinstance(button, MissionButton):
                        GAME_MISSION_NAME = button.game_mission_code_name
                        load_game(button.GAME_MAP)
                        return
                    elif isinstance(button, MissionSelection_Button):
                        mission_select_interface = False

            pygame.draw.rect(E.screen, (200, 200, 200), ((E.screen.get_size()[0] - 700) // 2, 599, 702,
                                                         20), 3)
            pygame.draw.rect(E.screen, Engine.GREEN,
                             ((E.screen.get_size()[0] - 700) // 2 + 1, 600,
                              int(700 * (mission_completed / total_missions)), 18))
            E.screen.blit(completion_text,
                          ((E.screen.get_size()[0] - 700) // 2 + (700 - completion_text.get_width()) // 2, 602))
        elif challenge_select_interface:
            for button in challenge_select_interface_buttons:
                button.display()
                button.is_on(mouse_coordinate)
                if button.is_triggered(input_info.get("LEFT_CLICK")):
                    if isinstance(button, ChallengeButton):
                        GAME_MISSION_NAME = button.game_mission_code_name
                        load_game(button.GAME_MAP)
                        button.function()
                        return
                    elif isinstance(button, ChallengeSelection_Button):
                        challenge_select_interface = False

            pygame.draw.rect(E.screen, (200, 200, 200), ((E.screen.get_size()[0] - 700) // 2, 599, 702,
                                                                     20), 3)
            pygame.draw.rect(E.screen, Engine.GREEN,
                             ((E.screen.get_size()[0] - 700) // 2 + 1, 600,
                              int(700 * (challenges_completed / total_challenges)), 18))
            E.screen.blit(completion_text_d,
                          ((E.screen.get_size()[0] - 700) // 2 + (700 - completion_text_d.get_width()) // 2, 602))

        # We display the mouse cursor
        E.screen.blit(HUD.cursor_image, (mouse_coordinate[0] - HUD.cursor_image.get_width() // 2,
                                         mouse_coordinate[1] - HUD.cursor_image.get_height() // 2))
        pygame.display.flip()

        check_event()
        Clock.tick(TICK_SPEED)

        # If a button has been pressed, the game have to launch (because only 3 buttons: QUIT or LAUNCH or InfiniteMode)
        if trigger_button:
            load_game("engine/saves/DefendCore_Map1")
            E.game_manager.launch_infinite_mode()
            return


def end_game(reason: str, victory: bool):  # This function is called if we had a "Victory" or "Defeat" and this is an
    # end screen: "reason" is a string that explain the reason of loose or victory, victory is a boolean who indicate
    # if this is an victory or a defeat

    if victory:
        GAME_DATA[GAME_MISSION_NAME] = True
        with open("engine/data/game_state.txt", 'w') as f:
            f.writelines(str(GAME_DATA))

    E.display(P, False, False)

    game_image = pygame.display.get_surface().copy()
    black_screen_lo = pygame.image.load("assets/HUD/black_screen_low_opacity.png").convert_alpha()
    game_over_black = pygame.image.load("assets/HUD/game_over_black.png").convert_alpha()
    victory_logo = pygame.image.load("assets/HUD/victory_logo.png").convert_alpha()

    reason_of_loose_font = pygame.font.Font("assets/font/text.ttf", 25)

    actual_frame = 0    # Frame counter

    first_animation = 20   # Animation of the victory or loose logo

    second_animation = TICK_SPEED * 1  # Animation of death message or victory message
    # The text appear progressively, so we define the speed and the number of character per frame
    amount_of_character_per_frame = second_animation // len(reason)
    actual_text = str()
    full_text = copy.copy(reason)

    third_animation = TICK_SPEED // 2  # Animation of the menu button
    width_per_frame = 552 / third_animation
    actual_width = 0

    quit_button = None
    quit_button_state = False

    while True:

        mouse_coordinate = pygame.mouse.get_pos()

        E.screen.blit(game_image, (0, 0))
        E.screen.blit(black_screen_lo, (0, 0))

        # ----------- This manages all animation (if is victory of loose) ----------- #
        if actual_frame < first_animation:
            if not victory:
                E.screen.blit(game_over_black, (498 - actual_frame * 2, 64))
            else:
                E.screen.blit(victory_logo, (536 - actual_frame * 2, 63))
        else:
            if not victory:
                E.screen.blit(game_over_black, (458, 64))
            else:
                E.screen.blit(victory_logo, (496, 63))

        if actual_frame < second_animation:
            if actual_frame % amount_of_character_per_frame == 0 and full_text != "":
                actual_text += full_text[0]
                full_text = full_text[1:]
        text = reason_of_loose_font.render(actual_text, True, E.WHITE)
        E.screen.blit(text, ((E.SCREEN_SIZE[0] - text.get_width()) // 2, 150))

        pygame.draw.rect(E.screen, Engine.DARK_BLUE, ((E.SCREEN_SIZE[0] - actual_width) // 2, 503, actual_width, 101))

        if actual_frame < third_animation:
            actual_width += width_per_frame
        elif actual_frame == third_animation:
            quit_button = Button((386, 520, 509, 68), None, "Menu principal", Engine.LIGHT_BLUE)
        else:
            quit_button.is_on(mouse_coordinate)
            quit_button.display()
            quit_button_state = quit_button.is_triggered(input_info.get("LEFT_CLICK"))
            if input_info.get(pygame.K_SPACE):
                quit_button_state = True
            display_keyboard_info("Space", (409, 528))

        actual_frame += 1
        # ---------------------------------------------------------------------------------------------------------- #

        # Display mouse cursor
        E.screen.blit(HUD.cursor_image, (mouse_coordinate[0] - HUD.cursor_image.get_width() // 2,
                                         mouse_coordinate[1] - HUD.cursor_image.get_height() // 2))

        pygame.display.flip()

        check_event()
        Clock.tick(TICK_SPEED)

        if quit_button_state:
            time.sleep(0.25)
            return  # Quit the function to return at menu


def display_keyboard_info(key: str, pos):  # Cette fonction crée la représentation d'une touche de clavier ,
    # elle est appelée et afficher lors de l'animation de fin
    keyboard_key = pygame.image.load("assets/HUD/keyboard_key.png")

    big_key_font = pygame.font.Font("assets/font/text.ttf", 32)
    small_key_font = pygame.font.Font("assets/font/text.ttf", 12)

    E.screen.blit(keyboard_key, pos)

    if len(key) == 1:
        key_text = big_key_font.render(key, True, Engine.WHITE)
        E.screen.blit(key_text, (pos[0] + 16, pos[1] + 6))
    else:
        key_text = small_key_font.render(key, True, Engine.WHITE)
        E.screen.blit(key_text, (pos[0] + 6, pos[1] + 13))


def game():
    # This function launch the game ( Engine = E, Player = P in E.entities[0], Core in E.core, Map in E.map,
    # GameManager in E.GameManager, Camera in E.camera, HUD in E.HUD needed to launch)
    while True:
        E.display(P)
        pygame.display.update()

        # fps = Clock.get_fps()
        # print(f"FPS:{fps}")

        check_event()
        mouse_coordinate = pygame.mouse.get_pos()

        offset = [0, 0, 0]  # We check the keys relative to player movement
        if input_info.get(pygame.K_z):
            offset[1] += 1
        if input_info.get(pygame.K_s):
            offset[1] += -1
        if input_info.get(pygame.K_q):
            offset[0] += 1
        if input_info.get(pygame.K_d):
            offset[0] += -1

        P.move(tuple(offset))  # We move the player according to the pressed movement keys
        if P.pos != P.last_pos:
            vector = (P.pos[0] - P.last_pos[0], P.pos[1] - P.last_pos[1], 0)
            pos = (P.pos[0] - random.uniform(0, vector[0] * 5), P.pos[1] - random.uniform(0, vector[1] * 5), 0)
            Particle(pos, 6, Engine.WHITE)

        # We check the keys pressed and we launch functions assorted
        # if the item come to 0

        if input_info.get(pygame.K_2) and P.inventory.inventory["utility"] is not None:  # Use consumable item
            if not P.inventory.inventory["utility"].use():
                P.inventory.delete_item("utility")
        if input_info.get(pygame.K_3) and P.inventory.inventory["unique"] is not None:  # Use unique item
            P.inventory.inventory["unique"].use()
        if input_info.get(pygame.K_f) and P.inventory.inventory["spell"] is not None:  # Use the spell
            P.inventory.inventory["spell"].use()
            input_info[pygame.K_f] = False

        if input_info.get(pygame.K_g):  # Open the Talent tree
            E.open_interface(change_talent)

        # We do the attack management
        if not P.visor_mode:
            if input_info.get("LEFT_CLICK") and P.inventory.inventory["weapon"] is not None and not P.paralysis:
                P.inventory.inventory["weapon"].use()
                if isinstance(P.inventory.inventory["weapon"], Precision_Riffle):
                    input_info["LEFT_CLICK"] = False
            if input_info.get("RIGHT_CLICK") and P.melee_attack_start_time is None and not P.paralysis:
                P.melee_attack()
        else:
            if input_info.get("LEFT_CLICK") and not P.paralysis:
                P.visor_mode = False
                P.visor_projectile.active = True
                P.visor_projectile.pos = E.map_coordinates(mouse_coordinate)
                input_info["LEFT_CLICK"] = False
            elif input_info.get("RIGHT_CLICK"):
                P.visor_mode = False
                E.projectiles.remove(P.visor_projectile)
                input_info["RIGHT_CLICK"] = False

        # Interaction Build management
        for build in E.builds:
            if isinstance(build, Interaction_Build):
                if build.is_colliding(P.pos) and input_info.get(pygame.K_e):
                    build.interaction()
                    input_info.clear()
        if E.core.is_colliding(P.pos) and input_info.get(pygame.K_e):
            E.core.interaction()
            input_info[pygame.K_e] = False

        if DEVELOPER_MODE:
            if input_info.get(pygame.K_t):  # Open the shop
                shop()
                input_info[pygame.K_t] = False
            if input_info.get(pygame.K_F1):
                P.inventory.give_money(50)
            if input_info.get(pygame.K_F2):
                P.inventory.give_crystals(50)
            if input_info.get(pygame.K_F3):
                P.give_exp(100)
            if input_info.get(pygame.K_F4):
                P.add_health(3)
            if input_info.get(pygame.K_F5):
                E.core.add_health(3)
            if input_info.get(pygame.K_F6):
                effect = Give_Speed(10, 1)
                effect.launch(P)
                input_info[pygame.K_F6] = False
            if input_info.get(pygame.K_F7):
                effect = Damage_Boost(10, 2)
                effect.launch(P)
                input_info[pygame.K_F7] = False
            if input_info.get(pygame.K_F8):
                effect = Give_Attack_Speed(10, -2)
                effect.launch(P)
                input_info[pygame.K_F8] = False
            if input_info.get(pygame.K_F9):
                P["weapon"].refill_ammo()
            if input_info.get(pygame.K_F10):
                shop(DEVELOPER_SHOP)
                input_info[pygame.K_F10] = False
            if input_info.get(pygame.K_F11):
                input_info[pygame.K_F11] = False
                E.core.speed += 0.01
            if input_info.get(pygame.K_F12):
                input_info[pygame.K_F12] = False
                E.core.speed -= 0.01

        # Background offset update
        a = E.plane.convert(P.last_pos)
        b = E.plane.convert(P.pos)
        E.add_offset((b[0] - a[0], b[1] - a[1]))    # Update the position of the screen save (for optimise the FPS)

        E.actualise()  # We actualise all elements
        try_to_add_new_resource_build()

        if E.main_objective.finish:
            end_game(E.main_objective.finish_reason, E.main_objective.state)
            return

        Clock.tick(TICK_SPEED)


def edit_map_mode():
    global E, P

    M = Map()
    width = int(input("WIDTH of the MAP : "))
    height = int(input("HEIGHT of the MAP : "))
    M.create(width, height, 1, Cell())

    E = Engine(Plane(30), Camera(), M, None, None, None)
    P = Player((0, 0, 0), E.camera, None)
    Give_Speed(9999999999999999999999999999, 0.4).launch(P)

    p_img = pygame.transform.scale(P.image, (13, 45))
    c_img = pygame.transform.scale(Core((0, 0, 0)).textures[0], (20, 45))
    s_img = pygame.transform.scale(pygame.image.load("assets/BUILD/SHOP/2_4.png"), (45, 45))
    chest_img = pygame.transform.scale(pygame.image.load("assets/BUILD/Chest.png"), (45, 35))

    buttons = [OpenMapMenuButton((80, 480, 200, 50), None, "Open", Engine.LIGHT_BLUE, 24),
               SaveMapButton((80, 550, 200, 50), None, "Save", Engine.GREEN, 24),
               CellWalkableButton((80, 620, 220, 50), None, "Cell Walkable", Engine.LIGHT_YELLOW, 24),
               CellSpawnPointButton((320, 620, 220, 50), None, "Cell SpawnPoint", Engine.LIGHT_YELLOW, 24),
               ShowBuildButton((580, 620, 100, 50), None, "Build", Engine.LIGHT_YELLOW, 24),
               ExtraMapButton((720, 630, 30, 30)),
               WorldStartButton((760, 620, 60, 50), p_img, None, Engine.LIGHT_YELLOW, 24),
               CorePosButton((830, 620, 60, 50), c_img, None, Engine.LIGHT_YELLOW, 24),
               ShopPosButton((900, 620, 60, 50), s_img, None, Engine.LIGHT_YELLOW, 24),
               ChestPosButton((970, 620, 60, 50), chest_img, None, Engine.LIGHT_YELLOW, 24),
               ColorPaletteButton((1100, 600, 130, 25), Engine.RED, 0),
               ColorPaletteButton((1100, 625, 130, 25), Engine.GREEN, 1),
               ColorPaletteButton((1100, 650, 130, 25), Engine.DARK_BLUE, 2)]

    for num, color in enumerate(Engine.ALL_COLORS):
        line = num//2
        buttons.append(ColorButton((1100 + (num % 2 * 80), 30 + (line * 80), 50, 50), color))

    d_img = pygame.transform.scale(Distributor((-1, -1, 0)).texture, (31, 45))
    p_img = pygame.transform.scale(Pillar((-1, -1, 0)).texture, (15, 45))
    f_img = Flower_Build((-1, -1, 0)).texture
    build_buttons = [BuildPosButton((580, 560, 60, 50), Distributor, d_img, None, Engine.LIGHT_YELLOW),
                     BuildPosButton((650, 560, 60, 50), Pillar, p_img, None, Engine.LIGHT_YELLOW),
                     BuildPosButton((720, 560, 60, 50), Flower_Build, f_img, None, Engine.LIGHT_YELLOW),
                     BuildPosButton((790, 560, 60, 50), Broken_Core, c_img, None, Engine.LIGHT_YELLOW),]

    cell_to_drop = Cell()
    extra_item_to_drop = None
    can_edit_map = True
    show_extra_map = True
    show_build_buttons = False
    build_name = None
    localisation = None

    save_dir = "engine/saves/"
    all_maps_create = [m for m in os.listdir(save_dir)]
    maps_buttons = []
    for i, m in enumerate(all_maps_create):
        maps_buttons.append(Button((10, 100 + i*40, 250, 30), None, m, Engine.LIGHT_ALPHA, 20))
    open_map_menu = False

    while True:
        mouse_coordinates = pygame.mouse.get_pos()
        mouse_coordinates_in_map = E.map_coordinates(mouse_coordinates)
        mouse_coordinates_in_map = (int(mouse_coordinates_in_map[0]), int(mouse_coordinates_in_map[1]), 0)

        E.display(P, True, False, False, False, True)

        if show_extra_map:
            if E.map.map_info.get("WORLD_START"):
                Player(E.map.map_info["WORLD_START"], None, None).display()
            if E.map.map_info.get("CORE_POS"):
                Core(E.map.map_info["CORE_POS"]).display()
            if E.map.map_info.get("CHEST_SPAWN_POS"):
                for chest_pos in E.map.map_info["CHEST_SPAWN_POS"]:
                    Chest(chest_pos).display()
            if E.map.map_info.get("SHOP_SPAWN_POS"):
                for shop_pos in E.map.map_info["SHOP_SPAWN_POS"]:
                    Shop_Spot(shop_pos).display()
            if E.map.map_info.get("BUILDS"):
                for build in E.map.map_info["BUILDS"]:
                    BUILD_CONVERTER[build[0]](build[1]).display()

            if input_info.get("RIGHT_CLICK") and E.in_map(mouse_coordinates_in_map):
                if E.map.map_info.get("WORLD_START") and E.map.map_info["WORLD_START"] == mouse_coordinates_in_map:
                    E.map.map_info["WORLD_START"] = None
                if E.map.map_info.get("CORE_POS") and E.map.map_info["CORE_POS"] == mouse_coordinates_in_map:
                    E.map.map_info["CORE_POS"] = None
                if E.map.map_info.get("CHEST_SPAWN_POS"):
                    for chest_pos in E.map.map_info["CHEST_SPAWN_POS"]:
                        if chest_pos == mouse_coordinates_in_map:
                            E.map.map_info["CHEST_SPAWN_POS"].remove(chest_pos)
                if E.map.map_info.get("SHOP_SPAWN_POS"):
                    for shop_pos in E.map.map_info["SHOP_SPAWN_POS"]:
                        if shop_pos == mouse_coordinates_in_map:
                            E.map.map_info["SHOP_SPAWN_POS"].remove(shop_pos)
                if E.map.map_info.get("BUILDS"):
                    for build in E.map.map_info["BUILDS"]:
                        if build[1] == mouse_coordinates_in_map:
                            E.map.map_info["BUILDS"].remove(build)

        if extra_item_to_drop is not None:
            extra_item_to_drop.pos = mouse_coordinates_in_map
            extra_item_to_drop.display()
            if input_info["LEFT_CLICK"] and E.in_map(mouse_coordinates_in_map):
                if build_name is None:
                    if isinstance(extra_item_to_drop, Player):
                        E.map.map_info["WORLD_START"] = extra_item_to_drop.pos
                    elif isinstance(extra_item_to_drop, Core):
                        E.map.map_info["CORE_POS"] = extra_item_to_drop.pos
                    elif isinstance(extra_item_to_drop, Shop_Spot):
                        if E.map.map_info.get("SHOP_SPAWN_POS"):
                            E.map.map_info["SHOP_SPAWN_POS"].append(extra_item_to_drop.pos)
                        else:
                            E.map.map_info["SHOP_SPAWN_POS"] = [extra_item_to_drop.pos]
                    elif isinstance(extra_item_to_drop, Chest):
                        if E.map.map_info.get("CHEST_SPAWN_POS"):
                            E.map.map_info["CHEST_SPAWN_POS"].append(extra_item_to_drop.pos)
                        else:
                            E.map.map_info["CHEST_SPAWN_POS"] = [extra_item_to_drop.pos]
                else:
                    if E.map.map_info.get("BUILDS") is None:
                        E.map.map_info["BUILDS"] = list()
                    E.map.map_info["BUILDS"].append((build_name, extra_item_to_drop.pos))
                    build_name = None
                extra_item_to_drop = None

        text_render = pygame.font.Font(None, 20).render(f"MOUSE COORDINATES : {mouse_coordinates_in_map}", True,
                                                        Engine.LIGHT_YELLOW)
        E.screen.blit(text_render, (20, 20))

        cell_info = f"CELL PARAMETERS : "
        cell_parameters_text_render = pygame.font.Font(None, 20).render(cell_info, True, Engine.LIGHT_YELLOW)
        E.screen.blit(cell_parameters_text_render, (20, 45))

        text_render = pygame.font.Font(None, 20).render(f" - WALKABLE = {cell_to_drop.walkable}", True,
                                                        Engine.LIGHT_YELLOW)
        E.screen.blit(text_render, (20 + cell_parameters_text_render.get_width(), 45))
        text_render = pygame.font.Font(None, 20).render(f" - SPAWN POINT = {cell_to_drop.spawn_point}", True,
                                                        Engine.LIGHT_YELLOW)
        E.screen.blit(text_render, (20 + cell_parameters_text_render.get_width(), 65))
        text_render = pygame.font.Font(None, 20).render(f" - COLOR = {cell_to_drop.color}", True,
                                                        Engine.LIGHT_YELLOW)
        E.screen.blit(text_render, (20 + cell_parameters_text_render.get_width(), 85))
        pygame.draw.rect(E.screen, cell_to_drop.color,
                         (25 + cell_parameters_text_render.get_width() + text_render.get_width(), 82, 20, 20))
        pygame.draw.rect(E.screen, Engine.LIGHT_YELLOW,
                         (25 + cell_parameters_text_render.get_width() + text_render.get_width(), 82, 20, 20), 2)

        E.screen.blit(pygame.font.Font(None, 20).render("0", True,
                                                        Engine.LIGHT_YELLOW), (1090, 580))
        E.screen.blit(pygame.font.Font(None, 20).render("255", True,
                                                        Engine.LIGHT_YELLOW), (1235, 580))

        if input_info.get("LEFT_CLICK") and E.in_map(mouse_coordinates_in_map) and can_edit_map and \
                extra_item_to_drop is None:
            E.map[mouse_coordinates_in_map] = copy.deepcopy(cell_to_drop)
        if input_info.get("MWB") and E.in_map(mouse_coordinates_in_map):
            cell_to_drop.color = E.map[mouse_coordinates_in_map].color

        can_edit_map = True
        for button in buttons:
            button.display()
            is_on = button.is_on(mouse_coordinates)
            if is_on:
                can_edit_map = False
            if button.is_triggered(input_info.get("LEFT_CLICK")):
                if isinstance(button, ColorButton) and not isinstance(button, (ColorPaletteButton, RG_Button)):
                    cell_to_drop.color = button.color
                elif isinstance(button, ColorPaletteButton):
                    color = list(cell_to_drop.color)
                    color[button.color_rgb_pos] = button.get_color_percentage_of_click(mouse_coordinates)
                    cell_to_drop.color = tuple(color)
                    E.screen.blit(pygame.font.Font(None, 20).render(f"{color[button.color_rgb_pos]}", True,
                                                                    Engine.LIGHT_YELLOW), (1090 + 65, 580))
                elif isinstance(button, CellWalkableButton):
                    cell_to_drop.walkable = not cell_to_drop.walkable
                    input_info["LEFT_CLICK"] = False
                elif isinstance(button, CellSpawnPointButton):
                    cell_to_drop.spawn_point = not cell_to_drop.spawn_point
                    input_info["LEFT_CLICK"] = False
                elif isinstance(button, SaveMapButton):
                    if localisation is None:
                        date = time.strftime("%Y-%m-%d", time.gmtime())
                        localisation = f"{save_dir}map_{date}_1"
                        i = 1
                        while os.path.exists(localisation):
                            i += 1
                            localisation = localisation[:-1]
                            localisation += str(i)
                    E.map.save(localisation)
                    E.map.load_save(localisation)
                    input_info["LEFT_CLICK"] = False
                elif isinstance(button, OpenMapMenuButton):
                    open_map_menu = not open_map_menu
                    input_info["LEFT_CLICK"] = False
                elif isinstance(button, ExtraMapButton):
                    show_extra_map = not show_extra_map
                    input_info["LEFT_CLICK"] = False
                elif isinstance(button, ExtraItemButton):
                    if isinstance(button, WorldStartButton):
                        extra_item_to_drop = Player(mouse_coordinates_in_map, None, None)
                    elif isinstance(button, CorePosButton):
                        extra_item_to_drop = Core(mouse_coordinates_in_map)
                    elif isinstance(button, ShopPosButton):
                        extra_item_to_drop = Shop_Spot(mouse_coordinates_in_map)
                    elif isinstance(button, ChestPosButton):
                        extra_item_to_drop = Chest(mouse_coordinates_in_map, 0)
                elif isinstance(button, ShowBuildButton):
                    show_build_buttons = not show_build_buttons
                    input_info["LEFT_CLICK"] = False

        if show_build_buttons:
            for button in build_buttons:
                button.display()
                button.is_on(mouse_coordinates)
                if button.is_triggered(input_info.get("LEFT_CLICK")):
                    build_type = button.build_type
                    extra_item_to_drop = build_type((-1, -1, 0))
                    build_name = build_type.NAME

        if open_map_menu:
            for button in maps_buttons:
                button.display()
                button.is_on(mouse_coordinates)
                if button.is_triggered(input_info.get("LEFT_CLICK")):
                    localisation = f"{save_dir}{button.text}"
                    E.map.load_save(localisation)

        pygame.display.update()

        offset = [0, 0, 0]
        if input_info.get(pygame.K_z):
            offset[1] += 1
        if input_info.get(pygame.K_s):
            offset[1] += -1
        if input_info.get(pygame.K_q):
            offset[0] += 1
        if input_info.get(pygame.K_d):
            offset[0] += -1
        P.move(tuple(offset), True)

        check_event()


def wave_creator_mode():
    global E
    E = Engine(Plane(30), Camera(), None, None, None, None)
    E.entities.append(Player((1, 1, 0), None, None))
    M = Map()

    waves_amount = 1
    actual_wave = 1

    FINAL_WAVES = [[]]

    buttons = [AddWavesButton((80, 620, 220, 50), None, "Add Wave", Engine.LIGHT_YELLOW, 24),
               Button((320, 620, 220, 50), None, "Assign To Map", Engine.LIGHT_BLUE, 24)]

    waves_buttons = [WaveSelectionButton()]

    boss_img = pygame.transform.scale(UIF45().image, (50, 48))

    enemies_buttons = [EnemySelectionButton((800, 600, 70, 70), SpiderBot().image, SpiderBot),
                       EnemySelectionButton((880, 600, 70, 70), ScarletSpider().image, ScarletSpider),
                       EnemySelectionButton((960, 600, 70, 70), MainBot().image, MainBot),
                       EnemySelectionButton((1040, 600, 70, 70), GoldBot().image, GoldBot),
                       EnemySelectionButton((1120, 600, 70, 70), boss_img, UIF45),
                       ]

    actual_height = 0

    save_dir = "engine/saves/"
    all_maps_create = [m for m in os.listdir(save_dir)]
    maps_buttons = []
    for i, m in enumerate(all_maps_create):
        M = Map()
        M.load_save(f"{save_dir}{m}")
        color = Engine.LIGHT_RED if M.map_info.get("WAVES") is None else Engine.GREEN
        maps_buttons.append(Button((10, 100 + i*40, 250, 30), None, m, color, 20))
    open_map_menu = False

    while True:
        mouse_coordinates = pygame.mouse.get_pos()
        max_pixel_height = waves_amount * 90

        E.screen.fill(E.background_color)

        text_render = pygame.font.Font(None, 20).render(f"WAVES AMOUNT : {waves_amount}", True,
                                                        Engine.LIGHT_YELLOW)
        E.screen.blit(text_render, (10, 10))

        for button in buttons:
            button.display()
            button.is_on(mouse_coordinates)
            if button.is_triggered(input_info.get("LEFT_CLICK")):
                if isinstance(button, AddWavesButton):
                    waves_amount += 1
                    actual_wave = waves_amount
                    FINAL_WAVES.append(list())
                    waves_buttons.append(WaveSelectionButton())
                    input_info["LEFT_CLICK"] = False
                else:
                    open_map_menu = not open_map_menu
                    input_info["LEFT_CLICK"] = False

        if not open_map_menu:
            for button in enemies_buttons:
                button.display()
                button.is_on(mouse_coordinates)
                if button.is_triggered(input_info.get("LEFT_CLICK")) or \
                        button.is_triggered(input_info.get("RIGHT_CLICK")):
                    changer = 1 if input_info.get("LEFT_CLICK") else -1
                    enemy_already_in_wave = False
                    for enemy_tuple in FINAL_WAVES[actual_wave-1]:
                        if enemy_tuple[0] == button.enemy:
                            if enemy_tuple[1] + changer >= 0:
                                enemy_tuple[1] += changer
                            enemy_already_in_wave = True
                    if not enemy_already_in_wave:
                        FINAL_WAVES[actual_wave-1].append([button.enemy, 1])

                    input_info["LEFT_CLICK"] = False
                    input_info["RIGHT_CLICK"] = False
            screen_save = pygame.display.get_surface().copy()

            for amount, button in enumerate(waves_buttons):
                button.value = amount + 1
                button.active = actual_wave == button.value
                button.wave_content = FINAL_WAVES[amount]
                button.offset = actual_height
                button.display()
                button.is_on(mouse_coordinates)
                if button.is_triggered(input_info.get("LEFT_CLICK")):
                    actual_wave = button.value
                if button.is_triggered(input_info.get("RIGHT_CLICK")):
                    waves_buttons.remove(waves_buttons[button.value-1])
                    FINAL_WAVES.remove(FINAL_WAVES[button.value-1])
                    actual_wave = 1
                    waves_amount -= 1

            TOP = pygame.Surface((1280, 30))
            TOP.blit(screen_save, (0, 0))
            E.screen.blit(TOP, (0, 0))

            DOWN = pygame.Surface((1280, 140))
            DOWN.blit(screen_save, (0, -600))
            E.screen.blit(DOWN, (0, 600))
        else:
            for button in maps_buttons:
                button.display()
                button.is_on(mouse_coordinates)
                if button.is_triggered(input_info["LEFT_CLICK"]):
                    FINAL_WAVES_CONVERT = []
                    for wave in FINAL_WAVES:
                        FINAL_WAVES_CONVERT.append([])
                        for enemy_tuple in wave:
                            FINAL_WAVES_CONVERT[-1].append((enemy_tuple[0].NAME, enemy_tuple[1]))
                    M.load_save(f"{save_dir}{button.text}")
                    M.map_info["WAVES"] = FINAL_WAVES_CONVERT
                    M.save(f"{save_dir}{button.text}")
                    button.color = Engine.GREEN

        pygame.display.update()

        for event in pygame.event.get():  # We check the different events of the user
            check_input(event)
            if event.type == pygame.QUIT:
                exit_program()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                if event.button == 4:
                    if actual_height > 0:
                        actual_height -= 5
                elif event.button == 5:
                    if actual_height < max_pixel_height:
                        actual_height += 5


if EDIT_MAP_MODE:
    edit_map_mode()
if WAVES_CREATOR_MODE:
    wave_creator_mode()


load_game("engine/saves/DefendCore_Map0")

pygame.mixer.init()
pygame.mixer.music.load("assets/MUSIC/MainTheme.wav")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

while True:
    main_menu()
    game()
