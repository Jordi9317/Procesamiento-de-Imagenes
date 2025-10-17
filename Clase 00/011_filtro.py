import py5

img = None

def setup():
    global img
    py5.size(400, 400)
    img = py5.load_image("img/Colo.png")

def draw():
    py5.image(img, 0, 0, 400, 400)
    py5.apply_filter(py5.GRAY)

def key_pressed():
    if py5.key == "s":
        py5.save_frame("imagen_ColoGris.png")
        print("💾 Imagen guardada como 'imagen_ColoGris.png'")

if __name__ == "__main__":
    py5.key_pressed = key_pressed
    py5.run_sketch()
