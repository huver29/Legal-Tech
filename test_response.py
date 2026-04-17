import requests
import json
import time

# Wait for server
time.sleep(3)

# Make request
response = requests.post('http://127.0.0.1:8000/api/consulta', 
                        json={'query': 'derecho a la vida'},
                        timeout=10)

print("Status:", response.status_code)
print("\nFull response:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False)[:2000])
