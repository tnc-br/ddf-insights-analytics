"""
Script de testes locais para fraud-detection-generate-maps
Testa todas as funções principais sem precisar de Google Cloud ou Earth Engine
"""

import sys
import os
from pathlib import Path

# Adiciona mocks ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importa mocks ANTES de importar as funções reais
from mock_earth_engine import ee_mock as ee
from mock_geemap import MockGeeMap as geemap
from mock_gcs import MockStorage as storage_module
from mock_firestore import create_mock_firestore_client

# Agora podemos importar as funções principais
# Nota: Como main.py importa os módulos reais, vamos reimplementar as funções aqui


# Constantes (mesmas do main.py)
GCS_BUCKET_NAME = "timberid-public-to-internet"
GCS_FOLDER_NAME = "timberid-maps"
RADIUS_MASK_1_KM_LAYER_NAME = "1 km radius mask"
RADIUS_MASK_10_KM_LAYER_NAME = "10 km radius mask"
BRAZIL_LAND_USE_LAYER_NAME = "Brazil Land Use"
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_deforestation_regeneration_v1"


def generate_initial_map(land_use_mapbiomas_image):
    """
    Generates an initial map of a given location using the Google Earth Engine (GEE) Python API.
    
    Args:
        land_use_mapbiomas_image (ee.Image): An `ee.Image` object representing the land use map.
    
    Returns:
        A `geemap.Map` object representing the initial map.
    """
    print("\n🗺️  GERANDO MAPA INICIAL")
    print("=" * 60)
    
    # load MapBiomas Brazil deforestation + land use dataset
    land_use_layers_2021_simplified = (
        land_use_mapbiomas_image.select("product_2021").divide(100).floor()
    )
    
    # display the full land use map
    vis_params = {
        "min": 1,
        "max": 7,
        "palette": [
            "#fffbc2",  # 1, 'Anthropic'
            "#09611f",  # 2, 'Primary Vegetation'
            "#4ea376",  # 3, 'Secondary Vegetation'
            "#e31a1c",  # 4, 'Deforestation in  Primary Vegetation'
            "#94fc03",  # 5, 'Secondary Vegetation Regrowth'
            "#ffa500",  # 6, 'Deforestation in Secondary Vegetation'
            "#212121",  # 7, 'Not applied'
        ],
    }

    gee_mapbiomas_map = geemap.Map()
    gee_mapbiomas_map.addLayer(land_use_layers_2021_simplified, vis_params, BRAZIL_LAND_USE_LAYER_NAME)
    
    print("✅ Mapa inicial criado com sucesso")
    return gee_mapbiomas_map


def generate_html_file_from_map(gee_mapbiomas_map, document_id):
    """
    Generates an HTML file from a Google Earth Engine (GEE) map and saves it to disk.
    
    Args:
        gee_mapbiomas_map (geemap.Map): A `geemap.Map` object representing the map to convert to HTML.
        document_id (str): The ID of the Firestore document.
    
    Returns:
        The full filename of the generated HTML file.
    """
    print("\n📝 GERANDO ARQUIVO HTML")
    print("=" * 60)
    
    download_dir = os.getcwd()
    html_file = os.path.join(download_dir, f"{document_id}.html")
    gee_mapbiomas_map.to_html(
        filename=html_file, title="Land Use details", width="100%", height="300px"
    )
    
    print(f"✅ HTML gerado: {html_file}")
    return html_file


def upload_map_to_gcs(html_file, document_id):
    """
    Uploads an HTML file to Google Cloud Storage (GCS).
    
    Args:
        html_file (str): The full filename of the HTML file to upload.
        document_id (str): The ID of the Firestore document.
    
    Returns:
        None
    """
    print("\n☁️  UPLOAD PARA GOOGLE CLOUD STORAGE")
    print("=" * 60)
    
    storage_client = storage_module.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"{GCS_FOLDER_NAME}/{document_id}.html")
    blob.upload_from_filename(html_file)
    
    print(f"✅ Map uploaded to gs://{GCS_BUCKET_NAME}/{GCS_FOLDER_NAME}/{document_id}.html")


