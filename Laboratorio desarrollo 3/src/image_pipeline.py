"""
Pipeline completo de procesamiento de imágenes
Combina face enhancement y super-resolution en un flujo optimizado.
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image
import time
import gc

from .face_enhancement import FaceEnhancerCPU
from .super_resolution import SuperResolverCPU
from .inpainting import InpaintingProcessorCPU
from .image_to_image import ImageToImageTransformerCPU
from .image_restoration import AdvancedImageRestorer

logger = logging.getLogger(__name__)

class ImageRestorationPipeline:
    """
    Pipeline completo para restauración de imágenes.
    Combina detección facial, mejora y super-resolución.
    """

    def __init__(self):
        self.face_enhancer = FaceEnhancerCPU()
        self.super_resolver = SuperResolverCPU()
        self.inpainting_processor = InpaintingProcessorCPU()
        self.image_to_image_transformer = ImageToImageTransformerCPU()
        self.image_restorer = AdvancedImageRestorer()
        self._initialized = False

    def _initialize(self):
        """Inicialización lazy de componentes"""
        if not self._initialized:
            logger.info("Inicializando pipeline de restauración")
            self._initialized = True

    def process_image(self, image: Image.Image, options: Dict[str, Any]) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Procesa una imagen completa según las opciones especificadas.

        Args:
            image: Imagen PIL original
            options: Diccionario con opciones de procesamiento
                - face_enhancement: bool - Aplicar mejora facial
                - super_resolution: bool - Aplicar super-resolución
                - scale_factor: int - Factor de escala (2, 3, 4)
                - enhancement_strength: float - Intensidad de mejora facial (0.0-1.0)
                - interpolation_method: str - Método de interpolación
                - auto_restoration: bool - Aplicar restauración automática de daños
                - restoration_method: str - Método de restauración ("content_aware", "telea", "ns")

        Returns:
            Tupla (imagen_procesada, metadata)
        """
        self._initialize()

        metadata = {
            "original_size": image.size,
            "processing_time": 0,
            "steps_applied": [],
            "face_count": 0,
            "final_size": image.size,
            "errors": []
        }

        start_time = time.time()

        try:
            processed_image = image.copy()

            # Paso 0: Auto Restoration (primero para limpiar daños antes de otros procesos)
            if options.get("auto_restoration", False):
                logger.info("Aplicando restauración automática de daños")
                step_start = time.time()

                try:
                    restoration_method = options.get("restoration_method", "content_aware")
                    processed_image, restoration_info = self.image_restorer.restore_image(
                        processed_image,
                        restoration_method=restoration_method
                    )

                    metadata["steps_applied"].append("auto_restoration")
                    metadata["restoration_method"] = restoration_method
                    metadata["damage_regions_found"] = restoration_info.get("original_damage_regions", 0)
                    metadata["damage_regions_restored"] = restoration_info.get("regions_restored", 0)
                    metadata["damage_types_found"] = restoration_info.get("damage_types_found", [])

                    logger.info(f"Restauración automática completada en {time.time() - step_start:.2f}s")
                    logger.info(f"Regiones de daño restauradas: {metadata['damage_regions_restored']}")
                except Exception as e:
                    error_msg = f"Error en restauración automática: {str(e)}"
                    logger.error(error_msg)
                    metadata["errors"].append(error_msg)

            # Paso 1: Face Enhancement
            if options.get("face_enhancement", False):
                logger.info("Aplicando mejora facial")
                step_start = time.time()

                try:
                    processed_image = self.face_enhancer.enhance_faces(
                        processed_image,
                        strength=options.get("enhancement_strength", 0.7)
                    )
                    metadata["face_count"] = self.face_enhancer.get_face_count(image)
                    metadata["steps_applied"].append("face_enhancement")
                    logger.info(f"Mejora facial completada en {time.time() - step_start:.2f}s")
                except Exception as e:
                    error_msg = f"Error en mejora facial: {str(e)}"
                    logger.error(error_msg)
                    metadata["errors"].append(error_msg)

            # Paso 2: Inpainting (antes de super-resolution para mejor calidad)
            if options.get("inpainting", False):
                logger.info("Aplicando inpainting")
                step_start = time.time()

                try:
                    # Para demo, aplicamos inpainting a una región central
                    # En una implementación completa, esto vendría de una máscara del usuario
                    width, height = processed_image.size
                    bbox = (width//4, height//4, width//2, height//2)  # Región central

                    processed_image = self.inpainting_processor.remove_object(
                        processed_image,
                        bbox,
                        method=options.get("inpaint_method", "telea")
                    )

                    metadata["steps_applied"].append("inpainting")
                    metadata["inpaint_method"] = options.get("inpaint_method", "telea")
                    logger.info(f"Inpainting completado en {time.time() - step_start:.2f}s")
                except Exception as e:
                    error_msg = f"Error en inpainting: {str(e)}"
                    logger.error(error_msg)
                    metadata["errors"].append(error_msg)

            # Paso 3: Image-to-Image transformations
            if options.get("image_to_image", False):
                logger.info("Aplicando transformación image-to-image")
                step_start = time.time()

                try:
                    transform_type = options.get("transform_type", "Estilo de Color")
                    style_option = options.get("style_option", "warm")
                    intensity = options.get("transform_intensity", 0.7)

                    if transform_type == "Estilo de Color":
                        processed_image = self.image_to_image_transformer.apply_color_transformation(
                            processed_image, style_option, intensity
                        )
                    elif transform_type == "Estación":
                        processed_image = self.image_to_image_transformer.apply_seasonal_transformation(
                            processed_image, style_option, intensity
                        )
                    elif transform_type == "Hora del Día":
                        processed_image = self.image_to_image_transformer.apply_time_transformation(
                            processed_image, style_option, intensity
                        )

                    metadata["steps_applied"].append("image_to_image")
                    metadata["transform_type"] = transform_type
                    metadata["style_option"] = style_option
                    metadata["transform_intensity"] = intensity
                    logger.info(f"Transformación I2I completada en {time.time() - step_start:.2f}s")
                except Exception as e:
                    error_msg = f"Error en transformación I2I: {str(e)}"
                    logger.error(error_msg)
                    metadata["errors"].append(error_msg)

            # Paso 4: Super Resolution (al final para mejor calidad)
            if options.get("super_resolution", False):
                logger.info("Aplicando super-resolución")
                step_start = time.time()

                try:
                    scale_factor = options.get("scale_factor", 2)
                    method = options.get("interpolation_method", "lanczos")

                    processed_image = self.super_resolver.upscale(
                        processed_image,
                        scale_factor=scale_factor,
                        method=method
                    )

                    metadata["steps_applied"].append("super_resolution")
                    metadata["scale_factor"] = scale_factor
                    metadata["interpolation_method"] = method
                    logger.info(f"Super-resolución completada en {time.time() - step_start:.2f}s")
                except Exception as e:
                    error_msg = f"Error en super-resolución: {str(e)}"
                    logger.error(error_msg)
                    metadata["errors"].append(error_msg)

            # Actualizar metadata final
            metadata["final_size"] = processed_image.size
            metadata["processing_time"] = time.time() - start_time

            # Liberar memoria
            gc.collect()

            logger.info(f"Pipeline completado en {metadata['processing_time']:.2f}s")
            return processed_image, metadata

        except Exception as e:
            error_msg = f"Error crítico en pipeline: {str(e)}"
            logger.error(error_msg)
            metadata["errors"].append(error_msg)
            metadata["processing_time"] = time.time() - start_time

            # Retornar imagen original en caso de error crítico
            return image, metadata

    def get_available_options(self) -> Dict[str, Any]:
        """
        Retorna las opciones disponibles para el pipeline.

        Returns:
            Diccionario con opciones y sus valores permitidos
        """
        return {
            "auto_restoration": {
                "type": "boolean",
                "default": False,
                "description": "Aplicar restauración automática de daños en la imagen"
            },
            "restoration_method": {
                "type": "choice",
                "options": self.image_restorer.get_supported_restoration_methods(),
                "default": "content_aware",
                "description": "Método de restauración automática"
            },
            "face_enhancement": {
                "type": "boolean",
                "default": True,
                "description": "Aplicar mejora automática de rostros"
            },
            "enhancement_strength": {
                "type": "float",
                "range": [0.0, 1.0],
                "default": 0.7,
                "description": "Intensidad de mejora facial"
            },
            "super_resolution": {
                "type": "boolean",
                "default": True,
                "description": "Aplicar aumento de resolución"
            },
            "scale_factor": {
                "type": "choice",
                "options": self.super_resolver.get_supported_scale_factors(),
                "default": 2,
                "description": "Factor de escala para super-resolución"
            },
            "interpolation_method": {
                "type": "choice",
                "options": self.super_resolver.get_supported_methods(),
                "default": "lanczos",
                "description": "Método de interpolación"
            }
        }

    def estimate_processing_time(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, float]:
        """
        Estima el tiempo de procesamiento para una imagen.

        Args:
            image: Imagen PIL
            options: Opciones de procesamiento

        Returns:
            Diccionario con estimaciones de tiempo
        """
        width, height = image.size

        # Estimaciones base (pueden calibrarse con benchmarks reales)
        base_face_time = 2.0  # segundos por rostro detectado
        base_sr_time_per_megapixel = 1.0  # segundos por megapíxel upscaled

        estimated_time = 0.0

        # Estimar tiempo de face enhancement
        if options.get("face_enhancement", False):
            face_count = max(1, self.face_enhancer.get_face_count(image))
            estimated_time += base_face_time * face_count

        # Estimar tiempo de super-resolution
        if options.get("super_resolution", False):
            scale_factor = options.get("scale_factor", 2)
            upscaled_pixels = (width * scale_factor) * (height * scale_factor)
            megapixels = upscaled_pixels / 1_000_000
            estimated_time += base_sr_time_per_megapixel * megapixels

        return {
            "estimated_seconds": estimated_time,
            "estimated_minutes": estimated_time / 60,
            "face_detection_time": base_face_time if options.get("face_enhancement", False) else 0,
            "super_resolution_time": estimated_time - (base_face_time if options.get("face_enhancement", False) else 0)
        }

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida que las opciones proporcionadas sean correctas.

        Args:
            options: Opciones a validar

        Returns:
            Tupla (es_valido, lista_de_errores)
        """
        available_options = self.get_available_options()
        errors = []

        for key, value in options.items():
            if key not in available_options:
                errors.append(f"Opción desconocida: {key}")
                continue

            option_config = available_options[key]

            # Validar tipo
            if option_config["type"] == "boolean":
                if not isinstance(value, bool):
                    errors.append(f"{key} debe ser boolean, recibido {type(value)}")
            elif option_config["type"] == "float":
                if not isinstance(value, (int, float)):
                    errors.append(f"{key} debe ser numérico")
                elif not (option_config["range"][0] <= value <= option_config["range"][1]):
                    errors.append(f"{key} debe estar entre {option_config['range']}")
            elif option_config["type"] == "choice":
                if value not in option_config["options"]:
                    errors.append(f"{key} debe ser uno de: {option_config['options']}")

        return len(errors) == 0, errors