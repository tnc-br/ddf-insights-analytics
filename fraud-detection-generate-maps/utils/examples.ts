// ============================================================================
// FRAUD DETECTION GENERATE MAPS - EXEMPLOS DE USO
// ============================================================================

// Este arquivo contém exemplos de uso dos tipos TypeScript e validações Zod
// para o sistema fraud-detection-generate-maps

import {
  validateMapGenerationSample,
  validateMapGenerationMessage,
  validateCoordinates,
  hasValidCoordinates,
  isAllMapsCommand,
  isCoordinateMessage,
  type MapGenerationSample,
  type MapGenerationMessage,
  type Coordinates,
  type MapbiomasAlert,
} from "./types";

// ============================================================================
// EXEMPLOS DE SAMPLES VÁLIDAS
// ============================================================================

// Sample mínima válida para geração de mapas
const minimalValidSample: MapGenerationSample = {
  // Identificação obrigatória
  sample_name: "Amostra de Hymenaea courbaril - Região MT",
  code_lab: "fd1239d5488215a23440",
  created_by: "UtGYAXLklJd6S3dEHQXEJtKNsnk1",

  // Coordenadas obrigatórias (Mato Grosso, Brasil)
  lat: -13.0845,
  lon: -53.3795,

  // Dados isotópicos obrigatórios
  d18O_cel: [23.5, 24.1, 23.8], // Pelo menos 2 medições necessárias

  // Informações da amostra
  species: "Hymenaea courbaril",
  trusted: "untrusted",
  status: "concluded",

  // Metadados temporais
  created_on: "8-9-2023",
};

// Sample completa com todos os dados enriquecidos
const enrichedSample: MapGenerationSample = {
  ...minimalValidSample,

  // Dados isotópicos adicionais
  d15N_cel: [2.1, 2.3, 2.0],
  d13C_cel: [-25.4, -25.7, -25.1],

  // Dados organizacionais
  org_name: "Organização de Pesquisa Florestal",
  date_of_harvest: "15-7-2023",
  last_updated_by: "Josh Wolkoff",

  // Resultados da validação
  validity: "invalid",
  validity_details: {
    p_value_oxygen: 0.001193676470473496,
    p_value_nitrogen: 0.010445452763826784,
    p_value_carbon: 0.00034070435105630674,
    reference_oxygen_isoscape_name: "brazil_isoscape_v1",
    reference_oxygen_isoscape_creation_date: "2023-01-15",
    reference_oxygen_isoscape_precision: 0.85,
    reference_oxygen_isoscape_recall: 0.78,
    d18O_cel_sample_mean: 23.8,
    d18O_cel_sample_variance: 0.09,
    d18O_cel_reference_mean: 25.2,
    d18O_cel_reference_variance: 1.2,
    p_value: 4.248069198730162e-9,
    p_value_threshold: 0.05,
  },

  // Dados de uso da terra
  water_pct: {
    is_point_water: false,
    water_mean_in_1km_buffer: 2.5,
    water_mean_in_10km_buffer: 8.7,
  },
  land_use_anthropic_pct: {
    "2019": 15.2,
    "2020": 18.6,
    "2021": 22.1,
  },
  land_use_primary_vegetation_pct: {
    "2019": 76.8,
    "2020": 71.4,
    "2021": 65.9,
  },
  land_use_secondary_vegetation_or_regrowth_pct: {
    "2019": 8.0,
    "2020": 10.0,
    "2021": 12.0,
  },

  // Alertas MapBiomas próximos
  alerts: [
    {
      alertCode: "598526",
      areaHa: 4.4139,
      detectedAt: "01/05/2022",
      url: "https://plataforma.alerta.mapbiomas.org/laudo/598526",
      distance_to_point: 11.01548890454279,
      coordinates: {
        latitude: -13.143667047067119,
        longitude: -53.29779479726426,
      },
      alertInsertedAt: "06/07/2022 14:44",
      before: {
        url: "https://storage.googleapis.com/alerta-public/IMAGES/574931/before_deforestation.png",
        satellite: "PlanetScope",
      },
      after: {
        url: "https://storage.googleapis.com/alerta-public/IMAGES/600014/after_deforestation.png",
        satellite: "PlanetScope",
      },
    },
  ],

  // Dados adicionais
  n_wood: [12, 15, 14],
};

