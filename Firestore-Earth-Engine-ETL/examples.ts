// ============================================================================
// FIRESTORE EARTH ENGINE ETL - EXEMPLOS DE USO
// ============================================================================

// Este arquivo contém exemplos de uso dos tipos TypeScript e validações Zod
// para o sistema Firestore-Earth-Engine-ETL

import {
  validateTrustedSample,
  validateUntrustedSample,
  validateETLConfig,
  validateCoordinates,
  hasValidCoordinates,
  isTrustedSample,
  isUntrustedSample,
  isValidOrgName,
  type TrustedSample,
  type UntrustedSample,
  type ETLConfig,
  type Coordinates,
  DefaultETLConfig,
} from "./types";

// ============================================================================
// EXEMPLOS DE TRUSTED SAMPLES VÁLIDAS
// ============================================================================

// Trusted sample mínima válida
const minimalTrustedSample: TrustedSample = {
  // Coordenadas obrigatórias (Mato Grosso, Brasil)
  lat: -13.0845,
  lon: -53.3795,

  // Array de pontos isotópicos (obrigatório)
  points: [
    {
      d18O_cel: 23.5,
      d15N_wood: 2.1,
      d13C_wood: -25.4,
      code: "sample_001",
      species: "Hymenaea courbaril",
    },
  ],

  // Metadados obrigatórios
  created_on: "8-9-2023",
  org_name: "forest-research-org",
};

// Trusted sample completa com múltiplos pontos
const completeTrustedSample: TrustedSample = {
  lat: -15.7942, // Brasília
  lon: -47.8822,

  // Múltiplos pontos isotópicos
  points: [
    {
      d18O_cel: 23.5,
      d15N_wood: 2.1,
      d13C_wood: -25.4,
      code: "sample_001",
      code_lab: "LAB001",
      species: "Hymenaea courbaril",
      date_of_harvest: "15-7-2023",
      vpd: 1.2,
      mean_annual_temperature: 25.5,
      mean_annual_precipitation: 1500.0,
    },
    {
      d18O_cel: 24.1,
      d15N_wood: 2.3,
      d13C_wood: -25.7,
      code: "sample_002",
      code_lab: "LAB001",
      species: "Hymenaea courbaril",
      date_of_harvest: "15-7-2023",
    },
    {
      d18O_cel: 23.8,
      d15N_wood: 2.0,
      d13C_wood: -25.1,
      code: "sample_003",
      code_lab: "LAB001",
      species: "Hymenaea courbaril",
    },
  ],

  created_on: "2023-09-08T10:30:00Z", // ISO format
  org_name: "timber-certification-brazil",

  // Campos adicionais opcionais
  d18o_cel: [23.5, 24.1, 23.8],
  d15n_wood: [2.1, 2.3, 2.0],
  d13c_wood: [-25.4, -25.7, -25.1],
  code: "BATCH_2023_001",
  code_lab: "LAB001_BATCH",
  date_of_harvest: "15-07-2023",
  vpd: 1.2,
  mean_annual_temperature: 25.5,
  mean_annual_precipitation: 1500.0,
};

// ============================================================================
// EXEMPLOS DE UNTRUSTED SAMPLES VÁLIDAS
// ============================================================================

// Untrusted sample mínima válida
const minimalUntrustedSample: UntrustedSample = {
  // Coordenadas obrigatórias
  lat: -13.0845,
  lon: -53.3795,

  // Arrays de medições isotópicas (mínimo 2 cada)
  carbon: [-25.4, -25.7, -25.1],
  nitrogen: [2.1, 2.3, 2.0],
  oxygen: [23.5, 24.1, 23.8],

  // Resultados da validação
  validity: "Not Likely",
  validity_details: {
    p_value_oxygen: 0.001193676470473496,
    p_value_nitrogen: 0.010445452763826784,
    p_value_carbon: 0.00034070435105630674,
    reference_oxygen_isoscape_name: "brazil_isoscape_v1",
    d18O_cel_sample_mean: 23.8,
    d18O_cel_sample_variance: 0.09,
    p_value: 4.248069198730162e-9,
    p_value_threshold: 0.05,
  },

  // Metadados obrigatórios
  created_on: "8-9-2023",
  org_name: "timber-analysis-lab",
};

