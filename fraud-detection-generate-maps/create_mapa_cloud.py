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
    """Conecta com Firebase (OBRIGATÓRIO)"""
    credenciais_paths = [
        "serviceAccountKey.json",
        "../serviceAccountKey.json"
    ]
    
    credencial_encontrada = None
    for path in credenciais_paths:
        if os.path.exists(path):
            credencial_encontrada = path
            break
    
    if not credencial_encontrada:
        print("\n❌ ERRO: Nenhum arquivo de credenciais Firebase encontrado!")
        print("📁 Caminhos procurados:")
        for path in credenciais_paths:
            print(f"   • {path}")
        print("\n💡 Solução:")
        print("   1. Obtenha serviceAccountKey.json do Firebase Console")
        print("   2. Coloque em fraud-detection-generate-maps/serviceAccountKey.json")
        return None
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credencial_encontrada
    
    try:
        from google.cloud import firestore
        db = firestore.Client()
        return db
    except Exception as e:
        print(f"\n❌ ERRO: Falha ao conectar com Firebase!")
        print(f"📊 Detalhes: {e}")
        print("\n💡 Solução:")
        print("   1. Verifique se serviceAccountKey.json é válido")
        print("   2. Confirme permissões de acesso ao Firestore")
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
            print(f"\n❌ ERRO: Falha ao publicar no Pub/Sub!")
            print(f"📊 Detalhes: {result.stderr}")
            print("\n💡 Solução:")
            print("   1. Verifique se gcloud CLI está instalado: gcloud --version")
            print("   2. Autentique: gcloud auth login")
            print(f"   3. Configure projeto: gcloud config set project {project_id}")
            print("   4. Verifique permissões para publicar no tópico '{topic_id}'")
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
        check_intervals = [30, 60, 90, 120]  # Verificar a cada 30s
        
        for interval in check_intervals:
            time_to_wait = interval - (check_intervals[check_intervals.index(interval) - 1] if check_intervals.index(interval) > 0 else 0)
            
            print(f"\n⏳ Aguardando {time_to_wait}s...")
            time.sleep(time_to_wait)
            
            # Verificar se o mapa já está pronto
            try:
                doc = db.collection('untrusted_samples').document(doc_id).get()
                if not doc.exists:
                    print(f"\n❌ ERRO: Documento '{doc_id}' não encontrado!")
                    print("💡 Verifique se o ID está correto e o documento existe em 'untrusted_samples'")
                    return False
                
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
                print(f"\n❌ ERRO ao verificar status: {e}")
                print("💡 Continuando aguardando...")
        
        # Timeout - Erro porque não conseguiu verificar
        print(f"\n❌ ERRO: Timeout de 2 minutos atingido!")
        print(f"📊 O campo 'map_url' não foi encontrado no documento após 2 minutos")
        print("\n💡 Possíveis causas:")
        print("   1. Cloud Function ainda está processando (pode demorar mais)")
        print("   2. Erro no processamento da Cloud Function")
        print("   3. Documento não tem dados necessários (d18O_cel, coordenadas)")
        print("\n💡 Próximos passos:")
        print("   1. Verifique logs da Cloud Function no GCP Console")
        print("   2. Confirme que documento tem campos: d18O_cel, lat, lon")
        print("   3. Aguarde mais tempo e verifique manualmente:")
        print(f"      https://console.firebase.google.com/project/{project_id}/firestore")
        
        return False
            
    except Exception as e:
        print(f"\n❌ ERRO: Exceção inesperada!")
        print(f"📊 Detalhes: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    if len(sys.argv) < 2:
        print("""
⚡ EXECUTOR COM PUB/SUB + WAIT

Uso:
  python create_mapa_cloud.py <document_id>

Exemplo:
  python create_mapa_cloud.py 6ed0ffa36587c49f5b54

💡 Este script:
   1. Publica mensagem no Pub/Sub
   2. Aguarda 2 minutos
   3. Verifica se o mapa está pronto
   4. Mostra a URL do Firestore (se disponível)
        """)
        return

    doc_id = sys.argv[1]
    
    # Conectar ao Firebase (OBRIGATÓRIO)
    db = get_firebase_client()
    
    if not db:
        print("\n❌ ERRO: Conexão com Firebase é OBRIGATÓRIA para este script!")
        print("💡 Este script precisa do Firebase para:")
        print("   • Verificar status do processamento")
        print("   • Buscar URL do mapa gerado")
        print("\n💡 Alternativa:")
        print("   • Use create_mapa_local.py para processamento local sem Firebase")
        return
    
    print("✅ Conectado ao Firebase")
    
    # Executar
    executar_pubsub_e_aguardar(doc_id, db)

if __name__ == "__main__":
    main()
