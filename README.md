# DDF Insights Analytics - TimberID

Sistema integrado de **detecção de fraude, análise geoespacial e ETL** para validação de amostras de madeira usando **análise isotópica**, **dados do MapBiomas**, e **Google Earth Engine**.

---

## 📋 Índice

1. [Sistemas por Ordem de Prioridade](#-sistemas-por-ordem-de-prioridade)
2. [Dependências Necessárias](#-dependências-necessárias)
3. [Arquitetura Geral](#-arquitetura-geral)
4. [Descrição Detalhada dos Sistemas](#-descrição-detalhada-dos-sistemas)
5. [Configuração e Deployment](#-configuração-e-deployment)
6. [Testes Locais](#-testes-locais)

---

## 🎯 Sistemas por Ordem de Prioridade

### **1. fraud-detection-update-sample/** ⭐⭐⭐⭐⭐ (CORE)

**Trigger**: Firestore document change (untrusted_samples)  
**Tipo**: Cloud Function (Event-driven)

#### Funções Principais:

- **`evaluate()`** - Entry point principal que orquestra todo o fluxo de detecção de fraude
- **`fraud_detection_process_sample()`** - Valida amostras isotópicas (O-18, C-13, N-15) comparando com isoscapes de referência do Earth Engine
- **`fraud_detection_fetch_land_use_data()`** - Calcula porcentagens de uso da terra (vegetação primária, secundária, antrópica, água) em um raio de 10km
- **`fraud_detection_generate_map_and_upload_to_gcs()`** - Gera mapa interativo HTML com visualização de uso da terra e faz upload para Google Cloud Storage
- **`fraud_detection_fetch_mapbiomas_alerts()`** - Consulta API do MapBiomas Alerta para buscar alertas de desmatamento próximos às coordenadas

**O que faz**: Sistema principal de detecção de fraude. Processa cada amostra não confiável aplicando análise isotópica, verificação de uso da terra, geração de mapas e consulta de alertas ambientais. Atualiza o Firestore com resultados de validade e dados geoespaciais.

**Core da aplicação**: ✅ Este é o núcleo do sistema de detecção de fraude.

<!-- ToDo: Core da aplicação -->

### **2. Firestore-Earth-Engine-ETL/** ⭐⭐⭐⭐

**Trigger**: HTTP request (manual ou agendado)  
**Tipo**: Cloud Function (HTTP)

#### Funções Principais:

- **`etl()`** - Entry point que sincroniza dados do Firestore para o Earth Engine
- **`transform_snapshot_to_featuresCollection_trusted()`** - Converte amostras confiáveis (trusted_samples) em Features geoespaciais do Earth Engine
- **`transform_snapshot_to_featuresCollection_untrusted()`** - Converte amostras não confiáveis (untrusted_samples) em Features geoespaciais aplicando schema de validação
- **`save_collection_to_ee()`** - Salva FeatureCollections no Earth Engine com permissões organizacionais (ACL)
- **`get_asset_list()`** - Lista recursivamente assets do Earth Engine para limpeza antes de novos uploads

**O que faz**: Pipeline ETL que extrai amostras do Firestore, transforma em Features geoespaciais do Earth Engine organizadas por organização, e carrega no Earth Engine com controle de acesso. Permite análises geoespaciais avançadas e compartilhamento controlado de dados entre organizações.

---

### **3. fraud-detection-new-isoscape/** ⭐⭐⭐⭐

**Trigger**: HTTP request (manual ou agendado)  
**Tipo**: Cloud Function (HTTP)

#### Funções Principais:

- **`reevaluate()`** - Entry point que verifica atualizações de isoscapes e re-processa amostras
- **`is_isoscapes_updated()`** - Detecta se algum isoscape foi atualizado nas últimas 27 horas verificando `updateTime` dos assets no Earth Engine

**O que faz**: Sistema de monitoramento e invalidação de cache. Detecta quando novos isoscapes de referência isotópica são publicados no Earth Engine e automaticamente re-escreve todas as amostras não confiáveis no Firestore, disparando o sistema `fraud-detection-update-sample` para re-análise com dados atualizados.

---

### **4. fraud-detection-generate-maps/** ⭐⭐⭐

**Trigger**: Pub/Sub message  
**Tipo**: Cloud Function (Event-driven)

#### Funções Principais:

- **`receive_pubsub_message_generate_maps()`** - Entry point que processa mensagens Pub/Sub para gerar mapas
- **`generate_initial_map()`** - Cria mapa base usando dados do MapBiomas Collection 8.0 (2021)
- **`generate_full_map_and_upload_to_gcs()`** - Adiciona buffers (1km e 10km) ao mapa e faz upload para GCS
- **`generate_html_file_from_map()`** - Converte mapa geemap para arquivo HTML interativo
- **`upload_map_to_gcs()`** - Faz upload do HTML para Google Cloud Storage em pasta específica

**O que faz**: Gera mapas interativos de uso da terra para localizações específicas ou em lote (comando "ALL_MAPS"). Utiliza dados do MapBiomas para visualização de 7 categorias de uso da terra com buffers de 1km (ponto de interesse) e 10km (contexto regional). Mapas são armazenados no GCS para acesso via web.

---

### **5. update-org-ee-auto-auth/** ⭐⭐⭐

**Trigger**: Firestore document change (organizations)  
**Tipo**: Cloud Function (Event-driven)

#### Funções Principais:

- **`update_ee_acl()`** - Entry point que gerencia organizações e permissões
- **`check_org()`** - Verifica se organização existe no Google Workspace, cria grupo se necessário, e cria pasta no Earth Engine
- **`get_asset_list()`** - Lista recursivamente assets e pastas do Earth Engine para aplicar permissões
- **`assign_acl()`** - Configura ACLs (Access Control Lists) nos assets do Earth Engine, dando permissão de escrita ao grupo da organização

**O que faz**: Sistema de provisionamento automático de organizações. Quando uma nova organização é criada no Firestore, automaticamente cria grupo no Google Workspace, provisiona pasta dedicada no Earth Engine, e configura permissões para isolamento de dados entre organizações.

---

### **6. user-update-iam-check/** ⭐⭐

**Trigger**: Firestore document change (users)  
**Tipo**: Cloud Function (Event-driven)

#### Funções Principais:

- **`grant_access()`** - Entry point que gerencia ciclo de vida de permissões de usuários
- **`UserIam.grant_access_new_user()`** - Adiciona usuário aos grupos do Google Workspace baseado no role (admin, site_admin, member)
- **`UserIam.ungrant_access_new_user()`** - Remove permissões antigas quando usuário é atualizado
- **`UserIam.grant_access_deleted_user()`** - Aplica novas permissões após atualização
- **`UserIam.ungrant_access_deleted_user()`** - Remove completamente permissões quando usuário é deletado
- **`UserIam.set_service()`** - Configura autenticação com Google Admin SDK usando service account

**O que faz**: Gerenciamento automático de IAM (Identity and Access Management). Sincroniza mudanças de usuários no Firestore com permissões reais no Google Workspace e GCP. Garante que acesso seja sempre consistente com estado atual dos usuários (criação, atualização de role, deleção).

---

## 📦 Dependências Necessárias

### **Prioridade Crítica (Core)** ⭐⭐⭐⭐⭐

```python
# Google Cloud Platform
google-cloud-firestore         # Database NoSQL para armazenar amostras
firebase-admin                  # SDK Firebase para Firestore
google-cloud-storage           # Armazenamento de mapas e credenciais

# Google Earth Engine
earthengine-api==0.1.358       # API para análise geoespacial e isoscapes

# Cloud Functions Framework
functions-framework>=3.3.0     # Runtime para Cloud Functions
cloudevents>=1.9.0             # Event handling
google-events>=0.4.0           # Google Cloud event types
```

### **Prioridade Alta (Análise de Dados)** ⭐⭐⭐⭐

```python
# Processamento Científico
numpy                          # Cálculos estatísticos e arrays
scipy                          # Análise estatística avançada (chi-square, KDE)

# Geoespacial
geemap                         # Criação de mapas interativos do Earth Engine
```

### **Prioridade Média (Utilidades)** ⭐⭐⭐

```python
# Data/Time
python-dateutil               # Parsing de datas

# Google APIs
google-api-core              # Core API utilities
google-auth                  # Autenticação Google Cloud
protobuf==4.22.1            # Protocol buffers para serialização

# Google Workspace
google-api-python-client    # Google Workspace Admin SDK
google-auth-httplib2        # HTTP library para autenticação
google-auth-oauthlib        # OAuth2 para Google APIs
```

### **Prioridade Baixa (Pub/Sub)** ⭐⭐

```python
google-cloud-pubsub         # Messaging para geração de mapas em lote
```

### **Instalação Completa**

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Ou instalar apenas as críticas para testes locais
pip install numpy scipy earthengine-api firebase-admin google-cloud-firestore
```

---

## 🏗️ Arquitetura Geral

### **Fluxo Principal de Detecção de Fraude**

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FIRESTORE DATABASE                            │
│  Collections: trusted_samples, untrusted_samples, organizations      │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ Document Change Event
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│           fraud-detection-update-sample (CORE)                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 1. fraud_detection_process_sample()                          │   │
│  │    → Análise isotópica (O-18, C-13, N-15)                    │   │
│  │    → Comparação com isoscapes do Earth Engine                │   │
│  │    → Cálculo de p-values e validação estatística             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 2. fraud_detection_fetch_land_use_data()                     │   │
│  │    → MapBiomas Collection 8.0 (2021)                         │   │
│  │    → Buffer 10km para contexto regional                      │   │
│  │    → % vegetação primária, secundária, antrópica, água       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 3. fraud_detection_generate_map_and_upload_to_gcs()          │   │
│  │    → Mapa HTML interativo                                    │   │
│  │    → Upload para Google Cloud Storage                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 4. fraud_detection_fetch_mapbiomas_alerts()                  │   │
│  │    → API MapBiomas Alerta                                    │   │
│  │    → Alertas de desmatamento na região                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ Update Document
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FIRESTORE (Resultados)                            │
│  validity, validity_details, water_pct, land_use_*, alerts, map_url │
└─────────────────────────────────────────────────────────────────────┘
```

### **Sistemas de Suporte**

```
┌──────────────────────┐      ┌──────────────────────┐
│  New Isoscapes       │      │  Organization Added  │
│  Detected            │      │  to Firestore        │
└──────┬───────────────┘      └──────┬───────────────┘
       │                              │
       ▼                              ▼
┌──────────────────────┐      ┌──────────────────────┐
│ fraud-detection-     │      │ update-org-ee-       │
│ new-isoscape         │      │ auto-auth            │
│ → Re-trigger all     │      │ → Create GW group    │
│   samples            │      │ → Create EE folder   │
└──────────────────────┘      │ → Set ACL            │
                              └──────────────────────┘

┌──────────────────────┐      ┌──────────────────────┐
│  User Added/Updated  │      │  Pub/Sub Message     │
│  in Firestore        │      │  "ALL_MAPS"          │
└──────┬───────────────┘      └──────┬───────────────┘
       │                              │
       ▼                              ▼
┌──────────────────────┐      ┌──────────────────────┐
│ user-update-iam-     │      │ fraud-detection-     │
│ check                │      │ generate-maps        │
│ → Add to GW groups   │      │ → Batch map          │
│ → Manage IAM         │      │   generation         │
└──────────────────────┘      └──────────────────────┘
```

### **ETL Pipeline**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HTTP Trigger (Manual/Scheduled)                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│             Firestore-Earth-Engine-ETL                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Extract: Firestore Collections                               │   │
│  │   → trusted_samples (lat, lon, points, created_on)           │   │
│  │   → untrusted_samples (lat, lon, isotopes, validity)         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Transform: Validate & Convert                                │   │
│  │   → Coordinate validation (lat/lon)                          │   │
│  │   → Group by org_name                                        │   │
│  │   → Convert to ee.Feature with geometry                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Load: Upload to Earth Engine                                 │   │
│  │   → projects/{project}/assets/ee_org/{org}/trusted_samples   │   │
│  │   → projects/{project}/assets/ee_org/{org}/untrusted_samples │   │
│  │   → Set ACL for organization access                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              GOOGLE EARTH ENGINE ASSETS                              │
│  Organizational FeatureCollections for geospatial analysis          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Descrição Detalhada dos Sistemas

### **1. fraud-detection-update-sample/** (CORE)

**Responsabilidade**: Detecção de fraude principal  
**Tecnologias**: Cloud Functions, Earth Engine, Firestore, MapBiomas API, GCS  
**Trigger**: Firestore document change event  
**Input**: Documento untrusted_sample com coordenadas e medições isotópicas  
**Output**: Documento atualizado com validity, land_use percentages, alerts, map_url

**Arquivos principais**:

- `main.py` - Orquestrador principal com função `evaluate()`
- `fraud_detection_process_sample.py` - Validação isotópica core
- `fraud_detection_fetch_land_use_data.py` - Análise de uso da terra
- `fraud_detection_generate_map_and_upload_to_gcs.py` - Geração de mapas
- `fraud_detection_fetch_mapbiomas_alerts.py` - Consulta de alertas

**Quando usar**: Automaticamente disparado quando amostra é adicionada/atualizada no Firestore

---

### **2. Firestore-Earth-Engine-ETL/**

**Responsabilidade**: Sincronização de dados Firestore → Earth Engine  
**Tecnologias**: Cloud Functions HTTP, Earth Engine API, Firestore  
**Trigger**: HTTP request (manual ou Cloud Scheduler)  
**Input**: Todas as amostras trusted/untrusted do Firestore  
**Output**: FeatureCollections organizadas por organização no Earth Engine

**Arquivos principais**:

- `main.py` - Pipeline ETL completo com funções extract, transform, load

**Quando usar**: Executar diariamente via Cloud Scheduler ou após grandes atualizações de dados

---

### **3. fraud-detection-new-isoscape/**

**Responsabilidade**: Monitoramento de atualizações de isoscapes  
**Tecnologias**: Cloud Functions HTTP, Earth Engine API  
**Trigger**: HTTP request (manual ou Cloud Scheduler)  
**Input**: Assets na pasta `projects/{project}/assets/isoscapes`  
**Output**: Re-trigger de todas amostras se isoscapes atualizados

**Arquivos principais**:

- `main.py` - Verificação de updateTime e re-escrita de documentos

**Quando usar**: Executar após publicação de novos isoscapes de referência, ou diariamente via scheduler

---

### **4. fraud-detection-generate-maps/**

**Responsabilidade**: Geração de mapas interativos de uso da terra  
**Tecnologias**: Cloud Functions Pub/Sub, Earth Engine, geemap, GCS  
**Trigger**: Pub/Sub message  
**Input**: Coordenadas ou comando "ALL_MAPS"  
**Output**: Mapa HTML interativo no GCS

**Arquivos principais**:

- `main.py` - Processamento de mensagens e geração de mapas

**Quando usar**: Via Pub/Sub para mapas individuais ou em lote

---

### **5. update-org-ee-auto-auth/**

**Responsabilidade**: Provisionamento automático de organizações  
**Tecnologias**: Cloud Functions, Earth Engine API, Google Workspace Admin SDK  
**Trigger**: Firestore document change (organizations)  
**Input**: Documento de organização com org_email e org_name  
**Output**: Grupo no Google Workspace, pasta no EE, ACLs configuradas

**Arquivos principais**:

- `main.py` - Gerenciamento de organizações e permissões

**Quando usar**: Automaticamente disparado quando nova organização é criada

---

### **6. user-update-iam-check/**

**Responsabilidade**: Gerenciamento de IAM e permissões de usuários  
**Tecnologias**: Cloud Functions, Google Workspace Admin SDK  
**Trigger**: Firestore document change (users)  
**Input**: Documento de usuário com email, role, org  
**Output**: Usuário adicionado/removido de grupos do Google Workspace

**Arquivos principais**:

- `main.py` - Orquestração de eventos de usuário
- `iam.py` - Classe UserIam com lógica de permissões

**Quando usar**: Automaticamente disparado em mudanças de usuários

---

## ⚙️ Configuração e Deployment

### **Variáveis de Ambiente Globais**

```bash
# Google Cloud Platform
GCP_PROJECT_ID=your-project-id

# Google Cloud Storage
GCS_BUCKET_NAME=timberid-public-to-internet
GCS_FOLDER_NAME=timberid-maps

# Earth Engine Paths
ORG_EE_PATH=projects/${GCP_PROJECT_ID}/assets/ee_org
ISOSCAPES_EE_PATH=projects/${GCP_PROJECT_ID}/assets/isoscapes
```

### **Deployment de Cloud Functions**

```bash
# Deploy fraud-detection-update-sample (Firestore trigger)
gcloud functions deploy fraud-detection-update-sample \
  --runtime python39 \
  --trigger-event providers/cloud.firestore/eventTypes/document.write \
  --trigger-resource "projects/${GCP_PROJECT_ID}/databases/(default)/documents/untrusted_samples/{documentId}" \
  --env-vars-file .env.yaml

# Deploy Firestore-Earth-Engine-ETL (HTTP)
gcloud functions deploy firestore-ee-etl \
  --runtime python39 \
  --trigger-http \
  --entry-point etl \
  --env-vars-file .env.yaml

# Deploy fraud-detection-new-isoscape (HTTP)
gcloud functions deploy fraud-detection-new-isoscape \
  --runtime python39 \
  --trigger-http \
  --entry-point reevaluate \
  --env-vars-file .env.yaml

# Deploy fraud-detection-generate-maps (Pub/Sub)
gcloud functions deploy fraud-detection-generate-maps \
  --runtime python39 \
  --trigger-topic fraud-detection-generate-maps-daily \
  --entry-point receive_pubsub_message_generate_maps \
  --env-vars-file .env.yaml

# Deploy update-org-ee-auto-auth (Firestore trigger)
gcloud functions deploy update-org-ee-auto-auth \
  --runtime python39 \
  --trigger-event providers/cloud.firestore/eventTypes/document.write \
  --trigger-resource "projects/${GCP_PROJECT_ID}/databases/(default)/documents/organizations/{documentId}" \
  --env-vars-file .env.yaml

# Deploy user-update-iam-check (Firestore trigger)
gcloud functions deploy user-update-iam-check \
  --runtime python39 \
  --trigger-event providers/cloud.firestore/eventTypes/document.write \
  --trigger-resource "projects/${GCP_PROJECT_ID}/databases/(default)/documents/users/{documentId}" \
  --env-vars-file .env.yaml
```

### **Cloud Scheduler Jobs**

```bash
# ETL diário às 2h
gcloud scheduler jobs create http firestore-ee-etl-daily \
  --schedule="0 2 * * *" \
  --uri="https://${REGION}-${GCP_PROJECT_ID}.cloudfunctions.net/firestore-ee-etl" \
  --http-method=POST

# Verificação de novos isoscapes diária às 3h
gcloud scheduler jobs create http check-isoscapes-daily \
  --schedule="0 3 * * *" \
  --uri="https://${REGION}-${GCP_PROJECT_ID}.cloudfunctions.net/fraud-detection-new-isoscape" \
  --http-method=POST
```

---

## 🧪 Testes Locais

### **Teste Rápido - fraud-detection-update-sample**

```bash
cd fraud-detection-update-sample

# Instalar dependências
pip install numpy scipy

# Teste simplificado (sem Google Cloud)
python test_local.py

# Teste com mock completo (simula Earth Engine)
python mock_fraud_detection.py
```

### **Teste Python REPL**

```python
# Testar função específica
from fraud_detection_process_sample import fraud_detection_process_sample

sample = {
    "lat": -13.0845,
    "lon": -53.3795,
    "O-18": [23.5, 24.1, 23.8],
    "C-13": [-28.5, -28.3],
    "N-15": [2.1, 2.3, 2.2]
}

result = fraud_detection_process_sample(sample)
print(result)
```

### **Executar Cloud Function Localmente**

```bash
# Instalar Functions Framework
pip install functions-framework

# Executar função HTTP
functions-framework --target=etl --source=main.py --port=8080

# Testar com curl
curl -X POST http://localhost:8080
```

---

## 📊 Estrutura Completa do Projeto

```
ddf-insights-analytics/
├── README.md                                    # Este arquivo
├── CODEOWNERS                                   # GitHub code owners
│
├── fraud-detection-update-sample/              # ⭐⭐⭐⭐⭐ CORE SYSTEM
│   ├── main.py                                  # Orquestrador principal
│   ├── fraud_detection_process_sample.py        # Validação isotópica
│   ├── fraud_detection_fetch_land_use_data.py   # Análise uso da terra
│   ├── fraud_detection_generate_map_and_upload_to_gcs.py
│   ├── fraud_detection_fetch_mapbiomas_alerts.py
│   ├── requirements.txt
│   ├── README.md
│   ├── mock_fraud_detection.py                  # Mock para testes
│   ├── test_local.py                            # Testes simplificados
│   ├── analytics-visualizer-templates/
│   │   └── greppo-colab-demo.ipynb
│   └── tests/
│       ├── test_main.py
│       ├── test_fraud_detection_fetch_mapbiomas_alerts.py
│       └── json_test_data.py
│
├── Firestore-Earth-Engine-ETL/                 # ⭐⭐⭐⭐ ETL Pipeline
│   ├── main.py                                  # Pipeline ETL completo
│   ├── requirements.txt
│   ├── README.md
│   ├── types.ts                                 # TypeScript types
│   └── examples.ts                              # Exemplos de uso
│
├── fraud-detection-new-isoscape/               # ⭐⭐⭐⭐ Isoscape Monitor
│   ├── main.py                                  # Verificação de updates
│   ├── requirements.txt
│   └── README.md
│
├── fraud-detection-generate-maps/              # ⭐⭐⭐ Map Generator
│   ├── main.py                                  # Geração de mapas
│   ├── requirements.txt
│   ├── README.md
│   ├── types.ts                                 # TypeScript types
│   ├── examples.ts                              # Exemplos de uso
│   └── types-README.md
│
├── update-org-ee-auto-auth/                    # ⭐⭐⭐ Org Provisioning
│   ├── main.py                                  # Gerenciamento de orgs
│   ├── requirements.txt
│   └── README.md
│
└── user-update-iam-check/                      # ⭐⭐ User IAM Manager
    ├── main.py                                  # Orquestração de eventos
    ├── iam.py                                   # Lógica de permissões
    ├── requirements.txt
    └── README.md
```

---

## 🔗 Links Úteis

- **MapBiomas Brazil**: https://mapbiomas.org
- **Google Earth Engine**: https://earthengine.google.com
- **Firebase Firestore**: https://firebase.google.com/docs/firestore
- **Cloud Functions**: https://cloud.google.com/functions

---

## 📝 Notas de Desenvolvimento

### **Ambientes**

- **Produção**: `river-sky-386919` → Grupos `@timberid.org`
- **Teste**: `river-sky-386919` → Grupos `-test@timberid.org`

### **Convenções**

- Coordenadas sempre em formato decimal (lat, lon)
- Latitude: -90 a 90 | Longitude: -180 a 180
- Medições isotópicas: arrays com pelo menos 2 valores
- Organizações: nomes em lowercase

### **Limitações Conhecidas**

- MapBiomas limitado ao território brasileiro
- Resolução de 30 metros para dados de uso da terra
- Earth Engine tem quotas de processamento
- Timeouts de Cloud Functions: 540s (9 minutos)

---

## 🚀 Quick Start

```bash
# 1. Clonar repositório
git clone https://github.com/tnc-br/ddf-insights-analytics.git
cd ddf-insights-analytics

# 2. Configurar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r fraud-detection-update-sample/requirements.txt

# 4. Testar localmente
cd fraud-detection-update-sample
python test_local.py

# 5. Deploy (após configurar GCP)
gcloud auth login
gcloud config set project ${GCP_PROJECT_ID}
# Executar comandos de deployment acima
```

---

**Desenvolvido por**: TNC Brasil - TimberID Team  
**Última atualização**: Outubro 2025  
**Versão**: 1.0.0
