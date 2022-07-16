import pygame
import math

from entity.Entity import Entity
from engine.Engine import Engine
from entity.player.Player import *
from engine.Particles import *
from entity.Effect import *


class Projectile(Entity):

    def __init__(self, pos: tuple, speed: float, vector: tuple, damage: int, max_distance_travel=100,
                 projectile_radius=3, remove_if_collide=True, damage_if_collide=True, enemy_projectile=False,
                 can_hit_core=True, particle_color=Engine.ORANGE):
        super().__init__(pos, speed)
        self.projectile_radius = projectile_radius
        self.damage = damage
        self.vector = vector
        self.total_distance = 0
        self.max_distance_travel = max_distance_travel
        self.remove_if_collide = remove_if_collide
        self.damage_if_collide = damage_if_collide
        self.enemy_projectile = enemy_projectile
        self.can_hit_core = can_hit_core
        self.particle_color = particle_color
        Engine.instance.projectiles.append(self)

        self.active = True

    def projectile_move(self):
        self.move(self.vector)
        self.total_distance += Engine.instance.plane.distance(self.pos, self.last_pos)
        if not Engine.instance.map.content.get(self.pos) and not Engine.instance.in_screen(self.pos) and self not \
                in Engine.instance.projectiles_to_delete:
            Engine.instance.projectiles_to_delete.append(self)

    def travel_test(self):
        if self.total_distance >= self.max_distance_travel and self not in Engine.instance.projectiles_to_delete:
            Engine.instance.projectiles_to_delete.append(self)

    def display(self):
        if self.active:
            e = Engine.instance
            if not self.enemy_projectile:
                pygame.draw.circle(e.screen, Engine.WHITE, e.screen_coordinates(self.pos), self.projectile_radius)
            else:
                pygame.draw.circle(e.screen, Engine.LIGHT_RED, e.screen_coordinates(self.pos), self.projectile_radius)

    def actualise(self) -> bool:
        if self.active:

            self.projectile_move()
            self.add_particles()

            collide = False
            if self.damage_if_collide:
                if not self.enemy_projectile:
                    for entity in Engine.instance.entities:
                        if isinstance(entity, (Enemy, Boss)) and entity.get_rect().colliderect(self.get_rect()) and \
                                not collide:
                            entity.remove_health(Player.instance.attack_damage_amount(self.damage))
                            collide = True
                            self.to_remove()

                    for build in Engine.instance.builds:
                        if isinstance(build, Destruction_Build) and build.get_rect().colliderect(self.get_rect()):
                            build.damage(Player.instance.attack_damage_amount(self.damage))
                            collide = True
                            self.to_remove()
                else:
                    if Player.instance.get_rect().colliderect(self.get_rect()):
                        Player.instance.remove_health(self.damage)
                        collide = True
                        self.to_remove()

                    elif self.can_hit_core and Core.instance.get_rect().colliderect(self.get_rect()):
                        Core.instance.remove_health(self.damage)
                        collide = True
                        self.to_remove()

            self.travel_test()

            return collide

    def to_remove(self):
        if self.remove_if_collide and self not in Engine.instance.projectiles_to_delete:
            Engine.instance.projectiles_to_delete.append(self)
            return True
        return False

    def get_rect(self):
        screen_pos = Engine.instance.screen_coordinates(self.pos)
        return pygame.rect.Rect(screen_pos[0] - self.projectile_radius,
                                    screen_pos[1] - self.projectile_radius,self.projectile_radius*2,
                                self.projectile_radius*2)

    def add_particles(self):
        pos = (self.pos[0] - self.vector[0] * 0.05,
            self.pos[1] - self.vector[1] * 0.05, 0)
        new_particles_amount = 18
        radius = self.projectile_radius + 1
        for projectile in range(new_particles_amount):
            pr = 1.5 if self.enemy_projectile else 0.75
            Particle(pos, radius, self.particle_color, pr)
            pos = (pos[0] - self.vector[0] * 0.05,
                   pos[1] - self.vector[1] * 0.05, 0)
            radius -= (self.projectile_radius / new_particles_amount)


class Enemy_Projectile(Projectile):
    TRAVEL_DISTANCE = 40
    PROJECTILE_SPEED = 0.1

    def __init__(self, pos, vector: tuple, impact_damage):
        PROJECTILE_RADIUS = 5
        remove_if_collide = True
        enemy_projectile = True
        super().__init__(pos, Enemy_Projectile.PROJECTILE_SPEED, vector, impact_damage,
                         Enemy_Projectile.TRAVEL_DISTANCE, PROJECTILE_RADIUS, remove_if_collide, True, enemy_projectile)


