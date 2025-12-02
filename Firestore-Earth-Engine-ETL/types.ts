import { z } from "zod";

// ============================================================================
// FIRESTORE EARTH ENGINE ETL - TYPESCRIPT TYPES & ZOD VALIDATION
// ============================================================================

// ============================================================================
// SHARED TYPES
// ============================================================================

// Coordenadas geográficas com validação rigorosa
export interface Coordinates {
  lat: number; // Latitude: -90 a 90
  lon: number; // Longitude: -180 a 180
}

// Dados isotópicos individuais para trusted samples
export interface IsotopicPoint {
  d18O_cel?: number; // Oxigênio-18 na celulose
  d15N_wood?: number; // Nitrogênio-15 na madeira
  d13C_wood?: number; // Carbono-13 na madeira
  code?: string; // Código da medição
  code_lab?: string; // Código do laboratório
  date_of_harvest?: string; // Data da colheita
  vpd?: number; // Vapor Pressure Deficit
  mean_annual_temperature?: number; // Temperatura média anual
  mean_annual_precipitation?: number; // Precipitação média anual
  species?: string; // Espécie da madeira
  [key: string]: any; // Outros campos dinâmicos
}

// Detalhes de validação isotópica
export interface ValidityDetails {
  p_value_oxygen?: number;
  p_value_carbon?: number;
  p_value_nitrogen?: number;
  reference_oxygen_isoscape_name?: string;
  reference_oxygen_isoscape_creation_date?: string;
  reference_oxygen_isoscape_precision?: number;
  reference_oxygen_isoscape_recall?: number;
  d18O_cel_sample_mean?: number;
  d18O_cel_sample_variance?: number;
  d18O_cel_reference_mean?: number;
  d18O_cel_reference_variance?: number;
  p_value?: number;
  p_value_threshold?: number;
}

// ============================================================================
// TRUSTED SAMPLES - ESTRUTURA PARA AMOSTRAS CONFIÁVEIS
// ============================================================================

export interface TrustedSample {
  // Coordenadas obrigatórias
  lat: number; // Latitude (-90 a 90)
  lon: number; // Longitude (-180 a 180)

  // Array de pontos isotópicos (múltiplas medições por amostra)
  points: IsotopicPoint[]; // Array de medições isotópicas

  // Metadados obrigatórios
  created_on: string; // Data de criação
  org_name: string; // Nome da organização

  // Campos adicionais opcionais (comentados no schema original)
  d18o_cel?: number[]; // Oxigênio-18 celulose
  d15n_wood?: number[]; // Nitrogênio-15 madeira
  d13c_wood?: number[]; // Carbono-13 madeira
  code?: string; // Código da amostra
  code_lab?: string; // Código do laboratório
  date_of_harvest?: string; // Data da colheita
  vpd?: number; // Vapor Pressure Deficit
  mean_annual_temperature?: number; // Temperatura média anual
  mean_annual_precipitation?: number; // Precipitação média anual
}

// ============================================================================
// UNTRUSTED SAMPLES - ESTRUTURA PARA AMOSTRAS EM VALIDAÇÃO
// ============================================================================

export interface UntrustedSample {
  // Coordenadas obrigatórias
  lat: number; // Latitude (-90 a 90)
  lon: number; // Longitude (-180 a 180)

  // Dados isotópicos para análise (arrays de medições)
  carbon: number[]; // Medições de carbono-13
  nitrogen: number[]; // Medições de nitrogênio-15
  oxygen: number[]; // Medições de oxigênio-18

  // Resultados da validação
  validity: "Possible" | "Not Likely" | string; // Status de validação
  validity_details: ValidityDetails; // Detalhes da análise

  // Metadados obrigatórios
  created_on: string; // Data de criação
  org_name: string; // Nome da organização

  // Dados adicionais
  date_of_harvest?: string; // Data da colheita
}

// ============================================================================
// ETL CONFIGURATION
// ============================================================================

export interface ETLConfig {
  gcp_project_id: string; // ID do projeto GCP
  org_ee_path: string; // Path base no Earth Engine
  trusted_schema: string[]; // Schema para trusted samples
  untrusted_schema: string[]; // Schema para untrusted samples
}

// Resultado do processamento ETL
export interface ETLResult {
  status: "success" | "error";
  trusted_samples_processed: number;
  untrusted_samples_processed: number;
  trusted_samples_skipped: number;
  untrusted_samples_skipped: number;
  organizations: string[];
  errors: string[];
  processing_time_ms: number;
}

