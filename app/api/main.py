from pathlib import Path
import csv
import os
import ollama
import re
import time
import unicodedata
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

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

    with CSV_PATH.open('r', encoding='latin-1') as csv_file:
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


def build_ollama_prompt(article: Dict[str, str], related: List[Dict[str, str]], query: str) -> List[Dict[str, str]]:
    related_section = ''
    if related:
        related_section = '\n\nArtículos relacionados:\n' + '\n'.join([
            f"- {item['articulo']} ({item['capitulo_nombre'] or item['titulo_nombre']}): {item['texto']}"
            for item in related[:3]
        ])

    return [
        {
            'role': 'system',
            'content': (
                'Eres un asistente jurídico experto en la Constitución Política de Colombia de 1991. '
                'Utiliza la información proporcionada para responder con precisión y claridad, explicando el contexto constitucional, '
                'los artículos relacionados y una recomendación práctica para un caso realista.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f"Consulta: {query}\n\n"
                f"Artículo objetivo: {article['articulo']}\n"
                f"Texto: {article['texto']}\n"
                f"Título: {article['titulo_nombre']}\n"
                f"Capítulo: {article['capitulo_nombre']}\n"
                f"{related_section}\n"
                'Responde como un mentor jurídico. Primero resume el artículo, luego indica las relaciones principales, '
                'y finalmente ofrece una guía práctica clara para actuar con fundamento constitucional.'
            ),
        },
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


def rank_articles(query: str) -> List[Dict[str, str]]:
    normalized = normalize(query)
    if not normalized:
        return []

    matches = []
    for article in ARTICLES:
        score = sum(1 for token in normalized.split() if token in article['search_text'])
        if score > 0:
            matches.append((score, article))

    matches.sort(key=lambda item: item[0], reverse=True)
    return [article for _, article in matches[:6]]


def find_article(query: str) -> Dict[str, str]:
    number_match = re.search(r'\b(\d{1,3})\b', query)
    if number_match:
        candidate = ARTICLES_BY_NUMBER.get(number_match.group(1))
        if candidate:
            return candidate

    candidates = rank_articles(query)
    if candidates:
        return candidates[0]
    return {}


def build_comparison(article: Dict[str, str]) -> List[Dict[str, str]]:
    if not article:
        return []

    related = [other for other in ARTICLES if other['number'] != article['number'] and other['capitulo_nombre'] == article['capitulo_nombre']]
    return related[:3]


def build_analysis(article: Dict[str, str], related: List[Dict[str, str]]) -> Dict[str, str]:
    heading = article['articulo']
    simple = (
        f"{heading} garantiza un principio constitucional fundamental. "
        f"Su redacción protege la interpretación jurídica del texto actual y reafirma la prevalencia de los derechos fundamentales en Colombia."
    )
    technical = (
        f"El artículo {article['number']} forma parte de {article['titulo_nombre']} y se ubica en {article['capitulo_nombre']}. "
        f"Desde un enfoque técnico, es un artículo de aplicación directa que refuerza la protección de los derechos frente a la acción estatal y privada."
    )
    comparison_items = ', '.join([f"{item['articulo']}" for item in related]) or 'No hay comparaciones directas disponibles.'
    comparative = (
        f"Este artículo se relaciona con {comparison_items}. "
        f"Su comparación permite identificar patrones constitucionales comunes y diferencias en el tratamiento de derechos conexos."
    )
    case_practice = (
        f"Caso práctico: una persona presenta un reclamo cuando se vulnera el derecho consagrado en {heading}. "
        f"El análisis debe valorar los hechos a la luz de la Constitución y de la jurisprudencia que alimenta el deber de protección estatal."
    )
    reflection = (
        f"Pregunta de reflexión: ¿qué garantías adicionales se deben activar cuando se invoca {heading} en un proceso de tutela?"
    )

    return {
        'simple': simple,
        'technical': technical,
        'comparative': comparative,
        'case_practice': case_practice,
        'reflection': reflection,
    }


def build_case(article: Dict[str, str]) -> Dict[str, str]:
    return {
        'scenario': (
            f"Caso de estudio: una persona invoca {article['articulo']} porque considera que su libertad y dignidad fueron vulneradas en un proceso administrativo. "
            f"El caso simulado explora la carga probatoria y el análisis de la Constitucionalidad en la decisión judicial."
        ),
        'prompt': (
            f"Simula un juez que debe resolver un conflicto constitucional vinculado a {article['articulo']}. "
            f"Incluye referencia a los deberes de tutela y al respeto de los derechos fundamentales."
        ),
    }


@app.post('/api/consulta')
def consulta(payload: Dict[str, str]):
    query = (payload.get('query') or '').strip()
    if not query:
        raise HTTPException(status_code=400, detail='La consulta no puede estar vacía.')

    start_time = time.perf_counter()
    article = find_article(query)
    if not article:
        raise HTTPException(status_code=404, detail='No se encontró un artículo que coincida con la consulta.')

    related = build_comparison(article)
    analysis = build_analysis(article, related)
    case_simulation = build_case(article)
    llm_response = get_ollama_response(article, related, query)
    elapsed = round((time.perf_counter() - start_time) * 1000)

    return {
        'query': query,
        'article': article,
        'related': related,
        'analysis': analysis,
        'case_simulation': case_simulation,
        'llm_response': llm_response,
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