// ============================================================================
// EXEMPLOS DE MENSAGENS PUB/SUB
// ============================================================================

// Mensagem para processar sample específica
const specificSampleMessage: MapGenerationMessage = {
  latitude: -13.0845,
  longitude: -53.3795,
  document_id: "fd1239d5488215a23440",
};

// Mensagem para processar todos os mapas
const allMapsMessage: MapGenerationMessage = {
  command: "ALL_MAPS",
};

// ============================================================================
// EXEMPLOS DE COORDENADAS
// ============================================================================

// Coordenadas válidas no Brasil
const brazilCoordinates: Coordinates = {
  latitude: -15.7942, // Brasília
  longitude: -47.8822,
};

// Coordenadas na Amazônia
const amazonCoordinates: Coordinates = {
  latitude: -3.4653, // Manaus
  longitude: -62.2159,
};

// ============================================================================
// EXEMPLOS DE VALIDAÇÃO
// ============================================================================

/**
 * Exemplo de validação de sample com tratamento de erros
 */
function exampleValidateSample() {
  try {
    // Validação bem-sucedida
    const validSample = validateMapGenerationSample(minimalValidSample);
    console.log("✅ Sample válida:", validSample.sample_name);
    return validSample;
  } catch (error) {
    console.error("❌ Erro na validação da sample:", error.message);
    throw error;
  }
}

/**
 * Exemplo de validação de mensagem Pub/Sub
 */
function exampleValidateMessage() {
  try {
    // Validação de mensagem específica
    const validMessage = validateMapGenerationMessage(specificSampleMessage);
    console.log("✅ Mensagem válida:", validMessage);

    // Validação de comando ALL_MAPS
    const allMapsCommand = validateMapGenerationMessage(allMapsMessage);
    console.log("✅ Comando ALL_MAPS válido:", allMapsCommand);

    return { validMessage, allMapsCommand };
  } catch (error) {
    console.error("❌ Erro na validação da mensagem:", error.message);
    throw error;
  }
}

/**
 * Exemplo de validação de coordenadas
 */
function exampleValidateCoordinates() {
  try {
    // Coordenadas válidas
    const validCoords = validateCoordinates(brazilCoordinates);
    console.log("✅ Coordenadas válidas:", validCoords);

    // Coordenadas inválidas (irá falhar)
    const invalidCoords = {
      latitude: 95, // Inválido: > 90
      longitude: -200, // Inválido: < -180
    };

    validateCoordinates(invalidCoords); // Irá lançar erro
  } catch (error) {
    console.error("❌ Coordenadas inválidas:", error.message);
  }
}

/**
 * Exemplo de uso de type guards
 */
function exampleTypeGuards() {
  const partialSample = {
    sample_name: "Teste",
    lat: -13.0845,
    lon: -53.3795,
  };

  // Verifica se tem coordenadas válidas
  if (hasValidCoordinates(partialSample)) {
    console.log(
      "✅ Sample tem coordenadas válidas:",
      partialSample.lat,
      partialSample.lon
    );
  }

  // Verifica tipo de mensagem
  if (isAllMapsCommand(allMapsMessage)) {
    console.log("✅ É comando ALL_MAPS:", allMapsMessage.command);
  }

  if (isCoordinateMessage(specificSampleMessage)) {
    console.log(
      "✅ É mensagem com coordenadas:",
      specificSampleMessage.latitude,
      specificSampleMessage.longitude
    );
  }
}

// ============================================================================
// EXEMPLOS DE SAMPLES INVÁLIDAS (PARA TESTES)
// ============================================================================

// Sample com coordenadas inválidas
const invalidCoordinatesSample = {
  ...minimalValidSample,
  lat: 95, // Inválido: latitude > 90
  lon: -200, // Inválido: longitude < -180
};

// Sample com dados isotópicos insuficientes
const insufficientIsotopeData = {
  ...minimalValidSample,
  d18O_cel: [23.5], // Inválido: apenas 1 medição (mínimo 2)
};

