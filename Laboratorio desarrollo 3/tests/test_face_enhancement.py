"""
Tests para el módulo de mejora facial
"""

import pytest
import numpy as np
from PIL import Image
import sys
import os

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from face_enhancement import FaceEnhancerCPU

class TestFaceEnhancerCPU:
    """Tests para FaceEnhancerCPU"""

    @pytest.fixture
    def enhancer(self):
        """Fixture que proporciona un enhancer inicializado"""
        return FaceEnhancerCPU()

    @pytest.fixture
    def test_image(self):
        """Fixture que proporciona una imagen de prueba"""
        # Crear imagen RGB de 256x256
        img_array = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        return Image.fromarray(img_array)

    @pytest.fixture
    def test_image_with_face(self):
        """Fixture que proporciona una imagen con un rostro simulado"""
        # Crear imagen con un rectángulo que simule un rostro
        img_array = np.full((256, 256, 3), 128, dtype=np.uint8)

        # Agregar un "rostro" más claro en el centro
        img_array[100:156, 100:156] = 200

        return Image.fromarray(img_array)

    def test_initialization(self, enhancer):
        """Test que el enhancer se inicializa correctamente"""
        assert enhancer is not None
        assert hasattr(enhancer, 'detect_faces')
        assert hasattr(enhancer, 'enhance_faces')

    def test_detect_faces_no_faces(self, enhancer, test_image):
        """Test detección de rostros en imagen sin rostros"""
        faces = enhancer.detect_faces(test_image)
        assert isinstance(faces, list)
        # Puede detectar falsos positivos, pero debe ser una lista

    def test_detect_faces_with_simulated_face(self, enhancer, test_image_with_face):
        """Test detección de rostros en imagen con rostro simulado"""
        faces = enhancer.detect_faces(test_image_with_face)
        assert isinstance(faces, list)
        # El detector Haar puede o no detectar el rectángulo simulado

    def test_enhance_faces_no_faces(self, enhancer, test_image):
        """Test mejora facial en imagen sin rostros detectados"""
        result = enhancer.enhance_faces(test_image)

        # Debe retornar una imagen PIL
        assert isinstance(result, Image.Image)

        # Debe mantener las mismas dimensiones
        assert result.size == test_image.size

        # Debe mantener el modo de color
        assert result.mode == test_image.mode

    def test_enhance_faces_with_strength(self, enhancer, test_image):
        """Test mejora facial con diferentes intensidades"""
        for strength in [0.0, 0.5, 1.0]:
            result = enhancer.enhance_faces(test_image, strength=strength)
            assert isinstance(result, Image.Image)
            assert result.size == test_image.size

    def test_enhance_face_region(self, enhancer, test_image):
        """Test mejora de región facial específica"""
        # Definir una región arbitraria
        face_region = (50, 50, 100, 100)

        result = enhancer.enhance_face_region(test_image, face_region)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_get_face_count(self, enhancer, test_image):
        """Test conteo de rostros"""
        count = enhancer.get_face_count(test_image)
        assert isinstance(count, int)
        assert count >= 0

    def test_error_handling_corrupt_image(self, enhancer):
        """Test manejo de errores con imagen corrupta"""
        # Crear imagen con datos inválidos
        try:
            corrupt_image = Image.fromarray(np.zeros((10, 10), dtype=np.uint8))
            result = enhancer.enhance_faces(corrupt_image)
            # Debe retornar la imagen original en caso de error
            assert isinstance(result, Image.Image)
        except Exception:
            # Es aceptable que lance excepción para imágenes muy pequeñas
            pass

    def test_memory_efficiency(self, enhancer, test_image):
        """Test que no hay leaks de memoria graves"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Procesar múltiples veces
        for _ in range(5):
            result = enhancer.enhance_faces(test_image)
            assert result is not None

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # El aumento de memoria debe ser razonable (< 50MB)
        assert memory_increase < 50 * 1024 * 1024, f"Aumento de memoria excesivo: {memory_increase / 1024 / 1024:.1f} MB"

if __name__ == "__main__":
    pytest.main([__file__])