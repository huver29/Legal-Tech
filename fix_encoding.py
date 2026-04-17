#!/usr/bin/env python3
"""
Script para diagnosticar y reparar problemas de encoding en el CSV.
"""
import sys
import csv
from pathlib import Path

def diagnose_encoding():
    """Diagnostica problemas de encoding."""
    
    print("="*70)
    print("  🔍 DIAGNÓSTICO DE ENCODING")
    print("="*70 + "\n")
    
    csv_path = Path('data/processed/cp_co_1991.csv')
    
    # Leer con diferentes encodings
    encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    print("Intentando leer CSV con diferentes encodings:\n")
    
    for enc in encodings_to_try:
        try:
            with csv_path.open('r', encoding=enc) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # Verificar un artículo
                if rows:
                    sample_text = rows[0].get('articulo', '')
                    print(f"✓ {enc.upper()}: {sample_text}")
                    
                    # Verificar si contiene caracteres especiales correctamente
                    if 'Artículo' in sample_text or 'Capítulo' in sample_text:
                        print(f"   ✅ Encoding correcto - caracteres acentuados OK\n")
                        return enc, rows
                    elif 'ArtÃ' in sample_text:
                        print(f"   ⚠️  Encoding incorrecto - caracteres corruptos\n")
                    
        except Exception as e:
            print(f"❌ {enc.upper()}: Error - {str(e)[:50]}\n")
    
    return None, []

def fix_encoding():
    """Repara el encoding del CSV."""
    
    enc, rows = diagnose_encoding()
    
    if not enc or not rows:
        print("❌ No se pudo diagnosticar encoding")
        return False
    
    if enc == 'utf-8':
        print("✅ El encoding ya es UTF-8 - no se necesita conversión\n")
        return True
    
    print(f"Convirtiendo de {enc} a UTF-8...\n")
    
    csv_path = Path('data/processed/cp_co_1991.csv')
    
    # Leer con encoding detectado
    with csv_path.open('r', encoding=enc) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Escribir con UTF-8
    with csv_path.open('w', encoding='utf-8', newline='') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"✓ {len(rows)} filas escritas con UTF-8\n")
    
    # Verificar
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        test_rows = list(reader)
    
    sample = test_rows[0].get('articulo', '')
    print(f"Verificación: {sample}")
    
    if 'Artículo' in sample or 'Art' in sample:
        print("✅ Encoding reparado exitosamente\n")
        return True
    else:
        print("⚠️  Podría haber problemas aún\n")
        return False

if __name__ == "__main__":
    try:
        fix_encoding()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