// Sample com espécie vazia
const emptySample = {
  ...minimalValidSample,
  species: "", // Inválido: espécie vazia
};

// Mensagem Pub/Sub inválida
const invalidMessage = {
  latitude: "invalid", // Inválido: deve ser number
  longitude: -53.3795,
  document_id: "", // Inválido: ID vazio
};

// ============================================================================
// FUNÇÃO DE DEMONSTRAÇÃO COMPLETA
// ============================================================================

/**
 * Demonstração completa do sistema de validação
 */
export function demonstrateMapGenerationValidation() {
  console.log("🗺️  DEMONSTRAÇÃO - FRAUD DETECTION GENERATE MAPS");
  console.log("================================================");

  // 1. Validação de samples
  console.log("\n1. VALIDAÇÃO DE SAMPLES:");
  try {
    exampleValidateSample();
  } catch (error) {
    console.error("Erro na validação de sample");
  }

  // 2. Validação de mensagens
  console.log("\n2. VALIDAÇÃO DE MENSAGENS PUB/SUB:");
  try {
    exampleValidateMessage();
  } catch (error) {
    console.error("Erro na validação de mensagem");
  }

  // 3. Validação de coordenadas
  console.log("\n3. VALIDAÇÃO DE COORDENADAS:");
  exampleValidateCoordinates();

  // 4. Type guards
  console.log("\n4. TYPE GUARDS:");
  exampleTypeGuards();

  // 5. Demonstração de erros
  console.log("\n5. DEMONSTRAÇÃO DE ERROS:");

  try {
    validateMapGenerationSample(invalidCoordinatesSample);
  } catch (error) {
    console.log("❌ Coordenadas inválidas capturadas:", error.message);
  }

  try {
    validateMapGenerationSample(insufficientIsotopeData);
  } catch (error) {
    console.log("❌ Dados isotópicos insuficientes capturados:", error.message);
  }

  try {
    validateMapGenerationMessage(invalidMessage);
  } catch (error) {
    console.log("❌ Mensagem inválida capturada:", error.message);
  }

  console.log("\n✅ Demonstração completa finalizada!");
}

// ============================================================================
// UTILITÁRIOS PARA DESENVOLVIMENTO
// ============================================================================

/**
 * Gera sample de teste com coordenadas aleatórias no Brasil
 */
export function generateTestSample(sampleName: string): MapGenerationSample {
  // Coordenadas aleatórias dentro do Brasil
  const lat = -5 + Math.random() * -20; // Entre -5 e -25
  const lon = -35 + Math.random() * -25; // Entre -35 e -60

  return {
    sample_name: sampleName,
    code_lab: `test_${Date.now()}`,
    created_by: "test_user",
    lat: Number(lat.toFixed(4)),
    lon: Number(lon.toFixed(4)),
    d18O_cel: [
      20 + Math.random() * 10, // Entre 20 e 30
      20 + Math.random() * 10,
      20 + Math.random() * 10,
    ],
    species: "Test Species",
    trusted: "untrusted",
    status: "pending",
    created_on: new Date().toISOString(),
  };
}

/**
 * Valida múltiplas samples e retorna estatísticas
 */
export function validateMultipleSamples(samples: unknown[]): {
  valid: number;
  invalid: number;
  errors: string[];
} {
  let valid = 0;
  let invalid = 0;
  const errors: string[] = [];

  samples.forEach((sample, index) => {
    try {
      validateMapGenerationSample(sample);
      valid++;
    } catch (error) {
      invalid++;
      errors.push(`Sample ${index}: ${error.message}`);
    }
  });

  return { valid, invalid, errors };
}

export default {
  // Exemplos
  minimalValidSample,
  enrichedSample,
  specificSampleMessage,
  allMapsMessage,
  brazilCoordinates,

  // Demonstrações
  demonstrateMapGenerationValidation,
  generateTestSample,
  validateMultipleSamples,

  // Validações individuais
  exampleValidateSample,
  exampleValidateMessage,
  exampleValidateCoordinates,
  exampleTypeGuards,
};
