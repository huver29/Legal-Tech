#!/usr/bin/env python3
"""
Script de diagnóstico para verificar que la búsqueda funciona correctamente.
"""
import sys
from pathlib import Path
import csv

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from app.core.rag_v2 import (
    HybridSearchEngine, 
    EmbeddingsLoader, 
    QueryEmbedder,
    TextNormalizer
)

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def load_csv_data():
    """Carga datos del CSV."""
    csv_path = ROOT_DIR / 'data' / 'processed' / 'cp_co_1991.csv'
    articles = []
    
    if not csv_path.exists():
        print(f"❌ CSV no encontrado: {csv_path}")
        return articles
    
    try:
        with csv_path.open('r', encoding='latin-1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                articles.append(row)
        print(f"✓ CSV cargado: {len(articles)} filas")
        
        # Mostrar primeras filas
        if articles:
            print("\n📄 Estructura del CSV:")
            print(f"   Columnas: {list(articles[0].keys())}")
            print(f"\n📝 Primeras 3 filas:")
            for i, row in enumerate(articles[:3], 1):
                print(f"   {i}. Art. {row.get('articulo')}: {row.get('titulo_nombre')}")
        
        return articles
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        return articles

def test_embeddings_search():
    """Prueba la búsqueda con embeddings."""
    print_section("🔍 PRUEBA 1: BÚSQUEDA CON EMBEDDINGS")
    
    # Cargar datos
    csv_path = ROOT_DIR / 'data' / 'processed' / 'cp_co_1991.csv'
    embeddings_path = ROOT_DIR / 'data' / 'index' / 'cp_co_1991_emb.npy'
    
    # Cargar artículos
    articles = []
    with csv_path.open('r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            import re
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
    
    print(f"✓ {len(articles)} artículos cargados desde CSV")
    
    # Cargar embeddings
    embeddings_loader = EmbeddingsLoader(embeddings_path, articles)
    print(f"✓ Embeddings disponibles: {embeddings_loader.has_embeddings()}")
    
    # Crear motor de búsqueda
    search_engine = HybridSearchEngine(
        articles=articles,
        embeddings_loader=embeddings_loader,
        semantic_weight=0.6,
        lexical_weight=0.4
    )
    
    # Crear embedder de queries
    embedder = QueryEmbedder()
    print(f"✓ Embedder de queries inicializado: {embedder.initialized}")
    
    # Pruebas de búsqueda
    test_queries = [
        ("derecho a la vida", "Debería encontrar artículo 11"),
        ("libertad de expresión", "Debería encontrar artículo 20"),
        ("educación", "Debería encontrar artículo 67"),
        ("artículo 1", "Búsqueda exacta por número"),
        ("familia", "Debería encontrar artículos sobre familia"),
    ]
    
    print("\n📊 RESULTADOS DE BÚSQUEDA:")
    print("-" * 70)
    
    for query, expected in test_queries:
        print(f"\n🔎 Query: '{query}'")
        print(f"   Esperado: {expected}")
        
        # Generar embedding
        query_embedding = embedder.embed_query(query)
        
        # Buscar
        results = search_engine.hybrid_search_cached(
            query,
            query_embedding=query_embedding,
            top_k=5
        )
        
        if results:
            print(f"   ✓ Encontrados {len(results)} resultados:")
            for i, result in enumerate(results, 1):
                print(f"     {i}. Art. {result.article_number}: {result.article['titulo_nombre']}")
                print(f"        Score: {result.relevance_score:.3f} ({result.search_type})")
                print(f"        Texto: {result.article['texto'][:100]}...")
        else:
            print(f"   ❌ No se encontraron resultados")

def test_lexical_search():
    """Prueba solo búsqueda léxica."""
    print_section("🔤 PRUEBA 2: BÚSQUEDA LÉXICA (SIN EMBEDDINGS)")
    
    csv_path = ROOT_DIR / 'data' / 'processed' / 'cp_co_1991.csv'
    embeddings_path = ROOT_DIR / 'data' / 'index' / 'cp_co_1991_emb.npy'
    
    # Cargar artículos
    articles = []
    with csv_path.open('r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            import re
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
    
    embeddings_loader = EmbeddingsLoader(embeddings_path, articles)
    search_engine = HybridSearchEngine(articles, embeddings_loader)
    
    test_query = "derecho a la vida"
    print(f"📝 Buscando: '{test_query}'")
    print(f"   (Sin embedding semántico)\n")
    
    # Búsqueda léxica
    lexical_results = search_engine.search_lexical(test_query, top_k=5)
    
    if lexical_results:
        print(f"✓ {len(lexical_results)} resultados léxicos:")
        for i, result in enumerate(lexical_results, 1):
            print(f"  {i}. Art. {result.article_number}: {result.article['titulo_nombre']}")
            print(f"     Score: {result.relevance_score:.3f}")
    else:
        print("❌ No se encontraron resultados léxicos")

def main():
    """Ejecuta diagnóstico."""
    print("\n" + "="*70)
    print("  🧪 DIAGNÓSTICO DE BÚSQUEDA - IurisLex v2")
    print("="*70)
    
    # Verificar archivos
    print_section("📂 VERIFICACIÓN DE ARCHIVOS")
    
    csv_path = ROOT_DIR / 'data' / 'processed' / 'cp_co_1991.csv'
    emb_path = ROOT_DIR / 'data' / 'index' / 'cp_co_1991_emb.npy'
    
    print(f"CSV: {csv_path}")
    print(f"  Existe: {'✓' if csv_path.exists() else '❌'}")
    if csv_path.exists():
        size_mb = csv_path.stat().st_size / (1024*1024)
        print(f"  Tamaño: {size_mb:.2f} MB")
    
    print(f"\nEmbeddings: {emb_path}")
    print(f"  Existe: {'✓' if emb_path.exists() else '❌'}")
    if emb_path.exists():
        import numpy as np
        try:
            emb = np.load(emb_path, allow_pickle=True)
            print(f"  Shape: {emb.shape}")
            print(f"  Dtype: {emb.dtype}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Verificar datos CSV
    print_section("💾 VERIFICACIÓN DE DATOS CSV")
    load_csv_data()
    
    # Pruebas
    test_lexical_search()
    test_embeddings_search()
    
    print_section("✅ DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()
