#!/usr/bin/env python3
"""
⚡ EXECUTOR COM PUB/SUB + WAIT - Aguarda e mostra URL
Publica no Pub/Sub, aguarda 2 minutos e busca URL do Firestore
"""

import sys
import os
import subprocess
import time
from datetime import datetime, timedelta

try:
    import pytz
    HAS_PYTZ = True
except:
    HAS_PYTZ = False

def get_firebase_client():
    """Conecta com Firebase"""
    credenciais_paths = [
        "serviceAccountKey.json",
        "../serviceAccountKey.json"
    ]
    
    for path in credenciais_paths:
        if os.path.exists(path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
            break
    
    try:
        from google.cloud import firestore
        db = firestore.Client()
        return db
    except:
        return None

def executar_pubsub_e_aguardar(doc_id, db):
    """Publica mensagem no Pub/Sub e aguarda processamento"""
    
    print(f"\n🗺️  GERANDO MAPA: {doc_id}")
    print("🔥 Publicando mensagem no Pub/Sub via gcloud...")
    
    project_id = "river-sky-386919"
    topic_id = "fraud-detection-generate-maps-daily"
    
    # Comando gcloud
    cmd = f"gcloud pubsub topics publish {topic_id} --message={doc_id} --project={project_id}"
    
    try:
        # Executar comando
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            print(f"❌ Erro ao publicar: {result.stderr}")
            return False
        
        print(f"✅ Mensagem publicada!")
        
        # Calcular tempo estimado
        if HAS_PYTZ:
            timezone_br = pytz.timezone('America/Sao_Paulo')
            agora = datetime.now(timezone_br)
        else:
            agora = datetime.now()
        
        tempo_pronto = agora + timedelta(minutes=2)
        
        print(f"\n⏰ AGUARDANDO PROCESSAMENTO...")
        print(f"   🕐 Hora atual: {agora.strftime('%H:%M:%S')}")
        print(f"   ⏳ Estimativa de conclusão: {tempo_pronto.strftime('%H:%M:%S')}")
        
        # Aguardar em intervalos
        total_wait = 120  # 2 minutos
        check_intervals = [30, 60, 90, 120]  # Verificar a cada 30s
        
        for interval in check_intervals:
            time_to_wait = interval - (check_intervals[check_intervals.index(interval) - 1] if check_intervals.index(interval) > 0 else 0)
            
            print(f"\n⏳ Aguardando {time_to_wait}s...")
            time.sleep(time_to_wait)
            
            # Verificar se o mapa já está pronto
            if db:
                try:
                    doc = db.collection('untrusted_samples').document(doc_id).get()
                    if doc.exists:
                        data = doc.to_dict()
                        map_url = data.get('map_url')
                        
                        if map_url:
                            updated_at = data.get('map_updated_at')
                            print(f"\n🎉 MAPA PRONTO!")
                            print(f"\n📊 INFORMAÇÕES:")
                            print(f"   URL: {map_url}")
                            if updated_at:
                                print(f"   Atualizado em: {updated_at}")
                            
                            print(f"\n🌐 Abra no navegador:")
                            print(f"   {map_url}")
                            
                            return True
                    
                    print(f"   ⏳ Ainda processando... (verificado aos {interval}s)")
                    
                except Exception as e:
                    print(f"   ⚠️  Erro ao verificar status: {e}")
        
        # Timeout - mostrar URL padrão
        print(f"\n⏰ Timeout de 2 minutos atingido")
        default_url = f"https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/{doc_id}.html"
        print(f"\n💡 Tente acessar:")
        print(f"   {default_url}")
        print(f"\n⚠️  Se o mapa não carregar, aguarde mais alguns segundos e recarregue a página")
        
        return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("""
⚡ EXECUTOR COM PUB/SUB + WAIT

Uso:
  python easy_pubsub_wait.py <document_id>

Exemplo:
  python easy_pubsub_wait.py 6ed0ffa36587c49f5b54

💡 Este script:
   1. Publica mensagem no Pub/Sub
   2. Aguarda 2 minutos
   3. Verifica se o mapa está pronto
   4. Mostra a URL do Firestore (se disponível)
        """)
        return

    doc_id = sys.argv[1]
    
    # Conectar ao Firebase
    db = get_firebase_client()
    
    if db:
        print("✅ Conectado ao Firebase")
    else:
        print("⚠️  Sem conexão Firebase - não poderá verificar status automaticamente")
    
    # Executar
    executar_pubsub_e_aguardar(doc_id, db)

if __name__ == "__main__":
    main()
