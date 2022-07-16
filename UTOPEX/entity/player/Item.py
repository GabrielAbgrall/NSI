import pygame
import time
import math

from entity.Effect import *
from entity.Projectile import *
from engine.Engine import *


# BASE ITEM CLASS

#  La classe item comprend tout ce qui est dans l'inventaire
class Item:
    def __init__(self, name, item_type, image):
        self.name = name
        self.item_type = item_type

        self.image = image
        if isinstance(self, (Rocket_Launcher, Close_Gun, AssaultRifle, Thompson, Precision_Riffle, Imprecise_Riffle)):
            self.image = pygame.transform.scale(self.image, (64, 64))
        else:
            self.image = pygame.transform.scale(self.image, (48, 48))
        if isinstance(self, Weapon):
            self.shop_image = pygame.transform.scale(image, (100, 100))  # Utile pour l'affichage en boutique
        else:
            self.shop_image = pygame.transform.scale(image, (60, 60))

    def use(self):
        pass


# Certain items ont des cool down avant réutilisation ( les consommables ont un cooldown mais ne sont pas
# réutilisable à l'infini)


class Item_with_CD(Item):
    def __init__(self, name, image, cd, item_type):
        super().__init__(name, item_type, image)
        self.cd = cd
        self.start_time = None

    def actualise_state(self):  # Met à jour le cooldown
        if time.perf_counter() >= self.start_time + self.cd:
            self.start_time = None


# ------------------------- #


# TYPE OF ITEMS
class Unique_Item(Item_with_CD):  # Ce sont les items unique qui sont réutilisable à l'infini
    def __init__(self, name, image, cd):
        super().__init__(name, image, cd, "unique")


class Utility_Item(Item_with_CD):  # Ce sont les items qui sont consommable
    def __init__(self, name, image, usage, effects, cd):
        super().__init__(name, image, cd, "utility")
        self.usage = usage
        self.effects = effects

    def use(self) -> bool:
        if self.start_time is None:
            self.usage -= 1
            for effect in self.effects:
                effect.launch(Player.instance)  # On applique l'effet au player
            self.start_time = time.perf_counter()

        return self.usage > 0


class Weapon(Item):  # Ce sont les armes
    def __init__(self, name, image, weapon_type):
        super().__init__(name, "weapon", image)  # "weapon" sert d'index au dictionnaire de Invetory
        self.weapon_type = weapon_type
        self.start_time = None


class Firearm(Weapon):
    def __init__(self, name, image, weapon_type, ammo, time_between_ball, projectile_range,
                 damage, ammo_speed, ammo_drop):
        super().__init__(name, image, weapon_type)
        self.ammo = ammo
        self.start_ammo = ammo

        self.time_between_ball = time_between_ball  # Cooldown entre les balles
        self.projectile_range = projectile_range
        self.damage = damage
        self.ammo_speed = ammo_speed

        self.ammo_drop = ammo_drop

    def drop_ammo(self):  # Lorque l'on tue un ennemie il donne un nombre aléatoire de munition
        self.ammo += random.randint(self.ammo_drop[0], self.ammo_drop[1])

    def refill_ammo(self):
        self.ammo += self.start_ammo

    def semi_refill_ammo(self):
        self.ammo += self.start_ammo // 2

    def actualise_state(self):  # Cooldown entre les tirs
        if self.start_time is not None:
            if time.perf_counter() >= self.start_time + (self.time_between_ball * Player.instance.attack_speed_ratio):
                self.start_time = None


