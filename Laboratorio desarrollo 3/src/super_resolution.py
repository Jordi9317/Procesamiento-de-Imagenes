"""
Módulo de super-resolución para CPU
Implementa técnicas de aumento de resolución usando algoritmos tradicionales.
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter
import logging
from typing import Optional, Tuple
import gc

logger = logging.getLogger(__name__)

class SuperResolverCPU:
    """
    Clase para super-resolución optimizada para CPU.
    Usa técnicas tradicionales de interpolación y mejora de calidad.
    """

    def __init__(self):
        self._initialized = False

    def _initialize(self):
        """Inicialización del módulo"""
        if not self._initialized:
            self._initialized = True
            logger.info("Super-resolver CPU inicializado")

    def upscale(self, image: Image.Image, scale_factor: int = 2,
                method: str = "lanczos", enhance_sharpness: bool = True,
                reduce_blur: bool = True) -> Image.Image:
        """
        Aumenta la resolución de la imagen con algoritmos avanzados de enfoque.

        Args:
            image: Imagen PIL original
            scale_factor: Factor de escala (2, 3, 4)
            method: Método de interpolación ('lanczos', 'bicubic', 'bilinear')
            enhance_sharpness: Aplicar mejora de nitidez avanzada
            reduce_blur: Aplicar reducción de desenfoque

        Returns:
            Imagen PIL con resolución aumentada y mejorada
        """
        self._initialize()

        try:
            # Validar parámetros
            if scale_factor not in [2, 3, 4]:
                raise ValueError("scale_factor debe ser 2, 3 o 4")

            # Convertir a array numpy
            img_array = np.array(image)

            # Paso 1: Pre-procesamiento para mejorar calidad antes del escalado
            if enhance_sharpness or reduce_blur:
                img_array = self._apply_preprocessing_enhancements(
                    img_array, enhance_sharpness, reduce_blur
                )

            # Aplicar interpolación
            if method == "lanczos":
                interpolation = cv2.INTER_LANCZOS4
            elif method == "bicubic":
                interpolation = cv2.INTER_CUBIC
            elif method == "bilinear":
                interpolation = cv2.INTER_LINEAR
            else:
                interpolation = cv2.INTER_LANCZOS4

            # Calcular nuevas dimensiones
            height, width = img_array.shape[:2]
            new_width = width * scale_factor
            new_height = height * scale_factor

            # Aplicar interpolación
            upscaled = cv2.resize(img_array, (new_width, new_height),
                                interpolation=interpolation)

            # Paso 2: Post-procesamiento avanzado
            if enhance_sharpness:
                upscaled = self._apply_advanced_sharpening(upscaled)

            # Aplicar mejoras de calidad tradicionales
            enhanced = self._apply_quality_enhancements(upscaled, scale_factor)

            # Convertir de vuelta a PIL
            result = Image.fromarray(enhanced)

            # Liberar memoria
            gc.collect()

            logger.info(f"Super-resolución avanzada aplicada: {width}x{height} -> {new_width}x{new_height}")
            return result

        except Exception as e:
            logger.error(f"Error en super-resolución avanzada: {e}")
            return image  # Retornar imagen original en caso de error

    def _apply_preprocessing_enhancements(self, img_array: np.ndarray,
                                        enhance_sharpness: bool,
                                        reduce_blur: bool) -> np.ndarray:
        """
        Aplica mejoras de pre-procesamiento antes del escalado.
        """
        enhanced = img_array.copy()

        if enhance_sharpness:
            # Unsharp masking suave antes del escalado
            enhanced = self._apply_unsharp_mask(enhanced, amount=0.3)

        if reduce_blur:
            # Reducción ligera de desenfoque
            enhanced = self._apply_light_blur_reduction(enhanced)

        # Mejorar contraste local
        enhanced = self._apply_local_contrast_enhancement(enhanced)

        return enhanced

    def _apply_advanced_sharpening(self, img_array: np.ndarray) -> np.ndarray:
        """
        Aplica técnicas avanzadas de sharpening después del escalado.
        """
        enhanced = img_array.copy()

        # 1. Unsharp masking más agresivo
        enhanced = self._apply_unsharp_mask(enhanced, amount=0.8, radius=1.5)

        # 2. Edge enhancement
        enhanced = self._apply_edge_enhancement(enhanced)

        # 3. Sharpening final
        enhanced = self._apply_sharpness_filter(enhanced)

        return enhanced

    def _apply_quality_enhancements(self, img_array: np.ndarray,
                                  scale_factor: int) -> np.ndarray:
        """
        Aplica mejoras de calidad tradicionales a la imagen upscaled.
        Optimizado para evitar oscurecimiento excesivo.

        Args:
            img_array: Array numpy de la imagen
            scale_factor: Factor de escala aplicado

        Returns:
            Array numpy mejorado
        """
        enhanced = img_array.copy().astype(np.float32)

        # 1. Reducción de ruido adaptativa suave
        if scale_factor >= 3:
            # Para escalas altas, denoising muy suave para no oscurecer
            enhanced = cv2.bilateralFilter(enhanced.astype(np.uint8), 5, 15, 15).astype(np.float32)
        else:
            # Para escala 2x, denoising mínimo
            enhanced = cv2.bilateralFilter(enhanced.astype(np.uint8), 3, 10, 10).astype(np.float32)

        # 2. Mejora de contraste local suave (CLAHE)
        if len(enhanced.shape) == 3:
            # Imagen RGB - CLAHE más conservador
            lab = cv2.cvtColor(enhanced.astype(np.uint8), cv2.COLOR_RGB2LAB)
            clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(12, 12))  # Más suave
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB).astype(np.float32)
        else:
            # Imagen en escala de grises
            clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(12, 12))
            enhanced = clahe.apply(enhanced.astype(np.uint8)).astype(np.float32)

        # 3. Ajuste de brillo y contraste sutil
        # Evitar oscurecimiento - boost de brillo conservador
        if len(enhanced.shape) == 3:
            # Calcular brillo promedio
            brightness = np.mean(enhanced)
            if brightness < 128:  # Solo si está oscuro
                # Boost de brillo suave
                enhanced = cv2.convertScaleAbs(enhanced, alpha=1.05, beta=5)
            else:
                # Mantenimiento de brillo
                enhanced = cv2.convertScaleAbs(enhanced, alpha=1.02, beta=0)

            # Ajuste de saturación mínimo
            hsv = cv2.cvtColor(enhanced.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.02, 0, 255)  # Boost mínimo
            enhanced = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

        return enhanced.astype(np.uint8)

    def _apply_unsharp_mask(self, img_array: np.ndarray, amount: float = 0.5,
                           radius: float = 1.0) -> np.ndarray:
        """Aplica unsharp masking para mejorar nitidez"""
        # Crear versión desenfocada
        blurred = cv2.GaussianBlur(img_array, (0, 0), sigmaX=radius)

        # Calcular máscara de enfoque
        unsharp_mask = cv2.addWeighted(img_array, 1 + amount, blurred, -amount, 0)

        return unsharp_mask

    def _apply_light_blur_reduction(self, img_array: np.ndarray) -> np.ndarray:
        """Aplica reducción ligera de desenfoque"""
        # Filtro de alto paso simple
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]], dtype=np.float32) * 0.1

        sharpened = cv2.filter2D(img_array.astype(np.float32), -1, kernel)

        return np.clip(sharpened, 0, 255).astype(np.uint8)

    def _apply_local_contrast_enhancement(self, img_array: np.ndarray) -> np.ndarray:
        """Mejora el contraste local usando CLAHE"""
        if len(img_array.shape) == 3:
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        else:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(img_array)

        return enhanced

    def _apply_edge_enhancement(self, img_array: np.ndarray) -> np.ndarray:
        """Mejora los bordes para mayor nitidez"""
        # Detectar bordes con Sobel
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(img_array.shape) == 3 else img_array

        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edges = cv2.magnitude(sobel_x, sobel_y)

        # Normalizar
        edges = cv2.normalize(edges, None, 0, 1, cv2.NORM_MINMAX)

        # Aplicar realce de bordes
        enhanced = img_array.astype(np.float32)
        for i in range(3 if len(img_array.shape) == 3 else 1):
            channel = enhanced[:, :, i] if len(img_array.shape) == 3 else enhanced
            channel += edges * 0.1  # Realce sutil
            channel = np.clip(channel, 0, 255)

        return enhanced.astype(np.uint8)

    def _apply_sharpness_filter(self, img_array: np.ndarray) -> np.ndarray:
        """Aplica un filtro de nitidez final"""
        # Kernel de sharpening
        kernel = np.array([[0, -0.5, 0],
                          [-0.5, 3, -0.5],
                          [0, -0.5, 0]], dtype=np.float32)

        # Aplicar por canal
        if len(img_array.shape) == 3:
            sharpened = img_array.copy().astype(np.float32)
            for i in range(3):
                sharpened[:, :, i] = cv2.filter2D(img_array[:, :, i].astype(np.float32), -1, kernel)
        else:
            sharpened = cv2.filter2D(img_array.astype(np.float32), -1, kernel)

        return np.clip(sharpened, 0, 255).astype(np.uint8)

    def batch_upscale(self, images: list, scale_factor: int = 2,
                     method: str = "lanczos") -> list:
        """
        Procesa múltiples imágenes en lote.

        Args:
            images: Lista de imágenes PIL
            scale_factor: Factor de escala
            method: Método de interpolación

        Returns:
            Lista de imágenes procesadas
        """
        results = []
        for img in images:
            try:
                result = self.upscale(img, scale_factor, method)
                results.append(result)
            except Exception as e:
                logger.error(f"Error procesando imagen: {e}")
                results.append(img)  # Mantener imagen original

            # Liberar memoria entre imágenes
            gc.collect()

        return results

    def get_supported_scale_factors(self) -> list:
        """Retorna los factores de escala soportados"""
        return [2, 3, 4]

    def get_supported_methods(self) -> list:
        """Retorna los métodos de interpolación soportados"""
        return ["lanczos", "bicubic", "bilinear"]

    def estimate_memory_usage(self, image: Image.Image, scale_factor: int) -> dict:
        """
        Estima el uso de memoria para una operación.

        Args:
            image: Imagen PIL
            scale_factor: Factor de escala

        Returns:
            Diccionario con estimaciones de memoria
        """
        width, height = image.size
        channels = len(image.getbands())

        original_pixels = width * height * channels
        upscaled_pixels = (width * scale_factor) * (height * scale_factor) * channels

        # Estimación en bytes (float32)
        original_memory = original_pixels * 4
        upscaled_memory = upscaled_pixels * 4
        processing_memory = upscaled_pixels * 8  # Buffers temporales

        return {
            "original_mb": original_memory / (1024 * 1024),
            "upscaled_mb": upscaled_memory / (1024 * 1024),
            "processing_mb": processing_memory / (1024 * 1024),
            "total_mb": (original_memory + upscaled_memory + processing_memory) / (1024 * 1024)
        }