import { z } from "zod";

// ============================================================================
// FRAUD DETECTION GENERATE MAPS - TYPESCRIPT TYPES & ZOD VALIDATION
// ============================================================================

// Coordenadas geográficas com validação de faixas válidas
export interface Coordinates {
  latitude: number; // -90 a 90
  longitude: number; // -180 a 180
}

// Imagem de satélite para alertas
export interface SatelliteImage {
  url: string;
  satellite: "PlanetScope" | "Sentinel-2" | string;
}

// Imagens antes e depois para alertas MapBiomas
export interface AlertImages {
  before: SatelliteImage;
  after: SatelliteImage;
}

// Alerta individual do MapBiomas
export interface MapbiomasAlert {
  alertCode: string;
  areaHa: number;
  detectedAt: string;
  url: string;
  distance_to_point: number;
  coordinates: Coordinates;
  alertInsertedAt: string;
  before: SatelliteImage;
  after: SatelliteImage;
}

// Dados de uso da terra (percentuais por ano)
export interface LandUseData {
  [year: string]: number; // Percentual de 0 a 100
}

// Dados de água (percentuais)
export interface WaterData {
  is_point_water: boolean;
  water_mean_in_1km_buffer: number;
  water_mean_in_10km_buffer: number;
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

// Sample principal usado para geração de mapas
export interface MapGenerationSample {
  // Identificação obrigatória
  sample_name: string;
  code_lab: string;
  created_by: string;

  // Coordenadas obrigatórias para geração de mapas
  lat: number; // Latitude: -90 a 90
  lon: number; // Longitude: -180 a 180

  // Dados isotópicos obrigatórios (arrays de medições)
  d18O_cel: number[]; // Medições de oxigênio-18 na celulose
  d15N_cel?: number[]; // Medições de nitrogênio-15 na celulose (opcional)
  d13C_cel?: number[]; // Medições de carbono-13 na celulose (opcional)

  // Informações da amostra
  species: string;
  trusted: "trusted" | "untrusted";
  status: "pending" | "processing" | "concluded" | "failed";

  // Metadados temporais
  created_on: string;
  date_of_harvest?: string;
  last_updated_by?: string;

  // Dados organizacionais
  org_name?: string;

  // Dados adicionais enriquecidos pelo sistema
  validity?: "valid" | "invalid" | number;
  validity_details?: ValidityDetails;

  // Dados de uso da terra (adicionados pelo sistema)
  water_pct?: WaterData;
  land_use_anthropic_pct?: LandUseData;
  land_use_primary_vegetation_pct?: LandUseData;
  land_use_secondary_vegetation_or_regrowth_pct?: LandUseData;

  // Alertas MapBiomas (adicionados pelo sistema)
  alerts?: MapbiomasAlert[];

  // Dados adicionais de madeira
  n_wood?: number[];
}

// Mensagem Pub/Sub para geração de mapas
export interface MapGenerationMessage {
  // Mensagem individual com coordenadas específicas
  latitude?: number;
  longitude?: number;
  document_id?: string;

