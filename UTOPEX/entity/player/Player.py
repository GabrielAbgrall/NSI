import math
import os

import pygame
from shapely.geometry import Polygon

import engine.BasicFunction
from entity.enemy.Enemy import *


class Player(Smart_Entity):  # Voici le player, il correspond à qui le joueur va joueur
    START_HP = 20
    START_SPEED = 0.1

    MELEE_ATTACK_TOUCH_SOUND = pygame.mixer.Sound(os.path.join("assets", "SOUND", "meleetouch.wav"))
    MELEE_ATTACK_TOUCH_SOUND.set_volume(0.125)
    MELEE_ATTACK_SOUND = pygame.mixer.Sound(os.path.join("assets", "SOUND", "melee.wav"))

    MELEE_ATTACK_CD = 0.5
    MELEE_ATTACK_BASE_DAMAGE = 1

    EXP_COEFFICIENT = 1.2
    MONEY_PER_LVL = 30

    instance = None

    def __init__(self, pos, camera, inventory):
        super().__init__(pos, Player.START_SPEED, Player.START_HP)
        self.image = pygame.image.load(os.path.join("assets", "PLAYER", "RIGHT.png"))
        self.textures = [pygame.image.load(os.path.join("assets", "PLAYER", "LEFT.png")),  # C'est les différentes textures du joueur
                    pygame.image.load(os.path.join("assets", "PLAYER", "RIGHT.png")),
                    pygame.image.load(os.path.join("assets", "PLAYER", "UP.png")),
                    pygame.image.load(os.path.join("assets", "PLAYER", "DOWN.png"))]
        self.last_image = self.image
        self.camera = camera  # La camera est tout le temps cetrée sur le joueur
        if self.camera is not None:
            self.camera.pos = self.pos
        self.inventory = inventory  # Le joueur possède un invetaire dans lequel sont rangé ses utilitaires et ses armes

        self.melee_attack_damage = Player.MELEE_ATTACK_BASE_DAMAGE # Le player à un attauqe de melle avec son clic droit
        self.melee_attack_start_time = None
        self.melee_attack_radius = 10

        self.melee_animation = False
        self.melee_textures = [pygame.image.load(os.path.join("assets", "PLAYER", "Melee_Frame", f"{img}.png")) for img in range(11)]
        self.melee_actual_texture = 0
        self.melee_textures_frame_per_img = 4
        self.melee_textures_actual_frame = 0
        self.melee_angle = 0

        self.visor_mode = False  # Visom mode est activé avec le sniper et la capacité tacticien de la grenade
        self.visor_projectile = None

        self.in_loot = False    # The loot mode is unleashed when the player open a loot_box
        # (Able to display the loot interface)
        self.loot_content = None
        self.loot_position = None
        self.loot_offset = 0

        #  Tout ce qui suit sont des paramètres du joueur
        self.resources_drop_ratio = 1
        self.mining_resources_ratio = 1
        self.lvl = 1
        self.max_lvl = 15
        self.experience = 0
        self.experience_required = 200
        self.talent_point = 1

        Player.instance = self

    def display(self):  # Permet de gèrer l'affichage du joueur
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        texture = self.get_display_texture()  # On définie quelle texture a le joueur
        self.last_image = texture
        e.screen.blit(texture, (pos[0] - self.image.get_width() // 2, pos[1] - self.image.get_height()))

        # Melee attack hit box
        # pygame.draw.polygon(e.screen, Engine.WHITE, self.get_poly())

        if self.melee_animation:
            img = pygame.transform.rotate(self.melee_textures[self.melee_actual_texture],
                                          e.radians_to_degrees(-self.melee_angle) + 90)
            e.screen.blit(img, (pos[0] - img.get_width() // 2, pos[1] - img.get_height() // 2 - 20))
            self.melee_textures_actual_frame += 1
            if self.melee_textures_actual_frame >= self.melee_textures_frame_per_img:
                self.melee_actual_texture += 1
                self.melee_textures_actual_frame = 0
                if self.melee_actual_texture >= len(self.melee_textures):
                    self.melee_animation = False
                    self.melee_actual_texture = 0

    def __setitem__(self, key, value):
        key = value.item_type
        self.inventory[key] = value

    def __getitem__(self, key):
        return self.inventory[key]

    def get_poly(self):
        mouse_pos = pygame.mouse.get_pos()

        center_pos = Engine.instance.screen_coordinates(self.pos)
        center_pos = (center_pos[0] - self.image.get_width() // 2, center_pos[1] - self.image.get_height() // 2)

        x_delta = (mouse_pos[0] - center_pos[0])
        y_delta = (center_pos[1] - mouse_pos[1])
        theta = math.atan2(y_delta, x_delta) + math.pi/2
        theta_orthog = theta + math.pi/2

        shield_center = {
            "lower": pygame.Vector2(
                center_pos[0] + 20 * math.sin(theta),
                center_pos[1] + 20 * math.cos(theta)
            ),
            "upper": pygame.Vector2(
                center_pos[0] + 25 * math.sin(theta),
                center_pos[1] + 25 * math.cos(theta)
            )
        }
        shield_lower = {
            "lower": pygame.Vector2(
                shield_center["lower"][0] - 30 * math.sin(theta_orthog),
                shield_center["lower"][1] - 30 * math.cos(theta_orthog)
            ),
            "upper": pygame.Vector2(
                shield_center["upper"][0] - 30 * math.sin(theta_orthog),
                shield_center["upper"][1] - 30 * math.cos(theta_orthog)
            )
        }
        shield_upper = {
            "lower": pygame.Vector2(
                shield_center["lower"][0] + 30 * math.sin(theta_orthog),
                shield_center["lower"][1] + 30 * math.cos(theta_orthog)
            ),
            "upper": pygame.Vector2(
                shield_center["upper"][0] + 30 * math.sin(theta_orthog),
                shield_center["upper"][1] + 30 * math.cos(theta_orthog)
            )
        }

        return [
            shield_lower["lower"],
            shield_lower["upper"],
            shield_upper["upper"],
            shield_upper["lower"]
        ]

    def get_display_texture(self):  # Cette fonction va à partir du vecteur qu'est en train d'emprunter le joueur
        # définir quelle texture celui-ci va avoir en fonction de si il va en -x, x ,-y, y
        vector = (self.pos[0] - self.last_pos[0], self.pos[1] - self.last_pos[1], self.pos[2] - self.last_pos[2])
        if vector == (0, 0, 0):
            return self.last_image
        if abs(vector[0]) >= abs(vector[1]):
            if vector[0] > 0:
                return self.textures[0]
            return self.textures[1]
        else:
            if vector[1] > 0:
                return self.textures[2]
            return self.textures[3]

    def actualise(self):  # Cette fonction s'occupe de d'enlever els effet du joueur si nécessaire et de
        # réinitialiser le cooldown de l'attaque de melee
        super().actualise()

        if self.melee_attack_start_time is not None and time.perf_counter() - self.melee_attack_start_time >= \
                Player.MELEE_ATTACK_CD * self.attack_speed_ratio:
            self.melee_attack_start_time = None

    def melee_attack(self):  # Melee attaque se déclenche lorque le joueur appuie sur clic droir
        Player.MELEE_ATTACK_SOUND.play()  # Elle joue le son du coup dans le vide
        self.melee_attack_start_time = time.perf_counter()
        self.melee_animation = True
        self.melee_angle = Engine.instance.trigonometric_angle_of_cursor()
        player_rect = self.get_rect()  # Ce rect correspond à l'image du joueur
        #hit_rect = pygame.rect. \
        #    Rect(player_rect.x - self.melee_attack_radius, player_rect.y - self.melee_attack_radius,
        #         player_rect.width + 2 * self.melee_attack_radius, player_rect.height + 2 * self.melee_attack_radius)
        #  Et on crée une hitbox un peu plus grande à partir de cette image

        hit_polygon = Polygon(self.get_poly())

        for ENTITY in Engine.instance.entities:  # On regarde si il y a une collision avec une entitée
            entity_rect = ENTITY.get_rect()
            entity_polygon = Polygon([(entity_rect.x, entity_rect.y), (entity_rect.x + entity_rect.width, entity_rect.y),
                                     (entity_rect.x, entity_rect.y + entity_rect.height),
                                     (entity_rect.x + entity_rect.width, entity_rect.y + entity_rect.height)])
            if isinstance(ENTITY, (Enemy, Boss)) and hit_polygon.intersects(entity_polygon):
                Player.MELEE_ATTACK_TOUCH_SOUND.play()
                ENTITY.remove_health(self.attack_damage_amount(self.melee_attack_damage))  # Et on lui met les dégâts
                return  # Un seul ennemi à la fois peut être touché par l'attaque de melee

        for BUILD in Engine.instance.builds:  # On regarde si il y a une collision avec un build(cristaux)
            build_rect = BUILD.get_rect()
            build_polygon = Polygon([(build_rect.x, build_rect.y), (build_rect.x + build_rect.width, build_rect.y),
                                     (build_rect.x, build_rect.y + build_rect.height),
                                     (build_rect.x + build_rect.width, build_rect.y + build_rect.height)])
            if isinstance(BUILD, Destruction_Build) and hit_polygon.intersects(build_polygon):
                BUILD.damage(self.attack_damage_amount(self.melee_attack_damage) * self.mining_resources_ratio)  # Et on lui met les dégâts
                return   # Un seul cristal à la fois peut être touché par l'attaque de melee

    def move(self, vector: tuple, force_move=False):
        # Move est appliqué sur la position du joueur et de la camera( on leur applique
        # une translation grace à un vecteur)
        if (self.can_move(vector) and not self.paralysis) or force_move:
            self.camera.move(vector)
            super().move(vector)

            if force_move:
                if not 0 <= self.pos[0] < Engine.instance.map.size[0] or not \
                        0 <= self.pos[1] < Engine.instance.map.size[1]:
                    self.pos = self.last_pos
                    self.camera.pos = self.camera.last_pos

    def move_to(self, vector: tuple):  # On téléporte le joueur à une position
        self.camera.move_to(vector)
        super().move_to(vector)

    def can_move(self, vector: tuple) -> bool:  # Cette fonction vérifie que le joueur puisse marcher sur la case
        # vers la quelle il va (donc si la case est marchable et si il ne sors pas de la map)
        super().move(vector)

        pos_float = (self.pos[0], self.pos[1], self.pos[2])
        pos = (int(self.pos[0]), int(self.pos[1]), int(self.pos[2]))

        self.pos = self.last_pos
        #  Si il ne sors pas de la map
        if pos_float[0] < 0 or pos_float[1] < 0 or pos_float[2] < 0:
            return False
        elif (pos[0] < 0 or pos[1] < 0 or pos[2] < 0) or (
                pos[0] > Engine.instance.map.size[0] - 1 or pos[1] > Engine.instance.map.size[1] - 1):
            return False

        #  Si la case vers laquelle il va est marchable
        return Engine.instance.map.content[pos].walkable

    def add_health(self, amount: int) -> None:  # Cette fonction permet d'ajouter de la vie au joueur
        self.health += amount if self.health + amount <= self.max_health else self.max_health - self.health

    def remove_health(self, amount: int) -> None:  # Cette fonction permet de retirer de la vie au joueur
        self.health -= amount

        if self.health <= 0:
            pass

    def change_speed(self, amount: float):  # Augmente la vitesse du joueur et de la camera simultanement ( pour que
        # celle-ci puisse suivre ;p ), la speed correspond à un coefficient par lequel on multiplie le vecteur(
        # inferieur à 1 pour que le joueur ne se téléporte pas car 1 équivaut a la distance entre une case ainsi la
        # speed de base étant 0.1, le joueur fais un dixième de case par raffraichissment)
        super().change_speed(amount)

        self.camera.change_speed(amount)

    def change_resources_drop_ratio(self, amount):
        self.resources_drop_ratio += amount

    def change_mining_resources_ratio(self, amount):
        self.mining_resources_ratio += amount

    def give_exp(self, amount):  # Cette fonction augmente le nombre de point d'experience du joueur, la barre d'xp
        # du joueur, et s'occupe de lui faire passer des niveaux si nécessaire
        self.experience += amount

        if self.experience >= self.experience_required:
            self.lvl += 1
            if self.lvl >= self.max_lvl:
                self.lvl = self.max_lvl
            else:
                self.talent_point += 1
            self.experience -= self.experience_required
            self.experience_required *= Player.EXP_COEFFICIENT
            self.inventory.give_money(Player.MONEY_PER_LVL)

        Engine.instance.HUD.receive_exp(amount)

    def init_visor_mode(self, Projectile):  # Cette fonction active le mode viseur du joueur et elle oblige le joueur
        # à tirer pour sortir de ce mode
        Projectile.active = False
        self.visor_mode = True
        self.visor_projectile = Projectile