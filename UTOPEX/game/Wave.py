import time
import random
from engine.Engine import Engine


class Wave:

    def __init__(self, cooldown: int):
        self.cooldown = cooldown
        # Entités à envoyer dans le monde
        self.entities = []
        # Entités déjà envoyées dans le monde
        self._cast_entities = []

        # Timer et temp de la dernière
        # mise à jour de ce dernier
        self.timer = cooldown
        self.lastUpdate = -1
        # Permet de savoir si la vague a
        # commencé à être envoyée dans le monde
        self.launched = False

    def add_entities(self, entity_type, number):
        # Ajoute une entité d'un type et d'un nombre donné
        # à la liste des entités de la vague
        for _ in range(number):
            self.entities.append(entity_type())

    def insertion(self, GameManager, entities_list):
        GameManager.waves.append(self)

        for entity_tuple in entities_list:
            self.add_entities(entity_tuple[0], entity_tuple[1])

    def update(self, spawn_points, difficulty) -> bool:
        # Met à jour la vague
        if not self.launched:
            self.launched = True
            self.lastUpdate = time.perf_counter()
            random.shuffle(self.entities)
        self.update_timer()
        if self.timer >= self.cooldown and len(self.entities) > 0:
            # Si le temps nécessaire s'est écoulé,
            # envoie la prochaine entité sur le monde
            entity = self.entities.pop()
            self._cast_entities.append(entity)
            entity.pos = random.choice(spawn_points)
            entity.use_coefficient(difficulty)
            Engine.instance.entities.append(entity)
            self.timer %= self.cooldown

        # Vérifie si au moins une des entités envoyées est encore en vie
        # Sinon le game manager passera a la vague suivante
        if not self.entities:
            for e in self._cast_entities:
                if e.health > 0:
                    return False
            return True
        else:
            return False

    def update_timer(self):
        # Met à jour les timers
        now = time.perf_counter()
        self.timer += now - self.lastUpdate
        self.lastUpdate = now


CLASSIC_WAVES_GAME = [[('MainBot', 3), ('SpiderBot', 5)],
                      [('MainBot', 4), ('SpiderBot', 7)],
                      [('MainBot', 3), ('SpiderBot', 5), ('GoldBot', 1)],
                      [('MainBot', 4), ('SpiderBot', 10), ('GoldBot', 1)],
                      [('MainBot', 3), ('SpiderBot', 7), ('GoldBot', 3), ('ScarletSpider', 1)],
                      [('MainBot', 3), ('SpiderBot', 30), ('GoldBot', 2), ('ScarletSpider', 1)],
                      [('MainBot', 5), ('SpiderBot', 25), ('GoldBot', 2), ('ScarletSpider', 2)],
                      [('UI F-45', 1)]]
