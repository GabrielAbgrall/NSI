import time
import random

import engine.BasicFunction
from engine.Engine import *
from build.Build import *
from entity.enemy.Enemy import *
from game.Wave import *


class GameManager:

    instance = None

    def __init__(self, launch_cooldown: int, wave_cooldown: int, alternate_objective=None, infinite_wave=False):
        if alternate_objective is None:
            alternate_objective = []

        self.waves = []                     # Waves list (Waiting the current wave end)
        self.current_wave = None            # Wave in game
        self.wave_cooldown = wave_cooldown  # Time between each wave
        self.wave_launched = False

        self.time_between_enemy = 2   # In sec

        self.waves_accomplished = 0

        self.spawn_points = []              # Possible spawn points of entities

        self.timer = 0                     # Time since the game start
        self.launch_cooldown = launch_cooldown
        self.wave_timer = wave_cooldown
        self.lastUpdate = None

        self.difficulty = 0.9             # Difficulty coefficient (Multiply the life, damage and loots of enemies)
        # The difficulty increase at each waves
        self.difficulty_per_wave = 0.1

        self.infinite_wave = infinite_wave  # Infinite mode parameters
        self.wave_model = [(MainBot, 3), (SpiderBot, 4), (GoldBot, -1), (ScarletSpider, -1)]
        # Start wave of Infinite Mode, evolves over time (thanks to the second difficulty coefficient)
        self.difficulty2 = 1
        self.infinite_wave_created = -1

        self.alternate_objectives = alternate_objective     # All bonus objectives
        self.alternate_objectives_start = copy.deepcopy(self.alternate_objectives)
        self.waves_until_reset_alternate_objectives = 8
        self.do_alternates_objectives = True

        self.chest_spawn_pos = None
        self.chest_actual_pos = 0
        self.no_chest = False

        self.shop_spawn_pos = None
        self.shop_actual_pos = 0
        self.no_shop = False

        self.debug = False                 # Debug message (active or not : Manually)

        # Instance of GameManager to access anywhere in the program
        GameManager.instance = self

    def update(self):
        # Update timers and check if the game or new waves have to launch
        self.update_timer()
        if self.timer >= self.launch_cooldown:
            self.update_wave()

            if self.wave_timer >= self.wave_cooldown:

                if not self.wave_launched:
                    self.wave_launched = True
                    if self.do_alternates_objectives:
                        # Random test, to launch an alternate objective (in terms of the amount of objectives and the
                        # amount of waves remaining (in the list))
                        nb_o = len(self.alternate_objectives)
                        nb_wr = len(self.waves) + 1

                        if random.uniform(0, 1) <= (nb_o / nb_wr) and self.alternate_objectives:
                            Engine.instance.objectives.append(self.alternate_objectives.pop
                                                              (random.randint(0, len(self.alternate_objectives) - 1))())

                if self.current_wave:
                    # Update the current wave (spawn new enemies) and return a boolean who indicate if all mobs of the
                    # wave are dead
                    change_wave = self.actualise_current_wave(self.spawn_points)
                    if change_wave:
                        self.waves_accomplished += 1
                        self.current_wave = None
                        self.wave_timer = 0
                        if self.waves_accomplished % 10 == 0:
                            self.wave_timer -= 50
                            self.wave_cooldown += 30
                        self.update_wave()
                        self.spawn_victory_wave_chest()
                        self.spawn_shop()
                        self.wave_launched = False

    def update_timer(self):
        # Actualise all timer
        if self.lastUpdate is None:
            self.lastUpdate = time.perf_counter()
        now = time.perf_counter()
        elapsed_time = now - self.lastUpdate
        self.timer += elapsed_time
        if self.timer >= self.launch_cooldown:
            self.wave_timer += elapsed_time
        self.lastUpdate = now

    def update_wave(self):
        # If the list of waves is not empty, the function launch a new wave
        if self.current_wave is None and len(self.waves) > 0:
            self.launch_wave()

        if self.current_wave is None and len(self.waves) == 0 and self.infinite_wave:
            for i in range(self.waves_until_reset_alternate_objectives):
                self.create_wave()
            self.create_boss_wave()
            self.reset_alternates_objectives()
            self.launch_wave()

    def launch_wave(self):
        self.difficulty += self.difficulty_per_wave
        self.current_wave = self.waves.pop(0)

    def actualise_current_wave(self, spawn_points) -> bool:
        # Init or update the current wave
        if self.debug and not self.current_wave.launched:
            print(f"New Wave launched")
        return self.current_wave.update(spawn_points, self.difficulty)

    def launch_infinite_mode(self, difficulty="NORMAL"):
        DIFFICULTY = {"NORMAL": 1.1, "EASY": 1.05, "HARD": 1.15, "IMPOSSIBLE": 1.2}

        self.waves = []
        self.infinite_wave = True

        self.difficulty2 = DIFFICULTY[difficulty]
        if not isinstance(self.difficulty2, float):
            self.difficulty2 = DIFFICULTY["NORMAL"]

        self.create_wave()

    def create_wave(self):
        wave = []
        for enemy_tuple in self.wave_model:
            amount = int(enemy_tuple[1] * self.difficulty2)
            if amount == enemy_tuple[1]:
                if self.infinite_wave_created % enemy_tuple[0].OCCURRENCE_FREQUENCY == 0:
                    amount += 1
            wave.append((enemy_tuple[0], amount))

        Wave(self.time_between_enemy).insertion(self, wave)
        self.wave_model = wave
        self.infinite_wave_created += 1
        # print(wave)
        # print(self.infinite_wave_accomplished)

    def create_boss_wave(self):
        Wave(self.time_between_enemy).insertion(self, [(random.choice(BOSS_LIST), 1)])
        self.infinite_wave_created += 1

    def reset_alternates_objectives(self):
        self.alternate_objectives = copy.copy(self.alternate_objectives_start)

    def spawn_victory_wave_chest(self):
        # At each end of wave, a chest spawn at the same coordinate
        if self.chest_spawn_pos is not None and not self.no_chest:
            chest_index = self.chest_actual_pos if self.chest_actual_pos < len(self.chest_spawn_pos) else \
                len(self.chest_spawn_pos) - 1
            Engine.instance.builds.append(Chest(self.chest_spawn_pos[chest_index], self.difficulty))

    def spawn_shop(self):
        if self.waves_accomplished % 2 == 0 and self.shop_spawn_pos is not None and not self.no_shop:
            shop_index = self.shop_actual_pos if self.shop_actual_pos < len(self.shop_spawn_pos) else \
                len(self.shop_spawn_pos) - 1
            Engine.instance.builds.append(Shop_Spot(self.shop_spawn_pos[shop_index]))


