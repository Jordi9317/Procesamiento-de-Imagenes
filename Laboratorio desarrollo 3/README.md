# 🖼️ Image Restoration App

Aplicación web local para restaurar y mejorar imágenes degradadas usando modelos de IA. Combina restauración facial con GFPGAN y super-resolución con modelos de difusión.

## ✨ Características

- **Restauración Facial**: Mejora automática de rostros usando GFPGAN
- **Super-Resolution**: Aumento de resolución 2x-4x con modelos de difusión
- **Pipeline Combinado**: Procesamiento automático completo
- **Interfaz Web**: Streamlit intuitiva y responsive
- **Procesamiento Local**: Todo se ejecuta en tu máquina
- **Optimizado**: Funciona en CPU y GPU

## 🚀 Instalación Rápida

### 1. Clonar o descargar el proyecto

```bash
cd c:\Proyecto\Laboratorio_desarrollo_3
```

### 2. Crear y activar entorno virtual

```cmd
# Windows
python -m venv venv
venv\Scripts\activate
```

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar aplicación

```bash
streamlit run app.py
```

¡La aplicación se abrirá en `http://localhost:8501`!

## 📋 Requisitos del Sistema

### Mínimos
- **Python**: 3.8+
- **RAM**: 8GB
- **Almacenamiento**: 5GB libres

### Recomendados
- **Python**: 3.9+
- **RAM**: 16GB
- **GPU**: NVIDIA con 4GB+ VRAM
- **Almacenamiento**: 10GB libres

## 🎯 Uso de la Aplicación

### 1. Carga de Imágenes
- Arrastra y suelta imágenes o haz clic para seleccionar
- Formatos soportados: JPG, PNG, WebP
- Tamaño máximo: 10MB por imagen

### 2. Modos de Procesamiento

#### Face Restoration
- Detecta automáticamente rostros en la imagen
- Aplica restauración con GFPGAN
- Parámetros ajustables: intensidad, confianza de detección

#### Super Resolution
- Aumenta resolución 2x, 3x o 4x
- Usa modelos de difusión para calidad superior
- Prompt opcional para guiar el proceso

#### Combined Pipeline
- Aplica ambos procesos automáticamente
- Optimizado para mejores resultados

### 3. Exportación
- Descarga imágenes procesadas
- Formatos: PNG (con transparencia), JPG
- Metadata incluida (parámetros usados)

## 🏗️ Arquitectura

```
image_restoration_app/
├── app.py                 # Interfaz principal Streamlit
├── requirements.txt       # Dependencias
├── src/
│   ├── models/           # Modelos IA (GFPGAN, Diffusers)
│   ├── utils/            # Utilidades de procesamiento
│   └── config/           # Configuraciones
├── tests/                # Pruebas unitarias
├── benchmarks/           # Scripts de rendimiento
└── assets/               # Modelos e imágenes de ejemplo
```

## 🔧 Configuración Avanzada

### Variables de Entorno (.env)

```bash
# Dispositivo de procesamiento
DEVICE=auto              # auto, cpu, cuda

# Límites
MAX_IMAGE_SIZE=2048      # píxeles
MAX_FILE_SIZE_MB=10      # MB

# Directorios
MODEL_CACHE_DIR=./assets/models
OUTPUT_DIR=./output

# Modelos
GFPGAN_MODEL=experiments/pretrained_models/GFPGANv1.4.pth
SR_MODEL=stabilityai/stable-diffusion-x4-upscaler
```

### Optimizaciones de Rendimiento

#### Para GPU
```bash
# En .env
DEVICE=cuda
```

#### Para CPU
```bash
# En .env
DEVICE=cpu
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar todos los tests
pytest tests/

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

### Benchmarks
```bash
# Benchmark de rendimiento
python benchmarks/benchmark_face.py
python benchmarks/benchmark_sr.py
```

## 📊 Rendimiento

### Tiempos Aproximados (GPU RTX 3060)

| Operación | Tiempo | Memoria |
|-----------|--------|---------|
| Face Restoration | 2-5s | ~2GB |
| Super Resolution 2x | 5-10s | ~4GB |
| Super Resolution 4x | 15-30s | ~6GB |
| Pipeline Completo | 20-45s | ~8GB |

### Tiempos Aproximados (CPU i7)

| Operación | Tiempo | Memoria |
|-----------|--------|---------|
| Face Restoration | 10-20s | ~4GB |
| Super Resolution 2x | 30-60s | ~8GB |
| Super Resolution 4x | 2-3min | ~12GB |

## 🐛 Solución de Problemas

### Problema Común: "CUDA out of memory"
```bash
# Solución 1: Reducir tamaño de imagen
MAX_IMAGE_SIZE=1024

# Solución 2: Usar CPU
DEVICE=cpu

# Solución 3: Procesar una imagen a la vez
```

### Problema: Modelos no se descargan
```bash
# Verificar conexión a internet
# Configurar proxy si es necesario
# Intentar con VPN
```

### Problema: Aplicación no inicia
```bash
# Verificar entorno virtual activado
venv\Scripts\activate

# Reinstalar streamlit
pip install streamlit --upgrade

# Ejecutar en puerto diferente
streamlit run app.py --server.port 8502
```

## 🤝 Contribución

### Desarrollo Local
```bash
# Clonar repositorio
git clone <url-del-repo>
cd image-restoration-app

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Ejecutar tests
pytest tests/

# Ejecutar aplicación
streamlit run app.py
```

### Guías de Contribución
- Seguir PEP 8 para estilo de código
- Agregar tests para nuevas funcionalidades
- Actualizar documentación
- Usar commits descriptivos

## 📄 Licencias

### Código
- **MIT License**: Código fuente de la aplicación

### Modelos
- **GFPGAN**: MIT License
- **Stable Diffusion**: CreativeML Open RAIL-M
- **Diffusers**: Apache 2.0

**Importante**: Revisar términos de uso para aplicaciones comerciales.

## 🙏 Agradecimientos

- **GFPGAN**: Para restauración facial de alta calidad
- **Stability AI**: Por modelos de difusión accesibles
- **Hugging Face**: Por la plataforma de modelos
- **Streamlit**: Por el framework web

## 📞 Soporte

### Documentación
- [Guía de Instalación](setup_guide.md)
- [Arquitectura](architecture_plan.md)
- [Dependencias](requirements.md)

### Issues y Bugs
Reportar en: [GitHub Issues](https://github.com/usuario/repo/issues)

### Contacto
- Email: soporte@imagenesIA.com
- Discord: [Servidor de Comunidad](https://discord.gg/imagenesIA)

---

**⭐ Si te gusta el proyecto, ¡dale una estrella en GitHub!**

*Creado con ❤️ para la comunidad de procesamiento de imágenes*