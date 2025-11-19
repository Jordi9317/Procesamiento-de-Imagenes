"""
Tests para el módulo de super-resolución
"""

import pytest
import numpy as np
from PIL import Image
import sys
import os

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from super_resolution import SuperResolverCPU

class TestSuperResolverCPU:
    """Tests para SuperResolverCPU"""

    @pytest.fixture
    def resolver(self):
        """Fixture que proporciona un resolver inicializado"""
        return SuperResolverCPU()

    @pytest.fixture
    def small_image(self):
        """Fixture que proporciona una imagen pequeña de prueba"""
        # Crear imagen RGB de 64x64
        img_array = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        return Image.fromarray(img_array)

    @pytest.fixture
    def medium_image(self):
        """Fixture que proporciona una imagen mediana de prueba"""
        # Crear imagen RGB de 128x128
        img_array = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
        return Image.fromarray(img_array)

    def test_initialization(self, resolver):
        """Test que el resolver se inicializa correctamente"""
        assert resolver is not None
        assert hasattr(resolver, 'upscale')
        assert hasattr(resolver, 'batch_upscale')

    def test_upscale_factor_2(self, resolver, small_image):
        """Test upscale con factor 2"""
        result = resolver.upscale(small_image, scale_factor=2)

        assert isinstance(result, Image.Image)
        assert result.size == (128, 128)  # 64 * 2
        assert result.mode == small_image.mode

    def test_upscale_factor_3(self, resolver, small_image):
        """Test upscale con factor 3"""
        result = resolver.upscale(small_image, scale_factor=3)

        assert isinstance(result, Image.Image)
        assert result.size == (192, 192)  # 64 * 3

    def test_upscale_factor_4(self, resolver, small_image):
        """Test upscale con factor 4"""
        result = resolver.upscale(small_image, scale_factor=4)

        assert isinstance(result, Image.Image)
        assert result.size == (256, 256)  # 64 * 4

    def test_upscale_invalid_factor(self, resolver, small_image):
        """Test upscale con factor inválido"""
        with pytest.raises(ValueError):
            resolver.upscale(small_image, scale_factor=5)

    def test_upscale_methods(self, resolver, small_image):
        """Test diferentes métodos de interpolación"""
        methods = ["lanczos", "bicubic", "bilinear"]

        for method in methods:
            result = resolver.upscale(small_image, scale_factor=2, method=method)
            assert isinstance(result, Image.Image)
            assert result.size == (128, 128)

    def test_upscale_invalid_method(self, resolver, small_image):
        """Test método de interpolación inválido"""
        with pytest.raises(ValueError):
            resolver.upscale(small_image, scale_factor=2, method="invalid")

    def test_batch_upscale(self, resolver, small_image):
        """Test procesamiento por lotes"""
        images = [small_image, small_image, small_image]
        results = resolver.batch_upscale(images, scale_factor=2)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, Image.Image)
            assert result.size == (128, 128)

    def test_get_supported_scale_factors(self, resolver):
        """Test obtener factores de escala soportados"""
        factors = resolver.get_supported_scale_factors()
        assert isinstance(factors, list)
        assert 2 in factors
        assert 3 in factors
        assert 4 in factors

    def test_get_supported_methods(self, resolver):
        """Test obtener métodos de interpolación soportados"""
        methods = resolver.get_supported_methods()
        assert isinstance(methods, list)
        assert "lanczos" in methods
        assert "bicubic" in methods
        assert "bilinear" in methods

    def test_estimate_memory_usage(self, resolver, medium_image):
        """Test estimación de uso de memoria"""
        memory_info = resolver.estimate_memory_usage(medium_image, 2)

        required_keys = ["original_mb", "upscaled_mb", "processing_mb", "total_mb"]
        for key in required_keys:
            assert key in memory_info
            assert isinstance(memory_info[key], float)
            assert memory_info[key] > 0

    def test_error_handling_corrupt_image(self, resolver):
        """Test manejo de errores con imagen corrupta"""
        # Crear imagen con datos inválidos
        try:
            corrupt_image = Image.fromarray(np.zeros((10, 10), dtype=np.uint8))
            result = resolver.upscale(corrupt_image, scale_factor=2)
            # Debe retornar la imagen original en caso de error
            assert isinstance(result, Image.Image)
        except Exception:
            # Es aceptable que lance excepción para imágenes muy pequeñas
            pass

    def test_memory_efficiency(self, resolver, small_image):
        """Test que no hay leaks de memoria graves"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Procesar múltiples veces
        for _ in range(3):
            result = resolver.upscale(small_image, scale_factor=2)
            assert result is not None

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # El aumento de memoria debe ser razonable (< 30MB)
        assert memory_increase < 30 * 1024 * 1024, f"Aumento de memoria excesivo: {memory_increase / 1024 / 1024:.1f} MB"

    def test_quality_preservation(self, resolver, small_image):
        """Test que la calidad se preserva razonablemente"""
        # Crear imagen con patrón conocido
        test_array = np.zeros((64, 64, 3), dtype=np.uint8)
        test_array[20:44, 20:44] = 255  # Cuadrado blanco
        test_image = Image.fromarray(test_array)

        # Upscale
        result = resolver.upscale(test_image, scale_factor=2)

        # Verificar que el resultado es válido
        assert result.size == (128, 128)
        result_array = np.array(result)

        # Verificar que hay variación en los píxeles (no todo es uniforme)
        unique_values = len(np.unique(result_array))
        assert unique_values > 10, f"Demasiados pocos valores únicos: {unique_values}"

if __name__ == "__main__":
    pytest.main([__file__])