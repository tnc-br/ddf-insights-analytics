# Fraud Detection Generate Maps - Types & Validation

Sistema de tipos TypeScript e validações Zod para o módulo de geração de mapas do sistema de detecção de fraude TimberID.

## Visão Geral

Este módulo fornece definições de tipos TypeScript e esquemas de validação Zod para garantir a integridade e consistência dos dados utilizados no sistema de geração de mapas interativos para detecção de fraude.

## Arquitetura dos Dados

```
Sample de Entrada → Validação Zod → Processamento → Mapa Interativo → GCS Storage
```

## Principais Tipos de Dados

### 1. MapGenerationSample

Estrutura principal para amostras processadas pelo sistema de geração de mapas.

```typescript
interface MapGenerationSample {
  // Identificação obrigatória
  sample_name: string; // Nome da amostra
  code_lab: string; // Código do laboratório
  created_by: string; // ID do usuário criador

  // Coordenadas obrigatórias
  lat: number; // Latitude (-90 a 90)
  lon: number; // Longitude (-180 a 180)

  // Dados isotópicos obrigatórios
  d18O_cel: number[]; // Medições oxigênio-18 (min: 2, max: 50)
  d15N_cel?: number[]; // Medições nitrogênio-15 (opcional)
  d13C_cel?: number[]; // Medições carbono-13 (opcional)

  // Metadados da amostra
  species: string; // Espécie da madeira
  trusted: "trusted" | "untrusted";
  status: "pending" | "processing" | "concluded" | "failed";
  created_on: string; // Data de criação

  // Dados enriquecidos (adicionados pelo sistema)
  validity?: "valid" | "invalid" | number;
  water_pct?: WaterData;
  land_use_anthropic_pct?: LandUseData;
  alerts?: MapbiomasAlert[];
}
```

### 2. MapGenerationMessage

Estrutura para mensagens Pub/Sub que acionam a geração de mapas.

```typescript
interface MapGenerationMessage {
  // Opção 1: Coordenadas específicas
  latitude?: number;
  longitude?: number;
  document_id?: string;

  // Opção 2: Comando especial
  command?: "ALL_MAPS";
}
```

### 3. Coordinates

Coordenadas geográficas com validação rigorosa.

```typescript
interface Coordinates {
  latitude: number; // -90 a 90
  longitude: number; // -180 a 180
}
```

### 4. MapbiomasAlert

Alertas de desmatamento obtidos da API MapBiomas.

```typescript
interface MapbiomasAlert {
  alertCode: string;
  areaHa: number;
  detectedAt: string;
  distance_to_point: number;
  coordinates: Coordinates;
  before: SatelliteImage;
  after: SatelliteImage;
}
```

### 5. ValidityDetails

Resultados detalhados da análise isotópica de validação.

```typescript
interface ValidityDetails {
  p_value_oxygen?: number; // 0 a 1
  p_value_carbon?: number; // 0 a 1
  p_value_nitrogen?: number; // 0 a 1
  reference_oxygen_isoscape_name?: string;
  d18O_cel_sample_mean?: number;
  d18O_cel_reference_mean?: number;
  // ... outros campos estatísticos
}
```

## Esquemas de Validação Zod

### Validações Principais

```typescript
// Sample completa
const MapGenerationSampleSchema = z.object({
  sample_name: z.string().min(1),
  lat: z.number().min(-90).max(90),
  lon: z.number().min(-180).max(180),
  d18O_cel: z.array(z.number()).min(2).max(50),
  // ... outras validações
});

// Coordenadas geográficas
const CoordinatesSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
});

// Mensagem Pub/Sub
const MapGenerationMessageSchema = z.union([
  z.object({
    latitude: z.number().min(-90).max(90),
    longitude: z.number().min(-180).max(180),
    document_id: z.string().min(1),
  }),
  z.object({
    command: z.literal("ALL_MAPS"),
  }),
]);
```

### Regras de Validação

