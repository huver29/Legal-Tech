#!/usr/bin/env python3
"""
Script para regenerar embeddings con las dimensiones correctas (384).
"""
import sys
import csv
from pathlib import Path
import numpy as np
from tqdm import tqdm

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from app.core.rag_v2 import QueryEmbedder, TextNormalizer

def generate_embeddings():
    """Regenera embeddings para todos los artículos."""
    
    # Paths
    csv_path = ROOT_DIR / 'data' / 'processed' / 'cp_co_1991.csv'
    output_path = ROOT_DIR / 'data' / 'index' / 'cp_co_1991_emb.npy'
    
    print("="*70)
    print("  🔄 REGENERANDO EMBEDDINGS")
    print("="*70)
    
    # Verificar CSV
    if not csv_path.exists():
        print(f"❌ CSV no encontrado: {csv_path}")
        return False
    
    print(f"\n📂 CSV: {csv_path}")
    print(f"📁 Output: {output_path}\n")
    
    # Cargar datos
    print("1️⃣ Leyendo CSV...")
    articles_text = []
    
    with csv_path.open('r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Crear texto combinado del artículo
            text_parts = [
                row.get('articulo', ''),
                row.get('titulo_nombre', ''),
                row.get('capitulo_nombre', ''),
                row.get('texto', '')
            ]
            combined_text = ' '.join(str(p).strip() for p in text_parts if p)
            articles_text.append(combined_text)
    
    print(f"   ✓ {len(articles_text)} artículos cargados")
    
    # Crear embedder
    print("\n2️⃣ Inicializando modelo de embeddings...")
    embedder = QueryEmbedder(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    
    if not embedder.initialized:
        print("   ❌ Error inicializando modelo")
        return False
    
    print("   ✓ Modelo cargado")
    
    # Generar embeddings
    print("\n3️⃣ Generando embeddings...")
    
    try:
        # Procesar en lotes para evitar problemas de memoria
        batch_size = 50
        embeddings = []
        
        for i in range(0, len(articles_text), batch_size):
            batch = articles_text[i:i+batch_size]
            batch_embeddings = embedder.embed_queries(batch)
            
            # Filtrar None values
            valid_embeddings = [e for e in batch_embeddings if e is not None]
            embeddings.extend(valid_embeddings)
            
            progress = min(i + batch_size, len(articles_text))
            print(f"   Procesados: {progress}/{len(articles_text)} artículos", end='\r')
        
        print(f"   ✓ {len(embeddings)} embeddings generados              ")
        
        # Convertir a numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        print(f"   ✓ Shape: {embeddings_array.shape}")
        print(f"   ✓ Dtype: {embeddings_array.dtype}")
        
        # Guardar
        print("\n4️⃣ Guardando embeddings...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(output_path, embeddings_array)
        print(f"   ✓ Guardado en: {output_path}")
        
        # Verificar
        print("\n5️⃣ Verificando...")
        loaded = np.load(output_path, allow_pickle=True)
        print(f"   ✓ Verificación: {loaded.shape}")
        
        print("\n" + "="*70)
        print("  ✅ EMBEDDINGS REGENERADOS EXITOSAMENTE")
        print("="*70)
        print(f"\n📊 Resumen:")
        print(f"   Artículos: {len(articles_text)}")
        print(f"   Dimensiones: {embeddings_array.shape[1]} (384-dim)")
        print(f"   Tamaño: {embeddings_array.nbytes / (1024*1024):.2f} MB")
        print(f"\n✨ Ahora la búsqueda semántica funcionará correctamente.\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = generate_embeddings()
    sys.exit(0 if success else 1)
