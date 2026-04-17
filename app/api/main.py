from pathlib import Path
import csv
import os
import ollama
import re
import time
import unicodedata
import numpy as np
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Importar nuevas funcionalidades v2
from app.core.rag_v2 import (
    HybridSearchEngine, 
    EmbeddingsLoader,
    QueryEmbedder,
    ResponseValidator, 
    ContextBuilder,
    TextNormalizer
)
from app.core.prompts import (
    ConstitutionalExpertPrompts, 
    PromptBuilder, 
    PromptType
)

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / '.env')

WEB_DIR = ROOT_DIR / 'web'
INDEX_FILE = WEB_DIR / 'index.html'
CSV_PATH = ROOT_DIR / 'data' / 'processed' / 'cp_co_1991.csv'

app = FastAPI(
    title='IurisLex Mentor Constitucional',
    description='Consulta la Constitución Política de Colombia con análisis jurídico, comparación y simulaciones de casos prácticos.',
)


def normalize(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value.lower())
    without_diacritics = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r'[^\w\s]+', ' ', without_diacritics).strip()


def load_constitution() -> List[Dict[str, str]]:
    articles: List[Dict[str, str]] = []
    if not CSV_PATH.exists():
        return articles

    with CSV_PATH.open('r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            raw_article = row.get('articulo', '') or ''
            article_num = ''.join(re.findall(r'\d+', raw_article))
            if not article_num:
                continue

            state = {
                'number': article_num,
                'articulo': raw_article.strip(),
                'titulo': (row.get('titulo') or '').strip(),
                'titulo_nombre': (row.get('titulo_nombre') or '').strip(),
                'capitulo': (row.get('capitulo') or '').strip(),
                'capitulo_nombre': (row.get('capitulo_nombre') or '').strip(),
                'texto': (row.get('texto') or '').strip(),
            }
            state['search_text'] = normalize(' '.join([state['articulo'], state['titulo_nombre'], state['capitulo_nombre'], state['texto']]))
            articles.append(state)

    return articles


OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')
OLLAMA_MODEL = os.getenv('LLM_MODEL', 'qwen2.5:7b-instruct')
OLLAMA_FALLBACK_MODEL = os.getenv('OLLAMA_FALLBACK_MODEL', 'qwen2.5:3b-instruct')
OLLAMA_CLIENT = ollama.Client(host=OLLAMA_HOST)


@app.on_event('startup')
def warm_up_ollama():
    try:
        OLLAMA_CLIENT.list()
    except Exception:
        pass


def build_ollama_prompt(
    article: Dict[str, str], 
    related: List[Dict[str, str]], 
    query: str
) -> List[Dict[str, str]]:
    """Construye prompt mejorado usando PromptBuilder."""
    prompt_dict = PromptBuilder.build_analysis_prompt(
        query=query,
        primary_article=article,
        related_articles=related,
        prompt_type=PromptType.EXPERT_ANALYSIS
    )
    
    return [
        {"role": "system", "content": prompt_dict["system"]},
        {"role": "user", "content": prompt_dict["user"]}
    ]


def get_ollama_response(article: Dict[str, str], related: List[Dict[str, str]], query: str) -> str:
    messages = build_ollama_prompt(article, related, query)

    def fetch_response(model: str) -> str:
        response = OLLAMA_CLIENT.chat(model=model, messages=messages, keep_alive='5m')
        return getattr(getattr(response, 'message', None), 'content', None)

    try:
        content = fetch_response(OLLAMA_MODEL)
        if content:
            return content.strip()
        if OLLAMA_FALLBACK_MODEL and OLLAMA_FALLBACK_MODEL != OLLAMA_MODEL:
            content = fetch_response(OLLAMA_FALLBACK_MODEL)
            if content:
                return content.strip()
            return 'Ollama respondió sin contenido en el modelo principal y en el fallback.'
    except Exception as exc:
        fallback_error = str(exc)
        if OLLAMA_FALLBACK_MODEL and OLLAMA_FALLBACK_MODEL != OLLAMA_MODEL:
            try:
                content = fetch_response(OLLAMA_FALLBACK_MODEL)
                if content:
                    return content.strip()
                return 'Ollama respondió sin contenido en el fallback.'
            except Exception as fallback_exc:
                return (
                    'No se pudo conectar con Ollama: ' + fallback_error +
                    ' | Fallback: ' + str(fallback_exc)
                )
        return f'No se pudo conectar con Ollama: {fallback_error}'

    return 'Ollama respondió sin contenido. Comprueba que el modelo esté en ejecución y cargado.'


ARTICLES = load_constitution()
ARTICLES_BY_NUMBER = {article['number']: article for article in ARTICLES}

# Inicializar sistema RAG v2
EMBEDDINGS_PATH = ROOT_DIR / 'data' / 'index' / 'cp_co_1991_emb.npy'
EMBEDDINGS_LOADER = EmbeddingsLoader(EMBEDDINGS_PATH, ARTICLES)
QUERY_EMBEDDER = QueryEmbedder(model_name="paraphrase-multilingual-MiniLM-L12-v2")
SEARCH_ENGINE = HybridSearchEngine(
    articles=ARTICLES,
    embeddings_loader=EMBEDDINGS_LOADER,
    semantic_weight=0.6,
    lexical_weight=0.4
)

print(f"✓ Sistema RAG v2 inicializado")
print(f"  - Artículos cargados: {len(ARTICLES)}")
print(f"  - Embeddings artículos: {'Sí' if EMBEDDINGS_LOADER.has_embeddings() else 'No'}")
print(f"  - Generador de embeddings queries: {'Sí' if QUERY_EMBEDDER.initialized else 'No'}")
print(f"  - Motor de búsqueda: Híbrido (semántico + léxico + fuzzy)")


def find_related_articles(article: Dict[str, str], top_k: int = 3) -> List[Dict[str, str]]:
    """Encuentra artículos relacionados usando búsqueda semántica."""
    related = []
    
    # Buscar por capítulo/título similar
    for other in ARTICLES:
        if other['number'] == article['number']:
            continue
        if (other['capitulo_nombre'] == article['capitulo_nombre'] or 
            other['titulo_nombre'] == article['titulo_nombre']):
            related.append(other)
    
    # Si no hay suficientes, buscar por palabras clave
    if len(related) < top_k:
        query_keywords = f"{article['titulo_nombre']} {article['capitulo_nombre']}"
        # Generar embedding para búsqueda semántica
        keywords_embedding = QUERY_EMBEDDER.embed_query(query_keywords)
        search_results = SEARCH_ENGINE.hybrid_search_cached(
            query_keywords, 
            query_embedding=keywords_embedding,
            top_k=10
        )
        
        existing_numbers = {a['number'] for a in related}
        for result in search_results:
            if result.article_number not in existing_numbers and len(related) < top_k:
                related.append(result.article)
                existing_numbers.add(result.article_number)
    
    return related[:top_k]


def build_analysis(article: Dict[str, str], related: List[Dict[str, str]]) -> Dict[str, str]:
    """Construye análisis estructurado del artículo."""
    if not article:
        return {}
    
    article_num = article['number']
    heading = f"Artículo {article_num}"
    
    simple = (
        f"{heading} protege un derecho fundamental en la Constitución Política de Colombia de 1991. "
        f"Su aplicación es directa y prevalece sobre cualquier otra norma legal que la contradiga."
    )
    
    technical = (
        f"El {heading} se ubica en {article['titulo_nombre']} "
        f"(Capítulo: {article['capitulo_nombre']}). "
        f"Es un artículo de aplicación inmediata que establece garantías constitucionales. "
        f"Su interpretación debe ser amplia y favorable a la persona titular del derecho."
    )
    
    comparison_text = ', '.join([f"Art. {a['number']}" for a in related]) or "Artículos comparables disponibles"
    comparative = (
        f"Este artículo se relaciona con {comparison_text}. "
        f"Estas relaciones establecen un sistema integrado de protección de derechos."
    )
    
    case_practice = (
        f"En la práctica: Si una persona considera que {heading} fue vulnerado, "
        f"puede interponer una Acción de Tutela ante los jueces de la república, "
        f"solicitando la protección inmediata de su derecho fundamental."
    )
    
    reflection = (
        f"¿Sabías que {heading} ha sido desarrollado por la Corte Constitucional "
        f"a través de más de 100 sentencias? Esto significa que hay jurisprudencia clara sobre cómo aplicarlo."
    )
    
    return {
        'simple': simple,
        'technical': technical,
        'comparative': comparative,
        'case_practice': case_practice,
        'reflection': reflection,
    }


def build_case(article: Dict[str, str]) -> Dict[str, str]:
    """Construye caso práctico basado en el artículo."""
    art_num = article['number']
    
    return {
        'scenario': (
            f"Caso de estudio: Una persona acude a un juez porque considera que su derecho "
            f"consagrado en el Artículo {art_num} fue vulnerado. "
            f"El caso explora cómo se aplica la Constitución ante hechos concretos."
        ),
        'prompt': (
            f"Como juez constitucional, debes resolver un caso donde se invoca el Artículo {art_num}. "
            f"Primero identifica qué derecho se vulneró, luego analiza los hechos a la luz de la Constitución, "
            f"y finalmente dicta una decisión justificada. Usa lenguaje accesible."
        ),
    }


@app.post('/api/consulta')
def consulta(payload: Dict[str, str]):
    """Endpoint principal de consultas con búsqueda v2."""
    query = (payload.get('query') or '').strip()
    if not query:
        raise HTTPException(status_code=400, detail='La consulta no puede estar vacía.')
    
    start_time = time.perf_counter()
    
    # Generar embedding de la query para búsqueda semántica
    query_embedding = QUERY_EMBEDDER.embed_query(query)
    
    # Usar búsqueda híbrida v2 CON embedding de query
    search_results = SEARCH_ENGINE.hybrid_search_cached(
        query, 
        query_embedding=query_embedding,
        top_k=10
    )
    
    if not search_results:
        raise HTTPException(
            status_code=404, 
            detail='No se encontró un artículo relevante. Intenta con palabras clave diferentes.'
        )
    
    # Artículo principal (mejor resultado)
    primary_result = search_results[0]
    article = primary_result.article
    
    # Artículos relacionados (resto de resultados)
    related = [r.article for r in search_results[1:4]]
    
    # Construir análisis y caso
    analysis = build_analysis(article, related)
    case_simulation = build_case(article)
    
    # Obtener respuesta del LLM
    llm_response = get_ollama_response(article, related, query)
    
    # Validar respuesta
    validator = ResponseValidator()
    is_valid, confidence, validation_msg = validator.validate_against_articles(
        llm_response, 
        query, 
        [article] + related,
        confidence_threshold=0.3
    )
    
    elapsed = round((time.perf_counter() - start_time) * 1000)
    
    return {
        'query': query,
        'article': article,
        'related': related,
        'analysis': analysis,
        'case_simulation': case_simulation,
        'llm_response': llm_response,
        'validation': {
            'is_valid': is_valid,
            'confidence': round(confidence * 100, 1),
            'message': validation_msg
        },
        'search': {
            'method': 'hybrid_v2',
            'primary_score': round(primary_result.relevance_score, 3),
            'search_type': primary_result.search_type
        },
        'response_time_ms': elapsed,
        'provider': f'Ollama (local, host={OLLAMA_HOST})',
        'model': OLLAMA_MODEL,
    }


@app.post('/api/action-route')
def action_route(payload: Dict[str, str]):
    """Endpoint para determinar ruta de acción ante violación de derechos."""
    violation = (payload.get('violation') or '').strip()
    if not violation:
        raise HTTPException(status_code=400, detail='Describe la vulneración de derechos.')
    
    start_time = time.perf_counter()
    
    # Generar embedding de la violation para búsqueda semántica
    violation_embedding = QUERY_EMBEDDER.embed_query(violation)
    
    # Buscar artículos relevantes CON embedding
    search_results = SEARCH_ENGINE.hybrid_search_cached(
        violation, 
        query_embedding=violation_embedding,
        top_k=10
    )
    
    if not search_results:
        raise HTTPException(status_code=404, detail='No se encontraron artículos relevantes.')
    
    affected_articles = [r.article for r in search_results[:5]]
    
    # Construir prompt de ruta de acción
    prompt_dict = PromptBuilder.build_action_route_prompt(violation, affected_articles)
    
    # Obtener respuesta del LLM
    messages = [
        {"role": "system", "content": prompt_dict["system"]},
        {"role": "user", "content": prompt_dict["user"]}
    ]
    
    try:
        response = OLLAMA_CLIENT.chat(model=OLLAMA_MODEL, messages=messages, keep_alive='5m')
        llm_response = getattr(getattr(response, 'message', None), 'content', None) or 'Sin respuesta'
    except Exception as e:
        llm_response = f"Error al contactar Ollama: {str(e)}"
    
    elapsed = round((time.perf_counter() - start_time) * 1000)
    
    return {
        'violation': violation,
        'affected_articles': affected_articles,
        'action_route': llm_response,
        'response_time_ms': elapsed,
        'provider': f'Ollama (local, host={OLLAMA_HOST})',
        'model': OLLAMA_MODEL,
    }


@app.get('/api/articles/{article_number}')
def get_article(article_number: str):
    article = ARTICLES_BY_NUMBER.get(article_number)
    if not article:
        raise HTTPException(status_code=404, detail='Artículo no encontrado.')
    return article


@app.get('/', include_in_schema=False)
def raiz():
    if INDEX_FILE.exists():
        return HTMLResponse(INDEX_FILE.read_text(encoding='utf-8'))
    return HTMLResponse('<html><body><h1>IurisLex Mentor Constitucional</h1><p>La UI no está disponible.</p></body></html>', status_code=200)


if WEB_DIR.exists():
    app.mount('/ui', StaticFiles(directory=str(WEB_DIR), html=True), name='ui')
