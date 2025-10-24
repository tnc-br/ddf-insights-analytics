# ⏰ Agendamento Automático de Mapas - Cloud Scheduler

## 🎯 Resposta Direta

**SIM, existe agendamento automático!**

A geração de mapas é executada **TODOS OS DIAS às 9h** (horário de São Paulo).

## 📅 Detalhes do Agendamento

### Configuração Atual

```yaml
Nome: fraud-detection-generate-maps-daily
Status: ENABLED ✅ (Ativo)
Região: southamerica-east1
Fuso Horário: America/Sao_Paulo (GMT-3)
Schedule: 0 9 * * * (Cron expression)
Target: Pub/Sub Topic
```

### 🕐 Quando Executa

**Frequência:** Diariamente  
**Horário:** 09:00 (9h da manhã)  
**Fuso:** America/Sao_Paulo (Brasília)

**Próxima execução:** 2025-10-17 às 09:00 (12:00 UTC)

### 📝 Formato Cron

```
0 9 * * *
│ │ │ │ │
│ │ │ │ └── Dia da semana (qualquer)
│ │ │ └──── Mês (qualquer)
│ │ └────── Dia do mês (qualquer)
│ └──────── Hora: 9
└────────── Minuto: 0

= Todo dia às 09:00 (horário de São Paulo)
```

## 🔍 O Que o Agendamento Faz

### Ação Executada

**Publica mensagem especial no Pub/Sub:**

```
Tópico: fraud-detection-generate-maps-daily
Mensagem: "ALL_MAPS"
```

### Fluxo Completo

```
┌────────────────────────────────────────────────────────┐
│ TODOS OS DIAS ÀS 09:00 (Horário de São Paulo)         │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│ 1. CLOUD SCHEDULER                                     │
│    Publica mensagem "ALL_MAPS" no Pub/Sub             │
│    Topic: fraud-detection-generate-maps-daily         │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│ 2. CLOUD FUNCTION DETECTA "ALL_MAPS"                  │
│    main.py linha 72-90                                │
│    if pub_sub_message == "ALL_MAPS":                  │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│ 3. BUSCA TODOS OS DOCUMENTOS                          │
│    collection_ref.stream()                            │
│    - untrusted_samples                                │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│ 4. PARA CADA DOCUMENTO                                │
│    Publica mensagem individual no Pub/Sub             │
│    - 6ed0ffa36587c49f5b54                             │
│    - abc123def456                                     │
│    - xyz789ghi012                                     │
│    - ...                                              │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│ 5. CADA MENSAGEM DISPARA CLOUD FUNCTION NOVAMENTE     │
│    Gera 1 mapa por documento                          │
└────────────────────────────────────────────────────────┘
```

## 📊 Histórico de Execuções

### Última Execução

**Data/Hora:** 2025-10-16 às 09:00 (12:00 UTC)  
**Status:** lastAttemptTime: '2025-10-16T12:00:00.670334Z'

### Próxima Execução

**Data/Hora:** 2025-10-17 às 09:00 (12:00 UTC)  
**Agendado para:** '2025-10-17T12:00:00.734819Z'

## 🔧 Configuração Técnica Completa

```yaml
name: projects/river-sky-386919/locations/southamerica-east1/jobs/fraud-detection-generate-maps-daily

# Target: Pub/Sub
pubsubTarget:
  data: QUxMX01BUFM= # Base64 de "ALL_MAPS"
  topicName: projects/river-sky-386919/topics/fraud-detection-generate-maps-daily

# Schedule
schedule: 0 9 * * *
timeZone: America/Sao_Paulo

# Estado
state: ENABLED

# Retry Config
retryConfig:
  maxBackoffDuration: 3600s
  maxDoublings: 5
  maxRetryDuration: 0s
  minBackoffDuration: 5s

# Histórico
lastAttemptTime: "2025-10-16T12:00:00.670334Z"
scheduleTime: "2025-10-17T12:00:00.734819Z"
userUpdateTime: "2023-09-27T20:18:44Z"
```

## 📈 Outros Agendamentos no Projeto

### 1. fraud-detection-generate-maps-daily (Este!)

```
Schedule: 0 9 * * * (09:00 diariamente)
Target: Pub/Sub
Status: ENABLED ✅
```

### 2. Fraud_Detection_New_Isoscape_scheduler

```
Schedule: 0 22 * * * (22:00 diariamente)
Timezone: America/Manaus
Target: HTTP
Status: ENABLED ✅
```

### 3. TimberID_ETL_piepline_scheduler

```
Schedule: 0 0 * * * (00:00 meia-noite)
Timezone: America/Boa_Vista
Target: HTTP
Status: ENABLED ✅
```

## 🎯 Impacto do Agendamento

