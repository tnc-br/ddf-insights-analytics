# 🧪 Como Testar Geração de Mapas

## ❌ Problema: Teste Local

Você **não consegue** gerar mapas localmente porque:

1. Service account não tem permissão `roles/earthengine.admin`
2. Service account não tem permissão `roles/serviceusage.serviceUsageConsumer`
3. Essas permissões são necessárias para Earth Engine funcionar fora do GCP

## ✅ Solução: Usar Pub/Sub (Cloud Function)

A Cloud Function já tem as permissões corretas! Use:

```bash
python easy_pubsub.py 6ed0ffa36587c49f5b54
```

### Resultado:

```
✅ Mensagem publicada com sucesso!

⏰ TEMPO ESTIMADO:
   🕐 Hora atual: 11:36:30
   ✅ Mapa estará pronto entre:
      • 11:37:30 (1 minuto)
      • 11:38:30 (2 minutos)

🌐 URL Pública:
   https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html

💡 PRÓXIMOS PASSOS:
   1. ⏰ Aguarde 1-2 minutos
   2. 🌐 Abra a URL acima no navegador
```

## 🎯 Para Testar Com Firebase Storage

### Opção 1: Via Pub/Sub (RECOMENDADO)

```bash
# 1. Publicar mensagem
python easy_pubsub.py 6ed0ffa36587c49f5b54

# 2. Aguardar 2 minutos
# (A Cloud Function vai processar)

# 3. Abrir URL
# https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

### Opção 2: Re-deploy com Firebase Storage

Se você já migrou o `main.py` para usar Firebase Storage:

```bash
# 1. Backup
cp main.py main_gcs_backup.py

# 2. Usar versão Firebase Storage
cp main_firebase_storage.py main.py

# 3. Re-deploy
gcloud functions deploy fraud-detection-generate-maps \
  --gen2 \
  --runtime=python310 \
  --region=us-central1 \
  --source=. \
  --entry-point=receive_pubsub_message_generate_maps \
  --trigger-topic=fraud-detection-generate-maps-daily \
  --project=river-sky-386919

# 4. Testar
python easy_pubsub.py 6ed0ffa36587c49f5b54

# 5. Verificar documento no Firestore
# (Vai ter campos map_url e map_updated_at)
```

## 🔍 Como Verificar se Firebase Storage Está Funcionando

### Depois de Migrar para Firebase Storage:

```python
from google.cloud import firestore

db = firestore.Client()
doc = db.collection('untrusted_samples').document('6ed0ffa36587c49f5b54').get()
data = doc.to_dict()

# Se Firebase Storage estiver ativo:
if 'map_url' in data:
    print(f"✅ Mapa disponível: {data['map_url']}")
    print(f"📅 Atualizado em: {data['map_updated_at']}")
else:
    print("⏳ Mapa ainda não gerado")
```

## 📊 Comparação

| Método                         | Vantagens           | Desvantagens              |
| ------------------------------ | ------------------- | ------------------------- |
| **Teste Local**                | Mais rápido         | ❌ Requer permissões EE   |
| **Pub/Sub (GCS)**              | ✅ Funciona agora   | URL não fica no Firestore |
| **Pub/Sub (Firebase Storage)** | ✅ URL no Firestore | Requer re-deploy          |

## 🎯 Recomendação ATUAL

**Para testar AGORA (sem re-deploy):**

```bash
# 1. Gerar mapa via Pub/Sub
python easy_pubsub.py 6ed0ffa36587c49f5b54

# 2. Aguardar 1-2 minutos

# 3. Abrir URL
# https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

✅ **Isso funciona AGORA** e gera o mapa REAL!

## 🚀 Para o Futuro (com Firebase Storage)

1. Re-deploy da Cloud Function com `main_firebase_storage.py`
2. URLs salvas automaticamente no Firestore
3. Pode buscar URL diretamente do documento

## ⚠️ Por Que Teste Local Não Funciona?

```
❌ Erro: Caller does not have required permission to use project river-sky-386919
   Grant the caller the roles/serviceusage.serviceUsageConsumer role
```

**Explicação:**

- Earth Engine precisa de permissões especiais
- Service account local não tem essas permissões
- Cloud Function SIM tem essas permissões
- **Solução:** Usar Cloud Function via Pub/Sub

## 📝 Resumo Final

**Para gerar mapa e ver URL:**

```bash
# Execute este comando
python easy_pubsub.py 6ed0ffa36587c49f5b54

# Aguarde 1-2 minutos

# Abra esta URL no navegador
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

✅ **Funciona!**
✅ **Gera mapa REAL!**
✅ **URL disponível imediatamente!**
