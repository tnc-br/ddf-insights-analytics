#!/usr/bin/env python3
"""
🗺️ EXECUTOR - Generate New Mapa com dados do Firebase

Busca documento no Firebase e gera mapa isotópico probabilístico
usando a função pd_raster do generate_new_mapa.py

Uso:
    python execute_generate_mapa.py <document_id>

Exemplo:
    python execute_generate_mapa.py 6ed0ffa36587c49f5b54
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
        "firebase-key.json",
        "service-account.json"
    ]
    
    for path in credenciais_paths:
        if os.path.exists(path):
            print(f"✅ Encontrou credenciais: {path}")
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
            break
    else:
        print("❌ Nenhum arquivo de credenciais encontrado!")
        print("💡 Coloque serviceAccountKey.json na pasta atual")
        return None
    
    try:
        from google.cloud import firestore
        db = firestore.Client()
        print("✅ Conectado ao Firebase")
        return db
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

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
                
                # Extrair coordenadas
                lat = doc_data.get('lat') or doc_data.get('latitude') or doc_data.get('location', {}).get('lat')
                lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude') or doc_data.get('location', {}).get('lon')
                
                # Extrair valores isotópicos (procurar campos comuns)
                isotopes = {}
                isotope_fields = ['O18', 'C13', 'N15', 'H2', 'S34', 
                                 'd18O', 'd13C', 'd15N', 'd2H', 'd34S',
                                 'oxygen_18', 'carbon_13', 'nitrogen_15']
                
                for field in isotope_fields:
                    if field in doc_data:
                        isotopes[field] = doc_data[field]
                
                print(f"\n📍 Coordenadas: ({lat}, {lon})")
                print(f"🧪 Isótopos encontrados: {list(isotopes.keys())}")
                print(f"📊 Valores: {isotopes}")
                
                return {
                    'id': doc_id,
                    'lat': float(lat) if lat else None,
                    'lon': float(lon) if lon else None,
                    'isotopes': isotopes,
                    'org_name': doc_data.get('org_name', 'N/A'),
                    'colecao': colecao,
                    'raw_data': doc_data
                }
        except Exception as e:
            print(f"⚠️  Erro ao buscar em {colecao}: {e}")
            continue
    
    print(f"❌ Documento '{doc_id}' não encontrado em nenhuma coleção")
    return None

def preparar_dados_para_pd_raster(doc_data):
    """Converte dados do Firebase para formato esperado por pd_raster"""
    
    if not doc_data['isotopes']:
        print("\n❌ Nenhum dado isotópico encontrado no documento!")
        print("💡 Campos procurados: O18, C13, N15, d18O, d13C, d15N, etc.")
        return None
    
    # Criar DataFrame com ID e valores isotópicos
    data_dict = {'ID': [doc_data['id']]}
    data_dict.update(doc_data['isotopes'])
    
    unknown_df = pd.DataFrame(data_dict)
    
    print(f"\n📋 DataFrame preparado:")
    print(unknown_df)
    print(f"\n📊 Colunas: {list(unknown_df.columns)}")
    print(f"📊 Shape: {unknown_df.shape}")
    
    return unknown_df

def executar_geracao_mapa(doc_id):
    """Função principal que orquestra todo o processo"""
    
    print("=" * 70)
    print("🗺️  GERADOR DE MAPAS ISOTÓPICOS - Generate New Mapa")
    print("=" * 70)
    
    # 1. Conectar ao Firebase
    db = get_firebase_client()
    if not db:
        return False
    
    # 2. Buscar documento
    doc_data = buscar_documento(db, doc_id)
    if not doc_data:
        return False
    
    # 3. Verificar se tem coordenadas (necessário para isoscapes)
    if not doc_data['lat'] or not doc_data['lon']:
        print("\n❌ Documento não possui coordenadas válidas!")
        return False
    
    # 4. Preparar dados
    unknown_df = preparar_dados_para_pd_raster(doc_data)
    if unknown_df is None:
        return False
    
    # 5. Verificar se temos isoscapes disponíveis
    print("\n" + "=" * 70)
    print("⚠️  NOTA IMPORTANTE SOBRE ISOSCAPES")
    print("=" * 70)
    print("""
Para gerar o mapa, você precisa de arquivos raster (GeoTIFF) com isoscapes.

Exemplo de estrutura esperada:
  - isoscapes/
    ├── oxygen_18_mean_sd.tif    (2 bandas: média e desvio padrão)
    ├── carbon_13_mean_sd.tif
    └── nitrogen_15_mean_sd.tif

