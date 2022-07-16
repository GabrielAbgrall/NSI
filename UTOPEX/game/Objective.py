from entity.player.Player import *
from game.GameManager import *


class MainObjective:
    def __init__(self, description: str):
        # Cette fonction définit un objectif principal pour la partie en cours (Il s'agit des variables générales, les
        # vérifications propres à l'objectif sont définit par surcharge)

        # L'objectif est encore réalisable ? (True or False=> Loose)
        self.state = True
        self.finish = False

        self.finish_reason = ""

        self.description = description

    def actualise(self):
        pass

    def end_game(self, victory: bool, reason: str):
        self.state = victory
        self.finish = True
        self.finish_reason = reason


class DefendCore(MainObjective):
    def __init__(self):
        description = "Défendre le coeur"
        super().__init__(description)

    def actualise(self):
        p = Player.instance
        c = Core.instance
        gm = GameManager.instance

        if p.health <= 0:
            self.end_game(False, "Vous avez été abattu par un ennemi !")
        if c.life <= 0:
            self.end_game(False, "Le coeur a été détruit par un ennemi !")

        if gm.current_wave is None and len(gm.waves) == 0:
            self.end_game(True, "Vous avez terrassé toutes les vagues !")


class SaveCore(MainObjective):
    def __init__(self):
        description = "Alimenter le vaisseau"
        super().__init__(description)

        self.frame_before_end = 500
        self.frame_actual = 0

    def actualise(self):
        p = Player.instance
        c = Core.instance
        gm = GameManager.instance

        if gm.phase == 0:
            self.description = "Alimenter le vaisseau"
        elif gm.phase == 1:
            self.description = "Escorter le vaisseau"
        elif gm.phase == 2:
            self.description = "Protéger le vaisseau"

        if p.health <= 0:
            self.end_game(False, "Vous avez été abattu par un ennemi !")
        if c.life <= 0:
            self.end_game(False, "Le vaisseau a été détruit par un ennemi !")

        if gm.current_wave is None and len(gm.waves) == 0:
            self.frame_actual += 1
            if self.frame_actual == 250:
                Engine.instance.HUD.launch_animation(Engine.instance.HUD.FLASH_SCREEN, 2.5)
            if self.frame_actual == 260:
                for build in Engine.instance.builds:
                    if isinstance(build, Broken_Core):
                        build.texture = Core((-1, -1, 0)).textures[3]
            if self.frame_actual >= self.frame_before_end:
                self.end_game(True, "Vous avez sauver le coeur !")


# -------------------------------------------- #

class Objective:
    def __init__(self, loot: list, duration: int, objective_type: str, required_rate: int, description: str, image):
        self.loot = loot
        self.start_time = None
        self.duration = duration

        self.objective_type = objective_type

        self.required_rate = required_rate
        self.actual_rate = 0

        self.description = description
        self.logo = image

    def actualise(self):
        if self.start_time is None:
            self.start_time = time.perf_counter()

        if self.actual_rate >= self.required_rate:
            self.objective_completed()

        if time.perf_counter() >= self.start_time + self.duration:
            self.objective_failed()

    def objective_completed(self):
        p = Player.instance

        p.inventory.give_crystals(self.loot[0])
        p.inventory.give_money(self.loot[1])
        p.give_exp(self.loot[2])

        Engine.instance.objectives_to_delete.append(self)

    def objective_failed(self):
        if self not in Engine.instance.objectives_to_delete:
            Engine.instance.objectives_to_delete.append(self)


