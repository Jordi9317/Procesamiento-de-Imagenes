"""
Módulo de Inpainting para CPU
Implementa eliminación de objetos usando modelos de difusión.
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, Tuple, List
import gc

logger = logging.getLogger(__name__)

class InpaintingProcessorCPU:
    """
    Clase para inpainting optimizado para CPU.
    Usa técnicas tradicionales de procesamiento de imágenes.
    """

    def __init__(self):
        self.initialized = False

    def _ensure_initialized(self):
        """Asegura que todos los componentes estén inicializados"""
        if not self.initialized:
            self.initialized = True
            logger.info("Procesador de inpainting inicializado")

    def create_mask_from_bbox(self, image_size: Tuple[int, int],
                            bbox: Tuple[int, int, int, int]) -> Image.Image:
        """
        Crea una máscara rectangular a partir de coordenadas de bounding box.

        Args:
            image_size: Tupla (width, height) del tamaño de la imagen
            bbox: Tupla (x, y, width, height) del bounding box

        Returns:
            Máscara PIL en blanco y negro
        """
        width, height = image_size
        x, y, w, h = bbox

        # Crear máscara negra
        mask_array = np.zeros((height, width), dtype=np.uint8)

        # Dibujar rectángulo blanco
        mask_array[y:y+h, x:x+w] = 255

        return Image.fromarray(mask_array)

    def apply_simple_inpainting(self, image: Image.Image, mask: Image.Image,
                               method: str = "telea") -> Image.Image:
        """
        Aplica inpainting simple usando algoritmos tradicionales de OpenCV.

        Args:
            image: Imagen PIL original
            mask: Máscara PIL (blanco = área a rellenar)
            method: Método de inpainting ("telea" o "ns")

        Returns:
            Imagen PIL con inpainting aplicado
        """
        try:
            # Convertir a formato OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv_mask = np.array(mask).astype(np.uint8)

            # Aplicar inpainting
            if method == "telea":
                inpainted = cv2.inpaint(cv_image, cv_mask, 3, cv2.INPAINT_TELEA)
            elif method == "ns":
                inpainted = cv2.inpaint(cv_image, cv_mask, 3, cv2.INPAINT_NS)
            else:
                raise ValueError(f"Método desconocido: {method}")

            # Convertir de vuelta a PIL
            result = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))

            return result

        except Exception as e:
            logger.error(f"Error en inpainting simple: {e}")
            return image

    def apply_content_aware_fill(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """
        Aplica un relleno consciente del contenido usando técnicas de clonación.

        Args:
            image: Imagen PIL original
            mask: Máscara PIL del área a rellenar

        Returns:
            Imagen PIL con relleno aplicado
        """
        try:
            # Convertir a formato OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv_mask = np.array(mask).astype(np.uint8)

            # Encontrar contorno de la máscara
            contours, _ = cv2.findContours(cv_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                logger.warning("No se encontraron contornos en la máscara")
                return image

            # Usar el contorno más grande
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)

            # Crear región fuente (alrededor del área a rellenar)
            source_region = cv_image[max(0, y-10):min(cv_image.shape[0], y+h+10),
                                   max(0, x-10):min(cv_image.shape[1], x+w+10)]

            if source_region.size == 0:
                logger.warning("Región fuente vacía")
                return image

            # Aplicar desenfoque gaussiano para suavizar
            blurred = cv2.GaussianBlur(source_region, (5, 5), 0)

            # Crear máscara para la región a rellenar
            region_mask = cv_mask[y:y+h, x:x+w]

            # Asegurar que las dimensiones coincidan
            if blurred.shape[:2] != (h, w):
                blurred = cv2.resize(blurred, (w, h))

            # Mezclar con desenfoque - menos agresivo para evitar oscurecimiento
            result = cv_image.copy()
            result[y:y+h, x:x+w] = cv2.addWeighted(
                cv_image[y:y+h, x:x+w], 0.8,  # Más peso a la imagen original
                blurred, 0.2, 0  # Menos peso al desenfoque
            )

            # Convertir de vuelta a PIL
            result_pil = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

            return result_pil

        except Exception as e:
            logger.error(f"Error en content-aware fill: {e}")
            return image

    def remove_object(self, image: Image.Image, bbox: Tuple[int, int, int, int],
                     method: str = "telea") -> Image.Image:
        """
        Elimina un objeto de la imagen usando las coordenadas del bounding box.

        Args:
            image: Imagen PIL original
            bbox: Tupla (x, y, width, height) del objeto a eliminar
            method: Método de inpainting ("telea", "ns", "content_aware")

        Returns:
            Imagen PIL sin el objeto
        """
        try:
            self._ensure_initialized()

            # Crear máscara desde bounding box
            mask = self.create_mask_from_bbox(image.size, bbox)

            # Aplicar método seleccionado
            if method == "content_aware":
                result = self.apply_content_aware_fill(image, mask)
            else:
                result = self.apply_simple_inpainting(image, mask, method)

            # Liberar memoria
            gc.collect()

            logger.info(f"Objeto eliminado usando método: {method}")
            return result

        except Exception as e:
            logger.error(f"Error eliminando objeto: {e}")
            return image

    def batch_remove_objects(self, image: Image.Image,
                           bboxes: List[Tuple[int, int, int, int]],
                           method: str = "telea") -> Image.Image:
        """
        Elimina múltiples objetos de la imagen.

        Args:
            image: Imagen PIL original
            bboxes: Lista de bounding boxes (x, y, width, height)
            method: Método de inpainting

        Returns:
            Imagen PIL sin los objetos
        """
        try:
            result = image.copy()

            for i, bbox in enumerate(bboxes):
                logger.info(f"Eliminando objeto {i+1}/{len(bboxes)}")
                result = self.remove_object(result, bbox, method)

            return result

        except Exception as e:
            logger.error(f"Error en eliminación por lotes: {e}")
            return image

    def get_supported_methods(self) -> List[str]:
        """
        Retorna la lista de métodos de inpainting soportados.

        Returns:
            Lista de nombres de métodos
        """
        return ["telea", "ns", "content_aware"]