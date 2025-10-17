# TRABAJO PRÁCTICO INTEGRADOR N°1: Sistema de Análisis de Documentos Digitalizados

## Descripción del Proyecto

Este proyecto desarrolla un sistema básico de análisis automático de documentos digitalizados, integrando técnicas de procesamiento de imágenes para abordar problemas comunes como la rotación, baja calidad e iluminación deficiente en documentos escaneados.

## Estructura del Trabajo

El trabajo está organizado en las siguientes partes, reflejadas en el notebook principal:

1.  **Fundamentos Teóricos:** Discute la metodología de trabajo con cuadernos interactivos en IA y Ciencia de Datos.
2.  **Setup del Entorno:** Configuración de librerías y funciones utilitarias para el procesamiento de imágenes.
3.  **Análisis de Imágenes:** Carga e inspección visual y técnica (histogramas) de un dataset de ejemplo de 3 documentos.
4.  **Preprocessing Básico:** Aplicación de técnicas de segmentación, mejora de calidad (ecualización, sharpening) y corrección geométrica (homografía) a las imágenes del dataset.
5.  **Reflexión Final:** Análisis de los resultados, desafíos y aprendizajes del proceso.

## Requisitos

Para ejecutar este proyecto, necesitarás tener instalado Python 3.6+ y las siguientes librerías. La celda 6BUY1Z-4b622 del notebook se encarga de instalar las principales:

*   `requests`
*   `Pillow`
*   `matplotlib`
*   `numpy`
*   `pandas`
*   `seaborn`
*   `opencv-python` (`cv2`)
*   `scikit-image` (`skimage`)
*   `scikit-learn` (`sklearn`)

Si usas Google Colab, el entorno ya incluye la mayoría de estas dependencias.

## Setup del Entorno y Ejecución

1.  **Clonar el Repositorio (Si aplica) o Descargar los Archivos:** Asegúrate de tener el notebook principal (`TRABAJO_PRACTICO_INTEGRADOR_1.ipynb`) y cualquier otro archivo de código auxiliar.
2.  **Crear la Carpeta `dataset/`:** En la misma ubicación del notebook, crea una carpeta llamada `dataset/`.
3.  **Agregar Imágenes al Dataset:** Dentro de la carpeta `dataset/`, coloca tus 3 imágenes de documentos con las siguientes características:
    *   `Buena calidad.jpg` (o el nombre que hayas usado en el código)
    *   `Rotada.jpg` (o el nombre que hayas usado en el código)
    *   `Con problemas.jpg` (o el nombre que hayas usado en el código)
    *   **¡Importante!** Asegúrate de que los nombres de archivo en la carpeta `dataset/` coincidan exactamente con los nombres utilizados en el código del notebook (`iJlGWs1Csuvs`). Presta atención a espacios y mayúsculas/minúsculas.
4.  **Abrir y Ejecutar el Notebook:** Abre el archivo `TRABAJO_PRACTICO_INTEGRADOR_1.ipynb` en Google Colab, Jupyter Notebook, JupyterLab o tu entorno de cuadernos interactivos preferido.
5.  **Ejecutar Celdas Secuencialmente:** Ejecuta todas las celdas del notebook en orden. Esto instalará las dependencias, cargará las funciones, procesará las imágenes del `dataset/` y mostrará los resultados.
6.  **Revisar y Completar:** Revisa los resultados de las celdas de procesamiento de imágenes y completa la sección de **Reflexión Final** con tus análisis y aprendizajes.

## Contenidos del Dataset de Ejemplo

El dataset utilizado para la demostración incluye:

*   `Buena calidad.jpg`: Una imagen de documento con buena iluminación y alineación.
*   `Rotada.jpg`: Una imagen de documento que requiere corrección de rotación.
*   `Con problemas.jpg`: Una imagen de documento con problemas de iluminación o enfoque.

*(Nota: Estas imágenes son ejemplos y pueden ser reemplazadas por tus propias imágenes siempre que cumplan con las características y nombres de archivo especificados).*

