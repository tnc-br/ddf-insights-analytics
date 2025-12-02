import { z } from "zod";

/**
 * Zod validation schemas for fraud detection sample data
 * Based on the fraud-detection-update-sample system
 *
 * These schemas enforce:
 * - Data types
 * - Value ranges and constraints
 * - Required vs optional fields
 * - Array length requirements
 * - String format validations
 */

// Date validation regex (DD-MM-YYYY format)
const dateRegex = /^\d{1,2}-\d{1,2}-\d{4}$/;

// Date and time validation regex (DD/MM/YYYY HH:mm format)
const dateTimeRegex = /^\d{1,2}\/\d{1,2}\/\d{4} \d{1,2}:\d{2}$/;

// Simple date validation regex (DD/MM/YYYY format)
const simpleDateRegex = /^\d{1,2}\/\d{1,2}\/\d{4}$/;

// Water percentage schema
export const WaterPercentageSchema = z.object({
  is_point_water: z.boolean(),
  water_mean_in_10km_buffer: z.number().min(0).max(1),
  water_mean_in_1km_buffer: z.number().min(0).max(1),
});

// Land use percentage by year schema (percentages should be 0-1)
export const LandUsePercentageByYearSchema = z.object({
  "2011": z.number().min(0).max(1),
  "2012": z.number().min(0).max(1),
  "2013": z.number().min(0).max(1),
  "2014": z.number().min(0).max(1),
  "2015": z.number().min(0).max(1),
  "2016": z.number().min(0).max(1),
  "2017": z.number().min(0).max(1),
  "2018": z.number().min(0).max(1),
  "2019": z.number().min(0).max(1),
  "2020": z.number().min(0).max(1),
  "2021": z.number().min(0).max(1),
});

// Validity details schema
export const ValidityDetailsSchema = z.object({
  p_value_oxygen: z.number().min(0).max(1),
  p_value_carbon: z.number().min(0).max(1),
  p_value_nitrogen: z.number().min(0).max(1),
  reference_oxygen_isoscape_name: z.string().optional(),
  reference_oxygen_isoscape_creation_date: z.string().optional(),
  reference_oxygen_isoscape_precision: z.number().min(0).max(1).optional(),
  reference_oxygen_isoscape_recall: z.number().min(0).max(1).optional(),
  d18O_cel_sample_mean: z.number().optional(),
  d18O_cel_sample_variance: z.number().min(0).optional(),
  d18O_cel_reference_mean: z.number().optional(),
  d18O_cel_reference_variance: z.number().min(0).optional(),
  p_value: z.number().min(0).max(1),
  p_value_threshold: z.number().min(0).max(1),
});

// Alert image schema
export const AlertImageSchema = z.object({
  url: z.string().url(),
  satellite: z.string().min(1),
});

// Coordinates schema
export const CoordinatesSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
});

// MapBiomas alert schema
export const MapBiomasAlertSchema = z.object({
  alertCode: z.string().min(1),
  areaHa: z.number().min(0),
  detectedAt: z
    .string()
    .regex(simpleDateRegex, "Date must be in DD/MM/YYYY format"),
  alertInsertedAt: z
    .string()
    .regex(dateTimeRegex, "DateTime must be in DD/MM/YYYY HH:mm format"),
  coordinates: CoordinatesSchema,
  url: z.string().url(),
  distance_to_point: z.number().min(0),
  before: AlertImageSchema,
  after: AlertImageSchema,
});

