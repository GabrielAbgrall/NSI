import pygame

from entity.player.Item import *
from entity.player.TalentContainer import *

BOMB_SPELL = Bomb()


def Assign_BombSpell():
    global BOMB_SPELL
    Player.instance.inventory.set_item(BOMB_SPELL)


T_Bomb = Talent_Container(
    "Bombe cristal",
    ["Envoie un projectile qui explose et inflige des dégâts"],
    Assign_BombSpell,
    [50, 100],
    pygame.image.load("assets/TALENT/BOMB/Bomb.png")
)

T_Tact = Talent_Container(
    "Tacticien",
    ["Vous pouvez désormais sélectionner une zone d'atterissage"," pour votre bombe"],
    BOMB_SPELL.T_tact,
    [50, 150],
    pygame.image.load("assets/TALENT/BOMB/Tact.png")
)

T_Fireworks = Talent_Container(
    "Artificier",
    ["Augmente les dégâts et et réduit le temps de rechargement", " de 10 sec"],
    BOMB_SPELL.T_fireworks,
    [50, 150],
    pygame.image.load("assets/TALENT/BOMB/Fireworks.png")
)

T_ProtectBomb = Talent_Container(
    "Protectionniste",
    ["Une partie des dégâts infligées par la bombe vous sont remis", "sous forme de PV"],
    BOMB_SPELL.T_protection_bomb,
    [50, 250],
    pygame.image.load("assets/TALENT/BOMB/Protection_Bomb.png")
)

T_ChainDeath = Talent_Container(
    "Mort en chaîne",
    ["Si un ennemi meurt d'une explosion alors une nouvelle", "explosion est déclenchée"],
    BOMB_SPELL.T_chain_death,
    [50, 250],
    pygame.image.load("assets/TALENT/BOMB/Chain_Death.png")
)

T_master_fireworks = Talent_Container(
    "Maître Artificier",
    ["Vous possédez désormais 2 charges"],
    BOMB_SPELL.T_master_fireworks,
    [50, 250],
    pygame.image.load("assets/TALENT/BOMB/Master_Fireworks.png")
)

T_Fragmentation = Talent_Container(
    "Fragmentation",
    ["La bombe déclenche plusieurs petite explosion autour", "du point d'impact"],
    BOMB_SPELL.T_fragmentation,
    [50, 250],
    pygame.image.load("assets/TALENT/BOMB/Fragmentation.png")
)