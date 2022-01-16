import Map

m = Map.Map("bg.jpg", 500, 400)
m.start()
while m.running:
    m.check()
m.stop()