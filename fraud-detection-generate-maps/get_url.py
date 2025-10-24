#!/usr/bin/env python3
"""
🔗 Conversor de URL GCS para HTTP
"""

import sys

def converter_url(doc_id):
    """Converte ID do documento para URL HTTP pública"""
    gcs_path = f"gs://timberid-public-to-internet/timberid-maps/{doc_id}.html"
    http_url = f"https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/{doc_id}.html"
    
    print(f"📋 Documento: {doc_id}")
    print(f"📦 GCS Path: {gcs_path}")
    print(f"🌐 URL HTTP: {http_url}")
    print(f"\n🔗 Link para abrir no navegador:")
    print(f"   {http_url}")
    
    return http_url

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
🔗 CONVERSOR DE URL - Mapas TimberID

Uso:
  python get_url.py DOCUMENT_ID

Exemplo:
  python get_url.py 6ed0ffa36587c49f5b54
  python get_url.py 01a6b48a8f43932a8d61

Resultado:
  https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/DOCUMENT_ID.html
        """)
    else:
        doc_id = sys.argv[1]
        converter_url(doc_id)