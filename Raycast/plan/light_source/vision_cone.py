from plan.light_source.light_source import LightSource

class VisionCone(LightSource):

    def __init__(self, nb_rays, angle: int):
        super().__init__(nb_rays)
        for ray in self.rays:
            if not(0 <= ray.angle <= angle):
                ray = None
        self.rays = [ray for ray in self.rays if ray is not None]