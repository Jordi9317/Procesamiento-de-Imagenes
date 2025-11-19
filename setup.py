#!/usr/bin/env python3
"""
Script de instalación automática para Image Restoration App (CPU)
Configura el entorno virtual y instala todas las dependencias necesarias.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n* {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error en {description}: {e}")
        print(f"Output: {e.output}")
        return False

def check_python_version():
    """Verifica que Python sea compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} no es compatible. Se requiere Python 3.8+")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def create_venv():
    """Crea entorno virtual"""
    if os.path.exists("venv"):
        print("Entorno virtual ya existe")
        return True

    command = f'"{sys.executable}" -m venv venv'
    return run_command(command, "Creando entorno virtual")

def activate_venv():
    """Activa el entorno virtual"""
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "venv/bin/activate"

    if not os.path.exists(activate_script):
        print("❌ Script de activación no encontrado")
        return False

    print(f"Para activar manualmente: {activate_script}")
    return True

def install_pytorch_cpu():
    """Instala PyTorch optimizado para CPU"""
    command = f'"{sys.executable}" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu'
    return run_command(command, "Instalando PyTorch CPU")

def install_core_dependencies():
    """Instala dependencias principales"""
    packages = [
        "streamlit",
        "Pillow",
        "numpy",
        "opencv-python",
        "requests",
        "tqdm",
        "python-dotenv",
        "scipy",
        "matplotlib"
    ]

    command = f'"{sys.executable}" -m pip install {" ".join(packages)}'
    return run_command(command, "Instalando dependencias core")

def install_face_detection():
    """Instala librerías para detección facial"""
    packages = [
        "scikit-image"
    ]

    command = f'"{sys.executable}" -m pip install {" ".join(packages)}'
    return run_command(command, "Instalando detección facial")

def test_installation():
    """Verifica que la instalación sea correcta"""
    print("\nProbando instalacion...")

    test_code = """
import sys
try:
    import torch
    import streamlit as st
    import cv2
    import numpy as np
    from PIL import Image
    # import face_recognition  # Removido por compatibilidad
    print("SUCCESS: Todas las dependencias instaladas correctamente")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA disponible: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
"""

    try:
        result = subprocess.run([sys.executable, "-c", test_code],
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error en testing: {e}")
        print(f"Stderr: {e.stderr}")
        return False

def create_env_file():
    """Crea archivo .env con configuración por defecto"""
    env_content = """# Configuración de Image Restoration App

# Dispositivo (auto detecta CPU)
DEVICE=cpu

# Límites de procesamiento
MAX_IMAGE_SIZE=2048
MAX_FILE_SIZE_MB=10

# Directorios
OUTPUT_DIR=./output
LOG_DIR=./logs

# Configuración de procesamiento
FACE_DETECTION_CONFIDENCE=0.6
SUPER_RESOLUTION_SCALE=2

# Logging
LOG_LEVEL=INFO
"""

    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("Archivo .env creado")
        return True
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return False

def main():
    """Función principal de instalación"""
    print("Instalacion de Image Restoration App (CPU)")
    print("=" * 50)

    # Verificar Python
    if not check_python_version():
        return False

    # Crear entorno virtual
    if not create_venv():
        return False

    # Activar entorno (informativo)
    activate_venv()

    # Instalar PyTorch CPU
    if not install_pytorch_cpu():
        return False

    # Instalar dependencias core
    if not install_core_dependencies():
        return False

    # Instalar detección facial
    if not install_face_detection():
        return False

    # Crear archivo de configuración
    create_env_file()

    # Probar instalación
    if not test_installation():
        return False

    print("\n" + "=" * 50)
    print("Instalacion completada exitosamente!")
    print("\nPara usar la aplicación:")
    print("1. Activa el entorno: venv\\Scripts\\activate (Windows) o source venv/bin/activate (Linux/Mac)")
    print("2. Ejecuta: streamlit run app.py")
    print("3. Abre http://localhost:8501 en tu navegador")
    print("\nDocumentacion: README.md")
    print("Configuracion: .env")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)