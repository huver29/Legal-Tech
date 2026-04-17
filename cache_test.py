import requests
import time

BASE_URL = "http://localhost:8000/api"

print("CACHE VERIFICATION TEST\n")

# First request - warm up
print("Warming up cache...")
r0 = requests.post(f"{BASE_URL}/consulta", json={"query": "constitución"}, timeout=10)
print(f"Status: {r0.status_code}\n")

# Test with timing
print("First request (fresh):")
start = time.time()
r1 = requests.post(f"{BASE_URL}/consulta", json={"query": "test"}, timeout=10)
elapsed1 = (time.time() - start) * 1000
content1 = len(r1.content)
print(f"  Time: {elapsed1:.2f}ms, Response size: {content1} bytes")

print("\nWaiting 0.5 seconds...")
time.sleep(0.5)

print("Second request (same query, from cache):")
start = time.time()
r2 = requests.post(f"{BASE_URL}/consulta", json={"query": "test"}, timeout=10)
elapsed2 = (time.time() - start) * 1000
content2 = len(r2.content)
print(f"  Time: {elapsed2:.2f}ms, Response size: {content2} bytes")

improvement = (elapsed1 - elapsed2) / elapsed1 * 100 if elapsed1 > 0 else 0
print(f"\nCache improvement: {improvement:.1f}%")
print(f"Response match: {r1.content == r2.content}")

if elapsed2 < elapsed1 * 0.8:
    print("\n✓ Cache IS working (2nd req ~20% faster)")
else:
    print("\n~ Cache effect not significant")
