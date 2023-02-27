import engine
import entity

# Window data
TITLE = "Fireflies"
DIMENSIONS = (1000, 800)

if __name__ == '__main__':
    e = engine.Engine(TITLE, DIMENSIONS, fps=60)
    
    entity.Firefly.INTERACTIONS = True

    for _ in range(1000):
        firefly = entity.Firefly(DIMENSIONS)
        e.entities.append(firefly)

    e.run()
