"""
Benchmark: Medición de tiempo de respuesta de IurisLex v2
Ejecuta 50 queries variadas y genera reporte con percentiles, desglose de tiempos
"""

import json
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import subprocess
import sys
import os

import requests


# Configuración
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 15  # segundos
BENCHMARK_OUTPUT = Path(__file__).parent / "BENCHMARK_BASELINE.md"
BENCHMARK_JSON = Path(__file__).parent / "benchmark_results.json"


# Queries de prueba: 50 queries en 5 categorías
QUERIES = {
    "búsqueda_simple": [
        "¿Cuáles son los derechos fundamentales?",
        "¿Qué es la soberanía nacional?",
        "¿Qué dice sobre la igualdad?",
        "Habeas corpus",
        "Libertad de expresión",
    ],
    "búsqueda_compleja": [
        "¿Cuáles son los derechos fundamentales y cómo se protegen constitucionalmente?",
        "¿Qué procedimientos existen para proteger los derechos cuando están siendo vulnerados?",
        "Explica la estructura y funciones de las tres ramas del poder público",
        "¿Cuál es el rol del Congreso en la aprobación de leyes y tratados internacionales?",
        "¿Qué mecanismos constitucionales existen para proteger los derechos de las minorías?",
    ],
    "búsqueda_con_typos": [
        "¿Qué es la soveranía naciional?",  # typos: soberanía
        "habeas corpis",  # typo: corpus
        "libertad de expresion",  # typo: expresión
        "derechos fundamntales",  # typo: fundamentales
        "consitución",  # typo: constitución
    ],
    "búsqueda_multiple_artículos": [
        "¿Qué artículos hablan sobre los derechos de los ciudadanos?",
        "¿Qué diferencia hay entre la nación y el territorio nacional?",
        "¿Cuáles son los principios que rigen la actividad estatal?",
        "¿Qué dicen los artículos sobre la participación política?",
        "¿Cómo está organizada la rama ejecutiva?",
    ],
    "búsqueda_específica": [
        "Artículo 1",
        "Artículo 19",
        "Artículo 44",
        "Artículo 86",
        "Artículo 365",
    ],
}

# Aplanar queries para iterar
ALL_QUERIES = []
for category, queries_list in QUERIES.items():
    for query in queries_list:
        ALL_QUERIES.append((category, query))


def check_api_running() -> bool:
    """Verifica si la API está corriendo."""
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def execute_query(query: str, timeout: int = TIMEOUT) -> Dict[str, Any]:
    """
    Ejecuta una query contra el endpoint /api/consulta.
    Retorna: {
        'query': str,
        'status': 'success'|'timeout'|'error',
        'response_time_ms': int,
        'api_response_time_ms': int,  # Tiempo reportado por API
        'error': str|None,
        'article_found': str|None
    }
    """
    payload = {
        "query": query,
        "include_analysis": True,
        "include_case": True
    }
    
    start_time = time.perf_counter()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/consulta",
            json=payload,
            timeout=timeout
        )
        
        elapsed_ms = round((time.perf_counter() - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'query': query,
                'status': 'success',
                'response_time_ms': elapsed_ms,
                'api_response_time_ms': data.get('metadata', {}).get('response_time_ms', 0),
                'article_found': data.get('primary_article', {}).get('number'),
                'confidence': data.get('response_validation', {}).get('confidence_score'),
                'error': None
            }
        else:
            return {
                'query': query,
                'status': 'error',
                'response_time_ms': elapsed_ms,
                'api_response_time_ms': 0,
                'error': f"Status {response.status_code}: {response.text[:200]}",
                'article_found': None,
                'confidence': 0
            }
            
    except requests.Timeout:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000)
        return {
            'query': query,
            'status': 'timeout',
            'response_time_ms': elapsed_ms,
            'api_response_time_ms': 0,
            'error': f"Timeout después de {timeout}s",
            'article_found': None,
            'confidence': 0
        }
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000)
        return {
            'query': query,
            'status': 'error',
            'response_time_ms': elapsed_ms,
            'api_response_time_ms': 0,
            'error': str(e),
            'article_found': None,
            'confidence': 0
        }


