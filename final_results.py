import json
data = json.load(open('benchmark_results.json'))
stats = data['stats']
times = stats['response_times']
print('SUMMARY STATISTICS:')
print(f"Total queries: {stats['total_queries']}")
print(f"Successful queries: {stats['successful']}")
print(f"P50 (Median): {times['p50']}ms")
print(f"P75: {times['p75']}ms")
print(f"P95: {times['p95']}ms")
print(f"P99: {times['p99']}ms")
print(f"Mean: {times['mean']:.2f}ms")
print(f"Min: {times['min']}ms")
print(f"Max: {times['max']}ms")
print(f"Std Dev: {times['stdev']:.2f}ms")
print(f"Benchmark duration: {stats['benchmark_duration_seconds']}s")
print()
print('=' * 50)
print('IMPROVEMENT vs BASELINE:')
print('=' * 50)
baseline_p50 = 6140
baseline_p95 = 6192
baseline_mean = 6142
imp_p50 = ((baseline_p50 - times['p50']) / baseline_p50 * 100)
imp_p95 = ((baseline_p95 - times['p95']) / baseline_p95 * 100)
imp_mean = ((baseline_mean - times['mean']) / baseline_mean * 100)
print(f"P50 improvement: {imp_p50:.2f}%")
print(f"P95 improvement: {imp_p95:.2f}%")
print(f"Mean improvement: {imp_mean:.2f}%")
print()
avg_improvement = (imp_p50 + imp_p95 + imp_mean) / 3
print('=' * 50)
print(f'Average optimization gain: {avg_improvement:.2f}%')
print('=' * 50)
