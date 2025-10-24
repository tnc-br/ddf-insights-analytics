# 📡 Onde e Quando as Mensagens São Publicadas

## 🎯 Resposta Rápida

**ONDE:** Tópico Pub/Sub `fraud-detection-generate-maps-daily`  
**QUANDO:** Existem **3 cenários** diferentes!

## 📍 ONDE - Localização do Tópico Pub/Sub

### Informações do Tópico

```
Nome: fraud-detection-generate-maps-daily
Projeto: river-sky-386919
Região: Global (Pub/Sub é global por padrão)
Path completo: projects/river-sky-386919/topics/fraud-detection-generate-maps-daily
```

### Como Verificar

```bash
# Ver detalhes do tópico
gcloud pubsub topics describe fraud-detection-generate-maps-daily \
  --project=river-sky-386919

# Listar subscribers (quem escuta este tópico)
gcloud pubsub topics list-subscriptions fraud-detection-generate-maps-daily \
  --project=river-sky-386919
```

## ⏰ QUANDO - 3 Cenários de Publicação

### 🔹 CENÁRIO 1: Você Publica Manualmente (MAIS COMUM)

#### Quando Acontece:

Quando você executa qualquer um destes scripts:

```bash
python easy_pubsub.py 6ed0ffa36587c49f5b54
# OU
python easy_pubsub_wait.py 6ed0ffa36587c49f5b54
# OU
python easy.py 6ed0ffa36587c49f5b54
```

#### Onde no Código:

**`easy_pubsub.py` (linha 78-94):**

```python
def executar_pubsub(doc_id):
    """Publica mensagem no Pub/Sub usando gcloud CLI"""

    project_id = "river-sky-386919"
    topic_id = "fraud-detection-generate-maps-daily"  # ← AQUI!

    # Comando gcloud
    cmd = [
        "gcloud", "pubsub", "topics", "publish",
        topic_id,                                     # ← PUBLICA AQUI!
        f"--message={doc_id}",                        # ← Mensagem: "6ed0ffa36587c49f5b54"
        f"--project={project_id}"
    ]

    # Executa comando
    result = subprocess.run(cmd_str, capture_output=True, text=True, shell=True)
```

#### Fluxo:

```
Você digita:
  python easy_pubsub.py 6ed0ffa36587c49f5b54

↓

Script executa internamente:
  gcloud pubsub topics publish fraud-detection-generate-maps-daily \
    --message="6ed0ffa36587c49f5b54" \
    --project=river-sky-386919

↓

Mensagem publicada no tópico:
  fraud-detection-generate-maps-daily

↓

Cloud Function detecta e executa automaticamente
```

---

### 🔹 CENÁRIO 2: Cloud Function Publica (Modo "ALL_MAPS")

#### Quando Acontece:

Quando alguém publica a mensagem especial `"ALL_MAPS"` no tópico

```bash
gcloud pubsub topics publish fraud-detection-generate-maps-daily \
  --message="ALL_MAPS" \
  --project=river-sky-386919
```

#### Onde no Código:

**`main.py` (linhas 72-90):**

```python
@functions_framework.cloud_event
def receive_pubsub_message_generate_maps(cloud_event):
    # Decodifica mensagem recebida
    pub_sub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()

    # Se mensagem for "ALL_MAPS"
    elif pub_sub_message == ALL_MAPS_MESSAGE_CONTENT:  # ← "ALL_MAPS"
        print(f'Received message: {pub_sub_message}, generating all maps')

        # Busca TODOS os documentos do Firestore
        docs = collection_ref.stream()

        # Cria publisher Pub/Sub
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(GCP_PROJECT_ID, TOPIC_ID)  # ← MESMO TÓPICO!

        # Para CADA documento, publica uma mensagem
        for doc in docs:
            document_id = doc.id
            data = document_id.encode("utf-8")

            # PUBLICA mensagem individual para cada documento
            future = publisher.publish(topic_path, data)  # ← PUBLICA AQUI!
            print(f"Published messaged for id: {document_id}")
```

#### Fluxo:

```
Alguém publica:
  "ALL_MAPS"

↓

Cloud Function recebe e detecta mensagem especial

↓

Busca TODOS os documentos no Firestore:
  - 6ed0ffa36587c49f5b54
  - abc123def456
  - xyz789ghi012
  - ...

↓

Para CADA documento, publica nova mensagem no MESMO tópico:
  fraud-detection-generate-maps-daily

↓

Cada mensagem dispara a Cloud Function NOVAMENTE
  (mas agora com ID específico, não "ALL_MAPS")

↓

Cada execução gera 1 mapa
```

#### ⚠️ Importante:

Isso cria um **loop controlado**:

1. Mensagem "ALL_MAPS" → Cloud Function
2. Cloud Function → Publica N mensagens (uma por documento)
3. Cada mensagem → Dispara Cloud Function novamente
4. Cada execução → Gera 1 mapa

**NÃO é loop infinito** porque:

- ✅ Mensagens individuais (IDs) NÃO disparam novo batch
- ✅ Apenas "ALL_MAPS" dispara o batch

---

### 🔹 CENÁRIO 3: Agendamento Automático (Cron Job)

#### Quando Acontece:

Se houver um **Cloud Scheduler** configurado (precisa verificar se existe)

```bash
# Verificar se há jobs agendados
gcloud scheduler jobs list --project=river-sky-386919
```

