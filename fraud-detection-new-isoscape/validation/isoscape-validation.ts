import { z } from "zod";

/**
 * Zod validation schemas for fraud detection new isoscape system
 * Based on the fraud-detection-new-isoscape system
 *
 * These schemas enforce:
 * - Geographic coordinate validation
 * - Timestamp format validation
 * - Asset path validation
 * - Isotope measurement constraints
 * - Processing configuration validation
 */

// ISO 8601 date validation
const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/;

// Earth Engine asset path validation
const assetPathRegex = /^projects\/[a-zA-Z0-9\-_]+\/assets\/[a-zA-Z0-9\-_\/]+$/;

// GCP Project ID validation
const projectIdRegex = /^[a-z][a-z0-9\-]{4,28}[a-z0-9]$/;

// Version string validation (v1, v2, etc.)
const versionRegex = /^v\d+(\.\d+)*$/;

// Earth Engine band schema
export const EarthEngineBandSchema = z.object({
  id: z.string().min(1, "Band ID is required"),
  dataType: z.object({
    type: z.string().min(1, "Data type is required"),
    precision: z.string().optional(),
  }),
  dimensions: z.array(z.string()).optional(),
  crs: z.string().optional(),
  crsTransform: z.array(z.number()).optional(),
});

// Geographic extent schema
export const GeographicExtentSchema = z
  .object({
    north: z
      .number()
      .min(-90, "North boundary must be >= -90")
      .max(90, "North boundary must be <= 90"),
    south: z
      .number()
      .min(-90, "South boundary must be >= -90")
      .max(90, "South boundary must be <= 90"),
    east: z
      .number()
      .min(-180, "East boundary must be >= -180")
      .max(180, "East boundary must be <= 180"),
    west: z
      .number()
      .min(-180, "West boundary must be >= -180")
      .max(180, "West boundary must be <= 180"),
    projection: z.string().optional(),
  })
  .refine((data) => data.north > data.south, {
    message: "North boundary must be greater than south boundary",
    path: ["north"],
  })
  .refine((data) => data.east > data.west, {
    message: "East boundary must be greater than west boundary",
    path: ["east"],
  });

// Earth Engine asset schema
export const EarthEngineAssetSchema = z.object({
  name: z
    .string()
    .min(1, "Asset name is required")
    .regex(assetPathRegex, "Invalid Earth Engine asset path format"),
  type: z.enum(["FOLDER", "IMAGE_COLLECTION", "IMAGE", "TABLE", "ALGORITHM"]),
  id: z.string().optional(),
  updateTime: z
    .string()
    .regex(isoDateRegex, "Update time must be in ISO 8601 format")
    .optional(),
  startTime: z
    .string()
    .regex(isoDateRegex, "Start time must be in ISO 8601 format")
    .optional(),
  endTime: z
    .string()
    .regex(isoDateRegex, "End time must be in ISO 8601 format")
    .optional(),
  sizeBytes: z.string().optional(),
  properties: z.record(z.any()).optional(),
  bands: z.array(EarthEngineBandSchema).optional(),
});

// Isoscape asset schema
export const IsoscapeAssetSchema = EarthEngineAssetSchema.extend({
  type: z.literal("IMAGE"),
  isoscape_type: z.enum(["d18O", "d13C", "d15N"]),
  version: z
    .string()
    .regex(versionRegex, "Version must be in format v1, v2.1, etc.")
    .optional(),
  creation_date: z
    .string()
    .regex(isoDateRegex, "Creation date must be in ISO 8601 format")
    .optional(),
  precision: z
    .number()
    .min(0, "Precision must be >= 0")
    .max(1, "Precision must be <= 1")
    .optional(),
  recall: z
    .number()
    .min(0, "Recall must be >= 0")
    .max(1, "Recall must be <= 1")
    .optional(),
  spatial_resolution: z
    .number()
    .positive("Spatial resolution must be positive")
    .optional(),
  geographic_extent: GeographicExtentSchema.optional(),
  source_data: z
    .string()
    .max(500, "Source data description must be less than 500 characters")
    .optional(),
  processing_method: z
    .string()
    .max(1000, "Processing method must be less than 1000 characters")
    .optional(),
});