### O Que Acontece Diariamente às 09:00

1. ✅ Cloud Scheduler publica "ALL_MAPS"
2. ✅ Cloud Function detecta mensagem especial
3. ✅ Busca TODOS os documentos com coordenadas
4. ✅ Gera mapa para CADA documento
5. ✅ Upload de TODOS os mapas para GCS

### Quantos Mapas São Gerados?

**Depende de quantos documentos existem no Firestore!**

Para verificar:

```bash
# Ver quantos documentos seriam processados
python -c "
from google.cloud import firestore
db = firestore.Client()
docs = list(db.collection('untrusted_samples').stream())
print(f'Total de documentos: {len(docs)}')
"
```

## ⚠️ Considerações Importantes

### Custos

Cada execução diária:

- ✅ 1 mensagem Pub/Sub ("ALL_MAPS")
- ✅ N mensagens Pub/Sub (1 por documento)
- ✅ N execuções da Cloud Function
- ✅ N processamentos Earth Engine
- ✅ N uploads para GCS

**Exemplo:**
Se houver 100 documentos:

- 101 mensagens Pub/Sub
- 101 execuções Cloud Function
- 100 mapas gerados

### Performance

**Tempo estimado:**

- Cloud Function processa ~1-2 mapas por minuto
- 100 documentos = ~50-100 minutos
- Execução paralela (GCP escala automaticamente)

### Monitoramento

```bash
# Ver logs de hoje (09:00)
gcloud functions logs read fraud-detection-generate-maps \
  --region=southamerica-east1 \
  --start-time="2025-10-16T12:00:00Z" \
  --end-time="2025-10-16T13:00:00Z" \
  --project=river-sky-386919
```

## 🔧 Gerenciamento do Agendamento

### Pausar Agendamento

```bash
gcloud scheduler jobs pause fraud-detection-generate-maps-daily \
  --location=southamerica-east1 \
  --project=river-sky-386919
```

### Retomar Agendamento

```bash
gcloud scheduler jobs resume fraud-detection-generate-maps-daily \
  --location=southamerica-east1 \
  --project=river-sky-386919
```

### Executar Manualmente (Fora do Horário)

```bash
gcloud scheduler jobs run fraud-detection-generate-maps-daily \
  --location=southamerica-east1 \
  --project=river-sky-386919
```

### Alterar Horário

```bash
gcloud scheduler jobs update pubsub fraud-detection-generate-maps-daily \
  --location=southamerica-east1 \
  --schedule="0 10 * * *" \
  --project=river-sky-386919
```

## 📊 Comparação: Manual vs Agendado

| Aspecto        | Manual                       | Agendado           |
| -------------- | ---------------------------- | ------------------ |
| **Quando**     | Quando você roda script      | Todo dia às 09:00  |
| **Documentos** | 1 por vez                    | TODOS de uma vez   |
| **Mensagem**   | ID específico                | "ALL_MAPS"         |
| **Uso**        | Teste, correção              | Atualização diária |
| **Comando**    | `python easy_pubsub.py <id>` | Automático         |

## 🎯 Casos de Uso

### Use Manual Quando:

- ✅ Testar novo documento
- ✅ Re-gerar mapa específico
- ✅ Corrigir problema em um documento
- ✅ Demonstração/debug

### Use Agendado Quando:

- ✅ Atualizar todos os mapas diariamente
- ✅ Manter mapas sincronizados com dados
- ✅ Processar novos documentos automaticamente
- ✅ Manutenção regular

## 📝 Resumo

### ✅ SIM, está agendado!

**Quando:** Todos os dias às **09:00** (horário de São Paulo)  
**O que faz:** Gera mapas para **TODOS** os documentos  
**Como:** Publica "ALL_MAPS" → Cloud Function processa tudo  
**Status:** **ENABLED** ✅ (Ativo)

### Próxima Execução:

**2025-10-17 às 09:00** (Amanhã de manhã)

### Para Ver Execução de Hoje:

```bash
# Logs de hoje às 09:00
gcloud functions logs read fraud-detection-generate-maps \
  --region=southamerica-east1 \
  --start-time="2025-10-16T12:00:00Z" \
  --limit=100 \
  --project=river-sky-386919
```

### Criado em:

**2023-09-27** (já está rodando há mais de 1 ano!)

## 🔍 Verificação Rápida

```bash
# Status do agendamento
gcloud scheduler jobs describe fraud-detection-generate-maps-daily \
  --location=southamerica-east1 \
  --project=river-sky-386919 \
  --format="value(state,schedule,timeZone)"
```

**Resultado esperado:**

```
ENABLED
0 9 * * *
America/Sao_Paulo
```

✅ **Tudo configurado e funcionando!**
