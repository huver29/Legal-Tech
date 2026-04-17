import requests
import json
import time

# Wait for server
time.sleep(2)

# Make request with longer timeout
response = requests.post('http://127.0.0.1:8000/api/consulta', 
                        json={'query': 'derecho a la vida'},
                        timeout=40)

data = response.json()

print("=== Key Finding ===")
print(f"article object returned: {type(data['article'])}")
print(f"article object keys: {list(data['article'].keys())}")
print(f"\nThe 'article' field is a dictionary, NOT a string")
print(f"To get article number: data['article']['number'] = '{data['article']['number']}'")

# Check what fields are available
print(f"\nAvailable article fields:")
for key, value in data['article'].items():
    print(f"  - article['{key}'] = {repr(value)[:80]}")

print(f"\n=== Accessing the Response Correctly ===")
print(f"Article Number: {data['article']['number']}")
print(f"Article Text: {data['article']['texto']}")
print(f"Search Type: {data['search']['search_type']}")
print(f"Relevance Score: {data['search']['primary_score']}")
print(f"Response Time: {data['response_time_ms']} ms")

# Now test with multiple queries to verify consistency
print(f"\n=== Testing other queries ===")
for query in ['libertad de expresion', 'art 1']:
    response = requests.post('http://127.0.0.1:8000/api/consulta', 
                            json={'query': query},
                            timeout=40)
    data = response.json()
    print(f"Query: '{query}' -> Article {data['article']['number']} (Score: {data['search']['primary_score']})")
