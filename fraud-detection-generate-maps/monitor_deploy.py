#!/usr/bin/env python3
"""
⏰ Monitor de Deploy - Aguarda deploy e testa automaticamente
"""

import subprocess
import time
from datetime import datetime

def verificar_status_deploy():
    """Verifica se o deploy foi completado"""
    try:
        cmd = "gcloud functions describe fraud-detection-generate-maps --region=southamerica-east1 --project=river-sky-386919 --format=value(state)"
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            status = result.stdout.strip()
            return status
        else:
            return "UNKNOWN"
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return "ERROR"

def main():
    print("""
╔════════════════════════════════════════════╗
║   ⏰ MONITOR DE DEPLOY                    ║
║   Aguardando Cloud Function...            ║
╚════════════════════════════════════════════╝
    """)
    
    print(f"🕐 Hora de início: {datetime.now().strftime('%H:%M:%S')}")
    print(f"📡 Verificando status da Cloud Function...\n")
    
    tentativas = 0
    max_tentativas = 20  # 20 tentativas x 30s = 10 minutos
    
    while tentativas < max_tentativas:
        status = verificar_status_deploy()
        tentativas += 1
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Tentativa {tentativas}/{max_tentativas}: Status = {status}")
        
        if status == "ACTIVE":
            print(f"\n✅ DEPLOY COMPLETO!")
            print(f"🕐 Hora de conclusão: {datetime.now().strftime('%H:%M:%S')}")
            print(f"\n🎉 Cloud Function está pronta!")
            print(f"\n💡 AGORA VOCÊ PODE:")
            print(f"   1. Gerar mapa: python easy_pubsub.py 6ed0ffa36587c49f5b54")
            print(f"   2. Aguardar 1-2 minutos")
            print(f"   3. Verificar: python verificar_mapa.py 6ed0ffa36587c49f5b54")
            return True
            
        elif status == "FAILED":
            print(f"\n❌ DEPLOY FALHOU!")
            print(f"\n🔍 Ver logs:")
            print(f"   gcloud functions logs read fraud-detection-generate-maps --region=southamerica-east1 --limit=50 --project=river-sky-386919")
            return False
            
        elif status == "DEPLOYING":
            print(f"   ⏳ Ainda em andamento... aguardando 30s")
            time.sleep(30)
            
        else:
            print(f"   ⚠️  Status desconhecido: {status}")
            time.sleep(30)
    
    print(f"\n⏰ TIMEOUT - Excedeu tempo máximo de espera")
    print(f"\n💡 Verifique manualmente:")
    print(f"   gcloud functions describe fraud-detection-generate-maps --region=southamerica-east1 --project=river-sky-386919")
    
    return False

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
