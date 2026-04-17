import json
data = json.load(open('benchmark_results.json'))
stats = data['stats']
print('Stats keys:', list(stats.keys()))
print()
for key, value in stats.items():
    print(f'{key}: {value}')
