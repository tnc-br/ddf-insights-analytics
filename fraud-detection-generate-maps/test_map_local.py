#!/usr/bin/env python3
"""
🧪 TESTE LOCAL - Gera Mapa REAL e Sobe no Storage
Executa LOCALMENTE: busca Firebase → gera mapa → upload Storage → mostra URL
"""

import os
import sys

def get_firebase_client():
    """Conecta com Firebase"""
    credenciais_paths = [
        "serviceAccountKey.json",
        "../serviceAccountKey.json"
    ]
    
    for path in credenciais_paths:
        if os.path.exists(path):
            print(f"✅ Credenciais encontradas: {path}")
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
            break
    
    try:
        from google.cloud import firestore
        from firebase_admin import initialize_app, storage, credentials
        
        # Inicializar Firebase Admin
        try:
            cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
            app = initialize_app(cred, {
                'storageBucket': 'timberid-public-to-internet'
            })
            print("✅ Firebase Admin inicializado")
        except ValueError as e:
            if "already exists" in str(e):
                print("✅ Firebase Admin já inicializado")
            else:
                raise
        
        db = firestore.Client()
        bucket = storage.bucket()
        
        return db, bucket
        
    except Exception as e:
        print(f"❌ Erro ao conectar Firebase: {e}")
        return None, None

def get_documento(db, doc_id):
    """Busca documento no Firestore"""
    try:
        colecoes = ['trusted_samples', 'unknown_samples', 'untrusted_samples']
        print(f"\n🔍 Buscando documento: {doc_id}")
        
        for colecao in colecoes:
            try:
                doc_ref = db.collection(colecao).document(doc_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    doc_data = doc.to_dict()
                    print(f"✅ Encontrado na coleção: {colecao}")
                    
                    lat = doc_data.get('lat') or doc_data.get('latitude')
                    lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude')
                    
                    if lat and lon:
                        print(f"✅ Coordenadas: ({lat}, {lon})")
                        return {
                            'id': doc_id,
                            'lat': float(lat),
                            'lon': float(lon),
                            'colecao': colecao
                        }
            except:
                continue
        
        print(f"❌ Documento '{doc_id}' não encontrado")
        return None
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def gerar_mapa(lat, lon, doc_id):
    """Gera o mapa usando Earth Engine"""
    try:
        print(f"\n🗺️  GERANDO MAPA COM EARTH ENGINE...")
        
        # Importar bibliotecas necessárias
        import ee
        import geemap
        from google.oauth2 import service_account
        
        # Autenticar Earth Engine
        print("🔑 Autenticando Earth Engine...")
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=[
                'https://www.googleapis.com/auth/earthengine',
                'https://www.googleapis.com/auth/cloud-platform',
                'https://www.googleapis.com/auth/devstorage.read_write'
            ]
        )
        
        project_id = 'river-sky-386919'
        ee.Initialize(credentials, project=project_id)
        print("✅ Earth Engine inicializado")
        
        # MapBiomas Collection 8
        MAPBIOMAS_IMAGE = "projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_deforestation_regeneration_v1"
        
        # Carregar imagem MapBiomas
        print("📦 Carregando MapBiomas Collection 8...")
        land_use_mapbiomas_image = ee.Image(MAPBIOMAS_IMAGE)
        
        # Gerar mapa base
        print("🎨 Gerando mapa base...")
        gee_mapbiomas_map = geemap.Map()
        gee_mapbiomas_map.add_basemap("SATELLITE")
        gee_mapbiomas_map.addLayer(land_use_mapbiomas_image, {}, "Brazil Land Use")
        
        # Criar buffers
        print(f"📍 Processando coordenadas ({lat}, {lon})...")
        point = ee.Geometry.Point(lon, lat)
        radius_1km_buffer = point.buffer(1000)
        radius_10km_buffer = point.buffer(10000)
        
        print("   ⚡ Criando buffer 1km...")
        print("   ⚡ Criando buffer 10km...")
        
        # Adicionar layers
        gee_mapbiomas_map.addLayer(
            land_use_mapbiomas_image.mask().geometry().difference(radius_10km_buffer),
            {},
            "10 km radius mask"
        )
        gee_mapbiomas_map.addLayer(
            radius_1km_buffer,
            {"color": "white"},
            "1 km radius mask"
        )
        gee_mapbiomas_map.centerObject(radius_10km_buffer, 11)
        
        # Gerar HTML
        print("   ⚡ Gerando arquivo HTML...")
        download_dir = os.getcwd()
        html_file = os.path.join(download_dir, f"{doc_id}.html")
        
        gee_mapbiomas_map.to_html(
            filename=html_file,
            title="Land Use Details",
            width="100%",
            height="300px"
        )
        
        print(f"✅ Mapa HTML gerado: {html_file}")
        return html_file
        
    except Exception as e:
        print(f"❌ Erro ao gerar mapa: {e}")
        import traceback
        print(f"\n🔍 Traceback:")
        print(traceback.format_exc())
        return None

