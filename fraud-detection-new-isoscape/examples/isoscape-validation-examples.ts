import {
  validateIsoscapeAsset,
  validateUpdateRequest,
  validateUpdateResponse,
  validateUntrustedSample,
  validateBatchOperation,
  validateMonitoringConfig,
} from "../validation/isoscape-validation";
import {
  IsoscapeAsset,
  IsoscapeUpdateRequest,
  IsoscapeUpdateResponse,
  UntrustedSample,
  BatchReprocessingOperation,
} from "../types/isoscape";

/**
 * Exemplos de uso das validações de isoscape
 * Para o sistema fraud-detection-new-isoscape
 */

// Exemplo de isoscape asset válido
const validIsoscapeAsset: IsoscapeAsset = {
  name: "projects/timber-project/assets/isoscapes/d18O_v2",
  type: "IMAGE",
  isoscape_type: "d18O",
  version: "v2.1",
  updateTime: "2023-09-19T10:30:00.000Z",
  creation_date: "2023-09-15T08:00:00.000Z",
  precision: 0.85,
  recall: 0.92,
  spatial_resolution: 1000, // 1km resolution
  geographic_extent: {
    north: 10.0,
    south: -35.0,
    east: -30.0,
    west: -75.0,
    projection: "EPSG:4326",
  },
  source_data: "Global precipitation isotope database",
  processing_method: "Kriging interpolation with elevation co-variates",
  bands: [
    {
      id: "b1",
      dataType: {
        type: "DOUBLE",
        precision: "double",
      },
      crs: "EPSG:4326",
    },
  ],
};

// Exemplo de request de verificação de atualizações
const validUpdateRequest: IsoscapeUpdateRequest = {
  project_id: "timber-project",
  isoscape_path: "projects/timber-project/assets/isoscapes",
  check_window_hours: 27,
  force_update: false,
};

// Exemplo de response de verificação de atualizações
const validUpdateResponse: IsoscapeUpdateResponse = {
  success: true,
  updates_found: true,
  check_timestamp: "2023-09-19T10:30:00.000Z",
  check_window_hours: 27,
  updated_assets: [
    {
      asset_name: "projects/timber-project/assets/isoscapes/d18O_v2",
      asset_id: "d18O_v2_123456",
      isoscape_type: "d18O",
      update_time: "2023-09-19T08:15:00.000Z",
      version: "v2.1",
      changes: "Improved spatial resolution and updated calibration data",
    },
  ],
  samples_reprocessed: 1250,
  total_samples: 1250,
  processing_time_ms: 45000,
};

// Exemplo de amostra não confiável
const validUntrustedSample: UntrustedSample = {
  id: "sample-123456",
  sample_name: "Amazon Basin Sample #42",
  lat: -8.5,
  lon: -55.2,
  d18O_cel: [22.5, 23.1, 22.8, 23.3],
  d15N_cel: [-12.5, -11.8, -12.1],
  d13C_cel: [-28.2, -27.9, -28.5, -28.1],
  status: "pending",
  created_at: "2023-09-18T14:30:00.000Z",
  org: "research-institute",
  created_by: "researcher@institute.org",
};

// Exemplo de operação de reprocessamento em lote
const validBatchOperation: BatchReprocessingOperation = {
  operation_id: "batch-20230919-103000",
  trigger_reason: "isoscape_update",
  start_time: "2023-09-19T10:30:00.000Z",
  status: "running",
  samples_to_process: 1250,
  samples_processed: 850,
  samples_failed: 5,
  updated_isoscapes: [
    {
      asset_name: "projects/timber-project/assets/isoscapes/d18O_v2",
      asset_id: "d18O_v2_123456",
      isoscape_type: "d18O",
      update_time: "2023-09-19T08:15:00.000Z",
      version: "v2.1",
    },
  ],
};

console.log("=== Validação de Isoscape Asset ===");
const assetResult = validateIsoscapeAsset(validIsoscapeAsset);
if (assetResult.success) {
  console.log("✅ Isoscape asset válido");
  console.log("Tipo:", assetResult.data.isoscape_type);
  console.log("Versão:", assetResult.data.version);
  console.log("Precisão:", assetResult.data.precision);
  console.log(
    "Resolução espacial:",
    assetResult.data.spatial_resolution,
    "metros"
  );
} else {
  console.error("❌ Erros de validação:", assetResult.error.issues);
}

console.log("\n=== Validação de Request de Atualização ===");
const requestResult = validateUpdateRequest(validUpdateRequest);
if (requestResult.success) {
  console.log("✅ Request de atualização válido");
  console.log("Projeto:", requestResult.data.project_id);
  console.log(
    "Janela de verificação:",
    requestResult.data.check_window_hours,
    "horas"
  );
  console.log("Forçar atualização:", requestResult.data.force_update);
} else {
  console.error("❌ Erros de validação:", requestResult.error.issues);
}

