"""
Mock do Firestore para testes locais
Simula documentos e coleções sem precisar de conexão real
"""


class MockDocumentSnapshot:
    """Mock de DocumentSnapshot"""
    
    def __init__(self, doc_id, data, exists=True):
        self.id = doc_id
        self._data = data
        self.exists = exists
    
    def to_dict(self):
        """Retorna dados do documento"""
        return self._data
    
    def get(self):
        """Retorna o próprio snapshot"""
        return self


class MockDocumentReference:
    """Mock de DocumentReference"""
    
    def __init__(self, doc_id, data=None):
        self.id = doc_id
        self._data = data or {}
    
    def get(self):
        """Simula busca de documento"""
        exists = bool(self._data)
        print(f"  📄 Buscando documento: {self.id} {'✅' if exists else '❌'}")
        return MockDocumentSnapshot(self.id, self._data, exists)


class MockCollectionReference:
    """Mock de CollectionReference"""
    
    def __init__(self, collection_name, documents=None):
        self.collection_name = collection_name
        self._documents = documents or {}
        print(f"  📁 Acessando coleção: {collection_name}")
    
    def document(self, doc_id):
        """Retorna referência para documento"""
        data = self._documents.get(doc_id, None)
        return MockDocumentReference(doc_id, data)
    
    def stream(self):
        """Retorna stream de documentos"""
        print(f"  🌊 Streaming {len(self._documents)} documentos da coleção {self.collection_name}")
        for doc_id, data in self._documents.items():
            yield MockDocumentSnapshot(doc_id, data, exists=True)


class MockFirestoreClient:
    """Mock de Firestore Client"""
    
    def __init__(self, collections=None):
        self._collections = collections or {}
        print("✅ Firestore Client inicializado (MOCK)")
    
    def collection(self, collection_name):
        """Acessa coleção"""
        documents = self._collections.get(collection_name, {})
        return MockCollectionReference(collection_name, documents)


def create_mock_firestore_client(sample_documents=None):
    """
    Factory function para criar cliente Firestore mockado
    
    Args:
        sample_documents: Dict com documentos de teste
            Ex: {
                "untrusted_samples": {
                    "sample_001": {"lat": -13.0845, "lon": -53.3795},
                    "sample_002": {"lat": -15.7942, "lon": -47.8822}
                }
            }
    """
    return MockFirestoreClient(sample_documents or {})
