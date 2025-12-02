# ddf-insights-analytics

## Tests

To run the unit tests, run from the root of the repo:

```
python3 -m unittest tests/test_main.py
```

Este arquivo implementa uma Cloud Function do Google Cloud que funciona como um sistema de detecção de fraude para análise de amostras geoespaciais. Aqui está o que ele faz:

Funcionalidade Principal
O arquivo define uma função chamada evaluate que é ativada automaticamente sempre que há mudanças em documentos do Firestore (banco de dados NoSQL do Google Cloud).

Fluxo de Execução
Trigger de Firestore: A função é disparada quando um documento no Firestore é criado ou atualizado

Verificação de Mudanças:

Analisa se as mudanças foram feitas em campos de entrada (não em campos de saída)
Se apenas campos de saída foram alterados, pula o processamento para evitar loops infinitos
Processamento de Dados Geoespaciais (4 etapas principais):

ETAPA 1: Valida a amostra usando fraud_detection_process_sample()

ETAPA 2: Calcula porcentagens de uso da terra usando dados do MapBiomas via fraud_detection_fetch_land_use_data()

ETAPA 3: Gera e faz upload de um mapa visual para o Google Cloud Storage via fraud_detection_generate_map_and_upload_to_gcs()

ETAPA 4: Consulta a API do MapBiomas Alerta para buscar alertas de desmatamento próximos às coordenadas via fraud_detection_fetch_mapbiomas_alerts()

Atualização Final: Salva todos os resultados calculados de volta no documento do Firestore

Campos Analisados
O sistema trabalha com:

Coordenadas (lat, lon)
Dados de uso da terra (vegetação primária, secundária, áreas antrópicas)
Porcentagem de água
Alertas de desmatamento
Validação da amostra
Integração com Serviços
Google Earth Engine: Para análise de dados geoespaciais
Firestore: Para armazenamento de dados
Google Cloud Storage: Para armazenar mapas gerados
MapBiomas: Para dados de uso da terra e alertas ambientais
Este sistema parece ser usado para monitoramento ambiental e detecção de fraudes relacionadas a mudanças no uso da terra, especialmente útil para projetos de conservação ou compliance ambiental.