console.log("\n=== Validação de Response de Atualização ===");
const responseResult = validateUpdateResponse(validUpdateResponse);
if (responseResult.success) {
  console.log("✅ Response de atualização válido");
  console.log("Atualizações encontradas:", responseResult.data.updates_found);
  console.log("Assets atualizados:", responseResult.data.updated_assets.length);
  console.log(
    "Amostras reprocessadas:",
    responseResult.data.samples_reprocessed
  );
  console.log(
    "Tempo de processamento:",
    responseResult.data.processing_time_ms,
    "ms"
  );
} else {
  console.error("❌ Erros de validação:", responseResult.error.issues);
}

console.log("\n=== Validação de Amostra Não Confiável ===");
const sampleResult = validateUntrustedSample(validUntrustedSample);
if (sampleResult.success) {
  console.log("✅ Amostra não confiável válida");
  console.log("Coordenadas:", {
    lat: sampleResult.data.lat,
    lon: sampleResult.data.lon,
  });
  console.log("Medições disponíveis:", {
    oxygen: sampleResult.data.d18O_cel?.length || 0,
    nitrogen: sampleResult.data.d15N_cel?.length || 0,
    carbon: sampleResult.data.d13C_cel?.length || 0,
  });
} else {
  console.error("❌ Erros de validação:", sampleResult.error.issues);
}

console.log("\n=== Validação de Operação em Lote ===");
const batchResult = validateBatchOperation(validBatchOperation);
if (batchResult.success) {
  console.log("✅ Operação em lote válida");
  console.log("Status:", batchResult.data.status);
  console.log(
    "Progresso:",
    `${batchResult.data.samples_processed}/${batchResult.data.samples_to_process}`
  );
  console.log("Falhas:", batchResult.data.samples_failed);
  console.log("Trigger:", batchResult.data.trigger_reason);
} else {
  console.error("❌ Erros de validação:", batchResult.error.issues);
}

// Exemplos de validação com dados inválidos
console.log("\n=== Exemplos de Dados Inválidos ===");

// Asset com tipo inválido
const invalidTypeAsset = {
  ...validIsoscapeAsset,
  type: "TABLE" as any, // Isoscapes devem ser IMAGE
};
const typeResult = validateIsoscapeAsset(invalidTypeAsset);
if (!typeResult.success) {
  console.log("❌ Tipo de asset inválido:", typeResult.error.issues[0].message);
}

// Request com projeto inválido
const invalidProjectRequest = {
  ...validUpdateRequest,
  project_id: "Invalid_Project-123!", // Formato inválido de project ID
};
const projectResult = validateUpdateRequest(invalidProjectRequest);
if (!projectResult.success) {
  console.log("❌ Project ID inválido:", projectResult.error.issues[0].message);
}

// Janela de tempo inválida
const invalidTimeRequest = {
  ...validUpdateRequest,
  check_window_hours: 200, // Mais de 168 horas (1 semana)
};
const timeResult = validateUpdateRequest(invalidTimeRequest);
if (!timeResult.success) {
  console.log(
    "❌ Janela de tempo inválida:",
    timeResult.error.issues[0].message
  );
}

// Coordenadas inválidas
const invalidCoordsSample = {
  ...validUntrustedSample,
  lat: 95, // Latitude inválida (> 90)
};
const coordsResult = validateUntrustedSample(invalidCoordsSample);
if (!coordsResult.success) {
  console.log(
    "❌ Coordenadas inválidas:",
    coordsResult.error.issues[0].message
  );
}

// Amostra sem medições suficientes
const insufficientSample = {
  ...validUntrustedSample,
  d18O_cel: [22.5], // Apenas 1 medição
  d15N_cel: undefined,
  d13C_cel: undefined,
};
const measurementResult = validateUntrustedSample(insufficientSample);
if (!measurementResult.success) {
  console.log(
    "❌ Medições insuficientes:",
    measurementResult.error.issues[0].message
  );
}

// Extensão geográfica inválida
const invalidExtentAsset = {
  ...validIsoscapeAsset,
  geographic_extent: {
    north: -10.0, // Norte menor que sul
    south: 10.0,
    east: -30.0,
    west: -75.0,
  },
};
const extentResult = validateIsoscapeAsset(invalidExtentAsset);
if (!extentResult.success) {
  console.log(
    "❌ Extensão geográfica inválida:",
    extentResult.error.issues[0].message
  );
}

// Versão em formato inválido
const invalidVersionAsset = {
  ...validIsoscapeAsset,
  version: "version-2.1", // Deve ser vX.X
};
const versionResult = validateIsoscapeAsset(invalidVersionAsset);
if (!versionResult.success) {
  console.log(
    "❌ Formato de versão inválido:",
    versionResult.error.issues[0].message
  );
}

// Timestamp em formato inválido
const invalidTimestampAsset = {
  ...validIsoscapeAsset,
  updateTime: "2023-09-19 10:30:00", // Formato não ISO 8601
};
const timestampResult = validateIsoscapeAsset(invalidTimestampAsset);
if (!timestampResult.success) {
  console.log(
    "❌ Timestamp inválido:",
    timestampResult.error.issues[0].message
  );
}

export {
  validIsoscapeAsset,
  validUpdateRequest,
  validUpdateResponse,
  validUntrustedSample,
  validBatchOperation,
};
