#!/usr/bin/env python3
"""
Image Restoration App - CPU Optimized
Aplicación web Streamlit para restaurar y mejorar imágenes usando IA.
"""

import streamlit as st
import logging
from pathlib import Path
from PIL import Image
import time
import os
from datetime import datetime
import io
import base64

# Importar módulos locales
from Laboratorio_desarrollo_3.src.image_pipeline import ImageRestorationPipeline
from Laboratorio_desarrollo_3.src.validation import ImageValidator, ErrorHandler, safe_image_operation

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la página
st.set_page_config(
    page_title="🖼️ Image Restoration App",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        # Image Restoration App

        Aplicación para restaurar y mejorar imágenes usando técnicas de IA optimizadas para CPU.

        **Características:**
        - Mejora automática de rostros
        - Super-resolución 2x-4x
        - Procesamiento local y privado
        - Optimizado para CPU

        **Versión:** 1.0.0
        """
    }
)

# Inicializar pipeline en session state
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = ImageRestorationPipeline()

if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []

def get_image_download_link(img, filename, text):
    """Genera un link de descarga para una imagen"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

def show_image_type_guide():
    """Muestra guía interactiva según tipo de imagen"""
    st.header("🎯 Asistente Inteligente - ¿Qué tipo de imagen tienes?")

    # Selector de tipo de imagen
    image_types = {
        "📸 Foto con rostros": {
            "description": "Retrato, selfie, foto grupal con personas",
            "recommended": ["face_enhancement", "super_resolution"],
            "config": {
                "face_enhancement": True,
                "enhancement_strength": 0.7,
                "super_resolution": True,
                "scale_factor": 3,
                "interpolation_method": "lanczos",
                "enhance_sharpness": True,
                "reduce_blur": False
            }
        },
        "🔍 Imagen pixelada/pequeña": {
            "description": "Foto de baja resolución, captura pixelada",
            "recommended": ["super_resolution"],
            "config": {
                "face_enhancement": False,
                "super_resolution": True,
                "scale_factor": 4,
                "interpolation_method": "lanczos",
                "enhance_sharpness": True,
                "reduce_blur": False
            }
        },
        "🌫️ Foto borrosa/desenfocada": {
            "description": "Imagen con desenfoque, movimiento, fuera de foco",
            "recommended": ["super_resolution"],
            "config": {
                "face_enhancement": True,
                "enhancement_strength": 0.8,
                "super_resolution": True,
                "scale_factor": 2,
                "interpolation_method": "bicubic",
                "enhance_sharpness": True,
                "reduce_blur": True
            }
        },
        "🚫 Objetos no deseados": {
            "description": "Foto con personas/cosas que quieres eliminar",
            "recommended": ["inpainting"],
            "config": {
                "face_enhancement": False,
                "super_resolution": False,
                "inpainting": True,
                "inpaint_method": "telea"
            }
        },
        "🎨 Cambiar estilo/atmósfera": {
            "description": "Modificar colores, estación, hora del día",
            "recommended": ["image_to_image"],
            "config": {
                "face_enhancement": False,
                "super_resolution": False,
                "inpainting": False,
                "image_to_image": True,
                "transform_type": "Estilo de Color",
                "style_option": "vibrant",
                "transform_intensity": 0.7
            }
        },
        "📜 Foto antigua/dañada": {
            "description": "Imagen vintage con imperfecciones, manchas",
            "recommended": ["auto_restoration", "face_enhancement", "super_resolution"],
            "config": {
                "auto_restoration": True,
                "restoration_method": "content_aware",
                "face_enhancement": True,
                "enhancement_strength": 0.6,
                "super_resolution": True,
                "scale_factor": 2,
                "interpolation_method": "lanczos",
                "enhance_sharpness": True,
                "reduce_blur": True
            }
        }
    }

    selected_type = st.selectbox(
        "Selecciona el tipo de imagen que tienes:",
        options=list(image_types.keys()),
        help="Elige la opción que mejor describe tu imagen"
    )

    # Mostrar descripción y recomendaciones
    type_info = image_types[selected_type]

    st.info(f"**{selected_type}**: {type_info['description']}")

    st.subheader("✅ Herramientas Recomendadas")
    recommended_tools = type_info['recommended']
    for tool in recommended_tools:
        if tool == "auto_restoration":
            st.success("🔧 **Restauración Automática**: Detecta y repara daños automáticamente")
        elif tool == "face_enhancement":
            st.success("🧑 **Face Enhancement**: Mejora automáticamente rostros")
        elif tool == "super_resolution":
            st.success("🔍 **Super-Resolution**: Aumenta resolución y nitidez")
        elif tool == "inpainting":
            st.success("🖌️ **Inpainting**: Elimina objetos no deseados")
        elif tool == "image_to_image":
            st.success("🎨 **Image-to-Image**: Transforma estilo y atmósfera")

    # Botón para aplicar configuración recomendada
    if st.button("🚀 Aplicar Configuración Recomendada", type="primary"):
        # Guardar configuración en session state
        st.session_state.recommended_config = type_info['config']
        st.success("✅ Configuración aplicada al sidebar. Ahora sube tu imagen y procesa.")

        # Mostrar configuración aplicada
        with st.expander("⚙️ Configuración Aplicada"):
            config = type_info['config']
            if config.get('auto_restoration'):
                st.write(f"• Restauración Automática: ON (método: {config.get('restoration_method', 'content_aware')})")
            if config.get('face_enhancement'):
                st.write(f"• Face Enhancement: ON (intensidad: {config.get('enhancement_strength', 0.7)})")
            if config.get('super_resolution'):
                st.write(f"• Super-Resolution: ON ({config.get('scale_factor', 2)}x, {config.get('interpolation_method', 'lanczos')})")
                if config.get('enhance_sharpness'):
                    st.write("• Nitidez Avanzada: ON")
                if config.get('reduce_blur'):
                    st.write("• Reducción de Desenfoque: ON")
            if config.get('inpainting'):
                st.write(f"• Inpainting: ON (método: {config.get('inpaint_method', 'telea')})")
            if config.get('image_to_image'):
                st.write(f"• Image-to-Image: ON ({config.get('transform_type', 'Estilo de Color')}: {config.get('style_option', 'warm')})")

    return image_types

def main():
    """Función principal de la aplicación"""

    # Título principal
    st.title("🖼️ Image Restoration App")
    st.markdown("*Restaurá y mejorá tus imágenes con IA - Optimizado para CPU*")

    # Tabs para navegación
    tab1, tab2 = st.tabs(["🎯 Asistente Inteligente", "⚙️ Configuración Manual"])

    with tab1:
        # Asistente inteligente
        image_types = show_image_type_guide()

    with tab2:
        st.header("⚙️ Configuración Manual Avanzada")
        st.markdown("Para usuarios avanzados que quieren control total")

    # Sidebar con configuración
    with st.sidebar:
        st.header("⚙️ Configuración")

        # Cargar configuración recomendada si existe
        if 'recommended_config' in st.session_state:
            st.info("🎯 Configuración recomendada aplicada automáticamente")
            config = st.session_state.recommended_config

            # Aplicar configuración recomendada
            auto_restoration = config.get('auto_restoration', False)
            restoration_method = config.get('restoration_method', 'content_aware')
            face_enhancement = config.get('face_enhancement', True)
            enhancement_strength = config.get('enhancement_strength', 0.7)
            super_resolution = config.get('super_resolution', True)
            scale_factor = config.get('scale_factor', 2)
            interpolation_method = config.get('interpolation_method', 'lanczos')
            enhance_sharpness = config.get('enhance_sharpness', True)
            reduce_blur = config.get('reduce_blur', False)
            enable_inpainting = config.get('inpainting', False)
            inpaint_method = config.get('inpaint_method', 'telea')
            enable_image_to_image = config.get('image_to_image', False)
            transform_type = config.get('transform_type', 'Estilo de Color')
            style_option = config.get('style_option', 'warm')
            transform_intensity = config.get('transform_intensity', 0.7)

            st.success("✅ Configuración inteligente aplicada")
        else:
            # Configuración manual por defecto
            auto_restoration = False
            restoration_method = "content_aware"
            face_enhancement = True
            enhancement_strength = 0.7
            super_resolution = True
            scale_factor = 2
            interpolation_method = "lanczos"
            enhance_sharpness = True
            reduce_blur = False
            enable_inpainting = False
            inpaint_method = "telea"
            enable_image_to_image = False
            transform_type = "Estilo de Color"
            style_option = "warm"
            transform_intensity = 0.7

        # Opciones de procesamiento
        st.subheader("Opciones de Procesamiento")

        # Nueva opción: Auto Restoration
        auto_restoration = st.checkbox(
            "🔧 Restauración Automática",
            value=auto_restoration,
            help="Detecta y repara automáticamente daños en la imagen (grietas, manchas, quemaduras)"
        )

        if auto_restoration:
            restoration_method = st.selectbox(
                "Método de Restauración",
                options=["content_aware", "telea", "ns"],
                index=["content_aware", "telea", "ns"].index(restoration_method) if restoration_method in ["content_aware", "telea", "ns"] else 0,
                help="Algoritmo para restaurar daños detectados automáticamente"
            )

        face_enhancement = st.checkbox(
            "Mejora Facial",
            value=face_enhancement,
            help="Detecta y mejora automáticamente los rostros en la imagen"
        )

        enhancement_strength = st.slider(
            "Intensidad Facial",
            min_value=0.0,
            max_value=1.0,
            value=enhancement_strength,
            step=0.1,
            help="Controla la intensidad de la mejora facial",
            disabled=not face_enhancement
        )

        super_resolution = st.checkbox(
            "Super-Resolución",
            value=super_resolution,
            help="Aumenta la resolución de la imagen"
        )

        scale_factor = st.selectbox(
            "Factor de Escala",
            options=[2, 3, 4],
            index=[2, 3, 4].index(scale_factor) if scale_factor in [2, 3, 4] else 0,
            help="Cuánto aumentar la resolución",
            disabled=not super_resolution
        )

        interpolation_method = st.selectbox(
            "Método de Interpolación",
            options=["lanczos", "bicubic", "bilinear"],
            index=["lanczos", "bicubic", "bilinear"].index(interpolation_method) if interpolation_method in ["lanczos", "bicubic", "bilinear"] else 0,
            help="Algoritmo de interpolación para super-resolución",
            disabled=not super_resolution
        )

        # Opciones avanzadas de super-resolution
        if super_resolution:
            st.subheader("Opciones Avanzadas")
            enhance_sharpness = st.checkbox(
                "Mejora de Nitidez Avanzada",
                value=enhance_sharpness,
                help="Aplica algoritmos avanzados de enfoque (unsharp masking, edge enhancement)"
            )

            reduce_blur = st.checkbox(
                "Reducción de Desenfoque",
                value=reduce_blur,
                help="Intenta reducir desenfoque en imágenes borrosas"
            )

        # Nuevas opciones: Inpainting
        st.subheader("🖌️ Inpainting")
        enable_inpainting = st.checkbox(
            "Eliminar Objetos",
            value=enable_inpainting,
            help="Elimina objetos no deseados de la imagen"
        )

        if enable_inpainting:
            inpaint_method = st.selectbox(
                "Método de Inpainting",
                options=["telea", "ns", "content_aware"],
                index=["telea", "ns", "content_aware"].index(inpaint_method) if inpaint_method in ["telea", "ns", "content_aware"] else 0,
                help="Algoritmo para rellenar áreas eliminadas"
            )

        # Nuevas opciones: Image-to-Image
        st.subheader("🎨 Image-to-Image")
        enable_image_to_image = st.checkbox(
            "Transformaciones de Estilo",
            value=enable_image_to_image,
            help="Aplica transformaciones de estilo a la imagen"
        )

        if enable_image_to_image:
            transform_type = st.selectbox(
                "Tipo de Transformación",
                options=["Estilo de Color", "Estación", "Hora del Día"],
                index=["Estilo de Color", "Estación", "Hora del Día"].index(transform_type) if transform_type in ["Estilo de Color", "Estación", "Hora del Día"] else 0,
                help="Tipo de transformación a aplicar"
            )

            if transform_type == "Estilo de Color":
                style_options = ["warm", "cool", "vintage", "dramatic", "vibrant", "muted", "high_contrast", "soft"]
                style_option = st.selectbox(
                    "Estilo",
                    options=style_options,
                    index=style_options.index(style_option) if style_option in style_options else 0,
                    help="Estilo de color a aplicar"
                )
            elif transform_type == "Estación":
                season_options = ["spring", "summer", "autumn", "winter"]
                style_option = st.selectbox(
                    "Estación",
                    options=season_options,
                    index=season_options.index(style_option) if style_option in season_options else 0,
                    help="Estación del año"
                )
            else:  # Hora del Día
                time_options = ["dawn", "morning", "noon", "sunset", "night"]
                style_option = st.selectbox(
                    "Hora del Día",
                    options=time_options,
                    index=time_options.index(style_option) if style_option in time_options else 0,
                    help="Momento del día"
                )

            transform_intensity = st.slider(
                "Intensidad de Transformación",
                min_value=0.1,
                max_value=1.0,
                value=transform_intensity,
                step=0.1,
                help="Intensidad de la transformación aplicada"
            )

        # Información del sistema
        st.subheader("💻 Información del Sistema")
        st.info("✅ Optimizado para CPU\n✅ Procesamiento local\n✅ Sin límites de uso")

        # Botón de procesamiento
        process_button = st.button("🚀 Procesar Imágenes", type="primary", use_container_width=True)

        # Limpiar configuración recomendada
        if st.button("🔄 Limpiar Configuración Inteligente"):
            if 'recommended_config' in st.session_state:
                del st.session_state.recommended_config
            st.rerun()

    # Área principal
    col1, col2 = st.columns(2)

    with col1:
        st.header("📤 Imagen Original")

        # Upload de imagen
        uploaded_file = st.file_uploader(
            "Seleccioná una imagen",
            type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
            help="Formatos soportados: PNG, JPG, JPEG, WebP, BMP. Máximo 10MB."
        )

        if uploaded_file is not None:
            try:
                # Cargar imagen
                image = Image.open(uploaded_file)

                # Validar imagen
                is_valid, errors = ImageValidator.validate_image_object(image)
                if not is_valid:
                    st.error("❌ Error en la imagen:")
                    for error in errors:
                        st.error(f"• {error}")
                    return

                # Mostrar imagen original
                st.image(image, caption="Imagen Original", use_container_width=True)

                # Información de la imagen
                img_info = ImageValidator.get_image_info(image)
                with st.expander("📊 Información de la Imagen"):
                    st.write(f"**Tamaño:** {img_info['width']} x {img_info['height']} píxeles")
                    st.write(".2f")
                    st.write(f"**Modo:** {img_info['mode']}")
                    st.write(".1f")

            except Exception as e:
                st.error(f"❌ Error cargando imagen: {str(e)}")
                return
        else:
            # Imagen de ejemplo
            st.info("💡 Subí una imagen para comenzar")
            st.markdown("""
            **Ejemplos de uso:**
            - Fotos antiguas con rostros
            - Imágenes pixeladas
            - Fotos con iluminación pobre
            - Retrato con detalles finos
            """)

    with col2:
        st.header("📥 Resultado")

        # Mostrar resultado si existe
        if 'result_image' in st.session_state and st.session_state.result_image is not None:
            result_img = st.session_state.result_image

            # Mostrar imagen procesada
            st.image(result_img, caption="Imagen Procesada", use_container_width=True)

            # DEBUGGING: Mostrar información del procesamiento
            if 'processing_metadata' in st.session_state:
                metadata = st.session_state.processing_metadata
                with st.expander("🔍 Información de Debug"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Rostros detectados:** {metadata.get('face_count', 0)}")
                        st.write(f"**Pasos aplicados:** {', '.join(metadata.get('steps_applied', []))}")
                        st.write(f"**Tamaño original:** {metadata.get('original_size', 'N/A')}")
                        if metadata.get('damage_regions_found', 0) > 0:
                            st.write(f"**Daños detectados:** {metadata.get('damage_regions_found', 0)}")
                            st.write(f"**Daños restaurados:** {metadata.get('damage_regions_restored', 0)}")
                            st.write(f"**Tipos de daño:** {', '.join(metadata.get('damage_types_found', []))}")
                    with col2:
                        st.write(f"**Tamaño final:** {metadata.get('final_size', 'N/A')}")
                        st.write(".2f")
                        if metadata.get('errors'):
                            st.error(f"**Errores:** {len(metadata['errors'])}")
                            for error in metadata['errors']:
                                st.error(f"• {error}")

            # Información del procesamiento
            if 'processing_metadata' in st.session_state:
                metadata = st.session_state.processing_metadata
                with st.expander("📈 Información del Procesamiento"):
                    st.write(".2f")
                    if 'face_count' in metadata:
                        st.write(f"**Rostros detectados:** {metadata['face_count']}")
                    if 'steps_applied' in metadata:
                        st.write(f"**Pasos aplicados:** {', '.join(metadata['steps_applied'])}")
                    if 'scale_factor' in metadata:
                        st.write(f"**Factor de escala:** {metadata['scale_factor']}x")
                    if metadata.get('damage_regions_found', 0) > 0:
                        st.write(f"**Regiones de daño encontradas:** {metadata['damage_regions_found']}")
                        st.write(f"**Regiones restauradas:** {metadata['damage_regions_restored']}")
                        if metadata.get('damage_types_found'):
                            st.write(f"**Tipos de daño:** {', '.join(metadata['damage_types_found'])}")
                    if metadata.get('errors'):
                        st.error("Errores durante el procesamiento:")
                        for error in metadata['errors']:
                            st.error(f"• {error}")

            # Botón de descarga
            if st.button("💾 Descargar Resultado", use_container_width=True):
                # Crear nombre de archivo con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"restored_image_{timestamp}.png"

                # Convertir imagen a bytes para descarga
                import io
                buffered = io.BytesIO()
                result_img.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()

                st.download_button(
                    label="📥 Descargar PNG",
                    data=img_bytes,
                    file_name=filename,
                    mime="image/png",
                    use_container_width=True
                )

        else:
            st.info("🎯 El resultado aparecerá aquí después del procesamiento")

    # Procesamiento
    if process_button and uploaded_file is not None:
        try:
            with st.spinner("🔄 Procesando imagen... Esto puede tardar unos segundos."):

                # Preparar opciones de procesamiento
                options = {
                    'auto_restoration': auto_restoration,
                    'restoration_method': restoration_method if auto_restoration else 'content_aware',
                    'face_enhancement': face_enhancement,
                    'enhancement_strength': enhancement_strength,
                    'super_resolution': super_resolution,
                    'scale_factor': scale_factor,
                    'interpolation_method': interpolation_method,
                    'enhance_sharpness': enhance_sharpness if super_resolution else False,
                    'reduce_blur': reduce_blur if super_resolution else False,
                    'inpainting': enable_inpainting,
                    'inpaint_method': inpaint_method if enable_inpainting else None,
                    'image_to_image': enable_image_to_image,
                    'transform_type': transform_type if enable_image_to_image else None,
                    'style_option': style_option if enable_image_to_image else None,
                    'transform_intensity': transform_intensity if enable_image_to_image else 0.7
                }

                # Validar opciones
                is_valid, errors = ImageValidator.validate_processing_options(options)
                if not is_valid:
                    st.error("❌ Error en configuración:")
                    for error in errors:
                        st.error(f"• {error}")
                    return

                # Procesar imagen
                start_time = time.time()
                result, metadata = st.session_state.pipeline.process_image(image, options)
                processing_time = time.time() - start_time

                # Guardar resultado en session state
                st.session_state.result_image = result
                st.session_state.processing_metadata = metadata

                # Mostrar éxito
                st.success(f"✅ Procesamiento completado en {processing_time:.2f} segundos")
                st.rerun()

        except Exception as e:
            error_info = ErrorHandler.handle_processing_error(e, "procesamiento_principal")
            st.error(f"❌ Error durante el procesamiento: {error_info['user_message']}")

            # Log detallado para debugging
            logger.error(f"Error detallado: {str(e)}")
            with st.expander("🔍 Detalles del Error (para soporte)"):
                st.code(str(e))

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Image Restoration App v1.0.0 - Optimizado para CPU<br>
        Procesamiento local • Sin límites de uso • Código abierto
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()