def calculate_percentiles(times: List[int]) -> Dict[str, float]:
    """Calcula percentiles p50, p75, p95, p99."""
    if not times:
        return {}
    
    sorted_times = sorted(times)
    n = len(sorted_times)
    
    def percentile(p):
        idx = int((p / 100) * (n - 1))
        return sorted_times[idx]
    
    return {
        'p50': percentile(50),
        'p75': percentile(75),
        'p95': percentile(95),
        'p99': percentile(99),
        'min': min(sorted_times),
        'max': max(sorted_times),
        'mean': round(statistics.mean(sorted_times), 1),
        'stdev': round(statistics.stdev(sorted_times), 1) if len(sorted_times) > 1 else 0,
    }


def generate_markdown_report(results: List[Dict], stats: Dict) -> str:
    """Genera reporte en Markdown."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    success_count = len([r for r in results if r['status'] == 'success'])
    timeout_count = len([r for r in results if r['status'] == 'timeout'])
    error_count = len([r for r in results if r['status'] == 'error'])
    
    success_times = [r['response_time_ms'] for r in results if r['status'] == 'success']
    
    report = f"""# Benchmark de Tiempo de Respuesta - IurisLex v2

**Generado:** {timestamp}

## Resumen Ejecutivo

- **Total de queries:** {len(results)}
- **Exitosas:** {success_count} ({100*success_count/len(results):.0f}%)
- **Timeout:** {timeout_count} ({100*timeout_count/len(results):.0f}%)
- **Error:** {error_count} ({100*error_count/len(results):.0f}%)

### Métricas de Tiempo (queries exitosas)

| Métrica | Valor (ms) |
|---------|-----------|
| **Media** | {stats['response_times']['mean']:.0f} |
| **Mediana (p50)** | {stats['response_times']['p50']:.0f} |
| **P75** | {stats['response_times']['p75']:.0f} |
| **P95** | {stats['response_times']['p95']:.0f} |
| **P99** | {stats['response_times']['p99']:.0f} |
| **Mín** | {stats['response_times']['min']:.0f} |
| **Máx** | {stats['response_times']['max']:.0f} |
| **Desv Est** | {stats['response_times']['stdev']:.0f} |

---

## Resultados por Categoría

"""
    
    for category in QUERIES.keys():
        category_results = [r for r in results if r['category'] == category]
        category_times = [r['response_time_ms'] for r in category_results if r['status'] == 'success']
        
        if category_times:
            stats_cat = calculate_percentiles(category_times)
            report += f"""### {category.upper()}

- **Queries:** {len(category_results)}
- **Exitosas:** {len(category_times)}
- **Media:** {stats_cat['mean']:.0f}ms
- **P95:** {stats_cat['p95']:.0f}ms

"""
    
    report += """---

## Resultados Detallados

| # | Categoría | Query | Status | Tiempo (ms) | Artículo | Confianza |
|---|-----------|-------|--------|------------|---------|-----------|
"""
    
    for i, result in enumerate(results, 1):
        time_ms = result['response_time_ms']
        status = result['status']
        article = result['article_found'] or "N/A"
        confidence = f"{result['confidence']*100:.0f}%" if result['confidence'] else "N/A"
        query_short = result['query'][:50] + "..." if len(result['query']) > 50 else result['query']
        
        report += f"| {i} | {result['category']} | {query_short} | {status} | {time_ms} | {article} | {confidence} |\n"
    
    report += f"""

---

## Interpretación

- **Línea Base:** Este benchmark establece la línea base para las optimizaciones
- **Meta Post-Optimización:** Reducir tiempo medio a <3000ms (40-50% mejora)
- **Queries Exitosas:** Se considera solo estas para cálculo de percentiles
- **Outliers:** Revisar queries con tiempo > p95 para identificar casos problemáticos