def upload_para_storage(html_file, doc_id, bucket):
    """Faz upload do HTML para Firebase Storage"""
    try:
        print(f"\n📤 FAZENDO UPLOAD PARA FIREBASE STORAGE...")
        
        folder_name = "timberid-maps"
        blob_path = f"{folder_name}/{doc_id}.html"
        
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(html_file)
        
        # Gerar URL pública
        public_url = f"https://storage.googleapis.com/{bucket.name}/{blob_path}"
        
        print(f"✅ Upload concluído!")
        print(f"📁 Path: {blob_path}")
        print(f"🌐 URL: {public_url}")
        
        # Limpar arquivo local
        os.remove(html_file)
        print(f"🧹 Arquivo local removido")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        import traceback
        print(traceback.format_exc())
        return None

def salvar_url_no_firestore(db, doc_id, colecao, url):
    """Salva a URL no documento do Firestore"""
    try:
        print(f"\n📝 Salvando URL no Firestore...")
        
        from firebase_admin import firestore as admin_firestore
        
        doc_ref = db.collection(colecao).document(doc_id)
        doc_ref.update({
            'map_url': url,
            'map_updated_at': admin_firestore.SERVER_TIMESTAMP
        })
        
        print(f"✅ URL salva no documento: {colecao}/{doc_id}")
        
    except Exception as e:
        print(f"⚠️  Não foi possível salvar URL: {e}")

def main():
    if len(sys.argv) < 2:
        print("""
🧪 TESTE LOCAL - Gera Mapa REAL e Sobe no Storage

Uso:
  python test_map_local.py <document_id>

Exemplo:
  python test_map_local.py 6ed0ffa36587c49f5b54

💡 Este script executa LOCALMENTE:
   1. Busca documento no Firebase
   2. Gera mapa REAL com Earth Engine
   3. Faz upload no Firebase Storage
   4. Mostra URL pública para abrir no navegador
   5. (Opcional) Salva URL no Firestore

⚠️  ATENÇÃO: Requer permissões Earth Engine!
        """)
        return

    doc_id = sys.argv[1]
    
    print("""
╔════════════════════════════════════════════════╗
║   🧪 TESTE LOCAL - GERAÇÃO DE MAPA REAL      ║
║   Firebase + Earth Engine + Storage           ║
╚════════════════════════════════════════════════╝
    """)
    
    # 1. Conectar Firebase
    print("\n📡 PASSO 1: Conectar ao Firebase...")
    db, bucket = get_firebase_client()
    
    if not db or not bucket:
        print("\n❌ Falha na conexão com Firebase")
        return
    
    # 2. Buscar documento
    print("\n📋 PASSO 2: Buscar documento...")
    doc_data = get_documento(db, doc_id)
    
    if not doc_data:
        print("\n❌ Documento não encontrado")
        return
    
    # 3. Gerar mapa
    print("\n🗺️  PASSO 3: Gerar mapa com Earth Engine...")
    html_file = gerar_mapa(doc_data['lat'], doc_data['lon'], doc_id)
    
    if not html_file:
        print("\n❌ Falha na geração do mapa")
        return
    
    # 4. Upload para Storage
    print("\n📤 PASSO 4: Upload para Firebase Storage...")
    public_url = upload_para_storage(html_file, doc_id, bucket)
    
    if not public_url:
        print("\n❌ Falha no upload")
        return
    
    # 5. (Opcional) Salvar URL no Firestore
    print("\n💾 PASSO 5 (Opcional): Salvar URL no Firestore...")
    resposta = input("Deseja salvar a URL no documento do Firestore? (s/n): ").lower()
    
    if resposta == 's':
        salvar_url_no_firestore(db, doc_id, doc_data['colecao'], public_url)
    else:
        print("⏭️  URL não salva no Firestore")
    
    # Resultado final
    print("\n" + "="*60)
    print("🎉 TESTE COMPLETO!")
    print("="*60)
    print(f"\n📊 RESULTADO:")
    print(f"   Documento: {doc_id}")
    print(f"   Coleção: {doc_data['colecao']}")
    print(f"   Coordenadas: ({doc_data['lat']}, {doc_data['lon']})")
    print(f"\n🌐 URL DO MAPA:")
    print(f"   {public_url}")
    print(f"\n💡 Abra no navegador para visualizar!")
    print("="*60)

if __name__ == "__main__":
    main()
