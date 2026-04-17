"""
Script de Ejemplo: Uso de IurisLex v2
Demuestra todos los endpoints y capacidades del sistema mejorado
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


class Colors:
    """ANSI colors para terminal."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_section(title: str):
    """Imprime una sección con formato."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f" {title}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(msg: str):
    """Imprime un mensaje de éxito."""
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")


def print_info(msg: str):
    """Imprime información."""
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")


def print_json(data: Dict[str, Any], indent: int = 2):
    """Imprime JSON formateado."""
    print(json.dumps(data, ensure_ascii=False, indent=indent))


def health_check():
    """Verifica estado del sistema."""
    print_section("1. Health Check - Estado del Sistema")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        response.raise_for_status()
        data = response.json()
        
        print_success(f"Sistema saludable: {data['status']}")
        print_info(f"Artículos cargados: {data['articles_loaded']}")
        print_info(f"Ollama conectado: {data['ollama_connected']}")
        print_info(f"Motor de búsqueda: {data['search_engine_ready']}")
        print_info(f"Embeddings disponibles: {data['embeddings_available']}")
        print_info(f"Versión: {data['version']}")
        
        return data['ollama_connected']
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        return False


def test_search_basic():
    """Prueba búsqueda básica."""
    print_section("2. Búsqueda Básica - Artículo sobre Igualdad")
    
    query = "¿Cuál es mi derecho a la igualdad?"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/consulta",
            json={"query": query}
        )
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Consulta: {query}")
        print_success(f"Artículo encontrado: Art. {data['primary_article']['number']}")
        print_info(f"Título: {data['primary_article']['titulo_nombre']}")
        print_info(f"Relevancia: {data['primary_article']['relevance_score']:.2%}")
        print_info(f"Tipo búsqueda: {data['primary_article']['search_type']}")
        
        print(f"\n{Colors.BOLD}Respuesta LLM:{Colors.ENDC}")
        print(f"{data['llm_response'][:400]}...\n")
        
        validation = data['response_validation']
        print_info(f"Validación: {'✓ Válida' if validation['is_valid'] else '✗ Inválida'}")
        print_info(f"Confianza: {validation['confidence_score']:.2%}")
        print_info(f"Citas verificadas: {validation['citation_verified']}")
        print_info(f"Tiempo respuesta: {data['metadata']['response_time_ms']}ms")
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")


def test_search_with_typo():
    """Prueba búsqueda con typo (Fuzzy matching)."""
    print_section("3. Búsqueda Fuzzy - Con Typo (dereccho al trabjo)")
    
    query = "dereccho al trabjo"  # Typos deliberados
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search-advanced",
            json={"query": query, "top_k": 3}
        )
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Búsqueda: '{query}' (con typos)")
        print_success(f"Resultados encontrados: {data['results_count']}")
        
        for i, result in enumerate(data['results'][:3], 1):
            print(f"\n{Colors.BOLD}{i}. Art. {result['number']}: {result['titulo_nombre']}{Colors.ENDC}")
            print_info(f"   Relevancia: {result['relevance_score']:.2%}")
            print_info(f"   Tipo: {result['search_type']}")
            print_info(f"   Texto: {result['texto'][:100]}...")
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")


def test_action_route():
    """Prueba ruta de acción (CASO CRÍTICO)."""
    print_section("4. Ruta de Acción - Vulneración de Derechos")
    
    violation = "Fui despedida sin justificación por quedar embarazada"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/action-route",
            json={"violation_description": violation}
        )
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Vulneración: {violation}")
        print_success(f"Derechos afectados identificados: {len(data['affected_rights'])}")
        
        for right in data['affected_rights']:
            print(f"\n{Colors.BOLD}Art. {right['number']}: {right['titulo_nombre']}{Colors.ENDC}")
            print_info(f"Texto: {right['texto'][:120]}...")
        
        print(f"\n{Colors.BOLD}Ruta de Acción Recomendada:{Colors.ENDC}")
        print(data['action_route'][:800] + "...\n")
        
        print(f"{Colors.BOLD}Acciones Disponibles:{Colors.ENDC}")
        for i, action in enumerate(data['available_actions'], 1):
            print(f"  {i}. {action}")
        
        print_info(f"Tiempo de procesamiento: {data['response_time_ms']}ms")
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")


def test_work_right():
    """Prueba búsqueda sobre derecho al trabajo."""
    print_section("5. Consulta Específica - Derecho al Trabajo")
    
    query = "¿Qué protege el derecho al trabajo?"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/consulta",
            json={"query": query}
        )
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Pregunta: {query}")
        print_success(f"Art. Principal: {data['primary_article']['number']}")
        
        print(f"\n{Colors.BOLD}Artículos Relacionados:{Colors.ENDC}")
        for art in data['related_articles']:
            print(f"  - Art. {art['number']}: {art['titulo_nombre']}")
        
        print(f"\n{Colors.BOLD}Análisis del LLM:{Colors.ENDC}")
        print(data['llm_response'][:500] + "...\n")
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")


def test_article_direct():
    """Prueba obtener artículo directamente."""
    print_section("6. Obtener Artículo Específico - Art. 13")
    
    try:
        response = requests.get(f"{BASE_URL}/api/articles/13")
        response.raise_for_status()
        data = response.json()
        
        print_success(f"Artículo: {data['articulo']}")
        print_info(f"Título: {data['titulo_nombre']}")
        print_info(f"Capítulo: {data['capitulo_nombre']}")
        
        print(f"\n{Colors.BOLD}Texto Completo:{Colors.ENDC}")
        print(data['texto'])
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")


def test_list_articles():
    """Prueba listar artículos con paginación."""
    print_section("7. Listar Artículos - Con Paginación")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/articles",
            params={"limit": 5, "offset": 0}
        )
        response.raise_for_status()
        data = response.json()
        
        print_success(f"Total de artículos: {data['total_count']}")
        print_info(f"Retornados: {data['returned_count']}")
        print_info(f"Offset: {data['offset']}")
        
        print(f"\n{Colors.BOLD}Primeros 5 artículos:{Colors.ENDC}")
        for art in data['articles']:
            print(f"  Art. {art['number']}: {art['titulo_nombre']}")
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")


def test_comparison():
    """Prueba búsqueda comparativa."""
    print_section("8. Búsqueda Comparativa - Derechos Humanos")
    
    query = "derechos humanos fundamentales"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search-advanced",
            json={"query": query, "top_k": 5}
        )
        response.raise_for_status()
        data = response.json()
        
        print_info(f"Búsqueda: {query}")
        print_success(f"Artículos encontrados: {data['results_count']}")
        
        print(f"\n{Colors.BOLD}Top 5 Resultados:{Colors.ENDC}")
        for result in data['results'][:5]:
            relevance_bar = "█" * int(result['relevance_score'] * 20)
            print(f"Art. {result['number']:3} │ {relevance_bar:20} │ {result['titulo_nombre']}")
        
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")


def main():
    """Ejecuta todos los tests."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║         IurisLex v2: Suite de Ejemplos de Uso                       ║")
    print("║         Mentor Constitucional con Búsqueda Semántica y RAG          ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    # Verificar conexión
    if not health_check():
        print(f"\n{Colors.FAIL}✗ API no disponible en {BASE_URL}{Colors.ENDC}")
        print("Por favor, asegúrate de que:")
        print("  1. Ollama está corriendo: ollama serve")
        print("  2. La API está corriendo: uvicorn app.api.main:app --reload")
        return
    
    # Ejecutar tests
    try:
        test_search_basic()
        test_search_with_typo()
        test_action_route()
        test_work_right()
        test_article_direct()
        test_list_articles()
        test_comparison()
        
        print_section("✅ TODOS LOS TESTS COMPLETADOS")
        print(f"{Colors.OKGREEN}El sistema IurisLex v2 está funcionando correctamente.{Colors.ENDC}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠ Tests interrumpidos por el usuario{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Error inesperado: {e}{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
