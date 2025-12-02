# Migration Guide: Pub/Sub → Firestore Trigger

## 📋 Resumo das Mudanças

A Cloud Function `fraud-detection-generate-maps` foi **refatorada** de:

- ❌ **Trigger Pub/Sub** (ativado por mensagens/cron)
- ✅ **Firestore Trigger** (ativado por alterações em documentos)

## 🔄 Arquitetura Antiga vs Nova

### ❌ ANTES (Pub/Sub + Cron)

```
┌─────────────────┐
│ Cloud Scheduler │
│  (cron diário)  │
└────────┬────────┘
         │ publica "ALL_MAPS"
         ↓
    ┌─────────┐
    │ Pub/Sub │
    │  Topic  │
    └────┬────┘
         │
         ↓
┌─────────────────────────────────┐
│  Cloud Function                 │
│  receive_pubsub_message_...     │
│                                 │
│  1. Recebe mensagem             │
│  2. Se "ALL_MAPS":              │
│     - Lista todos docs          │
│     - Publica msg por doc       │
│  3. Se document_id:             │
│     - Gera mapa                 │
└─────────────────────────────────┘
```

**Problemas:**

- 🐌 Latência (mensagens em fila)
- 🔧 Complexo (3 componentes)
- 🐛 Difícil debugar
- 💰 Custo adicional (Pub/Sub)

### ✅ DEPOIS (Firestore Trigger)

```
┌─────────────────────────────┐
│  Firestore Collection       │
│  untrusted_samples          │
│                             │
│  Document criado/atualizado │
└──────────┬──────────────────┘
           │ trigger direto
           ↓
┌─────────────────────────────┐
│  Cloud Function             │
│  generate_sample_map        │
│                             │
│  1. Recebe evento           │
│  2. Valida lat/lon          │
│  3. Gera mapa               │
│  4. Atualiza doc.map_url    │
└─────────────────────────────┘
```

**Vantagens:**

- ⚡ Instantâneo
- 🎯 Simples (1 componente)
- 🐛 Fácil debugar
- 💰 Sem custo Pub/Sub

## 📝 Mudanças no Código

### `main.py`

#### Imports atualizados:

```python
# ❌ REMOVIDO
import base64
from google.cloud import pubsub_v1

# ✅ ADICIONADO
from cloudevents.http import CloudEvent
from google.events.cloud import firestore as firestoredata
from google.protobuf.json_format import MessageToDict
import traceback
```

#### Função principal:

```python
# ❌ ANTIGA
@functions_framework.cloud_event
def receive_pubsub_message_generate_maps(cloud_event):
    pub_sub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    # Lógica complexa com loops e re-publicação

# ✅ NOVA
@functions_framework.cloud_event
def generate_sample_map(cloud_event: CloudEvent) -> None:
    """Triggers by a change to a Firestore document."""
    firestore_payload = firestoredata.DocumentEventData()
    firestore_payload._pb.ParseFromString(cloud_event.data)
    # Processa apenas 1 documento
```

#### Prevenção de loop infinito:

```python
# ✅ ADICIONADO
OUTPUT_FIELDS = set(["map_url", "map_generated_at"])

if "updateMask" in firestore_payload_dict:
    updated_fields = set(firestore_payload_dict["updateMask"]["fieldPaths"])
    input_fields_updated = updated_fields - OUTPUT_FIELDS

    if len(input_fields_updated) == 0:
        print("Only output fields updated. Skipping map generation.")
        return
```

#### Retorno de URL:

```python
# ❌ ANTIGA
def generate_full_map_and_upload_to_gcs(...):
    upload_map_to_gcs(filename, document_id)
    # Não retorna nada

# ✅ NOVA
def generate_full_map_and_upload_to_gcs(...):
    map_url = upload_map_to_gcs(filename, document_id)
    return map_url  # Retorna URL para salvar no Firestore
```

#### Update do documento:

```python
# ✅ ADICIONADO
from datetime import datetime

affected_doc.update({
    "map_url": map_url,
    "map_generated_at": datetime.utcnow()
})
```

### `requirements.txt`

```diff
functions-framework==3.3.0
google-events==0.4.0
google-api-core
+protobuf==4.22.1
cloudevents==1.9.0
google-cloud-firestore
earthengine-api==0.1.358
firebase-admin
geemap
google-auth
google-cloud-storage
-google-cloud-pubsub      # ❌ REMOVIDO
-python-dotenv            # ❌ REMOVIDO (local only)
-argparse                 # ❌ REMOVIDO (local only)
-pytz                     # ❌ REMOVIDO (local only)
```

