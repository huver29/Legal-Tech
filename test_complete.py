#!/usr/bin/env python3
"""Test directo del endpoint /api/consulta"""
import json
from pathlib import Path
import sys

# Agregar el directorio de la app al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Importar directamente las funciones de la app
from app.api.main import find_article, build_comparison, build_analysis, build_case, normalize, ARTICLES, ARTICLES_BY_NUMBER

print("=" * 60)
print("TEST DE BÚSQUEDA Y PROCESAMIENTO")
print("=" * 60)

# Test 1: Verificar carga de artículos
print(f"\n[TEST 1] Artículos cargados: {len(ARTICLES)}")
if len(ARTICLES) == 0:
    print("[FAIL] No se cargaron artículos")
    sys.exit(1)
else:
    print(f"[PASS] Se cargaron {len(ARTICLES)} artículos correctamente")

# Test 2: Verificar índice por número
print(f"\n[TEST 2] Artículos por número indexados: {len(ARTICLES_BY_NUMBER)}")
print(f"[INFO] Primeros números: {sorted(ARTICLES_BY_NUMBER.keys())[:10]}")

# Test 3: Búsqueda de ejemplo
queries = ["1", "libertad", "derecho", "artículo 2"]
print(f"\n[TEST 3] Búsquedas de prueba:")

for query in queries:
    print(f"\n  Buscando: '{query}'")
    article = find_article(query)
    if article:
        print(f"  [FOUND] Art. {article['number']}: {article['articulo']}")
        print(f"          Texto: {article['texto'][:100]}...")
    else:
        print(f"  [NOT FOUND] No se encontró artículo")

# Test 4: Procesamiento completo de una consulta
print(f"\n[TEST 4] Procesamiento completo de consulta:")
query = "libertad"
print(f"  Query: '{query}'")

article = find_article(query)
if not article:
    print(f"  [FAIL] find_article retornó vacío")
    sys.exit(1)

print(f"  [OK] Artículo encontrado: Art. {article['number']}")

related = build_comparison(article)
print(f"  [OK] Relacionados encontrados: {len(related)}")

analysis = build_analysis(article, related)
print(f"  [OK] Análisis generado con {len(analysis)} campos")

case = build_case(article)
print(f"  [OK] Caso generado con {len(case)} campos")

# Test 5: Probar endpoint HTTP
print(f"\n[TEST 5] Test del endpoint HTTP:")
print(f"  Nota: asegúrate de que la app esté corriendo en http://127.0.0.1:8000")
print(f"  Comando: python -m uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000")

print("\n" + "=" * 60)
print("FIN DE TEST")
print("=" * 60)