// Earth Engine Feature para export
export interface EarthEngineFeature {
  geometry: {
    type: "Point";
    coordinates: [number, number]; // [longitude, latitude]
  };
  properties: Record<string, string>; // Todas as propriedades como string
  system_time_start: string; // Timestamp ISO
}

// ============================================================================
// ZOD VALIDATION SCHEMAS
// ============================================================================

// Schema para coordenadas geográficas
export const CoordinatesSchema = z.object({
  lat: z
    .number()
    .min(-90, "Latitude deve estar entre -90 e 90")
    .max(90, "Latitude deve estar entre -90 e 90"),
  lon: z
    .number()
    .min(-180, "Longitude deve estar entre -180 e 180")
    .max(180, "Longitude deve estar entre -180 e 180"),
});

// Schema para ponto isotópico individual
export const IsotopicPointSchema = z
  .object({
    d18O_cel: z.number().optional(),
    d15N_wood: z.number().optional(),
    d13C_wood: z.number().optional(),
    code: z.string().optional(),
    code_lab: z.string().optional(),
    date_of_harvest: z.string().optional(),
    vpd: z.number().nonnegative("VPD deve ser não negativo").optional(),
    mean_annual_temperature: z.number().optional(),
    mean_annual_precipitation: z
      .number()
      .nonnegative("Precipitação deve ser não negativa")
      .optional(),
    species: z.string().optional(),
  })
  .catchall(z.any()); // Permite campos adicionais

// Schema para detalhes de validação
export const ValidityDetailsSchema = z.object({
  p_value_oxygen: z
    .number()
    .min(0, "P-value deve ser >= 0")
    .max(1, "P-value deve ser <= 1")
    .optional(),
  p_value_carbon: z
    .number()
    .min(0, "P-value deve ser >= 0")
    .max(1, "P-value deve ser <= 1")
    .optional(),
  p_value_nitrogen: z
    .number()
    .min(0, "P-value deve ser >= 0")
    .max(1, "P-value deve ser <= 1")
    .optional(),
  reference_oxygen_isoscape_name: z.string().optional(),
  reference_oxygen_isoscape_creation_date: z.string().optional(),
  reference_oxygen_isoscape_precision: z.number().min(0).max(1).optional(),
  reference_oxygen_isoscape_recall: z.number().min(0).max(1).optional(),
  d18O_cel_sample_mean: z.number().optional(),
  d18O_cel_sample_variance: z
    .number()
    .nonnegative("Variância deve ser não negativa")
    .optional(),
  d18O_cel_reference_mean: z.number().optional(),
  d18O_cel_reference_variance: z
    .number()
    .nonnegative("Variância deve ser não negativa")
    .optional(),
  p_value: z.number().min(0).max(1).optional(),
  p_value_threshold: z.number().min(0).max(1).optional(),
});

// Schema para nome de organização
const OrgNameSchema = z
  .string()
  .min(1, "Nome da organização é obrigatório")
  .regex(
    /^[a-z0-9-_]+$/,
    "Nome da organização deve conter apenas letras minúsculas, números, hífens e underscores"
  )
  .transform((name) => name.toLowerCase()); // Sempre minúsculo

// Schema para data de criação
const CreatedOnSchema = z
  .string()
  .min(1, "Data de criação é obrigatória")
  .refine((date) => {
    // Aceita vários formatos de data
    const patterns = [
      /^\d{1,2}-\d{1,2}-\d{4}$/, // d-m-yyyy
      /^\d{4}-\d{2}-\d{2}$/, // yyyy-mm-dd
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/, // ISO format
    ];
    return patterns.some((pattern) => pattern.test(date));
  }, "Formato de data inválido. Use: dd-mm-yyyy, yyyy-mm-dd ou ISO format");

// ============================================================================
// TRUSTED SAMPLES SCHEMA
// ============================================================================

