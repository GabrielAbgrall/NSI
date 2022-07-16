import pygame
import math

from build.Build import *
from engine.Engine import Engine
from engine.Particles import *


class Core(Interaction_Build):
    instance = None
    MAX_LIFE = 100

    CORE_LIFE_BAR_LEN = 700  # Ceci est la longueur de la barre de vie du coeur

    CRYSTAL_FOR_HEAL = 30  # C'est le coup de réparation:
    HEAL_PER_FILL = 5  # De 5% de la vie du coeur à l'aide des cristaux récoltable.

    NAME = "CŒUR"
    ON_CONTENT = ["APPUYEZ /i", f"{CRYSTAL_FOR_HEAL} /c", "SOIGNE LE CŒUR"]

    def __init__(self, pos):  # On crée le coeur à partir de Interaction Build qui
        # hérite lui-même de Build qui gèrent l'affichage, les dégâts pris ou les interractions par le joueur
        texture = pygame.image.load("assets/BUILD/Core.png").convert_alpha()
        collision_radius = 1
        super().__init__(Core.NAME, pos, collision_radius, Core.MAX_LIFE, texture, Core.ON_CONTENT)

        texture_size = self.texture.get_size()  # Il sagit de la taille de assets\BUILD\Core.png qui comporte les 4
        # Etats de destruction du Coeur
        self.textures = [self.texture.subsurface(x, 0, texture_size[0] // 4, texture_size[1])
                         for x in range(0, texture_size[0], texture_size[0] // 4)]
        # La fonction si dessus crée une liste de quatre image découpé dans la grande qu'est assets\BUILD\Core.png
        self.textures.reverse()  # On retourne la liste pour plus de facilité après

        Core.instance = self

    def display(self):  # On réécrit la fonction display pour gèrer le fait d'afficher 4 états differents du Coeur
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        text_index = math.ceil(self.life / (Core.MAX_LIFE / len(self.textures))) - 1  # On définit quelle image afficher
        e.screen.blit(self.textures[text_index], (pos[0] - self.textures[0].get_width() // 2, pos[1] -
                                                  self.textures[text_index].get_height()))  # Puis on l'affiche

    def add_health(self, amount: int) -> None:  # Permet d'ajouter de la vie au Coeur
        self.life += amount if self.life + amount <= Core.MAX_LIFE else Core.MAX_LIFE - self.life

    def remove_health(self, amount: int) -> None:
        self.life -= amount

        if self.life <= 0:
            pass

    def interaction(self):
        # Cette fonction permet d'interragir avec le coeur en le soignant si l'on a assez de cristaux
        if Engine.instance.entities[0].inventory.try_to_remove_crystals(Core.CRYSTAL_FOR_HEAL):
            Engine.instance.entities[0].inventory.remove_crystals(Core.CRYSTAL_FOR_HEAL)
            self.add_health(self.max_life * (Core.HEAL_PER_FILL / 100))

    def get_rect(self):
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        return pygame.rect.Rect((pos[0] - self.textures[0].get_width() // 2,
                                 pos[1] - self.textures[0].get_height(),
                                 self.textures[0].get_width(),
                                 self.textures[0].get_height()))


class Payload(Movable_Build):
    CRYSTAL_FOR_HEAL = 30
    HEAL_PER_FILL = 5
    FUEL_REQUIRED = 50

    MAX_LIFE = 250

    NAME = "VAISSEAU"
    ON_CONTENT_P1 = ["APPUYEZ /i", f"{CRYSTAL_FOR_HEAL} /c", "INTRODUIT DU CARBURANT"]
    ON_CONTENT_P2 = ["APPUYEZ /i", f"{CRYSTAL_FOR_HEAL} /c", "SOIGNE LE VAISSEAU"]

    def __init__(self, pos):
        payload_speed = 0.008
        collision_radius = 4

        texture = pygame.image.load("assets/BUILD/PAYLOAD/RIGHT.png").convert_alpha()

        super().__init__(Payload.NAME, pos, payload_speed, collision_radius, Payload.MAX_LIFE, texture,
                         Payload.ON_CONTENT_P1)

        self.textures = [pygame.image.load("assets/BUILD/PAYLOAD/LEFT.png").convert_alpha(),
                         pygame.image.load("assets/BUILD/PAYLOAD/RIGHT.png").convert_alpha(),
                         pygame.image.load("assets/BUILD/PAYLOAD/UP.png").convert_alpha(),
                         pygame.image.load("assets/BUILD/PAYLOAD/DOWN.png").convert_alpha()]

        self.broken_core = None
        self.broken_core_pos = None

        self.fuel = 0
        self.fuel_required = Payload.FUEL_REQUIRED

        self.phase = 0

        self.travel = [(135, 43, 0), (135, 72, 0), (61, 72, 0), (14, 72, 0), (14, 16, 0)]

        Core.instance = self

    def add_health(self, amount: int) -> None:
        self.life += amount if self.life + amount <= self.max_life else self.max_life - self.life

    def remove_health(self, amount: int) -> None:
        self.life -= amount

    def actualise(self):
        if self.phase == 0:
            self.on_content[1] = f"{self.fuel} / {self.fuel_required} /c"
        elif self.phase == 1:
            if Engine.instance.game_manager.wave_launched:
                vector = (self.travel[0][0] - self.pos[0], self.travel[0][1] - self.pos[1], 0)
                self.move(vector)

                if Engine.instance.plane.distance(self.pos, self.travel[0]) <= 0.2:
                    self.travel.remove(self.travel[0])
                    travel_is_finish = True if len(self.travel) == 0 else False
                    Engine.instance.game_manager.new_phase(travel_is_finish)
                    if travel_is_finish:
                        self.phase += 1

    def get_display_texture(self):
        if len(self.travel) > 0:
            vector = (self.travel[0][0] - self.pos[0], self.travel[0][1] - self.pos[1], self.travel[0][2] - self.pos[2])
            if abs(vector[0]) >= abs(vector[1]):
                if vector[0] > 0:
                    return self.textures[0]
                return self.textures[1]
            else:
                if vector[1] > 0:
                    return self.textures[2]
                return self.textures[3]
        return self.texture

    def display(self):
        e = Engine.instance
        pos1 = e.screen_coordinates(self.pos)
        texture = self.get_display_texture()
        e.screen.blit(texture, (pos1[0] - texture.get_width() // 2, pos1[1] - texture.get_height() // 2))

        if self.phase == 2:
            if self.broken_core_pos is not None:
                pos2 = e.screen_coordinates(self.broken_core_pos)
                pygame.draw.line(Engine.instance.screen, Engine.DARK_BLUE2, (pos1[0], pos1[1]),
                                 (pos2[0], pos2[1] - self.broken_core.get_height() // 2 - 30))
                width_height = (abs(pos1[0] - pos2[0]), abs(pos1[1] - (pos2[1] - self.broken_core.get_height() // 2 - 30)))
                coefficient = random.uniform(0, 1)
                pos = (pos1[0] - width_height[0] * coefficient, pos1[1] + width_height[1] * coefficient)
                Particle(Engine.instance.map_coordinates(pos), 8, Engine.DARK_BLUE2, 0.05)
            else:
                for build in Engine.instance.builds:
                    if isinstance(build, Broken_Core):
                        self.broken_core_pos = build.pos
                        self.broken_core = build.texture

    def interaction(self):
        p = Engine.instance.entities[0]
        if self.phase == 0:
            if p.inventory.try_to_remove_crystals(5):
                self.fuel += 5
                p.inventory.remove_crystals(5)
                if self.fuel >= self.fuel_required:
                    self.phase += 1
                    Engine.instance.game_manager.new_phase(True)
                    self.on_content = Payload.ON_CONTENT_P2
        else:
            if p.inventory.try_to_remove_crystals(Payload.CRYSTAL_FOR_HEAL):
                p.inventory.remove_crystals(Payload.CRYSTAL_FOR_HEAL)
                self.add_health(self.max_life * (Payload.HEAL_PER_FILL / 100))

    def get_rect(self):
        e = Engine.instance
        pos = e.screen_coordinates(self.pos)
        texture = self.get_display_texture()

        return pygame.rect.Rect(pos[0] - texture.get_width() // 2, pos[1] - texture.get_height() // 2,
                                texture.get_width(), texture.get_height())
