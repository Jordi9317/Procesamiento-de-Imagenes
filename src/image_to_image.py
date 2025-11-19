"""
Módulo de Image-to-Image para CPU
Implementa transformaciones de imágenes usando técnicas tradicionales.
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import logging
from typing import Optional, Tuple, List, Dict, Any
import gc

logger = logging.getLogger(__name__)

class ImageToImageTransformerCPU:
    """
    Clase para transformaciones image-to-image optimizadas para CPU.
    Usa técnicas tradicionales de procesamiento de imágenes.
    """

    def __init__(self):
        self.initialized = False

    def _ensure_initialized(self):
        """Asegura que todos los componentes estén inicializados"""
        if not self.initialized:
            self.initialized = True
            logger.info("Transformador image-to-image inicializado")

    def apply_color_transformation(self, image: Image.Image,
                                 target_style: str,
                                 intensity: float = 0.7) -> Image.Image:
        """
        Aplica transformaciones de color basadas en estilos predefinidos.

        Args:
            image: Imagen PIL original
            target_style: Estilo objetivo ("warm", "cool", "vintage", "dramatic", etc.)
            intensity: Intensidad de la transformación (0.0-1.0)

        Returns:
            Imagen PIL transformada
        """
        try:
            # Convertir a array numpy para procesamiento
            img_array = np.array(image)

            if target_style == "warm":
                # Aumentar rojos y amarillos, reducir azules
                img_array = self._adjust_color_temperature(img_array, warmth=1 + intensity * 0.5)

            elif target_style == "cool":
                # Aumentar azules, reducir rojos y amarillos
                img_array = self._adjust_color_temperature(img_array, warmth=1 - intensity * 0.5)

            elif target_style == "vintage":
                # Efecto sepia + reducción de saturación
                img_array = self._apply_sepia_filter(img_array, intensity)
                img_array = self._adjust_saturation(img_array, 1 - intensity * 0.3)

            elif target_style == "dramatic":
                # Alto contraste + sombras profundas
                img_array = self._adjust_contrast(img_array, 1 + intensity * 0.8)
                img_array = self._adjust_brightness(img_array, 1 - intensity * 0.2)

            elif target_style == "vibrant":
                # Aumentar saturación y contraste
                img_array = self._adjust_saturation(img_array, 1 + intensity * 0.6)
                img_array = self._adjust_contrast(img_array, 1 + intensity * 0.4)

            elif target_style == "muted":
                # Reducir saturación y contraste
                img_array = self._adjust_saturation(img_array, 1 - intensity * 0.7)
                img_array = self._adjust_contrast(img_array, 1 - intensity * 0.3)

            elif target_style == "high_contrast":
                # Máximo contraste para efecto B&W dramático
                img_array = self._apply_high_contrast(img_array, intensity)

            elif target_style == "soft":
                # Desenfoque suave + reducción de contraste
                img_array = cv2.GaussianBlur(img_array, (0, 0), sigmaX=intensity * 3)
                img_array = self._adjust_contrast(img_array, 1 - intensity * 0.4)

            else:
                logger.warning(f"Estilo desconocido: {target_style}")
                return image

            # Asegurar valores válidos
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)

            # Convertir de vuelta a PIL
            result = Image.fromarray(img_array)

            return result

        except Exception as e:
            logger.error(f"Error en transformación de color: {e}")
            return image

    def _adjust_color_temperature(self, img_array: np.ndarray, warmth: float) -> np.ndarray:
        """Ajusta la temperatura de color"""
        # Separar canales RGB
        r, g, b = cv2.split(img_array.astype(np.float32))

        # Ajustar basado en warmth
        if warmth > 1:
            # Más cálido: aumentar rojo y verde, reducir azul
            r = r * warmth
            g = g * (warmth * 0.8)
            b = b / warmth
        else:
            # Más frío: aumentar azul, reducir rojo
            r = r * warmth
            b = b / warmth

        # Recombinar y normalizar
        result = cv2.merge([r, g, b])
        result = np.clip(result, 0, 255)

        return result.astype(np.uint8)

    def _apply_sepia_filter(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Aplica filtro sepia"""
        # Matriz de transformación sepia
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])

        # Aplicar transformación
        sepia_img = cv2.transform(img_array.astype(np.float32), sepia_matrix)

        # Mezclar con original basado en intensidad
        result = cv2.addWeighted(img_array, 1 - intensity, sepia_img, intensity, 0)

        return np.clip(result, 0, 255).astype(np.uint8)

    def _adjust_saturation(self, img_array: np.ndarray, saturation_factor: float) -> np.ndarray:
        """Ajusta la saturación de la imagen"""
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV).astype(np.float32)

        # Ajustar componente de saturación
        hsv[:, :, 1] = hsv[:, :, 1] * saturation_factor
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)

        # Convertir de vuelta
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        return result

    def _adjust_contrast(self, img_array: np.ndarray, contrast_factor: float) -> np.ndarray:
        """Ajusta el contraste de la imagen"""
        # Calcular el punto medio
        mean = np.mean(img_array)

        # Aplicar ajuste de contraste
        result = (img_array - mean) * contrast_factor + mean

        return np.clip(result, 0, 255).astype(np.uint8)

    def _adjust_brightness(self, img_array: np.ndarray, brightness_factor: float) -> np.ndarray:
        """Ajusta el brillo de la imagen"""
        if brightness_factor > 1:
            result = img_array * brightness_factor
        else:
            result = img_array * brightness_factor

        return np.clip(result, 0, 255).astype(np.uint8)

    def _apply_high_contrast(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Aplica efecto de alto contraste"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Aplicar threshold adaptativo
        threshold_value = int(128 * (1 + intensity))
        _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

        # Convertir de vuelta a RGB
        result = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)

        return result

    def apply_seasonal_transformation(self, image: Image.Image,
                                    season: str,
                                    intensity: float = 0.7) -> Image.Image:
        """
        Aplica transformaciones estacionales a la imagen.

        Args:
            image: Imagen PIL original
            season: Estación ("spring", "summer", "autumn", "winter")
            intensity: Intensidad de la transformación

        Returns:
            Imagen PIL transformada
        """
        try:
            img_array = np.array(image)

            if season == "spring":
                # Colores vibrantes, tonos pastel
                img_array = self._adjust_saturation(img_array, 1 + intensity * 0.4)
                img_array = self._adjust_color_temperature(img_array, 1.1)

            elif season == "summer":
                # Colores cálidos, brillantes
                img_array = self._adjust_saturation(img_array, 1 + intensity * 0.6)
                img_array = self._adjust_brightness(img_array, 1 + intensity * 0.2)
                img_array = self._adjust_color_temperature(img_array, 1.2)

            elif season == "autumn":
                # Tonos naranjas y rojizos
                img_array = self._apply_autumn_tones(img_array, intensity)

            elif season == "winter":
                # Tonos fríos, azules
                img_array = self._adjust_color_temperature(img_array, 0.8)
                img_array = self._adjust_saturation(img_array, 1 - intensity * 0.3)
                img_array = self._adjust_contrast(img_array, 1 + intensity * 0.2)

            else:
                logger.warning(f"Estación desconocida: {season}")
                return image

            result = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

            return result

        except Exception as e:
            logger.error(f"Error en transformación estacional: {e}")
            return image

    def _apply_autumn_tones(self, img_array: np.ndarray, intensity: float) -> np.ndarray:
        """Aplica tonos otoñales (naranjas y rojizos)"""
        # Aumentar rojos y reducir azules
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV).astype(np.float32)

        # Ajustar matiz hacia tonos rojizos
        hsv[:, :, 0] = (hsv[:, :, 0] + intensity * 15) % 180  # Desplazamiento en matiz

        # Aumentar saturación
        hsv[:, :, 1] = hsv[:, :, 1] * (1 + intensity * 0.3)

        # Convertir de vuelta
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        return result

    def apply_time_transformation(self, image: Image.Image,
                                time_of_day: str,
                                intensity: float = 0.7) -> Image.Image:
        """
        Aplica transformaciones de hora del día.

        Args:
            image: Imagen PIL original
            time_of_day: Hora del día ("dawn", "morning", "noon", "sunset", "night")
            intensity: Intensidad de la transformación

        Returns:
            Imagen PIL transformada
        """
        try:
            img_array = np.array(image)

            if time_of_day == "dawn":
                # Tonos suaves, azules y rosados
                img_array = self._adjust_color_temperature(img_array, 0.9)
                img_array = self._adjust_saturation(img_array, 1 - intensity * 0.2)
                img_array = self._adjust_brightness(img_array, 0.9)

            elif time_of_day == "morning":
                # Luz natural, colores frescos
                img_array = self._adjust_color_temperature(img_array, 1.0)
                img_array = self._adjust_saturation(img_array, 1 + intensity * 0.2)
                img_array = self._adjust_contrast(img_array, 1 + intensity * 0.1)

            elif time_of_day == "noon":
                # Luz brillante, alto contraste
                img_array = self._adjust_brightness(img_array, 1 + intensity * 0.1)
                img_array = self._adjust_contrast(img_array, 1 + intensity * 0.3)

            elif time_of_day == "sunset":
                # Tonos cálidos, naranjas
                img_array = self._adjust_color_temperature(img_array, 1.3)
                img_array = self._adjust_saturation(img_array, 1 + intensity * 0.4)
                img_array = self._adjust_contrast(img_array, 1 + intensity * 0.2)

            elif time_of_day == "night":
                # Tonos fríos, azules, bajo brillo
                img_array = self._adjust_color_temperature(img_array, 0.7)
                img_array = self._adjust_brightness(img_array, 1 - intensity * 0.4)
                img_array = self._adjust_contrast(img_array, 1 + intensity * 0.2)

            else:
                logger.warning(f"Hora del día desconocida: {time_of_day}")
                return image

            result = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

            return result

        except Exception as e:
            logger.error(f"Error en transformación temporal: {e}")
            return image

    def get_supported_styles(self) -> List[str]:
        """Retorna estilos de color soportados"""
        return ["warm", "cool", "vintage", "dramatic", "vibrant", "muted", "high_contrast", "soft"]

    def get_supported_seasons(self) -> List[str]:
        """Retorna estaciones soportadas"""
        return ["spring", "summer", "autumn", "winter"]

    def get_supported_times(self) -> List[str]:
        """Retorna horas del día soportadas"""
        return ["dawn", "morning", "noon", "sunset", "night"]