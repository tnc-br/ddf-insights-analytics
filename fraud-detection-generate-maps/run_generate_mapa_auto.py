#!/usr/bin/env python3
"""
🗺️ EXECUTOR AUTOMÁTICO - Generate Mapa para documento específico

Executa automaticamente sem interação do usuário
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Importar funções do generate_new_mapa
from generate_new_mapa import pd_raster

def get_firebase_client():
    """Conecta com Firebase usando credenciais locais"""
    credenciais_paths = [
        "serviceAccountKey.json",
        "../serviceAccountKey.json",
    ]
    
    for path in credenciais_paths:
        if os.path.exists(path):
            print(f"✅ Encontrou credenciais: {path}")
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
            break
    
    from google.cloud import firestore
    db = firestore.Client()
    print("✅ Conectado ao Firebase")
    return db

def buscar_documento(db, doc_id):
    """Busca documento em todas as coleções possíveis"""
    colecoes = ['trusted_samples', 'untrusted_samples', 'unknown_samples']
    
    print(f"\n🔍 Buscando documento: {doc_id}")
    
    for colecao in colecoes:
        try:
            doc_ref = db.collection(colecao).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                doc_data = doc.to_dict()
                print(f"✅ Documento encontrado na coleção: {colecao}")
                
                lat = doc_data.get('lat') or doc_data.get('latitude')
                lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude')
                
                # Extrair valores isotópicos - PRIORIZAR campo 'isotopes' se existir
                isotopes = {}
                
                # Primeiro tentar buscar do campo 'isotopes' (estruturado)
                if 'isotopes' in doc_data and isinstance(doc_data['isotopes'], dict):
                    isotopes.update(doc_data['isotopes'])
                    print(f"🧪 Isótopos do campo 'isotopes': {isotopes}")
                
                # Depois buscar campos diretos (fallback) - mas SEM sobrescrever
                isotope_fields = ['O18', 'C13', 'N15', 'H2', 'S34', 
                                 'd18O', 'd13C', 'd15N', 'd2H', 'd34S',
                                 'oxygen_18', 'carbon_13', 'nitrogen_15']
                
                for field in isotope_fields:
                    if field in doc_data and field not in isotopes:
                        isotopes[field] = doc_data[field]
                
                print(f"📍 Coordenadas: ({lat}, {lon})")
                print(f"🧪 Isótopos finais: {list(isotopes.keys())}")
                print(f"📊 Valores: {isotopes}")
                
                return {
                    'id': doc_id,
                    'lat': float(lat) if lat else None,
                    'lon': float(lon) if lon else None,
                    'isotopes': isotopes,
                    'org_name': doc_data.get('org_name', 'N/A'),
                    'colecao': colecao,
                    'raw_data': doc_data  # Incluir dados completos para debug
                }
        except Exception as e:
            continue
    
    return None

def main():
    doc_id = "6ed0ffa36587c49f5b54"
    
    print("=" * 70)
    print("🗺️  GERADOR AUTOMÁTICO DE MAPAS ISOTÓPICOS")
    print("=" * 70)
    
    # 1. Conectar ao Firebase
    db = get_firebase_client()
    
    # 2. Buscar documento
    doc_data = buscar_documento(db, doc_id)
    if not doc_data or not doc_data['isotopes']:
        print("\n❌ Documento não tem dados isotópicos!")
        return
    
    # 3. Preparar DataFrame com apenas O18
    # Buscar valor de O18 na estrutura 'isotopes' (novo) ou campo direto (antigo)
    o18_value = None
    if 'isotopes' in doc_data and isinstance(doc_data.get('isotopes'), dict):
        o18_value = doc_data['isotopes'].get('O18')
    
    if o18_value is None:
        print("\n❌ Documento não tem valor de O18 em isotopes!")
        return
    
    unknown_df = pd.DataFrame({
        'ID': [doc_data['id']],
        'O18': [o18_value]
    })
    
    print(f"\n📋 DataFrame preparado:")
    print(unknown_df)
    
    # 4. Configurar isoscape (apenas Oxigênio)
    r_path = 'isoscapes/oxygen_18_brazil.tif'
    
    # Verificar se existe
    if not os.path.exists(r_path):
        print(f"❌ Arquivo não encontrado: {r_path}")
        print("💡 Execute: python create_example_isoscapes.py")
        return
    
    # 4.5. Configurar máscara do Brasil
    mask_path = 'shapefiles/brazil_simplified.shp'
    if not os.path.exists(mask_path):
        print(f"⚠️  Máscara do Brasil não encontrada: {mask_path}")
        print("💡 Execute: python create_brazil_mask.py")
        mask_path = None
    else:
        print(f"\n🗺️  Usando máscara: {mask_path}")
    
    print(f"\n📊 Modo: SINGLE-ISOSCAPE (apenas O18)")
    print(f"   • {r_path}")
    
    # 5. Criar diretório de output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = f"output_maps/{doc_id}_{timestamp}"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"\n📁 Pasta de output: {out_dir}")
    print("\n🚀 Executando pd_raster()...")
    print("=" * 70)
    
    try:
        # EXECUTAR A FUNÇÃO PRINCIPAL!
        result = pd_raster(
            r=r_path,  # String única para single-isoscape
            unknown=unknown_df,
            prior=None,
            mask=mask_path,  # ← MÁSCARA DO BRASIL
            genplot=True,
            out_dir=out_dir
        )
        
        print("\n" + "=" * 70)
        print("✅ SUCESSO!")
        print("=" * 70)
        print(f"\n📊 Resultados gerados:")
        print(f"   • {len(result)} mapa(s) de probabilidade")
        print(f"   • Rasters GeoTIFF: {out_dir}")
        print(f"   • PDF: {out_dir}/output_pdRaster.pdf")
        
        # Abrir o PDF automaticamente
        pdf_path = f"{out_dir}/output_pdRaster.pdf"
        if os.path.exists(pdf_path):
            print(f"\n🌐 Abrindo PDF...")
            os.system(f'start "" "{pdf_path}"')
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    main()
