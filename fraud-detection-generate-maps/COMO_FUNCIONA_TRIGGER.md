# 📡 Como o main.py é Executado - Explicação Completa

## 🎯 Resposta Direta

O `main.py` é executado via **TRIGGER Pub/Sub**!

**NÃO é chamado diretamente** - é **ativado automaticamente** quando uma mensagem chega no tópico Pub/Sub.

## 🔍 Anatomia do Código

### 1. Decorator `@functions_framework.cloud_event`

```python
@functions_framework.cloud_event
def receive_pubsub_message_generate_maps(cloud_event):
    # ...
```

Este decorator indica que a função é um **Cloud Event Handler** - ela responde a eventos de nuvem, especificamente mensagens Pub/Sub.

### 2. Configuração do Trigger (No Deploy)

Quando você faz deploy da Cloud Function:

```bash
gcloud functions deploy fraud-detection-generate-maps \
  --gen2 \
  --runtime=python311 \
  --region=southamerica-east1 \
  --source=. \
  --entry-point=receive_pubsub_message_generate_maps \
  --trigger-topic=fraud-detection-generate-maps-daily \  # ← AQUI!
  --project=river-sky-386919
```

O parâmetro `--trigger-topic=fraud-detection-generate-maps-daily` configura:

- ✅ A função **escuta** mensagens do tópico `fraud-detection-generate-maps-daily`
- ✅ Quando uma mensagem chega, a função é **automaticamente executada**
- ✅ A mensagem é passada como parâmetro `cloud_event`

## 📊 Fluxo Completo de Execução

```
┌──────────────────────────────────────────────────────────────┐
│ 1. VOCÊ PUBLICA MENSAGEM                                     │
│    python easy_pubsub.py 6ed0ffa36587c49f5b54                │
│    └─> gcloud pubsub topics publish fraud-detection-...      │
└───────────────────┬──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. PUB/SUB RECEBE MENSAGEM                                   │
│    Tópico: fraud-detection-generate-maps-daily               │
│    Mensagem: "6ed0ffa36587c49f5b54"                          │
└───────────────────┬──────────────────────────────────────────┘
                    │
                    ▼ (TRIGGER AUTOMÁTICO!)
┌──────────────────────────────────────────────────────────────┐
│ 3. CLOUD FUNCTION É ATIVADA AUTOMATICAMENTE                  │
│    GCP detecta nova mensagem no tópico                       │
│    └─> Inicia execução da Cloud Function                     │
└───────────────────┬──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. main.py EXECUTA                                           │
│    receive_pubsub_message_generate_maps(cloud_event)         │
│    │                                                          │
│    ├─> Decodifica mensagem: "6ed0ffa36587c49f5b54"           │
│    ├─> Busca documento no Firestore                          │
│    ├─> Gera mapa com Earth Engine                            │
│    └─> Faz upload para GCS                                   │
└───────────────────┬──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. RESULTADO                                                 │
│    Mapa criado em:                                           │
│    gs://timberid-public-to-internet/timberid-maps/...html    │
└──────────────────────────────────────────────────────────────┘
```

## 🔑 Componentes Principais

### A) Pub/Sub Topic

```
Nome: fraud-detection-generate-maps-daily
Localização: GCP Project river-sky-386919
Função: Recebe mensagens e dispara a Cloud Function
```

### B) Cloud Function

```
Nome: fraud-detection-generate-maps
Região: southamerica-east1
Runtime: Python 3.11
Trigger: Pub/Sub Topic (fraud-detection-generate-maps-daily)
Entry Point: receive_pubsub_message_generate_maps
```

### C) Código (main.py)

```python
@functions_framework.cloud_event  # ← Indica que é um Cloud Event Handler
def receive_pubsub_message_generate_maps(cloud_event):  # ← Recebe o evento
    # Decodifica a mensagem
    pub_sub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()

    # Resto do código...
```

## 💡 Como Funciona na Prática

### Quando você executa:

```bash
python easy_pubsub.py 6ed0ffa36587c49f5b54
```

**Internamente acontece:**

1. **Seu script** → publica mensagem no Pub/Sub

   ```python
   # easy_pubsub.py internamente faz:
   gcloud pubsub topics publish fraud-detection-generate-maps-daily \
     --message="6ed0ffa36587c49f5b54"
   ```

2. **Pub/Sub** → recebe e armazena a mensagem

   ```
   Tópico: fraud-detection-generate-maps-daily
   Mensagem ID: 16728760615337043
   Data: "6ed0ffa36587c49f5b54"
   ```

