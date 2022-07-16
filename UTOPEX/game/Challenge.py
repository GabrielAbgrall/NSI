from engine.Engine import *


def C_NoChest():
    Engine.instance.game_manager.no_chest = True


def C_Weakness():
    Player = Engine.instance.entities[0]
    Player.max_health = Player.max_health // 2
    Player.health = Player.max_health


def C_DoublePower():
    Engine.instance.game_manager.difficulty += 0.5


def C_Melee():
    for wave in Engine.instance.game_manager.waves:
        for enemy in range(len(wave.entities)):
            en_type = type(wave.entities[enemy])
            wave.entities.append(en_type())
