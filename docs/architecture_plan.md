# Arquitectura del Proyecto: Aplicación de Restauración y Mejora de Imágenes con IA

## Resumen Ejecutivo

Este proyecto implementa una aplicación web local en Streamlit para restaurar y mejorar imágenes degradadas usando modelos de IA. La aplicación combina restauración facial con GFPGAN y super-resolución con modelos de difusión, ejecutándose completamente dentro del entorno virtual `venv`.

## Objetivos Principales

- **Restauración Facial**: Usar GFPGAN para mejorar calidad de rostros en imágenes
- **Super-Resolution**: Implementar mejora de resolución usando modelos de difusión
- **Interfaz Web**: Aplicación Streamlit intuitiva y responsive
- **Modularidad**: Arquitectura limpia separando UI, modelos y utilidades
- **Reproducibilidad**: Todo ejecutable desde el entorno virtual `venv`

## Arquitectura General

```
image_restoration_app/
├── app.py                          # Interfaz principal de Streamlit
├── requirements.txt                # Dependencias del proyecto
├── setup_venv.py                   # Script de configuración del entorno
├── README.md                       # Documentación completa
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── face_restoration.py     # Módulo GFPGAN
│   │   └── super_resolution.py     # Módulo de super-resolución
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_processing.py     # Utilidades de procesamiento
│   │   ├── validation.py           # Validaciones de entrada
│   │   └── error_handling.py       # Manejo de errores
│   └── config/
│       ├── __init__.py
│       └── settings.py             # Configuraciones globales
├── tests/
│   ├── __init__.py
│   ├── test_face_restoration.py
│   ├── test_super_resolution.py
│   └── test_integration.py
├── benchmarks/
│   ├── benchmark_face.py
│   └── benchmark_sr.py
└── assets/
    ├── sample_images/              # Imágenes de ejemplo
    └── models/                     # Modelos descargados (opcional)
```

## Tecnologías y Librerías

### Core
- **Streamlit**: Framework web para la interfaz
- **Python 3.8+**: Lenguaje base
- **PyTorch**: Framework de deep learning
- **Pillow**: Procesamiento básico de imágenes

### Modelos de IA
- **GFPGAN**: Para restauración facial (face restoration)
- **Diffusers**: Para super-resolución y mejoras generales
- **Transformers**: Modelos de Hugging Face

### Utilidades
- **NumPy**: Operaciones numéricas
- **OpenCV**: Procesamiento avanzado de imágenes
- **Requests**: Descarga de modelos
- **Pathlib**: Manejo de rutas

## Módulos Principales

### 1. Face Restoration (GFPGAN)

**Responsabilidades:**
- Detectar rostros en imágenes
- Aplicar restauración usando GFPGAN
- Manejar múltiples rostros por imagen
- Optimizar uso de memoria GPU/CPU

**API:**
```python
class FaceRestorer:
    def __init__(self, device: str = "auto")
    def restore_faces(self, image: Image, strength: float = 0.8) -> Image
    def detect_faces(self, image: Image) -> List[Dict]
```

### 2. Super Resolution (Diffusers)

**Responsabilidades:**
- Mejorar resolución de imágenes usando modelos de difusión
- Soporte para múltiples factores de escala (2x, 4x)
- Optimización de memoria para GPUs limitadas
- Procesamiento por lotes para eficiencia

**API:**
```python
class SuperResolver:
    def __init__(self, model_name: str = "stabilityai/stable-diffusion-x4-upscaler")
    def upscale(self, image: Image, scale_factor: int = 4, prompt: str = "") -> Image
    def batch_upscale(self, images: List[Image], **kwargs) -> List[Image]
```

### 3. Interfaz Streamlit

**Características:**
- Upload de imágenes múltiples
- Preview antes/después
- Controles de parámetros ajustables
- Barra de progreso para operaciones largas
- Manejo de errores con mensajes informativos
- Responsive design

**Páginas:**
- **Home**: Información general y carga de imágenes
- **Face Restoration**: Restauración facial dedicada
- **Super Resolution**: Mejora de resolución
- **Combined**: Pipeline completo (face + SR)

## Flujo de Trabajo

### 1. Configuración Inicial
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

### 2. Procesamiento de Imágenes

**Pipeline Básico:**
1. **Validación**: Verificar formato, tamaño, contenido
2. **Preprocesamiento**: Resize, normalización
3. **Procesamiento IA**: Aplicar modelos según selección
4. **Postprocesamiento**: Ajustes finales, metadata
5. **Export**: Guardar resultados con opciones

