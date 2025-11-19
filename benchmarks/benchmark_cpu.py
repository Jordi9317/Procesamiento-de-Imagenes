#!/usr/bin/env python3
"""
Benchmark de rendimiento para Image Restoration App (CPU)
Mide tiempos de procesamiento y uso de recursos.
"""

import time
import psutil
import os
from PIL import Image
import numpy as np
import sys
import logging

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from image_pipeline import ImageRestorationPipeline
from validation import ImageValidator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CPUBenchmark:
    """Clase para ejecutar benchmarks de CPU"""

    def __init__(self):
        self.pipeline = ImageRestorationPipeline()
        self.process = psutil.Process(os.getpid())

    def create_test_image(self, size=(512, 512), with_face=False):
        """Crea una imagen de prueba"""
        if with_face:
            # Crear imagen con patrón que simule un rostro
            img_array = np.full((size[1], size[0], 3), 100, dtype=np.uint8)

            # Agregar ovalo para simular rostro
            center_x, center_y = size[0] // 2, size[1] // 2
            face_width, face_height = size[0] // 3, size[1] // 2

            y, x = np.ogrid[:size[1], :size[0]]
            mask = ((x - center_x) / face_width) ** 2 + ((y - center_y) / face_height) ** 2 <= 1
            img_array[mask] = 180  # Color más claro para el "rostro"

            return Image.fromarray(img_array)
        else:
            # Imagen aleatoria
            img_array = np.random.randint(0, 255, (size[1], size[0], 3), dtype=np.uint8)
            return Image.fromarray(img_array)

    def get_memory_usage(self):
        """Obtiene uso de memoria en MB"""
        memory_info = self.process.memory_info()
        return memory_info.rss / (1024 * 1024)  # MB

    def get_cpu_percent(self):
        """Obtiene uso de CPU"""
        return self.process.cpu_percent(interval=0.1)

    def benchmark_face_enhancement(self, image_sizes=[(256, 256), (512, 512), (1024, 1024)]):
        """Benchmark de mejora facial"""
        logger.info("=== Benchmark: Face Enhancement ===")

        results = []

        for size in image_sizes:
            logger.info(f"Probando tamaño: {size[0]}x{size[1]}")

            # Crear imagen de prueba
            test_image = self.create_test_image(size, with_face=True)

            # Medir memoria inicial
            initial_memory = self.get_memory_usage()

            # Ejecutar procesamiento
            start_time = time.time()

            options = {
                'face_enhancement': True,
                'enhancement_strength': 0.7,
                'super_resolution': False
            }

            result, metadata = self.pipeline.process_image(test_image, options)

            processing_time = time.time() - start_time
            final_memory = self.get_memory_usage()
            memory_used = final_memory - initial_memory

            result_data = {
                'operation': 'face_enhancement',
                'image_size': size,
                'processing_time': processing_time,
                'memory_used_mb': memory_used,
                'faces_detected': metadata.get('face_count', 0),
                'success': result is not None
            }

            results.append(result_data)
            logger.info(f"  ✅ {size[0]}x{size[1]}: {processing_time:.2f}s, {memory_used:.1f}MB")
        return results

    def benchmark_super_resolution(self, base_size=(256, 256), scale_factors=[2, 3, 4]):
        """Benchmark de super-resolución"""
        logger.info("=== Benchmark: Super Resolution ===")

        results = []

        for scale in scale_factors:
            logger.info(f"Probando escala: {scale}x")

            # Crear imagen de prueba
            test_image = self.create_test_image(base_size)

            # Medir memoria inicial
            initial_memory = self.get_memory_usage()

            # Ejecutar procesamiento
            start_time = time.time()

            options = {
                'face_enhancement': False,
                'super_resolution': True,
                'scale_factor': scale,
                'interpolation_method': 'lanczos'
            }

            result, metadata = self.pipeline.process_image(test_image, options)

            processing_time = time.time() - start_time
            final_memory = self.get_memory_usage()
            memory_used = final_memory - initial_memory

            result_data = {
                'operation': 'super_resolution',
                'scale_factor': scale,
                'input_size': base_size,
                'output_size': result.size if result else None,
                'processing_time': processing_time,
                'memory_used_mb': memory_used,
                'success': result is not None
            }

            results.append(result_data)
            logger.info(f"  ✅ {scale}x: {processing_time:.2f}s, {memory_used:.1f}MB")
        return results

    def benchmark_pipeline_complete(self, image_sizes=[(256, 256), (512, 512)]):
        """Benchmark del pipeline completo"""
        logger.info("=== Benchmark: Pipeline Completo ===")

        results = []

        for size in image_sizes:
            logger.info(f"Probando pipeline completo: {size[0]}x{size[1]}")

            # Crear imagen de prueba
            test_image = self.create_test_image(size, with_face=True)

            # Medir memoria inicial
            initial_memory = self.get_memory_usage()

            # Ejecutar procesamiento completo
            start_time = time.time()

            options = {
                'face_enhancement': True,
                'enhancement_strength': 0.7,
                'super_resolution': True,
                'scale_factor': 2,
                'interpolation_method': 'lanczos'
            }

            result, metadata = self.pipeline.process_image(test_image, options)

            processing_time = time.time() - start_time
            final_memory = self.get_memory_usage()
            memory_used = final_memory - initial_memory

            result_data = {
                'operation': 'pipeline_complete',
                'image_size': size,
                'processing_time': processing_time,
                'memory_used_mb': memory_used,
                'faces_detected': metadata.get('face_count', 0),
                'steps_applied': metadata.get('steps_applied', []),
                'success': result is not None
            }

            results.append(result_data)
            logger.info(f"  ✅ {size[0]}x{size[1]}: {processing_time:.2f}s, {memory_used:.1f}MB")
        return results

    def run_all_benchmarks(self):
        """Ejecuta todos los benchmarks"""
        logger.info("🚀 Iniciando benchmarks completos de CPU")
        logger.info("=" * 60)

        # Información del sistema
        system_info = {
            'cpu_count': psutil.cpu_count(),
            'cpu_logical': psutil.cpu_count(logical=True),
            'memory_total': psutil.virtual_memory().total / (1024**3),  # GB
            'platform': sys.platform
        }

        logger.info("Información del Sistema:")
        logger.info(f"  CPU cores: {system_info['cpu_count']}")
        logger.info(f"  CPU threads: {system_info['cpu_logical']}")
        logger.info(f"  Memoria total: {system_info['memory_total']:.1f}GB")
        logger.info(f"  Plataforma: {system_info['platform']}")

        all_results = {
            'system_info': system_info,
            'face_enhancement': self.benchmark_face_enhancement(),
            'super_resolution': self.benchmark_super_resolution(),
            'pipeline_complete': self.benchmark_pipeline_complete(),
            'timestamp': time.time()
        }

        # Imprimir resumen
        self.print_summary(all_results)

        return all_results

    def print_summary(self, results):
        """Imprime resumen de resultados"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RESUMEN DE BENCHMARKS")
        logger.info("=" * 60)

        # Face Enhancement
        fe_results = results['face_enhancement']
        if fe_results:
            logger.info("🎭 Face Enhancement:")
            for result in fe_results:
                status = "✅" if result['success'] else "❌"
                logger.info(f"  {status} {result['image_size'][0]}x{result['image_size'][1]}: {result['processing_time']:.2f}s, {result['memory_used_mb']:.1f}MB")

        # Super Resolution
        sr_results = results['super_resolution']
        if sr_results:
            logger.info("🔍 Super Resolution:")
            for result in sr_results:
                status = "✅" if result['success'] else "❌"
                logger.info(f"  {status} {result['scale_factor']}x: {result['processing_time']:.2f}s, {result['memory_used_mb']:.1f}MB")

        # Pipeline Completo
        pc_results = results['pipeline_complete']
        if pc_results:
            logger.info("🔄 Pipeline Completo:")
            for result in pc_results:
                status = "✅" if result['success'] else "❌"
                logger.info(f"  {status} {result['image_size'][0]}x{result['image_size'][1]}: {result['processing_time']:.2f}s, {result['memory_used_mb']:.1f}MB")

        # Estadísticas generales
        all_times = []
        all_memories = []

        for category in ['face_enhancement', 'super_resolution', 'pipeline_complete']:
            for result in results[category]:
                if result['success']:
                    all_times.append(result['processing_time'])
                    all_memories.append(result['memory_used_mb'])

        if all_times:
            logger.info("\n📈 Estadísticas Generales:")
            logger.info(f"  Tiempo promedio: {sum(all_times)/len(all_times):.2f}s")
            logger.info(f"  Tiempo total: {sum(all_times):.2f}s")
            logger.info(f"  Memoria promedio: {sum(all_memories)/len(all_memories):.1f}MB")
            logger.info(f"  Memoria máxima: {max(all_memories):.1f}MB")
def main():
    """Función principal"""
    try:
        benchmark = CPUBenchmark()
        results = benchmark.run_all_benchmarks()

        # Guardar resultados (opcional)
        import json
        output_file = "benchmark_results.json"
        with open(output_file, 'w') as f:
            # Convertir tuplas a listas para JSON
            json_results = results.copy()
            for category in ['face_enhancement', 'super_resolution', 'pipeline_complete']:
                for result in json_results[category]:
                    if 'image_size' in result and isinstance(result['image_size'], tuple):
                        result['image_size'] = list(result['image_size'])
                    if 'input_size' in result and isinstance(result['input_size'], tuple):
                        result['input_size'] = list(result['input_size'])
                    if 'output_size' in result and result['output_size'] is not None and isinstance(result['output_size'], tuple):
                        result['output_size'] = list(result['output_size'])

            json.dump(json_results, f, indent=2, default=str)

        logger.info(f"\n💾 Resultados guardados en: {output_file}")

    except Exception as e:
        logger.error(f"Error ejecutando benchmarks: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)