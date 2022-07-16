import pygame
import random
import copy
import math
import time
from engine.Plane import Plane
from engine.Engine import Engine
from entity.Effect import *


class Build:  # Les builds sont tout ce qui apparait sur la map qui sont immobile et qui ne sont pas des cases

    def __init__(self, name, pos, collision_radius, life, texture):
        self.name = name

        #  Chaque build a sa position, sa hitbox, sa vie/ vie max et sa texture
        self.pos = pos
        self.collision_radius = collision_radius
        self.life = life
        self.max_life = life
        self.texture = texture

        self.explosion_damage = False  # Indique si le build à déjà pris récemment des dégâts par une grenade

    def actualise(self):
        pass  # pass car elle est overwrite plus bas

    def display(self):  # Cette fonction gère tout ce qui concerne l'affichage des builds sur la fenêtre
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)  # Convertion des coordonnées sur le plan du Build vers les coordonnées
        # de la fenêtre python
        texture = self.get_display_texture()
        e.screen.blit(texture, (pos[0] - texture.get_width() // 2, pos[1] - texture.get_height()))

    def damage(self, amount) -> bool:  # Cette fonction gère les dégâts que prend le build
        self.life -= amount
        if self.life <= 0:
            if not (not (self in Engine.instance.builds) or self in Engine.instance.builds_to_delete):
                # Si le Build n'a plus de vie il va dans la "corbeille" des builds
                Engine.instance.builds_to_delete.append(self)
            return True     # todo : optimise
        return False

    def is_colliding(self, pos):  # Permet de détecter les collisions avec des entitées
        return Plane.distance(self.pos, pos) <= self.collision_radius

    def get_display_texture(self):
        return self.texture

    def get_rect(self):  # Permet de détecter les collisions avec des projectiles
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        texture = self.get_display_texture()
        return pygame.rect.Rect(pos[0] - texture.get_width() // 2, pos[1] - texture.get_height(),
                                texture.get_width(), texture.get_height())


class Broken_Core(Build):
    NAME = "CŒUR DÉTRUIT"

    def __init__(self, pos):
        texture = pygame.image.load("assets/BUILD/Broken_Core.png").convert_alpha()
        super().__init__(Broken_Core.NAME, pos, 1, 0, texture)


class Destruction_Build(Build):  # Ce sont les Builds qui sont des ressources collectables
    def __init__(self, name, pos, collision_radius, life, texture):
        super().__init__(name, pos, collision_radius, life, texture)

        self.full_dead = False


class Crystal(Destruction_Build):  # Ce sont les cristaux qui sont des builds collectables

    NAME = "CRYSTAL"

    BASE_LIFE = 30
    CRYSTAL_DEATH_SOUND = pygame.mixer.Sound("assets/SOUND/Crystal.wav")
    CRYSTAL_DEATH_SOUND.set_volume(0.1)
    DROP_RANGE = [5, 10]  # Ce sont les fourchettes de drop de cristaux et d'expérience
    EXP_RANGE = [1, 5]

    def __init__(self, pos):
        texture = pygame.image.load("assets/BUILD/Cristal.png")
        super().__init__(Crystal.NAME, pos, 2, Crystal.BASE_LIFE, texture)

        self.drop = random.randint(Crystal.DROP_RANGE[0], Crystal.DROP_RANGE[1])
        self.exp = random.randint(Crystal.EXP_RANGE[0], Crystal.EXP_RANGE[1])

    def damage(self, amount):  # Cette fonction gère tout ce qui concerne les dégâts que prend le cristal et ce qu'il
        # donne à sa mort
        is__dead = super().damage(amount)

        if is__dead and not self.full_dead:
            self.full_dead = True
            Crystal.CRYSTAL_DEATH_SOUND.play()
            Engine.instance.entities[0].inventory.give_crystals(self.drop)  # entities[0] est le joueur
            Engine.instance.entities[0].give_exp(self.exp)

        return is__dead


class SpiderEgg(Destruction_Build):
    NAME = "NID D'ARAIGNEE"

    RANGE_OF_SPIDER_SPAWN = [3, 4]
    TIME_BEFORE_EXPLOSION = 20

    def __init__(self, pos):
        collision_radius = 2
        life = 40
        texture = pygame.image.load("assets/BUILD/SpiderSpawner.png")
        super().__init__(SpiderEgg.NAME, pos, collision_radius, life, texture)

        self.spider_spawn_amount = random.randint(SpiderEgg.RANGE_OF_SPIDER_SPAWN[0],
                                                  SpiderEgg.RANGE_OF_SPIDER_SPAWN[1])
        self.time_before_explosion = SpiderEgg.TIME_BEFORE_EXPLOSION
        self.start_time = time.perf_counter()

        self.already_count = False

    def actualise(self):
        _time = time.perf_counter()
        if _time >= self.start_time + self.time_before_explosion:
            E = Engine.instance
            E.builds_to_delete.append(self)

            from entity.enemy.Enemy import spawn_enemies
            spawn_enemies(int(3 * E.game_manager.difficulty * 2), self.pos, 3)

    def damage(self, amount):
        is__dead = super().damage(amount)

        if is__dead and not self.already_count:
            self.already_count = True
            for objective in Engine.instance.objectives:
                if objective.objective_type == "Spider_Invasion":
                    objective.actual_rate += 1


class Mini_Box(Destruction_Build):
    NAME = "BOX"

    MONEY_RANGE = [10, 15]
    CRYSTAL_RANGE = [3, 7]
    EXP_RANGE = [35, 55]
    AMMO_RANGE = [1, 1]

    def __init__(self, pos):
        collision_radius = 1
        texture = pygame.image.load("assets/BUILD/Box.png")
        life = 5
        super().__init__(Mini_Box.NAME, pos, collision_radius, life, texture)

        self.resources = [random.randint(Mini_Box.MONEY_RANGE[0], Mini_Box.MONEY_RANGE[1]),
                          random.randint(Mini_Box.CRYSTAL_RANGE[0], Mini_Box.CRYSTAL_RANGE[1]),
                          random.randint(Mini_Box.EXP_RANGE[0], Mini_Box.EXP_RANGE[1]),
                          random.randint(Mini_Box.AMMO_RANGE[0], Mini_Box.AMMO_RANGE[1])]

    def damage(self, amount) -> bool:
        is_dead = super().damage(amount)

        if is_dead:
            p = Engine.instance.entities[0]
            p.inventory.give_money(self.resources[0])
            p.inventory.give_crystals(self.resources[1])
            p.give_exp(self.resources[2])
            for i in range(self.resources[3]):
                p["weapon"].semi_refill_ammo()

        return is_dead


class Pillar(Destruction_Build):
    NAME = "PILLIER"

    def __init__(self, pos):
        collision_radius = 2
        life = 40
        texture = pygame.image.load("assets/BUILD/Pillar/0.png")
        super().__init__(Pillar.NAME, pos, collision_radius, life, texture)

        self.texture2 = pygame.image.load("assets/BUILD/Pillar/1.png")

    def get_display_texture(self):
        if self.life >= self.max_life // 2:
            return self.texture
        return self.texture2

    def display(self):
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        texture = self.get_display_texture()
        e.screen.blit(texture, (pos[0] - texture.get_width() // 2 + 2, pos[1] - texture.get_height() + 2))

    def damage(self, amount) -> bool:
        is_dead = super().damage(amount)

        if is_dead:
            Engine.instance.builds.append(Mini_Box(self.pos))

        return is_dead


class Green_Crystal(Crystal):
    def __init__(self, pos):
        super().__init__(pos)
        self.texture = pygame.image.load("assets/BUILD/Green_Cristal.png")

        self.already_count = False

    def damage(self, amount):
        is__dead = super().damage(amount)

        if is__dead and not self.already_count:
            self.already_count = True
            for objective in Engine.instance.objectives:
                if objective.objective_type == "Crystal_collect":
                    objective.actual_rate += 1

        return is__dead


class Blue_Crystal(Crystal):
    BASE_LIFE = 12
    EXP_RANGE = [20, 40]

    def __init__(self, pos):
        super().__init__(pos)
        self.texture = pygame.image.load("assets/BUILD/Blue_Cristal.png")

        self.exp = random.randint(Blue_Crystal.EXP_RANGE[0], Blue_Crystal.EXP_RANGE[1])

        self.life = Blue_Crystal.BASE_LIFE
        self.max_life = Blue_Crystal.BASE_LIFE


class Red_Crystal(Crystal):
    BASE_LIFE = 6
    DROP_RANGE = [10, 18]

    def __init__(self, pos):
        super().__init__(pos)
        self.texture = pygame.image.load("assets/BUILD/Red_Cristal.png")

        self.life = Red_Crystal.BASE_LIFE
        self.max_life = Red_Crystal.BASE_LIFE

        self.drop = random.randint(Red_Crystal.DROP_RANGE[0], Red_Crystal.DROP_RANGE[1])


class Interaction_Build(Build):  # Ce sont les builds avec lesquels on peut interragir en appuyant sur E
    def __init__(self, name, pos, collision_radius, life, texture, on_content):
        super().__init__(name, pos, collision_radius, life, texture)

        self.on_content = on_content

    def interaction(self):
        pass  # pass car interaction est overwrite en fonction des objets en eux-mêmes


class Movable_Build(Interaction_Build):

    def __init__(self, name, pos, speed, collision_radius, life, texture, on_content):
        super().__init__(name, pos, collision_radius, life, texture, on_content)

        self.last_pos = self.pos
        self.speed = speed

    def move(self, pos):  # The function take a vector and apply few transformations to move the entity
        norm = Plane.distance((0, 0, 0), pos)
        self.last_pos = tuple(self.pos)
        if norm == 0:
            return
        vector = (pos[0] / norm, pos[1] / norm, pos[2] / norm)
        self.pos = (self.pos[0] + vector[0] * self.speed, self.pos[1] + vector[1] * self.speed, self.pos[2] + vector[2]
                    * self.speed)

    def move_to(self, pos: tuple) -> None:
        self.pos = pos


class Distributor(Interaction_Build):  # Le Distributeur est un build permettant d'acheter des items moneyant finance
    NAME = "DISTRIBUTEUR"

    DISTRIBUTION_PRICE = 75  # Le prix d'achat dans le distributeur

    ON_CONTENT = ["APPUYEZ /i", f"{DISTRIBUTION_PRICE} /m", "CONSOMMABLE ALÉATOIRE"]

    def __init__(self, pos):
        collision_radius = 2  # Distance à laquelle on peut interragir avec ce distributeur
        life = 0  # Le distributeur est incassable
        texture = pygame.image.load("assets/BUILD/Distributor.png")
        super().__init__(Distributor.NAME, pos, collision_radius, life, texture, Distributor.ON_CONTENT)

        from entity.player.Item import all_utility_items
        self.items = all_utility_items  # C'est une lsite comprenant tout les items utilitaires

    def interaction(self):  # Lorsque l'on appuie sur E  et que l'on a portée cette fonction est appelé et elle gère
        # le retrait de l'argent du joueur et le don de l'item acheté
        if Engine.instance.entities[0].inventory.try_to_remove_money(Distributor.DISTRIBUTION_PRICE):
            Engine.instance.entities[0].inventory.remove_money(Distributor.DISTRIBUTION_PRICE)
            Engine.instance.entities[0].inventory.set_item(copy.copy(random.choice(self.items)))


class LootBox(Interaction_Build):
    NAME = "CAISSE"
    ON_CONTENT = ["APPUYEZ /i"]

    TIME_ON_MAP_AFTER_OPENING = 10

    def __init__(self, pos, loot_table: list, resources_loot: list):
        collision_radius = 3
        texture = pygame.image.load("assets/BUILD/Loot_Box.png")
        super().__init__(LootBox.NAME, pos, collision_radius, 0, texture, LootBox.ON_CONTENT)

        self.loot = []
        for loot in loot_table:
            if random.randint(1, 100) <= loot[1]:
                self.loot.append(loot[0])
        self.resources_loot = resources_loot

        self.open_time = 0

    def interaction(self):
        p = Engine.instance.entities[0]

        p.in_loot = not p.in_loot
        if p.in_loot:
            p.loot_content = [self.loot, self.resources_loot]
            p.loot_position = Engine.instance.screen_coordinates(self.pos)
            p.loot_offset = 0

    def actualise(self):
        p = Engine.instance.entities[0]
        if p.in_loot:
            self.open_time = time.perf_counter()
        else:
            if self.open_time != 0:
                if time.perf_counter() - self.open_time >= LootBox.TIME_ON_MAP_AFTER_OPENING:
                    Engine.instance.builds_to_delete.append(self)


class Chest(Interaction_Build):
    NAME = "COFFRE"
    ON_CONTENT = ["APPUYEZ /i"]

    # Probabilities to drop in the chest
    WEAPON_DROP_RATE = 20  # weapons
    UNIQUE_ITEM_DROP_RATE = 10  # unique items

    MONEY_DROP_RANGE = [40, 75]  # Money, crystals, EXP
    CRYSTAL_DROP_RANGE = [65, 100]
    EXP_DROP_RANGE = [75, 125]

    def __init__(self, pos, drop_coefficient=0):
        collision_radius = 3  # Distance we can interact with
        life = 0  # Chest is unbreakable

        texture = pygame.image.load("assets/BUILD/Chest.png")
        self.time_open = 0  # Time when the chest is open
        super().__init__(Chest.NAME, pos, collision_radius, life, texture, Chest.ON_CONTENT)

        from entity.player.Item import all_utility_items, all_weapon_items_drop, all_unique_items, Colt
        # This is the amount of money, crystals and exp content inside the chest
        self.resources = [int(random.randint(Chest.MONEY_DROP_RANGE[0], Chest.MONEY_DROP_RANGE[1]) * drop_coefficient),
                          int(random.randint(Chest.CRYSTAL_DROP_RANGE[0], Chest.CRYSTAL_DROP_RANGE[1]) *
                              drop_coefficient),
                          int(random.randint(Chest.EXP_DROP_RANGE[0], Chest.EXP_DROP_RANGE[1]) * drop_coefficient)]
        # 0 : Money; 1 : Crystal; 2 : EXP

        if drop_coefficient > 0:
            self.items = []  # Ce sont les items et eventuellement l'armes et l'item unique dans le coffre
            if Engine.instance.entities[0]["utility"] is None:
                self.items.append(copy.copy(random.choice(all_utility_items)))

            if random.randint(1, 100) >= 100 - Chest.WEAPON_DROP_RATE and \
                    isinstance(Engine.instance.entities[0]["weapon"], Colt):
                self.items.append(copy.copy(random.choice(all_weapon_items_drop)))

            if random.randint(1, 100) >= 100 - Chest.UNIQUE_ITEM_DROP_RATE and Engine.instance.entities[0]["unique"] \
                    is None:
                self.items.append(copy.copy(random.choice(all_unique_items)))

            self.ammo_loader = random.randint(1, 1)

            self.open = False

    def interaction(self):  # Cette fonction s'occupe de distribuer au joueur ce qu'il a gagner
        if not self.open:
            p = Engine.instance.entities[0]
            self.open = True
            self.time_open = time.perf_counter()
            self.texture = pygame.image.load("assets/BUILD/Open_Chest.png")
            p.inventory.give_money(self.resources[0])
            p.inventory.give_crystals(self.resources[1])
            p.give_exp(self.resources[2])

            for item in self.items:
                p.inventory.set_item(item)

            for ammo_loader in range(self.ammo_loader):
                p.inventory["weapon"].semi_refill_ammo()

    def actualise(self):  # Actualise : DeSpawn the chest after 10 second of opening
        _time = time.perf_counter()
        if self.time_open > 0 and _time - self.time_open > 10:
            e = Engine.instance
            e.builds_to_delete.append(self)


class Shop_Spot(Interaction_Build):
    NAME = "BOUTIQUE"
    ON_CONTENT = ["APPUYEZ /i", "ÉCHANGER VOTRE MONNAIE"]

    def __init__(self, pos):
        collision_radius = 2
        texture = pygame.image.load("assets/BUILD/SHOP/0.png")
        super().__init__(Shop_Spot.NAME, pos, collision_radius, 0, texture, Shop_Spot.ON_CONTENT)

        self.time_in_map = 40
        self.start_time = time.perf_counter()

        self.main_textures = [pygame.image.load("assets/BUILD/SHOP/0.png").convert_alpha(),
                              pygame.image.load("assets/BUILD/SHOP/1.png").convert_alpha()]
        self.alternate_textures = [
            pygame.image.load("assets/BUILD/SHOP/2_0.png").convert_alpha(),
            pygame.image.load("assets/BUILD/SHOP/2_1.png").convert_alpha(),
            pygame.image.load("assets/BUILD/SHOP/2_2.png").convert_alpha(),
            pygame.image.load("assets/BUILD/SHOP/2_3.png").convert_alpha(),
            pygame.image.load("assets/BUILD/SHOP/2_4.png").convert_alpha(),
            pygame.image.load("assets/BUILD/SHOP/2_5.png").convert_alpha(),
        ]

        self.transition_time = 0.25
        self.time_between_transition = 1
        self.in_transition = True
        self.actual_state_time = time.perf_counter()
        self.actual_texture = None

    def display(self):
        texture = None

        if not self.in_transition:
            _time = time.perf_counter()
            if time.perf_counter() >= self.actual_state_time + self.time_between_transition:
                self.in_transition = True
                self.actual_state_time = _time
            else:
                texture = self.actual_texture

        if self.in_transition:
            _time = time.perf_counter()
            if time.perf_counter() >= self.actual_state_time + self.transition_time:
                self.in_transition = False
                self.actual_state_time = _time
                self.actual_texture = self.alternate_textures[random.randint(0, len(self.alternate_textures) - 1)]
                texture = self.actual_texture
            else:
                time_between_img = self.transition_time / len(self.main_textures)
                index = (_time - self.actual_state_time) // time_between_img
                texture = self.main_textures[int(index)]

        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        e.screen.blit(texture, (pos[0] - texture.get_width() // 2, pos[1] - texture.get_height()))

    def interaction(self):
        from entity.player.Shop import shop
        shop()

    def actualise(self):
        _time = time.perf_counter()
        if _time >= self.start_time + self.time_in_map:
            Engine.instance.builds_to_delete.append(self)


class Flower_Build(Interaction_Build):
    NAME = "FLEUR"
    ON_CONTENT = ["CONSOMMER /i", "POSSÈDE DES EFFETS ÉTRANGES"]

    EFFECTS = [Give_Speed(10, 0.125), Give_Speed(10, -0.05), Regeneration(10, 1, 0.5)]

    def __init__(self, pos):
        collision_radius = 1
        texture = pygame.image.load("assets/BUILD/Flower.png")
        super().__init__(Flower_Build.NAME, pos, collision_radius, 0, texture, Flower_Build.ON_CONTENT)

        self.pos = (self.pos[0] + random.uniform(0, 0.8), self.pos[1] + random.uniform(0, 0.8), 0)

    def interaction(self):
        p = Engine.instance.entities[0]
        if not p.flower_effect:
            random.choice(Flower_Build.EFFECTS).launch(p)
            FlowerImpact().launch(p)


class PNJ(Movable_Build):
    PNJ_NAME_LIST = ["Dog'z", "Kipioux", "Altéa", "Nessia", "Korbhen"]

    TEXTURES = [[pygame.image.load("assets/BUILD/PNJ/0/LEFT.png"),
                 pygame.image.load("assets/BUILD/PNJ/0/RIGHT.png"),
                 pygame.image.load("assets/BUILD/PNJ/0/UP.png"),
                 pygame.image.load("assets/BUILD/PNJ/0/DOWN.png")],

                [pygame.image.load("assets/BUILD/PNJ/1/LEFT.png"),
                 pygame.image.load("assets/BUILD/PNJ/1/RIGHT.png"),
                 pygame.image.load("assets/BUILD/PNJ/1/UP.png"),
                 pygame.image.load("assets/BUILD/PNJ/1/DOWN.png")],

                [pygame.image.load("assets/BUILD/PNJ/2/LEFT.png"),
                 pygame.image.load("assets/BUILD/PNJ/2/RIGHT.png"),
                 pygame.image.load("assets/BUILD/PNJ/2/UP.png"),
                 pygame.image.load("assets/BUILD/PNJ/2/DOWN.png")]
                ]
    ON_CONTENT = []

    START_HP = 70

    def __init__(self, pos, difficulty_coefficient=1, pnj_type="Base"):
        name = random.choice(PNJ.PNJ_NAME_LIST)
        collision_radius = 3

        life = PNJ.START_HP * difficulty_coefficient

        if pnj_type == "Mercenary":
            self.textures = PNJ.TEXTURES[2]
        elif pnj_type == "Technician":
            self.textures = PNJ.TEXTURES[1]
        else:
            self.textures = PNJ.TEXTURES[0]
        texture = self.textures[1]

        speed = 0.0125
        super().__init__(name, pos, speed, collision_radius, life, texture, PNJ.ON_CONTENT)

        self.pnj_type = pnj_type

        self.in_danger = False

        self.target = None
        self.way = None
        self.PF_CD = 5
        self.PF_start = 0

        self.active_start_time = time.perf_counter()

    def display(self):
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        texture = self.get_display_texture()
        e.screen.blit(texture, (pos[0] - texture.get_width() // 2, pos[1] - texture.get_height()))

    def get_display_texture(self):
        if self.way:
            vector = (self.way[0][0] - self.pos[0], self.way[0][1] - self.pos[1], self.way[0][2] - self.pos[2])
            if abs(vector[0]) >= abs(vector[1]):
                if vector[0] > 0:
                    return self.textures[0]
                return self.textures[1]
            else:
                if vector[1] > 0:
                    return self.textures[2]
                return self.textures[3]
        return self.texture

    def find_way(self, target):
        self.way = Engine.instance.a_star.path(self.pos, target.pos)[1:]
        self.PF_start = time.perf_counter()

    def remove_health(self, amount: int):
        super().damage(amount)

    def interaction(self):
        pass

    def remove_the_danger(self):
        self.in_danger = False
        self.life = self.max_life
        self.active_start_time = time.perf_counter()


class ShopKeeper(PNJ):
    def __init__(self, pos, difficulty_coefficient=1):
        super().__init__(pos, difficulty_coefficient, "Shopkeeper")

        from entity.player.Shop import create_random_utility_shop
        self.shop = create_random_utility_shop(3)  # todo : Add new shop type

        self.time_in_map = 15

    def interaction(self):
        if not self.in_danger:
            from entity.player.Shop import shop
            shop(self.shop)

    def actualise(self):
        if time.perf_counter() - self.active_start_time >= self.time_in_map and not self.in_danger:
            Engine.instance.builds_to_delete.append(self)

    def remove_the_danger(self):
        super().remove_the_danger()
        self.on_content = ["APPUYEZ /i", "MARCHAND AMBULANT"]


class RecruitPnj(PNJ):
    def __init__(self, pos, difficulty_coefficient=1, pnj_type="RecruitPnj"):
        super().__init__(pos, difficulty_coefficient, pnj_type)

        self.is_recruit = False
        self.recruit_price = 150
        self.recruit_bonus_price = 50

        self.time_in_map = 20

    def interaction(self):
        if not self.in_danger:
            if not self.is_recruit:
                self.recruit()
            else:
                self.recruit_bonus()

    def recruit(self):
        if Engine.instance.entities[0].inventory.try_to_remove_money(self.recruit_price):
            self.is_recruit = True
            Engine.instance.entities[0].inventory.remove_money(self.recruit_price)
            return True
        return False

    def recruit_bonus(self):
        if Engine.instance.entities[0].inventory.try_to_remove_money(self.recruit_bonus_price):
            Engine.instance.entities[0].inventory.remove_money(self.recruit_bonus_price)
            return True
        return False

    def actualise(self):
        if time.perf_counter() - self.active_start_time >= self.time_in_map and not self.in_danger and not \
                self.is_recruit:
            Engine.instance.builds_to_delete.append(self)


class Technician(RecruitPnj):
    def __init__(self, pos, difficulty_coefficient=1):
        super().__init__(pos, difficulty_coefficient, "Technician")
        self.attack_cd = 0.3
        self.attack = 1
        self.attack_time = 0

    def recruit(self):
        is_r = super().recruit()
        if is_r:
            self.on_content = ["APPUYEZ /i", "50 /m", "AUGMENTE LA QUANTITÉ DE RESSOURCES REÇU"]
        return is_r

    def recruit_bonus(self):
        bonus = super().recruit_bonus()
        if bonus:
            ResourcesDropRatioBoost(20, 1).launch(Engine.instance.entities[0])

    def actualise(self):
        super().actualise()
        if self.is_recruit:
            if self.target is None:
                for build in Engine.instance.builds:
                    if isinstance(build, Crystal) and (self.target is None or
                                                       Engine.instance.plane.distance(self.pos, build.pos) <
                                                       Engine.instance.plane.distance(self.pos, self.target.pos)):
                        self.target = build
                if self.target is not None:
                    self.find_way(self.target)
            else:
                if Engine.instance.plane.distance(self.pos, self.target.pos) >= 0.2:
                    vector = (self.way[0][0] - self.pos[0], self.way[0][1] - self.pos[1], self.way[0][2] - self.pos[2])
                    self.move(vector)
                    if Engine.instance.plane.distance(self.pos, self.way[0]) <= 0.2:
                        self.way.remove(self.way[0])
                else:
                    _time = time.perf_counter()
                    if _time - self.attack_time >= self.attack_cd:
                        self.attack_time = _time
                        if self.target.damage(self.attack):
                            self.target = None

    def remove_the_danger(self):
        super().remove_the_danger()
        self.on_content = ["APPUYEZ /i", "150 /m", "RECRUTEZ UN MINEUR"]


class Mercenary(RecruitPnj):
    def __init__(self, pos, difficulty_coefficient=1):
        super().__init__(pos, difficulty_coefficient, "Mercenary")
        self.attack_cd = 2
        self.attack = 1
        self.attack_time = 0

    def recruit(self):
        is_r = super().recruit()
        if is_r:
            self.on_content = ["APPUYEZ /i", "50 /m", "RECEVEZ DES MUNITIONS"]

    def recruit_bonus(self):
        bonus = super().recruit_bonus()
        if bonus:
            Engine.instance.entities[0]["weapon"].semi_refill_ammo()

    def actualise(self):
        super().actualise()
        if self.is_recruit:
            if self.target is None:
                from entity.enemy.Enemy import Enemy
                for k in range(5):
                    enemy = random.choice(Engine.instance.entities)
                    if isinstance(enemy, Enemy):
                        self.target = enemy
                        break
                if self.target is not None:
                    self.find_way(self.target)
            else:
                if time.perf_counter() - self.PF_start >= self.PF_CD:
                    self.find_way(self.target)
                if Engine.instance.plane.distance(self.pos, self.target.pos) >= 5:
                    if len(self.way) > 0:
                        vector = (self.way[0][0] - self.pos[0], self.way[0][1] - self.pos[1],
                                  self.way[0][2] - self.pos[2])
                        self.move(vector)
                        if Engine.instance.plane.distance(self.pos, self.way[0]) <= 0.2:
                            self.way.remove(self.way[0])
                else:
                    if self.target.health < 1:
                        self.target = None

                    _time = time.perf_counter()
                    if _time - self.attack_time >= self.attack_cd and self.target is not None:
                        self.attack_time = _time
                        theta = Engine.instance.trigonometric_angle_of_two_element(self.pos, self.target.pos)
                        from entity.Projectile import Projectile
                        Projectile(self.pos, 0.05, (math.cos(theta), math.sin(theta), 0), self.attack)

    def remove_the_danger(self):
        super().remove_the_danger()
        self.on_content = ["APPUYEZ /i", "150 /m", "RECRUTEZ UN MERCENAIRE"]


def spawn_resources_build_spot(amount, build_type=Crystal):
    # Cette fonction  s'occupe de faire apparaitre les ressources que sont les
    # cristaux sur les sur lesquels le joueur peut marcher ( Elle sont grises ). Cette fonction va placer "amount"
    # cristaux
    E = Engine.instance
    while amount > 0:
        pos = (random.randint(0, E.map.size[0] - 1), random.randint(0, E.map.size[1] - 1), 0)
        if E.map.content[pos].walkable:  # Si la case est "marchable"
            pos_already_take = False  # On vérifie que d'autre build ne sont pas déjà sur la case,
            if E.core.pos == pos:
                pos_already_take = True
            if not pos_already_take:
                for build in E.builds:
                    if build.pos == pos:
                        pos_already_take = True
                if not pos_already_take:  # Si c'est le cas on fait apparaîte le cristal à cette position
                    E.builds.append(build_type(pos))
                    amount -= 1


def spawn_build_around_spawn_point(amount: int, spawn_point: tuple, spawn_radius: int, build_type=Crystal):
    E = Engine.instance
    while amount > 0:
        pos = (spawn_point[0] + random.randint(-spawn_radius, spawn_radius),
               spawn_point[1] + random.randint(-spawn_radius, spawn_radius), 0)
        if E.map.content.get(pos) is not None and E.map.content[pos].walkable:  # Si la case est "marchable"
            pos_already_take = False  # On vérifie que d'autre build ne sont pas déjà sur la case,
            if E.core.pos == pos:
                pos_already_take = True
            if not pos_already_take:
                for build in E.builds:
                    if build.pos == pos:
                        pos_already_take = True
                if not pos_already_take:  # Si c'est le cas on fait apparaîte le cristal à cette position
                    E.builds.append(build_type(pos))
                    amount -= 1


def try_to_add_new_resource_build(build_type=Crystal):
    MAX_CRYSTAL_PER_MAP = 10
    CRYSTAL_SPAWN_CHANCE = 1  # over 1000

    E = Engine.instance

    crystal_amount = 0
    for build in E.builds:
        if isinstance(build, build_type):
            crystal_amount += 1

    if crystal_amount < MAX_CRYSTAL_PER_MAP:
        if random.randint(1, 1000) >= 1000 - CRYSTAL_SPAWN_CHANCE:
            spawn_resources_build_spot(1, build_type)


BUILD_CONVERTER = {Distributor.NAME: Distributor, Pillar.NAME: Pillar, Flower_Build.NAME: Flower_Build,
                   Broken_Core.NAME: Broken_Core}
