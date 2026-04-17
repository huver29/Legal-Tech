import requests
import json

BASE_URL = "http://localhost:8000/api"

print("SAMPLE RESPONSES FOR QUALITY VERIFICATION\n")
print("=" * 70)

queries = [
    "¿Qué son los derechos fundamentales?",
    "habeas corpus"
]

for query in queries:
    print(f"\nQuery: {query}")
    print("-" * 70)
    
    r = requests.post(f"{BASE_URL}/consulta", json={"query": query}, timeout=10)
    data = r.json()
    
    print(f"Article Found: Artículo {data['primary_article']['number']}")
    print(f"Confidence Score: {data['response_validation']['confidence_score']}")
    print(f"Valid Response: {data['response_validation']['is_valid']}")
    print(f"\nLLM Response (first 400 chars):")
    print(data['llm_response'][:400])
    print("...[truncated]")
