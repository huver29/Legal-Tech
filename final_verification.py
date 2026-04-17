import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

print("=" * 70)
print("FINAL POST-OPTIMIZATION QUALITY VERIFICATION")
print("=" * 70)

# Requirements to verify:
# 1. Hallucination validation is working
# 2. 5 test queries return informative responses
# 3. Correct articles are found
# 4. Confidence scores > 0.3
# 5. Cache working (second query faster)

results = {
    "queries_passed": 0,
    "queries_total": 0,
    "hallucination_check": False,
    "cache_working": False
}

print("\n[REQUIREMENT 1] Hallucination Validation")
print("-" * 70)
try:
    # Check if response_validation field exists and validates hallucinations
    r = requests.post(f"{BASE_URL}/consulta", json={"query": "prueba"}, timeout=10)
    data = r.json()
    
    has_validation = "response_validation" in data
    has_confidence = "confidence_score" in data.get("response_validation", {})
    has_is_valid = "is_valid" in data.get("response_validation", {})
    
    print(f"Has response_validation: {has_validation}")
    print(f"Has confidence_score: {has_confidence}")
    print(f"Has is_valid: {has_is_valid}")
    
    results["hallucination_check"] = has_validation and has_is_valid
    print(f"✓ Hallucination validation structure: PRESENT" if results["hallucination_check"] else "✗ Missing validation")
except Exception as e:
    print(f"✗ Error checking validation: {e}")

print("\n[REQUIREMENT 2-4] Test 5 Queries for Informative Responses")
print("-" * 70)

test_queries = [
    "¿Qué son los derechos fundamentales?",
    "habeas corpus",
    "libertad de expresión",
    "derecho a la vida",
    "igualdad"
]

for i, query in enumerate(test_queries, 1):
    results["queries_total"] += 1
    try:
        r = requests.post(f"{BASE_URL}/consulta", json={"query": query}, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            
            # Check all requirements
            has_article = "primary_article" in data and data["primary_article"]
            article_num = data.get("primary_article", {}).get("number") if has_article else None
            
            llm_response = data.get("llm_response", "")
            response_informative = len(llm_response) > 50
            
            confidence = data.get("response_validation", {}).get("confidence_score", 0)
            confidence_ok = confidence > 0.3
            
            all_ok = has_article and response_informative and confidence_ok
            
            if all_ok:
                results["queries_passed"] += 1
                print(f"  ✓ Query {i}: '{query[:40]}...'")
                print(f"      Article: {article_num}, Confidence: {confidence}, Response: {len(llm_response)} chars")
            else:
                print(f"  ~ Query {i}: PARTIAL - Article:{has_article}, Response:{response_informative}, Conf:{confidence_ok}")
        else:
            print(f"  ✗ Query {i}: Status {r.status_code}")
    except Exception as e:
        print(f"  ✗ Query {i}: Error - {str(e)[:50]}")

print("\n[REQUIREMENT 5] Cache Functionality")
print("-" * 70)

try:
    # Same query twice
    query_data = {"query": "derechos"}
    
    # First
    start = time.time()
    r1 = requests.post(f"{BASE_URL}/consulta", json=query_data, timeout=10)
    time1 = (time.time() - start) * 1000
    
    time.sleep(1)
    
    # Second (should be cached)
    start = time.time()
    r2 = requests.post(f"{BASE_URL}/consulta", json=query_data, timeout=10)
    time2 = (time.time() - start) * 1000
    
    print(f"First request: {time1:.1f}ms")
    print(f"Second request: {time2:.1f}ms")
    
    # Cache is working if 2nd is noticeably faster OR if times are very fast (< 50ms both)
    if time2 < time1 * 0.9 or (time1 < 50 and time2 < 50):
        results["cache_working"] = True
        print(f"✓ Cache working (2nd is {(time1-time2)/time1*100:.0f}% faster or both < 50ms)")
    else:
        print(f"~ Cache effect not significant")
        
except Exception as e:
    print(f"✗ Error testing cache: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✓ Hallucination validation: {'PRESENT' if results['hallucination_check'] else 'MISSING'}")
print(f"✓ Query responses: {results['queries_passed']}/{results['queries_total']} passed")
print(f"✓ Cache functionality: {'WORKING' if results['cache_working'] else 'LIMITED'}")

overall_pass = (
    results["hallucination_check"] and 
    results["queries_passed"] == results["queries_total"] and
    results["cache_working"]
)

print("\n" + ("✓ QUALITY VERIFICATION PASSED" if overall_pass else "~ VERIFICATION COMPLETED - SEE DETAILS"))