// Untrusted sample completa
const completeUntrustedSample: UntrustedSample = {
  lat: -3.4653, // Manaus, Amazonas
  lon: -62.2159,

  // Arrays com mais medições
  carbon: [-25.4, -25.7, -25.1, -25.9, -25.2],
  nitrogen: [2.1, 2.3, 2.0, 1.8, 2.4],
  oxygen: [23.5, 24.1, 23.8, 24.3, 23.2],

  validity: "Possible",
  validity_details: {
    p_value_oxygen: 0.15,
    p_value_nitrogen: 0.08,
    p_value_carbon: 0.12,
    reference_oxygen_isoscape_name: "amazon_isoscape_v2",
    reference_oxygen_isoscape_creation_date: "2023-01-15",
    reference_oxygen_isoscape_precision: 0.85,
    reference_oxygen_isoscape_recall: 0.78,
    d18O_cel_sample_mean: 23.78,
    d18O_cel_sample_variance: 0.18,
    d18O_cel_reference_mean: 24.1,
    d18O_cel_reference_variance: 0.25,
    p_value: 0.144,
    p_value_threshold: 0.05,
  },

  created_on: "2023-09-08T14:22:30Z",
  org_name: "amazon-forest-institute",
  date_of_harvest: "20-08-2023",
};

// ============================================================================
// EXEMPLOS DE CONFIGURAÇÃO ETL
// ============================================================================

// Configuração de produção
const productionETLConfig: ETLConfig = {
  gcp_project_id: "river-sky-386919",
  org_ee_path: "projects/river-sky-386919/assets/ee_org",
  trusted_schema: ["lat", "lon", "points", "created_on", "org_name"],
  untrusted_schema: [
    "lat",
    "lon",
    "carbon",
    "nitrogen",
    "oxygen",
    "validity",
    "validity_details",
    "created_on",
    "date_of_harvest",
    "org_name",
  ],
};

// Configuração de desenvolvimento
const developmentETLConfig: ETLConfig = {
  gcp_project_id: "timberid-dev-12345",
  org_ee_path: "projects/timberid-dev-12345/assets/ee_org_dev",
  trusted_schema: [
    "lat",
    "lon",
    "points",
    "created_on",
    "org_name",
    "d18o_cel",
  ],
  untrusted_schema: [
    "lat",
    "lon",
    "carbon",
    "nitrogen",
    "oxygen",
    "validity",
    "validity_details",
    "created_on",
    "org_name",
  ],
};

// ============================================================================
// EXEMPLOS DE COORDENADAS
// ============================================================================

// Coordenadas válidas no Brasil
const validBrazilCoordinates: Coordinates[] = [
  { lat: -15.7942, lon: -47.8822 }, // Brasília
  { lat: -23.5505, lon: -46.6333 }, // São Paulo
  { lat: -22.9068, lon: -43.1729 }, // Rio de Janeiro
  { lat: -3.4653, lon: -62.2159 }, // Manaus
  { lat: -8.0476, lon: -34.877 }, // Recife
];

// ============================================================================
// EXEMPLOS DE VALIDAÇÃO
// ============================================================================

/**
 * Exemplo de validação de trusted sample com tratamento de erros
 */
function exampleValidateTrustedSample() {
  console.log("🌳 VALIDAÇÃO DE TRUSTED SAMPLE");

  try {
    // Validação bem-sucedida
    const validSample = validateTrustedSample(minimalTrustedSample);
    console.log("✅ Trusted sample válida:", validSample.org_name);
    console.log(`📍 Coordenadas: ${validSample.lat}, ${validSample.lon}`);
    console.log(`🔬 Pontos isotópicos: ${validSample.points.length}`);
    return validSample;
  } catch (error) {
    console.error("❌ Erro na validação da trusted sample:", error.message);
    throw error;
  }
}

/**
 * Exemplo de validação de untrusted sample
 */
function exampleValidateUntrustedSample() {
  console.log("\n🧪 VALIDAÇÃO DE UNTRUSTED SAMPLE");

  try {
    const validSample = validateUntrustedSample(completeUntrustedSample);
    console.log("✅ Untrusted sample válida:", validSample.org_name);
    console.log(
      `📊 Medições - C: ${validSample.carbon.length}, N: ${validSample.nitrogen.length}, O: ${validSample.oxygen.length}`
    );
    console.log(`🎯 Validação: ${validSample.validity}`);
    return validSample;
  } catch (error) {
    console.error("❌ Erro na validação da untrusted sample:", error.message);
    throw error;
  }
}

/**
 * Exemplo de validação de configuração ETL
 */
