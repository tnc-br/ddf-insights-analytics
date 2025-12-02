/**
 * TypeScript types for fraud detection new isoscape system
 * Based on the fraud-detection-new-isoscape system
 */

// Isoscape types (isotope reference maps)
export type IsoscapeType = "d18O" | "d13C" | "d15N";

// Earth Engine asset types
export type EarthEngineAssetType =
  | "FOLDER"
  | "IMAGE_COLLECTION"
  | "IMAGE"
  | "TABLE"
  | "ALGORITHM";

// Earth Engine asset structure
export interface EarthEngineAsset {
  name: string; // Full asset path (e.g., projects/project-id/assets/isoscapes/d18O_v1)
  type: EarthEngineAssetType;
  id?: string; // Asset ID
  updateTime?: string; // ISO 8601 timestamp of last update
  startTime?: string; // ISO 8601 timestamp
  endTime?: string; // ISO 8601 timestamp
  sizeBytes?: string; // Size in bytes as string
  properties?: Record<string, any>; // Custom properties
  bands?: EarthEngineBand[]; // Image bands (for IMAGE and IMAGE_COLLECTION)
}

// Earth Engine band information
export interface EarthEngineBand {
  id: string; // Band name/identifier
  dataType: {
    type: string; // Data type (e.g., "DOUBLE", "INT32")
    precision?: string; // Precision information
  };
  dimensions?: string[]; // Band dimensions
  crs?: string; // Coordinate reference system
  crsTransform?: number[]; // CRS transformation matrix
}

// Isoscape asset structure
export interface IsoscapeAsset extends EarthEngineAsset {
  type: "IMAGE"; // Isoscapes are always images
  isoscape_type: IsoscapeType; // Type of isotope (d18O, d13C, d15N)
  version?: string; // Version identifier (e.g., "v1", "v2")
  creation_date?: string; // ISO 8601 date when isoscape was created
  precision?: number; // Statistical precision (0-1)
  recall?: number; // Statistical recall (0-1)
  spatial_resolution?: number; // Resolution in meters
  geographic_extent?: GeographicExtent; // Geographic coverage
  source_data?: string; // Description of source data
  processing_method?: string; // How the isoscape was generated
}

// Geographic extent
export interface GeographicExtent {
  north: number; // Northern boundary (latitude)
  south: number; // Southern boundary (latitude)
  east: number; // Eastern boundary (longitude)
  west: number; // Western boundary (longitude)
  projection?: string; // Coordinate system
}

// Isoscape update check request
export interface IsoscapeUpdateRequest {
  project_id: string; // GCP Project ID
  isoscape_path?: string; // Custom path to isoscapes folder
  check_window_hours?: number; // Hours to look back for updates (default: 27)
  force_update?: boolean; // Force re-processing regardless of updates
}

// Isoscape update check response
export interface IsoscapeUpdateResponse {
  success: boolean;
  updates_found: boolean; // Whether any isoscapes were updated
  check_timestamp: string; // ISO 8601 timestamp of check
  check_window_hours: number; // Hours checked for updates
  updated_assets: IsoscapeUpdateInfo[]; // List of updated assets
  samples_reprocessed: number; // Number of samples that were re-processed
  total_samples: number; // Total samples in untrusted_samples collection
  processing_time_ms: number; // Time taken for the operation
  errors?: string[]; // Any errors encountered
}

// Information about an updated isoscape
export interface IsoscapeUpdateInfo {
  asset_name: string; // Full asset path
  asset_id: string; // Asset identifier
  isoscape_type: IsoscapeType; // Type of isotope
  update_time: string; // ISO 8601 timestamp of update
  version?: string; // Version identifier
  changes?: string; // Description of changes
}

// Firestore sample document (simplified for re-processing)
export interface UntrustedSample {
  // Core identification
  id: string; // Document ID
  sample_name?: string; // Name of the sample

  // Geographic coordinates (required for isoscape analysis)
  lat: number; // Latitude (-90 to 90)
  lon: number; // Longitude (-180 to 180)

  // Isotope measurements (at least one required)
  d18O_cel?: number[]; // Oxygen isotope measurements
  d15N_cel?: number[]; // Nitrogen isotope measurements
  d13C_cel?: number[]; // Carbon isotope measurements

  // Status and metadata
  status?: "pending" | "processing" | "completed" | "failed";
  created_at?: string; // ISO 8601 timestamp
  updated_at?: string; // ISO 8601 timestamp

  // Analysis results (will be updated after re-processing)
  validity?: "Possible" | "Not Likely";
  validity_details?: Record<string, any>;

  // Additional metadata
  org?: string; // Organization ID
  created_by?: string; // User who created the sample
}

// Batch re-processing operation
export interface BatchReprocessingOperation {
  operation_id: string; // Unique identifier for this operation
  trigger_reason: "isoscape_update" | "manual" | "scheduled";
  start_time: string; // ISO 8601 timestamp
  end_time?: string; // ISO 8601 timestamp (when completed)
  status: "running" | "completed" | "failed" | "cancelled";

  // Scope of operation
  samples_to_process: number; // Total samples to re-process
  samples_processed: number; // Samples completed
  samples_failed: number; // Samples that failed processing

  // Trigger information
  updated_isoscapes: IsoscapeUpdateInfo[]; // Isoscapes that triggered this operation

  // Results
  processing_errors?: ProcessingError[]; // Errors encountered
  summary?: BatchProcessingSummary; // Summary of results
}

// Processing error information
export interface ProcessingError {
  sample_id: string; // ID of sample that failed
  error_type: "validation" | "earth_engine" | "firestore" | "unknown";
  error_message: string; // Error description
  timestamp: string; // ISO 8601 timestamp
  retry_count?: number; // Number of retries attempted
}

// Summary of batch processing results
export interface BatchProcessingSummary {
  total_samples: number;
  successful_updates: number;
  failed_updates: number;
  skipped_samples: number; // Samples skipped due to missing data

  // Changes in results
  validity_changes: {
    possible_to_not_likely: number;
    not_likely_to_possible: number;
    no_change: number;
  };

  // Performance metrics
  average_processing_time_ms: number;
  total_processing_time_ms: number;
}

// Configuration for the isoscape monitoring system
export interface IsoscapeMonitoringConfig {
  project_id: string;
  isoscape_base_path: string; // Base path for isoscapes in Earth Engine
  check_interval_hours: number; // How often to check for updates
  update_window_hours: number; // How far back to look for updates

  // Firestore configuration
  firestore_project?: string; // Firestore project (if different from EE project)
  untrusted_samples_collection: string; // Collection name for samples

  // Processing options
  batch_size?: number; // Number of samples to process in each batch
  max_concurrent_updates?: number; // Maximum concurrent sample updates
  retry_failed_samples?: boolean; // Whether to retry failed samples

  // Notification settings
  notify_on_completion?: boolean;
  notification_endpoints?: string[]; // URLs to notify when processing completes
}
