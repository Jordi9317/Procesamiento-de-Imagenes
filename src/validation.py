"""
Módulo de validación y manejo de errores
Proporciona funciones para validar entradas y manejar errores de forma robusta.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ImageValidator:
    """
    Clase para validar imágenes y parámetros de entrada.
    """

    # Límites de validación
    MAX_FILE_SIZE_MB = 10
    MAX_IMAGE_SIZE = 2048
    MIN_IMAGE_SIZE = 32
    SUPPORTED_FORMATS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

    @staticmethod
    def validate_image_file(file_path: str) -> Tuple[bool, str]:
        """
        Valida que un archivo de imagen sea correcto.

        Args:
            file_path: Ruta al archivo

        Returns:
            Tupla (es_valido, mensaje_error)
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return False, f"Archivo no encontrado: {file_path}"

            # Verificar tamaño del archivo
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > ImageValidator.MAX_FILE_SIZE_MB:
                return False, ".1f"

            # Verificar extensión
            file_ext = Path(file_path).suffix.lower().lstrip('.')
            if file_ext not in ImageValidator.SUPPORTED_FORMATS:
                return False, f"Formato no soportado: {file_ext}. Usar: {', '.join(ImageValidator.SUPPORTED_FORMATS)}"

            # Intentar abrir la imagen
            with Image.open(file_path) as img:
                img.verify()  # Verificar integridad

            return True, "Archivo válido"

        except Exception as e:
            return False, f"Error validando archivo: {str(e)}"

    @staticmethod
    def validate_image_object(image: Image.Image) -> Tuple[bool, List[str]]:
        """
        Valida un objeto PIL Image.

        Args:
            image: Imagen PIL

        Returns:
            Tupla (es_valido, lista_errores)
        """
        errors = []

        try:
            # Verificar que es un objeto Image
            if not isinstance(image, Image.Image):
                errors.append("El objeto no es una imagen PIL válida")
                return False, errors

            # Verificar dimensiones
            width, height = image.size

            if width < ImageValidator.MIN_IMAGE_SIZE or height < ImageValidator.MIN_IMAGE_SIZE:
                errors.append(f"Imagen demasiado pequeña: {width}x{height}. Mínimo: {ImageValidator.MIN_IMAGE_SIZE}x{ImageValidator.MIN_IMAGE_SIZE}")

            if width > ImageValidator.MAX_IMAGE_SIZE or height > ImageValidator.MAX_IMAGE_SIZE:
                errors.append(f"Imagen demasiado grande: {width}x{height}. Máximo: {ImageValidator.MAX_IMAGE_SIZE}x{ImageValidator.MAX_IMAGE_SIZE}")

            # Verificar modo de color
            if image.mode not in ['RGB', 'RGBA', 'L', 'P']:
                errors.append(f"Modo de color no soportado: {image.mode}. Usar RGB, RGBA, L o P")

            # Verificar que no esté corrupta
            if image.size[0] == 0 or image.size[1] == 0:
                errors.append("Imagen corrupta o vacía")

        except Exception as e:
            errors.append(f"Error procesando imagen: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_processing_options(options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida las opciones de procesamiento.

        Args:
            options: Diccionario con opciones

        Returns:
            Tupla (es_valido, lista_errores)
        """
        errors = []

        # Validar face_enhancement
        if 'face_enhancement' in options:
            if not isinstance(options['face_enhancement'], bool):
                errors.append("face_enhancement debe ser True o False")

        # Validar enhancement_strength
        if 'enhancement_strength' in options:
            strength = options['enhancement_strength']
            if not isinstance(strength, (int, float)):
                errors.append("enhancement_strength debe ser numérico")
            elif not 0.0 <= strength <= 1.0:
                errors.append("enhancement_strength debe estar entre 0.0 y 1.0")

        # Validar super_resolution
        if 'super_resolution' in options:
            if not isinstance(options['super_resolution'], bool):
                errors.append("super_resolution debe ser True o False")

        # Validar scale_factor
        if 'scale_factor' in options:
            scale = options['scale_factor']
            if scale not in [2, 3, 4]:
                errors.append("scale_factor debe ser 2, 3 o 4")

        # Validar interpolation_method
        if 'interpolation_method' in options:
            method = options['interpolation_method']
            if method not in ['lanczos', 'bicubic', 'bilinear']:
                errors.append("interpolation_method debe ser 'lanczos', 'bicubic' o 'bilinear'")

        return len(errors) == 0, errors

    @staticmethod
    def get_image_info(image: Image.Image) -> Dict[str, Any]:
        """
        Obtiene información detallada de una imagen.

        Args:
            image: Imagen PIL

        Returns:
            Diccionario con información de la imagen
        """
        try:
            info = {
                'size': image.size,
                'mode': image.mode,
                'format': image.format,
                'width': image.size[0],
                'height': image.size[1],
                'aspect_ratio': image.size[0] / image.size[1] if image.size[1] > 0 else 0,
                'megapixels': (image.size[0] * image.size[1]) / 1_000_000,
                'file_size_mb': 0,  # Se calcula si hay filepath
                'has_alpha': image.mode == 'RGBA',
                'is_grayscale': image.mode == 'L'
            }

            # Estimar tamaño de archivo (aproximado)
            bytes_per_pixel = 3 if image.mode == 'RGB' else 4 if image.mode == 'RGBA' else 1
            estimated_bytes = image.size[0] * image.size[1] * bytes_per_pixel
            info['estimated_file_size_mb'] = estimated_bytes / (1024 * 1024)

            return info

        except Exception as e:
            logger.error(f"Error obteniendo info de imagen: {e}")
            return {'error': str(e)}

class ErrorHandler:
    """
    Clase para manejar errores de forma centralizada.
    """

    @staticmethod
    def handle_processing_error(error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Maneja errores durante el procesamiento.

        Args:
            error: Excepción ocurrida
            context: Contexto donde ocurrió el error

        Returns:
            Diccionario con información del error
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': str(Path(__file__).stat().st_mtime),  # Timestamp del módulo
            'recoverable': True
        }

        # Clasificar errores
        if isinstance(error, MemoryError):
            error_info['error_category'] = 'memory'
            error_info['user_message'] = "Memoria insuficiente. Intente con una imagen más pequeña."
            error_info['recoverable'] = False
        elif isinstance(error, FileNotFoundError):
            error_info['error_category'] = 'file'
            error_info['user_message'] = "Archivo no encontrado. Verifique la ruta."
        elif isinstance(error, PermissionError):
            error_info['error_category'] = 'permission'
            error_info['user_message'] = "Sin permisos para acceder al archivo."
        elif isinstance(error, ValueError):
            error_info['error_category'] = 'validation'
            error_info['user_message'] = f"Valor inválido: {str(error)}"
        else:
            error_info['error_category'] = 'unknown'
            error_info['user_message'] = "Error inesperado. Contacte al soporte."

        logger.error(f"Error en {context}: {error_info['error_type']}: {error_info['error_message']}")

        return error_info

    @staticmethod
    def create_error_response(error_info: Dict[str, Any], fallback_data: Any = None) -> Dict[str, Any]:
        """
        Crea una respuesta de error estructurada.

        Args:
            error_info: Información del error
            fallback_data: Datos de respaldo si es posible

        Returns:
            Respuesta estructurada
        """
        response = {
            'success': False,
            'error': error_info,
            'data': fallback_data,
            'timestamp': error_info.get('timestamp', 'unknown')
        }

        return response

def safe_image_operation(operation_func, *args, **kwargs):
    """
    Decorador/wrapper para operaciones de imagen seguras.

    Args:
        operation_func: Función a ejecutar
        *args, **kwargs: Argumentos para la función

    Returns:
        Resultado de la función o error estructurado
    """
    try:
        result = operation_func(*args, **kwargs)
        return {
            'success': True,
            'data': result,
            'error': None
        }
    except Exception as e:
        error_info = ErrorHandler.handle_processing_error(e, operation_func.__name__)
        return ErrorHandler.create_error_response(error_info)