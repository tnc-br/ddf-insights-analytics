#!/usr/bin/env python3
"""
Firebase Manual Executor - fraud-detection-generate-maps

Executor manual de funções Firebase que conecta ao Firestore, 
busca documentos e executa funções que normalmente são 
disparadas por hooks/triggers do Pub/Sub.

Usage:
    python firebase_manual_executor.py --document-id sample_001
    python firebase_manual_executor.py --all-maps
    python firebase_manual_executor.py --list-documents
    python firebase_manual_executor.py --interactive
"""

import os
import sys
import base64
import argparse
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from google.auth import compute_engine
import ee

# Importar funções do main.py
from main import (
    generate_initial_map,
    generate_full_map_and_upload_to_gcs,
    MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE,
    GCS_BUCKET_NAME,
    GCS_FOLDER_NAME
)


class MockCloudEvent:
    """
    Mock de CloudEvent para simular eventos Pub/Sub
    """
    def __init__(self, message_data: str):
        """
        Inicializa mock com dados da mensagem
        
        Args:
            message_data: String da mensagem (ex: "sample_001" ou "ALL_MAPS")
        """
        # Codifica mensagem em base64 como faz o Pub/Sub real
        encoded_data = base64.b64encode(message_data.encode()).decode()
        
        self.data = {
            "message": {
                "data": encoded_data,
                "messageId": "mock-message-id",
                "publishTime": "2024-10-16T10:00:00.000Z"
            }
        }


