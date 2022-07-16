import entity.Entity

# La camera est toujours centrée sur le joueur ainsi elle possède la même vitesse que lui. Elle hérite de Entitée
# pour pouvoir faire les mêmes déplacement que le joueur qui en est une lui aussi.


class Camera(entity.Entity.Entity):
    SPEED = 0.1

    def __init__(self):
        super().__init__((0, 0, 0), Camera.SPEED)
        self.scale = 1

    def reset_camera(self) -> None:
        self.move_to((0, 0, 0))
