from engine.Map import Map
from engine.Plane import Plane


class AStar:

    def __init__(self, world_map: Map):
        self.map = world_map
        self.node_set = {}
        self.convert()

    def convert(self):
        # Convertis un objet Map en Node (classe ci-dessous)
        # utilisables par l'algorithme de pathfiding
        self.node_set = {}
        for cell in self.map.content.values():
            # Les valeurs importantes sont sa position et son attribut "walkable"
            # qui permet de savoir si l'entité peut se déplacer sur cette case
            self.node_set[cell.pos] = Node(cell.pos, cell.walkable)

    def path(self, start_pos, target_pos) -> list:
        # Effectue les calculs neccessaires et renvoie le chemin
        # le plus court entre les deux position données en paramètres

        # Creation des Nodes de départ et d'arrivée
        start_node = Node((int(start_pos[0]), int(start_pos[1]), int(start_pos[2])))
        target_node = Node((int(target_pos[0]), int(target_pos[1]), int(target_pos[2])))

        # Deux listes qui permettent de stocker les Nodes à explorer
        # (open_set) et celles déjà vérifiées par l'algorithme (closed_set)
        open_set = [start_node]
        closed_set = []

        # Tant qu'il y a des Nodes à explorer, on continue de chercher
        while len(open_set) > 0:

            # On récupère la Node qui possède le cout total de
            # déplacement le moins cher (pour le chemin le plus court)
            c = self.min(open_set)

            # Mise à jour des listes pour ne pas réitérer avec cette Node
            open_set.remove(c)
            closed_set.append(c)

            if c == target_node:
                # On a trouvé la Node de destination
                # On crée une liste de positions pour
                # créer le chemin vers la destination
                path = self.node_to_path(c)
                if len(path) > 1:
                    if Plane.distance(path[-2], target_pos) < (
                            Plane.distance(path[-2], path[-1]) + Plane.distance(path[-1], target_pos)):
                        # On retire l'avant dernier élément s'il ralonge
                        # le chemin vers la trajectoire exacte de la cible
                        path.remove(path[len(path) - 1])
                path.append(target_pos)
                return path

            for n in self.neighbours(c):
                # On explore tous les voisins de la Node actuelle
                # Pour être valides, on doit pouvoir s'y déplacer
                # Et il ne doivent pas déjà avoir été explorés
                if n.walkable and n not in closed_set:
                    n_cost = c.g_cost + Plane.distance(c.pos, n.pos)
                    if n_cost < n.g_cost or n not in open_set:
                        # Si le nouveau chemin vers cette Node est plus court
                        # on met à jour ses informations
                        n.g_cost = n_cost
                        n.h_cost = Plane.distance(n.pos, target_node.pos)
                        n.f_cost = n.g_cost + n.h_cost
                        n.parent = c

                        if n not in open_set:
                            open_set.append(n)
        return []
    @staticmethod
    def min(lst):
        # Retourne la Node qui possède le cout
        # total de déplacement le plus petit
        m = lst[0]
        for i in range(1, len(lst)):
            c = lst[i]
            if c.f_cost <= m.f_cost and c.h_cost < m.h_cost:
                m = c
        return m

    @staticmethod
    def node_to_path(node) -> list:
        # Convertis le chemin exploré (grace au parent de chaque node)
        # Et crée une liste des positions de chacune de ses Nodes
        r = [node.pos]
        while node.parent:
            node = node.parent
            r.append((node.pos[0] + 0.5, node.pos[1] + 0.5, node.pos[2]))
        r.reverse()
        return r

    def neighbours(self, node):
        # Renvoie tous les voisins existants de la Node passée en paramètres
        r = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    n_pos = (node.pos[0] + x, node.pos[1] + y, node.pos[2] + z)
                    if n_pos in self.node_set:
                        r.append(self.node_set[n_pos])
        return r


class Node:

    def __init__(self, pos, walkable=True):
        self.pos = pos
        self.walkable = walkable
        # Cout de déplacement du chemin suivit depuis le départ
        self.g_cost = 0
        # Cout de déplacement jusqu'à la destination
        # (mis à jour plus tard à la distance a vol d'oiseau)
        self.h_cost = 0
        # Cout total
        self.f_cost = 0
        # Parent de la Node actuelle qui permet de retracer
        # le chemin une fois la destination trouvée
        self.parent = None

    def __eq__(self, other):
        return self.pos == other.pos
