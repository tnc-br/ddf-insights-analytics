#!/usr/bin/env python3
"""
🧪 Criar documento de teste com dados isotópicos

Adiciona um documento de teste ao Firebase com coordenadas e valores isotópicos
"""

import os
from google.cloud import firestore

# Configurar credenciais
credenciais_paths = [
    "serviceAccountKey.json",
    "../serviceAccountKey.json",
]

for path in credenciais_paths:
    if os.path.exists(path):
        print(f"✅ Usando credenciais: {path}")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
        break

# Conectar ao Firestore
db = firestore.Client()

# Dados de teste - Coordenadas na Amazônia
test_doc = {
    "id": "test_isotope_sample_001",
    "lat": -3.1190,  # Manaus
    "lon": -60.0217,
    
    # Valores isotópicos típicos para madeira da Amazônia
    "O18": -5.2,      # δ18O
    "C13": -28.1,     # δ13C  
    "N15": 3.4,       # δ15N
    
    # Metadados
    "org_name": "Test Organization",
    "created_at": firestore.SERVER_TIMESTAMP,
    "test_data": True,
    "description": "Amostra sintética para testar generate_new_mapa.py"
}

# Adicionar ao Firestore
doc_id = "test_isotope_sample_001"
collection = "untrusted_samples"

try:
    doc_ref = db.collection(collection).document(doc_id)
    doc_ref.set(test_doc)
    
    print("\n✅ Documento de teste criado!")
    print(f"   Coleção: {collection}")
    print(f"   ID: {doc_id}")
    print(f"   Coordenadas: ({test_doc['lat']}, {test_doc['lon']})")
    print(f"   Isótopos: O18={test_doc['O18']}, C13={test_doc['C13']}, N15={test_doc['N15']}")
    
    print(f"\n🚀 Agora execute:")
    print(f"   python execute_generate_mapa.py {doc_id}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
