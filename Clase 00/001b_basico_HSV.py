import py5


def setup():
    py5.size(400, 400)
    py5.color_mode(py5.HSB,400, 100, 100)
    py5.background(200)
    print("py5 funcionando correctamente")


def draw():
    py5.fill(235, 40, 30)
    py5.rect(150, 150, 100, 100)
    py5.fill(120, 80, 80)  # Cambia el color si lo deseas
    py5.triangle(200, 100, 120, 300, 280, 300)


py5.run_sketch()
