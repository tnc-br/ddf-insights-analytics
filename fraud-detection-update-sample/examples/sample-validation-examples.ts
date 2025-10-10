import {
  validateInputSample,
  validateSample,
} from "../validation/sample-validation";
import { InputSample, ProcessedSample } from "../types/sample";

/**
 * Exemplos de uso das validações de amostra
 */

// Exemplo de amostra de entrada válida
const validInputSample: InputSample = {
  lat: -13.0845,
  lon: -53.31466,
  sample_name: "test sample validity",
  created_on: "8-9-2023",
  species: "Hymenaea courbaril",
  site: "Test site",
  municipality: "Vilhena",
  trusted: "untrusted",
  status: "concluded",
  visibility: "public",
  created_by_name: "Josh Wolkoff",
  last_updated_by: "Josh Wolkoff",
  collected_by: "supplier",
  org_name: "t1QbuSDmOrvG1Khp9Vf2",
  code_lab: "fd1239d5488215a23440",
  d18O_cel: [22, 23, 24],
  d15N_cel: [-21, -29, -18],
  d13C_cel: [16, 14, 18],
  oxygen: [22, 23, 24],
  nitrogen: [-21, -29, -18],
  carbon: [16, 14, 18],
  n_wood: [12],
  c_wood: [12],
  c_cel: [12],
  amount_of_measurementste: "3",
};

// Exemplo de amostra processada completa
const validProcessedSample: ProcessedSample = {
  ...validInputSample,
  validity: "Possible",
  validity_details: {
    p_value_oxygen: 0.001193676470473496,
    p_value_carbon: 0.00034070435105630674,
    p_value_nitrogen: 0.010445452763826784,
    reference_oxygen_isoscape_name: "isoscape_v1",
    reference_oxygen_isoscape_creation_date: "2023-01-01",
    reference_oxygen_isoscape_precision: 0.85,
    reference_oxygen_isoscape_recall: 0.92,
    d18O_cel_sample_mean: 23,
    d18O_cel_sample_variance: 1.0,
    d18O_cel_reference_mean: 22.5,
    d18O_cel_reference_variance: 0.8,
    p_value: 4.248069198730162e-9,
    p_value_threshold: 0.05,
  },
  water_pct: {
    is_point_water: false,
    water_mean_in_10km_buffer: 0.0070068910493711264,
    water_mean_in_1km_buffer: 0,
  },
  land_use_anthropic_pct: {
    "2011": 0.45034623326325146,
    "2012": 0.44770272211177214,
    "2013": 0.4482117137641799,
    "2014": 0.45126455395621806,
    "2015": 0.45269307757612276,
    "2016": 0.4553281223992332,
    "2017": 0.4587216170736057,
    "2018": 0.4577154170252487,
    "2019": 0.4601431958992026,
    "2020": 0.46499305682441266,
    "2021": 0.46557667144547044,
  },
  land_use_primary_vegetation_pct: {
    "2011": 0.513664660491817,
    "2012": 0.5131409022482503,
    "2013": 0.5112154156350521,
    "2014": 0.5082717039773982,
    "2015": 0.5068101180838858,
    "2016": 0.504526055874371,
    "2017": 0.5002018637214489,
    "2018": 0.49918598734293695,
    "2019": 0.49446174335376347,
    "2020": 0.49335021902953274,
    "2021": 0.49279482181843925,
  },
  land_use_secondary_vegetation_or_regrowth_pct: {
    "2011": 0.03598910624493149,
    "2012": 0.03915637563997758,
    "2013": 0.04057287060076802,
    "2014": 0.04046374206638375,
    "2015": 0.04049680433999142,
    "2016": 0.040145821726395824,
    "2017": 0.0410765192049453,
    "2018": 0.04309859563181422,
    "2019": 0.045395060747033804,
    "2020": 0.041656724146054556,
    "2021": 0.04162850673609025,
  },
  alerts: [
    {
      alertCode: "11368",
      areaHa: 235.6794,
      detectedAt: "15/05/2019",
      alertInsertedAt: "10/02/2020 21:00",
      coordinates: {
        latitude: -13.025003713251833,
        longitude: -53.314664066568064,
      },
      url: "https://plataforma.alerta.mapbiomas.org/laudo/11368",
      distance_to_point: 9.632019033764433,
      before: {
        url: "https://storage.googleapis.com/alerta-public/IMAGES/11368/before_deforestation.png",
        satellite: "Sentinel-2",
      },
      after: {
        url: "https://storage.googleapis.com/alerta-public/IMAGES/11368/after_deforestation.png",
        satellite: "Sentinel-2",
      },
    },
  ],
};

// Exemplos de validação
console.log("=== Validação de Amostra de Entrada ===");
const inputResult = validateInputSample(validInputSample);
if (inputResult.success) {
  console.log("✅ Amostra de entrada válida");
  console.log("Coordenadas:", {
    lat: inputResult.data.lat,
    lon: inputResult.data.lon,
  });
  console.log("Medições disponíveis:", {
    oxygen: inputResult.data.d18O_cel?.length || 0,
    nitrogen: inputResult.data.d15N_cel?.length || 0,
    carbon: inputResult.data.d13C_cel?.length || 0,
  });
} else {
  console.error("❌ Erros de validação:", inputResult.error.issues);
}

console.log("\n=== Validação de Amostra Processada ===");
const processedResult = validateSample(validProcessedSample);
if (processedResult.success) {
  console.log("✅ Amostra processada válida");
  console.log("Resultado de validação:", processedResult.data.validity);
  console.log("Número de alertas:", processedResult.data.alerts?.length || 0);
} else {
  console.error("❌ Erros de validação:", processedResult.error.issues);
}

// Exemplos de validação com dados inválidos
console.log("\n=== Exemplos de Dados Inválidos ===");

// Latitude inválida
const invalidLatSample = { ...validInputSample, lat: 100 };
const latResult = validateInputSample(invalidLatSample);
if (!latResult.success) {
  console.log("❌ Latitude inválida:", latResult.error.issues[0].message);
}

// Medições insuficientes
const insufficientMeasurements = {
  ...validInputSample,
  d18O_cel: [22], // Apenas 1 medição
  d15N_cel: undefined,
  d13C_cel: undefined,
};
const measurementResult = validateInputSample(insufficientMeasurements);
if (!measurementResult.success) {
  console.log(
    "❌ Medições insuficientes:",
    measurementResult.error.issues[0].message
  );
}

// Data em formato inválido
const invalidDateSample = { ...validInputSample, created_on: "2023-09-08" }; // Formato incorreto
const dateResult = validateInputSample(invalidDateSample);
if (!dateResult.success) {
  console.log(
    "❌ Formato de data inválido:",
    dateResult.error.issues[0].message
  );
}

// Status inválido
const invalidStatusSample = {
  ...validInputSample,
  status: "invalid_status" as any,
};
const statusResult = validateInputSample(invalidStatusSample);
if (!statusResult.success) {
  console.log("❌ Status inválido:", statusResult.error.issues[0].message);
}

export { validInputSample, validProcessedSample };