class Spell(Item_with_CD):  # Cette classe correspond au grenade
    def __init__(self, name, image, cd, stack=None):
        super().__init__(name, image, cd, "spell")

        self.stack = stack
        if stack is not None:  # Cela permet d'actualiser le fait que l'on gagne des grenades jusqu'à être au max
            self.max_stack = stack

    # Tout cela correspond au effet appliqués aux cooldown de rechargement (par l'arbre de compétence)
    def increase_stack(self, amount):
        self.max_stack += amount

    def reduce_cd_A(self, amount):
        self.cd -= amount

    def reduce_cd_M(self, coefficient):
        self.cd *= coefficient

    def actualise_state(self):  # On redonne des charges du sort
        if time.perf_counter() >= self.start_time + self.cd:
            if self.stack is not None:
                self.stack += 1
                if self.stack == self.max_stack:
                    self.start_time = None
                else:
                    self.start_time = time.perf_counter()
            else:
                self.start_time = None


# ------------------------- #


# ------------------------- #
class Gun(Firearm):
    SHOT_SOUND = pygame.mixer.Sound("assets\SOUND\Gun.wav")
    SHOT_SOUND.set_volume(0.10)

    def __init__(self, name, image, weapon_type, ammo, time_between_ball, projectile_range,
                 damage, ammo_speed, ammo_drop):
        super().__init__(name, image, weapon_type, ammo, time_between_ball, projectile_range, damage, ammo_speed,
                         ammo_drop)

    def use(self) -> bool:  # Use est appelé quand on appuie sur clic gauche
        if self.start_time is None and self.ammo > 0:
            Gun.SHOT_SOUND.play()
            self.ammo -= 1

            theta = Engine.instance.trigonometric_angle_of_cursor()  # Angle avec lequel part la balle

            Projectile(Player.instance.pos, self.ammo_speed, (math.cos(theta), math.sin(theta), 0), self.damage,
                       self.projectile_range)
            self.start_time = time.perf_counter()

        return self.ammo > 0


class Precision_Riffle(Firearm):

    def __init__(self, name, image, ammo, time_between_ball, projectile_range,
                 damage, ammo_speed, ammo_drop):
        super().__init__(name, image, "SNIPER", ammo, time_between_ball, projectile_range, damage, ammo_speed,
                         ammo_drop)

    def use(self) -> bool:  # Use est appelé quand on appuie sur clic gauche
        if self.start_time is None and self.ammo > 0:
            self.ammo -= 1
            # Le Joueur obtient la vision sniper
            Player.instance.init_visor_mode(Sniper_Projectile(Player.instance.pos,
                                                              (0, 0, 0), self.damage))
            self.start_time = time.perf_counter()

        return self.ammo > 0


class Close_Gun(Firearm):

    def __init__(self, name, image, ammo, bullet, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop):
        super().__init__(name, image, "SHOTGUN", ammo, time_between_ball, projectile_range,
                         damage, ammo_speed, ammo_drop)
        self.bullet = bullet

    def use(self) -> bool:  # Use est appelé quand on appuie sur clic gauche
        if self.start_time is None and self.ammo > 0:
            Gun.SHOT_SOUND.play()
            self.ammo -= 1

            theta = Engine.instance.trigonometric_angle_of_cursor()
            for i in range(self.bullet):
                bullet_angle = theta + random.uniform(-(math.pi / 16), (math.pi / 16))
                speed_inflexion = random.uniform(-0.2, 0.2)
                distance_variation = random.randint(-2, 2)

                Projectile(Player.instance.pos, self.ammo_speed + speed_inflexion
                           , (math.cos(bullet_angle), math.sin(bullet_angle), 0), self.damage, self.projectile_range
                           + distance_variation, 2)

            self.start_time = time.perf_counter()

        return self.ammo > 0


class Imprecise_Riffle(Firearm):

    def __init__(self, name, image, ammo, time_between_ball, projectile_range,
                 damage, ammo_speed, ammo_drop):
        super().__init__(name, image, "RIFLE", ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)

    def use(self) -> bool:  # Use est appelé quand on appuie sur clic gauche
        if self.start_time is None and self.ammo > 0:
            Gun.SHOT_SOUND.play()
            self.ammo -= 1

            theta = Engine.instance.trigonometric_angle_of_cursor()
            bullet_angle = theta + random.uniform(-(math.pi / 24), (math.pi / 24))

            Projectile(Player.instance.pos, self.ammo_speed, (math.cos(bullet_angle), math.sin(bullet_angle), 0),
                       self.damage, self.projectile_range)

            self.start_time = time.perf_counter()

        return self.ammo > 0


