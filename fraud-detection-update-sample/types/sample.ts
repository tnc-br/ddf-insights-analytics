/**
 * TypeScript types for fraud detection sample data
 * Based on the fraud-detection-update-sample system
 */

// Water percentage data structure
export interface WaterPercentage {
  is_point_water: boolean;
  water_mean_in_10km_buffer: number;
  water_mean_in_1km_buffer: number;
}

// Land use percentages by year (2011-2021)
export interface LandUsePercentageByYear {
  "2011": number;
  "2012": number;
  "2013": number;
  "2014": number;
  "2015": number;
  "2016": number;
  "2017": number;
  "2018": number;
  "2019": number;
  "2020": number;
  "2021": number;
}

// Validity details from fraud detection analysis
export interface ValidityDetails {
  p_value_oxygen: number;
  p_value_carbon: number;
  p_value_nitrogen: number;
  reference_oxygen_isoscape_name?: string;
  reference_oxygen_isoscape_creation_date?: string;
  reference_oxygen_isoscape_precision?: number;
  reference_oxygen_isoscape_recall?: number;
  d18O_cel_sample_mean?: number;
  d18O_cel_sample_variance?: number;
  d18O_cel_reference_mean?: number;
  d18O_cel_reference_variance?: number;
  p_value: number;
  p_value_threshold: number;
}

// Image data for MapBiomas alerts
export interface AlertImage {
  url: string;
  satellite: string;
}

// Coordinates structure
export interface Coordinates {
  latitude: number;
  longitude: number;
}

// MapBiomas alert structure
export interface MapBiomasAlert {
  alertCode: string;
  areaHa: number;
  detectedAt: string; // Date in DD/MM/YYYY format
  alertInsertedAt: string; // Date in DD/MM/YYYY HH:mm format
  coordinates: Coordinates;
  url: string;
  distance_to_point: number;
  before: AlertImage;
  after: AlertImage;
}

// Main sample interface
export interface Sample {
  // Required fields for processing
  lat: number; // Latitude (-90 to 90)
  lon: number; // Longitude (-180 to 180)

  // Basic sample information
  sample_name: string;
  created_on: string; // Date format DD-MM-YYYY
  species: string;
  site: string;
  municipality?: string;

  // Sample status and metadata
  trusted: "trusted" | "untrusted";
  status: "concluded" | "pending" | "in_progress";
  visibility: "public" | "private";

  // User information
  created_by_name: string;
  last_updated_by?: string;
  collected_by?: string;
  org_name?: string;

  // Laboratory measurements (isotope data)
  d18O_cel?: number[]; // Oxygen isotope measurements (minimum 2 for analysis)
  d15N_cel?: number[]; // Nitrogen isotope measurements (minimum 2 for analysis)
  d13C_cel?: number[]; // Carbon isotope measurements (minimum 2 for analysis)

  // Raw measurement data
  oxygen?: number[];
  nitrogen?: number[];
  carbon?: number[];

  // Wood measurements
  n_wood?: number[];
  c_wood?: number[];
  c_cel?: number[];

  // Sample metadata
  code_lab?: string;
  amount_of_measurementste?: string;

  // Output fields (computed by the system)
  validity?: "Possible" | "Not Likely";
  validity_details?: ValidityDetails;
  water_pct?: WaterPercentage;
  land_use_anthropic_pct?: LandUsePercentageByYear;
  land_use_primary_vegetation_pct?: LandUsePercentageByYear;
  land_use_secondary_vegetation_or_regrowth_pct?: LandUsePercentageByYear;
  alerts?: MapBiomasAlert[];
}

// Input sample type (before processing)
export interface InputSample
  extends Omit<
    Sample,
    | "validity"
    | "validity_details"
    | "water_pct"
    | "land_use_anthropic_pct"
    | "land_use_primary_vegetation_pct"
    | "land_use_secondary_vegetation_or_regrowth_pct"
    | "alerts"
  > {
  // Input samples should not have output fields
}

// Output sample type (after processing)
export interface ProcessedSample
  extends Required<
    Pick<
      Sample,
      | "lat"
      | "lon"
      | "sample_name"
      | "created_on"
      | "species"
      | "site"
      | "trusted"
      | "status"
      | "visibility"
      | "created_by_name"
      | "validity"
      | "validity_details"
      | "water_pct"
      | "land_use_anthropic_pct"
      | "land_use_primary_vegetation_pct"
      | "land_use_secondary_vegetation_or_regrowth_pct"
      | "alerts"
    >
  > {
  // Additional optional fields
  municipality?: string;
  last_updated_by?: string;
  collected_by?: string;
  org_name?: string;
  d18O_cel?: number[];
  d15N_cel?: number[];
  d13C_cel?: number[];
  oxygen?: number[];
  nitrogen?: number[];
  carbon?: number[];
  n_wood?: number[];
  c_wood?: number[];
  c_cel?: number[];
  code_lab?: string;
  amount_of_measurementste?: string;
}
