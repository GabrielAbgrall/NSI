import time
from entity.Entity import *


class Effect:
    def __init__(self, duration, amount, image):
        self.duration = duration
        self.amount = amount
        self.start_time = None

        self.image = image

    def launch(self, E: Smart_Entity):
        self.start_time = time.perf_counter()
        E.effects.append(self)

    def remove(self, E: Smart_Entity):
        pass

    def test(self, E: Smart_Entity) -> bool:
        if time.perf_counter() >= self.start_time + self.duration:
            self.remove(E)
            return True

        return False


class Tick_Effect(Effect):
    def __init__(self, duration, amount, tick_per_second, function_per_tick, image):
        super().__init__(duration, amount, image)

        self.tps = tick_per_second
        self.function_per_tick = function_per_tick
        self.last_tick = time.perf_counter()

    def test(self, E: Smart_Entity) -> bool:
        is_del = super().test(E)

        if not is_del and (time.perf_counter() >= self.last_tick + 1 / self.tps):
            self.function_per_tick(E, self.amount)
            self.last_tick = time.perf_counter()

        return is_del


class Damage_Boost(Effect):
    def __init__(self, duration, amount):
        image = pygame.image.load("assets/EFFECT/Damage_Boost.png")
        super().__init__(duration, amount, image)

    def launch(self, E: Smart_Entity):
        super().launch(E)

        E.change_damage_ratio(self.amount)

    def remove(self, E: Smart_Entity):
        E.change_damage_ratio(-self.amount)


class Give_Health(Effect):
    def __init__(self, duration, amount):
        image = None
        super().__init__(duration, amount, image)

    def launch(self, E: Smart_Entity):
        E.add_health(self.amount)


class Give_Speed(Effect):
    def __init__(self, duration, amount):
        image = pygame.image.load("assets/EFFECT/Give_Speed.png")
        super().__init__(duration, amount, image)

    def launch(self, E: Smart_Entity):
        super().launch(E)

        E.change_speed(self.amount)

    def remove(self, E: Smart_Entity):
        E.change_speed(-self.amount)


class Give_Attack_Speed(Effect):
    def __init__(self, duration, amount):
        image = pygame.image.load("assets/EFFECT/Give_Attack_Speed.png")
        super().__init__(duration, amount, image)

    def launch(self, E: Smart_Entity):
        super().launch(E)

        E.change_attack_speed_ratio(self.amount)

    def remove(self, E: Smart_Entity):
        E.change_attack_speed_ratio(-self.amount)


class Paralysis(Effect):
    def __init__(self, duration):
        image = pygame.image.load("assets/EFFECT/Paralysis.png")
        super().__init__(duration, 0, image)

    def launch(self, E: Smart_Entity):
        super().launch(E)

        E.paralysis = True

    def test(self, E: Smart_Entity) -> bool:
        if not E.paralysis:
            E.paralysis = True

        delete = super().test(E)
        return delete

    def remove(self, E: Smart_Entity):
        E.paralysis = False


class ResourcesDropRatioBoost(Effect):
    def __init__(self, duration, amount):
        image = pygame.image.load("assets/EFFECT/ResourcesDropRatioBoost.png")
        super().__init__(duration, amount, image)

    def launch(self, E: Smart_Entity):
        super().launch(E)

        E.change_resources_drop_ratio(self.amount)

    def remove(self, E: Smart_Entity):
        E.change_resources_drop_ratio(-self.amount)


class MiningResourcesRatioBoost(Effect):
    def __init__(self, duration, amount):
        image = pygame.image.load("assets/EFFECT/MiningResourcesBoost.png")
        super().__init__(duration, amount, image)

    def launch(self, E: Smart_Entity):
        super().launch(E)

        E.change_mining_resources_ratio(self.amount)

    def remove(self, E: Smart_Entity):
        E.change_mining_resources_ratio(-self.amount)


class FlowerImpact(Effect):
    def __init__(self):
        image = pygame.image.load("assets/EFFECT/FlowerImpact.png")
        super().__init__(90, 0, image)

    def launch(self, E: Smart_Entity):
        super().launch(E)

        E.change_flower_effect()

    def remove(self, E: Smart_Entity):
        E.change_flower_effect()


class Regeneration(Tick_Effect):
    def __init__(self, duration, amount, tps):
        f = Smart_Entity.add_health
        image = pygame.image.load("assets/EFFECT/Regeneration.png")
        super().__init__(duration, amount, tps, f, image)