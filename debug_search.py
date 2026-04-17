#!/usr/bin/env python3
"""Debug script to test article loading and search functionality"""
import csv
import re
import unicodedata
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
CSV_PATH = ROOT_DIR / 'data' / 'processed' / 'cp_co_1991.csv'

def normalize(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value.lower())
    without_diacritics = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r'[^\w\s]+', ' ', without_diacritics).strip()

def load_constitution():
    articles = []
    if not CSV_PATH.exists():
        print(f"[ERROR] CSV no encontrado en: {CSV_PATH}")
        return articles
    
    print(f"[OK] CSV encontrado en: {CSV_PATH}")
    
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

def test_search(articles, query):
    print(f"\n[SEARCH] Buscando: '{query}'")
    print(f"   Normalizado: '{normalize(query)}'")
    
    # Búsqueda por número
    number_match = re.search(r'\b(\d{1,3})\b', query)
    if number_match:
        num = number_match.group(1)
        articles_by_number = {article['number']: article for article in articles}
        if num in articles_by_number:
            print(f"   [FOUND] Encontrado por número: Art. {num}")
            return
    
    # Búsqueda por ranking
    normalized = normalize(query)
    if not normalized:
        print("   [ERROR] Query normalizado vacío")
        return
    
    matches = []
    for article in articles:
        score = sum(1 for token in normalized.split() if token in article['search_text'])
        if score > 0:
            matches.append((score, article))
    
    matches.sort(key=lambda item: item[0], reverse=True)
    
    if matches:
        print(f"   [FOUND] Encontrados {len(matches)} artículos")
        for score, article in matches[:3]:
            print(f"      - Art. {article['number']}: {article['titulo_nombre']} (score: {score})")
    else:
        print(f"   [NOT FOUND] No se encontraron artículos")
        # Debug: mostrar primeros tokens
        print(f"      Tokens buscados: {normalized.split()[:5]}")
        print(f"      Primeros search_text de artículos:")
        for article in articles[:3]:
            print(f"         Art. {article['number']}: {article['search_text'][:80]}...")

if __name__ == '__main__':
    articles = load_constitution()
    print(f"\n[STATS] Total artículos cargados: {len(articles)}")
    
    if articles:
        print(f"\n[ARTICLES] Primeros artículos:")
        for article in articles[:3]:
            print(f"  Art. {article['number']}: {article['articulo']} - {article['titulo_nombre']}")
    
    # Pruebas de búsqueda
    test_queries = [
        "artículo 1",
        "libertad",
        "derecho",
        "estado social",
        "1",
        "principios fundamentales"
    ]
    
    for query in test_queries:
        test_search(articles, query)
