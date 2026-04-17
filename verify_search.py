#!/usr/bin/env python3
"""
Script final de prueba para verificar que la búsqueda funciona correctamente.
"""
import sys
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from app.core.rag_v2 import (
    HybridSearchEngine, 
    EmbeddingsLoader, 
    QueryEmbedder,
    TextNormalizer
)
import csv
import re

def load_articles():
    """Carga artículos desde CSV."""
    csv_path = ROOT_DIR / 'data' / 'processed' / 'cp_co_1991.csv'
    articles = []
    
    with csv_path.open('r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_article = row.get('articulo', '') or ''
            article_num = ''.join(re.findall(r'\d+', raw_article))
            if not article_num:
                continue
            
            normalizer = TextNormalizer()
            state = {
                'number': article_num,
                'articulo': raw_article.strip(),
                'titulo': (row.get('titulo') or '').strip(),
                'titulo_nombre': (row.get('titulo_nombre') or '').strip(),
                'capitulo': (row.get('capitulo') or '').strip(),
                'capitulo_nombre': (row.get('capitulo_nombre') or '').strip(),
                'texto': (row.get('texto') or '').strip(),
            }
            state['search_text'] = normalizer.normalize(' '.join([
                state['articulo'], 
                state['titulo_nombre'], 
                state['capitulo_nombre'], 
                state['texto']
            ]))
            articles.append(state)
    
    return articles

def main():
    print("\n" + "="*70)
    print("  🧪 PRUEBA FINAL DE BÚSQUEDA SEMÁNTICA")
    print("="*70 + "\n")
    
    # Cargar componentes
    print("1️⃣ Cargando datos...")
    articles = load_articles()
    print(f"   ✓ {len(articles)} artículos cargados")
    
    embeddings_path = ROOT_DIR / 'data' / 'index' / 'cp_co_1991_emb.npy'
    embeddings_loader = EmbeddingsLoader(embeddings_path, articles)
    print(f"   ✓ Embeddings: {embeddings_loader.embeddings.shape}")
    
    search_engine = HybridSearchEngine(articles, embeddings_loader)
    print(f"   ✓ Motor de búsqueda inicializado")
    
    embedder = QueryEmbedder()
    print(f"   ✓ Embedder de queries: {embedder.initialized}")
    
    # Pruebas
    print("\n2️⃣ Ejecutando pruebas de búsqueda...\n")
    
    test_cases = [
        ("derecho a la vida", [11]),  # Debería encontrar Art. 11
        ("libertad de expresión", [20]),  # Debería encontrar Art. 20
        ("educación pública", [67]),  # Debería encontrar Art. 67
        ("art 1", [1]),  # Búsqueda exacta
        ("familia", [42, 43, 44]),  # Artículos sobre familia
    ]
    
    all_correct = True
    
    for query, expected_articles in test_cases:
        print(f"📝 Query: '{query}'")
        print(f"   Esperado: Art. {expected_articles}")
        
        # Generar embedding
        query_embedding = embedder.embed_query(query)
        
        # Buscar
        results = search_engine.hybrid_search(
            query,
            query_embedding=query_embedding,
            top_k=5
        )
        
        if results:
            found_numbers = [int(r.article_number) for r in results[:3]]
            print(f"   Encontrado: Art. {found_numbers}")
            
            # Verificar si alguno coincide
            match = any(n in found_numbers for n in expected_articles)
            
            if match:
                print(f"   ✅ CORRECTO - Búsqueda relevante\n")
            else:
                print(f"   ⚠️  ADVERTENCIA - No encontró artículos esperados\n")
                all_correct = False
            
            # Mostrar detalles del primer resultado
            top = results[0]
            print(f"   📄 Top resultado:")
            print(f"      Artículo: {top.article_number}")
            print(f"      Título: {top.article['titulo_nombre']}")
            print(f"      Score: {top.relevance_score:.3f}")
            print(f"      Tipo: {top.search_type}")
            print(f"      Texto: {top.article['texto'][:100]}...\n")
        else:
            print(f"   ❌ ERROR - No se encontraron resultados\n")
            all_correct = False
    
    print("="*70)
    if all_correct:
        print("  ✅ TODAS LAS PRUEBAS PASARON")
        print("  La búsqueda semántica funciona correctamente")
    else:
        print("  ⚠️  Algunas pruebas mostraron advertencias")
    print("="*70 + "\n")
    
    print("📌 SIGUIENTE PASO:")
    print("   Reinicia el servidor uvicorn para cargar los embeddings nuevos:")
    print("   $ uvicorn app.api.main:app --reload\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
