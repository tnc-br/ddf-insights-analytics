"""
Script para atualizar documento Firestore com apenas isótopo de Oxigênio
"""
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase
cred = credentials.Certificate('../serviceAccountKey.json')
try:
    app = firebase_admin.get_app()
except ValueError:
    app = firebase_admin.initialize_app(cred)

db = firestore.client()

# ID do documento
doc_id = '6ed0ffa36587c49f5b54'

# Buscar documento
doc_ref = db.collection('untrusted_samples').document(doc_id)
doc = doc_ref.get()

if doc.exists:
    print(f"📄 Documento encontrado: {doc_id}")
    data = doc.to_dict()
    print(f"   Dados atuais: {data}")
    
    # Atualizar com apenas O18
    updates = {
        'isotopes': {
            'O18': 26.22
        }
    }
    
    # Remover C13 e N15 se existirem
    if 'isotopes' in data:
        if 'C13' in data['isotopes']:
            updates['isotopes.C13'] = firestore.DELETE_FIELD
        if 'N15' in data['isotopes']:
            updates['isotopes.N15'] = firestore.DELETE_FIELD
    
    doc_ref.update(updates)
    
    print(f"\n✅ Documento atualizado!")
    print(f"   Novo valor: O18 = 26.22")
    print(f"   C13 e N15 removidos")
    
    # Verificar atualização
    updated_doc = doc_ref.get()
    print(f"\n📊 Dados atualizados: {updated_doc.to_dict()}")
    
else:
    print(f"❌ Documento {doc_id} não encontrado!")