| Campo       | Regra                  | Descrição                        |
| ----------- | ---------------------- | -------------------------------- |
| `lat`       | -90 ≤ valor ≤ 90       | Latitude válida                  |
| `lon`       | -180 ≤ valor ≤ 180     | Longitude válida                 |
| `d18O_cel`  | Array com 2-50 números | Medições isotópicas mínimas      |
| `species`   | String não vazia       | Espécie obrigatória              |
| `p_value_*` | 0 ≤ valor ≤ 1          | Valores de probabilidade válidos |
| `*_pct`     | 0 ≤ valor ≤ 100        | Percentuais válidos              |
| URLs        | Formato URL válido     | Links para imagens de satélite   |

## Funções de Validação

### Validação de Sample

```typescript
function validateMapGenerationSample(data: unknown): MapGenerationSample {
  const result = MapGenerationSampleSchema.safeParse(data);
  if (!result.success) {
    throw new Error(`Validação falhou: ${errors}`);
  }
  return result.data;
}
```

### Validação de Mensagem Pub/Sub

```typescript
function validateMapGenerationMessage(data: unknown): MapGenerationMessage {
  // Valida mensagem de coordenadas OU comando ALL_MAPS
}
```

### Validação de Coordenadas

```typescript
function validateCoordinates(data: unknown): Coordinates {
  // Valida faixas de latitude e longitude
}
```

## Type Guards

Funções para verificação de tipos em tempo de execução:

```typescript
// Verifica se sample tem coordenadas válidas
function hasValidCoordinates(sample: Partial<MapGenerationSample>): boolean;

// Verifica se mensagem é comando ALL_MAPS
function isAllMapsCommand(message: MapGenerationMessage): boolean;

// Verifica se mensagem contém coordenadas específicas
function isCoordinateMessage(message: MapGenerationMessage): boolean;
```

## Tipos Utilitários

### Tipos Derivados

```typescript
// Sample mínima para geração de mapas
type MinimalMapSample = Pick<MapGenerationSample, "lat" | "lon">;

// Sample com dados completos enriquecidos
type EnrichedMapSample = Required<
  Pick<
    MapGenerationSample,
    "lat" | "lon" | "water_pct" | "land_use_anthropic_pct" | "alerts"
  >
>;

// Resultado da geração de mapa
interface MapGenerationResult {
  document_id: string;
  html_file_path: string;
  gcs_upload_path: string;
  generation_timestamp: string;
  coordinates: Coordinates;
  processing_time_ms: number;
}
```

### Configuração do Sistema

```typescript
interface MapGenerationConfig {
  gcs_bucket_name: string; // Bucket do Google Cloud Storage
  gcs_folder_name: string; // Pasta para armazenar mapas
  gcp_project_id: string; // ID do projeto GCP
  topic_id: string; // Tópico Pub/Sub
  mapbiomas_asset_path: string; // Caminho do asset MapBiomas no Earth Engine
}
```

## Uso Prático

### 1. Validação de Entrada

```typescript
import { validateMapGenerationSample } from "./types";

// Validar dados recebidos via Pub/Sub
try {
  const validSample = validateMapGenerationSample(rawData);
  // Processar sample validada
} catch (error) {
  console.error("Dados inválidos:", error.message);
}
```

### 2. Type Guards

```typescript
import { hasValidCoordinates, isAllMapsCommand } from "./types";

// Verificar se sample pode gerar mapa
if (hasValidCoordinates(sample)) {
  generateMap(sample.lat, sample.lon);
}

// Verificar tipo de mensagem
if (isAllMapsCommand(message)) {
  processAllSamples();
} else {
  processSingleSample(message);
}
```

### 3. Validação de Coordenadas

```typescript
import { validateCoordinates } from "./types";

// Validar coordenadas antes de usar com Earth Engine
const coords = validateCoordinates({ latitude: -13.0845, longitude: -53.3795 });
const point = ee.Geometry.Point(coords.longitude, coords.latitude);
```

## Integração com Sistema

### Fluxo de Dados

1. **Entrada**: Mensagem Pub/Sub → `validateMapGenerationMessage()`
2. **Processamento**: Firestore document → `validateMapGenerationSample()`
3. **Coordenadas**: Extração → `validateCoordinates()`
4. **Saída**: Mapa gerado → `MapGenerationResult`