// Isoscape update request schema
export const IsoscapeUpdateRequestSchema = z.object({
  project_id: z.string().regex(projectIdRegex, "Invalid GCP Project ID format"),
  isoscape_path: z
    .string()
    .regex(assetPathRegex, "Invalid Earth Engine asset path")
    .optional(),
  check_window_hours: z
    .number()
    .int("Check window must be an integer")
    .min(1, "Check window must be at least 1 hour")
    .max(168, "Check window cannot exceed 168 hours (1 week)")
    .default(27),
  force_update: z.boolean().default(false),
});

// Isoscape update info schema
export const IsoscapeUpdateInfoSchema = z.object({
  asset_name: z.string().min(1, "Asset name is required"),
  asset_id: z.string().min(1, "Asset ID is required"),
  isoscape_type: z.enum(["d18O", "d13C", "d15N"]),
  update_time: z
    .string()
    .regex(isoDateRegex, "Update time must be in ISO 8601 format"),
  version: z
    .string()
    .regex(versionRegex, "Version must be in format v1, v2.1, etc.")
    .optional(),
  changes: z
    .string()
    .max(1000, "Changes description must be less than 1000 characters")
    .optional(),
});

// Isoscape update response schema
export const IsoscapeUpdateResponseSchema = z.object({
  success: z.boolean(),
  updates_found: z.boolean(),
  check_timestamp: z
    .string()
    .regex(isoDateRegex, "Check timestamp must be in ISO 8601 format"),
  check_window_hours: z
    .number()
    .int("Check window must be an integer")
    .min(1, "Check window must be positive"),
  updated_assets: z.array(IsoscapeUpdateInfoSchema),
  samples_reprocessed: z
    .number()
    .int("Samples reprocessed must be an integer")
    .min(0, "Samples reprocessed cannot be negative"),
  total_samples: z
    .number()
    .int("Total samples must be an integer")
    .min(0, "Total samples cannot be negative"),
  processing_time_ms: z
    .number()
    .int("Processing time must be an integer")
    .min(0, "Processing time cannot be negative"),
  errors: z.array(z.string()).optional(),
});

// Untrusted sample schema (simplified for re-processing)
export const UntrustedSampleSchema = z.object({
  id: z.string().min(1, "Sample ID is required"),
  sample_name: z
    .string()
    .max(255, "Sample name must be less than 255 characters")
    .optional(),

  // Geographic coordinates (required for isoscape analysis)
  lat: z
    .number()
    .min(-90, "Latitude must be between -90 and 90 degrees")
    .max(90, "Latitude must be between -90 and 90 degrees"),
  lon: z
    .number()
    .min(-180, "Longitude must be between -180 and 180 degrees")
    .max(180, "Longitude must be between -180 and 180 degrees"),

  // Isotope measurements (at least one required)
  d18O_cel: z
    .array(z.number())
    .min(2, "Oxygen isotope measurements must have at least 2 values")
    .max(50, "Too many oxygen measurements")
    .optional(),
  d15N_cel: z
    .array(z.number())
    .min(2, "Nitrogen isotope measurements must have at least 2 values")
    .max(50, "Too many nitrogen measurements")
    .optional(),
  d13C_cel: z
    .array(z.number())
    .min(2, "Carbon isotope measurements must have at least 2 values")
    .max(50, "Too many carbon measurements")
    .optional(),

  // Status and metadata
  status: z.enum(["pending", "processing", "completed", "failed"]).optional(),
  created_at: z
    .string()
    .regex(isoDateRegex, "Created at must be in ISO 8601 format")
    .optional(),
  updated_at: z
    .string()
    .regex(isoDateRegex, "Updated at must be in ISO 8601 format")
    .optional(),

  // Analysis results
  validity: z.enum(["Possible", "Not Likely"]).optional(),
  validity_details: z.record(z.any()).optional(),

  // Additional metadata
  org: z
    .string()
    .max(50, "Organization ID must be less than 50 characters")
    .optional(),
  created_by: z
    .string()
    .max(100, "Created by must be less than 100 characters")
    .optional(),
});

