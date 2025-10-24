"""
Script para criar dados de teste no Firestore
Execute este script para popular o Firestore com samples de teste
"""

from google.cloud import firestore
import json

def create_test_samples():
    """
    Cria samples de teste no Firestore para testar a Cloud Function
    """
    
    # Inicializar cliente Firestore
    db = firestore.Client()
    
    # Dados de teste com coordenadas reais do Brasil
    test_samples = [
        {
            "id": "Developer",
            "data": {
                "lat": -13.0845,
                "lon": -53.3795,
                "org_name": "test-organization",
                "created_on": "2024-10-14T10:00:00Z",
                "sample_type": "wood_chip",
                "region": "Mato Grosso"
            }
        },
        {
            "id": "sample_001", 
            "data": {
                "lat": -15.7942,
                "lon": -47.8822,
                "org_name": "conservation-international",
                "created_on": "2024-10-14T10:00:00Z",
                "sample_type": "wood_core",
                "region": "Distrito Federal"
            }
        },
        {
            "id": "amazonia_test_sample",
            "data": {
                "lat": -3.1190,
                "lon": -60.0217,
                "org_name": "instituto-amazonia",
                "created_on": "2024-10-14T10:00:00Z", 
                "sample_type": "wood_chip",
                "region": "Amazonas"
            }
        },
        {
            "id": "mata_atlantica_test_sample",
            "data": {
                "lat": -22.9068,
                "lon": -43.1729,
                "org_name": "fundacao-sos-mata-atlantica",
                "created_on": "2024-10-14T10:00:00Z",
                "sample_type": "wood_core", 
                "region": "Rio de Janeiro"
            }
        },
        {
            "id": "cerrado_test_sample",
            "data": {
                "lat": -14.2350,
                "lon": -51.9253,
                "org_name": "conservation-international",
                "created_on": "2024-10-14T10:00:00Z",
                "sample_type": "wood_chip",
                "region": "Mato Grosso"
            }
        },
        {
            "id": "pantanal_test_sample", 
            "data": {
                "lat": -16.5000,
                "lon": -56.6500,
                "org_name": "instituto-pantanal",
                "created_on": "2024-10-14T10:00:00Z",
                "sample_type": "wood_core",
                "region": "Mato Grosso do Sul"
            }
        },
        {
            "id": "ef8c9fc3c7983d512b71",
            "data": {
                "lat": -10.9472,
                "lon": -37.0731,
                "org_name": "ibama-sergipe", 
                "created_on": "2024-10-14T10:00:00Z",
                "sample_type": "wood_chip",
                "region": "Sergipe"
            }
        },
        {
            "id": "brasilia_sample_2024",
            "data": {
                "lat": -15.7801,
                "lon": -47.9292,
                "org_name": "ibama-df",
                "created_on": "2024-10-14T10:00:00Z",
                "sample_type": "wood_core", 
                "region": "Distrito Federal"
            }
        },
        {
            "id": "sample_sem_coordenadas",
            "data": {
                "org_name": "test-organization",
                "created_on": "2024-10-14T10:00:00Z",
                "sample_type": "wood_chip",
                "region": "Teste",
                "note": "Esta sample não tem lat/lon para testar erro"
            }
        }
    ]
    
    # Criar documentos no Firestore
    collection_ref = db.collection('untrusted_samples')
    
    print("🔄 Criando samples de teste no Firestore...")
    
    for sample in test_samples:
        doc_ref = collection_ref.document(sample['id'])
        doc_ref.set(sample['data'])
        print(f"  ✅ Criada sample: {sample['id']} ({sample['data'].get('region', 'N/A')})")
    
    print(f"\n🎉 {len(test_samples)} samples de teste criadas com sucesso!")
    print("\n📋 IDs das samples criadas:")
    for sample in test_samples:
        print(f"  - {sample['id']}")
    
    return test_samples


def list_existing_samples():
    """
    Lista samples existentes no Firestore
    """
    db = firestore.Client()
    collection_ref = db.collection('untrusted_samples')
    
    print("📋 Samples existentes no Firestore:")
    docs = collection_ref.stream()
    
    count = 0
    for doc in docs:
        data = doc.to_dict()
        lat = data.get('lat', 'N/A')
        lon = data.get('lon', 'N/A')
        region = data.get('region', 'N/A')
        print(f"  - {doc.id} | Região: {region} | Coords: ({lat}, {lon})")
        count += 1
    
    print(f"\n📊 Total: {count} samples encontradas")
    return count


def delete_test_samples():
    """
    Remove samples de teste do Firestore
    """
    db = firestore.Client()
    collection_ref = db.collection('untrusted_samples')
    
    test_ids = [
        "Developer",
        "sample_001", 
        "amazonia_test_sample",
        "mata_atlantica_test_sample",
        "cerrado_test_sample", 
        "pantanal_test_sample",
        "ef8c9fc3c7983d512b71",
        "brasilia_sample_2024",
        "sample_sem_coordenadas"
    ]
    
    print("🗑️  Removendo samples de teste...")
    
    for test_id in test_ids:
        try:
            collection_ref.document(test_id).delete()
            print(f"  ✅ Removida sample: {test_id}")
        except Exception as e:
            print(f"  ⚠️  Erro ao remover {test_id}: {e}")
    
    print("🧹 Limpeza concluída!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_test_samples()
        elif command == "list":
            list_existing_samples()
        elif command == "delete":
            delete_test_samples()
        else:
            print("❌ Comando inválido. Use: create, list, ou delete")
    else:
        print("🚀 SCRIPT DE TESTE - FIRESTORE SAMPLES")
        print("=" * 50)
        print("Comandos disponíveis:")
        print("  python create_test_data.py create  - Criar samples de teste")
        print("  python create_test_data.py list    - Listar samples existentes") 
        print("  python create_test_data.py delete  - Remover samples de teste")
        print("=" * 50)
        
        choice = input("\nEscolha uma opção (create/list/delete): ").strip().lower()
        
        if choice == "create":
            create_test_samples()
        elif choice == "list":
            list_existing_samples()
        elif choice == "delete":
            delete_test_samples()
        else:
            print("❌ Opção inválida!")