class FirebaseManualExecutor:
    """
    Executor manual para funções de geração de mapas do Firebase
    """
    
    def __init__(self, project_id: Optional[str] = None):
        """
        Inicializa executor
        
        Args:
            project_id: ID do projeto GCP (opcional, usa variável de ambiente se não fornecido)
        """
        self.project_id = project_id or os.environ.get("GCP_PROJECT_ID", "river-sky-386919")
        self.db = firestore.Client(project=self.project_id)
        self.collection_name = "untrusted_samples"
        
        # Inicializar Earth Engine
        self._initialize_earth_engine()
        
        print(f"✅ FirebaseManualExecutor inicializado")
        print(f"   Projeto: {self.project_id}")
        print(f"   Coleção: {self.collection_name}")
    
    def _initialize_earth_engine(self):
        """Inicializa Earth Engine com credenciais"""
        try:
            credentials = compute_engine.Credentials(
                scopes=['https://www.googleapis.com/auth/earthengine']
            )
            ee.Initialize(credentials)
            print("✅ Earth Engine inicializado")
        except Exception as e:
            print(f"⚠️  Aviso: Erro ao inicializar Earth Engine: {e}")
            print("   (Testes locais podem usar mocks)")
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca documento no Firestore
        
        Args:
            document_id: ID do documento
            
        Returns:
            Dados do documento ou None se não encontrado
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                print(f"📄 Documento encontrado: {document_id}")
                print(f"   Dados: {list(data.keys()) if data else 'vazio'}")
                return data
            else:
                print(f"❌ Documento não encontrado: {document_id}")
                return None
        except Exception as e:
            print(f"💥 Erro ao buscar documento {document_id}: {e}")
            return None
    
    def list_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Lista documentos da coleção
        
        Args:
            limit: Máximo de documentos a listar
            
        Returns:
            Lista de documentos com ID e dados básicos
        """
        try:
            collection_ref = self.db.collection(self.collection_name)
            docs = collection_ref.limit(limit).stream()
            
            documents = []
            for doc in docs:
                data = doc.to_dict()
                documents.append({
                    "id": doc.id,
                    "has_coordinates": "lat" in data and "lon" in data,
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "org_name": data.get("org_name", "N/A"),
                    "created_on": data.get("created_on", "N/A")
                })
            
            print(f"📋 Encontrados {len(documents)} documentos:")
            for doc in documents:
                coords = f"({doc['lat']}, {doc['lon']})" if doc['has_coordinates'] else "sem coordenadas"
                print(f"   • {doc['id']} | {coords} | {doc['org_name']}")
            
            return documents
        
        except Exception as e:
            print(f"💥 Erro ao listar documentos: {e}")
            return []
    
    def execute_map_generation(self, document_id: str, simulate_only: bool = False) -> bool:
        """
        Executa geração de mapa para um documento específico
        
        Args:
            document_id: ID do documento no Firestore
            simulate_only: Se True, apenas simula sem executar
            
        Returns:
            True se executou com sucesso, False caso contrário
        """
        print(f"\n🚀 Executando geração de mapa para: {document_id}")
        print("=" * 60)
        
        # Verificar se documento existe
        doc_data = self.get_document(document_id)
        if not doc_data:
            return False
        
        # Verificar coordenadas
        if 'lat' not in doc_data or 'lon' not in doc_data:
            print(f"❌ Documento {document_id} não possui coordenadas (lat/lon)")
            return False
        
        lat, lon = doc_data['lat'], doc_data['lon']
        print(f"📍 Coordenadas: ({lat}, {lon})")
        
        if simulate_only:
            print("🔄 SIMULAÇÃO - Não executando funções reais")
            return True
        
        try:
            # Simular Cloud Event
            mock_event = MockCloudEvent(document_id)
            
            # Executar funções do main.py diretamente
            print("🗺️  Carregando imagem MapBiomas...")
            land_use_mapbiomas_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
            
            print("🎨 Gerando mapa inicial...")
            mapbiomas_land_use_base_map = generate_initial_map(land_use_mapbiomas_image)
            
            print("🌍 Gerando mapa completo e fazendo upload...")
            generate_full_map_and_upload_to_gcs(
                lat, lon, 
                land_use_mapbiomas_image, 
                mapbiomas_land_use_base_map, 
                document_id
            )
            
            print(f"✅ Mapa gerado com sucesso para {document_id}!")
            print(f"📂 Localização: gs://{GCS_BUCKET_NAME}/{GCS_FOLDER_NAME}/{document_id}.html")
            return True
            
        except Exception as e:
            print(f"💥 Erro ao executar geração de mapa: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute_all_maps(self, simulate_only: bool = False, max_docs: int = 50) -> Dict[str, int]:
        """
        Executa geração de mapas para todos os documentos com coordenadas
        
        Args:
            simulate_only: Se True, apenas simula sem executar
            max_docs: Máximo de documentos a processar
            
        Returns:
            Estatísticas da execução
        """
        print(f"\n🌍 Executando geração de TODOS os mapas (max: {max_docs})")
        print("=" * 60)
        
        # Listar documentos
        documents = self.list_documents(limit=max_docs)
        
        # Filtrar documentos com coordenadas
        valid_docs = [doc for doc in documents if doc['has_coordinates']]
        invalid_docs = [doc for doc in documents if not doc['has_coordinates']]
        
        print(f"\n📊 Análise:")
        print(f"   Total encontrados: {len(documents)}")
        print(f"   Com coordenadas: {len(valid_docs)}")
        print(f"   Sem coordenadas: {len(invalid_docs)}")
        
        if simulate_only:
            print("🔄 SIMULAÇÃO - Não executando funções reais")
            return {
                "total": len(documents),
                "valid": len(valid_docs),
                "invalid": len(invalid_docs),
                "success": len(valid_docs),  # Em simulação, todos "passam"
                "failed": 0
            }
        
        # Executar para cada documento válido
        success_count = 0
        failed_count = 0
        
        for doc in valid_docs:
            print(f"\n📦 Processando: {doc['id']}")
            try:
                if self.execute_map_generation(doc['id'], simulate_only=False):
                    success_count += 1
                else:
                    failed_count += 1
            except KeyboardInterrupt:
                print("\n⚠️  Execução interrompida pelo usuário")
                break
            except Exception as e:
                print(f"💥 Erro inesperado para {doc['id']}: {e}")
                failed_count += 1
        
        # Estatísticas finais
        stats = {
            "total": len(documents),
            "valid": len(valid_docs),
            "invalid": len(invalid_docs),
            "success": success_count,
            "failed": failed_count
        }
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   ✅ Sucessos: {stats['success']}")
        print(f"   ❌ Falhas: {stats['failed']}")
        print(f"   ⚠️  Sem coordenadas: {stats['invalid']}")
        
        return stats
    
    def interactive_mode(self):
        """
        Modo interativo para executar funções
        """
        print("\n🎮 MODO INTERATIVO - Firebase Manual Executor")
        print("=" * 60)
        
        while True:
            print("\nOpções disponíveis:")
            print("1. Gerar mapa para documento específico")
            print("2. Listar documentos")
            print("3. Gerar todos os mapas")
            print("4. Simular geração de mapa")
            print("5. Sair")
            
            choice = input("\nEscolha uma opção (1-5): ").strip()
            
            try:
                if choice == "1":
                    doc_id = input("Digite o ID do documento: ").strip()
                    if doc_id:
                        self.execute_map_generation(doc_id)
                    else:
                        print("❌ ID não pode ser vazio")
                
                elif choice == "2":
                    limit = input("Número máximo de documentos (padrão: 20): ").strip()
                    limit = int(limit) if limit.isdigit() else 20
                    self.list_documents(limit)
                
                elif choice == "3":
                    max_docs = input("Máximo de documentos a processar (padrão: 10): ").strip()
                    max_docs = int(max_docs) if max_docs.isdigit() else 10
                    
                    confirm = input(f"⚠️  Isso processará até {max_docs} documentos. Continuar? (s/N): ")
                    if confirm.lower() in ['s', 'sim', 'y', 'yes']:
                        self.execute_all_maps(max_docs=max_docs)
                    else:
                        print("❌ Operação cancelada")
                
                elif choice == "4":
                    doc_id = input("Digite o ID do documento para simular: ").strip()
                    if doc_id:
                        self.execute_map_generation(doc_id, simulate_only=True)
                    else:
                        print("❌ ID não pode ser vazio")
                
                elif choice == "5":
                    print("👋 Até logo!")
                    break
                
                else:
                    print("❌ Opção inválida")
                
                input("\n⏸️  Pressione ENTER para continuar...")
                
            except KeyboardInterrupt:
                print("\n👋 Até logo!")
                break
            except Exception as e:
                print(f"💥 Erro: {e}")


def main():
    """
    Função principal com argumentos de linha de comando
    """
    parser = argparse.ArgumentParser(description="Firebase Manual Executor - fraud-detection-generate-maps")
    parser.add_argument("--document-id", "-d", type=str, help="ID do documento para gerar mapa")
    parser.add_argument("--all-maps", "-a", action="store_true", help="Gerar mapas para todos os documentos")
    parser.add_argument("--list-documents", "-l", action="store_true", help="Listar documentos disponíveis")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interativo")
    parser.add_argument("--simulate", "-s", action="store_true", help="Apenas simular, não executar")
    parser.add_argument("--max-docs", "-m", type=int, default=10, help="Máximo de documentos para --all-maps")
    parser.add_argument("--project-id", "-p", type=str, help="ID do projeto GCP")
    
    args = parser.parse_args()
    
    # Inicializar executor
    executor = FirebaseManualExecutor(project_id=args.project_id)
    
    # Executar baseado nos argumentos
    if args.interactive:
        executor.interactive_mode()
    elif args.document_id:
        executor.execute_map_generation(args.document_id, simulate_only=args.simulate)
    elif args.all_maps:
        executor.execute_all_maps(simulate_only=args.simulate, max_docs=args.max_docs)
    elif args.list_documents:
        executor.list_documents()
    else:
        # Se nenhum argumento específico, mostrar ajuda
        parser.print_help()
        print("\n💡 Dica: Use --interactive para modo interativo")


if __name__ == "__main__":
    main()