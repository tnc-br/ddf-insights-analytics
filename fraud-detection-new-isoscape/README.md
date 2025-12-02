# Fraud Detection New Isoscape

Este sistema implementa uma **Cloud Function HTTP** que **detecta atualizações em isoscapes** no Google Earth Engine e **re-executa automaticamente a análise de detecção de fraude** em todas as amostras não confiáveis quando novos dados de referência estão disponíveis.

## Funcionalidade Principal

O arquivo `main.py` define uma função HTTP `reevaluate` que:

1. **Monitora isoscapes** no Google Earth Engine
2. **Detecta atualizações recentes** (últimas 27 horas)
3. **Re-processa todas as amostras** quando novos isoscapes são detectados

## Fluxo de Execução

### 1. **Inicialização**

- Autentica com Google Earth Engine usando service account
- Configura acesso ao Firestore
- Define caminho dos isoscapes: `projects/{GCP_PROJECT_ID}/assets/isoscapes`

### 2. **Verificação de Atualizações** (`is_isoscapes_updated`)

```python
# Verifica se algum isoscape foi atualizado nas últimas 27 horas
(datetime.now()-timedelta(hours=27)) <= update_date <= datetime.now()
```

**Processo:**

- Lista todos os assets na pasta de isoscapes
- Verifica o `updateTime` de cada asset
- Retorna `True` se algum foi atualizado recentemente

### 3. **Re-processamento de Amostras**

Se isoscapes foram atualizados:

- **Busca todas** as amostras da coleção `untrusted_samples`
- **Re-escreve** cada documento no Firestore (mesmo conteúdo)
- **Dispara** o sistema `fraud-detection-update-sample` automaticamente

## Como Funciona a Integração

### 🔄 **Trigger Chain**

```
Nova Isoscape → fraud-detection-new-isoscape → Re-escreve Firestore → fraud-detection-update-sample
```

1. **Novo isoscape** é adicionado ao Earth Engine
2. **Esta função** detecta a mudança
3. **Re-escreve** documentos no Firestore (mesmo conteúdo)
4. **Firestore trigger** dispara `fraud-detection-update-sample`
5. **Análise** é re-executada com novos dados de referência

### 📊 **Dados Analisados**

- **Isoscapes**: Mapas de referência isotópica (d18O, d13C, d15N)
- **Amostras**: Documentos em `untrusted_samples` que precisam ser validados
- **Janela temporal**: 27 horas para detectar atualizações

## Estrutura de Assets no Earth Engine

```
projects/{GCP_PROJECT_ID}/assets/
└── isoscapes/
    ├── d18O_isoscape_v1
    ├── d18O_isoscape_v2
    ├── d13C_isoscape_v1
    └── d15N_isoscape_v1
```

## Variáveis de Ambiente

- `GCP_PROJECT_ID`: ID do projeto no Google Cloud Platform

## Dependências

- **Google Earth Engine**: Acesso aos isoscapes de referência
- **Google Firestore**: Armazenamento de amostras
- **Google Cloud Functions**: Execução da função HTTP

## Endpoint

A função é exposta como endpoint HTTP que pode ser:

- **Chamado manualmente** para forçar verificação
- **Integrado** com sistemas de CI/CD
- **Agendado** via Cloud Scheduler

## Casos de Uso

### ✅ **Quando é Útil**

- **Novos isoscapes** são publicados
- **Melhorias** nos dados de referência
- **Atualizações** nos modelos isotópicos
- **Re-análise** de todo o dataset

### 📝 **Exemplo de Uso**

```bash
# Chamar endpoint HTTP
curl -X GET https://your-region-your-project.cloudfunctions.net/reevaluate
```

### 🔄 **Fluxo Automático**

1. Cientista publica novo isoscape no Earth Engine
2. Função detecta mudança nas próximas 27 horas
3. Todas as amostras são automaticamente re-analisadas
4. Resultados atualizados ficam disponíveis

## Versionamento (TODO)

O código inclui um comentário sobre implementação futura:

```python
# TODO Add versionning to assets (allow maximum to ten versions)
```

Isso sugere planos para:

- **Controle de versão** dos isoscapes
- **Limite** de 10 versões por asset
- **Rastreabilidade** das mudanças

## Integração com Outros Sistemas

### 🔗 **Sistemas Relacionados**

- **fraud-detection-update-sample**: Processa amostras individuais
- **Earth Engine Assets**: Fonte dos dados de referência
- **Firestore Collections**: `untrusted_samples`

### 📋 **Campos Esperados nas Amostras**

- Coordenadas (`lat`, `lon`)
- Medições isotópicas (`d18O_cel`, `d13C_cel`, `d15N_cel`)
- Metadados da amostra

## Propósito

Este sistema garante que:

1. **Dados sempre atualizados**: Amostras são re-analisadas com isoscapes mais recentes
2. **Automação completa**: Não requer intervenção manual
3. **Consistência**: Todas as amostras usam os mesmos dados de referência
4. **Eficiência**: Só re-processa quando há mudanças reais

É essencialmente um **sistema de invalidação de cache** que garante que as análises de detecção de fraude sempre utilizem os dados de referência isotópica mais atualizados disponíveis.