3. **GCP Event System** → detecta nova mensagem

   ```
   "Nova mensagem no tópico fraud-detection-generate-maps-daily!"
   → Verificar se há subscribers...
   → Encontrado: Cloud Function fraud-detection-generate-maps
   → DISPARAR FUNÇÃO!
   ```

4. **Cloud Function** → inicia automaticamente

   ```python
   # Cloud Run container é iniciado (se não estiver ativo)
   # main.py é carregado
   # receive_pubsub_message_generate_maps() é chamada
   # com cloud_event contendo a mensagem
   ```

5. **Função executa** → processa mensagem
   ```python
   pub_sub_message = "6ed0ffa36587c49f5b54"
   # Busca no Firestore...
   # Gera mapa...
   # Upload para GCS...
   ```

## 🆚 Comparação: Diferentes Tipos de Triggers

### 1. HTTP Trigger (NÃO é o seu caso)

```python
@functions_framework.http
def hello_http(request):
    return 'Hello!'

# Deploy:
--trigger-http

# Uso:
curl https://REGION-PROJECT.cloudfunctions.net/hello_http
```

### 2. Pub/Sub Trigger (É O SEU CASO!)

```python
@functions_framework.cloud_event
def receive_pubsub_message_generate_maps(cloud_event):
    # ...

# Deploy:
--trigger-topic=fraud-detection-generate-maps-daily

# Uso:
gcloud pubsub topics publish TOPIC --message="data"
```

### 3. Firestore Trigger (Exemplo de outro tipo)

```python
@functions_framework.cloud_event
def on_document_created(cloud_event):
    # Dispara quando documento é criado no Firestore

# Deploy:
--trigger-event-filters="type=google.cloud.firestore.document.v1.created"
```

## 📝 Como Verificar o Trigger Atual

```bash
# Ver configuração completa da Cloud Function
gcloud functions describe fraud-detection-generate-maps \
  --region=southamerica-east1 \
  --project=river-sky-386919
```

**Saída (relevante):**

```yaml
eventTrigger:
  eventType: google.cloud.pubsub.topic.v1.messagePublished
  pubsubTopic: projects/river-sky-386919/topics/fraud-detection-generate-maps-daily
  trigger: projects/river-sky-386919/locations/southamerica-east1/triggers/...
```

Isso confirma:

- ✅ Tipo: Pub/Sub Message Published
- ✅ Tópico: fraud-detection-generate-maps-daily
- ✅ Trigger automático: SIM

## 🎯 Resumo

| Aspecto                          | Resposta                                    |
| -------------------------------- | ------------------------------------------- |
| **Como é executado?**            | Via **Trigger Pub/Sub** (automático)        |
| **É chamado diretamente?**       | ❌ NÃO                                      |
| **Precisa invocar manualmente?** | ❌ NÃO - apenas publica mensagem no Pub/Sub |
| **Quem inicia a execução?**      | **GCP Event System** (automático)           |
| **O que dispara?**               | **Mensagem no tópico Pub/Sub**              |
| **Tópico**                       | `fraud-detection-generate-maps-daily`       |
| **Decorator**                    | `@functions_framework.cloud_event`          |

## 💡 Analogia Simples

Pense assim:

**Pub/Sub = Caixa de Correio**

- Você coloca uma carta (mensagem) na caixa

**Cloud Function = Campainha**

- Quando a carta chega, a campainha toca **automaticamente**
- Alguém (a função) vem atender **automaticamente**

**Você NÃO precisa:**

- ❌ Tocar a campainha manualmente
- ❌ Chamar a função
- ❌ Executar o código

**Você SÓ precisa:**

- ✅ Colocar a mensagem no Pub/Sub
- ✅ O resto acontece sozinho!

## 🔧 Configuração no Deploy

O "magic" está aqui:

```bash
--trigger-topic=fraud-detection-generate-maps-daily
```

Este parâmetro:

1. ✅ Cria um **subscription** no tópico Pub/Sub
2. ✅ Configura a função para ser **disparada automaticamente**
3. ✅ Conecta Pub/Sub → Cloud Function

**Sem este parâmetro**, a função não saberia quando executar!

## 🎯 Conclusão

**`main.py` é executado via TRIGGER Pub/Sub!**

- 🚀 **Automático**: Não precisa chamar a função
- 📡 **Event-Driven**: Responde a eventos (mensagens)
- 🔄 **Escalável**: GCP gerencia tudo automaticamente
- ⚡ **Simples**: Você só publica mensagem no Pub/Sub

**Workflow:**

```
Você → Pub/Sub → [TRIGGER AUTOMÁTICO] → Cloud Function → Resultado
```
