import csv
from pathlib import Path

csv_path = Path('data/processed/cp_co_1991.csv')
with csv_path.open('r', encoding='latin-1') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(f'Total rows: {len(rows)}')
    print(f'Columns: {list(rows[0].keys())}')
    
    # Show first few rows
    print('\nFirst 5 rows:')
    for i, row in enumerate(rows[:5]):
        print(f'{i+1}. Art: {row.get("articulo")}, Texto preview: {row.get("texto")[:80]}')
    
    # Show rows around article 11
    print('\nSearching for article 11:')
    for i, row in enumerate(rows):
        if '11' in row.get('articulo', ''):
            print(f'{i}. {row.get("articulo")} - {row.get("texto")[:100]}')

    # Count articles with 'transitorio'
    transitorio_count = sum(1 for r in rows if 'transitorio' in r.get('articulo', '').lower())
    print(f'\nArtículos transitorios: {transitorio_count}')