## 🚀 Deploy

### Comando antigo (Pub/Sub):

```bash
gcloud functions deploy fraud-detection-generate-maps \
  --trigger-topic=fraud-detection-generate-maps-daily \
  # ... outros parâmetros
```

### Comando novo (Firestore):

```bash
gcloud functions deploy sample-map-generator \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=generate_sample_map \
  --trigger-event-filters="type=google.cloud.firestore.document.v1.written" \
  --trigger-event-filters="database=(default)" \
  --trigger-location=us-central1 \
  --trigger-event-filters-path-pattern="document=untrusted_samples/{documentId}" \
  --set-env-vars="GCP_PROJECT_ID=river-sky-386919" \
  --memory=2GB \
  --timeout=540s
```

**Ou usar o script:**

```bash
./deploy.sh
```

## 🗑️ Recursos para Remover

Após deploy da nova versão, podem ser deletados:

### Cloud Scheduler:

```bash
gcloud scheduler jobs delete fraud-detection-generate-maps-daily-cron
```

### Pub/Sub Topic:

```bash
gcloud pubsub topics delete fraud-detection-generate-maps-daily
```

### Função antiga:

```bash
gcloud functions delete fraud-detection-generate-maps
```

## 🧪 Teste

### Teste local:

```bash
python test_local.py
```

### Teste no Firestore:

1. Criar/atualizar documento em `untrusted_samples` com:

```javascript
{
  "lat": -15.793889,
  "lon": -47.882778
}
```

2. Verificar logs:

```bash
gcloud functions logs read sample-map-generator --limit=50
```

3. Verificar documento atualizado:

```javascript
{
  "lat": -15.793889,
  "lon": -47.882778,
  "map_url": "https://storage.googleapis.com/.../MAP.html",
  "map_generated_at": "2025-11-21T14:30:15.123456"
}
```

## ⚠️ Breaking Changes

### Para integrações externas:

#### ❌ NÃO funciona mais:

```bash
# Publicar mensagem no Pub/Sub
gcloud pubsub topics publish fraud-detection-generate-maps-daily \
  --message="DOCUMENT_ID"
```

#### ✅ Agora use:

```javascript
// Criar/atualizar documento no Firestore
db.collection("untrusted_samples").doc("DOCUMENT_ID").set({
  lat: -15.793889,
  lon: -47.882778,
});
// Trigger automático!
```

### Para processamento em batch:

#### ❌ NÃO funciona mais:

```bash
# Enviar mensagem "ALL_MAPS"
gcloud pubsub topics publish fraud-detection-generate-maps-daily \
  --message="ALL_MAPS"
```

#### ✅ Agora use:

```javascript
// Loop por todos os documentos
const docs = await db.collection("untrusted_samples").get();
for (const doc of docs.docs) {
  // Trigger automático ao atualizar timestamp
  await doc.ref.update({
    updated_at: new Date(),
  });
}
```

## 📊 Comparação de Performance

| Métrica            | Pub/Sub (antiga) | Firestore Trigger (nova) |
| ------------------ | ---------------- | ------------------------ |
| **Latência**       | ~30s (queue)     | <1s (instantâneo)        |
| **Complexidade**   | 3 componentes    | 1 componente             |
| **Custo/mês**      | ~$5-10           | ~$1-2                    |
| **Debug**          | Difícil          | Fácil (logs diretos)     |
| **Escalabilidade** | Média            | Alta                     |

## 🎯 Próximos Passos

1. ✅ Código refatorado
2. ⏳ Deploy da nova função
3. ⏳ Testar com documento real
4. ⏳ Monitorar logs por 24h
5. ⏳ Deletar recursos antigos (Scheduler + Pub/Sub)
6. ⏳ Atualizar documentação dos outros serviços

## 📚 Referências

- [Cloud Functions Firestore Triggers](https://cloud.google.com/functions/docs/calling/cloud-firestore)
- [Firestore Trigger Event Filters](https://cloud.google.com/eventarc/docs/path-patterns)
- [Migration Guide: 1st gen → 2nd gen](https://cloud.google.com/functions/docs/2nd-gen/migrating)

---

**Data da migração:** 21 de novembro de 2025  
**Autor:** TimberID Analytics Team
