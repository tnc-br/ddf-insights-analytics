#!/usr/bin/env python3
"""
⚡ EXECUTOR COM PUB/SUB - Usando gcloud CLI
Usa o gcloud para publicar mensagens (não precisa de permissões adicionais)
"""

import sys
import os
import subprocess
from datetime import datetime, timedelta

# Tentar importar pytz, se não tiver usa datetime simples
try:
    import pytz
    HAS_PYTZ = True
except:
    HAS_PYTZ = False

def get_firebase_client():
    """Conecta com Firebase"""
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
    
    try:
        from google.cloud import firestore
        db = firestore.Client()
        return db
    except Exception as e:
        print(f"⚠️  Não foi possível conectar ao Firebase: {e}")
        return None

def get_documento_especifico(db, doc_id):
    """Busca documento pelo ID"""
    try:
        colecoes = ['trusted_samples', 'unknown_samples', 'untrusted_samples']
        print(f"🔍 Buscando documento: {doc_id}")
        
        for colecao in colecoes:
            try:
                doc_ref = db.collection(colecao).document(doc_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    doc_data = doc.to_dict()
                    print(f"✅ Documento encontrado na coleção: {colecao}")
                    
                    lat = doc_data.get('lat') or doc_data.get('latitude') or doc_data.get('location', {}).get('lat')
                    lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude') or doc_data.get('location', {}).get('lon')
                    
                    if lat is not None and lon is not None:
                        print(f"✅ Coordenadas: ({lat}, {lon})")
                        return {
                            "id_original": doc_id,
                            "lat": float(lat),
                            "lon": float(lon),
                            "org": doc_data.get('org_name') or doc_data.get('organization', 'N/A'),
                            "colecao": colecao
                        }
            except:
                continue
        
        print(f"❌ Documento '{doc_id}' não encontrado")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def executar_pubsub(doc_id):
    """Publica mensagem no Pub/Sub usando gcloud CLI"""
    
    print(f"\n🗺️  GERANDO MAPA: {doc_id}")
    print("🔥 Publicando mensagem no Pub/Sub via gcloud...")
    
    project_id = "river-sky-386919"
    topic_id = "fraud-detection-generate-maps-daily"
    
    # Comando gcloud
    cmd = [
        "gcloud", "pubsub", "topics", "publish",
        topic_id,
        f"--message={doc_id}",
        f"--project={project_id}"
    ]
    
    print(f"📤 Comando: {' '.join(cmd)}")
    
    try:
        # Executar comando com shell=True no Windows
        cmd_str = ' '.join(cmd)
        result = subprocess.run(cmd_str, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"✅ Mensagem publicada com sucesso!")
            print(f"📋 Output: {result.stdout.strip()}")
            
            # Calcular tempo estimado
            if HAS_PYTZ:
                timezone_br = pytz.timezone('America/Sao_Paulo')
                agora = datetime.now(timezone_br)
            else:
                agora = datetime.now()
            
            tempo_pronto_min = agora + timedelta(minutes=1)
            tempo_pronto_max = agora + timedelta(minutes=2)
            
            print(f"\n⏰ TEMPO ESTIMADO:")
            print(f"   🕐 Hora atual: {agora.strftime('%H:%M:%S')}")
            print(f"   ✅ Mapa estará pronto entre:")
            print(f"      • {tempo_pronto_min.strftime('%H:%M:%S')} (1 minuto)")
            print(f"      • {tempo_pronto_max.strftime('%H:%M:%S')} (2 minutos)")
            
            # URLs
            gcs_path = f"gs://timberid-public-to-internet/timberid-maps/{doc_id}.html"
            http_url = f"https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/{doc_id}.html"
            
            print(f"\n📦 Localização do mapa:")
            print(f"   GCS: {gcs_path}")
            print(f"\n🌐 URL Pública:")
            print(f"   {http_url}")
            
            print(f"\n💡 PRÓXIMOS PASSOS:")
            print(f"   1. ⏰ Aguarde 1-2 minutos")
            print(f"   2. 🌐 Abra a URL acima no navegador")
            print(f"   3. 🔄 Se ainda não estiver pronto, aguarde mais alguns segundos e recarregue")
            
            print(f"\n🚀 Processamento iniciado via Cloud Function!")
            return True
            
        else:
            print(f"❌ Erro ao publicar mensagem:")
            print(f"   {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ gcloud CLI não encontrado!")
        print("\n💡 Instale o gcloud CLI:")
        print("   https://cloud.google.com/sdk/docs/install")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("""
⚡ EXECUTOR COM PUB/SUB - Usando gcloud CLI

Uso:
  python easy_pubsub.py <document_id>

Exemplo:
  python easy_pubsub.py 6ed0ffa36587c49f5b54

💡 Este script usa o gcloud CLI para publicar no Pub/Sub,
   então funciona com suas credenciais do gcloud auth login.
        """)
        return

    doc_id = sys.argv[1]
    
    # Conectar ao Firebase para validar documento
    db = get_firebase_client()
    
    if db:
        doc_data = get_documento_especifico(db, doc_id)
        if doc_data:
            # Documento encontrado, publicar no Pub/Sub
            executar_pubsub(doc_data['id_original'])
        else:
            print(f"\n❌ Documento '{doc_id}' não encontrado no Firebase")
            print("💡 Continuando mesmo assim com o ID fornecido...")
            executar_pubsub(doc_id)
    else:
        print("\n⚠️  Sem conexão Firebase, usando ID diretamente...")
        executar_pubsub(doc_id)

if __name__ == "__main__":
    main()
