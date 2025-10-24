"""
Script simples para testar geração de mapa localmente
Busca documento do Firestore e gera mapa HTML
"""

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../serviceAccountKey.json'

from google.cloud import firestore
import ee
import geemap

# Configurações
GCP_PROJECT_ID = "river-sky-386919"
# MapBiomas Collection 8 - Land Use and Land Cover
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1"

# IDs para testar
DOCUMENT_ID = "6ed0ffa36587c49f5b54"
COLLECTION_NAME = "untrusted_samples"

def main():
    print("=" * 60)
    print("🗺️  TESTE DE GERAÇÃO DE MAPA LOCAL")
    print("=" * 60)
    print()
    
    # 1. Buscar documento do Firestore
    print(f"📄 Buscando documento: {DOCUMENT_ID}")
    db = firestore.Client()
    doc_ref = db.collection(COLLECTION_NAME).document(DOCUMENT_ID)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"❌ Documento não encontrado: {DOCUMENT_ID}")
        return
    
    doc_dict = doc.to_dict()
    
    if 'lat' not in doc_dict or 'lon' not in doc_dict:
        print(f"❌ Documento não contém lat/lon")
        return
    
    lat = doc_dict['lat']
    lon = doc_dict['lon']
    print(f"✅ Documento encontrado!")
    print(f"   Latitude: {lat}")
    print(f"   Longitude: {lon}")
    print()
    
    # 2. Inicializar Earth Engine
    print("🌍 Inicializando Earth Engine...")
    try:
        ee.Initialize(project=GCP_PROJECT_ID)
        print("✅ Earth Engine inicializado!")
    except Exception as e:
        print(f"❌ Erro ao inicializar EE: {e}")
        return
    print()
    
    # 3. Carregar dados MapBiomas
    print("🗺️  Carregando MapBiomas Collection 8...")
    try:
        land_use_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
        print("✅ MapBiomas carregado!")
    except Exception as e:
        print(f"❌ Erro ao carregar MapBiomas: {e}")
        return
    print()
    
    # 4. Criar mapa base
    print("🎨 Criando mapa...")
    try:
        # Criar mapa com ee_initialize=False para não tentar reinicializar
        gee_map = geemap.Map(ee_initialize=False)
        gee_map.add_basemap("SATELLITE")
        
        # Adicionar camada MapBiomas
        gee_map.addLayer(land_use_image, {}, "Brazil Land Use")
        
        # Criar buffers de 1km e 10km
        point = ee.Geometry.Point(lon, lat)
        radius_1km = point.buffer(1000)
        radius_10km = point.buffer(10000)
        
        # Adicionar máscaras
        gee_map.addLayer(
            land_use_image.mask().geometry().difference(radius_10km), 
            {}, 
            "10 km radius mask"
        )
        gee_map.addLayer(
            radius_1km, 
            {"color": "white"}, 
            "1 km radius mask"
        )
        
        # Centralizar no ponto
        gee_map.centerObject(radius_10km, 11)
        
        print("✅ Mapa criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar mapa: {e}")
        import traceback
        traceback.print_exc()
        return
    print()
    
    # 5. Salvar HTML
    print("💾 Salvando arquivo HTML...")
    try:
        html_file = f"{DOCUMENT_ID}_local.html"
        gee_map.to_html(
            filename=html_file,
            title="Land Use details",
            width="100%",
            height="800px"
        )
        
        full_path = os.path.abspath(html_file)
        print(f"✅ Arquivo salvo: {full_path}")
    except Exception as e:
        print(f"❌ Erro ao salvar HTML: {e}")
        import traceback
        traceback.print_exc()
        return
    print()
    
    # 6. Resultado final
    print("=" * 60)
    print("✅ SUCESSO! Mapa gerado localmente")
    print("=" * 60)
    print()
    print(f"📁 Arquivo: {full_path}")
    print(f"🌐 Abra no navegador: file:///{full_path.replace(chr(92), '/')}")
    print()
    print("💡 Para visualizar:")
    print(f"   1. Abra o arquivo: {html_file}")
    print(f"   2. Ou execute: start {html_file}")
    print()

if __name__ == "__main__":
    main()