**Pipeline Completo (Combined):**
1. Detección automática de rostros
2. Restauración facial si se detectan rostros
3. Super-resolution general
4. Optimización final

## Validaciones y Manejo de Errores

### Validaciones de Entrada
- **Formatos soportados**: JPG, PNG, WebP
- **Tamaño máximo**: 10MB por imagen
- **Resolución máxima**: 2048x2048 píxeles
- **Contenido**: Verificación básica de imagen válida

### Manejo de Errores
- **GPU/CPU**: Detección automática y fallback
- **Memoria**: Monitoreo y optimizaciones automáticas
- **Modelos**: Descarga automática con reintentos
- **Timeouts**: Límites de tiempo para operaciones largas

## Optimizaciones de Rendimiento

### Memoria
- **Modelos cuantizados**: Uso de versiones optimizadas
- **Batch processing**: Procesamiento por lotes
- **CPU offloading**: Mover componentes entre GPU/CPU
- **Garbage collection**: Liberación manual de memoria

### Velocidad
- **Modelos Turbo**: Uso de versiones aceleradas
- **Cache inteligente**: Reutilización de modelos cargados
- **Multithreading**: Operaciones I/O en paralelo
- **Progressive loading**: Carga incremental de modelos

## Testing y Calidad

### Pruebas Unitarias
- **Modelos**: Funcionalidad básica de cada módulo
- **Utilidades**: Procesamiento de imágenes, validaciones
- **Integración**: Flujos completos end-to-end

### Benchmarks
- **Rendimiento**: Tiempo de procesamiento por imagen
- **Calidad**: Métricas PSNR, SSIM para comparación
- **Memoria**: Uso de RAM/VRAM durante ejecución
- **Escalabilidad**: Rendimiento con múltiples imágenes

## Configuración y Deployment

### Variables de Entorno
```bash
# .env
DEVICE=auto  # auto, cpu, cuda
MAX_IMAGE_SIZE=2048
MODEL_CACHE_DIR=./assets/models
LOG_LEVEL=INFO
```

### Docker (Opcional)
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## Métricas de Éxito

### Funcionales
- ✅ Restauración facial efectiva en imágenes con rostros
- ✅ Mejora de resolución 2x-4x sin pérdida de calidad
- ✅ Interfaz intuitiva y responsive
- ✅ Procesamiento de múltiples imágenes

### Técnicas
- ✅ Arquitectura modular y mantenible
- ✅ Cobertura de pruebas >80%
- ✅ Documentación completa
- ✅ Rendimiento optimizado para hardware limitado

### Usuario
- ✅ Fácil instalación y configuración
- ✅ Resultados de alta calidad
- ✅ Feedback visual durante procesamiento
- ✅ Opciones de export flexibles

## Riesgos y Mitigaciones

### Riesgos Técnicos
- **Dependencias de modelos**: Descarga automática con fallbacks
- **Compatibilidad hardware**: Detección automática y optimizaciones
- **Memoria insuficiente**: Procesamiento por partes y warnings

### Riesgos de Proyecto
- **Complejidad de GFPGAN**: Implementación modular con alternativas
- **Licencias de modelos**: Documentación clara de términos de uso
- **Mantenimiento**: Código bien estructurado y documentado

## Próximos Pasos

### Fase 1: MVP (2 semanas)
- [ ] Estructura básica del proyecto
- [ ] Módulo de face restoration con GFPGAN
- [ ] Interfaz Streamlit básica
- [ ] Tests básicos

### Fase 2: Funcionalidades Avanzadas (2 semanas)
- [ ] Super-resolution con diffusers
- [ ] Pipeline combinado
- [ ] Optimizaciones de rendimiento
- [ ] Benchmarks

### Fase 3: Pulido y Deployment (1 semana)
- [ ] UI/UX mejorada
- [ ] Documentación completa
- [ ] Scripts de instalación
- [ ] Testing exhaustivo

## Conclusión

Esta arquitectura proporciona una base sólida para una aplicación de restauración de imágenes con IA, balanceando facilidad de uso, rendimiento y mantenibilidad. La modularidad permite futuras extensiones y el enfoque en reproducibilidad asegura que cualquier usuario pueda ejecutar el proyecto en su entorno virtual.