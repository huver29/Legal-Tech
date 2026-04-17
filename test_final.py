#!/usr/bin/env python3
"""Test final rápido del proyecto reconstruido"""
import sys
from pathlib import Path

# Agregar proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.api.main import (
        ARTICLES, ARTICLES_BY_NUMBER, find_article,
        build_comparison, build_analysis, build_case, normalize
    )
    
    print("\n" + "="*60)
    print("TEST FINAL - PROYECTO RECONSTRUIDO")
    print("="*60)
    
    # Test 1: Artículos cargados
    print(f"\n[TEST 1] Artículos cargados: {len(ARTICLES)}")
    assert len(ARTICLES) > 0, "No se cargaron artículos"
    print("✓ PASS")
    
    # Test 2: Índice por número
    print(f"\n[TEST 2] Artículos indexados: {len(ARTICLES_BY_NUMBER)}")
    assert len(ARTICLES_BY_NUMBER) > 0, "Índice vacío"
    print("✓ PASS")
    
    # Test 3: Búsqueda por número
    print("\n[TEST 3] Búsqueda por número '1'")
    art = find_article("1")
    assert art and art['number'] == '1', "No encontró Art. 1"
    print(f"✓ Encontrado: {art['articulo']}")
    
    # Test 4: Búsqueda por texto
    print("\n[TEST 4] Búsqueda por texto 'libertad'")
    art = find_article("libertad")
    assert art and art, "No encontró artículo"
    print(f"✓ Encontrado: Art. {art['number']} - {art['titulo_nombre']}")
    
    # Test 5: Comparación
    print("\n[TEST 5] Artículos relacionados")
    related = build_comparison(art)
    print(f"✓ {len(related)} artículos relacionados encontrados")
    
    # Test 6: Análisis
    print("\n[TEST 6] Análisis generado")
    analysis = build_analysis(art, related)
    assert len(analysis) == 5, "Campos de análisis faltantes"
    print(f"✓ {len(analysis)} campos de análisis")
    
    # Test 7: Caso
    print("\n[TEST 7] Caso simulado")
    case = build_case(art)
    assert len(case) == 2, "Campos de caso faltantes"
    print(f"✓ Caso con {len(case)} campos")
    
    print("\n" + "="*60)
    print("TODOS LOS TESTS PASARON")
    print("="*60)
    print("\nPuedes ejecutar:")
    print("  python -m uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000")
    print("\nLuego abre:")
    print("  http://127.0.0.1:8000/")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
