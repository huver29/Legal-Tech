"""
Prompts mejorados para LLM - Experto en Derecho Constitucional Colombiano.
Implementa validación de alucinaciones y respuestas estructuradas.
"""
from enum import Enum
from typing import Dict


class PromptType(Enum):
    """Tipos de prompts disponibles."""
    EXPERT_ANALYSIS = "expert_analysis"
    SIMPLE_EXPLANATION = "simple_explanation"
    CASE_SIMULATION = "case_simulation"
    ACTION_ROUTE = "action_route"
    COMPARISON = "comparison"


class ConstitutionalExpertPrompts:
    """Colección de prompts expertos en derecho constitucional."""
    
    SYSTEM_PROMPT = """Eres un experto en Derecho Constitucional Colombiano con 20 años de experiencia.

INSTRUCCIONES CRÍTICAS:
1. SIEMPRE basa tus respuestas ÚNICAMENTE en los artículos constitucionales proporcionados
2. Si la información no está en los artículos, responde: "No encuentro soporte constitucional para esta pregunta"
3. NUNCA inventes información jurídica
4. SIEMPRE cita explícitamente el artículo (ej: "Artículo 13 establece...")
5. Usa lenguaje claro para ciudadanos, no jerga jurídica innecesaria

FORMATO OBLIGATORIO DE RESPUESTA:

## Artículo(s) Aplicable(s)
[Listar números: Art. X, Art. Y, etc.]

## Explicación Clara
[Explicar el concepto en máximo 3 párrafos, lenguaje simple]

## Derechos/Garantías Específicos
[Listar qué protege o establece]

## Ejemplo Práctico de la Vida Real
[Dar 1 ejemplo concreto de cómo aplica en Colombia]

## Paso Siguiente (si aplica)
[Si hay acciones disponibles, describirlas brevemente]

VALIDACIÓN: Todas tus respuestas deben poder citar artículos específicos. Si no es posible, responde con honestidad."""
    
    @staticmethod
    def expert_analysis(
        query: str,
        context: str,
        related_articles: str
    ) -> Dict[str, str]:
        """Prompt para análisis experto de artículos."""
        return {
            "system": ConstitutionalExpertPrompts.SYSTEM_PROMPT,
            "user": f"""CONSULTA: {query}

{context}

{related_articles}

Proporciona un análisis experto siguiendo el formato obligatorio.
Asegúrate de que CADA afirmación está basada en los artículos anteriores."""
        }
    
    @staticmethod
    def simple_explanation(
        query: str,
        article_text: str,
        article_number: str
    ) -> Dict[str, str]:
        """Prompt para explicación simplificada."""
        return {
            "system": ConstitutionalExpertPrompts.SYSTEM_PROMPT,
            "user": f"""El usuario pregunta: {query}

ARTÍCULO RELEVANTE:
Artículo {article_number}: {article_text}

TAREA:
Explica este artículo como si le hablaras a una persona sin educación legal:
1. ¿Qué es? (una frase)
2. ¿Para qué sirve? (máximo 2 frases)
3. ¿Cómo me afecta a mí? (un ejemplo real)
4. ¿Qué hago si me vulneran este derecho? (opciones breves)

IMPORTANTE: Usa palabras simples. Evita "jurisprudencia", "lapso", "ejecutoriedad"."""
        }
    
    @staticmethod
    def case_simulation(
        scenario: str,
        relevant_articles: str,
        article_number: str
    ) -> Dict[str, str]:
        """Prompt para simulación de casos."""
        return {
            "system": ConstitutionalExpertPrompts.SYSTEM_PROMPT,
            "user": f"""ESCENARIO: {scenario}

ARTÍCULOS APLICABLES:
{relevant_articles}

TAREA (Resuelve como juez):
1. ¿Qué derecho está en juego? Cita el artículo.
2. ¿Fue vulnerado? Justifica basado en los artículos.
3. ¿Qué debe hacer la persona afectada? (Acción + proceso)
4. ¿Cuál sería la decisión del juez? Explica basándote en el Artículo {article_number}.

Respuesta estructurada y concisa."""
        }
    
    @staticmethod
    def action_route(
        violation_description: str,
        affected_right_articles: str
    ) -> Dict[str, str]:
        """Prompt para rutas de acción ante violación de derechos."""
        return {
            "system": ConstitutionalExpertPrompts.SYSTEM_PROMPT,
            "user": f"""VULNERACIÓN REPORTADA: {violation_description}

DERECHOS AFECTADOS (según la Constitución):
{affected_right_articles}

PROPORCIONA UNA RUTA DE ACCIÓN:

1. **Derecho Vulnerado**
   - Artículos aplicables
   - Qué se vulneró exactamente

2. **Acciones Inmediatas**
   - ¿Qué puedo hacer ahora?
   - ¿A quién acudo?

3. **Proceso de Tutela (si aplica)**
   - ¿Cuándo procede la tutela para esto?
   - Pasos básicos
   - Tiempo aproximado

4. **Otras Opciones**
   - Acciones alternativas
   - Entidades que pueden ayudar

IMPORTANTE: Sé específico, basándote SOLO en los artículos proporcionados."""
        }
    
    @staticmethod
    def comparison(
        article1_num: str,
        article1_text: str,
        article2_num: str,
        article2_text: str
    ) -> Dict[str, str]:
        """Prompt para comparar dos artículos."""
        return {
            "system": ConstitutionalExpertPrompts.SYSTEM_PROMPT,
            "user": f"""COMPARACIÓN DE ARTÍCULOS:

**Artículo {article1_num}:**
{article1_text}

**Artículo {article2_num}:**
{article2_text}

ANALIZA:
1. ¿Cuáles son las similitudes?
2. ¿Cuáles son las diferencias?
3. ¿Cuándo aplica uno y cuándo el otro?
4. ¿Están relacionados?

Mantén explicaciones simples."""
        }
    
    @staticmethod
    def validation_prompt(
        query: str,
        llm_response: str,
        articles_cited: str
    ) -> Dict[str, str]:
        """Prompt para validar respuestas del LLM."""
        return {
            "system": """Eres un revisor jurídico estricto. Tu tarea es verificar que una respuesta 
esté COMPLETAMENTE basada en artículos constitucionales y que sea CORRECTA.

Sé muy exigente. Si algo no está explícitamente en los artículos, marca como INCORRECTO.""",
            "user": f"""PREGUNTA ORIGINAL: {query}

RESPUESTA A VALIDAR:
{llm_response}

ARTÍCULOS DISPONIBLES:
{articles_cited}

EVALÚA:
1. ¿Cada afirmación está basada en los artículos? (SÍ/NO)
2. ¿Hay alucinaciones o información no sustentada? (SÍ/NO)
3. ¿La respuesta es completa y útil? (SÍ/NO)
4. Confianza general: 0-100%

Responde en JSON:
{{"valid": true/false, "confidence": 0-100, "issues": ["..."], "feedback": "..."}}"""
        }


