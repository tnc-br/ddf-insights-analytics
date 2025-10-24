#!/usr/bin/env python3
"""
🚀 EXECUTOR SIMPLES - Firebase Manual
Versão simplificada sem configurações complexas
"""

import os
import sys

# Adiciona o diretório atual ao path para importar main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def executar_facil():
    """Interface super simples para executar funções"""
    
    print("🔥 FIREBASE EXECUTOR SIMPLES")
    print("=" * 50)
    
    # Verificar se tem credenciais básicas
    tem_credenciais = False
    
    # Verificar se existe arquivo de credenciais comum
    credenciais_paths = [
        "firebase-key.json",
        "service-account.json", 
        "credentials.json",
        ".env"
    ]
    
    for path in credenciais_paths:
        if os.path.exists(path):
            print(f"✅ Encontrou credenciais: {path}")
            tem_credenciais = True
            break
    
    # Verificar variável de ambiente
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        print(f"✅ Variável de ambiente configurada: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
        tem_credenciais = True
    
    if not tem_credenciais:
        print("⚠️  Nenhuma credencial encontrada - usando modo SIMULAÇÃO")
        return executar_simulacao()
    
    # Se tem credenciais, tentar execução real
    return executar_real()

def executar_simulacao():
    """Modo simulação - sem credenciais necessárias"""
    
    print("\n🎮 MODO SIMULAÇÃO")
    print("-" * 30)
    
    documentos_exemplo = {
        "1": {"id": "Developer", "lat": -13.0845, "lon": -53.3795},
        "2": {"id": "sample_001", "lat": -15.7942, "lon": -47.8822},
        "3": {"id": "amazonia_test", "lat": -3.1190, "lon": -60.0217}
    }
    
    print("📋 Documentos disponíveis (MOCK):")
    for num, doc in documentos_exemplo.items():
        print(f"  {num}. {doc['id']} ({doc['lat']}, {doc['lon']})")
    
    print("\nOpções:")
    print("1-3: Simular geração de mapa")
    print("4: Simular TODOS os mapas")
    print("0: Sair")
    
    escolha = input("\nEscolha: ").strip()
    
    if escolha in ["1", "2", "3"]:
        doc = documentos_exemplo[escolha]
        simular_geracao_mapa(doc["id"], doc["lat"], doc["lon"])
    elif escolha == "4":
        print("\n🚀 Simulando geração de TODOS os mapas...")
        for doc in documentos_exemplo.values():
            simular_geracao_mapa(doc["id"], doc["lat"], doc["lon"])
    elif escolha == "0":
        print("👋 Tchau!")
        return
    else:
        print("❌ Opção inválida")

def simular_geracao_mapa(doc_id, lat, lon):
    """Simula a geração de um mapa"""
    
    print(f"\n🗺️  SIMULANDO MAPA: {doc_id}")
    print(f"📍 Coordenadas: ({lat}, {lon})")
    print("🔄 Processando...")
    print("   • Carregando MapBiomas Collection 8")
    print("   • Criando buffer de 1km")
    print("   • Criando buffer de 10km") 
    print("   • Gerando mapa HTML")
    print("   • Upload para GCS: timberid-maps/{}.html".format(doc_id))
    print(f"✅ Mapa simulado para {doc_id}!")

def executar_real():
    """Modo real - com credenciais"""
    
    print("\n🔥 MODO REAL")
    print("-" * 20)
    print("⚠️  ATENÇÃO: Executará funções reais!")
    
    confirma = input("Continuar? (s/N): ").lower()
    if confirma not in ['s', 'sim', 'y', 'yes']:
        print("👋 Cancelado pelo usuário")
        return
    
    try:
        # Tentar importar e executar versão real
        print("🔄 Importando sistema real...")
        from firebase_manual_executor import FirebaseManualExecutor
        
        # Interface simples para execução real
        print("\nOpções rápidas:")
        print("1. Listar documentos reais")
        print("2. Executar documento específico")
        print("3. Modo interativo completo")
        
        escolha = input("Escolha: ").strip()
        
        if escolha == "1":
            executor = FirebaseManualExecutor()
            executor.list_documents()
        elif escolha == "2":
            doc_id = input("ID do documento: ").strip()
            simulate = input("Só simular? (S/n): ").lower() not in ['n', 'no', 'nao']
            executor = FirebaseManualExecutor()
            executor.execute_map_generation(doc_id, simulate_only=simulate)
        elif escolha == "3":
            executor = FirebaseManualExecutor()
            executor.interactive_mode()
        else:
            print("❌ Opção inválida")
            
    except ImportError as e:
        print(f"❌ Erro ao importar sistema real: {e}")
        print("🔄 Voltando para modo simulação...")
        executar_simulacao()
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("💡 Verifique suas credenciais em SETUP_CREDENTIALS.md")

if __name__ == "__main__":
    # Interface ainda mais simples
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando in ['help', '--help', '-h']:
            print("""
🚀 EXECUTOR SIMPLES - Comandos:

python run_easy.py                 # Interface interativa
python run_easy.py sim             # Só simulação
python run_easy.py real            # Tentar execução real
python run_easy.py list            # Listar documentos
python run_easy.py Developer       # Executar documento específico

Exemplos:
  python run_easy.py                # Modo mais fácil
  python run_easy.py Developer      # Executar mapa do Developer
  python run_easy.py sim            # Só testar sem credenciais
            """)
            sys.exit(0)
            
        elif comando == 'sim':
            executar_simulacao()
        elif comando == 'real':
            executar_real()
        elif comando == 'list':
            try:
                from firebase_manual_executor import FirebaseManualExecutor
                executor = FirebaseManualExecutor()
                executor.list_documents()
            except:
                print("❌ Erro - usando simulação")
                executar_simulacao()
        else:
            # Assumir que é um document_id
            doc_id = sys.argv[1]
            try:
                from firebase_manual_executor import FirebaseManualExecutor
                executor = FirebaseManualExecutor()
                simulate = input(f"Executar {doc_id} em modo simulação? (S/n): ").lower() not in ['n', 'no']
                executor.execute_map_generation(doc_id, simulate_only=simulate)
            except:
                print(f"❌ Erro - simulando {doc_id}")
                simular_geracao_mapa(doc_id, -13.0845, -53.3795)
    else:
        # Modo interativo padrão
        executar_facil()