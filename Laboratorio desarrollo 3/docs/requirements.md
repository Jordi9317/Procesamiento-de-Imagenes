# Dependencias del Proyecto: Aplicación de Restauración de Imágenes

## Librerías Core

### Framework Web
- **streamlit>=1.28.0**: Interfaz web principal
- **streamlit-extras**: Componentes adicionales para Streamlit

### Deep Learning y Modelos IA
- **torch>=2.0.0**: PyTorch para modelos de deep learning
- **torchvision>=0.15.0**: Utilidades de visión por computadora
- **diffusers>=0.25.0**: Modelos de difusión para super-resolution
- **transformers>=4.35.0**: Modelos de Hugging Face
- **accelerate>=0.25.0**: Optimizaciones de rendimiento

### Procesamiento de Imágenes
- **Pillow>=10.0.0**: Manipulación básica de imágenes
- **opencv-python>=4.8.0**: Procesamiento avanzado de imágenes
- **numpy>=1.24.0**: Operaciones numéricas
- **scikit-image>=0.21.0**: Algoritmos de procesamiento de imágenes

### Face Restoration (GFPGAN)
- **gfpgan>=1.3.8**: Modelo GFPGAN para restauración facial
- **realesrgan>=0.3.0**: Componente requerido por GFPGAN
- **facexlib>=0.3.0**: Librería de detección facial
- **basicsr>=1.4.2**: Framework base para GFPGAN

### Utilidades
- **requests>=2.31.0**: Descarga de imágenes y modelos
- **pathlib2>=2.3.0**: Manejo moderno de rutas
- **python-dotenv>=1.0.0**: Variables de entorno
- **tqdm>=4.65.0**: Barras de progreso

### Testing y Desarrollo
- **pytest>=7.4.0**: Framework de testing
- **pytest-cov>=4.1.0**: Cobertura de tests
- **black>=23.0.0**: Formateo de código
- **flake8>=6.0.0**: Linting de código

## Instalación por Categorías

### Instalación Mínima (CPU)
```bash
pip install torch torchvision Pillow numpy streamlit
```

### Instalación Completa (GPU Recomendada)
```bash
pip install -r requirements.txt
```

### Instalación por Componentes
```bash
# Core
pip install streamlit torch torchvision diffusers transformers accelerate

# Imágenes
pip install Pillow opencv-python numpy scikit-image

# Face restoration
pip install gfpgan realesrgan facexlib basicsr

# Utilidades
pip install requests python-dotenv tqdm

# Testing
pip install pytest pytest-cov black flake8
```

## Requisitos del Sistema

### Hardware Mínimo
- **CPU**: Intel i5 / Ryzen 5 o superior
- **RAM**: 8 GB
- **Almacenamiento**: 5 GB libres
- **GPU**: Opcional, pero recomendado (4GB VRAM mínima)

### Hardware Recomendado
- **CPU**: Intel i7 / Ryzen 7 o superior
- **RAM**: 16 GB
- **GPU**: NVIDIA con 8GB+ VRAM (RTX 3060 o superior)
- **Almacenamiento**: SSD con 20GB libres

## Configuración del Entorno Virtual

### Windows
```cmd
# Crear entorno
python -m venv venv

# Activar entorno
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Linux/Mac
```bash
# Crear entorno
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Configuración de dispositivo
DEVICE=auto  # auto, cpu, cuda

# Límites de procesamiento
MAX_IMAGE_SIZE=2048
MAX_FILE_SIZE_MB=10

# Directorios
MODEL_CACHE_DIR=./assets/models
OUTPUT_DIR=./output
LOG_DIR=./logs

# Configuración de modelos
GFPGAN_MODEL=experiments/pretrained_models/GFPGANv1.4.pth
SR_MODEL=stabilityai/stable-diffusion-x4-upscaler

# Logging
LOG_LEVEL=INFO
```

## Solución de Problemas Comunes

### Error de CUDA
```bash
# Si hay problemas con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Error de GFPGAN
```bash
# Instalar en orden específico
pip install basicsr
pip install facexlib
pip install gfpgan
```

### Memoria Insuficiente
```bash
# Para sistemas con poca RAM
pip install --no-cache-dir -r requirements.txt
```

## Verificación de Instalación

Ejecutar después de la instalación:

```python
import torch
import streamlit as st
from diffusers import DiffusionPipeline
import gfpgan

print("✅ PyTorch:", torch.__version__)
print("✅ CUDA disponible:", torch.cuda.is_available())
print("✅ Streamlit importado correctamente")
print("✅ Diffusers importado correctamente")
print("✅ GFPGAN importado correctamente")
```

## Actualización de Dependencias

```bash
# Actualizar todas las dependencias
pip install -r requirements.txt --upgrade

# Actualizar solo paquetes específicos
pip install torch torchvision diffusers --upgrade
```

## Notas de Compatibilidad

- **Python 3.8+**: Requerido para todas las librerías
- **PyTorch**: Versión 2.0+ para mejor rendimiento
- **CUDA**: Versión 11.8+ si se usa GPU
- **GFPGAN**: Compatible con PyTorch 1.8-2.1
- **Streamlit**: Versión 1.28+ para mejores componentes

## Licencias

- **PyTorch**: BSD-3-Clause
- **Streamlit**: Apache 2.0
- **Diffusers**: Apache 2.0
- **GFPGAN**: MIT
- **OpenCV**: BSD-3-Clause

Asegurarse de revisar las licencias de uso comercial para modelos específicos.