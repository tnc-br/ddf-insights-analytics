# Sample Types and Validation

Este diretório contém definições de tipos TypeScript e validações Zod para o sistema de detecção de fraude de amostras.

## Estrutura

- `types/sample.ts` - Definições de tipos TypeScript
- `validation/sample-validation.ts` - Schemas de validação Zod
- `examples/` - Exemplos de uso

## Instalação

Para usar as validações Zod, instale a dependência:

```bash
npm install zod
# ou
yarn add zod
```

## Uso

### Tipos TypeScript

```typescript
import { Sample, InputSample, ProcessedSample } from "./types/sample";

// Amostra de entrada (antes do processamento)
const inputSample: InputSample = {
  lat: -13.0845,
  lon: -53.31466,
  sample_name: "test sample validity",
  created_on: "8-9-2023",
  species: "Hymenaea courbaril",
  site: "Test site",
  trusted: "untrusted",
  status: "concluded",
  visibility: "public",
  created_by_name: "Josh Wolkoff",
  d18O_cel: [22, 23, 24],
  d15N_cel: [-21, -29, -18],
  d13C_cel: [16, 14, 18],
};
```

### Validação com Zod

```typescript
import {
  validateInputSample,
  validateSample,
} from "./validation/sample-validation";

// Validar amostra de entrada
const result = validateInputSample(inputData);
if (result.success) {
  console.log("Amostra válida:", result.data);
} else {
  console.error("Erros de validação:", result.error.issues);
}

// Validar amostra completa (após processamento)
const fullResult = validateSample(processedData);
if (fullResult.success) {
  console.log("Amostra processada válida:", fullResult.data);
} else {
  console.error("Erros de validação:", fullResult.error.issues);
}
```

## Campos da Amostra

### Campos Obrigatórios

- `lat` (number): Latitude (-90 a 90 graus)
- `lon` (number): Longitude (-180 a 180 graus)
- `sample_name` (string): Nome da amostra (1-255 caracteres)
- `created_on` (string): Data de criação (formato DD-MM-YYYY)
- `species` (string): Espécie (1-100 caracteres)
- `site` (string): Local da coleta (1-100 caracteres)
- `trusted` ("trusted" | "untrusted"): Status de confiança
- `status` ("concluded" | "pending" | "in_progress"): Status do processamento
- `visibility` ("public" | "private"): Visibilidade da amostra
- `created_by_name` (string): Nome do criador (1-100 caracteres)

### Campos de Medição (Opcionais)

- `d18O_cel` (number[]): Medições de isótopo de oxigênio (mínimo 2 valores)
- `d15N_cel` (number[]): Medições de isótopo de nitrogênio (mínimo 2 valores)
- `d13C_cel` (number[]): Medições de isótopo de carbono (mínimo 2 valores)

**Nota**: Pelo menos um tipo de medição isotópica é necessário para a análise de detecção de fraude.

### Campos de Saída (Gerados pelo Sistema)

- `validity` ("Possible" | "Not Likely"): Resultado da validação
- `validity_details`: Detalhes estatísticos da análise
- `water_pct`: Porcentagens de água na região
- `land_use_*_pct`: Porcentagens de uso da terra por ano (2011-2021)
- `alerts`: Alertas do MapBiomas na região

## Validações Aplicadas

### Coordenadas Geográficas

- Latitude: -90 a 90 graus
- Longitude: -180 a 180 graus

### Formatos de Data

- `created_on`: DD-MM-YYYY
- `detectedAt` (alertas): DD/MM/YYYY
- `alertInsertedAt` (alertas): DD/MM/YYYY HH:mm

### Medições Isotópicas

- Mínimo 2 valores por array
- Máximo 50 valores por array
- Pelo menos um tipo de medição (d18O_cel, d15N_cel, ou d13C_cel) obrigatório

### Porcentagens

- Valores entre 0 e 1 (0% a 100%)
- P-values entre 0 e 1

### Strings

- Tamanhos mínimos e máximos definidos
- URLs válidas para alertas e imagens

## Exemplos de Erros de Validação

```typescript
// Latitude inválida
{
  "code": "too_small",
  "minimum": -90,
  "path": ["lat"],
  "message": "Latitude must be between -90 and 90 degrees"
}

// Medições insuficientes
{
  "code": "too_small",
  "minimum": 2,
  "path": ["d18O_cel"],
  "message": "Oxygen isotope measurements must have at least 2 values"
}

// Formato de data inválido
{
  "code": "invalid_string",
  "path": ["created_on"],
  "message": "Date must be in DD-MM-YYYY format"
}
```

## Integração com o Sistema Python

Estes tipos e validações podem ser usados em:

1. **Frontend TypeScript/JavaScript** - Validação antes do envio
2. **APIs Node.js** - Validação de entrada
3. **Documentação** - Referência de tipos
4. **Testes** - Geração de dados de teste válidos

O sistema Python continuará funcionando independentemente, mas essas definições garantem consistência entre diferentes partes do sistema.
