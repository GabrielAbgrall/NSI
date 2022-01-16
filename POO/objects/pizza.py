class Pizza:
    DOUGHS = {
        "fine": 0.0,
        "classique": 0.0,
        "mozza crust": 2.9,
        "pan": 1.5}

    SIZES = {
        "taille M": 7.99,
        "taille L": 7.99,
        "taille XL": 16.5,
        "taille BigOne": 48}

    INGREDIENTS = {
        "base crème": 0.0,
        "base BBQ": 0.0,
        "base tomate": 0.0,
        "ananas": 1.3,
        "bacon": 2.0,
        "boulettes boeuf": 1.8,
        "champignons": 1.3,
        "mozzarella": 2.0,
        "oignons": 1.0,
        "poivrons": 1.5,
        "piments": 1.0}

    ordered_pizzas = []
    total_income = 0.0

    @classmethod
    def order(cls, pizza):
        Pizza.ordered_pizzas.append(pizza)
        Pizza.total_income += pizza.get_price()

    def __init__(self):
        self.size = "taille M"
        self.dough = "classique"
        self.ingredients = []

    def select_size(self, size: str):
        if size in Pizza.SIZES.keys():
            self.size = size
        else:
            print("Taille indisponible")

    def select_dough(self, dough: str):
        if dough in Pizza.DOUGHS.keys():
            if self.size == "taille M"\
                    or self.size == "taille BigOne"\
                    or self.size == "taille L" and dough == "pan" or dough == "fine"\
                    or self.size == "taille XL" and dough == "fine":
                self.dough = dough
            else:
                print("Pate indisponible pour la pate actuelle")
        else:
            print("Pate indisponible")

    def add_ingredient(self, ingredient):
        self.add_ingredients(ingredient)

    def add_ingredients(self, *ingredients):
        for ingredient in ingredients:
            if ingredient in Pizza.INGREDIENTS:
                if ingredient not in self.ingredients:
                    self.ingredients.append(ingredient)
                else:
                    print("Ingredient déjà utilisé")
            else:
                print("Ingredient indisponible")

    def remove_ingredient(self, ingredient):
        self.remove_ingredients(ingredient)

    def remove_ingredients(self, *ingredients):
        for ingredient in ingredients:
            if ingredient in Pizza.INGREDIENTS and ingredient in self.ingredients:
                self.ingredients.remove(ingredient)
            else:
                print("Cet ingredient n'est pas utilisé")

    def get_price(self):
        price = Pizza.SIZES[self.size] + Pizza.DOUGHS[self.dough]
        for ingredient in self.ingredients:
            price += Pizza.INGREDIENTS[ingredient]
        return price

    def __str__(self):
        ingredients = ""
        for i in range(len(self.ingredients)):
            ingredients += self.ingredients[i]
            if i != len(self.ingredients) - 1:
                ingredients += ", "
        return f"Pizza:\n\ttaille: {self.size}\n\tpate: {self.dough}\n\tingredients: {ingredients}\n\tprix: {self.get_price()}"
