"""
Suite de pruebas para IurisLex v2
Valida búsqueda, RAG, prompts y validación de respuestas
"""
import sys
from pathlib import Path
import json

# Configurar path
ROOT_DIR = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(ROOT_DIR))

from app.core.rag_v2 import (
    TextNormalizer,
    ResponseValidator,
    EmbeddingsLoader,
    HybridSearchEngine
)
from app.core.prompts import ConstitutionalExpertPrompts, PromptBuilder


class Colors:
    """Colores para output en terminal."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def test_text_normalizer():
    """Prueba el normalizador de texto."""
    print(f"\n{Colors.BLUE}=== Test: TextNormalizer ==={Colors.END}")
    
    tests = [
        ("Derecho al TRABAJO", "derecho al trabajo"),
        ("Art. 25 - Constitución", "art 25 constitucin"),
        ("¿Por qué?", "por qu"),
        ("Artículo 1°", "articulo 1"),
    ]
    
    for input_text, expected in tests:
        result = TextNormalizer.normalize(input_text)
        status = Colors.GREEN + "✓" if result == expected else Colors.RED + "✗"
        print(f"{status} '{input_text}' → '{result}' {Colors.END}")


def test_article_number_extraction():
    """Prueba la extracción de números de artículos."""
    print(f"\n{Colors.BLUE}=== Test: Extract Article Numbers ==={Colors.END}")
    
    tests = [
        ("Artículo 13", "13"),
        ("Art. 25", "25"),
        ("art 53", "53"),
        ("¿Qué es el Art. 1?", "1"),
        ("Capítulo 3", None),
    ]
    
    for query, expected in tests:
        result = TextNormalizer.extract_article_number(query)
        status = Colors.GREEN + "✓" if result == expected else Colors.RED + "✗"
        print(f"{status} '{query}' → {result} (esperado: {expected}) {Colors.END}")


def test_response_validator():
    """Prueba el validador de respuestas."""
    print(f"\n{Colors.BLUE}=== Test: ResponseValidator ==={Colors.END}")
    
    # Test 1: Respuesta válida con referencias
    response1 = "El Artículo 13 establece que todas las personas nacen libres e iguales. El Artículo 1 refuerza..."
    query1 = "¿Qué es la igualdad?"
    articles = [
        {'number': '13', 'texto': 'Todas las personas nacen libres e iguales...'},
        {'number': '1', 'texto': 'Colombia es un Estado...'},
    ]
    
    is_valid, confidence, message = ResponseValidator.validate_against_articles(
        response1, query1, articles
    )
    print(f"{'✓' if is_valid else '✗'} Respuesta válida: {message} (Confianza: {confidence:.2%})")
    
    # Test 2: Respuesta sin referencias
    response2 = "La igualdad es un principio fundamental."
    is_valid2, confidence2, message2 = ResponseValidator.validate_against_articles(
        response2, query1, articles
    )
    print(f"{'✗' if not is_valid2 else '✓'} Respuesta sin artículos: {message2} (Confianza: {confidence2:.2%})")
    
    # Test 3: Respuesta muy corta
    response3 = "Sí."
    is_valid3, _, message3 = ResponseValidator.validate_against_articles(
        response3, query1, articles
    )
    print(f"{'✗' if not is_valid3 else '✓'} Respuesta muy corta: {message3}")


def test_extract_article_references():
    """Prueba la extracción de referencias de artículos de respuestas."""
    print(f"\n{Colors.BLUE}=== Test: Extract Article References ==={Colors.END}")
    
    tests = [
        (
            "El Artículo 13 establece... El Art. 1 dice...",
            ['13', '1']
        ),
        (
            "Conforme al artículo 25, el derecho al trabajo...",
            ['25']
        ),
        (
            "No hay referencias legales en esta respuesta.",
            []
        ),
    ]
    
    for response, expected in tests:
        result = ResponseValidator.extract_article_references(response)
        status = Colors.GREEN + "✓" if set(result) == set(expected) else Colors.RED + "✗"
        print(f"{status} Encontradas {len(result)} referencias: {result} {Colors.END}")


def test_prompts():
    """Prueba los prompts especializados."""
    print(f"\n{Colors.BLUE}=== Test: Prompts Especializados ==={Colors.END}")
    
    # Test: Sistema prompt no vacío
    system_prompt = ConstitutionalExpertPrompts.SYSTEM_PROMPT
    assert len(system_prompt) > 100, "System prompt muy corto"
    assert "NUNCA inventes" in system_prompt or "nunca inventes" in system_prompt.lower()
    print(f"✓ System prompt contiene instrucciones anti-alucinación")
    
    # Test: Expert analysis prompt
    expert_prompt = ConstitutionalExpertPrompts.expert_analysis(
        query="¿Qué es la igualdad?",
        context="Artículo 13...",
        related_articles="Artículos relacionados..."
    )
    assert 'system' in expert_prompt
    assert 'user' in expert_prompt
    assert len(expert_prompt['user']) > 50
    print(f"✓ Expert analysis prompt correctamente formado")
    
    # Test: Simple explanation prompt
    simple_prompt = ConstitutionalExpertPrompts.simple_explanation(
        query="¿Qué es trabajo?",
        article_text="El trabajo es un derecho...",
        article_number="25"
    )
    assert "palabras simples" in simple_prompt['user'].lower()
    print(f"✓ Simple explanation prompt contiene instrucciones de claridad")


def test_prompt_structure_validation():
    """Prueba que las respuestas tengan estructura correcta."""
    print(f"\n{Colors.BLUE}=== Test: Response Structure Validation ==={Colors.END}")
    
    from app.core.prompts import ResponseStructure
    
    # Respuesta bien estructurada
    good_response = """## Artículo(s) Aplicable(s)
    Art. 13, Art. 1
    
    ## Explicación Clara
    La igualdad es fundamental...
    
    ## Derechos/Garantías Específicos
    - Igualdad ante la ley
    - No discriminación
    
    ## Ejemplo Práctico de la Vida Real
    Si alguien es discriminado...
    
    ## Paso Siguiente
    Puede interponer tutela...
    """
    
    has_structure = ResponseStructure.validate_structure(
        good_response,
        ResponseStructure.EXPERT_ANALYSIS_SECTIONS
    )
    print(f"{'✓' if has_structure else '✗'} Respuesta bien estructurada: {has_structure}")
    
    # Respuesta mal estructurada
    bad_response = "El artículo 13 establece la igualdad."
    has_bad_structure = ResponseStructure.validate_structure(
        bad_response,
        ResponseStructure.EXPERT_ANALYSIS_SECTIONS
    )
    print(f"{'✗' if not has_bad_structure else '✓'} Respuesta sin estructura: {not has_bad_structure}")


def test_section_extraction():
    """Prueba la extracción de secciones de respuestas."""
    print(f"\n{Colors.BLUE}=== Test: Section Extraction ==={Colors.END}")
    
    from app.core.prompts import ResponseStructure
    
    response = """## Artículo(s) Aplicable(s)
    Art. 25
    
    ## Explicación Clara
    El derecho al trabajo es fundamental.
    
    ## Derechos Específicos
    - Estabilidad laboral
    - Justa causa para despido
    """
    
    sections = ResponseStructure.extract_sections(response)
    expected_sections = 3
    
    print(f"Secciones encontradas: {len(sections)}")
    for section, content in sections.items():
        print(f"  - {section}: {len(content)} caracteres")


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}IurisLex v2 - Suite de Pruebas Unitarias{Colors.END}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.END}")
    
    try:
        test_text_normalizer()
        test_article_number_extraction()
        test_response_validator()
        test_extract_article_references()
        test_prompts()
        test_prompt_structure_validation()
        test_section_extraction()
        
        print(f"\n{Colors.GREEN}{'='*60}")
        print(f"✓ Todas las pruebas ejecutadas exitosamente")
        print(f"{'='*60}{Colors.END}\n")
        
    except Exception as e:
        print(f"\n{Colors.RED}{'='*60}")
        print(f"✗ Error durante las pruebas: {e}")
        print(f"{'='*60}{Colors.END}\n")
        raise


if __name__ == '__main__':
    run_all_tests()
