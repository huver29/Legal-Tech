#!/usr/bin/env python3
import csv

f = open('data/processed/cp_co_1991.csv', 'r', encoding='utf-8')
reader = csv.DictReader(f)
rows = list(reader)

print("CSV Structure Analysis")
print("=" * 80)
print(f"Total filas: {len(rows)}\n")

# Contar por tipo
artículos_regulares = []
artículos_transitorios = []

for row in rows:
    articulo_text = row['articulo'].lower()
    if 'transitorio' in articulo_text:
        artículos_transitorios.append(row)
    else:
        artículos_regulares.append(row)

print(f"Artículos regulares: {len(artículos_regulares)}")
print(f"Artículos transitorios: {len(artículos_transitorios)}")

print("\nPrimeros 10 artículos regulares:")
for i, row in enumerate(artículos_regulares[:10]):
    print(f"  {i+1}. {row['articulo'][:50]}")

print("\nPrimeros 10 artículos transitorios:")
for i, row in enumerate(artículos_transitorios[:10]):
    print(f"  {i+1}. {row['articulo'][:50]}")
