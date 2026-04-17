# -*- coding: utf-8 -*-
from app.models.search import SearchEngine

# Create SearchEngine instance
search_engine = SearchEngine()

# Test searches
print('Testing search functionality directly:')
print()

# Test 1: derecho a la vida
print('Test 1: derecho a la vida')
results = search_engine.search('derecho a la vida', top_k=2)
for result in results:
    art_num = result['article_number']
    score = result['score']
    print(f'  - Article {art_num}: Score {score:.4f}')

print()

# Test 2: libertad de expresion
print('Test 2: libertad de expresion')
results = search_engine.search('libertad de expresion', top_k=2)
for result in results:
    art_num = result['article_number']
    score = result['score']
    print(f'  - Article {art_num}: Score {score:.4f}')

print()

# Test 3: art 1
print('Test 3: art 1 (exact search)')
results = search_engine.search('art 1', top_k=2)
for result in results:
    art_num = result['article_number']
    score = result['score']
    print(f'  - Article {art_num}: Score {score:.4f}')
