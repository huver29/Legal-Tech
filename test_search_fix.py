#!/usr/bin/env python3
"""
Script de prueba para verificar que la búsqueda semántica funciona correctamente.
"""
import sys
import json
import requests
from pathlib import Path

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

BASE_URL = "http://127.0.0.1:8000"

def print_header(title):
    """Imprime un encabezado de prueba."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_consulta(query: str):
    """Prueba el endpoint /api/consulta."""
    print(f"📝 Consultando: '{query}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/consulta",
            json={"query": query},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Artículo encontrado: {data['article']['number']} - {data['article']['titulo_nombre']}")
        print(f"✓ Tipo de búsqueda: {data['search']['search_type']}")
        print(f"✓ Score de relevancia: {data['search']['primary_score']}")
        print(f"✓ Tiempo de respuesta: {data['response_time_ms']}ms")
        
        # Mostrar el texto del artículo
        article_text = data['article']['texto'][:200]
        print(f"\n📄 Artículo ({data['article']['number']}):")
        print(f"   {article_text}...\n")
        
        # Mostrar artículos relacionados
        if data['related']:
            print(f"📎 Artículos relacionados:")
            for rel in data['related']:
                print(f"   - Art. {rel['number']}: {rel['titulo_nombre']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecuta pruebas."""
    print_header("🔍 PRUEBAS DE BÚSQUEDA - IurisLex v2 CON EMBEDDINGS")
    
    # Verificar conexión
    print("Verificando conexión al servidor...")
    try:
        resp = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        print(f"✓ Servidor disponible en {BASE_URL}\n")
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("Asegúrate de que uvicorn está ejecutándose en otra terminal")
        return False
    
    # Pruebas de búsqueda
    test_cases = [
        "¿Cuál es mi derecho a la vida?",
        "artículo 1",
        "libertad de expresión",
        "educación",
        "derechos fundamentales",
        "justicia",
        "constitución",
        "derecho al trabajo",
        "familia",
        "protección de menores"
    ]
    
    print_header("🧪 EJECUTANDO PRUEBAS DE BÚSQUEDA")
    
    passed = 0
    failed = 0
    
    for query in test_cases:
        if test_consulta(query):
            passed += 1
        else:
            failed += 1
        print("-" * 60)
    
    # Resumen
    print_header("📊 RESUMEN DE RESULTADOS")
    print(f"✓ Pruebas exitosas: {passed}/{len(test_cases)}")
    print(f"❌ Pruebas fallidas: {failed}/{len(test_cases)}")
    print(f"📈 Tasa de éxito: {(passed/len(test_cases)*100):.1f}%")
    
    if passed == len(test_cases):
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("La búsqueda semántica está funcionando correctamente.")
        return True
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los detalles arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