class DoubleW_Riffle(Firearm):

    def __init__(self, name, image, weapon_type, ammo, time_between_ball, projectile_range,
                 damage, ammo_speed, ammo_drop, weapon_bullet
                 , reload_time):
        super().__init__(name, image, weapon_type, ammo, time_between_ball, projectile_range,
                         damage, ammo_speed, ammo_drop)

        self.bullet = weapon_bullet
        self.actual_ammo_p = weapon_bullet
        self.reload_time = reload_time

        self.second_time = time.perf_counter()

    def use(self) -> bool:  # Use est appelé quand on appuie sur clic gauche
        if self.start_time is None and self.ammo > 0 and self.actual_ammo_p > 0:
            Gun.SHOT_SOUND.play()
            self.ammo -= 1
            self.actual_ammo_p -= 1

            theta = Engine.instance.trigonometric_angle_of_cursor()

            pos = list(Player.instance.pos)

            pos[0] += 0.5 if self.actual_ammo_p % 2 == 0 else -0.5

            Projectile(tuple(pos), self.ammo_speed, (math.cos(theta), math.sin(theta), 0),
                       self.damage, self.projectile_range)

            self.start_time = time.perf_counter()
            self.second_time = time.perf_counter()

        return self.ammo > 0

    def actualise_state(self):  # Cooldown entre les tirs
        super().actualise_state()

        if time.perf_counter() >= self.second_time + (self.reload_time * Player.instance.attack_speed_ratio):
            self.actual_ammo_p = self.bullet
            self.second_time = time.perf_counter()


class Rocket_Launcher(Firearm):

    def __init__(self, name, image, ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop):
        super().__init__(name, image, "LAUNCHER", ammo, time_between_ball, projectile_range,
                         damage, ammo_speed, ammo_drop)

    def use(self) -> bool:  # Use est appelé quand on appuie sur clic gauche
        if self.start_time is None and self.ammo > 0:
            Gun.SHOT_SOUND.play()
            self.ammo -= 1

            theta = Engine.instance.trigonometric_angle_of_cursor()

            Bomb_Projectile(Player.instance.pos, (math.cos(theta), math.sin(theta), 0), self.damage / 2, False, False,
                            False, True, False, 130, True, True)

            self.start_time = time.perf_counter()

        return self.ammo > 0


class AkimboM(DoubleW_Riffle):
    def __init__(self):
        name = "Mazeta"
        image = pygame.image.load("assets/ITEMS/Mazeta.png")
        ammo = 80
        time_between_ball = 0.05
        projectile_range = 10
        damage = 2
        ammo_speed = 1.4
        ammo_drop = [4, 8]

        bullet = 4
        reload_time = 0.6

        super().__init__(name, image, "PISTOL", ammo, time_between_ball, projectile_range,
                         damage, ammo_speed, ammo_drop, bullet, reload_time)

        self.shop_image = pygame.transform.scale(image, (90, 90))


class PRL7(Rocket_Launcher):
    def __init__(self):
        name = "PRL-7"
        image = pygame.image.load("assets/ITEMS/PRL-7.png")
        ammo = 8
        time_between_ball = 1
        projectile_range = Bomb_Projectile.TRAVEL_DISTANCE
        damage = 6
        ammo_speed = 1
        ammo_drop = [0, 2]
        super().__init__(name, image, ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)


class GMV200(Imprecise_Riffle):
    def __init__(self):
        name = "GMV-200"
        image = pygame.image.load("assets/ITEMS/GMV-200.png")
        ammo = 150
        time_between_ball = 0.025
        projectile_range = 40
        damage = 1
        ammo_speed = 1.25
        ammo_drop = [8, 12]
        super().__init__(name, image, ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)


