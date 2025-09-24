import py5


def setup():
    # Diferentes resoluciones
    py5.size(1800, 1600)  # HD 4:3
    py5.background(255)

    # Mostrar información de la ventana
    print(f"Ancho: {py5.width} píxeles")
    print(f"Alto: {py5.height} píxeles")
    print(f"Total píxeles: {py5.width * py5.height}")


py5.run_sketch()
