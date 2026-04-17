# -*- coding: utf-8 -*-
import requests
import time

# Wait for server to be ready
time.sleep(3)

base_url = 'http://127.0.0.1:8000'

# Test 1: derecho a la vida
print('Test 1: derecho a la vida')
response = requests.post(f'{base_url}/api/consulta', json={'query': 'derecho a la vida'})
if response.status_code == 200:
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        for result in data['results'][:2]:
            print(f"  - Article {result.get('article_number')}: Score {result.get('score'):.4f}")
else:
    print(f'Error: {response.status_code}')

print()

# Test 2: libertad de expresion
print('Test 2: libertad de expresion')
response = requests.post(f'{base_url}/api/consulta', json={'query': 'libertad de expresion'})
if response.status_code == 200:
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        for result in data['results'][:2]:
            print(f"  - Article {result.get('article_number')}: Score {result.get('score'):.4f}")
else:
    print(f'Error: {response.status_code}')

print()

# Test 3: art 1
print('Test 3: art 1 (exact search)')
response = requests.post(f'{base_url}/api/consulta', json={'query': 'art 1'})
if response.status_code == 200:
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        for result in data['results'][:2]:
            print(f"  - Article {result.get('article_number')}: Score {result.get('score'):.4f}")
else:
    print(f'Error: {response.status_code}')
