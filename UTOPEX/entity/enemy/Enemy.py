from entity.Entity import *
import pygame
from entity.AStar import AStar
import time
import random
from engine.Engine import Engine
from build.Core import *
from entity.Effect import *


class Enemy(Smart_Entity):  # La classe enemy est la clase mère de tout les types d'ennemis si dessous,
    # elle s'occupe du comportement des ennemis, des modification qui leurs sont apportés et de tout ce qui concerne
    # leurs affichage
    HEALTH_BAR_LEN = 30  # C'est la longueur de la barre de vie au dessus de leur têtes
    HEALTH_BAR_HEIGHT = 8  # C'est la hauteur de cette même barre de vie
    PLAYER_HIT_SOUND = pygame.mixer.Sound("assets\SOUND\hit.wav")
    PLAYER_HIT_SOUND.set_volume(0.025)
    CORE_HIT_SOUND = pygame.mixer.Sound("assets\SOUND\core_hit.mp3")
    CORE_HIT_SOUND.set_volume(0.025)
    PATH_FINDING_CD = 1  # C'est le cooldown(donc CD ou delais)entre les actualisation du chemin que prend l'ennemi
    # vers sa cible qui peut être un joueur ou le coeur .

    DISTANCE_DAMAGE_RADIUS = 20

    OCCURRENCE_FREQUENCY = 1

    def __init__(self, speed: float, health: int, cac_damage: bool, image, textures, attack_cd: float, target, damage,
                 money_drop, exp_drop):
        super().__init__((0, 0, 0), speed, health)
        self.image = image  # C'est l'image comportant les 4 positions du jouers
        self.textures = textures  # C'est la liste des différentes position de l'ennemi ( de face, de côté ...)
        self.attack_cd = attack_cd  # C'est le délais entre les attaques
        self.time_since_last_action = 0  # C'est le temps auquel l'ennemi lance son attaque
        self.target = target  # C'est la cible de l'ennemi: Le joueur ou le coeur

        self.last_path_update = 0  # C'est la délais depuis lequel l'ennemi a cherché son chemin

        self.path = []  # C'est la liste des case que dois prendre l'enemy pour aller vers sa cible
        self.destination = None  # C'est la première case qui va l'enmener a sa cible
        self.destination_vector = (0, 0, 0)  # C'est le veteur qui va enmener l'ennemi vers cette case
        self.travel = False  # Cela inqique si l'ennemi est sur sa cible ou non

        self.damage = damage  # C'est les dégâts que fait l'ennemi
        self.cac_damage = cac_damage  # L'ennemie fait t-il des dégâts à distance ou au corps à corps

        self.money_drop = money_drop  # C'est l'argent que va donner l'ennemi une fois mort
        self.exp_drop = exp_drop  # C'est l'expérience que va donner l'ennemi une fois mort

    def find_way(self, target):  # C'est la fonction qui va donner la liste de case pour aller vers la cible
        return Engine.instance.a_star.path(self.pos, target.pos)[1:]

    def remove_health(self, amount: int) -> bool:  # C'est la fonction qui retire de la vie a l'ennemi et qui s'occupe
        # de ce que celui-ci va donner à sa mort
        is_dead = super().remove_health(amount)

        if is_dead:
            Engine.instance.entities[0].inventory.give_money(self.money_drop)  # entities[0] est le joueur
            Engine.instance.entities[0].give_exp(self.exp_drop)
            Engine.instance.entities[0].inventory.inventory["weapon"].drop_ammo()
        return is_dead

    def display(self):  # C'est la fonction qui s'occupe de l'affichage de l'ennemi
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        texture = self.get_display_texture()  # On définie quelle texture a l'ennemi
        e.screen.blit(texture, (pos[0] - self.image.get_width() // 2, pos[1] - self.image.get_height()))

    def get_display_texture(self):  # Cette fonction va à partir du vecteur qu'est en train d'emprunter l'ennemi
        # définir quelle texture celui-ci va avoir en fonction de si il va en -x, x ,-y, y
        if abs(self.destination_vector[0]) >= abs(self.destination_vector[1]):
            if self.destination_vector[0] > 0:
                return self.textures[0]
            return self.textures[1]
        else:
            if self.destination_vector[1] > 0:
                return self.textures[2]
            return self.textures[3]

    def actualise(self):
        # Cette fonction gère tout ce qui est le comportement de l'ennemi
        if self.destination is None:  # Si l'ennemie viens d'apparaître
            self.destination = self.pos

        now = time.perf_counter()
        if now - self.last_path_update > Enemy.PATH_FINDING_CD:  # Si l'ennemie a actulalisé sa route depuis 1 seconde
            self.last_path_update = time.perf_counter()
            if Plane.distance(self.pos, self.target.pos) <= 40:
                self.path = self.find_way(self.target)  # On actualise sa route (liste de case pour atteindre sa cible
        if self.cac_damage:
            self.travel = Plane.distance(self.pos, self.destination) <= 0.2 and len(self.path) > 1  # Si l'ennemi n'est
        # pas arriver à 1/5 de case de sa destination et qu'il a une route pour y aller on actualise self.travel
        else:
            self.travel = Plane.distance(self.pos, self.destination) <= Enemy.DISTANCE_DAMAGE_RADIUS and len(
                self.path) > 1

        if self.travel:  # Si il est actuellement en mouvement
            self.path.remove(self.path[0])  # On sa première destination de la liste des destinations
            self.destination = self.path[0]  # On actualise sa destination
        self.destination_vector = (self.destination[0] - self.pos[0],  # Et la manière de s'y rendre
                                   self.destination[1] - self.pos[1],
                                   self.destination[2] - self.pos[2])
        self.move(self.destination_vector)  # On déplace l'enemy vers sa destination
        # self.draw_way() # Permet de voir le chemin qu'emprunte les ennemis
        if self.cac_damage:
            self.try_cac_damage()
        else:
            self.try_distance_damage()

    def try_cac_damage(self):
        now = time.perf_counter()

        if isinstance(self.target, (Core, Payload)):  # Si la cile est le Coeur
            core = Core.instance
            if core.life > 0:  # Si le coeur à toujours de la vie
                if core.is_colliding(self.pos):  # Et que l'enemie est à portée d'attaque
                    if now - self.time_since_last_action > (self.attack_cd * self.attack_speed_ratio):  # Si il n'a
                        # pas attaqué depuis une durée égale à son cooldown
                        Enemy.CORE_HIT_SOUND.play()
                        self.time_since_last_action = time.perf_counter()
                        self.target.remove_health(self.damage)  # Il attaque
        else:  # Sinon c'est que sa cible est un joueur
            monster_hit_box = self.get_rect()  # On applique le même comportement: Si il peut frapper et qu'il est a
            # portée il frappe
            player_hit_box = self.target.get_rect()
            if monster_hit_box.colliderect(player_hit_box):
                if now - self.time_since_last_action > (self.attack_cd * self.attack_speed_ratio):
                    Enemy.PLAYER_HIT_SOUND.play()
                    self.time_since_last_action = time.perf_counter()
                    self.target.remove_health(self.damage)

    def try_distance_damage(self):
        now = time.perf_counter()

        from entity.Projectile import Enemy_Projectile
        if Engine.instance.plane.distance(self.pos, self.target.pos) <= Enemy.DISTANCE_DAMAGE_RADIUS:
            if now - self.time_since_last_action > (self.attack_cd * self.attack_speed_ratio):
                theta = Engine.instance.trigonometric_angle_of_two_element(self.pos, self.target.pos)
                Enemy_Projectile(self.pos, (math.cos(theta), math.sin(theta), 0),
                                 self.damage)
                self.time_since_last_action = time.perf_counter()

    def draw_way(self):  # Permet de dessiner la route qu'emprunte l'ennemie
        e = Engine.instance
        for i in range(len(self.path) - 1):
            pygame.draw.line(e.screen, (0, 255, 0), e.screen_coordinates(self.path[i]),
                             e.screen_coordinates(self.path[i + 1]))
        pygame.display.flip()

    def use_coefficient(self, coefficient):  # Cette fonction permet de mettre à jour la difficulté, et le taux
        # d'argent et d'expérience donner par l'ennemi
        self.health = int(self.health * coefficient)
        self.max_health = int(self.max_health * coefficient)

        self.damage *= coefficient

        self.money_drop = int(self.money_drop * coefficient)
        self.exp_drop = int(self.exp_drop * coefficient)


class MainBot(Enemy):  # C'est un ennemi humanoïde qui va se diriger lentement mais inexorablement vers le joueur
    # pour lui infliger des attaques au corps à corps
    NAME = "MainBot"
    OCCURRENCE_FREQUENCY = 2

    def __init__(self):
        image = pygame.image.load("assets/ENEMIES/MainBot/RIGHT.png")
        textures = [pygame.image.load("assets/ENEMIES/MainBot/LEFT.png"),  # C'est les différentes textures de l'ennemi
                    pygame.image.load("assets/ENEMIES/MainBot/RIGHT.png"),
                    pygame.image.load("assets/ENEMIES/MainBot/UP.png"),
                    pygame.image.load("assets/ENEMIES/MainBot/DOWN.png")]
        # Ce sont les paramètres de cet ennemi
        START_HP = 10
        START_SPEED = 0.01
        ATTACK_CD = 0.5  # Cooldown entre les attaques
        ATTACK_DAMAGE = 1

        MONEY_DROP_RANGE = [3, 5]
        EXP_DROP_RANGE = [5, 8]

        money_drop = random.randint(MONEY_DROP_RANGE[0], MONEY_DROP_RANGE[1])
        exp_drop = random.randint(EXP_DROP_RANGE[0], EXP_DROP_RANGE[1])

        TARGET = Engine.instance.entities[0]  # Ca cible est le joueur

        cac_damage = True

        super().__init__(START_SPEED, START_HP, cac_damage, image, textures, ATTACK_CD,
                         TARGET, ATTACK_DAMAGE, money_drop, exp_drop)


class SpiderBot(Enemy):  # C'est un ennemi sous la forme d'une araignée mécanique qui va se diriger rapidement et en
    # nombre vers le coeur pour lui infligé de dégâts au corps à corps
    NAME = "SpiderBot"
    OCCURRENCE_FREQUENCY = 1

    def __init__(self):
        image = pygame.image.load("assets/ENEMIES/SpiderBot/RIGHT.png")
        textures = [pygame.image.load("assets/ENEMIES/SpiderBot/LEFT.png"),
                    pygame.image.load("assets/ENEMIES/SpiderBot/RIGHT.png"),
                    pygame.image.load("assets/ENEMIES/SpiderBot/UP.png"),
                    pygame.image.load("assets/ENEMIES/SpiderBot/DOWN.png")]
        # Ce sont les paramètres de cet ennemi

        MONEY_DROP_RANGE = [1, 3]
        EXP_DROP_RANGE = [2, 4]

        START_HP = 5
        START_SPEED = 0.018
        ATTACK_CD = 0.75
        ATTACK_DAMAGE = 1

        money_drop = random.randint(MONEY_DROP_RANGE[0], MONEY_DROP_RANGE[1])
        exp_drop = random.randint(EXP_DROP_RANGE[0], EXP_DROP_RANGE[1])

        TARGET = Engine.instance.core  # Ca cible est le coeur

        cac_damage = True

        super().__init__(START_SPEED, START_HP, cac_damage, image, textures, ATTACK_CD, TARGET, ATTACK_DAMAGE,
                         money_drop, exp_drop)


class GoldBot(Enemy):  # C'est un ennemi sous la forme d'une humanoïde paré d'or qui a pour unique objectif le fait
    # de réduire le joueur en poussière grace à leur gros calibre
    # nombre vers le coeur pour lui infligé de dégâts au corps à corps

    NAME = "GoldBot"
    OCCURRENCE_FREQUENCY = 3

    def __init__(self):
        image = pygame.image.load("assets/ENEMIES/GoldBot/RIGHT.png")
        textures = [pygame.image.load("assets/ENEMIES/GoldBot/LEFT.png"),
                    pygame.image.load("assets/ENEMIES/GoldBot/RIGHT.png"),
                    pygame.image.load("assets/ENEMIES/GoldBot/UP.png"),
                    pygame.image.load("assets/ENEMIES/GoldBot/DOWN.png")]
        # Ce sont les paramètres de cet ennemi

        MONEY_DROP_RANGE = [3, 5]
        EXP_DROP_RANGE = [5, 8]

        START_HP = 25
        START_SPEED = 0.007
        ATTACK_CD = 2.5
        ATTACK_DAMAGE = 2

        money_drop = random.randint(MONEY_DROP_RANGE[0], MONEY_DROP_RANGE[1])
        exp_drop = random.randint(EXP_DROP_RANGE[0], EXP_DROP_RANGE[1])

        TARGET = Engine.instance.entities[0]  # Ca cible est le joueur

        cac_damage = False

        super().__init__(START_SPEED, START_HP, cac_damage, image, textures, ATTACK_CD, TARGET, ATTACK_DAMAGE,
                         money_drop, exp_drop)


class ScarletSpider(Enemy):  # C'est un ennemi sous la forme d'une araignée mécanique qui va se diriger rapidement
    # vers le joueur pour exploser au corps à corps (ou en cas de mort)

    OCCURRENCE_FREQUENCY = 4
    NAME = "ScarletSpider"

    def __init__(self):
        image = pygame.image.load("assets/ENEMIES/ScarletSpider/RIGHT.png")
        textures = [pygame.image.load("assets/ENEMIES/ScarletSpider/LEFT.png"),
                    # C'est les différentes textures de l'ennemi
                    pygame.image.load("assets/ENEMIES/ScarletSpider/RIGHT.png"),
                    pygame.image.load("assets/ENEMIES/ScarletSpider/UP.png"),
                    pygame.image.load("assets/ENEMIES/ScarletSpider/DOWN.png")]
        # Ce sont les paramètres de cet ennemi
        START_HP = 15
        START_SPEED = 0.055
        ATTACK_CD = 0.75
        ATTACK_DAMAGE = 1

        MONEY_DROP_RANGE = [4, 7]
        EXP_DROP_RANGE = [7, 10]

        money_drop = random.randint(MONEY_DROP_RANGE[0], MONEY_DROP_RANGE[1])
        exp_drop = random.randint(EXP_DROP_RANGE[0], EXP_DROP_RANGE[1])

        TARGET = Engine.instance.entities[0]  # Sa cible est le joueur

        cac_damage = True

        super().__init__(START_SPEED, START_HP, cac_damage, image, textures, ATTACK_CD,
                         TARGET, ATTACK_DAMAGE, money_drop, exp_drop)
        self.explosion_damage = 7

    def actualise(self):
        super().actualise()

        if Plane.distance(self.pos, self.target.pos) < 2:
            self.explode()

    def explode(self):
        from entity.Projectile import Bomb_Projectile
        Bomb_Projectile(self.pos, (0, 0, 0), self.explosion_damage
                        , False, False, False, False, True, 75, False, False, True)

        if self not in Engine.instance.entities_to_delete:
            Engine.instance.entities_to_delete.append(self)

        self.health = -1

    def remove_health(self, amount: int) -> bool:
        is_dead = super().remove_health(amount)

        if is_dead:
            self.explode()

        return is_dead


def spawn_enemies(amount: int, spawn_point: tuple, spawn_radius=0, enemy_type=SpiderBot, target=None):
    for enemy in range(amount):
        entity = enemy_type()
        pos = None
        while not Engine.instance.map.content.get(pos) or not Engine.instance.map[pos].walkable:
            pos = (spawn_point[0] + random.randint(-spawn_radius, spawn_radius),
                   spawn_point[1] + random.randint(-spawn_radius, spawn_radius), 0)
        entity.pos = pos
        entity.use_coefficient(Engine.instance.game_manager.difficulty)
        Engine.instance.entities.append(entity)
        if target is not None:
            entity.target = target


def spawn_enemies_at_map_spawn_point(amount, enemy_type=SpiderBot):
    for enemy in range(amount):
        entity = enemy_type()
        entity.pos = random.choice(Engine.instance.game_manager.spawn_points)
        entity.use_coefficient(Engine.instance.game_manager.difficulty)
        Engine.instance.entities.append(entity)


# ----------------------------------------------- #
#                    BOSS                         #
# ----------------------------------------------- #


class Boss(Smart_Entity):
    TIME_BETWEEN_SPAWN_ENEMY = 3  # in sec
    BOSS_KILLED = 0

    def __init__(self, name, speed, health, target, damage, spells, time_between_spell, loot, resource_drop, main_image,
                 textures):
        super().__init__((0, 0, 0), speed, health)
        self.name = name

        self.damage = damage

        self.spells = spells
        self.in_spell = False
        self.spell = None
        self.time_between_spell = time_between_spell
        self.start_spell = time.perf_counter()

        self.angle = 1

        self.time_b_enemy = time.perf_counter()

        self.target = target

        self.image = main_image
        self.textures = textures
        self.texture_state = 0

        self.loot = loot
        self.resource_drop = resource_drop  # List of 2 element - 0: Money, 1: Crystals, 2: Ammo Box , 3: EXP

    def display(self):
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        texture = self.get_display_texture()  # We define which texture we have to display (in terms of his destination)
        e.screen.blit(texture, (pos[0] - texture.get_width() // 2, pos[1] - texture.get_height()))

        # pygame.draw.circle(e.screen, Engine.RED, pos, 3)
        # pygame.draw.circle(e.screen, Engine.GREEN, pos, UIF45.SPELL_RANGE[0] * Engine.instance.plane.size, 2)
        # pygame.draw.circle(e.screen, Engine.DARK_BLUE, pos, UIF45.SPELL_RANGE[1] *

    def remove_health(self, amount: int) -> bool:
        is_dead = super().remove_health(amount)

        if is_dead:
            Engine.instance.builds.append(LootBox(self.pos, self.loot, [self.resource_drop[0], self.resource_drop[1],
                                                                        self.resource_drop[2]]))
            Engine.instance.entities[0].give_exp(self.resource_drop[3])
            Boss.BOSS_KILLED += 1

        return is_dead

    def actualise(self):
        super().actualise()

    def use_coefficient(self, coefficient):
        self.max_health += Boss.BOSS_KILLED * 50
        self.health = self.max_health

    def find_way(self):  # This function give the list of next position of the boss
        pass

    def get_display_texture(self):  # This function choice the texture according to the vector of his destination
        vector = (self.target.pos[0] - self.pos[0], self.target.pos[1] - self.pos[1], self.target.pos[2] - self.pos[2])
        if abs(vector[0]) >= abs(vector[1]):
            side = 0 if vector[0] > 0 else 1
        else:
            side = 2 if vector[1] > 0 else 3
        return self.textures[self.texture_state][side]

    def get_rect(self):  # Give box of the boss
        screen_pos = Engine.instance.screen_coordinates(self.pos)
        texture = self.get_display_texture()
        return pygame.rect.Rect(screen_pos[0] - texture.get_width() // 2, screen_pos[1] - texture.get_height(),
                                texture.get_width(), texture.get_height())


class Boss_Spell:
    def __init__(self, duration, cd):
        self.duration = duration
        self.cd = cd

        self.start_time = None

    def launch_spell(self, boss: Boss):
        pass

    def actualise(self, boss: Boss):
        pass

    def end_spell(self, boss: Boss):
        pass


class UIF45(Boss):
    NAME = "UI F-45"

    START_HP = 275
    START_SPEED = 0.01
    BASE_DAMAGE = 1

    MAIN_IMAGE = pygame.image.load("assets/ENEMIES/UI-F45/0_RIGHT.png")

    TEXTURES = [[pygame.image.load("assets/ENEMIES/UI-F45/0_LEFT.png"),
                 pygame.image.load("assets/ENEMIES/UI-F45/0_RIGHT.png"),
                 pygame.image.load("assets/ENEMIES/UI-F45/0_UP.png"),
                 pygame.image.load("assets/ENEMIES/UI-F45/0_DOWN.png")],

                [pygame.image.load("assets/ENEMIES/UI-F45/1_LEFT.png"),
                 pygame.image.load("assets/ENEMIES/UI-F45/1_RIGHT.png"),
                 pygame.image.load("assets/ENEMIES/UI-F45/1_UP.png"),
                 pygame.image.load("assets/ENEMIES/UI-F45/1_DOWN.png")]]

    MONEY_DROP_RANGE = [130, 200]
    CRYSTAL_DROP_RANGE = [80, 150]
    EXP_DROP_RANGE = [300, 450]

    DAMAGE_DISTANCE_RANGE = [7, 10]
    SPELL_RANGE = [10, 14]

    TIME_BETWEEN_SPELL = 15

    def __init__(self):
        resource_drop = [random.randint(UIF45.MONEY_DROP_RANGE[0], UIF45.MONEY_DROP_RANGE[1]),
                         random.randint(UIF45.CRYSTAL_DROP_RANGE[0], UIF45.CRYSTAL_DROP_RANGE[1]),
                         random.randint(3, 5),
                         random.randint(UIF45.EXP_DROP_RANGE[0], UIF45.EXP_DROP_RANGE[1])]

        target = Engine.instance.entities[0]  # He target the player

        spells = [UIF45_Overload(), UIF45_Rail_gun(), UIF45_Dash()]

        from entity.player.Item import GMV200, Engine_Oil, RailGun
        loot = [(GMV200, 75), (RailGun, 50), (Engine_Oil, 110)]

        super().__init__(UIF45.NAME, UIF45.START_SPEED, UIF45.START_HP, target, UIF45.BASE_DAMAGE, spells,
                         UIF45.TIME_BETWEEN_SPELL, loot, resource_drop, UIF45.MAIN_IMAGE, UIF45.TEXTURES)

        self.ammo = 25
        self.max_ammo = 25
        self.time_between_ammo = 0.04
        self.reload_weapon_time = 5
        self.shoot_time = time.perf_counter()

        self.dash_state = False
        self.overload_state = False

    def actualise(self):
        super().actualise()
        e = Engine.instance
        if not self.dash_state:
            if e.plane.distance(self.pos, self.target.pos) >= UIF45.DAMAGE_DISTANCE_RANGE[1]:
                path = self.find_way()
            else:
                theta = Engine.instance.trigonometric_angle_of_two_element(self.target.pos, self.pos)

                theta += self.angle * math.pi / 16

                path = (self.target.pos[0] + math.cos(theta) * UIF45.DAMAGE_DISTANCE_RANGE[0],
                        self.target.pos[1] + math.sin(theta) * UIF45.DAMAGE_DISTANCE_RANGE[0], self.target.pos[2])
                if not e.map.content.get((int(path[0]), int(path[1]), int(path[2]))):
                    self.angle = -self.angle
            vector = (path[0] - self.pos[0], path[1] - self.pos[1], path[2] - self.pos[2])
        else:
            vector = (self.spell[0] - self.pos[0], self.spell[1] - self.pos[1], self.spell[2] - self.pos[2])

        self.move(vector)

        now = time.perf_counter()
        if now - self.time_b_enemy >= Boss.TIME_BETWEEN_SPAWN_ENEMY:
            spawn_enemies_at_map_spawn_point(1, SpiderBot)
            self.time_b_enemy = now

        if self.ammo > 0 and now - self.shoot_time >= self.time_between_ammo and not self.dash_state:
            self.ammo -= 1
            self.shoot_time = now

            # TODO: AMMO FROM BODY
            from entity.Projectile import UIF45_Projectile
            theta = Engine.instance.trigonometric_angle_of_two_element(self.pos, self.target.pos)
            if not self.overload_state:
                bullet_angle = theta + random.uniform(-(math.pi / 24), (math.pi / 24))
                speed = UIF45_Projectile.PROJECTILE_SPEED
            else:
                bullet_angle = theta + random.uniform(-(math.pi / 16), (math.pi / 16))
                speed = 0.3
            UIF45_Projectile(self.pos, (math.cos(bullet_angle), math.sin(bullet_angle), 0), self.damage, speed)
        elif self.ammo == 0:
            if now - self.shoot_time >= self.reload_weapon_time:
                self.ammo = self.max_ammo

        if self.in_spell:
            self.spell.actualise(self)

        if now - self.start_spell >= self.time_between_spell and self.spell is None:
            if Engine.instance.plane.distance(self.pos, self.target.pos) >= UIF45.SPELL_RANGE[1]:
                self.spell = self.spells[2]
            elif Engine.instance.plane.distance(self.pos, self.target.pos) >= UIF45.SPELL_RANGE[0]:
                self.spell = self.spells[0]
            else:
                self.spell = self.spells[1]
            self.spell.launch_spell(self)
            self.start_spell = now

    def find_way(self):
        theta = Engine.instance.trigonometric_angle_of_two_element(self.target.pos, self.pos)

        return self.target.pos[0] + math.cos(theta) * UIF45.DAMAGE_DISTANCE_RANGE[0], \
            self.target.pos[1] + math.sin(theta) * UIF45.DAMAGE_DISTANCE_RANGE[0], self.target.pos[2]


class UIF45_Dash(Boss_Spell):
    DURATION = 100  # Here the time don't have statement
    CD = 30  # in sec

    def __init__(self):
        super().__init__(UIF45_Dash.DURATION, UIF45_Dash.CD)

        self.boss_new_speed = 0.175
        self.destination = None
        self.damage = 6

        self.hit = False

    def __getitem__(self, item):
        return self.destination[item]

    def launch_spell(self, boss: UIF45):
        boss.in_spell = True
        boss.texture_state = 1
        boss.dash_state = True
        boss.speed = self.boss_new_speed

        theta = Engine.instance.trigonometric_angle_of_two_element(boss.pos, boss.target.pos)

        self.destination = (boss.target.pos[0] + math.cos(theta) * 3, boss.target.pos[1] + math.sin(theta) * 3, 0)
        self.hit = False

    def actualise(self, boss: UIF45):
        if (int(boss.pos[0]), int(boss.pos[1]), int(boss.pos[2])) == \
                (int(self.destination[0]), int(self.destination[1]), int(self.destination[2])):
            self.end_spell(boss)

        if not self.hit:
            hit_box = boss.get_rect()
            # TODO : Effect
            if hit_box.colliderect(boss.target.get_rect()):
                boss.target.remove_health(self.damage)
                self.hit = True

    def end_spell(self, boss: UIF45):
        boss.in_spell = False
        boss.spell = None
        boss.texture_state = 0
        boss.dash_state = False
        boss.speed = UIF45.START_SPEED


class UIF45_Rail_gun(Boss_Spell):
    DURATION = 100  # Here the time don't have statement
    CD = 30  # in sec

    def __init__(self):
        super().__init__(UIF45_Dash.DURATION, UIF45_Dash.CD)

        self.damage = 2

    def launch_spell(self, boss: UIF45):
        boss.in_spell = True

        theta = Engine.instance.trigonometric_angle_of_two_element(boss.pos, boss.target.pos)

        from entity.Projectile import Rail_gun_projectile
        Rail_gun_projectile(boss.pos, (math.cos(theta), math.sin(theta), 0), self.damage, True)

    def actualise(self, boss: UIF45):
        self.end_spell(boss)

    def end_spell(self, boss: UIF45):
        boss.in_spell = False
        boss.spell = None


class UIF45_Overload(Boss_Spell):
    DURATION = 5  # Here the time don't have statement
    CD = 30  # in sec

    def __init__(self):
        super().__init__(UIF45_Overload.DURATION, UIF45_Overload.CD)

        self.time_between_ammo_new = 0.02
        self.time_between_ammo_old = None

    def launch_spell(self, boss: UIF45):
        boss.in_spell = True
        boss.overload_state = True
        boss.ammo = 300
        self.time_between_ammo_old = boss.time_between_ammo
        boss.time_between_ammo = self.time_between_ammo_new

        self.start_time = time.perf_counter()

    def actualise(self, boss: UIF45):
        if time.perf_counter() - self.start_time >= self.duration and boss.overload_state:
            boss.overload_state = False
            boss.shoot_time = time.perf_counter() + self.duration
            Paralysis(self.duration).launch(boss)
        if time.perf_counter() - self.start_time >= self.duration * 2:
            self.end_spell(boss)

    def end_spell(self, boss: UIF45):
        boss.in_spell = False
        boss.spell = None
        boss.ammo = boss.max_ammo
        boss.time_between_ammo = self.time_between_ammo_old


BOSS_LIST = [UIF45]
ENEMY_LIST = [MainBot, SpiderBot, MainBot, ScarletSpider]
BASIC_ENEMY = [MainBot, SpiderBot]
SPECIAL_ENEMY = [GoldBot, ScarletSpider]
ENEMY_CONVERSION = {"ScarletSpider": ScarletSpider, "GoldBot": GoldBot, "MainBot": MainBot, "SpiderBot": SpiderBot,
                    "UI F-45": UIF45}
