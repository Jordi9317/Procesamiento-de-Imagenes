#!/usr/bin/env python3
"""
Script para convertir archivos a UTF-8 y corregir problemas de encoding.
"""

import os
import glob
from pathlib import Path

def convert_file_to_utf8(file_path):
    """Convierte un archivo a UTF-8 si es posible."""
    try:
        # Leer como binario
        with open(file_path, 'rb') as f:
            content = f.read()

        # Intentar decodificar como UTF-8
        try:
            text = content.decode('utf-8')
            print(f"INFO: {file_path} ya esta en UTF-8")
            return True
        except UnicodeDecodeError:
            # Intentar con latin-1 (common Windows encoding)
            try:
                text = content.decode('latin-1')
                utf8_content = text.encode('utf-8')

                # Escribir de vuelta como UTF-8
                with open(file_path, 'wb') as f:
                    f.write(utf8_content)

                print(f"SUCCESS: Convertido {file_path} de latin-1 a UTF-8")
                return True
            except Exception as e:
                print(f"ERROR: Error convirtiendo {file_path}: {e}")
                return False

    except Exception as e:
        print(f"ERROR: Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal."""
    # Archivos a convertir
    patterns = [
        "*.md",
        "*.txt",
        "*.py",
        "*.ipynb",
        "*.json",
        "*.yaml",
        "*.yml"
    ]

    converted = 0
    errors = 0

    for pattern in patterns:
        for file_path in glob.glob(f"**/{pattern}", recursive=True):
            if convert_file_to_utf8(file_path):
                converted += 1
            else:
                errors += 1

    print(f"\nSUMMARY: {converted} archivos convertidos, {errors} errores")

if __name__ == "__main__":
    main()