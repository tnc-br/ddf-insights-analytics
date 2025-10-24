#!/usr/bin/env python3
"""
🧪 Teste Firebase Storage - Versão Local
Testa upload de arquivo HTML para Firebase Storage
"""

import os
import sys
from datetime import datetime

def testar_firebase_storage():
    """Testa upload para Firebase Storage"""
    
    print("🔥 TESTE FIREBASE STORAGE\n")
    
    # Verificar credenciais
    credenciais_paths = [
        "serviceAccountKey.json",
        "../serviceAccountKey.json"
    ]
    
    creds_found = None
    for path in credenciais_paths:
        if os.path.exists(path):
            creds_found = path
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
            print(f"✅ Credenciais encontradas: {path}")
            break
    
    if not creds_found:
        print("❌ Credenciais não encontradas!")
        return False
    
    try:
        # Importar Firebase Admin
        from firebase_admin import initialize_app, storage, credentials
        
        print("🔄 Inicializando Firebase Admin...")
        
        # Inicializar Firebase (só uma vez)
        try:
            # Tentar inicializar com credenciais explícitas
            cred = credentials.Certificate(creds_found)
            # Especificar o storage bucket (pode ser o bucket GCS existente)
            app = initialize_app(cred, {
                'storageBucket': 'timberid-public-to-internet'
            })
            print("✅ Firebase Admin inicializado")
        except ValueError as e:
            if "already exists" in str(e):
                print("✅ Firebase Admin já estava inicializado")
            else:
                raise
        
        # Obter bucket
        print("🪣 Obtendo Firebase Storage bucket...")
        bucket = storage.bucket()
        print(f"✅ Bucket: {bucket.name}")
        
        # Criar arquivo HTML de teste
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_file = f"{test_id}.html"
        
        print(f"\n📄 Criando arquivo de teste: {test_file}")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Teste Firebase Storage</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>🧪 Teste Firebase Storage</h1>
    <p>Arquivo criado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>ID: {test_id}</p>
    <p>✅ Upload para Firebase Storage funcionando!</p>
</body>
</html>
            """)
        
        print(f"✅ Arquivo criado: {test_file}")
        
        # Fazer upload
        print(f"\n📤 Fazendo upload para Firebase Storage...")
        folder_name = "timberid-maps"
        blob_path = f"{folder_name}/{test_id}.html"
        
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(test_file)
        
        print(f"✅ Upload concluído!")
        print(f"📁 Path: {blob_path}")
        
        # Com Uniform Bucket-Level Access, não precisa fazer blob.make_public()
        # O bucket inteiro já é público via IAM
        print(f"\n🌐 Gerando URL pública...")
        
        # URL pública do GCS
        public_url = f"https://storage.googleapis.com/{bucket.name}/{blob_path}"
        
        print(f"\n🎉 SUCESSO!")
        print(f"\n📊 INFORMAÇÕES:")
        print(f"   Bucket: {bucket.name}")
        print(f"   Path: {blob_path}")
        print(f"   URL: {public_url}")
        
        print(f"\n💡 Abra no navegador:")
        print(f"   {public_url}")
        
        print(f"\n✅ Nota: Bucket usa 'Uniform Bucket-Level Access'")
        print(f"   (Isso significa que o bucket inteiro é público via IAM)")
        
        # Limpar arquivo local
        os.remove(test_file)
        print(f"\n🧹 Arquivo local removido: {test_file}")
        
        print(f"\n✅ TESTE COMPLETO!")
        print(f"\n📝 Próximo passo: Migrar main.py para usar Firebase Storage")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Erro de importação: {e}")
        print(f"\n💡 Instale firebase-admin:")
        print(f"   pip install firebase-admin")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        print(f"\n🔍 Traceback:")
        print(traceback.format_exc())
        return False

def main():
    print("""
╔════════════════════════════════════════╗
║   🧪 TESTE FIREBASE STORAGE           ║
║   Versão Local - Teste de Upload     ║
╚════════════════════════════════════════╝
    """)
    
    sucesso = testar_firebase_storage()
    
    if sucesso:
        print("\n" + "="*50)
        print("✅ Firebase Storage está funcionando!")
        print("="*50)
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("❌ Teste falhou - veja os erros acima")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    main()
