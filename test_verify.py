#!/usr/bin/env python3
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from app.core.rag_v2 import (
    EmbeddingsLoader,
    QueryEmbedder,
    HybridSearchEngine,
    TextNormalizer
)

# Load articles
print("\n" + "="*70)
print("LOADING CLEAN ARTICLES")
print("="*70 + "\n")

csv_path = Path('data/processed/cp_co_1991.csv')
df = pd.read_csv(csv_path, encoding='latin-1')
print("CSV loaded: " + str(len(df)) + " articles\n")

articles = []
for idx, row in df.iterrows():
    article_text = str(row.get('texto', ''))
    normalizer = TextNormalizer()
    search_text = normalizer.normalize(str(row.get('articulo', '')) + " " + article_text)
    
    article = {
        'number': str(row.get('articulo', '')).replace('Articulo ', '').strip(),
        'title': row.get('articulo', ''),
        'text': article_text[:300] + "..." if len(article_text) > 300 else article_text,
        'full_text': article_text,
        'titulo': row.get('titulo_nombre', ''),
        'search_text': search_text,
    }
    articles.append(article)

print("Articles processed: " + str(len(articles)))

# Initialize components
print("\n" + "="*70)
print("INITIALIZING COMPONENTS")
print("="*70 + "\n")

embeddings_path = Path('data/cp_co_1991_emb.npy')
embeddings_loader = EmbeddingsLoader(embeddings_path, articles)

if embeddings_loader.has_embeddings():
    print("Embeddings loaded successfully!")
    print("Shape: " + str(embeddings_loader.embeddings.shape))
else:
    print("ERROR: Could not load embeddings")
    sys.exit(1)

embedder = QueryEmbedder()
print("Embedder initialized: " + str(embedder.initialized))

search_engine = HybridSearchEngine(
    articles=articles,
    embeddings_loader=embeddings_loader,
    semantic_weight=0.6,
    lexical_weight=0.4
)

# Test queries
print("\n" + "="*70)
print("TEST QUERIES")
print("="*70 + "\n")

test_queries = [
    ("derecho a la vida", "Art 11"),
    ("libertad de expresion", "Art 20"),
    ("educacion", "Art 67"),
]

success_count = 0

for query, expected in test_queries:
    print("Query: " + query)
    print("Expected: " + expected)
    
    query_embedding = embedder.embed_query(query) if embedder.initialized else None
    results = search_engine.search_semantic(query, query_embedding, top_k=3) if query_embedding is not None else []
    
    if results:
        print("Found " + str(len(results)) + " results:")
        for i, r in enumerate(results[:3], 1):
            print("  " + str(i) + ". Art " + r.article_number + " - Score: {:.4f}".format(r.relevance_score))
            if expected in ("Art " + r.article_number):
                print("     [MATCH FOUND!]")
                success_count += 1
    else:
        print("No results found")
    
    print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)
print("Articles loaded: " + str(len(articles)))
print("Embeddings shape: " + str(embeddings_loader.embeddings.shape))
print("Match ratio: " + str(success_count) + "/" + str(len(test_queries)))

if success_count >= 2:
    print("\nSUCCESS: System is working correctly!")
else:
    print("\nWARNING: Some issues detected")

