import requests
import json
import time

# Wait for server
time.sleep(5)

# Make request with longer timeout
try:
    response = requests.post('http://127.0.0.1:8000/api/consulta', 
                            json={'query': 'derecho a la vida'},
                            timeout=30)  # 30 second timeout
    
    print("Status:", response.status_code)
    print("\nFull response:")
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
except requests.exceptions.Timeout:
    print("Request timed out after 30 seconds - API is hanging")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