class PromptBuilder:
    """Constructor dinámico de prompts."""
    
    @staticmethod
    def build_analysis_prompt(
        query: str,
        primary_article: Dict,
        related_articles: list,
        prompt_type: PromptType = PromptType.EXPERT_ANALYSIS
    ) -> Dict[str, str]:
        """Construye prompt dinámico para análisis."""
        
        article_text = f"Artículo {primary_article['number']}: {primary_article.get('texto', '')}"
        
        related_text = "ARTÍCULOS RELACIONADOS:\n"
        for art in related_articles[:3]:
            related_text += f"- Artículo {art['number']}: {art.get('texto', '')[:200]}...\n"
        
        if prompt_type == PromptType.SIMPLE_EXPLANATION:
            return ConstitutionalExpertPrompts.simple_explanation(
                query,
                article_text,
                primary_article['number']
            )
        elif prompt_type == PromptType.EXPERT_ANALYSIS:
            return ConstitutionalExpertPrompts.expert_analysis(
                query,
                article_text,
                related_text
            )
        else:
            # Default: expert analysis
            return ConstitutionalExpertPrompts.expert_analysis(
                query,
                article_text,
                related_text
            )
    
    @staticmethod
    def build_action_route_prompt(
        violation_description: str,
        affected_articles: list
    ) -> Dict[str, str]:
        """Construye prompt para ruta de acción."""
        
        articles_text = "\n".join([
            f"- Artículo {art['number']}: {art.get('texto', '')[:150]}..."
            for art in affected_articles[:3]
        ])
        
        return ConstitutionalExpertPrompts.action_route(
            violation_description,
            articles_text
        )


class ResponseStructure:
    """Estructura esperada de respuestas."""
    
    EXPERT_ANALYSIS_SECTIONS = [
        "Artículo(s) Aplicable(s)",
        "Explicación Clara",
        "Derechos/Garantías Específicos",
        "Ejemplo Práctico",
        "Paso Siguiente"
    ]
    
    ACTION_ROUTE_SECTIONS = [
        "Derecho Vulnerado",
        "Acciones Inmediatas",
        "Proceso de Tutela",
        "Otras Opciones"
    ]
    
    @staticmethod
    def validate_structure(response: str, expected_sections: list) -> bool:
        """Valida que la respuesta tenga la estructura esperada."""
        for section in expected_sections:
            if section.lower() not in response.lower():
                return False
        return True
    
    @staticmethod
    def extract_sections(response: str) -> Dict[str, str]:
        """Extrae secciones de una respuesta estructurada."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            if line.startswith('##'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('##', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
