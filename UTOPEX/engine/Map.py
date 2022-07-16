import ast
import engine.Cell
import copy
import os

from game.Wave import *


class Map:
    def __init__(self):
        self.content = {}  # Dict dans lequel sont rangées les cases avec pour clef les coordonnées tridimenionnelle
        self.size = (0, 0, 0)  # Il sagit des dimentions (x,y,z) max du dict

        self.map_info = {}
        self.background = None  # On ajoute le fond correspondant à la map, ultèrieurement

    def create(self, width: int, height: int, depth: int, content) -> None:
        # Cette fonction crée une map au dimension souhaitée avec un seul type de case dedans
        self.content = {}  # On s'assure que le dict est bien vide
        for x in range(width):
            for y in range(height):
                for z in range(depth):  # On crée le dictionnaire au dimentions souhaitées
                    self.content[(x, y, z)] = copy.copy(content)  # copy permet que les objets soit indépendants
                    self.content[(x, y, z)].pos = (x, y, z)  # On met à jour la variable pos de la case
        self.size = (width, height, depth)  # On actualise le size

    def __getitem__(self, item):
        return self.content[item]

    def __setitem__(self, key, value):
        self.content[key] = value
        self.content[key].pos = key

    def set_case(self, pos: tuple, item) -> None:
        self.__setitem__(pos, item)

    def save(self, localisation: str) -> None:  # Cette fonction permet de sauvegarder une map sous forme de TXT

        if not os.path.exists(localisation):
            os.makedirs(localisation)

        for index in self.content:  # Pour chaque Case du dictionnaire
            if isinstance(self.content[index], engine.Cell.Cell):  # On vérifie que c'est un objet de type Cell
                self.content[index] = self.content[index].__dict__  # On convertie cet objet sous forme de Dict
        with open(f"{localisation}/map.txt", 'w') as f:
            f.writelines(str(self.content))  # On sauvegarde ce dict d'objet sous forme de dict dans un TXT
        with open(f"{localisation}/map_info.txt", 'w') as f:
            f.writelines(str(self.map_info))

    def load_save(self, localisation: str) -> None:  # Cette fonction permet de charger une map étant sous forme de TXT
        with open(f"{localisation}/map.txt", 'r') as f:
            read = ast.literal_eval(f.read())  # on convertie la ligne du TXT(qui est un str) en un dict
            for index in read:  # Et pour tout les élément de ce dictionnaire
                if isinstance(read[index], dict):  # Si il sagit bien d'un dict on recrer un objet à partir de celui-ci
                    read[index] = engine.Cell.Cell(read[index]['walkable'], read[index]['color'], read[index]['pos'],
                                                   read[index]["spawn_point"])
            self.content = read
            x, y, z = 0, 0, 0  # La fin de la fonction permet de remettre à jour self.size à partir de la nouvelle map
            for index in self.content:
                x = index[0] if index[0] > x else x
                y = index[1] if index[1] > y else y
                z = index[2] if index[2] > z else z
            self.size = (x + 1, y + 1, z + 1)

        with open(f"{localisation}/map_info.txt", 'r') as f:
            read = ast.literal_eval(f.read())
            self.map_info = read

    def insert_data(self, GameManager, EnemyConversionKey: dict):
        self.insert_all_spawn_points(GameManager)
        self.insert_map_info(GameManager)
        self.insert_map_waves(GameManager, EnemyConversionKey)

    def insert_all_spawn_points(self, GameManager):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                for z in range(self.size[2]):
                    if self[(x, y, z)].spawn_point:
                        GameManager.spawn_points.append((x, y, z))

    def insert_map_info(self, GameManager):
        GameManager.do_alternates_objectives = self.map_info.get("DO_AO") if self.map_info.get("DO_AO") \
                                                                             is not None else True
        GameManager.chest_spawn_pos = self.map_info.get("CHEST_SPAWN_POS")
        GameManager.shop_spawn_pos = self.map_info.get("SHOP_SPAWN_POS")

    def spawn_all_builds(self, E: Engine):
        if self.map_info.get("BUILDS") is not None:
            from build.Build import BUILD_CONVERTER
            for build in self.map_info["BUILDS"]:
                E.builds.append(BUILD_CONVERTER[build[0]](build[1]))

    def insert_map_waves(self, GameManager, EnemyConversionKey: dict):
        waves_to_add = self.map_info.get("WAVES") if self.map_info.get("WAVES") is not None else CLASSIC_WAVES_GAME

        for wave in waves_to_add:
            entities_list = []
            for entity_type in wave:
                entities_list.append((EnemyConversionKey[entity_type[0]], entity_type[1]))
            Wave(GameManager.time_between_enemy).insertion(GameManager, entities_list)

    def set_background(self, image):
        self.background = image