def generate_full_map_and_upload_to_gcs(lat, lon, land_use_mapbiomas_image, mapbiomas_land_use_base_map, document_id):
    """
    Generates a map of a given location using the Google Earth Engine (GEE) Python API and uploads the map to Google Cloud Storage (GCS).
    
    Args:
        lat (float): The latitude of the location in decimal degrees.
        lon (float): The longitude of the location in decimal degrees.
        land_use_mapbiomas_image (ee.Image): An `ee.Image` object representing the land use map.
        mapbiomas_land_use_base_map (geemap.Map): A `geemap.Map` object representing the base map.
        document_id (str): The ID of the Firestore document.
    
    Returns:
        None
    """
    print(f"\n🌍 GERANDO MAPA COMPLETO PARA: {document_id}")
    print("=" * 60)
    print(f"📍 Coordenadas: ({lat}, {lon})")
    
    # create a 1 km and 10 km radius buffer around the point
    point = ee.Geometry.Point(lon, lat)
    radius_1km_buffer = point.buffer(1000)
    radius_10km_buffer = point.buffer(10000)

    if len(mapbiomas_land_use_base_map.layers) > 2:
        mapbiomas_land_use_base_map.remove_ee_layer(RADIUS_MASK_1_KM_LAYER_NAME)
        mapbiomas_land_use_base_map.remove_ee_layer(RADIUS_MASK_10_KM_LAYER_NAME)

    # create a mask for the 10 km radius buffer with a 10km hole
    mapbiomas_land_use_base_map.addLayer(
        land_use_mapbiomas_image.mask().geometry().difference(radius_10km_buffer), 
        {}, 
        RADIUS_MASK_10_KM_LAYER_NAME
    )
    # add the 1 km radius buffer as a layer
    mapbiomas_land_use_base_map.addLayer(radius_1km_buffer, {"color": "white"}, RADIUS_MASK_1_KM_LAYER_NAME)
    # center the map on the point
    mapbiomas_land_use_base_map.centerObject(radius_10km_buffer, 11)
    
    # generate the html file and upload to GCS
    filename = generate_html_file_from_map(mapbiomas_land_use_base_map, document_id)
    upload_map_to_gcs(filename, document_id)
    
    print(f"\n✅ MAPA COMPLETO GERADO E ENVIADO COM SUCESSO!")


# ============================================================================
# TESTES
# ============================================================================

def test_generate_initial_map():
    """Testa geração do mapa inicial"""
    print("\n" + "🧪" * 30)
    print("TESTE 1: GERAÇÃO DE MAPA INICIAL")
    print("🧪" * 30)
    
    # Initialize Earth Engine mock
    ee.Initialize()
    
    # Load MapBiomas image
    land_use_mapbiomas_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
    
    # Generate initial map
    base_map = generate_initial_map(land_use_mapbiomas_image)
    
    # Validações
    assert len(base_map.layers) == 1, "Mapa deve ter 1 camada"
    assert base_map.layers[0]["name"] == BRAZIL_LAND_USE_LAYER_NAME
    
    print("\n✅ TESTE 1 PASSOU!")
    return base_map, land_use_mapbiomas_image


def test_generate_full_map():
    """Testa geração de mapa completo com buffers"""
    print("\n" + "🧪" * 30)
    print("TESTE 2: GERAÇÃO DE MAPA COMPLETO")
    print("🧪" * 30)
    
    # Dados de teste
    lat = -13.0845
    lon = -53.3795
    document_id = "test_sample_001"
    
    # Setup
    ee.Initialize()
    land_use_mapbiomas_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
    base_map = generate_initial_map(land_use_mapbiomas_image)
    
    # Gera mapa completo e upload
    generate_full_map_and_upload_to_gcs(lat, lon, land_use_mapbiomas_image, base_map, document_id)
    
    # Validações
    assert len(base_map.layers) == 3, f"Mapa deve ter 3 camadas, tem {len(base_map.layers)}"
    assert base_map.zoom == 11, "Zoom deve ser 11"
    
    # Verifica se HTML foi criado
    html_file = f"{document_id}.html"
    assert os.path.exists(html_file), "Arquivo HTML deve existir"
    
    print("\n✅ TESTE 2 PASSOU!")
    
    # Cleanup
    if os.path.exists(html_file):
        os.remove(html_file)
        print(f"🧹 Arquivo temporário removido: {html_file}")