function exampleValidateETLConfig() {
  console.log("\n⚙️ VALIDAÇÃO DE CONFIGURAÇÃO ETL");

  try {
    const validConfig = validateETLConfig(productionETLConfig);
    console.log("✅ Configuração ETL válida:", validConfig.gcp_project_id);
    console.log(`🗂️ Path EE: ${validConfig.org_ee_path}`);
    console.log(
      `📋 Schemas - Trusted: ${validConfig.trusted_schema.length}, Untrusted: ${validConfig.untrusted_schema.length}`
    );
    return validConfig;
  } catch (error) {
    console.error("❌ Erro na validação da configuração:", error.message);
    throw error;
  }
}

/**
 * Exemplo de validação de coordenadas
 */
function exampleValidateCoordinates() {
  console.log("\n🗺️ VALIDAÇÃO DE COORDENADAS");

  validBrazilCoordinates.forEach((coords, index) => {
    try {
      const validCoords = validateCoordinates(coords);
      console.log(
        `✅ Coordenada ${index + 1} válida: ${validCoords.lat}, ${
          validCoords.lon
        }`
      );
    } catch (error) {
      console.error(`❌ Coordenada ${index + 1} inválida:`, error.message);
    }
  });

  // Teste com coordenadas inválidas
  try {
    const invalidCoords = { lat: 95, lon: -200 }; // Inválidas
    validateCoordinates(invalidCoords);
  } catch (error) {
    console.log(
      "✅ Coordenadas inválidas detectadas corretamente:",
      error.message
    );
  }
}

/**
 * Exemplo de uso de type guards
 */
function exampleTypeGuards() {
  console.log("\n🛡️ TYPE GUARDS");

  // Teste de coordenadas válidas
  const testSamples = [minimalTrustedSample, completeUntrustedSample];

  testSamples.forEach((sample, index) => {
    if (hasValidCoordinates(sample)) {
      console.log(`✅ Sample ${index + 1} tem coordenadas válidas`);

      if (isTrustedSample(sample)) {
        console.log(`  🌳 É trusted sample com ${sample.points.length} pontos`);
      } else if (isUntrustedSample(sample)) {
        console.log(
          `  🧪 É untrusted sample com validação: ${sample.validity}`
        );
      }
    }
  });

  // Teste de nomes de organização
  const orgNames = [
    "forest-research-org",
    "INVALID NAME!",
    "timber_lab_01",
    "",
  ];
  orgNames.forEach((name) => {
    const isValid = isValidOrgName(name);
    console.log(
      `${isValid ? "✅" : "❌"} Organização "${name}": ${
        isValid ? "válida" : "inválida"
      }`
    );
  });
}

// ============================================================================
// EXEMPLOS DE SAMPLES INVÁLIDAS (PARA TESTES DE ERRO)
// ============================================================================

// Trusted sample com coordenadas inválidas
const invalidCoordinatesTrusted = {
  ...minimalTrustedSample,
  lat: 95, // Inválido: > 90
  lon: -200, // Inválido: < -180
};

// Trusted sample sem pontos isotópicos
const noPointsTrusted = {
  ...minimalTrustedSample,
  points: [], // Inválido: array vazio
};

// Untrusted sample com medições insuficientes
const insufficientMeasurementsUntrusted = {
  ...minimalUntrustedSample,
  carbon: [-25.4], // Inválido: apenas 1 medição
  nitrogen: [2.1], // Inválido: apenas 1 medição
  oxygen: [23.5], // Inválido: apenas 1 medição
};

// Configuração ETL com projeto inválido
const invalidProjectConfig = {
  ...productionETLConfig,
  gcp_project_id: "INVALID PROJECT!", // Inválido: formato incorreto
};

// ============================================================================
// FUNÇÃO DE DEMONSTRAÇÃO COMPLETA
// ============================================================================

/**
 * Demonstração completa do sistema de validação ETL
 */
export function demonstrateETLValidation() {
  console.log("🔄 DEMONSTRAÇÃO - FIRESTORE EARTH ENGINE ETL");
  console.log("==============================================");

  // 1. Validação de trusted samples
  try {
    exampleValidateTrustedSample();
  } catch (error) {
    console.error("Erro na validação de trusted sample");
  }

  // 2. Validação de untrusted samples
  try {
    exampleValidateUntrustedSample();
  } catch (error) {
    console.error("Erro na validação de untrusted sample");
  }

  // 3. Validação de configuração
  try {
    exampleValidateETLConfig();
  } catch (error) {
    console.error("Erro na validação de configuração");
  }

  // 4. Validação de coordenadas
  exampleValidateCoordinates();

  // 5. Type guards
  exampleTypeGuards();

  // 6. Demonstração de erros
  console.log("\n❌ DEMONSTRAÇÃO DE ERROS:");

  try {
    validateTrustedSample(invalidCoordinatesTrusted);
  } catch (error) {
    console.log(
      "✅ Coordenadas inválidas capturadas:",
      error.message.substring(0, 80) + "..."
    );
  }

  try {
    validateTrustedSample(noPointsTrusted);
  } catch (error) {
    console.log(
      "✅ Array vazio de pontos capturado:",
      error.message.substring(0, 80) + "..."
    );
  }

  try {
    validateUntrustedSample(insufficientMeasurementsUntrusted);
  } catch (error) {
    console.log(
      "✅ Medições insuficientes capturadas:",
      error.message.substring(0, 80) + "..."
    );
  }

  try {
    validateETLConfig(invalidProjectConfig);
  } catch (error) {
    console.log(
      "✅ Projeto GCP inválido capturado:",
      error.message.substring(0, 80) + "..."
    );
  }

  console.log("\n✅ Demonstração completa finalizada!");
}