OPÇÕES:

1. SINGLE ISOSCAPE (1 isótopo):
   r_path = 'isoscapes/oxygen_18_mean_sd.tif'
   
2. MULTI-ISOSCAPE (vários isótopos combinados):
   r_paths = [
       'isoscapes/oxygen_18_mean_sd.tif',
       'isoscapes/carbon_13_mean_sd.tif',
       'isoscapes/nitrogen_15_mean_sd.tif'
   ]

💡 Se você não tem os isoscapes, este script vai gerar um EXEMPLO
   com dados simulados apenas para demonstração.
    """)
    
    resposta = input("\n❓ Você tem arquivos de isoscape disponíveis? (s/N): ").strip().lower()
    
    if resposta == 's':
        print("\n📂 Digite o caminho do(s) arquivo(s) isoscape:")
        print("   (Para múltiplos, separe com vírgula)")
        caminhos = input("   Caminho(s): ").strip()
        
        if ',' in caminhos:
            r_paths = [p.strip() for p in caminhos.split(',')]
            print(f"\n📊 Modo: MULTI-ISOSCAPE ({len(r_paths)} isótopos)")
        else:
            r_paths = caminhos
            print(f"\n📊 Modo: SINGLE-ISOSCAPE")
        
        # Verificar se arquivos existem
        paths_to_check = r_paths if isinstance(r_paths, list) else [r_paths]
        for path in paths_to_check:
            if not os.path.exists(path):
                print(f"❌ Arquivo não encontrado: {path}")
                return False
        
        # Criar diretório de output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = f"output_maps/{doc_id}_{timestamp}"
        os.makedirs(out_dir, exist_ok=True)
        
        print(f"\n📁 Pasta de output: {out_dir}")
        print("\n🚀 Executando pd_raster()...")
        print("=" * 70)
        
        try:
            # EXECUTAR A FUNÇÃO PRINCIPAL!
            result = pd_raster(
                r=r_paths,
                unknown=unknown_df,
                prior=None,  # Você pode adicionar um prior se tiver
                mask=None,   # Você pode adicionar uma máscara se quiser
                genplot=True,  # IMPORTANTE: gera os plots!
                out_dir=out_dir
            )
            
            print("\n" + "=" * 70)
            print("✅ SUCESSO!")
            print("=" * 70)
            print(f"\n📊 Resultados gerados:")
            print(f"   • {len(result)} mapa(s) de probabilidade")
            print(f"   • Rasters GeoTIFF salvos em: {out_dir}")
            print(f"   • PDF com visualização: {out_dir}/output_pdRaster.pdf")
            
            print(f"\n🌐 Para visualizar:")
            print(f"   1. Abra: {out_dir}/output_pdRaster.pdf")
            print(f"   2. Ou abra os arquivos .tif em QGIS/ArcGIS")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro ao executar pd_raster: {e}")
            import traceback
            print(traceback.format_exc())
            return False
    
    else:
        print("\n" + "=" * 70)
        print("💡 MODO DEMONSTRAÇÃO")
        print("=" * 70)
        print("""
Sem isoscapes reais, não é possível gerar o mapa probabilístico.

Para usar esta funcionalidade completamente, você precisa:

1. Obter isoscapes de referência (rasters GeoTIFF com 2 bandas)
2. Ou gerar isoscapes usando ferramentas como o pacote R 'isoscape'
3. Ou usar dados públicos de projetos como IsoMAP (http://isomap.org)

ALTERNATIVA:
Execute o sistema principal do TimberID que já tem integração
com Earth Engine e MapBiomas:

    python fraud-detection-update-sample/test_local.py
    
Ou publique no Pub/Sub para processar via Cloud Function:

    python easy_pubsub.py {doc_id}
        """)
        return False

def main():
    if len(sys.argv) < 2:
        print("""
🗺️ EXECUTOR - Generate New Mapa

Uso:
    python execute_generate_mapa.py <document_id>

Exemplo:
    python execute_generate_mapa.py 6ed0ffa36587c49f5b54

💡 Este script:
   1. Busca o documento no Firebase
   2. Extrai dados isotópicos
   3. Gera mapa probabilístico de origem
   4. Salva visualização em PDF

📋 Pré-requisitos:
   - serviceAccountKey.json na pasta
   - Arquivos isoscape (.tif) disponíveis
   - Dependências instaladas (ver requirements.txt)
        """)
        return
    
    doc_id = sys.argv[1]
    executar_geracao_mapa(doc_id)

if __name__ == "__main__":
    main()