class FastCrystal(Objective):

    CRYSTAL_DROP = [80, 100]
    MONEY_DROP = [10, 20]
    EXP_DROP = [30, 50]

    LOGO = pygame.image.load("assets/HUD/objective/crystal_collect_logo.png")

    def __init__(self):
        loot = [random.randint(FastCrystal.CRYSTAL_DROP[0], FastCrystal.CRYSTAL_DROP[1]),
                random.randint(FastCrystal.MONEY_DROP[0], FastCrystal.MONEY_DROP[1]),
                random.randint(FastCrystal.EXP_DROP[0], FastCrystal.EXP_DROP[1])
                ]
        duration = 70
        objective_type = "Crystal_collect"
        description = "Collecter des cristaux"
        crystal_needed = 5
        super().__init__(loot, duration, objective_type, crystal_needed, description, FastCrystal.LOGO)

        self.spawn_crystal = False

    def actualise(self):
        super().actualise()

        if not self.spawn_crystal:
            spawn_resources_build_spot(self.required_rate + 2, Green_Crystal)
            self.spawn_crystal = True


class SpiderInvasion(Objective):

    CRYSTAL_DROP = [30, 50]
    MONEY_DROP = [60, 75]
    EXP_DROP = [40, 70]

    LOGO = pygame.image.load("assets/HUD/objective/spider_spawner_logo.png")

    def __init__(self):
        loot = [random.randint(SpiderInvasion.CRYSTAL_DROP[0], SpiderInvasion.CRYSTAL_DROP[1]),
                random.randint(SpiderInvasion.MONEY_DROP[0], SpiderInvasion.MONEY_DROP[1]),
                random.randint(SpiderInvasion.EXP_DROP[0], SpiderInvasion.EXP_DROP[1])
                ]
        duration = SpiderEgg.TIME_BEFORE_EXPLOSION
        objective_type = "Spider_Invasion"
        description = "Détruire le nid d'araignée"
        needed = 1
        super().__init__(loot, duration, objective_type, needed, description, SpiderInvasion.LOGO)

        self.spawn_egg = False

    def actualise(self):
        super().actualise()

        if not self.spawn_egg:
            spawn_resources_build_spot(1, SpiderEgg)
            self.spawn_egg = True


class SavePnj(Objective):
    CRYSTAL_DROP = [10, 20]
    MONEY_DROP = [60, 90]
    EXP_DROP = [50, 60]

    PNJ_TYPE = [ShopKeeper, Mercenary, Technician]

    LOGO = pygame.image.load("assets/HUD/objective/pnj_head_logo.png")

    def __init__(self):
        loot = [random.randint(SavePnj.CRYSTAL_DROP[0], SavePnj.CRYSTAL_DROP[1]),
                random.randint(SavePnj.MONEY_DROP[0], SavePnj.MONEY_DROP[1]),
                random.randint(SavePnj.EXP_DROP[0], SavePnj.EXP_DROP[1])
                ]
        duration = 30
        objective_type = "Save_PNJ"
        description = "Sauvez le voyageur perdu"
        needed = 1
        super().__init__(loot, duration, objective_type, needed, description, SavePnj.LOGO)

        self.spawn_pnj = False
        self.enemy_amount = int(Engine.instance.game_manager.difficulty * 4)

        self.pnj = None
        self.enemies = []

    def actualise(self):
        if not self.spawn_pnj:
            spawn_resources_build_spot(1, random.choice(SavePnj.PNJ_TYPE))
            self.pnj = Engine.instance.builds[-1]
            self.pnj.in_danger = True

            pos = (int(self.pnj.pos[0]), int(self.pnj.pos[1]), 0)

            spawn_enemies(self.enemy_amount, pos, 4, MainBot, self.pnj)
            for i in range(self.enemy_amount):
                self.enemies.append(Engine.instance.entities[-(i + 1)])

            self.spawn_pnj = True
        else:
            success = True
            for enemy in self.enemies:
                if enemy.health > 0:
                    success = False

            if self.pnj.life <= 0:
                self.objective_failed()

            if success:
                self.actual_rate += 1
                self.pnj.remove_the_danger()

        super().actualise()

    def retarget_player(self):
        for enemy in self.enemies:
            if enemy.health > 0:
                enemy.target = Player.instance

    def objective_failed(self):
        super().objective_failed()
        self.retarget_player()