class UIF45_Projectile(Projectile):
    TRAVEL_DISTANCE = 100
    PROJECTILE_SPEED = 0.2

    def __init__(self, pos, vector: tuple, impact_damage, speed=None):
        if speed is None:
            speed = UIF45_Projectile.PROJECTILE_SPEED
        PROJECTILE_RADIUS = 3
        remove_if_collide = True
        enemy_projectile = True
        super().__init__(pos, speed, vector, impact_damage,
                         UIF45_Projectile.TRAVEL_DISTANCE, PROJECTILE_RADIUS, remove_if_collide, True, enemy_projectile,
                         False)


class Rail_gun_projectile(Projectile):
    TRAVEL_DISTANCE = 175
    PROJECTILE_SPEED = 0.3

    def __init__(self, pos, vector: tuple, impact_damage, enemy_projectile):
        PROJECTILE_RADIUS = 8
        remove_if_collide = True
        super().__init__(pos, Rail_gun_projectile.PROJECTILE_SPEED, vector, impact_damage,
                         Rail_gun_projectile.TRAVEL_DISTANCE, PROJECTILE_RADIUS, remove_if_collide, True,
                         enemy_projectile, False, Engine.LIGHT_BLUE)

        self.image = pygame.image.load("assets/OTHER/railgun_projectile.png")
        self.image = pygame.transform.scale(self.image, (PROJECTILE_RADIUS*2, PROJECTILE_RADIUS*2))

    def display(self):
        if self.active:
            e = Engine.instance
            pos = e.screen_coordinates(self.pos)

            e.screen.blit(self.image, (pos[0] - self.projectile_radius, pos[1] - self.projectile_radius))

    def actualise(self) -> bool:
        if self.active:
            self.projectile_move()
            self.add_particles()

            collide = False
            if self.damage_if_collide:
                if self.enemy_projectile:
                    if Player.instance.get_rect().colliderect(self.get_rect()):
                        Player.instance.remove_health(self.damage)
                        Paralysis(3).launch(Player.instance)
                        collide = True
                        self.to_remove()
                else:
                    for entity in Engine.instance.entities:
                        if isinstance(entity, Enemy) and entity.get_rect().colliderect(self.get_rect()):
                            entity.remove_health(self.damage)
                            Paralysis(3).launch(entity)
                            collide = True
                            self.to_remove()

                for build in Engine.instance.builds:
                    if isinstance(build, Destruction_Build) and build.get_rect().colliderect(self.get_rect()):
                        build.damage(self.damage)
                        collide = True
                        self.to_remove()

            return collide


class Sniper_Projectile(Projectile):
    TRAVEL_DISTANCE = 0
    PROJECTILE_SPEED = 0

    def __init__(self, pos, vector: tuple, impact_damage):
        PROJECTILE_RADIUS = 5
        remove_if_collide = True
        super().__init__(pos, Sniper_Projectile.PROJECTILE_SPEED, vector, impact_damage,
                         Sniper_Projectile.TRAVEL_DISTANCE, PROJECTILE_RADIUS, remove_if_collide)