class Sniper(Precision_Riffle):
    def __init__(self):
        name = "MB4412C"
        image = pygame.image.load("assets/ITEMS/MB4412C.png")
        ammo = 8
        time_between_ball = 1
        projectile_range = 40
        damage = 12
        ammo_speed = 2
        ammo_drop = [0, 2]
        super().__init__(name, image, ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)


class Colt(Gun):
    def __init__(self):
        name = "Colt 9mm"
        image = pygame.image.load("assets/ITEMS/Gun.png")
        ammo = 30
        time_between_ball = 0.5
        projectile_range = 40
        damage = 2
        ammo_speed = 1
        ammo_drop = [2, 5]
        super().__init__(name, image, "PISTOL", ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)

        self.shop_image = pygame.transform.scale(image, (90, 90))


class Fl49(Gun):
    def __init__(self):
        name = "FL-49"
        image = pygame.image.load("assets/ITEMS/FL-49.png")
        ammo = 15
        time_between_ball = 1
        projectile_range = 40
        damage = 4
        ammo_speed = 0.9
        ammo_drop = [2, 3]
        super().__init__(name, image, "PISTOL", ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)


class Thompson(Gun):
    def __init__(self):
        name = "Thompson"
        image = pygame.image.load("assets/ITEMS/Thompson.png")
        ammo = 110
        time_between_ball = 0.1
        projectile_range = 9
        damage = 1
        ammo_speed = 1
        ammo_drop = [5, 10]
        super().__init__(name, image, "RIFLE", ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)


class AssaultRifle(Gun):
    def __init__(self):
        name = "M16 A4"
        image = pygame.image.load("assets/ITEMS/M16A4.png")
        ammo = 50
        time_between_ball = 0.3
        projectile_range = 40
        damage = 4
        ammo_speed = 1
        ammo_drop = [2, 4]
        super().__init__(name, image, "RIFLE", ammo, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)


class ShotGun(Close_Gun):
    def __init__(self):
        name = "RS-X3"
        image = pygame.image.load("assets/ITEMS/RS-X2.png")
        ammo = 15
        time_between_ball = 0.75
        projectile_range = 7
        damage = 1
        ammo_speed = 1
        ammo_drop = [1, 3]

        bullet = 8
        super().__init__(name, image, ammo, bullet, time_between_ball, projectile_range, damage, ammo_speed, ammo_drop)


# ------------------------- #


class Cola(Utility_Item):
    def __init__(self):
        name = "DogaCola"
        image = pygame.image.load("assets/ITEMS/Dogacola.png")
        usage = 3
        cd = 20
        effect = [Damage_Boost(8, 0.5)]
        super().__init__(name, image, usage, effect, cd)


class ChocolateBar(Utility_Item):
    def __init__(self):
        name = "Scarlate"
        image = pygame.image.load("assets/ITEMS/Scarlate.png")
        usage = 3
        cd = 4
        effect = [Give_Health(0, 8)]
        super().__init__(name, image, usage, effect, cd)


class SpicyJuice(Utility_Item):
    def __init__(self):
        name = "SpicyJuice"
        image = pygame.image.load("assets/ITEMS/SpicyJuice.png")
        usage = 3
        cd = 30
        effect = [Give_Speed(8, 0.25)]
        super().__init__(name, image, usage, effect, cd)

        self.shop_image = pygame.transform.scale(image, (50, 50))


class Burger(Utility_Item):
    def __init__(self):
        name = "McDogald"
        image = pygame.image.load("assets/ITEMS/McDogald.png")
        usage = 1
        cd = 30
        effect = [Give_Speed(3, -0.05), Give_Health(0, 15)]
        super().__init__(name, image, usage, effect, cd)

        self.shop_image = pygame.transform.scale(image, (50, 50))


