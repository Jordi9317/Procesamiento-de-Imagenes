import py5

img = None

def setup():
    global img
    py5.size(400, 400)
    img = py5.load_image("img/Colo.png")

def draw():
    py5.image(img, 0, 0, 400, 400)
    py5.apply_filter(py5.THRESHOLD, 0.5)

def key_pressed():
    if py5.key == "s" and img is not None:
        # Guardar lo que se ve en la ventana (con filtro)
        py5.save_frame("imagen_blancoynegro.png")
        print("💾 Imagen guardada como 'imagen_blancoynegro.png'")

if __name__ == "__main__":
    py5.key_pressed = key_pressed
    py5.run_sketch()