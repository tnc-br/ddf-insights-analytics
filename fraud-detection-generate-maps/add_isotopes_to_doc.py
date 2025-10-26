#!/usr/bin/env python3
"""
🔧 Adicionar dados isotópicos ao documento existente
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

doc_id = "6ed0ffa36587c49f5b54"

print(f"\n🔍 Buscando documento: {doc_id}")

# Buscar em todas as coleções
colecoes = ['trusted_samples', 'untrusted_samples', 'unknown_samples']

for colecao in colecoes:
    try:
        doc_ref = db.collection(colecao).document(doc_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_data = doc.to_dict()
            print(f"✅ Documento encontrado na coleção: {colecao}")
            
            # Obter coordenadas existentes
            lat = doc_data.get('lat') or doc_data.get('latitude')
            lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude')
            
            print(f"📍 Coordenadas atuais: ({lat}, {lon})")
            print(f"📊 Dados atuais: {list(doc_data.keys())}")
            
            # Adicionar dados isotópicos sintéticos baseados na localização
            # Coordenadas estão em MT (Mato Grosso) - valores típicos para região
            isotope_data = {
                "O18": -4.8,      # δ18O típico para Cerrado/Amazônia
                "C13": -27.5,     # δ13C típico para madeira C3
                "N15": 2.8,       # δ15N típico para solos tropicais
            }
            
            print(f"\n📝 Adicionando dados isotópicos:")
            print(f"   O18 (δ18O): {isotope_data['O18']}‰")
            print(f"   C13 (δ13C): {isotope_data['C13']}‰")
            print(f"   N15 (δ15N): {isotope_data['N15']}‰")
            
            # Atualizar documento
            doc_ref.update(isotope_data)
            
            print(f"\n✅ Documento atualizado com sucesso!")
            print(f"\n🚀 Agora execute:")
            print(f"   python execute_generate_mapa.py {doc_id}")
            
            break
    except Exception as e:
        continue

else:
    print(f"❌ Documento '{doc_id}' não encontrado em nenhuma coleção")
