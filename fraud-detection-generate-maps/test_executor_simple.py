"""
Teste simples do Firebase Manual Executor
Versão sem dependências externas para validar a lógica
"""

class MockFirebaseExecutor:
    """Versão simplificada para demonstrar funcionalidade"""
    
    def __init__(self):
        print("✅ MockFirebaseExecutor inicializado")
        self.sample_documents = {
            "Developer": {"lat": -13.0845, "lon": -53.3795, "org_name": "test-org"},
            "sample_001": {"lat": -15.7942, "lon": -47.8822, "org_name": "conservation-intl"},
            "amazonia_test": {"lat": -3.1190, "lon": -60.0217, "org_name": "instituto-amazonia"},
            "sample_no_coords": {"org_name": "test-org", "created_on": "2024-10-16"},
        }
    
    def get_document(self, document_id: str):
        """Simula busca de documento"""
        if document_id in self.sample_documents:
            data = self.sample_documents[document_id]
            print(f"📄 Documento encontrado: {document_id}")
            print(f"   Dados: {list(data.keys())}")
            return data
        else:
            print(f"❌ Documento não encontrado: {document_id}")
            return None
    
    def list_documents(self):
        """Lista documentos disponíveis"""
        print("📋 Documentos disponíveis:")
        for doc_id, data in self.sample_documents.items():
            has_coords = "lat" in data and "lon" in data
            coords = f"({data.get('lat')}, {data.get('lon')})" if has_coords else "sem coordenadas"
            print(f"   • {doc_id} | {coords} | {data.get('org_name', 'N/A')}")
        return len(self.sample_documents)
    
    def execute_map_generation(self, document_id: str, simulate_only: bool = False):
        """Simula geração de mapa"""
        print(f"\n🚀 Executando geração de mapa para: {document_id}")
        print("=" * 60)
        
        # Buscar documento
        doc_data = self.get_document(document_id)
        if not doc_data:
            return False
        
        # Verificar coordenadas
        if 'lat' not in doc_data or 'lon' not in doc_data:
            print(f"❌ Documento {document_id} não possui coordenadas")
            return False
        
        lat, lon = doc_data['lat'], doc_data['lon']
        print(f"📍 Coordenadas: ({lat}, {lon})")
        
        if simulate_only:
            print("🔄 SIMULAÇÃO - Não executando funções reais")
            print("   • Carregaria imagem MapBiomas")
            print("   • Geraria mapa inicial")
            print("   • Criaria buffers de 1km e 10km") 
            print("   • Geraria HTML")
            print("   • Faria upload para GCS")
            print(f"✅ Simulação concluída para {document_id}")
        else:
            print("🔄 MODO REAL - Executaria funções do main.py")
            print("   ⚠️  Requer Earth Engine e GCS configurados")
            print(f"📂 Destino: gs://timberid-public-to-internet/timberid-maps/{document_id}.html")
            print(f"✅ Execução simulada para {document_id}")
        
        return True


def test_basic_functionality():
    """Testa funcionalidades básicas"""
    print("🧪 TESTE - Firebase Manual Executor (Mock)")
    print("=" * 60)
    
    executor = MockFirebaseExecutor()
    
    print("\n1️⃣ Testando listagem de documentos:")
    count = executor.list_documents()
    
    print(f"\n2️⃣ Testando documento válido (Developer):")
    executor.execute_map_generation("Developer", simulate_only=True)
    
    print(f"\n3️⃣ Testando documento inválido (inexistente):")
    executor.execute_map_generation("documento_inexistente", simulate_only=True)
    
    print(f"\n4️⃣ Testando documento sem coordenadas:")
    executor.execute_map_generation("sample_no_coords", simulate_only=True)
    
    print("\n✅ Todos os testes concluídos!")
    print(f"📊 Total de documentos mockados: {count}")


def interactive_test():
    """Teste interativo simplificado"""
    executor = MockFirebaseExecutor()
    
    print("\n🎮 TESTE INTERATIVO SIMPLES")
    print("=" * 40)
    
    while True:
        print("\nOpções:")
        print("1. Listar documentos")
        print("2. Testar documento específico") 
        print("3. Sair")
        
        choice = input("\nEscolha (1-3): ").strip()
        
        if choice == "1":
            executor.list_documents()
        elif choice == "2":
            doc_id = input("Digite o ID: ").strip()
            simulate = input("Simular apenas? (s/N): ").lower() in ['s', 'sim']
            executor.execute_map_generation(doc_id, simulate_only=simulate)
        elif choice == "3":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        test_basic_functionality()
        
        print("\n💡 Para teste interativo, execute:")
        print("   python test_executor_simple.py interactive")