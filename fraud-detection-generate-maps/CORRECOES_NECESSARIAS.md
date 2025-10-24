# 🔧 Correções Necessárias no main.py

## ❌ Problema Atual

A Cloud Function está falhando com **2 erros críticos**:

### Erro 1: geemap.Map() sem ee_initialize=False

```
AttributeError: module 'ee.data' has no attribute '_credentials'
```

**Causa:** Na linha 128, o código deployado está:

```python
gee_mapbiomas_map = geemap.Map()  # ❌ ERRADO
```

**Deveria ser:**

```python
gee_mapbiomas_map = geemap.Map(ee_initialize=False)  # ✅ CORRETO
```

### Erro 2: Caminho incorreto do MapBiomas (RESOLVIDO localmente)

O arquivo local já foi corrigido na linha 35:

```python
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1"
```

## ✅ Código Correto (Linha 128)

**Localização:** `fraud-detection-generate-maps/main.py` linha 128

**ANTES (código deployado atualmente):**

```python
def generate_initial_map(land_use_mapbiomas_image):
    """..."""
    # ... código anterior ...

    gee_mapbiomas_map = geemap.Map()  # ❌ ERRO AQUI!
    gee_mapbiomas_map.addLayer(land_use_layers_2021_simplified, vis_params, BRAZIL_LAND_USE_LAYER_NAME)
    return gee_mapbiomas_map
```

**DEPOIS (correção necessária):**

```python
def generate_initial_map(land_use_mapbiomas_image):
    """..."""
    # ... código anterior ...

    # Disable automatic EE initialization in geemap since we already initialized
    gee_mapbiomas_map = geemap.Map(ee_initialize=False)  # ✅ CORRETO!
    gee_mapbiomas_map.addLayer(land_use_layers_2021_simplified, vis_params, BRAZIL_LAND_USE_LAYER_NAME)
    return gee_mapbiomas_map
```

## 📝 Como Fazer o Deploy Correto

### Opção 1: Via gcloud CLI (Recomendado)

```bash
cd fraud-detection-generate-maps

gcloud functions deploy fraud-detection-generate-maps \
  --gen2 \
  --runtime=python311 \
  --region=southamerica-east1 \
  --source=. \
  --entry-point=receive_pubsub_message_generate_maps \
  --trigger-topic=fraud-detection-generate-maps-daily \
  --project=river-sky-386919
```

### Opção 2: Via Console GCP

1. Acesse: https://console.cloud.google.com/functions
2. Selecione: `fraud-detection-generate-maps`
3. Clique em: **EDIT** (Editar)
4. Na aba **SOURCE CODE** (Código-fonte):
   - Certifique-se de que está em modo **Inline Editor**
   - Navegue até o arquivo `main.py`
   - Vá até a linha 128
   - **ALTERE:**
     ```python
     gee_mapbiomas_map = geemap.Map()
     ```
   - **PARA:**
     ```python
     gee_mapbiomas_map = geemap.Map(ee_initialize=False)
     ```
5. Clique em: **DEPLOY** (Implementar)
6. Aguarde: Deploy completar (~3-5 minutos)

## 🔍 Como Verificar se o Deploy Funcionou

### 1. Verificar Status do Deploy

```bash
gcloud functions describe fraud-detection-generate-maps \
  --region=southamerica-east1 \
  --project=river-sky-386919 \
  --format="value(state,updateTime)"
```

**Resultado esperado:**

```
ACTIVE  2025-10-17T14:XX:XX.XXXXZ  # Data/hora ATUAL
```

### 2. Publicar Mensagem de Teste

```bash
python easy_pubsub.py 6ed0ffa36587c49f5b54
```

### 3. Verificar Logs (após 30 segundos)

```bash
gcloud functions logs read fraud-detection-generate-maps \
  --region=southamerica-east1 \
  --limit=20 \
  --project=river-sky-386919
```

**Resultado esperado (SEM ERROS):**

```
Document exists, generating map for 6ed0ffa36587c49f5b54
Map uploaded to gs://timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

### 4. Verificar se o Mapa Foi Gerado

```bash
python verificar_mapa.py 6ed0ffa36587c49f5b54
```

**Resultado esperado:**

```
✅ MAPA EXISTE!
📦 Tamanho: XXX KB
🕐 Última modificação: ...
🌐 URL: https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

## 📊 Resumo das Correções

| Linha | Antes                                                   | Depois                                               | Status                  |
| ----- | ------------------------------------------------------- | ---------------------------------------------------- | ----------------------- |
| 35    | `mapbiomas-workspace/.../deforestation_regeneration_v1` | `mapbiomas-public/.../integration_v1`                | ✅ Corrigido localmente |
| 48    | `ee.Initialize(credentials)`                            | `ee.Initialize(credentials, project=GCP_PROJECT_ID)` | ✅ Corrigido localmente |
| 128   | `geemap.Map()`                                          | `geemap.Map(ee_initialize=False)`                    | ❌ **PRECISA DEPLOY**   |

## 🎯 Ação Necessária

**URGENTE:** Fazer deploy do `main.py` com a correção da linha 128!

O arquivo local está correto, mas a Cloud Function ainda está rodando a versão antiga sem `ee_initialize=False`.

## 📞 Link do Mapa (Após Deploy)

Após o deploy correto, o mapa estará disponível em:

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

## 🔄 Logs de Erro Atual

```
AttributeError: module 'ee.data' has no attribute '_credentials'
```

Esse erro ocorre porque `geemap.Map()` está tentando inicializar o Earth Engine automaticamente, mas já fizemos `ee.Initialize()` antes na linha 48.

A solução é passar `ee_initialize=False` para desabilitar a inicialização automática do geemap.
