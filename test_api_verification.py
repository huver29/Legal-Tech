import json
import requests
import time

print("=" * 70)
print("VERIFICATION OF API ENDPOINTS AND RESPONSE QUALITY")
print("=" * 70)

BASE_URL = "http://localhost:8000/api"

# Test queries
queries = [
    {"query": "¿Qué son los derechos fundamentales?", "include_analysis": True, "include_case": True},
    {"query": "habeas corpus", "include_analysis": True, "include_case": True},
    {"query": "libertad de expresión", "include_analysis": True, "include_case": True},
    {"query": "derecho a la vida", "include_analysis": True, "include_case": True},
    {"query": "igualdad", "include_analysis": True, "include_case": True},
]

test_results = []

print("\n[TEST 1] Testing API Responses\n")
for i, payload in enumerate(queries, 1):
    query = payload["query"]
    print(f"Query {i}: '{query}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/consulta",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            checks = {
                "primary_article": "primary_article" in data,
                "llm_response": data.get("llm_response") and len(data.get("llm_response", "")) > 20,
                "response_validation": "response_validation" in data,
                "confidence_score": data.get("response_validation", {}).get("confidence_score", 0) > 0.3,
                "response_time": "metadata" in data,
            }
            
            print(f"  Status: ✓ 200 OK")
            print(f"  Article: {data.get('primary_article', {}).get('number', 'N/A')}")
            print(f"  Confidence: {data.get('response_validation', {}).get('confidence_score', 'N/A')}")
            print(f"  Response time: {data.get('metadata', {}).get('response_time_ms', 'N/A')}ms")
            print(f"  LLM Response (first 100 chars): {data.get('llm_response', '')[:100]}...")
            print(f"  Validation checks: {checks}")
            
            test_results.append({
                "query": query,
                "status": "PASS" if all(checks.values()) else "PARTIAL",
                "checks": checks
            })
        else:
            print(f"  Status: ✗ {response.status_code}")
            test_results.append({"query": query, "status": "FAIL"})
    except Exception as e:
        print(f"  Error: {str(e)}")
        test_results.append({"query": query, "status": "ERROR", "error": str(e)})
    
    print()

print("\n[TEST 2] Testing Cache Functionality\n")

# Same query twice
cache_query = {"query": "derechos fundamentales"}

print("First request (should be slower):")
start = time.time()
r1 = requests.post(f"{BASE_URL}/consulta", json=cache_query, timeout=10)
time1 = (time.time() - start) * 1000
print(f"  Time: {time1:.2f}ms")

time.sleep(1)

print("Second request (should be faster - cache hit):")
start = time.time()
r2 = requests.post(f"{BASE_URL}/consulta", json=cache_query, timeout=10)
time2 = (time.time() - start) * 1000
print(f"  Time: {time2:.2f}ms")

cache_improvement = ((time1 - time2) / time1 * 100) if time1 > 0 else 0
print(f"  Cache improvement: {cache_improvement:.1f}%")
if time2 < 100:
    print(f"  ✓ Cache is working (second query < 100ms)")
else:
    print(f"  ✗ Cache may not be working (second query >= 100ms)")

print("\n" + "=" * 70)
print("SUMMARY OF RESULTS")
print("=" * 70)
passed = sum(1 for r in test_results if r["status"] == "PASS")
partial = sum(1 for r in test_results if r["status"] == "PARTIAL")
failed = sum(1 for r in test_results if r["status"] in ["FAIL", "ERROR"])

print(f"Passed: {passed}/{len(test_results)}")
print(f"Partial: {partial}/{len(test_results)}")
print(f"Failed: {failed}/{len(test_results)}")

if passed + partial == len(test_results):
    print("\n✓ ALL TESTS COMPLETED SUCCESSFULLY")
else:
    print(f"\n✗ Some tests failed")
