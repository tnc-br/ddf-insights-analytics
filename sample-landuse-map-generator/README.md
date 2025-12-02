# Sample Map Generator

**Cloud Function** que gera mapas interativos HTML de uso do solo usando Google Earth Engine e MapBiomas.

## 🎯 Funcionalidade

Trigado automaticamente quando um documento é criado/atualizado na coleção `untrusted_samples`, gerando:

- **Visualização MapBiomas** - Uso do solo Collection 8 (2021)
- **Buffer 1km** - Círculo branco mostrando área de análise isotópica
- **Contexto 10km** - Área regional para análise de paisagem
- **Mapa Interativo** - HTML com zoom/pan usando geemap/Leaflet

## 🔥 Trigger

**Firestore Document Write** - `untrusted_samples/{documentId}`

```
Firestore update → Cloud Function → Earth Engine → MapBiomas → GCS
                                                                  ↓
                                              Document.map_url ←─┘
```

### Prevenção de Loop Infinito

A função **ignora** atualizações que modificam apenas campos de saída:

- `map_url` - URL do mapa no GCS
- `map_generated_at` - Timestamp da geração

Exemplo de log quando pulado:

```
Only output fields updated: {'map_url', 'map_generated_at'}. Skipping map generation.
```

## 📋 Campos Requeridos

O documento **deve conter**:

```javascript
{
  "lat": -15.793889,  // Latitude (decimal degrees)
  "lon": -47.882778   // Longitude (decimal degrees)
}
```

Campos opcionais ignorados (não trigam regeneração):

- `map_url` - Preenchido automaticamente após geração
- `map_generated_at` - Timestamp UTC da geração

## 🗺️ Output

### Documento Firestore atualizado:

```javascript
{
  "lat": -15.793889,
  "lon": -47.882778,
  "map_url": "https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html",
  "map_generated_at": "2025-11-21T14:30:15.123456"
}
```

### Arquivo no GCS:

- **Bucket:** `timberid-public-to-internet`
- **Path:** `timberid-maps/{documentId}.html`
- **Formato:** HTML interativo (geemap + Leaflet)
- **Acesso:** Público (URL pode ser aberta diretamente)

## 🚀 Deploy

### Usando gcloud CLI:

```bash
cd fraud-detection-generate-maps

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

### Variáveis de Ambiente:

| Variável         | Valor Padrão       | Descrição                    |
| ---------------- | ------------------ | ---------------------------- |
| `GCP_PROJECT_ID` | `river-sky-386919` | Project ID para Earth Engine |

## 🧪 Teste Local

### Instalação:

```bash
pip install -r requirements.txt
```

### Executar função localmente:

```bash
functions-framework --target=generate_sample_map --signature-type=cloudevent
```

### Testar com curl:

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "value": {
        "name": "projects/river-sky-386919/databases/(default)/documents/untrusted_samples/test123"
      }
    }
  }'
```

## 📊 MapBiomas Collection 8

### Dataset Earth Engine:

```
projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1
```

### Classes de Uso do Solo (valores 0-49):

- **1-5:** Florestas (nativas, savana, mangue)
- **11-13:** Áreas não florestais (wetlands, pastagens)
- **15:** Pastagem
- **18-21:** Agricultura (temporária, permanente)
- **23-31:** Áreas não vegetadas (urbano, mineração)
- **33:** Água

### Ano de Referência:

**2021** (band `classification_2021`) - Mais recente com cobertura completa

## 🔧 Arquitetura

### Comparação com versão anterior:

#### ❌ Antiga (Pub/Sub):

```
Cloud Scheduler → Pub/Sub → Cloud Function
                     ↓
            (mensagens em fila)
```

- Complexo (3 componentes)
- Latência adicional
- Difícil debugar
- Requer Pub/Sub topic + Cloud Scheduler

#### ✅ Nova (Firestore Trigger):

```
Firestore update → Cloud Function
```

- Simples (trigger direto)
- Reação instantânea
- Mesmo padrão do `fraud-detection-update-sample`
- Sem componentes externos

## 🐛 Troubleshooting

### Erro: "Document missing lat/lon coordinates"

**Causa:** Documento não tem campos `lat` e `lon`  
**Solução:** Adicionar coordenadas ao documento antes de salvar

### Erro: "Failed to initialize Earth Engine"

**Causa:** Service account sem permissões Earth Engine  
**Solução:** Verificar IAM roles do service account da Cloud Function

### Erro: Loop infinito de execuções

**Causa:** Função trigando a si mesma ao atualizar `map_url`  
**Solução:** Verificar lógica de `OUTPUT_FIELDS` no início da função

### Logs úteis:

```bash
# Ver logs da função
gcloud functions logs read sample-map-generator --limit=50

# Ver erros apenas
gcloud functions logs read sample-map-generator --limit=50 | grep ERROR
```

## 📚 Referências

- [MapBiomas Collection 8](https://mapbiomas.org/colecoes-mapbiomas-1)
- [Earth Engine Python API](https://developers.google.com/earth-engine/guides/python_install)
- [geemap Documentation](https://geemap.org/)
- [Cloud Functions Firestore Triggers](https://cloud.google.com/functions/docs/calling/cloud-firestore)

## 🔗 Serviços Relacionados

- **`fraud-detection-update-sample`** - Valida amostras e calcula land use
- **`Firestore-Earth-Engine-ETL`** - Sincroniza dados para Earth Engine
- **`user-update-iam-check`** - Gerencia permissões de usuários

---

**Última atualização:** 21 de novembro de 2025  
**Autor:** TimberID Analytics Team