#### Como Funcionaria:

```yaml
# Cloud Scheduler (se configurado)
Nome: daily-map-generation
Frequência: 0 0 * * *  (todo dia à meia-noite)
Ação: Publicar "ALL_MAPS" no tópico
```

**Nota:** Precisa verificar se isso está configurado no projeto.

---

## 📊 Comparação dos 3 Cenários

| Cenário         | Quem Publica                     | O Que Publica | Quando                   | Onde                                                  |
| --------------- | -------------------------------- | ------------- | ------------------------ | ----------------------------------------------------- |
| **1. Manual**   | Você (`easy_pubsub.py`)          | ID específico | Quando você roda script  | `fraud-detection-generate-maps-daily`                 |
| **2. ALL_MAPS** | Cloud Function (`main.py`)       | Múltiplos IDs | Quando recebe "ALL_MAPS" | `fraud-detection-generate-maps-daily` (mesmo tópico!) |
| **3. Agendado** | Cloud Scheduler (se configurado) | "ALL_MAPS"    | Horário agendado         | `fraud-detection-generate-maps-daily`                 |

## 🔍 Verificando Mensagens Publicadas

### Ver mensagens recentes (histórico)

```bash
# Ver logs de publicações
gcloud logging read "resource.type=pubsub_topic AND \
  resource.labels.topic_id=fraud-detection-generate-maps-daily" \
  --limit=50 \
  --project=river-sky-386919 \
  --format=json
```

### Ver subscribers ativos

```bash
gcloud pubsub subscriptions list \
  --filter="topic:fraud-detection-generate-maps-daily" \
  --project=river-sky-386919
```

## 💡 Exemplo Prático - Seu Caso de Hoje

### O que você fez:

```bash
python easy_pubsub.py 6ed0ffa36587c49f5b54
```

### O que aconteceu:

**Momento da publicação: 11:47:43**

1. **Script executou:**

   ```bash
   gcloud pubsub topics publish fraud-detection-generate-maps-daily \
     --message="6ed0ffa36587c49f5b54" \
     --project=river-sky-386919
   ```

2. **Pub/Sub recebeu:**

   ```
   Tópico: fraud-detection-generate-maps-daily
   Mensagem: "6ed0ffa36587c49f5b54"
   Message ID: 16728760615337043
   Timestamp: 2025-10-16T14:47:43Z
   ```

3. **Cloud Function foi disparada automaticamente:**

   ```
   Função: fraud-detection-generate-maps
   Região: southamerica-east1
   Trigger: Mensagem no tópico
   ```

4. **Mas falhou porque:**
   - ❌ Código deployado tinha erro (`ee.Initialize` sem `project=`)
   - ✅ Agora corrigido, esperando re-deploy

## 🎯 Resumo Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    TÓPICO PUB/SUB                           │
│         fraud-detection-generate-maps-daily                 │
│         (projects/river-sky-386919/topics/...)              │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┬───────────────────┐
        │                       │                    │
        ▼                       ▼                    ▼
   ┌─────────┐          ┌──────────────┐     ┌─────────────┐
   │ CENÁRIO │          │  CENÁRIO 2   │     │  CENÁRIO 3  │
   │    1    │          │              │     │             │
   │ Manual  │          │  ALL_MAPS    │     │  Agendado   │
   └─────────┘          │  (função     │     │  (scheduler)│
        │               │   publica    │     │             │
        │               │   mais msgs) │     │             │
        ▼               └──────────────┘     └─────────────┘
                                │
   Você executa:               │
   easy_pubsub.py              │
                               ▼
                        Para cada documento,
                        publica no MESMO tópico
                               │
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                              │
        ▼                                              ▼
   Cloud Function                            Cloud Function
   (processa ID)                             (processa ID)
```

## 🔧 Como Testar Cada Cenário

### Cenário 1 - Manual (O que você faz normalmente)

```bash
python easy_pubsub.py 6ed0ffa36587c49f5b54
```

### Cenário 2 - ALL_MAPS

```bash
gcloud pubsub topics publish fraud-detection-generate-maps-daily \
  --message="ALL_MAPS" \
  --project=river-sky-386919
```

**⚠️ CUIDADO:** Isso vai gerar mapas para TODOS os documentos!

### Cenário 3 - Verificar se há agendamento

```bash
gcloud scheduler jobs list --project=river-sky-386919
```

## 📝 Conclusão

### ONDE:

✅ **Tópico Pub/Sub:** `fraud-detection-generate-maps-daily`  
✅ **Projeto:** `river-sky-386919`  
✅ **Global** (Pub/Sub não tem região)

### QUANDO:

✅ **Cenário 1 (Manual):** Quando você roda `python easy_pubsub.py <id>`  
✅ **Cenário 2 (Batch):** Quando alguém publica "ALL_MAPS"  
✅ **Cenário 3 (Agendado):** Se houver Cloud Scheduler configurado (verificar)

### Seu caso hoje:

- ⏰ **11:47:43** - Você publicou via `easy_pubsub.py`
- 📡 **Tópico:** `fraud-detection-generate-maps-daily`
- 📝 **Mensagem:** `"6ed0ffa36587c49f5b54"`
- 🔄 **Cloud Function:** Tentou executar mas falhou (erro no código)
- ✅ **Solução:** Re-deploy em andamento com código corrigido