  // OU comando especial para processar todos os mapas
  command?: "ALL_MAPS";
}

// Configuração do sistema de geração de mapas
export interface MapGenerationConfig {
  gcs_bucket_name: string;
  gcs_folder_name: string;
  gcp_project_id: string;
  topic_id: string;
  mapbiomas_asset_path: string;
}

// Parâmetros de visualização para MapBiomas
export interface MapVisualizationParams {
  min: number;
  max: number;
  palette: string[]; // Array de cores hex
}

// Layers do mapa gerado
export interface MapLayers {
  brazil_land_use: string;
  radius_mask_1km: string;
  radius_mask_10km: string;
}

// ============================================================================
// ZOD VALIDATION SCHEMAS
// ============================================================================

// Schema para coordenadas geográficas
export const CoordinatesSchema = z.object({
  latitude: z
    .number()
    .min(-90, "Latitude deve estar entre -90 e 90")
    .max(90, "Latitude deve estar entre -90 e 90"),
  longitude: z
    .number()
    .min(-180, "Longitude deve estar entre -180 e 180")
    .max(180, "Longitude deve estar entre -180 e 180"),
});

// Schema para imagem de satélite
export const SatelliteImageSchema = z.object({
  url: z.string().url("URL deve ser válida"),
  satellite: z.string().min(1, "Satélite é obrigatório"),
});

// Schema para alerta MapBiomas
export const MapbiomasAlertSchema = z.object({
  alertCode: z.string().min(1, "Código do alerta é obrigatório"),
  areaHa: z.number().positive("Área deve ser positiva"),
  detectedAt: z.string().min(1, "Data de detecção é obrigatória"),
  url: z.string().url("URL deve ser válida"),
  distance_to_point: z.number().nonnegative("Distância não pode ser negativa"),
  coordinates: CoordinatesSchema,
  alertInsertedAt: z.string().min(1, "Data de inserção é obrigatória"),
  before: SatelliteImageSchema,
  after: SatelliteImageSchema,
});

// Schema para dados de uso da terra (percentuais por ano)
export const LandUseDataSchema = z.record(
  z.string(), // Ano como string
  z
    .number()
    .min(0, "Percentual não pode ser negativo")
    .max(100, "Percentual não pode exceder 100")
);

// Schema para dados de água
export const WaterDataSchema = z.object({
  is_point_water: z.boolean(),
  water_mean_in_1km_buffer: z
    .number()
    .min(0, "Percentual de água não pode ser negativo")
    .max(100, "Percentual de água não pode exceder 100"),
  water_mean_in_10km_buffer: z
    .number()
    .min(0, "Percentual de água não pode ser negativo")
    .max(100, "Percentual de água não pode exceder 100"),
});

// Schema para detalhes de validação
export const ValidityDetailsSchema = z.object({
  p_value_oxygen: z.number().min(0).max(1).optional(),
  p_value_carbon: z.number().min(0).max(1).optional(),
  p_value_nitrogen: z.number().min(0).max(1).optional(),
  reference_oxygen_isoscape_name: z.string().optional(),
  reference_oxygen_isoscape_creation_date: z.string().optional(),
  reference_oxygen_isoscape_precision: z.number().min(0).max(1).optional(),
  reference_oxygen_isoscape_recall: z.number().min(0).max(1).optional(),
  d18O_cel_sample_mean: z.number().optional(),
  d18O_cel_sample_variance: z.number().nonnegative().optional(),
  d18O_cel_reference_mean: z.number().optional(),
  d18O_cel_reference_variance: z.number().nonnegative().optional(),
  p_value: z.number().min(0).max(1).optional(),
  p_value_threshold: z.number().min(0).max(1).optional(),
});

// Schema principal para sample de geração de mapas
export const MapGenerationSampleSchema = z.object({
  // Identificação obrigatória
  sample_name: z.string().min(1, "Nome da amostra é obrigatório"),
  code_lab: z.string().min(1, "Código do laboratório é obrigatório"),
  created_by: z.string().min(1, "Criador é obrigatório"),

  // Coordenadas obrigatórias para geração de mapas
  lat: z
    .number()
    .min(-90, "Latitude deve estar entre -90 e 90")
    .max(90, "Latitude deve estar entre -90 e 90"),
  lon: z
    .number()
    .min(-180, "Longitude deve estar entre -180 e 180")
    .max(180, "Longitude deve estar entre -180 e 180"),

  // Dados isotópicos obrigatórios
  d18O_cel: z
    .array(z.number())
    .min(2, "Mínimo de 2 medições de oxigênio-18 necessárias")
    .max(50, "Máximo de 50 medições permitidas"),
  d15N_cel: z
    .array(z.number())
    .min(2, "Mínimo de 2 medições de nitrogênio-15 quando fornecidas")
    .max(50, "Máximo de 50 medições permitidas")
    .optional(),
  d13C_cel: z
    .array(z.number())
    .min(2, "Mínimo de 2 medições de carbono-13 quando fornecidas")
    .max(50, "Máximo de 50 medições permitidas")
    .optional(),

  // Informações da amostra
  species: z.string().min(1, "Espécie é obrigatória"),
  trusted: z.enum(["trusted", "untrusted"], {
    errorMap: () => ({ message: 'Status deve ser "trusted" ou "untrusted"' }),
  }),
  status: z.enum(["pending", "processing", "concluded", "failed"], {
    errorMap: () => ({
      message: "Status deve ser: pending, processing, concluded ou failed",
    }),
  }),

  // Metadados temporais
  created_on: z.string().min(1, "Data de criação é obrigatória"),
  date_of_harvest: z.string().optional(),
  last_updated_by: z.string().optional(),

  // Dados organizacionais
  org_name: z.string().optional(),

  // Dados enriquecidos pelo sistema (opcionais)
  validity: z
    .union([z.enum(["valid", "invalid"]), z.number().min(0)])
    .optional(),
  validity_details: ValidityDetailsSchema.optional(),

  // Dados de uso da terra
  water_pct: WaterDataSchema.optional(),
  land_use_anthropic_pct: LandUseDataSchema.optional(),
  land_use_primary_vegetation_pct: LandUseDataSchema.optional(),
  land_use_secondary_vegetation_or_regrowth_pct: LandUseDataSchema.optional(),

  // Alertas MapBiomas
  alerts: z.array(MapbiomasAlertSchema).optional(),

  // Dados adicionais
  n_wood: z.array(z.number()).optional(),
});

// Schema para mensagem Pub/Sub
export const MapGenerationMessageSchema = z.union([
  // Mensagem com coordenadas específicas
  z.object({
    latitude: z
      .number()
      .min(-90, "Latitude deve estar entre -90 e 90")
      .max(90, "Latitude deve estar entre -90 e 90"),
    longitude: z
      .number()
      .min(-180, "Longitude deve estar entre -180 e 180")
      .max(180, "Longitude deve estar entre -180 e 180"),
    document_id: z.string().min(1, "ID do documento é obrigatório"),
  }),
  // Comando para processar todos os mapas
  z.object({
    command: z.literal("ALL_MAPS"),
  }),
]);

// Schema para configuração do sistema
export const MapGenerationConfigSchema = z.object({
  gcs_bucket_name: z.string().min(1, "Nome do bucket GCS é obrigatório"),
  gcs_folder_name: z.string().min(1, "Nome da pasta GCS é obrigatória"),
  gcp_project_id: z.string().min(1, "ID do projeto GCP é obrigatório"),
  topic_id: z.string().min(1, "ID do tópico Pub/Sub é obrigatório"),
  mapbiomas_asset_path: z
    .string()
    .min(1, "Caminho do asset MapBiomas é obrigatório"),
});

// Schema para parâmetros de visualização
export const MapVisualizationParamsSchema = z.object({
  min: z.number(),
  max: z.number(),
  palette: z
    .array(
      z
        .string()
        .regex(/^#[0-9A-Fa-f]{6}$/, "Cores devem estar no formato hexadecimal")
    )
    .min(1, "Pelo menos uma cor é necessária"),
});

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

/**
 * Valida uma sample para geração de mapas
 */
export function validateMapGenerationSample(
  data: unknown
): MapGenerationSample {
  const result = MapGenerationSampleSchema.safeParse(data);

  if (!result.success) {
    const errors = result.error.errors
      .map((err) => `${err.path.join(".")}: ${err.message}`)
      .join(", ");
    throw new Error(`Validação da sample falhou: ${errors}`);
  }

  return result.data;
}

/**
 * Valida uma mensagem Pub/Sub para geração de mapas
 */
export function validateMapGenerationMessage(
  data: unknown
): MapGenerationMessage {
  const result = MapGenerationMessageSchema.safeParse(data);

  if (!result.success) {
    const errors = result.error.errors
      .map((err) => `${err.path.join(".")}: ${err.message}`)
      .join(", ");
    throw new Error(`Validação da mensagem Pub/Sub falhou: ${errors}`);
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
 * Valida configuração do sistema
 */
export function validateMapGenerationConfig(
  data: unknown
): MapGenerationConfig {
  const result = MapGenerationConfigSchema.safeParse(data);

  if (!result.success) {
    const errors = result.error.errors
      .map((err) => `${err.path.join(".")}: ${err.message}`)
      .join(", ");
    throw new Error(`Validação da configuração falhou: ${errors}`);
  }

  return result.data;
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Verifica se uma sample tem coordenadas válidas para geração de mapas
 */
export function hasValidCoordinates(
  sample: Partial<MapGenerationSample>
): sample is MapGenerationSample & { lat: number; lon: number } {
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
 * Verifica se uma mensagem é um comando ALL_MAPS
 */
export function isAllMapsCommand(
  message: MapGenerationMessage
): message is { command: "ALL_MAPS" } {
  return "command" in message && message.command === "ALL_MAPS";
}

/**
 * Verifica se uma mensagem contém coordenadas específicas
 */
export function isCoordinateMessage(
  message: MapGenerationMessage
): message is { latitude: number; longitude: number; document_id: string } {
  return (
    "latitude" in message && "longitude" in message && "document_id" in message
  );
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

// Sample mínima necessária para geração de mapas
export type MinimalMapSample = Pick<MapGenerationSample, "lat" | "lon">;

// Sample com dados enriquecidos completos
export type EnrichedMapSample = Required<
  Pick<
    MapGenerationSample,
    | "lat"
    | "lon"
    | "water_pct"
    | "land_use_anthropic_pct"
    | "land_use_primary_vegetation_pct"
    | "land_use_secondary_vegetation_or_regrowth_pct"
    | "alerts"
  >
>;

// Configuração para layers do mapa
export type MapLayerConfig = {
  readonly BRAZIL_LAND_USE: string;
  readonly RADIUS_MASK_1KM: string;
  readonly RADIUS_MASK_10KM: string;
};

// Resultado da geração de mapa
export interface MapGenerationResult {
  document_id: string;
  html_file_path: string;
  gcs_upload_path: string;
  generation_timestamp: string;
  coordinates: Coordinates;
  processing_time_ms: number;
}

export default {
  // Types
  MapGenerationSample,
  MapGenerationMessage,
  MapGenerationConfig,
  Coordinates,
  MapbiomasAlert,
  ValidityDetails,

  // Schemas
  MapGenerationSampleSchema,
  MapGenerationMessageSchema,
  MapGenerationConfigSchema,
  CoordinatesSchema,

  // Validators
  validateMapGenerationSample,
  validateMapGenerationMessage,
  validateCoordinates,
  validateMapGenerationConfig,

  // Type Guards
  hasValidCoordinates,
  isAllMapsCommand,
  isCoordinateMessage,
};