// Processing error schema
export const ProcessingErrorSchema = z.object({
  sample_id: z.string().min(1, "Sample ID is required"),
  error_type: z.enum(["validation", "earth_engine", "firestore", "unknown"]),
  error_message: z
    .string()
    .min(1, "Error message is required")
    .max(1000, "Error message must be less than 1000 characters"),
  timestamp: z
    .string()
    .regex(isoDateRegex, "Timestamp must be in ISO 8601 format"),
  retry_count: z
    .number()
    .int("Retry count must be an integer")
    .min(0, "Retry count cannot be negative")
    .optional(),
});

// Batch processing summary schema
export const BatchProcessingSummarySchema = z.object({
  total_samples: z
    .number()
    .int("Total samples must be an integer")
    .min(0, "Total samples cannot be negative"),
  successful_updates: z
    .number()
    .int("Successful updates must be an integer")
    .min(0, "Successful updates cannot be negative"),
  failed_updates: z
    .number()
    .int("Failed updates must be an integer")
    .min(0, "Failed updates cannot be negative"),
  skipped_samples: z
    .number()
    .int("Skipped samples must be an integer")
    .min(0, "Skipped samples cannot be negative"),

  validity_changes: z.object({
    possible_to_not_likely: z
      .number()
      .int("Must be an integer")
      .min(0, "Cannot be negative"),
    not_likely_to_possible: z
      .number()
      .int("Must be an integer")
      .min(0, "Cannot be negative"),
    no_change: z
      .number()
      .int("Must be an integer")
      .min(0, "Cannot be negative"),
  }),

  average_processing_time_ms: z
    .number()
    .int("Average processing time must be an integer")
    .min(0, "Average processing time cannot be negative"),
  total_processing_time_ms: z
    .number()
    .int("Total processing time must be an integer")
    .min(0, "Total processing time cannot be negative"),
});

// Batch reprocessing operation schema
export const BatchReprocessingOperationSchema = z.object({
  operation_id: z.string().min(1, "Operation ID is required"),
  trigger_reason: z.enum(["isoscape_update", "manual", "scheduled"]),
  start_time: z
    .string()
    .regex(isoDateRegex, "Start time must be in ISO 8601 format"),
  end_time: z
    .string()
    .regex(isoDateRegex, "End time must be in ISO 8601 format")
    .optional(),
  status: z.enum(["running", "completed", "failed", "cancelled"]),

  samples_to_process: z
    .number()
    .int("Samples to process must be an integer")
    .min(0, "Samples to process cannot be negative"),
  samples_processed: z
    .number()
    .int("Samples processed must be an integer")
    .min(0, "Samples processed cannot be negative"),
  samples_failed: z
    .number()
    .int("Samples failed must be an integer")
    .min(0, "Samples failed cannot be negative"),

  updated_isoscapes: z.array(IsoscapeUpdateInfoSchema),
  processing_errors: z.array(ProcessingErrorSchema).optional(),
  summary: BatchProcessingSummarySchema.optional(),
});

// Isoscape monitoring configuration schema
export const IsoscapeMonitoringConfigSchema = z.object({
  project_id: z.string().regex(projectIdRegex, "Invalid GCP Project ID format"),
  isoscape_base_path: z
    .string()
    .regex(assetPathRegex, "Invalid Earth Engine asset path"),
  check_interval_hours: z
    .number()
    .int("Check interval must be an integer")
    .min(1, "Check interval must be at least 1 hour")
    .max(168, "Check interval cannot exceed 168 hours"),
  update_window_hours: z
    .number()
    .int("Update window must be an integer")
    .min(1, "Update window must be at least 1 hour")
    .max(168, "Update window cannot exceed 168 hours"),

  firestore_project: z
    .string()
    .regex(projectIdRegex, "Invalid Firestore project ID format")
    .optional(),
  untrusted_samples_collection: z
    .string()
    .min(1, "Collection name is required")
    .max(100, "Collection name must be less than 100 characters"),

  batch_size: z
    .number()
    .int("Batch size must be an integer")
    .min(1, "Batch size must be at least 1")
    .max(1000, "Batch size cannot exceed 1000")
    .optional(),
  max_concurrent_updates: z
    .number()
    .int("Max concurrent updates must be an integer")
    .min(1, "Max concurrent updates must be at least 1")
    .max(100, "Max concurrent updates cannot exceed 100")
    .optional(),
  retry_failed_samples: z.boolean().optional(),

  notify_on_completion: z.boolean().optional(),
  notification_endpoints: z
    .array(z.string().url("Must be a valid URL"))
    .max(10, "Cannot have more than 10 notification endpoints")
    .optional(),
});

