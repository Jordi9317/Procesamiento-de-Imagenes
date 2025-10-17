import py5

def setup():
    py5.size(400, 400)
    py5.background(255)
    py5.color_mode(py5.RGB, 255)

def draw():
    py5.no_stroke()
    py5.fill(255, 0, 0)  # Triángulo rojo
    py5.triangle(100, 300, 200, 100, 300, 300)

    py5.no_fill()
    py5.stroke(0)  # Contorno negro
    py5.stroke_weight(3)
    py5.circle(200, 220, 100)  # Círculo dentro del triángulo

    py5.save_frame('C:\\Users\\jordi\\OneDrive\\Escritorio\\Tecnicas  Procesca de Imagenes\\Clase 01\\img\\figura_rgb.jpg')  # Guarda la imagen en formato JPEG
    

py5.run_sketch()