import requests
import json
import time

# Wait for server
time.sleep(2)

# Make request with longer timeout
response = requests.post('http://127.0.0.1:8000/api/consulta', 
                        json={'query': 'derecho a la vida'},
                        timeout=40)  # 40 second timeout

print("Status Code:", response.status_code)
print("\n=== Full Response Structure ===")
data = response.json()

# Print all keys at the root level
print("\nRoot level keys:", list(data.keys()))

# Show what each key contains
for key in data.keys():
    if isinstance(data[key], dict):
        print(f"\n'{key}' (dict) has keys: {list(data[key].keys())}")
    elif isinstance(data[key], list):
        print(f"\n'{key}' (list) has {len(data[key])} items")
        if len(data[key]) > 0 and isinstance(data[key][0], dict):
            print(f"  First item keys: {list(data[key][0].keys())}")
    else:
        val_str = str(data[key])[:100]
        print(f"\n'{key}' ({type(data[key]).__name__}): {val_str}")

# Print the full article object
print("\n=== Article Object ===")
print(json.dumps(data['article'], indent=2, ensure_ascii=False))

# Print related articles summary
print("\n=== Related Articles (first one) ===")
if data['related']:
    print(json.dumps(data['related'][0], indent=2, ensure_ascii=False)[:500])