// Custom validation for isotope measurements
export const validateIsotopeMeasurements = (sample: unknown) => {
  const parsed = UntrustedSampleSchema.parse(sample);

  // At least one type of isotope measurement should be provided
  const hasOxygen = parsed.d18O_cel && parsed.d18O_cel.length >= 2;
  const hasNitrogen = parsed.d15N_cel && parsed.d15N_cel.length >= 2;
  const hasCarbon = parsed.d13C_cel && parsed.d13C_cel.length >= 2;

  if (!hasOxygen && !hasNitrogen && !hasCarbon) {
    throw new z.ZodError([
      {
        code: "custom",
        message:
          "At least one type of isotope measurement (d18O_cel, d15N_cel, or d13C_cel) with minimum 2 values is required",
        path: ["isotope_measurements"],
      },
    ]);
  }

  return parsed;
};

// Validation functions
export const validateIsoscapeAsset = (data: unknown) => {
  return IsoscapeAssetSchema.safeParse(data);
};

export const validateUpdateRequest = (data: unknown) => {
  return IsoscapeUpdateRequestSchema.safeParse(data);
};

export const validateUpdateResponse = (data: unknown) => {
  return IsoscapeUpdateResponseSchema.safeParse(data);
};

export const validateUntrustedSample = (data: unknown) => {
  // First validate basic schema
  const basicValidation = UntrustedSampleSchema.safeParse(data);
  if (!basicValidation.success) {
    return basicValidation;
  }

  // Then apply custom validation
  try {
    const validatedSample = validateIsotopeMeasurements(data);
    return { success: true as const, data: validatedSample };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false as const, error };
    }
    throw error;
  }
};

export const validateBatchOperation = (data: unknown) => {
  return BatchReprocessingOperationSchema.safeParse(data);
};

export const validateMonitoringConfig = (data: unknown) => {
  return IsoscapeMonitoringConfigSchema.safeParse(data);
};

// Helper function to validate time window consistency
export const validateTimeWindow = (
  checkWindowHours: number,
  maxAllowedHours: number = 168
) => {
  return z
    .number()
    .int("Check window must be an integer")
    .min(1, "Check window must be at least 1 hour")
    .max(maxAllowedHours, `Check window cannot exceed ${maxAllowedHours} hours`)
    .safeParse(checkWindowHours);
};

// Export the inferred types
export type EarthEngineAsset = z.infer<typeof EarthEngineAssetSchema>;
export type IsoscapeAsset = z.infer<typeof IsoscapeAssetSchema>;
export type IsoscapeUpdateRequest = z.infer<typeof IsoscapeUpdateRequestSchema>;
export type IsoscapeUpdateResponse = z.infer<
  typeof IsoscapeUpdateResponseSchema
>;
export type IsoscapeUpdateInfo = z.infer<typeof IsoscapeUpdateInfoSchema>;
export type UntrustedSample = z.infer<typeof UntrustedSampleSchema>;
export type BatchReprocessingOperation = z.infer<
  typeof BatchReprocessingOperationSchema
>;
export type ProcessingError = z.infer<typeof ProcessingErrorSchema>;
export type BatchProcessingSummary = z.infer<
  typeof BatchProcessingSummarySchema
>;
export type IsoscapeMonitoringConfig = z.infer<
  typeof IsoscapeMonitoringConfigSchema
>;
export type GeographicExtent = z.infer<typeof GeographicExtentSchema>;
export type EarthEngineBand = z.infer<typeof EarthEngineBandSchema>;
