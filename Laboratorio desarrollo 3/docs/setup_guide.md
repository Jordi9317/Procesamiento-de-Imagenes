# Guía de Instalación y Configuración

## Requisitos Previos

### Sistema Operativo
- **Windows 10/11**
- **macOS 12+**
- **Linux (Ubuntu 20.04+, CentOS 8+)**

### Python
- **Versión**: 3.8 o superior
- **Arquitectura**: 64-bit

### Hardware Recomendado
- **CPU**: Intel i5/Ryzen 5 o superior
- **RAM**: 8GB mínimo, 16GB recomendado
- **GPU**: NVIDIA con 4GB VRAM mínimo (opcional pero recomendado)
- **Almacenamiento**: 10GB libres en disco

## Instalación Paso a Paso

### Paso 1: Verificar Python

```bash
# Verificar versión de Python
python --version
# Debe mostrar Python 3.8 o superior

# Si no está instalado, descargar desde:
# https://www.python.org/downloads/
```

### Paso 2: Crear Entorno Virtual

#### Windows (CMD/PowerShell)
```cmd
# Navegar al directorio del proyecto
cd c:\Proyecto\Laboratorio_desarrollo_3

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate
```

#### Linux/macOS (Terminal)
```bash
# Navegar al directorio del proyecto
cd /ruta/a/Laboratorio_desarrollo_3

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

**Nota**: El entorno virtual debe activarse **siempre** antes de usar la aplicación.

### Paso 3: Instalar Dependencias

```bash
# Asegurarse de que el entorno virtual esté activado
# (verás (venv) al inicio de la línea de comandos)

# Instalar dependencias principales
pip install -r requirements.txt
```

### Paso 4: Verificar Instalación

```bash
# Ejecutar verificación
python -c "
import torch
import streamlit
from diffusers import DiffusionPipeline
print('✅ Todas las dependencias instaladas correctamente')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA disponible: {torch.cuda.is_available()}')
"
```

### Paso 5: Primera Ejecución

```bash
# Ejecutar la aplicación
streamlit run app.py
```

La aplicación debería abrirse en tu navegador en `http://localhost:8501`

## Configuración Avanzada

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Copiar y modificar según tu configuración
cp .env.example .env

# O crear manualmente con:
DEVICE=auto
MAX_IMAGE_SIZE=2048
MODEL_CACHE_DIR=./assets/models
```

### Configuración de GPU (Opcional)

Si tienes GPU NVIDIA:

```bash
# Verificar instalación de CUDA
nvidia-smi

# Si CUDA no está instalado:
# Descargar desde: https://developer.nvidia.com/cuda-downloads
```

### Configuración para CPU (Si no tienes GPU)

```bash
# En .env
DEVICE=cpu

# Instalar versión CPU de PyTorch si es necesario
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## Solución de Problemas

### Error: "python no es reconocido"
```bash
# Agregar Python al PATH del sistema
# O usar python3 en Linux/Mac
python3 -m venv venv
```

### Error: "No module named 'torch'"
```bash
# Reactivar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstalar PyTorch
pip install torch torchvision
```

### Error de Memoria en GPU
```bash
# Reducir tamaño máximo de imagen en .env
MAX_IMAGE_SIZE=1024

# O forzar uso de CPU
DEVICE=cpu
```

### Error de Descarga de Modelos
```bash
# Verificar conexión a internet
# Configurar proxy si es necesario
# Intentar con VPN si hay restricciones de red
```

### Aplicación no se Abre
```bash
# Verificar que streamlit esté instalado
pip list | grep streamlit

# Ejecutar en puerto diferente
streamlit run app.py --server.port 8502
```

## Estructura de Archivos Esperada

Después de la instalación completa:

```
Laboratorio_desarrollo_3/
├── venv/                    # Entorno virtual
├── app.py                   # Aplicación principal
├── requirements.txt         # Dependencias
├── .env                     # Configuración (crear)
├── src/
│   ├── models/
│   ├── utils/
│   └── config/
├── tests/
├── benchmarks/
├── assets/
│   └── sample_images/
└── README.md
```

## Comandos Útiles

### Gestión del Entorno Virtual

```bash
# Activar
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Desactivar
deactivate

# Eliminar y recrear
rm -rf venv
python -m venv venv
```

### Actualización

```bash
# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Actualizar aplicación
git pull  # si es un repositorio
```

### Limpieza

```bash
# Limpiar cache de pip
pip cache purge

# Limpiar modelos descargados (libera espacio)
rm -rf assets/models/*
```

## Verificación Final

Para confirmar que todo funciona:

1. ✅ Entorno virtual activado (`(venv)` visible)
2. ✅ Todas las dependencias instaladas
3. ✅ Aplicación se ejecuta sin errores
4. ✅ Puedes cargar y procesar imágenes
5. ✅ Resultados se guardan correctamente

## Soporte

Si encuentras problemas:

1. Revisar esta guía nuevamente
2. Verificar [README.md](README.md) para más detalles
3. Consultar issues en el repositorio
4. Contactar al equipo de desarrollo

## Próximos Pasos

Una vez instalado:

1. Explorar la interfaz de la aplicación
2. Probar con imágenes de ejemplo
3. Experimentar con diferentes configuraciones
4. Revisar benchmarks de rendimiento