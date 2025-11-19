#!/usr/bin/env python3
"""
Image Restoration App - CPU Optimized
AplicaciÃ³n web Streamlit para restaurar y mejorar imÃ¡genes usando IA.
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

# Importar mÃ³dulos locales
from Laboratorio_desarrollo_3.src.image_pipeline import ImageRestorationPipeline
from Laboratorio_desarrollo_3.src.validation import ImageValidator, ErrorHandler, safe_image_operation

# ConfiguraciÃ³n de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ConfiguraciÃ³n de la pÃ¡gina
st.set_page_config(
    page_title="ð¼ï¸ Image Restoration App",
    page_icon="ð¼ï¸",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        # Image Restoration App

        AplicaciÃ³n para restaurar y mejorar imÃ¡genes usando tÃ©cnicas de IA optimizadas para CPU.

        **CaracterÃ­sticas:**
        - Mejora automÃ¡tica de rostros
        - Super-resoluciÃ³n 2x-4x
        - Procesamiento local y privado
        - Optimizado para CPU

        **VersiÃ³n:** 1.0.0
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
    """Muestra guÃ­a interactiva segÃºn tipo de imagen"""
    st.header("ð¯ Asistente Inteligente - Â¿QuÃ© tipo de imagen tienes?")

    # Selector de tipo de imagen
    image_types = {
        "ð¸ Foto con rostros": {
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
        "ð Imagen pixelada/pequeÃ±a": {
            "description": "Foto de baja resoluciÃ³n, captura pixelada",
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
        "ð«ï¸ Foto borrosa/desenfocada": {
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
        "ð« Objetos no deseados": {
            "description": "Foto con personas/cosas que quieres eliminar",
            "recommended": ["inpainting"],
            "config": {
                "face_enhancement": False,
                "super_resolution": False,
                "inpainting": True,
                "inpaint_method": "telea"
            }
        },
        "ð¨ Cambiar estilo/atmÃ³sfera": {
            "description": "Modificar colores, estaciÃ³n, hora del dÃ­a",
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
        "ð Foto antigua/daÃ±ada": {
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
        help="Elige la opciÃ³n que mejor describe tu imagen"
    )

    # Mostrar descripciÃ³n y recomendaciones
    type_info = image_types[selected_type]

    st.info(f"**{selected_type}**: {type_info['description']}")

    st.subheader("â Herramientas Recomendadas")
    recommended_tools = type_info['recommended']
    for tool in recommended_tools:
        if tool == "auto_restoration":
            st.success("ð§ **RestauraciÃ³n AutomÃ¡tica**: Detecta y repara daÃ±os automÃ¡ticamente")
        elif tool == "face_enhancement":
            st.success("ð§ **Face Enhancement**: Mejora automÃ¡ticamente rostros")
        elif tool == "super_resolution":
            st.success("ð **Super-Resolution**: Aumenta resoluciÃ³n y nitidez")
        elif tool == "inpainting":
            st.success("ðï¸ **Inpainting**: Elimina objetos no deseados")
        elif tool == "image_to_image":
            st.success("ð¨ **Image-to-Image**: Transforma estilo y atmÃ³sfera")

    # BotÃ³n para aplicar configuraciÃ³n recomendada
    if st.button("ð Aplicar ConfiguraciÃ³n Recomendada", type="primary"):
        # Guardar configuraciÃ³n en session state
        st.session_state.recommended_config = type_info['config']
        st.success("â ConfiguraciÃ³n aplicada al sidebar. Ahora sube tu imagen y procesa.")

        # Mostrar configuraciÃ³n aplicada
        with st.expander("âï¸ ConfiguraciÃ³n Aplicada"):
            config = type_info['config']
            if config.get('auto_restoration'):
                st.write(f"â¢ RestauraciÃ³n AutomÃ¡tica: ON (mÃ©todo: {config.get('restoration_method', 'content_aware')})")
            if config.get('face_enhancement'):
                st.write(f"â¢ Face Enhancement: ON (intensidad: {config.get('enhancement_strength', 0.7)})")
            if config.get('super_resolution'):
                st.write(f"â¢ Super-Resolution: ON ({config.get('scale_factor', 2)}x, {config.get('interpolation_method', 'lanczos')})")
                if config.get('enhance_sharpness'):
                    st.write("â¢ Nitidez Avanzada: ON")
                if config.get('reduce_blur'):
                    st.write("â¢ ReducciÃ³n de Desenfoque: ON")
            if config.get('inpainting'):
                st.write(f"â¢ Inpainting: ON (mÃ©todo: {config.get('inpaint_method', 'telea')})")
            if config.get('image_to_image'):
                st.write(f"â¢ Image-to-Image: ON ({config.get('transform_type', 'Estilo de Color')}: {config.get('style_option', 'warm')})")

    return image_types

def main():
    """FunciÃ³n principal de la aplicaciÃ³n"""

    # TÃ­tulo principal
    st.title("ð¼ï¸ Image Restoration App")
    st.markdown("*RestaurÃ¡ y mejorÃ¡ tus imÃ¡genes con IA - Optimizado para CPU*")

    # Tabs para navegaciÃ³n
    tab1, tab2 = st.tabs(["ð¯ Asistente Inteligente", "âï¸ ConfiguraciÃ³n Manual"])

    with tab1:
        # Asistente inteligente
        image_types = show_image_type_guide()

    with tab2:
        st.header("âï¸ ConfiguraciÃ³n Manual Avanzada")
        st.markdown("Para usuarios avanzados que quieren control total")

    # Sidebar con configuraciÃ³n
    with st.sidebar:
        st.header("âï¸ ConfiguraciÃ³n")

        # Cargar configuraciÃ³n recomendada si existe
        if 'recommended_config' in st.session_state:
            st.info("ð¯ ConfiguraciÃ³n recomendada aplicada automÃ¡ticamente")
            config = st.session_state.recommended_config

            # Aplicar configuraciÃ³n recomendada
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

            st.success("â ConfiguraciÃ³n inteligente aplicada")
        else:
            # ConfiguraciÃ³n manual por defecto
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

        # Nueva opciÃ³n: Auto Restoration
        auto_restoration = st.checkbox(
            "ð§ RestauraciÃ³n AutomÃ¡tica",
            value=auto_restoration,
            help="Detecta y repara automÃ¡ticamente daÃ±os en la imagen (grietas, manchas, quemaduras)"
        )

        if auto_restoration:
            restoration_method = st.selectbox(
                "MÃ©todo de RestauraciÃ³n",
                options=["content_aware", "telea", "ns"],
                index=["content_aware", "telea", "ns"].index(restoration_method) if restoration_method in ["content_aware", "telea", "ns"] else 0,
                help="Algoritmo para restaurar daÃ±os detectados automÃ¡ticamente"
            )

        face_enhancement = st.checkbox(
            "Mejora Facial",
            value=face_enhancement,
            help="Detecta y mejora automÃ¡ticamente los rostros en la imagen"
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
            "Super-ResoluciÃ³n",
            value=super_resolution,
            help="Aumenta la resoluciÃ³n de la imagen"
        )

        scale_factor = st.selectbox(
            "Factor de Escala",
            options=[2, 3, 4],
            index=[2, 3, 4].index(scale_factor) if scale_factor in [2, 3, 4] else 0,
            help="CuÃ¡nto aumentar la resoluciÃ³n",
            disabled=not super_resolution
        )

        interpolation_method = st.selectbox(
            "MÃ©todo de InterpolaciÃ³n",
            options=["lanczos", "bicubic", "bilinear"],
            index=["lanczos", "bicubic", "bilinear"].index(interpolation_method) if interpolation_method in ["lanczos", "bicubic", "bilinear"] else 0,
            help="Algoritmo de interpolaciÃ³n para super-resoluciÃ³n",
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
                "ReducciÃ³n de Desenfoque",
                value=reduce_blur,
                help="Intenta reducir desenfoque en imÃ¡genes borrosas"
            )

        # Nuevas opciones: Inpainting
        st.subheader("ðï¸ Inpainting")
        enable_inpainting = st.checkbox(
            "Eliminar Objetos",
            value=enable_inpainting,
            help="Elimina objetos no deseados de la imagen"
        )

        if enable_inpainting:
            inpaint_method = st.selectbox(
                "MÃ©todo de Inpainting",
                options=["telea", "ns", "content_aware"],
                index=["telea", "ns", "content_aware"].index(inpaint_method) if inpaint_method in ["telea", "ns", "content_aware"] else 0,
                help="Algoritmo para rellenar Ã¡reas eliminadas"
            )

        # Nuevas opciones: Image-to-Image
        st.subheader("ð¨ Image-to-Image")
        enable_image_to_image = st.checkbox(
            "Transformaciones de Estilo",
            value=enable_image_to_image,
            help="Aplica transformaciones de estilo a la imagen"
        )

        if enable_image_to_image:
            transform_type = st.selectbox(
                "Tipo de TransformaciÃ³n",
                options=["Estilo de Color", "EstaciÃ³n", "Hora del DÃ­a"],
                index=["Estilo de Color", "EstaciÃ³n", "Hora del DÃ­a"].index(transform_type) if transform_type in ["Estilo de Color", "EstaciÃ³n", "Hora del DÃ­a"] else 0,
                help="Tipo de transformaciÃ³n a aplicar"
            )

            if transform_type == "Estilo de Color":
                style_options = ["warm", "cool", "vintage", "dramatic", "vibrant", "muted", "high_contrast", "soft"]
                style_option = st.selectbox(
                    "Estilo",
                    options=style_options,
                    index=style_options.index(style_option) if style_option in style_options else 0,
                    help="Estilo de color a aplicar"
                )
            elif transform_type == "EstaciÃ³n":
                season_options = ["spring", "summer", "autumn", "winter"]
                style_option = st.selectbox(
                    "EstaciÃ³n",
                    options=season_options,
                    index=season_options.index(style_option) if style_option in season_options else 0,
                    help="EstaciÃ³n del aÃ±o"
                )
            else:  # Hora del DÃ­a
                time_options = ["dawn", "morning", "noon", "sunset", "night"]
                style_option = st.selectbox(
                    "Hora del DÃ­a",
                    options=time_options,
                    index=time_options.index(style_option) if style_option in time_options else 0,
                    help="Momento del dÃ­a"
                )

            transform_intensity = st.slider(
                "Intensidad de TransformaciÃ³n",
                min_value=0.1,
                max_value=1.0,
                value=transform_intensity,
                step=0.1,
                help="Intensidad de la transformaciÃ³n aplicada"
            )

        # InformaciÃ³n del sistema
        st.subheader("ð» InformaciÃ³n del Sistema")
        st.info("â Optimizado para CPU\nâ Procesamiento local\nâ Sin lÃ­mites de uso")

        # BotÃ³n de procesamiento
        process_button = st.button("ð Procesar ImÃ¡genes", type="primary", use_container_width=True)

        # Limpiar configuraciÃ³n recomendada
        if st.button("ð Limpiar ConfiguraciÃ³n Inteligente"):
            if 'recommended_config' in st.session_state:
                del st.session_state.recommended_config
            st.rerun()

    # Ãrea principal
    col1, col2 = st.columns(2)

    with col1:
        st.header("ð¤ Imagen Original")

        # Upload de imagen
        uploaded_file = st.file_uploader(
            "SeleccionÃ¡ una imagen",
            type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
            help="Formatos soportados: PNG, JPG, JPEG, WebP, BMP. MÃ¡ximo 10MB."
        )

        if uploaded_file is not None:
            try:
                # Cargar imagen
                image = Image.open(uploaded_file)

                # Validar imagen
                is_valid, errors = ImageValidator.validate_image_object(image)
                if not is_valid:
                    st.error("â Error en la imagen:")
                    for error in errors:
                        st.error(f"â¢ {error}")
                    return

                # Mostrar imagen original
                st.image(image, caption="Imagen Original", use_container_width=True)

                # InformaciÃ³n de la imagen
                img_info = ImageValidator.get_image_info(image)
                with st.expander("ð InformaciÃ³n de la Imagen"):
                    st.write(f"**TamaÃ±o:** {img_info['width']} x {img_info['height']} pÃ­xeles")
                    st.write(".2f")
                    st.write(f"**Modo:** {img_info['mode']}")
                    st.write(".1f")

            except Exception as e:
                st.error(f"â Error cargando imagen: {str(e)}")
                return
        else:
            # Imagen de ejemplo
            st.info("ð¡ SubÃ­ una imagen para comenzar")
            st.markdown("""
            **Ejemplos de uso:**
            - Fotos antiguas con rostros
            - ImÃ¡genes pixeladas
            - Fotos con iluminaciÃ³n pobre
            - Retrato con detalles finos
            """)

    with col2:
        st.header("ð¥ Resultado")

        # Mostrar resultado si existe
        if 'result_image' in st.session_state and st.session_state.result_image is not None:
            result_img = st.session_state.result_image

            # Mostrar imagen procesada
            st.image(result_img, caption="Imagen Procesada", use_container_width=True)

            # DEBUGGING: Mostrar informaciÃ³n del procesamiento
            if 'processing_metadata' in st.session_state:
                metadata = st.session_state.processing_metadata
                with st.expander("ð InformaciÃ³n de Debug"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Rostros detectados:** {metadata.get('face_count', 0)}")
                        st.write(f"**Pasos aplicados:** {', '.join(metadata.get('steps_applied', []))}")
                        st.write(f"**TamaÃ±o original:** {metadata.get('original_size', 'N/A')}")
                        if metadata.get('damage_regions_found', 0) > 0:
                            st.write(f"**DaÃ±os detectados:** {metadata.get('damage_regions_found', 0)}")
                            st.write(f"**DaÃ±os restaurados:** {metadata.get('damage_regions_restored', 0)}")
                            st.write(f"**Tipos de daÃ±o:** {', '.join(metadata.get('damage_types_found', []))}")
                    with col2:
                        st.write(f"**TamaÃ±o final:** {metadata.get('final_size', 'N/A')}")
                        st.write(".2f")
                        if metadata.get('errors'):
                            st.error(f"**Errores:** {len(metadata['errors'])}")
                            for error in metadata['errors']:
                                st.error(f"â¢ {error}")

            # InformaciÃ³n del procesamiento
            if 'processing_metadata' in st.session_state:
                metadata = st.session_state.processing_metadata
                with st.expander("ð InformaciÃ³n del Procesamiento"):
                    st.write(".2f")
                    if 'face_count' in metadata:
                        st.write(f"**Rostros detectados:** {metadata['face_count']}")
                    if 'steps_applied' in metadata:
                        st.write(f"**Pasos aplicados:** {', '.join(metadata['steps_applied'])}")
                    if 'scale_factor' in metadata:
                        st.write(f"**Factor de escala:** {metadata['scale_factor']}x")
                    if metadata.get('damage_regions_found', 0) > 0:
                        st.write(f"**Regiones de daÃ±o encontradas:** {metadata['damage_regions_found']}")
                        st.write(f"**Regiones restauradas:** {metadata['damage_regions_restored']}")
                        if metadata.get('damage_types_found'):
                            st.write(f"**Tipos de daÃ±o:** {', '.join(metadata['damage_types_found'])}")
                    if metadata.get('errors'):
                        st.error("Errores durante el procesamiento:")
                        for error in metadata['errors']:
                            st.error(f"â¢ {error}")

            # BotÃ³n de descarga
            if st.button("ð¾ Descargar Resultado", use_container_width=True):
                # Crear nombre de archivo con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"restored_image_{timestamp}.png"

                # Convertir imagen a bytes para descarga
                import io
                buffered = io.BytesIO()
                result_img.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()

                st.download_button(
                    label="ð¥ Descargar PNG",
                    data=img_bytes,
                    file_name=filename,
                    mime="image/png",
                    use_container_width=True
                )

        else:
            st.info("ð¯ El resultado aparecerÃ¡ aquÃ­ despuÃ©s del procesamiento")

    # Procesamiento
    if process_button and uploaded_file is not None:
        try:
            with st.spinner("ð Procesando imagen... Esto puede tardar unos segundos."):

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
                    st.error("â Error en configuraciÃ³n:")
                    for error in errors:
                        st.error(f"â¢ {error}")
                    return

                # Procesar imagen
                start_time = time.time()
                result, metadata = st.session_state.pipeline.process_image(image, options)
                processing_time = time.time() - start_time

                # Guardar resultado en session state
                st.session_state.result_image = result
                st.session_state.processing_metadata = metadata

                # Mostrar Ã©xito
                st.success(f"â Procesamiento completado en {processing_time:.2f} segundos")
                st.rerun()

        except Exception as e:
            error_info = ErrorHandler.handle_processing_error(e, "procesamiento_principal")
            st.error(f"â Error durante el procesamiento: {error_info['user_message']}")

            # Log detallado para debugging
            logger.error(f"Error detallado: {str(e)}")
            with st.expander("ð Detalles del Error (para soporte)"):
                st.code(str(e))

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Image Restoration App v1.0.0 - Optimizado para CPU<br>
        Procesamiento local â¢ Sin lÃ­mites de uso â¢ CÃ³digo abierto
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()"# Forzar actualizaci¢n" 
