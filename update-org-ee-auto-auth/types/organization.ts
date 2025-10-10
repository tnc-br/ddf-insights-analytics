/**
 * TypeScript types for organization management in the Earth Engine Auto Auth system
 * Based on the update-org-ee-auto-auth system
 */

// Google Workspace group structure
export interface GoogleWorkspaceGroup {
  kind: "group";
  email: string;
  name: string;
  description: string;
  id?: string;
  directMembersCount?: string;
  adminCreated?: boolean;
}

// Earth Engine asset types
export type EarthEngineAssetType =
  | "FOLDER"
  | "IMAGE_COLLECTION"
  | "IMAGE"
  | "TABLE"
  | "ALGORITHM";

// Earth Engine asset structure
export interface EarthEngineAsset {
  name: string;
  type: EarthEngineAssetType;
  startTime?: string;
  endTime?: string;
  updateTime?: string;
  sizeBytes?: string;
  properties?: Record<string, any>;
}

// ACL (Access Control List) structure for Earth Engine
export interface EarthEngineACL {
  owners?: string[];
  readers?: string[];
  writers?: string[];
  all_users_can_read?: boolean;
}

// Organization document structure (Firestore)
export interface Organization {
  // Required fields
  org_email: string; // Organization email (will be converted to lowercase)
  org_name: string; // Organization name (will be converted to lowercase)

  // Optional metadata fields
  created_at?: string; // ISO 8601 date string
  updated_at?: string; // ISO 8601 date string
  created_by?: string; // User who created the organization
  status?: "active" | "inactive" | "pending";

  // Optional descriptive fields
  description?: string;
  website?: string;
  country?: string;
  contact_person?: string;
  phone?: string;

  // System fields (managed automatically)
  google_group_created?: boolean;
  ee_folder_created?: boolean;
  ee_folder_path?: string;

  // Access control
  admins?: string[]; // List of admin user emails
  members?: string[]; // List of member user emails
}

// Input organization type (for creation/updates)
export interface InputOrganization
  extends Omit<
    Organization,
    | "google_group_created"
    | "ee_folder_created"
    | "ee_folder_path"
    | "created_at"
    | "updated_at"
  > {
  // Input organizations should not have system-managed fields
}

// Processed organization type (after system processing)
export interface ProcessedOrganization
  extends Required<
    Pick<
      Organization,
      | "org_email"
      | "org_name"
      | "created_at"
      | "google_group_created"
      | "ee_folder_created"
      | "ee_folder_path"
    >
  > {
  // Additional optional fields
  updated_at?: string;
  created_by?: string;
  status?: "active" | "inactive" | "pending";
  description?: string;
  website?: string;
  country?: string;
  contact_person?: string;
  phone?: string;
  admins?: string[];
  members?: string[];
}
