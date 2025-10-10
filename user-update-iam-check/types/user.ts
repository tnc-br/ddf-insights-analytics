/**
 * TypeScript types for user IAM management system
 * Based on the user-update-iam-check system
 */

// User roles in the system
export type UserRole = "admin" | "site_admin" | "member";

// Google Workspace member types
export type GoogleMemberType = "USER" | "GROUP" | "DOMAIN";

// Google Workspace member roles
export type GoogleMemberRole = "MEMBER" | "OWNER" | "MANAGER";

// Google Workspace member structure
export interface GoogleWorkspaceMember {
  kind: "member" | "admin";
  email: string;
  role: GoogleMemberRole;
  type: GoogleMemberType;
  id?: string;
  status?: string;
  delivery_settings?: string;
}

// Google Workspace group identifiers
export interface GoogleWorkspaceGroups {
  earthEngineProduction: "earth-engine-developers@timberid.org";
  earthEngineTest: "earth-engine-developers-test@timberid.org";
  gcpOrganizationAdmins: "gcp-organization-admins@timberid.org";
}

// IAM permissions by role
export interface RolePermissions {
  admin: {
    groups: [
      | "earth-engine-developers@timberid.org"
      | "earth-engine-developers-test@timberid.org"
    ];
    access: ["gcp_project", "earth_engine"];
    capabilities: ["full_access"];
  };
  site_admin: {
    groups: ["gcp-organization-admins@timberid.org"];
    access: ["gcp_project", "organization_management"];
    capabilities: ["manage_organization", "gcp_access"];
  };
  member: {
    groups: [
      | "earth-engine-developers@timberid.org"
      | "earth-engine-developers-test@timberid.org"
    ];
    access: ["earth_engine"];
    capabilities: ["earth_engine_assets_only"];
  };
}

// User document structure (Firestore)
export interface User {
  // Required fields
  email: string; // User email address
  role: UserRole; // User role in the system

  // Optional fields
  org?: string; // Organization ID (optional)

  // Optional metadata fields
  created_at?: string; // ISO 8601 date string
  updated_at?: string; // ISO 8601 date string
  created_by?: string; // Email of user who created this user
  status?: "active" | "inactive" | "pending" | "suspended";

  // Optional profile fields
  first_name?: string;
  last_name?: string;
  display_name?: string;
  phone?: string;
  department?: string;
  job_title?: string;

  // Access control metadata
  last_login?: string; // ISO 8601 date string
  login_count?: number; // Number of times user has logged in
  permissions_granted_at?: string; // When IAM permissions were last granted

  // Google Workspace integration
  google_groups?: string[]; // List of Google Groups this user belongs to
  workspace_user_id?: string; // Google Workspace user ID
}

// Input user type (for creation/updates)
export interface InputUser
  extends Omit<
    User,
    | "created_at"
    | "updated_at"
    | "permissions_granted_at"
    | "google_groups"
    | "workspace_user_id"
    | "last_login"
    | "login_count"
  > {
  // Input users should not have system-managed fields
}

// Processed user type (after IAM processing)
export interface ProcessedUser
  extends Required<
    Pick<User, "email" | "role" | "created_at" | "permissions_granted_at">
  > {
  // Additional optional fields
  org?: string;
  updated_at?: string;
  created_by?: string;
  status?: "active" | "inactive" | "pending" | "suspended";
  first_name?: string;
  last_name?: string;
  display_name?: string;
  phone?: string;
  department?: string;
  job_title?: string;
  last_login?: string;
  login_count?: number;
  google_groups?: string[];
  workspace_user_id?: string;
}

// Firestore event types for user changes
export interface FirestoreUserEvent {
  type: "created" | "updated" | "deleted";
  user?: User; // Current user data (for created/updated)
  old_user?: User; // Previous user data (for updated/deleted)
  timestamp: string; // ISO 8601 date string
}

// IAM operation result
export interface IAMOperationResult {
  success: boolean;
  operations: Array<{
    type: "grant" | "revoke";
    group: string;
    user_email: string;
    role: GoogleMemberRole;
    status: "success" | "failed" | "skipped";
    error?: string;
  }>;
  timestamp: string;
}