export const TrustedSampleSchema = z.object({
  // Coordenadas obrigatórias
  lat: z
    .number()
    .min(-90, "Latitude deve estar entre -90 e 90")
    .max(90, "Latitude deve estar entre -90 e 90"),
  lon: z
    .number()
    .min(-180, "Longitude deve estar entre -180 e 180")
    .max(180, "Longitude deve estar entre -180 e 180"),

  // Array de pontos isotópicos (obrigatório, mínimo 1)
  points: z
    .array(IsotopicPointSchema)
    .min(1, "Pelo menos um ponto isotópico é obrigatório")
    .max(100, "Máximo de 100 pontos isotópicos permitidos"),

  // Metadados obrigatórios
  created_on: CreatedOnSchema,
  org_name: OrgNameSchema,

  // Campos opcionais comentados no schema original
  d18o_cel: z.array(z.number()).optional(),
  d15n_wood: z.array(z.number()).optional(),
  d13c_wood: z.array(z.number()).optional(),
  code: z.string().optional(),
  code_lab: z.string().optional(),
  date_of_harvest: z.string().optional(),
  vpd: z.number().nonnegative("VPD deve ser não negativo").optional(),
  mean_annual_temperature: z.number().optional(),
  mean_annual_precipitation: z
    .number()
    .nonnegative("Precipitação deve ser não negativa")
    .optional(),
});

// ============================================================================
// UNTRUSTED SAMPLES SCHEMA
// ============================================================================

export const UntrustedSampleSchema = z.object({
  // Coordenadas obrigatórias
  lat: z
    .number()
    .min(-90, "Latitude deve estar entre -90 e 90")
    .max(90, "Latitude deve estar entre -90 e 90"),
  lon: z
    .number()
    .min(-180, "Longitude deve estar entre -180 e 180")
    .max(180, "Longitude deve estar entre -180 e 180"),

  // Dados isotópicos obrigatórios (arrays de medições)
  carbon: z
    .array(z.number())
    .min(2, "Mínimo de 2 medições de carbono necessárias")
    .max(50, "Máximo de 50 medições de carbono permitidas"),
  nitrogen: z
    .array(z.number())
    .min(2, "Mínimo de 2 medições de nitrogênio necessárias")
    .max(50, "Máximo de 50 medições de nitrogênio permitidas"),
  oxygen: z
    .array(z.number())
    .min(2, "Mínimo de 2 medições de oxigênio necessárias")
    .max(50, "Máximo de 50 medições de oxigênio permitidas"),

  // Resultados da validação
  validity: z.union([
    z.literal("Possible"),
    z.literal("Not Likely"),
    z.string(),
  ]),
  validity_details: ValidityDetailsSchema,

  // Metadados obrigatórios
  created_on: CreatedOnSchema,
  org_name: OrgNameSchema,

  // Dados opcionais
  date_of_harvest: z.string().optional(),
});

// ============================================================================
// ETL CONFIGURATION SCHEMA
// ============================================================================

export const ETLConfigSchema = z.object({
  gcp_project_id: z
    .string()
    .min(1, "ID do projeto GCP é obrigatório")
    .regex(
      /^[a-z][a-z0-9-]*[a-z0-9]$/,
      "ID do projeto deve seguir formato GCP válido"
    ),
  org_ee_path: z
    .string()
    .min(1, "Path do Earth Engine é obrigatório")
    .startsWith("projects/", 'Path deve começar com "projects/"'),
  trusted_schema: z
    .array(z.string())
    .min(1, "Schema de trusted samples deve ter pelo menos um campo"),
  untrusted_schema: z
    .array(z.string())
    .min(1, "Schema de untrusted samples deve ter pelo menos um campo"),
});

// Schema para resultado do ETL
export const ETLResultSchema = z.object({
  status: z.enum(["success", "error"]),
  trusted_samples_processed: z.number().nonnegative("Não pode ser negativo"),
  untrusted_samples_processed: z.number().nonnegative("Não pode ser negativo"),
  trusted_samples_skipped: z.number().nonnegative("Não pode ser negativo"),
  untrusted_samples_skipped: z.number().nonnegative("Não pode ser negativo"),
  organizations: z.array(z.string()),
  errors: z.array(z.string()),
  processing_time_ms: z
    .number()
    .nonnegative("Tempo de processamento deve ser não negativo"),
});

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

/**
 * Valida uma trusted sample para processamento ETL
 */
export function validateTrustedSample(data: unknown): TrustedSample {
  const result = TrustedSampleSchema.safeParse(data);

  if (!result.success) {
    const errors = result.error.errors
      .map((err) => `${err.path.join(".")}: ${err.message}`)
      .join(", ");
    throw new Error(`Validação de trusted sample falhou: ${errors}`);
  }

  return result.data;
}

/**
 * Valida uma untrusted sample para processamento ETL
 */
export function validateUntrustedSample(data: unknown): UntrustedSample {
  const result = UntrustedSampleSchema.safeParse(data);

  if (!result.success) {
    const errors = result.error.errors
      .map((err) => `${err.path.join(".")}: ${err.message}`)
      .join(", ");
    throw new Error(`Validação de untrusted sample falhou: ${errors}`);
  }

  return result.data;
}

