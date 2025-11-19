"""
Módulo de mejora facial para CPU
Implementa técnicas de mejora de rostros usando OpenCV y scikit-image.
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter
import logging
from typing import Optional, Tuple, List
import gc

logger = logging.getLogger(__name__)

class FaceEnhancerCPU:
    """
    Clase para mejora de rostros optimizada para CPU.
    Usa técnicas tradicionales de procesamiento de imágenes.
    """

    def __init__(self):
        self.face_cascade = None
        self._initialized = False

    def _initialize_detector(self):
        """Inicializa el detector de rostros de OpenCV"""
        if not self._initialized:
            try:
                # Usar clasificador Haar pre-entrenado
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                self._initialized = True
                logger.info("Detector de rostros inicializado")
            except Exception as e:
                logger.error(f"Error inicializando detector: {e}")
                raise

    def detect_faces(self, image: Image.Image) -> List[Tuple[int, int, int, int]]:
        """
        Detecta rostros en la imagen.

        Args:
            image: Imagen PIL

        Returns:
            Lista de tuplas (x, y, width, height) con posiciones de rostros
        """
        self._initialize_detector()

        # Convertir PIL a OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convertir a escala de grises para detección
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # Detectar rostros con parámetros más precisos
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.15,  # Menos sensible para menos falsos positivos
            minNeighbors=7,    # Más estricto para mejor precisión
            minSize=(60, 60),  # Tamaño mínimo mayor para rostros reales
            maxSize=(400, 400) # Tamaño máximo para rostros grandes
        )

        # Convertir a lista de tuplas
        face_regions = [(x, y, w, h) for (x, y, w, h) in faces]

        logger.info(f"Detectados {len(face_regions)} rostros con parámetros precisos")
        return face_regions

    def enhance_face_region(self, image: Image.Image, face_region: Tuple[int, int, int, int],
                          strength: float = 0.7) -> Image.Image:
        """
        Mejora una región facial específica.

        Args:
            image: Imagen PIL original
            face_region: Tupla (x, y, width, height)
            strength: Intensidad de la mejora (0.0-1.0)

        Returns:
            Imagen PIL con la región facial mejorada
        """
        x, y, w, h = face_region

        # Crear copia de la imagen
        enhanced_image = image.copy()

        # Extraer región facial
        face_crop = image.crop((x, y, x + w, y + h))

        # Aplicar mejoras locales
        enhanced_face = self._apply_local_enhancements(face_crop, strength)

        # Pegar de vuelta en la imagen original
        enhanced_image.paste(enhanced_face, (x, y))

        return enhanced_image

    def _apply_local_enhancements(self, face_image: Image.Image, strength: float) -> Image.Image:
        """
        Aplica mejoras locales avanzadas a una imagen de rostro.

        Args:
            face_image: Imagen PIL del rostro
            strength: Intensidad de mejora

        Returns:
            Imagen mejorada
        """
        # Convertir a array numpy
        img_array = np.array(face_image)

        # 1. Mejora de contraste adaptativo más agresiva (CLAHE)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(6, 6))  # Más agresivo
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        # 2. Reducción de ruido mejorada
        enhanced = cv2.bilateralFilter(enhanced, 11, 100, 100)  # Parámetros más agresivos

        # 3. Sharpening más fuerte
        kernel = np.array([[-1,-1,-1,-1,-1],
                           [-1, 2, 2, 2,-1],
                           [-1, 2, 8, 2,-1],
                           [-1, 2, 2, 2,-1],
                           [-1,-1,-1,-1,-1]]) * 0.05  # Kernel más fuerte
        enhanced = cv2.filter2D(enhanced, -1, kernel)

        # 4. Mejora de nitidez adicional con unsharp masking
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 1.0)
        enhanced = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)

        # 5. Ajuste de saturación y brillo más agresivos
        hsv = cv2.cvtColor(enhanced, cv2.COLOR_RGB2HSV)
        hsv = hsv.astype(np.float32)

        # Aumentar saturación significativamente
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + strength * 0.4), 0, 255)

        # Ajustar brillo más agresivamente
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + strength * 0.2), 0, 255)

        enhanced = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        # 6. Mejora final de contraste global
        enhanced = cv2.convertScaleAbs(enhanced, alpha=1.1, beta=5)  # Aumento de contraste

        # Convertir de vuelta a PIL
        result = Image.fromarray(enhanced)

        return result

    def enhance_faces(self, image: Image.Image, strength: float = 0.7) -> Image.Image:
        """
        Mejora todos los rostros detectados en la imagen.

        Args:
            image: Imagen PIL original
            strength: Intensidad de mejora (0.0-1.0)

        Returns:
            Imagen PIL con rostros mejorados
        """
        try:
            # Detectar rostros
            face_regions = self.detect_faces(image)

            if not face_regions:
                logger.info("No se detectaron rostros")
                return image

            # Aplicar mejora a cada rostro
            enhanced_image = image.copy()

            for face_region in face_regions:
                enhanced_image = self.enhance_face_region(enhanced_image, face_region, strength)

            # Liberar memoria
            gc.collect()

            logger.info(f"Mejorados {len(face_regions)} rostros")
            return enhanced_image

        except Exception as e:
            logger.error(f"Error en mejora facial: {e}")
            return image  # Retornar imagen original en caso de error

    def get_face_count(self, image: Image.Image) -> int:
        """
        Retorna el número de rostros detectados.

        Args:
            image: Imagen PIL

        Returns:
            Número de rostros
        """
        try:
            faces = self.detect_faces(image)
            return len(faces)
        except Exception as e:
            logger.error(f"Error contando rostros: {e}")
            return 0