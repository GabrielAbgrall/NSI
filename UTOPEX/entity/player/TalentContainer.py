class Talent_Container:
    def __init__(self, name, description, talent, price, image):
        self.name = name
        self.description = description
        self.talent = talent
        self.price = price
        self.image = image

        self.player_get = False
        self.upper_state = False