class SaveCore_GM(GameManager):
    def __init__(self, launch_cooldown: int, wave_cooldown: int, alternate_objective=None, infinite_wave=False):
        super().__init__(launch_cooldown, wave_cooldown, alternate_objective)

        self.phase = 0

        self.spawn_enemy_start = 0
        self.enemy_spawn = 1

        self.enemy_phase1 = 5
        self.enemy_phase2 = 7

        self.state_without_spawn = 0

    def update(self):
        self.update_timer()
        if self.timer >= self.launch_cooldown:
            if self.phase == 0 and not self.wave_launched:
                spawn_build_around_spawn_point(10, Engine.instance.core.pos, 10, Blue_Crystal)
            self.wave_launched = True
            if self.phase == 0:
                if time.perf_counter() >= self.spawn_enemy_start + self.time_between_enemy + 2.5:
                    enemy_amount = 0
                    for entity in Engine.instance.entities:
                        if isinstance(entity, Enemy):
                            enemy_amount += 1
                    if enemy_amount < self.enemy_phase1:
                        spawn_enemies(1, Engine.instance.core.pos, 10, random.choice(BASIC_ENEMY))
                    self.spawn_enemy_start = time.perf_counter()
            elif self.phase == 1:
                if time.perf_counter() >= self.spawn_enemy_start + self.time_between_enemy + 2:
                    enemy_amount = 0
                    for entity in Engine.instance.entities:
                        if isinstance(entity, Enemy):
                            enemy_amount += 1
                    if enemy_amount < self.enemy_phase2 or self.state_without_spawn >= 15:
                        pos = Engine.instance.core.pos
                        pos = (int(pos[0]), int(pos[1]), 0)
                        if self.state_without_spawn >= 15:
                            spawn_enemies(25, pos, 2, SpiderBot)
                        if self.enemy_spawn % 10 == 0:
                            spawn_enemies(1, pos, 7, random.choice(SPECIAL_ENEMY))
                            spawn_build_around_spawn_point(1, pos, 5, Red_Crystal)
                        else:
                            spawn_enemies(1, pos, 7, random.choice(BASIC_ENEMY))
                        self.state_without_spawn = 0
                    else:
                        self.state_without_spawn += 1
                    self.spawn_enemy_start = time.perf_counter()
                    self.enemy_spawn += 1
            elif self.phase == 2:
                self.update_wave()
                if self.wave_timer >= self.wave_cooldown:
                    if self.current_wave:
                        change_wave = self.actualise_current_wave(self.spawn_points)
                        if change_wave:
                            self.waves_accomplished += 1
                            self.current_wave = None
                            self.wave_timer = 0
                            self.update_wave()
                            self.spawn_victory_wave_chest()
                            self.spawn_shop()
                            self.wave_launched = False

    def new_phase(self, phase_reached: bool):
        if phase_reached:
            self.phase += 1
        self.spawn_victory_wave_chest()
        self.spawn_shop()
        self.shop_actual_pos += 1
        self.chest_actual_pos += 1
        self.timer = -self.wave_cooldown + self.launch_cooldown
        self.difficulty += self.difficulty_per_wave

        self.wave_launched = False

