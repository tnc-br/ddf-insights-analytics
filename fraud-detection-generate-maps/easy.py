#!/usr/bin/env python3
"""
⚡ EXECUTOR SUPER FÁCIL - Uma linha de comando
Versão que busca documentos REAIS do Firebase
"""

import sys
import os

def get_firebase_client():
    """Tenta conectar com Firebase real"""
    
    # Tentar encontrar arquivo de credenciais automaticamente
    credenciais_paths = [
        "serviceAccountKey.json",           # Arquivo existente na raiz
        "../serviceAccountKey.json",        # Se estiver na pasta pai
        "firebase-key.json",
        "service-account.json", 
        "credentials.json",
        "firebase-service-account.json"
    ]
    
    for path in credenciais_paths:
        if os.path.exists(path):
            print(f"✅ Encontrou credenciais: {path}")
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
            break
    
    try:
        from google.cloud import firestore
        # Tentar inicializar cliente Firestore
        db = firestore.Client()
        return db
    except Exception as e:
        print(f"⚠️  Não foi possível conectar ao Firebase: {e}")
        print("💡 Para usar dados reais, veja: CREDENCIAIS_RAPIDAS.md")
        print("🔄 Usando dados mockados...")
        return None

def get_documento_especifico(db, doc_id):
    """Busca um documento específico pelo ID"""
    try:
        # Coleções reais do Firebase
        colecoes = ['trusted_samples', 'unknown_samples', 'untrusted_samples']
        
        print(f"🔍 Buscando documento: {doc_id}")
        
        for colecao in colecoes:
            try:
                # Tentar buscar o documento nesta coleção
                doc_ref = db.collection(colecao).document(doc_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    doc_data = doc.to_dict()
                    print(f"✅ Documento encontrado na coleção: {colecao}")
                    
                    # Procurar coordenadas
                    lat = doc_data.get('lat') or doc_data.get('latitude') or doc_data.get('location', {}).get('lat')
                    lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude') or doc_data.get('location', {}).get('lon')
                    
                    if lat is not None and lon is not None:
                        print(f"✅ Coordenadas: ({lat}, {lon})")
                        return {
                            "id_original": doc_id,
                            "lat": float(lat),
                            "lon": float(lon),
                            "org": doc_data.get('org_name') or doc_data.get('organization', 'N/A'),
                            "created_on": doc_data.get('created_on', 'N/A'),
                            "colecao": colecao
                        }
                    else:
                        print(f"❌ Documento encontrado mas sem coordenadas válidas")
                        return None
                        
            except Exception as e:
                continue
        
        print(f"❌ Documento '{doc_id}' não encontrado em nenhuma coleção")
        return None
        
    except Exception as e:
        print(f"❌ Erro ao buscar documento: {e}")
        return None

def get_documentos_reais(db, limit_per_collection=5):
    """Busca documentos reais do Firestore (para listagem)"""
    try:
        # Coleções reais do Firebase
        colecoes = ['trusted_samples', 'unknown_samples', 'untrusted_samples']
        documentos_reais = {}
        total_count = 0
        
        for colecao in colecoes:
            try:
                print(f"🔍 Procurando na coleção: {colecao}")
                docs_ref = db.collection(colecao)
                docs = docs_ref.limit(limit_per_collection).stream()
                
                count = 0
                for doc in docs:
                    doc_data = doc.to_dict()
                    doc_id = doc.id
                    
                    # Procurar coordenadas em diferentes formatos
                    lat = doc_data.get('lat') or doc_data.get('latitude') or doc_data.get('location', {}).get('lat')
                    lon = doc_data.get('lon') or doc_data.get('lng') or doc_data.get('longitude') or doc_data.get('location', {}).get('lon')
                    
                    if lat is not None and lon is not None:
                        documentos_reais[doc_id.lower()] = {
                            "id_original": doc_id,
                            "lat": float(lat),
                            "lon": float(lon),
                            "org": doc_data.get('org_name') or doc_data.get('organization', 'N/A'),
                            "created_on": doc_data.get('created_on', 'N/A'),
                            "colecao": colecao
                        }
                        count += 1
                
                if count > 0:
                    print(f"   ✅ {count} documentos com coordenadas na coleção '{colecao}'")
                    total_count += count
                else:
                    print(f"   ❌ Nenhum documento com coordenadas na coleção '{colecao}'")
                    
            except Exception as e:
                print(f"   ❌ Erro ao acessar coleção '{colecao}': {e}")
                continue
        
        print(f"\n📊 TOTAL: {total_count} documentos encontrados")
        return documentos_reais if total_count > 0 else None
        
    except Exception as e:
        print(f"❌ Erro geral ao buscar documentos: {e}")
        return None

def get_documentos_mock():
    """Documentos mockados como fallback"""
    return {
        "developer": {"lat": -13.0845, "lon": -53.3795, "org": "test-org"},
        "sample_001": {"lat": -15.7942, "lon": -47.8822, "org": "conservation-intl"}, 
        "amazonia_test": {"lat": -3.1190, "lon": -60.0217, "org": "instituto-amazonia"}
    }

def main():
    if len(sys.argv) < 2:
        print("""
⚡ EXECUTOR SUPER FÁCIL - Documentos REAIS

Uso:
  python easy.py Developer         # Executar mapa para documento real
  python easy.py list              # Ver documentos da base Firebase
  python easy.py collections       # Explorar coleções disponíveis
  python easy.py all               # Executar todos os mapas reais
  python easy.py help              # Esta ajuda

Exemplos:
  python easy.py Developer         ← Busca documento real "Developer"
  python easy.py sample_001        ← Busca documento real "sample_001"  
  python easy.py collections       ← Ver estrutura do Firebase
  python easy.py all               ← Executa todos os documentos reais
        """)
        return

    comando = sys.argv[1].lower()
    
    # Tentar conectar com Firebase real
    db = get_firebase_client()
    
    # Para comando 'list', buscar todos os documentos
    if comando == "list":
        if db:
            print("🔥 Conectado ao Firebase - buscando TODOS os documentos")
            documentos = get_documentos_reais(db, limit_per_collection=5)
            if not documentos:
                print("🔄 Fallback para dados mockados")
                documentos = get_documentos_mock()
        else:
            print("🎭 Usando dados mockados")
            documentos = get_documentos_mock()
        
        print("📋 DOCUMENTOS DISPONÍVEIS:")
        for doc_id, data in documentos.items():
            id_original = data.get('id_original', doc_id)
            created = data.get('created_on', '')
            created_str = f" | {created}" if created and created != 'N/A' else ""
            colecao = data.get('colecao', '')
            colecao_str = f" [{colecao}]" if colecao else ""
            print(f"  • {id_original} → ({data['lat']}, {data['lon']}) | {data['org']}{created_str}{colecao_str}")
        return
    
    elif comando == "collections" or comando == "colecoes":
        if db:
            print("🔍 EXPLORANDO COLEÇÕES DO FIREBASE:")
            try:
                collections = db.collections()
                for collection in collections:
                    print(f"  📁 Coleção: {collection.id}")
                    try:
                        # Mostrar alguns documentos de exemplo
                        docs = collection.limit(3).stream()
                        for doc in docs:
                            doc_data = doc.to_dict()
                            print(f"    📄 {doc.id} → campos: {list(doc_data.keys())}")
                    except Exception as e:
                        print(f"    ❌ Erro ao ler documentos: {e}")
            except Exception as e:
                print(f"❌ Erro ao listar coleções: {e}")
        else:
            print("❌ Não conectado ao Firebase")
        
    elif comando == "all":
        # Para 'all', buscar todos os documentos
        if db:
            print("� Conectado ao Firebase - buscando TODOS os documentos")
            documentos = get_documentos_reais(db, limit_per_collection=5)
        else:
            documentos = get_documentos_mock()
            
        print("�🚀 EXECUTANDO TODOS OS MAPAS:")
        if documentos:
            for doc_id, data in documentos.items():
                id_original = data.get('id_original', doc_id)
                executar_mapa(id_original, data['lat'], data['lon'], db is not None)
        else:
            print("❌ Nenhum documento encontrado")
            
    elif comando == "help":
        print("💡 Ver comandos disponíveis: python easy.py")
        
    else:
        # Para documento específico, buscar APENAS esse documento
        doc_id = comando
        
        if db:
            print(f"🔥 Conectado ao Firebase - buscando documento específico: {doc_id}")
            doc_data = get_documento_especifico(db, doc_id)
            
            if doc_data:
                executar_mapa(doc_data['id_original'], doc_data['lat'], doc_data['lon'], True)
            else:
                # Tentar com dados mockados
                documentos_mock = get_documentos_mock()
                if doc_id in documentos_mock:
                    data = documentos_mock[doc_id]
                    executar_mapa(doc_id, data['lat'], data['lon'], False)
                else:
                    print(f"❌ Documento '{doc_id}' não encontrado!")
                    print("💡 Use: python easy.py list")
        else:
            # Sem Firebase, usar mock
            documentos_mock = get_documentos_mock()
            if doc_id in documentos_mock:
                data = documentos_mock[doc_id]
                executar_mapa(doc_id, data['lat'], data['lon'], False)
            else:
                print(f"❌ Documento '{doc_id}' não encontrado!")
                print("💡 Use: python easy.py list")

def executar_mapa(doc_id, lat, lon, is_real_data=False):
    """Executa geração de mapa (real ou simulado)"""
    
    data_type = "DADOS REAIS" if is_real_data else "SIMULAÇÃO"
    print(f"\n🗺️  GERANDO MAPA: {doc_id} [{data_type}]")
    print(f"📍 Coordenadas: ({lat}, {lon})")
    
    # URLs do mapa
    gcs_path = f"gs://timberid-public-to-internet/timberid-maps/{doc_id}.html"
    http_url = f"https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/{doc_id}.html"
    
    if is_real_data:
        print("🔥 Publicando mensagem no Pub/Sub para gerar mapa...")
        try:
            from google.cloud import pubsub_v1
            from datetime import datetime, timedelta
            import pytz
            
            # Configurações
            project_id = os.environ.get('GCP_PROJECT_ID', 'river-sky-386919')
            topic_id = "fraud-detection-generate-maps-daily"
            
            # Publicar mensagem no Pub/Sub
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(project_id, topic_id)
            
            # Mensagem é o ID do documento
            message_data = doc_id.encode("utf-8")
            
            print(f"� Enviando para: {topic_path}")
            print(f"📋 Mensagem: {doc_id}")
            
            # Publicar
            future = publisher.publish(topic_path, message_data)
            message_id = future.result()
            
            print(f"✅ Mensagem publicada com sucesso! ID: {message_id}")
            
            # Calcular tempo estimado
            timezone_br = pytz.timezone('America/Sao_Paulo')
            agora = datetime.now(timezone_br)
            tempo_pronto_min = agora + timedelta(minutes=1)
            tempo_pronto_max = agora + timedelta(minutes=2)
            
            print(f"\n⏰ TEMPO ESTIMADO:")
            print(f"   🕐 Hora atual: {agora.strftime('%H:%M:%S')}")
            print(f"   ✅ Mapa estará pronto entre:")
            print(f"      • {tempo_pronto_min.strftime('%H:%M:%S')} (mínimo)")
            print(f"      • {tempo_pronto_max.strftime('%H:%M:%S')} (máximo)")
            
            print(f"\n📦 Localização do mapa:")
            print(f"   GCS: {gcs_path}")
            print(f"\n🌐 URL Pública:")
            print(f"   {http_url}")
            
            print(f"\n💡 PRÓXIMOS PASSOS:")
            print(f"   1. Aguarde 1-2 minutos")
            print(f"   2. Abra a URL acima no navegador")
            print(f"   3. Se ainda não estiver pronto, aguarde mais alguns segundos")
            
            print(f"\n🚀 Processamento iniciado via Cloud Function!")
            
        except Exception as e:
            print(f"❌ Erro ao publicar no Pub/Sub: {e}")
            print(f"📋 Detalhes do erro: {type(e).__name__}")
            import traceback
            print(f"🔍 Traceback:\n{traceback.format_exc()}")
            print("\n💡 Verifique se google-cloud-pubsub está instalado:")
            print("   pip install google-cloud-pubsub")
            print("\n🔄 Voltando para simulação...")
            executar_simulacao(doc_id, lat, lon)
    else:
        executar_simulacao(doc_id, lat, lon)

def executar_simulacao(doc_id, lat, lon):
    """Simula geração de mapa"""
    http_url = f"https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/{doc_id}.html"
    
    print("🔄 Processando MapBiomas Collection 8...")
    print("   ✅ Buffer 1km criado")
    print("   ✅ Buffer 10km criado") 
    print("   ✅ Mapa HTML gerado")
    print(f"   ✅ Upload simulado: gs://timberid-public-to-internet/timberid-maps/{doc_id}.html")
    print(f"\n🔗 URL Pública (quando criado):")
    print(f"   {http_url}")
    print(f"\n🎉 Mapa '{doc_id}' simulado!")

if __name__ == "__main__":
    main()