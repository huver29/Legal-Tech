# Benchmark Comparison: Pre-optimization vs Post-optimization

# BASELINE (BEFORE)
baseline = {
    'P50': 6140,
    'P95': 6192,
    'Mean': 6142,
    'Min': 6086,
    'Max': 6205
}

# POST-OPTIMIZATION (AFTER)
post_opt = {
    'P50': 2041,
    'P95': 2077,
    'Mean': 2403.6,
    'Min': 2015,
    'Max': 6834
}

print('=' * 70)
print('BENCHMARK COMPARISON: PRE-OPTIMIZATION vs POST-OPTIMIZATION')
print('=' * 70)
print()

# Calculate improvements
improvements = {}
for metric in ['P50', 'P95', 'Mean']:
    improvement = ((baseline[metric] - post_opt[metric]) / baseline[metric]) * 100
    improvements[metric] = improvement
    print(f'{metric}:')
    print(f'  Before: {baseline[metric]:>8.1f}ms')
    print(f'  After:  {post_opt[metric]:>8.1f}ms')
    print(f'  Improvement: {improvement:>6.2f}%')
    print()

# Calculate average improvement
avg_improvement = sum(improvements.values()) / len(improvements)

print('=' * 70)
print('SUMMARY')
print('=' * 70)
print(f'P50 improvement: {improvements["P50"]:.2f}%')
print(f'P95 improvement: {improvements["P95"]:.2f}%')
print(f'Mean improvement: {improvements["Mean"]:.2f}%')
print()
print(f'Average optimization gain: {avg_improvement:.2f}%')
print()
print('=' * 70)
print('GOAL ASSESSMENT')
print('=' * 70)
print(f'Target goal: 30-50% improvement')
print(f'Achieved: {avg_improvement:.2f}%')
print()
if avg_improvement >= 50:
    print('? GOAL EXCEEDED: The optimization achieved {:.2f}% improvement,'.format(avg_improvement))
    print('  significantly exceeding the target range of 30-50%.')
    print()
    print('  Key results:')
    print(f'  - Response time reduced from ~6142ms to ~2404ms')
    print(f'  - Overall performance gain: {avg_improvement:.2f}%')
    print(f'  - The optimization was highly successful!')
elif avg_improvement >= 30:
    print(f'? GOAL MET: The optimization achieved {avg_improvement:.2f}% improvement,')
    print('  within the target range of 30-50%.')
else:
    print(f'? GOAL NOT MET: The optimization achieved {avg_improvement:.2f}% improvement,')
    print('  below the target range of 30-50%.')
print('=' * 70)
