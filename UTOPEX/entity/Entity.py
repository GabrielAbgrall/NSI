import pygame

from engine.Plane import Plane
from engine.Engine import Engine

# La classe est le nerf de la guerre du programme car elle gère tout ce qui concerne les chose qui peuvent bouger.
# Elle est à l'origine de beaucoup d'héritage.


class Entity:
    def __init__(self, pos, speed) -> None:
        self.pos = pos
        self.last_pos = pos
        self.speed = speed

    def move(self, pos):  # The function take a vector and apply few transformations to move the entity
        norm = Plane.distance((0, 0, 0), pos)
        self.last_pos = tuple(self.pos)
        if norm == 0:
            return
        vector = (pos[0] / norm, pos[1] / norm, pos[2] / norm)
        self.pos = (self.pos[0] + vector[0] * self.speed, self.pos[1] + vector[1] * self.speed, self.pos[2] + vector[2] * self.speed)

    def move_to(self, pos: tuple) -> None:  # Move entity
        self.pos = pos

    def display(self):
        pass  # Cette fonction est overwrite plus tard

    def actualise(self):
        pass  # Cette fonction est overwrite plus tard

    def change_speed(self, amount):
        self.speed += amount  # La speed est appliquée sur le vecteur dans move


class Smart_Entity(Entity):  # Les entitées intelligentes sont les ennemie et le player ils ont donc de la vie et des
    # effets peuvent leur être applqiués
    def __init__(self, pos, speed, health):
        super().__init__(pos, speed)
        self.health = health
        self.max_health = health

        self.effects = []

        self.attack_damage_ratio = 1
        self.attack_speed_ratio = 1

        self.explosion_damage = False
        self.paralysis = False
        self.flower_effect = False

    # Ce sont des effets appliqués au joueur par les consommables pour les rendres plus fort et aux ennemies à la fin
    # des vagues pour augmentée la difficultées de ceux-ci

    def move(self, pos):
        if not self.paralysis:
            super().move(pos)

    def change_damage_ratio(self, amount):
        self.attack_damage_ratio += amount

    def change_attack_speed_ratio(self, amount):
        self.attack_speed_ratio += amount

    def attack_damage_amount(self, attack):
        return attack * self.attack_damage_ratio

    def change_flower_effect(self):
        self.flower_effect = not self.flower_effect

    def actualise(self):  # Cette fonction s'occupe de retirer les effets qui ont expirés
        delete_effect = []
        for effect in self.effects:
            if effect.test(self):
                delete_effect.append(effect)
        for effect in delete_effect:
            self.effects.remove(effect)

    def add_health(self, amount: int) -> None:  # Ajoute de la vie si c'est possible
        self.health += amount if self.health + amount <= self.max_health else self.max_health - self.health

    def remove_health(self, amount: int) -> bool:  # Retire de la vie si c'est possible et tue l'entitée si elle n'a
        # plus de vie
        self.health -= amount

        if self.health <= 0:
            if self not in Engine.instance.entities_to_delete:
                Engine.instance.entities_to_delete.append(self)
                return True
        return False

    def get_rect(self):  # Donne la hitbox de l'entité
        screen_pos = Engine.instance.screen_coordinates(self.pos)
        return pygame.rect.Rect(screen_pos[0] - self.image.get_width() // 2, screen_pos[1] - self.image.get_height(),
                                self.image.get_width(), self.image.get_height())
