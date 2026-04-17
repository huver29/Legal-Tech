import json
import requests
import time

BASE_URL = "http://localhost:8000/api"

print("======= FINAL QUALITY VERIFICATION =======\n")

# Test 1: Multiple queries
print("[TEST 1] Query Responses (5 test cases)")
queries = [
    "¿Qué son los derechos fundamentales?",
    "habeas corpus",
    "libertad de expresión", 
    "derecho a la vida",
    "igualdad"
]

all_pass = True
for q in queries:
    try:
        r = requests.post(f"{BASE_URL}/consulta", json={"query": q}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            conf = data.get("response_validation", {}).get("confidence_score", 0)
            resp_len = len(data.get("llm_response", ""))
            has_article = "primary_article" in data and data["primary_article"]
            if conf > 0.3 and resp_len > 20 and has_article:
                print(f"  ✓ '{q}' - Article {data['primary_article']['number']}, confidence {conf}")
            else:
                print(f"  ~ '{q}' - Partial (confidence: {conf}, response: {resp_len} chars)")
                all_pass = False
        else:
            print(f"  ✗ '{q}' - Status {r.status_code}")
            all_pass = False
    except Exception as e:
        print(f"  ✗ '{q}' - Error: {e}")
        all_pass = False

# Test 2: Cache
print("\n[TEST 2] Cache Functionality")
cache_q = {"query": "derechos"}
t1 = time.time()
r1 = requests.post(f"{BASE_URL}/consulta", json=cache_q, timeout=10)
time1 = (time.time() - t1) * 1000

time.sleep(1)

t2 = time.time()
r2 = requests.post(f"{BASE_URL}/consulta", json=cache_q, timeout=10)
time2 = (time.time() - t2) * 1000

cache_ok = time2 < 100
print(f"  1st: {time1:.1f}ms, 2nd: {time2:.1f}ms")
if cache_ok:
    print(f"  ✓ Cache working (2nd < 100ms)")
else:
    print(f"  ~ Cache may not be optimal (2nd >= 100ms)")
    all_pass = False

print("\n" + "="*40)
if all_pass:
    print("✓ QUALITY VERIFICATION PASSED")
else:
    print("~ VERIFICATION COMPLETED (SEE DETAILS)")
print("="*40)