/**
 * Valida configuração do ETL
 */
export function validateETLConfig(data: unknown): ETLConfig {
  const result = ETLConfigSchema.safeParse(data);

  if (!result.success) {
    const errors = result.error.errors
      .map((err) => `${err.path.join(".")}: ${err.message}`)
      .join(", ");
    throw new Error(`Validação de configuração ETL falhou: ${errors}`);
  }

  return result.data;
}

/**
 * Valida coordenadas geográficas
 */
export function validateCoordinates(data: unknown): Coordinates {
  const result = CoordinatesSchema.safeParse(data);

  if (!result.success) {
    const errors = result.error.errors
      .map((err) => `${err.path.join(".")}: ${err.message}`)
      .join(", ");
    throw new Error(`Validação de coordenadas falhou: ${errors}`);
  }

  return result.data;
}

/**
 * Valida resultado do ETL
 */
export function validateETLResult(data: unknown): ETLResult {
  const result = ETLResultSchema.safeParse(data);

  if (!result.success) {
    const errors = result.error.errors
      .map((err) => `${err.path.join(".")}: ${err.message}`)
      .join(", ");
    throw new Error(`Validação de resultado ETL falhou: ${errors}`);
  }

  return result.data;
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Verifica se uma sample tem coordenadas válidas para processamento ETL
 */
export function hasValidCoordinates(
  sample: Partial<TrustedSample | UntrustedSample>
): sample is (TrustedSample | UntrustedSample) & Coordinates {
  return (
    typeof sample.lat === "number" &&
    typeof sample.lon === "number" &&
    sample.lat >= -90 &&
    sample.lat <= 90 &&
    sample.lon >= -180 &&
    sample.lon <= 180
  );
}

/**
 * Verifica se é uma trusted sample
 */
export function isTrustedSample(
  sample: TrustedSample | UntrustedSample
): sample is TrustedSample {
  return "points" in sample && Array.isArray((sample as TrustedSample).points);
}

/**
 * Verifica se é uma untrusted sample
 */
export function isUntrustedSample(
  sample: TrustedSample | UntrustedSample
): sample is UntrustedSample {
  return "carbon" in sample && "nitrogen" in sample && "oxygen" in sample;
}

/**
 * Verifica se uma organização tem nome válido
 */
export function isValidOrgName(orgName: string): boolean {
  return (
    /^[a-z0-9-_]+$/.test(orgName.toLowerCase()) && orgName.trim().length > 0
  );
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

// Sample mínima para ETL (apenas coordenadas)
export type MinimalETLSample = Pick<TrustedSample, "lat" | "lon">;

// Sample com organização válida
export type OrganizationalSample = {
  org_name: string;
  lat: number;
  lon: number;
};

// Configuração padrão do ETL
export const DefaultETLConfig: ETLConfig = {
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

// Mapeamento de tipos de sample para schemas
export const SampleSchemas = {
  trusted: TrustedSampleSchema,
  untrusted: UntrustedSampleSchema,
} as const;

// ============================================================================
// EARTH ENGINE INTEGRATION TYPES
// ============================================================================

// Asset path para organizações
export interface OrganizationAssetPath {
  org_name: string;
  trusted_path: string; // Path para trusted_samples
  untrusted_path: string; // Path para untrusted_samples
}

// Task de export para Earth Engine
export interface EarthEngineExportTask {
  task_id: string;
  status: "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";
  asset_id: string;
  description: string;
  organization: string;
  sample_type: "trusted" | "untrusted";
  created_at: string;
}

// ACL (Access Control List) para assets
export interface AssetACL {
  asset_id: string;
  writers: string[]; // Array de emails ou grupos
  readers?: string[]; // Array de emails ou grupos (opcional)
}

export default {
  // Types
  TrustedSample,
  UntrustedSample,
  ETLConfig,
  ETLResult,
  Coordinates,

  // Schemas
  TrustedSampleSchema,
  UntrustedSampleSchema,
  ETLConfigSchema,
  CoordinatesSchema,

  // Validators
  validateTrustedSample,
  validateUntrustedSample,
  validateETLConfig,
  validateCoordinates,
  validateETLResult,

  // Type Guards
  hasValidCoordinates,
  isTrustedSample,
  isUntrustedSample,
  isValidOrgName,

  // Constants
  DefaultETLConfig,
  SampleSchemas,
};
