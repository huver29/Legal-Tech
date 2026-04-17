# -*- coding: utf-8 -*-
import requests
import time

base_url = 'http://127.0.0.1:8000'

# Test 1: derecho a la vida
print('Test 1: derecho a la vida')
try:
    response = requests.post(f'{base_url}/api/consulta', json={'query': 'derecho a la vida'}, timeout=5)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            for result in data['results'][:2]:
                print(f"  - Article {result.get('article_number')}: Score {result.get('score'):.4f}")
    else:
        print(f'Error: {response.status_code}')
except Exception as e:
    print(f'Exception: {e}')

print()

# Test 2: libertad de expresion
print('Test 2: libertad de expresion')
try:
    response = requests.post(f'{base_url}/api/consulta', json={'query': 'libertad de expresion'}, timeout=5)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            for result in data['results'][:2]:
                print(f"  - Article {result.get('article_number')}: Score {result.get('score'):.4f}")
    else:
        print(f'Error: {response.status_code}')
except Exception as e:
    print(f'Exception: {e}')

print()

# Test 3: art 1
print('Test 3: art 1 (exact search)')
try:
    response = requests.post(f'{base_url}/api/consulta', json={'query': 'art 1'}, timeout=5)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            for result in data['results'][:2]:
                print(f"  - Article {result.get('article_number')}: Score {result.get('score'):.4f}")
    else:
        print(f'Error: {response.status_code}')
except Exception as e:
    print(f'Exception: {e}')
