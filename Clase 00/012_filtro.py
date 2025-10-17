import py5


def setup():
    py5.size(800,800)


def draw():
    img = py5.load_image("img/Colo.png")
    py5.image(img, 0, 0, 800, 800)  # Especificar el tamaño de la imagen
    py5.apply_filter(py5.INVERT)


def key_pressed():
    py5.save_frame("imagen_invertida.png")
    print("💾 Imagen guardada como 'imagen_invertida.png'")

if __name__ == "__main__":
    py5.key_pressed = key_pressed
    py5.run_sketch()
