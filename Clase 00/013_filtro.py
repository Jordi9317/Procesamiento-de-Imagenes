import py5


def setup():
    py5.size(400, 400)


def draw():
    img = py5.load_image("img/Colo.png")
    py5.image(img, 0, 0, 400, 400)  # Especificar el tamaño de la imagen
    py5.apply_filter(
        py5.BLUR, 5
    )  # Aplicar un filtro de desenfoque con un radio de 5 píxeles


def key_pressed():
    py5.save_frame("imagen_blur.png")
    print("💾 Imagen guardada como 'imagen_blur.png'")

if __name__ == "__main__":
    py5.key_pressed = key_pressed
    py5.run_sketch()