// ============================================================================
// UTILITÁRIOS PARA DESENVOLVIMENTO
// ============================================================================

/**
 * Gera trusted sample de teste com coordenadas aleatórias no Brasil
 */
export function generateTestTrustedSample(orgName: string): TrustedSample {
  // Coordenadas aleatórias dentro do Brasil
  const lat = -5 + Math.random() * -20; // Entre -5 e -25
  const lon = -35 + Math.random() * -25; // Entre -35 e -60

  return {
    lat: Number(lat.toFixed(4)),
    lon: Number(lon.toFixed(4)),
    points: [
      {
        d18O_cel: 20 + Math.random() * 10,
        d15N_wood: Math.random() * 5,
        d13C_wood: -30 + Math.random() * 10,
        code: `test_${Date.now()}`,
        species: "Test Species",
      },
    ],
    created_on: new Date().toISOString(),
    org_name: orgName.toLowerCase().replace(/\s+/g, "-"),
  };
}

/**
 * Gera untrusted sample de teste
 */
export function generateTestUntrustedSample(orgName: string): UntrustedSample {
  const lat = -5 + Math.random() * -20;
  const lon = -35 + Math.random() * -25;

  return {
    lat: Number(lat.toFixed(4)),
    lon: Number(lon.toFixed(4)),
    carbon: Array.from({ length: 3 }, () => -30 + Math.random() * 10),
    nitrogen: Array.from({ length: 3 }, () => Math.random() * 5),
    oxygen: Array.from({ length: 3 }, () => 20 + Math.random() * 10),
    validity: Math.random() > 0.5 ? "Possible" : "Not Likely",
    validity_details: {
      p_value_oxygen: Math.random(),
      p_value_carbon: Math.random(),
      p_value_nitrogen: Math.random(),
      p_value: Math.random(),
      p_value_threshold: 0.05,
    },
    created_on: new Date().toISOString(),
    org_name: orgName.toLowerCase().replace(/\s+/g, "-"),
  };
}

/**
 * Valida múltiplas samples e retorna estatísticas
 */
export function validateMultipleSamples(
  trustedSamples: unknown[],
  untrustedSamples: unknown[]
): {
  trusted: { valid: number; invalid: number; errors: string[] };
  untrusted: { valid: number; invalid: number; errors: string[] };
} {
  const trustedStats = { valid: 0, invalid: 0, errors: [] as string[] };
  const untrustedStats = { valid: 0, invalid: 0, errors: [] as string[] };

  // Validar trusted samples
  trustedSamples.forEach((sample, index) => {
    try {
      validateTrustedSample(sample);
      trustedStats.valid++;
    } catch (error) {
      trustedStats.invalid++;
      trustedStats.errors.push(`Trusted ${index}: ${error.message}`);
    }
  });

  // Validar untrusted samples
  untrustedSamples.forEach((sample, index) => {
    try {
      validateUntrustedSample(sample);
      untrustedStats.valid++;
    } catch (error) {
      untrustedStats.invalid++;
      untrustedStats.errors.push(`Untrusted ${index}: ${error.message}`);
    }
  });

  return { trusted: trustedStats, untrusted: untrustedStats };
}

export default {
  // Exemplos
  minimalTrustedSample,
  completeTrustedSample,
  minimalUntrustedSample,
  completeUntrustedSample,
  productionETLConfig,
  validBrazilCoordinates,

  // Demonstrações
  demonstrateETLValidation,
  generateTestTrustedSample,
  generateTestUntrustedSample,
  validateMultipleSamples,

  // Validações individuais
  exampleValidateTrustedSample,
  exampleValidateUntrustedSample,
  exampleValidateETLConfig,
  exampleValidateCoordinates,
  exampleTypeGuards,
};
