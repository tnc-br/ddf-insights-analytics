"""
Mock do Google Cloud Storage para testes locais
Simula upload de arquivos sem precisar de autenticação real
"""
import os
from pathlib import Path


class MockBlob:
    """Mock de storage.Blob"""
    
    def __init__(self, name, bucket_name):
        self.name = name
        self.bucket_name = bucket_name
        self.uploaded_from = None
    
    def upload_from_filename(self, filename):
        """Simula upload de arquivo"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Arquivo não encontrado: {filename}")
        
        file_size = os.path.getsize(filename)
        self.uploaded_from = filename
        
        print(f"  ☁️  Upload simulado:")
        print(f"     Arquivo: {filename}")
        print(f"     Tamanho: {file_size} bytes")
        print(f"     Destino: gs://{self.bucket_name}/{self.name}")
        
        return True


class MockBucket:
    """Mock de storage.Bucket"""
    
    def __init__(self, bucket_name):
        self.name = bucket_name
        self.blobs = {}
        print(f"  🪣 Bucket acessado: {bucket_name} (MOCK)")
    
    def blob(self, blob_name):
        """Cria ou recupera blob"""
        if blob_name not in self.blobs:
            self.blobs[blob_name] = MockBlob(blob_name, self.name)
        return self.blobs[blob_name]


class MockStorageClient:
    """Mock de storage.Client"""
    
    def __init__(self):
        self.buckets = {}
        print("✅ Storage Client inicializado (MOCK)")
    
    def bucket(self, bucket_name):
        """Acessa bucket"""
        if bucket_name not in self.buckets:
            self.buckets[bucket_name] = MockBucket(bucket_name)
        return self.buckets[bucket_name]


class MockStorage:
    """Mock do módulo google.cloud.storage"""
    
    @staticmethod
    def Client():
        return MockStorageClient()