class Candy(Utility_Item):
    def __init__(self):
        name = "Berty Candy"
        image = pygame.image.load("assets/ITEMS/Berty_Candy.png")
        usage = 5
        cd = 12
        effect = [Give_Speed(5, 0.1), Give_Attack_Speed(5, -0.5)]
        super().__init__(name, image, usage, effect, cd)

        self.shop_image = pygame.transform.scale(image, (50, 50))


class Engine_Oil(Utility_Item):
    def __init__(self):
        name = "Carburant"
        image = pygame.image.load("assets/ITEMS/Engine_Oil.png")
        usage = 2
        cd = 20
        effect = [Damage_Boost(10, 0.5), Give_Attack_Speed(10, -0.5)]
        super().__init__(name, image, usage, effect, cd)


class Ammo_Box(Item):
    def __init__(self):
        name = "Boîte de Munitions"
        image = pygame.image.load("assets/ITEMS/Ammo_box.png")
        super().__init__(name, "UTILITY", image)

        self.shop_image = pygame.transform.scale(image, (90, 90))


# ------------------------- #


class Necklace(Unique_Item):  # Collier qui permet de se Téléporter au coeur
    def __init__(self):
        name = "Collier"
        image = pygame.image.load("assets/ITEMS/Necklace.png")
        cd = 60
        super().__init__(name, image, cd)

        self.shop_image = pygame.transform.scale(image, (50, 50))

    def use(self):
        if self.start_time is None:
            self.start_time = time.perf_counter()
            #  Transportation
            Player.instance.move_to((Core.instance.pos[0] - 1, Core.instance.pos[1], Core.instance.pos[2]))


class Transmute(Unique_Item):  # Permet d'échanger sa position avec l'ennemi ciblé
    def __init__(self):
        name = "Transmuteur"
        image = pygame.image.load("assets/ITEMS/Transmuter.png")
        cd = 25
        super().__init__(name, image, cd)

    def use(self):
        if self.start_time is None:
            mouse_coordinates = pygame.mouse.get_pos()
            for enemy in Engine.instance.entities:
                if isinstance(enemy, Enemy) and enemy.get_rect().collidepoint(mouse_coordinates):
                    player_pos = Player.instance.pos
                    Player.instance.move_to(enemy.pos)
                    enemy.move_to(player_pos)
                    self.start_time = time.perf_counter()


class RailGun(Unique_Item):  # Gun who can stunt enemies
    def __init__(self):
        name = "RailGun"
        image = pygame.image.load("assets/ITEMS/RailGun.png")
        cd = 12
        super().__init__(name, image, cd)

        self.damage = 2

    def use(self):
        if self.start_time is None:
            self.start_time = time.perf_counter()

            e = Engine.instance
            p = Player.instance

            theta = e.trigonometric_angle_of_cursor()

            Rail_gun_projectile(p.pos, (math.cos(theta), math.sin(theta), 0),
                                p.attack_damage_amount(self.damage), False)


class Pickaxe(Unique_Item):  # Mining speed is increased
    def __init__(self):
        name = "Pioche"
        image = pygame.image.load("assets/ITEMS/Pickaxe.png")
        cd = 90
        super().__init__(name, image, cd)

    def use(self):
        if self.start_time is None:
            self.start_time = time.perf_counter()

            p = Player.instance

            MiningResourcesRatioBoost(20, 6).launch(p)