def test_multiple_samples():
    """Testa processamento de múltiplas amostras"""
    print("\n" + "🧪" * 30)
    print("TESTE 3: MÚLTIPLAS AMOSTRAS")
    print("🧪" * 30)
    
    samples = [
        {"id": "sample_001", "lat": -13.0845, "lon": -53.3795},
        {"id": "sample_002", "lat": -15.7942, "lon": -47.8822},
        {"id": "sample_003", "lat": -10.5000, "lon": -55.3000},
    ]
    
    # Setup
    ee.Initialize()
    land_use_mapbiomas_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
    base_map = generate_initial_map(land_use_mapbiomas_image)
    
    for sample in samples:
        print(f"\n📦 Processando: {sample['id']}")
        generate_full_map_and_upload_to_gcs(
            sample['lat'], 
            sample['lon'], 
            land_use_mapbiomas_image, 
            base_map, 
            sample['id']
        )
        
        # Cleanup HTML
        html_file = f"{sample['id']}.html"
        if os.path.exists(html_file):
            os.remove(html_file)
    
    print("\n✅ TESTE 3 PASSOU!")


def test_html_generation():
    """Testa geração de HTML"""
    print("\n" + "🧪" * 30)
    print("TESTE 4: GERAÇÃO DE HTML")
    print("🧪" * 30)
    
    document_id = "test_html_generation"
    
    # Cria mapa mock
    mock_map = geemap.Map()
    mock_map.addLayer(None, {}, "Test Layer 1")
    mock_map.addLayer(None, {}, "Test Layer 2")
    mock_map.centerObject(None, 11)
    
    # Gera HTML
    html_file = generate_html_file_from_map(mock_map, document_id)
    
    # Validações
    assert os.path.exists(html_file), "HTML deve existir"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Land Use details" in content
        assert "Test Layer 1" in content
        assert "Test Layer 2" in content
    
    print("\n✅ TESTE 4 PASSOU!")
    
    # Cleanup
    os.remove(html_file)


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("🚀 INICIANDO TESTES LOCAIS - FRAUD DETECTION GENERATE MAPS")
    print("=" * 60)
    
    try:
        test_generate_initial_map()
        test_generate_full_map()
        test_multiple_samples()
        test_html_generation()
        
        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return False
    except Exception as e:
        print(f"\n💥 ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def interactive_menu():
    """Menu interativo para testes"""
    while True:
        print("\n" + "=" * 60)
        print("🗺️  MENU DE TESTES - FRAUD DETECTION GENERATE MAPS")
        print("=" * 60)
        print("1. Executar todos os testes")
        print("2. Testar geração de mapa inicial")
        print("3. Testar geração de mapa completo")
        print("4. Testar múltiplas amostras")
        print("5. Testar geração de HTML")
        print("6. Testar com coordenadas customizadas")
        print("7. Sair")
        print("=" * 60)
        
        choice = input("\nEscolha uma opção (1-7): ").strip()
        
        if choice == "1":
            run_all_tests()
        elif choice == "2":
            test_generate_initial_map()
        elif choice == "3":
            test_generate_full_map()
        elif choice == "4":
            test_multiple_samples()
        elif choice == "5":
            test_html_generation()
        elif choice == "6":
            lat = float(input("Latitude: "))
            lon = float(input("Longitude: "))
            doc_id = input("Document ID: ")
            
            ee.Initialize()
            image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
            base_map = generate_initial_map(image)
            generate_full_map_and_upload_to_gcs(lat, lon, image, base_map, doc_id)
            
            # Cleanup
            html_file = f"{doc_id}.html"
            if os.path.exists(html_file):
                print(f"\n📄 HTML gerado: {html_file}")
                keep = input("Manter arquivo HTML? (s/n): ").lower()
                if keep != 's':
                    os.remove(html_file)
                    print("🧹 Arquivo removido")
        elif choice == "7":
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")
        
        input("\n⏸️  Pressione ENTER para continuar...")


if __name__ == "__main__":
    # Executa menu interativo
    interactive_menu()