### Tratamento de Erros

```typescript
// Exemplo de tratamento robusto
function processMapGeneration(rawMessage: unknown) {
  try {
    const message = validateMapGenerationMessage(rawMessage);

    if (isAllMapsCommand(message)) {
      return processAllMaps();
    }

    if (isCoordinateMessage(message)) {
      const sample = await getSampleFromFirestore(message.document_id);
      const validSample = validateMapGenerationSample(sample);

      if (hasValidCoordinates(validSample)) {
        return generateMapForSample(validSample);
      }
    }
  } catch (error) {
    console.error("Erro na validação:", error.message);
    throw new Error(`Processamento falhou: ${error.message}`);
  }
}
```

## Dependências

### Produção

- **zod**: `^3.22.4` - Validação de schemas e tipos

### Desenvolvimento

- **typescript**: `^5.0.0` - Compilador TypeScript
- **@types/node**: `^20.0.0` - Tipos Node.js

## Estrutura de Arquivos

```
fraud-detection-generate-maps/
├── types.ts           # Definições de tipos e validações (este arquivo)
├── examples.ts        # Exemplos de uso e demonstrações
├── main.py           # Cloud Function principal (Python)
├── requirements.txt  # Dependências Python
└── README.md         # Documentação do sistema completo
```

## Padrões de Desenvolvimento

### Naming Conventions

- **Interfaces**: PascalCase (`MapGenerationSample`)
- **Schemas**: PascalCase + "Schema" (`MapGenerationSampleSchema`)
- **Functions**: camelCase (`validateMapGenerationSample`)
- **Constants**: UPPER_SNAKE_CASE (`ALL_MAPS_MESSAGE`)

### Validação Rigorosa

- Todos os campos obrigatórios devem ter validação
- Faixas numéricas devem ser explicitamente definidas
- URLs devem ser validadas como formato válido
- Arrays devem ter limites mínimos e máximos definidos

### Error Handling

- Mensagens de erro descritivas em português
- Caminhos de campos incluídos nas mensagens de erro
- Validação fail-fast com todas as mensagens de erro

## Roadmap

### Melhorias Futuras

- [ ] Adicionar validação de formato de data ISO 8601
- [ ] Implementar validação de espécies contra lista conhecida
- [ ] Adicionar schemas para dados temporais de mudança de uso da terra
- [ ] Implementar validação de precisão de coordenadas
- [ ] Adicionar tipos para resultados de Earth Engine
- [ ] Integrar com OpenAPI/JSON Schema para documentação automática

### Otimizações

- [ ] Cache de schemas compilados
- [ ] Validação assíncrona para grandes datasets
- [ ] Streaming validation para processamento em lote
- [ ] Métricas de performance de validação

## Contribuição

Para adicionar novos tipos ou validações:

1. Defina a interface TypeScript
2. Crie o schema Zod correspondente
3. Implemente função de validação
4. Adicione type guards se necessário
5. Inclua exemplos de uso
6. Atualize documentação

## Exemplo Completo

```typescript
import {
  validateMapGenerationSample,
  hasValidCoordinates,
  type MapGenerationSample,
} from "./types";

// Sample de exemplo
const sampleData = {
  sample_name: "Hymenaea courbaril - MT",
  code_lab: "fd1239d5488215a23440",
  created_by: "user123",
  lat: -13.0845,
  lon: -53.3795,
  d18O_cel: [23.5, 24.1, 23.8],
  species: "Hymenaea courbaril",
  trusted: "untrusted",
  status: "concluded",
  created_on: "2023-09-08",
};

// Validação e uso
try {
  const validSample = validateMapGenerationSample(sampleData);

  if (hasValidCoordinates(validSample)) {
    console.log(`✅ Sample válida: ${validSample.sample_name}`);
    console.log(`📍 Coordenadas: ${validSample.lat}, ${validSample.lon}`);
    // Prosseguir com geração do mapa...
  }
} catch (error) {
  console.error("❌ Validação falhou:", error.message);
}
```
