import json
data = json.load(open('benchmark_results.json'))
print('Top-level keys:', list(data.keys()))
if 'statistics' in data:
    print('Statistics:', data['statistics'])
if 'summary' in data:
    print('Summary:', data['summary'])
