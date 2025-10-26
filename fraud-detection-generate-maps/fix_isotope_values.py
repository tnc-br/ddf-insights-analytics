#!/usr/bin/env python3
"""
🔧 Atualizar documento com valores isotópicos otimizados
"""

import os
from google.cloud import firestore

# Configurar credenciais
for path in ["serviceAccountKey.json", "../serviceAccountKey.json"]:
    if os.path.exists(path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
        break

db = firestore.Client()
doc_id = "6ed0ffa36587c49f5b54"

# Valores ajustados para o CENTRO dos ranges dos isoscapes
# Isso deve gerar um mapa com probabilidades mais distribuídas
isotope_data = {
    "O18": -5.0,   # Centro do range -9.24 a -0.79
    "C13": -26.0,  # Centro do range -31.58 a -20.32
    "N15": 4.0,    # Centro do range -1.72 a 9.66
}

doc_ref = db.collection('untrusted_samples').document(doc_id)
doc_ref.update(isotope_data)

print("✅ Valores isotópicos atualizados:")
print(f"   O18: {isotope_data['O18']}‰")
print(f"   C13: {isotope_data['C13']}‰")
print(f"   N15: {isotope_data['N15']}‰")
print("\n🚀 Execute novamente: python run_generate_mapa_auto.py")