class MachCrystal(Unique_Item):  # Mining speed is increased
    def __init__(self):
        name = "Musgravite"
        image = pygame.image.load("assets/ITEMS/MachCrystal.png")
        cd = 4
        super().__init__(name, image, cd)

    def use(self):
        if self.start_time is None:
            self.start_time = time.perf_counter()

            p = Player.instance

            condition = False
            coefficient = 1
            while not condition:
                coefficient -= 0.1
                vector = ((p.pos[0] - p.last_pos[0]) * coefficient, (p.pos[1] - p.last_pos[1]) * coefficient,
                          (p.pos[2] - p.last_pos[2]) * coefficient)
                base_vector = (p.pos[0] + (50 * coefficient) * vector[0], p.pos[1] + (50 * coefficient) * vector[1],
                               p.pos[2] + (50 * coefficient) * vector[2])
                condition = Engine.instance.map.content.get((int(base_vector[0]), int(base_vector[1]),
                                                             int(base_vector[2]))) is not None and \
                            Engine.instance.map.content.get((int(base_vector[0]), int(base_vector[1]),
                                                             int(base_vector[2]))).walkable
                if coefficient <= 0:
                    break

            if condition:
                for e in base_vector:
                    if e < 0:
                        return
                p.move_to(base_vector)


class Bomb(Spell):
    BASE_DAMAGE = 3
    CD = 30
    STACK = 1

    T_FIREWORKS_UP_DAMAGE = 3
    T_FIREWORKS_REDUCE_CD = 5

    T_MASTER_FIREWORKS_NEW_STACK = 1

    T_MASTER_NEW_STACK = 1
    T_MASTER_UP_DAMAGE = 3
    T_MASTER_COEFFICIENT_CD = 0.5

    # Ce sont les effets appliqués aux bombes par l'arbre de compétence
    def T_tact(self):
        self.tact = True

    def T_protection_bomb(self):
        self.protection_bomb = True

    def T_chain_death(self):
        self.chain_death = True

    def T_fireworks(self):
        self.damage += Bomb.T_FIREWORKS_UP_DAMAGE
        self.reduce_cd_A(5)

    def T_master_fireworks(self):
        self.increase_stack(Bomb.T_MASTER_FIREWORKS_NEW_STACK)

    def T_fragmentation(self):
        self.fragmentation = True

    def T_master(self):
        self.master = True
        self.increase_stack(Bomb.T_MASTER_NEW_STACK)
        self.reduce_cd_M(Bomb.T_MASTER_COEFFICIENT_CD)
        self.damage += Bomb.T_MASTER_UP_DAMAGE

    def __init__(self):
        name = "Bombe Cristal"
        image = pygame.image.load("assets/ITEMS/crystal_bomb.png")

        super().__init__(name, image, Bomb.CD, Bomb.STACK)
        self.damage = Bomb.BASE_DAMAGE

        # TALENT CHANGER
        self.tact = False
        self.protection_bomb = False
        self.chain_death = False
        self.fragmentation = False
        self.master = False

    def use(self) -> bool:  # Use envoie une grenade qui est un projectile explosif
        if self.stack >= 1:
            self.stack -= 1

            if not self.tact:  # Tact = True correspond au viseur précis des grenades qui est disponible
                theta = Engine.instance.trigonometric_angle_of_cursor()

                Bomb_Projectile(Player.instance.pos, (math.cos(theta), math.sin(theta), 0), self.damage,
                                self.chain_death,
                                self.protection_bomb, self.fragmentation, self.master, False)
            else:
                Bomb_Projectile(Player.instance.pos, (0, 0, 0), self.damage, self.chain_death,
                                self.protection_bomb, self.fragmentation, self.master, True)
                Engine.instance.projectiles[len(Engine.instance.projectiles) - 1].active = False
                Player.instance.visor_mode = True
                Player.instance.visor_projectile = Engine.instance.projectiles[len(Engine.instance.projectiles) - 1]
                Player.instance.visor_distance = 40

            if self.start_time is None:
                self.start_time = time.perf_counter()

        return True

    def reset_spell(self):
        self.__init__()


all_utility_items = [Burger(), Candy(), ChocolateBar(), Cola(), SpicyJuice()]
all_weapon_items_drop = [Thompson(), AssaultRifle(), Sniper(), ShotGun(), AkimboM()]
all_unique_items = [Necklace(), Transmute(), Pickaxe(), MachCrystal()]
