"""
Módulo de Restauración Avanzada de Imágenes
Detecta y repara automáticamente daños en imágenes: grietas, manchas, quemaduras, etc.
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter
import logging
from typing import List, Tuple, Dict, Optional, Any
import gc

logger = logging.getLogger(__name__)

class AdvancedImageRestorer:
    """
    Clase para restauración avanzada de imágenes dañadas.
    Detecta y repara automáticamente grietas, manchas, quemaduras y otros daños.
    """

    def __init__(self):
        self.initialized = False

    def _ensure_initialized(self):
        """Asegura que todos los componentes estén inicializados"""
        if not self.initialized:
            self.initialized = True
            logger.info("Restaurador avanzado de imágenes inicializado")

    def detect_damage(self, image: Image.Image) -> Dict[str, Any]:
        """
        Detecta automáticamente diferentes tipos de daño en la imagen.

        Args:
            image: Imagen PIL a analizar

        Returns:
            Diccionario con información de daños detectados
        """
        try:
            self._ensure_initialized()

            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(img_array.shape) == 3 else img_array

            damage_info = {
                "cracks": self._detect_cracks(gray),
                "stains": self._detect_stains(img_array),
                "burns": self._detect_burns(img_array),
                "folds": self._detect_folds(gray),
                "scratches": self._detect_scratches(gray),
                "total_damage_regions": 0,
                "damage_mask": None
            }

            # Crear máscara combinada de daños
            combined_mask = np.zeros_like(gray, dtype=np.uint8)

            for damage_type, regions in damage_info.items():
                if damage_type != "total_damage_regions" and damage_type != "damage_mask" and regions:
                    for region in regions:
                        if len(region) == 4:  # bbox
                            x, y, w, h = region
                            combined_mask[y:y+h, x:x+w] = 255
                        damage_info["total_damage_regions"] += 1

            damage_info["damage_mask"] = Image.fromarray(combined_mask)

            logger.info(f"Detectados {damage_info['total_damage_regions']} regiones de daño")
            return damage_info

        except Exception as e:
            logger.error(f"Error en detección de daños: {e}")
            return {"total_damage_regions": 0, "damage_mask": None}

    def _detect_cracks(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta grietas y líneas finas en la imagen.
        """
        try:
            # Aplicar filtro de Sobel para detectar bordes
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges = cv2.magnitude(sobel_x, sobel_y)

            # Umbralizar para encontrar líneas finas - umbral más alto para menos falsos positivos
            _, thresh = cv2.threshold(edges.astype(np.uint8), 80, 255, cv2.THRESH_BINARY)

            # Operaciones morfológicas para conectar líneas
            kernel = np.ones((2, 2), np.uint8)  # Kernel más pequeño
            dilated = cv2.dilate(thresh, kernel, iterations=1)

            # Encontrar contornos
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            cracks = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 2000:  # Rango más restrictivo para grietas reales
                    x, y, w, h = cv2.boundingRect(contour)
                    if w > h * 4 or h > w * 4:  # Forma mucho más elongada
                        cracks.append((x, y, w, h))

            return cracks

        except Exception as e:
            logger.error(f"Error detectando grietas: {e}")
            return []

    def _detect_stains(self, img_array: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta manchas de humedad y decoloración.
        """
        try:
            # Convertir a espacio HSV para mejor detección de manchas
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)

            # Las manchas suelen tener saturación baja y brillo variable
            saturation = hsv[:, :, 1]
            brightness = hsv[:, :, 2]

            # Crear máscara de áreas sospechosas con umbral más conservador
            stain_mask = cv2.adaptiveThreshold(
                cv2.GaussianBlur(saturation, (5, 5), 0),
                255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 5  # Umbral más alto
            )

            # Filtrar por tamaño - reducir el rango para evitar falsos positivos
            contours, _ = cv2.findContours(stain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            stains = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 5000:  # Rango más restrictivo para manchas reales
                    x, y, w, h = cv2.boundingRect(contour)
                    stains.append((x, y, w, h))

            return stains

        except Exception as e:
            logger.error(f"Error detectando manchas: {e}")
            return []

    def _detect_burns(self, img_array: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta áreas quemadas o sobreexpuestas.
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

            # Las áreas quemadas son muy brillantes - umbral más conservador
            _, burn_mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)  # Umbral más alto

            # Operaciones morfológicas
            kernel = np.ones((3, 3), np.uint8)
            burn_mask = cv2.morphologyEx(burn_mask, cv2.MORPH_CLOSE, kernel)

            # Encontrar contornos
            contours, _ = cv2.findContours(burn_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            burns = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 2000:  # Rango más restrictivo para quemaduras reales
                    x, y, w, h = cv2.boundingRect(contour)
                    burns.append((x, y, w, h))

            return burns

        except Exception as e:
            logger.error(f"Error detectando quemaduras: {e}")
            return []

    def _detect_folds(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta dobleces y arrugas en el papel.
        """
        try:
            # Aplicar filtro de mediana para reducir ruido
            filtered = cv2.medianBlur(gray, 5)

            # Detectar líneas usando transformada de Hough - parámetros más restrictivos
            edges = cv2.Canny(filtered, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80,  # Umbral más alto
                                  minLineLength=50, maxLineGap=5)  # Líneas más largas, menos gap

            folds = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # Calcular bounding box de la línea
                    x = min(x1, x2)
                    y = min(y1, y2)
                    w = abs(x2 - x1)
                    h = abs(y2 - y1)
                    if w > 30 or h > 30:  # Líneas más significativas
                        folds.append((x, y, w, h))

            return folds

        except Exception as e:
            logger.error(f"Error detectando dobleces: {e}")
            return []

    def _detect_scratches(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta rayones y marcas superficiales.
        """
        try:
            # Aplicar filtro de diferencia de gaussianas
            blur1 = cv2.GaussianBlur(gray, (0, 0), 1)
            blur2 = cv2.GaussianBlur(gray, (0, 0), 3)
            dog = cv2.subtract(blur1, blur2)

            # Umbralizar - umbral más alto para menos falsos positivos
            _, scratch_mask = cv2.threshold(dog, 50, 255, cv2.THRESH_BINARY)

            # Operaciones morfológicas
            kernel = np.ones((2, 2), np.uint8)
            scratch_mask = cv2.morphologyEx(scratch_mask, cv2.MORPH_CLOSE, kernel)

            # Encontrar contornos
            contours, _ = cv2.findContours(scratch_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            scratches = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 50 < area < 500:  # Rango más restrictivo para rayones reales
                    x, y, w, h = cv2.boundingRect(contour)
                    if w > h * 3 or h > w * 3:  # Forma mucho más elongada
                        scratches.append((x, y, w, h))

            return scratches

        except Exception as e:
            logger.error(f"Error detectando rayones: {e}")
            return []

    def restore_image(self, image: Image.Image, damage_info: Optional[Dict[str, Any]] = None,
                     restoration_method: str = "content_aware") -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Restaura automáticamente la imagen detectando y reparando daños.

        Args:
            image: Imagen PIL a restaurar
            damage_info: Información de daños pre-calculada (opcional)
            restoration_method: Método de restauración ("content_aware", "telea", "ns")

        Returns:
            Tupla (imagen_restaurada, info_restauracion)
        """
        try:
            self._ensure_initialized()

            # Detectar daños si no se proporcionaron
            if damage_info is None:
                damage_info = self.detect_damage(image)

            restored_image = image.copy()
            restoration_info = {
                "original_damage_regions": damage_info.get("total_damage_regions", 0),
                "regions_restored": 0,
                "restoration_method": restoration_method,
                "damage_types_found": []
            }

            # Procesar cada tipo de daño
            damage_types = ["cracks", "stains", "burns", "folds", "scratches"]

            for damage_type in damage_types:
                if damage_type in damage_info and damage_info[damage_type]:
                    regions = damage_info[damage_type]
                    restoration_info["damage_types_found"].append(damage_type)

                    for region in regions:
                        try:
                            # Crear máscara para esta región específica
                            mask = self._create_region_mask(image.size, region)

                            # Aplicar restauración
                            if restoration_method == "content_aware":
                                restored_image = self._apply_content_aware_restoration(
                                    restored_image, mask, region
                                )
                            elif restoration_method == "telea":
                                restored_image = self._apply_telea_restoration(restored_image, mask)
                            elif restoration_method == "ns":
                                restored_image = self._apply_ns_restoration(restored_image, mask)

                            restoration_info["regions_restored"] += 1

                        except Exception as e:
                            logger.warning(f"Error restaurando región {region}: {e}")
                            continue

            logger.info(f"Restauración completada: {restoration_info['regions_restored']} regiones reparadas")
            return restored_image, restoration_info

        except Exception as e:
            logger.error(f"Error en restauración automática: {e}")
            return image, {"error": str(e)}

    def _create_region_mask(self, image_size: Tuple[int, int],
                           region: Tuple[int, int, int, int]) -> Image.Image:
        """Crea una máscara para una región específica"""
        width, height = image_size
        x, y, w, h = region

        mask_array = np.zeros((height, width), dtype=np.uint8)
        mask_array[y:y+h, x:x+w] = 255

        return Image.fromarray(mask_array)

    def _apply_content_aware_restoration(self, image: Image.Image, mask: Image.Image,
                                       region: Tuple[int, int, int, int]) -> Image.Image:
        """Aplica restauración consciente del contenido"""
        # Usar el método existente del inpainting processor
        from .inpainting import InpaintingProcessorCPU
        inpainter = InpaintingProcessorCPU()
        return inpainter.apply_content_aware_fill(image, mask)

    def _apply_telea_restoration(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """Aplica método de restauración Telea"""
        from .inpainting import InpaintingProcessorCPU
        inpainter = InpaintingProcessorCPU()
        return inpainter.apply_simple_inpainting(image, mask, "telea")

    def _apply_ns_restoration(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """Aplica método de restauración Navier-Stokes"""
        from .inpainting import InpaintingProcessorCPU
        inpainter = InpaintingProcessorCPU()
        return inpainter.apply_simple_inpainting(image, mask, "ns")

    def get_supported_restoration_methods(self) -> List[str]:
        """Retorna métodos de restauración soportados"""
        return ["content_aware", "telea", "ns"]