---

## Próximos Pasos

1. Implementar **Fase 1: Paralelizar búsquedas** (estimado -400-900ms)
2. Implementar **Fase 2: Caché de búsquedas** (estimado -500-1000ms para repetidas)
3. Implementar **Fase 3: Timeout Ollama + fallback** (protección contra bloqueos)
4. Re-ejecutar benchmark para comparar mejoras

**Archivo generado:** {BENCHMARK_JSON}
"""
    
    return report


def main():
    """Ejecuta el benchmark completo."""
    print("=" * 70)
    print("BENCHMARK: Medición de Tiempo de Respuesta - IurisLex v2")
    print("=" * 70)
    
    # Verificar que API esté corriendo
    print("\n✓ Verificando si API está disponible...")
    if not check_api_running():
        print("❌ ERROR: API no está corriendo en http://localhost:8000")
        print("\nPor favor, inicia la API con:")
        print("  uvicorn app.api.main:app --reload")
        sys.exit(1)
    
    print("✓ API disponible\n")
    
    # Ejecutar queries
    print(f"Ejecutando {len(ALL_QUERIES)} queries benchmark...")
    print("(Esto puede tomar varios minutos)\n")
    
    results = []
    start_benchmark = time.perf_counter()
    
    for i, (category, query) in enumerate(ALL_QUERIES, 1):
        sys.stdout.write(f"\r[{i}/{len(ALL_QUERIES)}] Ejecutando: {query[:60]:<60}")
        sys.stdout.flush()
        
        result = execute_query(query)
        result['category'] = category
        results.append(result)
    
    total_time = time.perf_counter() - start_benchmark
    print(f"\n\n✓ Benchmark completado en {total_time:.1f}s\n")
    
    # Calcular estadísticas
    success_times = [r['response_time_ms'] for r in results if r['status'] == 'success']
    
    stats = {
        'total_queries': len(results),
        'successful': len(success_times),
        'response_times': calculate_percentiles(success_times) if success_times else {},
        'benchmark_duration_seconds': round(total_time, 1),
        'timestamp': datetime.now().isoformat(),
    }
    
    # Guardar JSON con resultados detallados
    with open(BENCHMARK_JSON, 'w') as f:
        json.dump({'stats': stats, 'results': results}, f, indent=2)
    print(f"✓ Resultados detallados guardados en: {BENCHMARK_JSON}")
    
    # Generar y guardar reporte Markdown
    report = generate_markdown_report(results, stats)
    with open(BENCHMARK_OUTPUT, 'w') as f:
        f.write(report)
    print(f"✓ Reporte generado en: {BENCHMARK_OUTPUT}\n")
    
    # Mostrar resumen en consola
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Total de queries:     {len(results)}")
    print(f"Exitosas:             {len(success_times)}")
    print(f"Timeouts/Errores:     {len(results) - len(success_times)}\n")
    
    if success_times:
        print("Tiempos de Respuesta (queries exitosas):")
        print(f"  Mín:                 {min(success_times)}ms")
        print(f"  Media:               {statistics.mean(success_times):.0f}ms")
        print(f"  Mediana (p50):       {sorted(success_times)[len(success_times)//2]:.0f}ms")
        print(f"  P95:                 {sorted(success_times)[int(len(success_times)*0.95)]:.0f}ms")
        print(f"  Máx:                 {max(success_times)}ms")
        print(f"\n  Desv Estándar:       {statistics.stdev(success_times):.0f}ms")
    
    print("\n" + "=" * 70)
    print("⚠️  Esta es tu LÍNEA BASE de rendimiento.")
    print("Después de optimizaciones, ejecuta este script nuevamente para comparar.")
    print("=" * 70)


if __name__ == "__main__":
    main()
