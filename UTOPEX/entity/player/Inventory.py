from entity.player.Item import *

# Inventory est une fonction appartenant au player dans lequel se range les armes(weapon), les items uniques(unique),
# les consommables(utility) et les grenades (spell)


class Inventory:
    instance = None

    MAX_MONEY = 999
    MAX_CRYSTALS = 999

    def __init__(self):
        self.inventory = {"spell": None, "weapon": None, "utility": None, "unique": None}

        self.crystals = 0
        self.money = 0

        Inventory.instance = self

    def __setitem__(self, key, value):
        if key != "CRYSTALS" and key != "MONEY":
            self.inventory[key] = value
        else:
            pass

    def set_item(self, ITEM: Item) -> None:  # Permet d'assigner une objet à un slot d'iventaire
        # ( ITEM.item_type peut être = à "weapon" par exemple)
        self.inventory[ITEM.item_type] = ITEM

    def delete_item(self, item_type):  # Supprime tout les items d'un type
        self.inventory[item_type] = None

    def __getitem__(self, item):
        return self.inventory[item]

    def actualise(self):  # Cette fonction vérifie les Cooldown et si il reste bien des charges des utilitaires par
        # exemple( actualise_state se situe dans Item)
        if self.inventory["utility"] is not None and self.inventory["utility"].start_time is not None:
            self.inventory["utility"].actualise_state()
        if self.inventory["weapon"] is not None:
            self.inventory["weapon"].actualise_state()
        if self.inventory["unique"] is not None and self.inventory["unique"].start_time is not None:
            self.inventory["unique"].actualise_state()
        if self.inventory["spell"] is not None and self.inventory["spell"].start_time is not None:
            self.inventory["spell"].actualise_state()

    def give_money(self, amount):  # Cette fonction donne de l'argent et actualise le HUD
        actual_money = self.money

        self.money = self.money + (amount * Player.instance.resources_drop_ratio) \
            if self.money + (amount * Player.instance.resources_drop_ratio)\
                                < Inventory.MAX_MONEY else Inventory.MAX_MONEY

        Engine.instance.HUD.receive_money(amount * Player.instance.resources_drop_ratio)

        return self.money - actual_money

    def remove_money(self, amount):  # Cette fonction retire de l'argent et actualise le HUD
        if self.money - amount >= 0:
            self.money -= amount
        else:
            self.money = 0

    def try_to_remove_money(self, amount) -> bool:  # Cette fonction sert à certain test
        return self.money-amount >= 0

    def give_crystals(self, amount):  # Cette fonction donne des cristaux et actualise le HUD
        actual_crystals = self.crystals

        self.crystals = self.crystals + (amount * Player.instance.resources_drop_ratio)\
            if self.crystals + (amount * Player.instance.resources_drop_ratio) < Inventory.MAX_CRYSTALS else \
            Inventory.MAX_CRYSTALS

        Engine.instance.HUD.receive_crystals(amount * Player.instance.resources_drop_ratio)

        # Return the difference
        return self.crystals - actual_crystals

    def remove_crystals(self, amount):  # Cette fonction retire des cristaux et actualise le HUD
        if self.crystals - amount >= 0:
            self.crystals -= amount
        else:
            self.crystals = 0

    def try_to_remove_crystals(self, amount) -> bool:  # Cette fonction sert à certains tests
        return self.crystals-amount >= 0