class Bomb_Projectile(Projectile):
    TRAVEL_DISTANCE = 8
    PROJECTILE_SPEED = 0.25

    CHAIN_DEATH_HEALTH_COEFFICIENT = 0.1
    FRAGMENTATION_EXPLOSION_RADIUS = 30

    def __init__(self, pos, vector: tuple, damage, chain_explosion: bool, protection_bomb: bool,
                 fragmentation: bool, environment_damage: bool, instant_explosion: bool, explode_radius=100,
                 damage_if_collide=False, explode_if_collide=False, enemy_projectile=False):
        PROJECTILE_RADIUS = 5
        remove_if_collide = False
        speed = Bomb_Projectile.PROJECTILE_SPEED

        if instant_explosion:
            max_distance_travel = 0
        else:
            max_distance_travel = Bomb_Projectile.TRAVEL_DISTANCE

        super().__init__(pos, speed, vector, damage, max_distance_travel, PROJECTILE_RADIUS, remove_if_collide,
                         damage_if_collide, enemy_projectile)

        # -- Explode Attribute -- #
        self.in_explode = False
        self.explode_speed = 50
        self.explode_radius = explode_radius
        self.explode_frame_account = 0

        # -- Explode Parameters -- #
        self.chain_explosion = chain_explosion
        self.protection_bomb = protection_bomb
        self.fragmentation = fragmentation
        self.environment_damage = environment_damage

        self.explode_if_collide = explode_if_collide

    def display(self):
        if self.active:
            if not self.in_explode:
                super().display()
            else:
                E = Engine.instance
                pygame.draw.circle(E.screen,
                                   (255, 80 + self.explode_frame_account, 35 + 2 * + self.explode_frame_account, 10),
                                   E.screen_coordinates(self.pos), int(self.get_actual_radius()))

    def actualise(self):
        if self.active:
            if self.max_distance_travel == 0:
                self.launch_explosion()
            if not self.in_explode:
                if super().actualise() and self.explode_if_collide:
                    self.launch_explosion()
                elif self.total_distance >= self.max_distance_travel - 3 and self not in Engine.instance.projectiles_to_delete:
                    self.launch_explosion()
            else:
                self.explode()

    def explode(self):
        self.explode_frame_account += 1
        hit_box = self.get_rect()

        if not self.enemy_projectile:
            damage_deal = 0
            damage_deal_per_enemy = Player.instance.attack_damage_amount(self.damage)
            for entity in Engine.instance.entities:
                if isinstance(entity, (Enemy, Boss)) and entity.get_rect().colliderect(hit_box) and not \
                        entity.explosion_damage:
                    is_dead = entity.remove_health(damage_deal_per_enemy)
                    damage_deal += damage_deal_per_enemy
                    if self.chain_explosion and is_dead:
                        Bomb_Projectile(entity.pos, (0, 0, 0), self.damage, False, self.protection_bomb, False,
                                        self.environment_damage, True)
                    entity.explosion_damage = True

            if self.environment_damage:
                for build in Engine.instance.builds:
                    if isinstance(build, Destruction_Build) and build.get_rect().colliderect(hit_box) and not \
                            build.explosion_damage:
                        build.damage(damage_deal_per_enemy)
                        build.explosion_damage = True

            if self.protection_bomb:
                Player.instance.add_health(int(Bomb_Projectile.CHAIN_DEATH_HEALTH_COEFFICIENT * damage_deal))
        else:
            if Player.instance.get_rect().colliderect(hit_box) and not Player.instance.explosion_damage:
                Player.instance.remove_health(self.damage)
                Player.instance.explosion_damage = True

            if Core.instance.get_rect().colliderect(hit_box) and not Core.instance.explosion_damage:
                Core.instance.remove_health(self.damage*3)
                Core.instance.explosion_damage = True

        if self.explode_frame_account == self.explode_speed:
            self.remove_explosion()

    def launch_explosion(self):
        self.in_explode = True
        self.vector = (0, 0, 0)

    def remove_explosion(self):
        self.in_explode = False
        Engine.instance.projectiles_to_delete.append(self)

        for entity in Engine.instance.entities:
            entity.explosion_damage = False

        if self.environment_damage:
            for build in Engine.instance.builds:
                build.explosion_damage = False

        if self.enemy_projectile:
            Player.instance.explosion_damage = False
            Core.instance.explosion_damage = False

        if self.fragmentation:
            Bomb_Projectile((self.pos[0] - 3, self.pos[1], 0), (0, 0, 0), self.damage, False, self.protection_bomb, False,
                            self.environment_damage, True, Bomb_Projectile.FRAGMENTATION_EXPLOSION_RADIUS)
            Bomb_Projectile((self.pos[0] + 3, self.pos[1], 0), (0, 0, 0), self.damage, False, self.protection_bomb, False,
                            self.environment_damage, True, Bomb_Projectile.FRAGMENTATION_EXPLOSION_RADIUS)
            Bomb_Projectile((self.pos[0], self.pos[1] - 3, 0), (0, 0, 0), self.damage, False, self.protection_bomb, False,
                            self.environment_damage, True, Bomb_Projectile.FRAGMENTATION_EXPLOSION_RADIUS)
            Bomb_Projectile((self.pos[0], self.pos[1] + 3, 0), (0, 0, 0), self.damage, False, self.protection_bomb, False,
                            self.environment_damage, True, Bomb_Projectile.FRAGMENTATION_EXPLOSION_RADIUS)

    def get_rect(self):
        screen_pos = Engine.instance.screen_coordinates(self.pos)
        radius = int(self.get_actual_radius())
        return pygame.rect.Rect(screen_pos[0] - radius, screen_pos[1] - radius, 2*radius,
                                2*radius)

    def get_actual_radius(self):
        if not self.in_explode:
            return self.projectile_radius
        return self.explode_frame_account * self.explode_radius / self.explode_speed


