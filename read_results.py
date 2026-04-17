import json
data = json.load(open('benchmark_results.json'))
stats = data['stats']
print('SUMMARY STATISTICS:')
print(f"Total queries: {stats['total_queries']}")
print(f"P50: {stats['percentile_50']}ms")
print(f"P95: {stats['percentile_95']}ms")
print(f"P99: {stats['percentile_99']}ms")
print(f"Mean: {stats['mean']:.2f}ms")
print(f"Min: {stats['min']}ms")
print(f"Max: {stats['max']}ms")
print()
print('=' * 50)
print('IMPROVEMENT vs BASELINE:')
print('=' * 50)
baseline_p50 = 6140
baseline_p95 = 6192
baseline_mean = 6142
imp_p50 = ((baseline_p50 - stats['percentile_50']) / baseline_p50 * 100) if stats['percentile_50'] > 0 else 0
imp_p95 = ((baseline_p95 - stats['percentile_95']) / baseline_p95 * 100) if stats['percentile_95'] > 0 else 0
imp_mean = ((baseline_mean - stats['mean']) / baseline_mean * 100) if stats['mean'] > 0 else 0
print(f"P50 improvement: {imp_p50:+.2f}%")
print(f"P95 improvement: {imp_p95:+.2f}%")
print(f"Mean improvement: {imp_mean:+.2f}%")
print()
print('Average optimization gain: {:.2f}%'.format((imp_p50 + imp_p95 + imp_mean) / 3))
