#!/usr/bin/env python3
"""
Script para crear un CSV limpio sin artículos transitorios.
"""
import sys
import csv
from pathlib import Path

def clean_csv():
    """Crea CSV limpio sin artículos transitorios."""
    
    print("="*70)
    print("  🧹 LIMPIANDO CSV - REMOVIENDO ARTÍCULOS TRANSITORIOS")
    print("="*70 + "\n")
    
    csv_path = Path('data/processed/cp_co_1991.csv')
    csv_backup = Path('data/processed/cp_co_1991_backup.csv')
    
    print(f"1️⃣ Leyendo CSV original: {csv_path}")
    
    # Leer CSV
    rows = []
    with csv_path.open('r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"   Total de filas: {len(rows)}")
    
    # Filtrar artículos transitorios
    print(f"\n2️⃣ Filtrando artículos transitorios...")
    clean_rows = []
    transitorio_count = 0
    
    for row in rows:
        articulo = row.get('articulo', '').lower()
        
        # Si contiene la palabra "transitorio", excluirlo
        if 'transitorio' in articulo:
            transitorio_count += 1
        else:
            clean_rows.append(row)
    
    print(f"   Artículos transitorios removidos: {transitorio_count}")
    print(f"   Artículos principales restantes: {len(clean_rows)}")
    
    # Crear backup
    print(f"\n3️⃣ Creando backup...")
    import shutil
    if not csv_backup.exists():
        shutil.copy(csv_path, csv_backup)
        print(f"   ✓ Backup guardado: {csv_backup}")
    else:
        print(f"   ℹ️  Backup ya existe")
    
    # Escribir CSV limpio
    print(f"\n4️⃣ Escribiendo CSV limpio...")
    with csv_path.open('w', encoding='latin-1', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(clean_rows)
    
    print(f"   ✓ {len(clean_rows)} artículos guardados en {csv_path}")
    
    # Verificar
    print(f"\n5️⃣ Verificando CSV limpio...")
    with csv_path.open('r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        test_rows = list(reader)
    
    transitorio_check = sum(1 for r in test_rows if 'transitorio' in r.get('articulo', '').lower())
    print(f"   Artículos transitorios encontrados: {transitorio_check}")
    
    if transitorio_check == 0:
        print(f"   ✓ CSV limpio verificado")
    else:
        print(f"   ❌ Todavía hay transitorios")
        return False
    
    print(f"\n6️⃣ Mostrando primeros artículos:")
    for i, row in enumerate(test_rows[:5]):
        print(f"   {i+1}. {row.get('articulo')} - {row.get('titulo_nombre')}")
    
    print("\n" + "="*70)
    print("  ✅ CSV LIMPIADO EXITOSAMENTE")
    print("="*70)
    print(f"\n📊 Resumen:")
    print(f"   Artículos principales: {len(clean_rows)}")
    print(f"   Artículos transitorios removidos: {transitorio_count}")
    print(f"   Total original: {len(rows)}")
    
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   Debes regenerar los embeddings después de esto.")
    print(f"   Ejecuta: python regenerate_embeddings.py\n")
    
    return True

if __name__ == "__main__":
    try:
        success = clean_csv()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