// Base sample schema with core validation rules
export const SampleSchema = z.object({
  // Required geographic coordinates
  lat: z
    .number()
    .min(-90, "Latitude must be between -90 and 90 degrees")
    .max(90, "Latitude must be between -90 and 90 degrees"),
  lon: z
    .number()
    .min(-180, "Longitude must be between -180 and 180 degrees")
    .max(180, "Longitude must be between -180 and 180 degrees"),

  // Required basic information
  sample_name: z
    .string()
    .min(1, "Sample name is required")
    .max(255, "Sample name must be less than 255 characters"),
  created_on: z.string().regex(dateRegex, "Date must be in DD-MM-YYYY format"),
  species: z
    .string()
    .min(1, "Species is required")
    .max(100, "Species must be less than 100 characters"),
  site: z
    .string()
    .min(1, "Site is required")
    .max(100, "Site must be less than 100 characters"),

  // Required status fields
  trusted: z.enum(["trusted", "untrusted"]),
  status: z.enum(["concluded", "pending", "in_progress"]),
  visibility: z.enum(["public", "private"]),

  // Required user information
  created_by_name: z
    .string()
    .min(1, "Creator name is required")
    .max(100, "Creator name must be less than 100 characters"),

  // Optional basic fields
  municipality: z.string().max(100).optional(),
  last_updated_by: z.string().max(100).optional(),
  collected_by: z.string().max(100).optional(),
  org_name: z.string().max(100).optional(),
  code_lab: z.string().max(50).optional(),
  amount_of_measurementste: z.string().max(20).optional(),

  // Isotope measurements (must have at least 2 measurements for analysis)
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

  // Raw measurement arrays
  oxygen: z.array(z.number()).max(50).optional(),
  nitrogen: z.array(z.number()).max(50).optional(),
  carbon: z.array(z.number()).max(50).optional(),

  // Wood measurement arrays
  n_wood: z.array(z.number()).max(50).optional(),
  c_wood: z.array(z.number()).max(50).optional(),
  c_cel: z.array(z.number()).max(50).optional(),

  // Output fields (computed by the system)
  validity: z.enum(["Possible", "Not Likely"]).optional(),
  validity_details: ValidityDetailsSchema.optional(),
  water_pct: WaterPercentageSchema.optional(),
  land_use_anthropic_pct: LandUsePercentageByYearSchema.optional(),
  land_use_primary_vegetation_pct: LandUsePercentageByYearSchema.optional(),
  land_use_secondary_vegetation_or_regrowth_pct:
    LandUsePercentageByYearSchema.optional(),
  alerts: z.array(MapBiomasAlertSchema).max(1000).optional(),
});

// Input sample schema (before processing) - excludes output fields
export const InputSampleSchema = SampleSchema.omit({
  validity: true,
  validity_details: true,
  water_pct: true,
  land_use_anthropic_pct: true,
  land_use_primary_vegetation_pct: true,
  land_use_secondary_vegetation_or_regrowth_pct: true,
  alerts: true,
});

// Processed sample schema (after processing) - requires all output fields
export const ProcessedSampleSchema = SampleSchema.extend({
  validity: z.enum(["Possible", "Not Likely"]),
  validity_details: ValidityDetailsSchema,
  water_pct: WaterPercentageSchema,
  land_use_anthropic_pct: LandUsePercentageByYearSchema,
  land_use_primary_vegetation_pct: LandUsePercentageByYearSchema,
  land_use_secondary_vegetation_or_regrowth_pct: LandUsePercentageByYearSchema,
  alerts: z.array(MapBiomasAlertSchema),
});

// Custom validation for isotope measurements
export const validateIsotopeMeasurements = (sample: unknown) => {
  const parsed = SampleSchema.parse(sample);

  // At least one type of isotope measurement should be provided for analysis
  const hasOxygen = parsed.d18O_cel && parsed.d18O_cel.length >= 2;
  const hasNitrogen = parsed.d15N_cel && parsed.d15N_cel.length >= 2;
  const hasCarbon = parsed.d13C_cel && parsed.d13C_cel.length >= 2;

  if (!hasOxygen && !hasNitrogen && !hasCarbon) {
    throw new z.ZodError([
      {
        code: "custom",
        message:
          "At least one type of isotope measurement (d18O_cel, d15N_cel, or d13C_cel) with minimum 2 values is required for fraud detection analysis",
        path: ["isotope_measurements"],
      },
    ]);
  }

  return parsed;
};

// Validation function with custom rules
export const validateSample = (data: unknown) => {
  // First validate basic schema
  const basicValidation = SampleSchema.safeParse(data);
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

// Input validation function
export const validateInputSample = (data: unknown) => {
  // First validate basic input schema
  const basicValidation = InputSampleSchema.safeParse(data);
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

// Export the inferred types
export type Sample = z.infer<typeof SampleSchema>;
export type InputSample = z.infer<typeof InputSampleSchema>;
export type ProcessedSample = z.infer<typeof ProcessedSampleSchema>;
export type WaterPercentage = z.infer<typeof WaterPercentageSchema>;
export type LandUsePercentageByYear = z.infer<
  typeof LandUsePercentageByYearSchema
>;
export type ValidityDetails = z.infer<typeof ValidityDetailsSchema>;
export type MapBiomasAlert = z.infer<typeof MapBiomasAlertSchema>;
export type AlertImage = z.infer<typeof AlertImageSchema>;
export type Coordinates = z.infer<typeof CoordinatesSchema>;
