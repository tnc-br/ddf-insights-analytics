#!/usr/bin/env python3
"""
🔍 Verificar Mapa - Checa se o mapa existe e mostra URL
"""

import sys
import requests

def verificar_mapa(doc_id):
    """Verifica se o mapa existe no Storage"""
    
    url = f"https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/{doc_id}.html"
    
    print(f"\n🔍 Verificando mapa para: {doc_id}")
    print(f"📍 URL: {url}")
    print(f"\n⏳ Checando...")
    
    try:
        response = requests.head(url, timeout=10)
        
        if response.status_code == 200:
            print(f"\n✅ MAPA EXISTE!")
            print(f"\n🌐 Abra no navegador:")
            print(f"   {url}")
            
            # Mostrar informações do arquivo
            if 'content-length' in response.headers:
                tamanho = int(response.headers['content-length'])
                tamanho_kb = tamanho / 1024
                print(f"\n📊 Tamanho: {tamanho_kb:.2f} KB")
            
            if 'last-modified' in response.headers:
                print(f"📅 Última modificação: {response.headers['last-modified']}")
            
            return True
            
        elif response.status_code == 404:
            print(f"\n❌ MAPA NÃO EXISTE")
            print(f"\n💡 Para gerar o mapa:")
            print(f"   python easy_pubsub.py {doc_id}")
            return False
            
        else:
            print(f"\n⚠️  Status inesperado: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro ao verificar: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("""
🔍 Verificar Mapa - Checa se o mapa existe

Uso:
  python verificar_mapa.py <document_id>

Exemplo:
  python verificar_mapa.py 6ed0ffa36587c49f5b54

💡 Verifica se o mapa HTML existe no Storage
   e mostra a URL para abrir no navegador.
        """)
        return

    doc_id = sys.argv[1]
    
    print("""
╔════════════════════════════════════════╗
║   🔍 VERIFICAR MAPA                   ║
╚════════════════════════════════════════╝
    """)
    
    existe = verificar_mapa(doc_id)
    
    if existe:
        print("\n" + "="*50)
        print("✅ Mapa disponível!")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ Mapa não encontrado")
        print("="*50)

if __name__ == "__main__":
    main()
