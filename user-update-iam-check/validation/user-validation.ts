import { z } from "zod";

/**
 * Zod validation schemas for user IAM management system
 * Based on the user-update-iam-check system
 *
 * These schemas enforce:
 * - Email format validation
 * - Role-based access control
 * - Organization membership validation
 * - Phone number format
 * - Date format validation
 * - String length constraints
 */

// Email validation regex (RFC 5322 compliant)
const emailRegex =
  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

// Phone number validation (international format)
const phoneRegex = /^\+?[1-9]\d{1,14}$/;

// ISO 8601 date validation
const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/;

// Name validation (letters, spaces, hyphens, apostrophes)
const nameRegex = /^[a-zA-Z\s\-'\.]+$/;

// Organization ID validation (alphanumeric, hyphens, underscores)
const orgIdRegex = /^[a-zA-Z0-9\-_]+$/;

// Google Workspace member schema
export const GoogleWorkspaceMemberSchema = z.object({
  kind: z.enum(["member", "admin"]),
  email: z.string().regex(emailRegex, "Invalid email format"),
  role: z.enum(["MEMBER", "OWNER", "MANAGER"]),
  type: z.enum(["USER", "GROUP", "DOMAIN"]),
  id: z.string().optional(),
  status: z.string().optional(),
  delivery_settings: z.string().optional(),
});

// Firestore user event schema
export const FirestoreUserEventSchema = z.object({
  type: z.enum(["created", "updated", "deleted"]),
  user: z
    .object({
      email: z.string().regex(emailRegex),
      role: z.enum(["admin", "site_admin", "member"]),
      org: z.string().optional(),
    })
    .optional(),
  old_user: z
    .object({
      email: z.string().regex(emailRegex),
      role: z.enum(["admin", "site_admin", "member"]),
      org: z.string().optional(),
    })
    .optional(),
  timestamp: z.string().regex(isoDateRegex),
});

// IAM operation result schema
export const IAMOperationResultSchema = z.object({
  success: z.boolean(),
  operations: z.array(
    z.object({
      type: z.enum(["grant", "revoke"]),
      group: z.string().min(1),
      user_email: z.string().regex(emailRegex),
      role: z.enum(["MEMBER", "OWNER", "MANAGER"]),
      status: z.enum(["success", "failed", "skipped"]),
      error: z.string().optional(),
    })
  ),
  timestamp: z.string().regex(isoDateRegex),
});

// Base user schema
export const UserSchema = z.object({
  // Required fields
  email: z
    .string()
    .min(1, "Email is required")
    .max(254, "Email too long")
    .regex(emailRegex, "Invalid email format")
    .transform((email) => email.toLowerCase()), // Normalize to lowercase

  role: z.enum(["admin", "site_admin", "member"], {
    errorMap: () => ({
      message: "Role must be 'admin', 'site_admin', or 'member'",
    }),
  }),

  // Optional organization field
  org: z
    .string()
    .min(1, "Organization ID cannot be empty")
    .max(50, "Organization ID too long")
    .regex(
      orgIdRegex,
      "Organization ID can only contain letters, numbers, hyphens, and underscores"
    )
    .optional(),

  // Optional metadata fields
  created_at: z
    .string()
    .regex(
      isoDateRegex,
      "Date must be in ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ)"
    )
    .optional(),
  updated_at: z
    .string()
    .regex(
      isoDateRegex,
      "Date must be in ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ)"
    )
    .optional(),
  created_by: z
    .string()
    .regex(emailRegex, "Creator must be a valid email")
    .optional(),
  status: z
    .enum(["active", "inactive", "pending", "suspended"])
    .default("pending"),

  // Optional profile fields
  first_name: z
    .string()
    .min(1, "First name cannot be empty")
    .max(50, "First name must be less than 50 characters")
    .regex(
      nameRegex,
      "First name can only contain letters, spaces, hyphens, and apostrophes"
    )
    .optional(),
  last_name: z
    .string()
    .min(1, "Last name cannot be empty")
    .max(50, "Last name must be less than 50 characters")
    .regex(
      nameRegex,
      "Last name can only contain letters, spaces, hyphens, and apostrophes"
    )
    .optional(),
  display_name: z
    .string()
    .min(1, "Display name cannot be empty")
    .max(100, "Display name must be less than 100 characters")
    .optional(),
  phone: z
    .string()
    .regex(
      phoneRegex,
      "Invalid phone number format. Use international format (+1234567890)"
    )
    .optional(),
  department: z
    .string()
    .max(100, "Department must be less than 100 characters")
    .optional(),
  job_title: z
    .string()
    .max(100, "Job title must be less than 100 characters")
    .optional(),

  // Access control metadata
  last_login: z
    .string()
    .regex(isoDateRegex, "Last login must be in ISO 8601 format")
    .optional(),
  login_count: z
    .number()
    .int("Login count must be an integer")
    .min(0, "Login count cannot be negative")
    .optional(),
  permissions_granted_at: z
    .string()
    .regex(isoDateRegex, "Permissions granted date must be in ISO 8601 format")
    .optional(),

  // Google Workspace integration
  google_groups: z
    .array(z.string().min(1, "Group name cannot be empty"))
    .max(20, "Too many Google Groups")
    .optional(),
  workspace_user_id: z
    .string()
    .min(1, "Workspace user ID cannot be empty")
    .optional(),
});

// Input user schema (for creation/updates) - excludes system-managed fields
export const InputUserSchema = UserSchema.omit({
  created_at: true,
  updated_at: true,
  permissions_granted_at: true,
  google_groups: true,
  workspace_user_id: true,
  last_login: true,
  login_count: true,
});

// Processed user schema (after IAM processing) - requires system fields
export const ProcessedUserSchema = UserSchema.extend({
  created_at: z.string().regex(isoDateRegex),
  permissions_granted_at: z.string().regex(isoDateRegex),
});

// Role-specific validation
export const validateRolePermissions = (user: unknown) => {
  const parsed = UserSchema.parse(user);

  // Site admins should have an organization
  if (
    parsed.role === "site_admin" &&
    (!parsed.org || parsed.org.trim() === "")
  ) {
    throw new z.ZodError([
      {
        code: "custom",
        message: "Site admins must be assigned to an organization",
        path: ["org"],
      },
    ]);
  }

  return parsed;
};

// Email domain validation for TimberID organization
export const validateTimberIdEmail = (
  user: unknown,
  allowedDomains: string[] = ["timberid.org"]
) => {
  const parsed = UserSchema.parse(user);

  // Check if email domain is allowed for admin/site_admin roles
  if (parsed.role === "admin" || parsed.role === "site_admin") {
    const emailDomain = parsed.email.split("@")[1];
    if (!allowedDomains.includes(emailDomain)) {
      throw new z.ZodError([
        {
          code: "custom",
          message: `Admin and site_admin users must have email from allowed domains: ${allowedDomains.join(
            ", "
          )}`,
          path: ["email"],
        },
      ]);
    }
  }

  return parsed;
};

// Validation functions
export const validateUser = (data: unknown) => {
  return UserSchema.safeParse(data);
};

export const validateInputUser = (data: unknown) => {
  return InputUserSchema.safeParse(data);
};

export const validateProcessedUser = (data: unknown) => {
  return ProcessedUserSchema.safeParse(data);
};

// Comprehensive validation with role and email domain checks
export const validateUserWithRules = (
  data: unknown,
  options: {
    allowedDomains?: string[];
    requireOrgForSiteAdmin?: boolean;
  } = {}
) => {
  const { allowedDomains = ["timberid.org"], requireOrgForSiteAdmin = true } =
    options;

  // First validate basic schema
  const basicValidation = InputUserSchema.safeParse(data);
  if (!basicValidation.success) {
    return basicValidation;
  }

  try {
    let validatedUser = basicValidation.data;

    // Apply role-specific validation
    if (requireOrgForSiteAdmin) {
      validatedUser = validateRolePermissions(validatedUser);
    }

    // Apply email domain validation
    validatedUser = validateTimberIdEmail(validatedUser, allowedDomains);

    return { success: true as const, data: validatedUser };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false as const, error };
    }
    throw error;
  }
};

// Validation for Firestore event data
export const validateFirestoreEvent = (data: unknown) => {
  return FirestoreUserEventSchema.safeParse(data);
};

// Helper function to validate Google Groups for user role
export const validateUserGroups = (
  role: "admin" | "site_admin" | "member",
  environment: "production" | "test" = "production"
) => {
  const expectedGroups: Record<string, string[]> = {
    admin:
      environment === "production"
        ? ["earth-engine-developers@timberid.org"]
        : ["earth-engine-developers-test@timberid.org"],
    site_admin: ["gcp-organization-admins@timberid.org"],
    member:
      environment === "production"
        ? ["earth-engine-developers@timberid.org"]
        : ["earth-engine-developers-test@timberid.org"],
  };

  return z.array(z.enum(expectedGroups[role] as [string, ...string[]]));
};

// Export the inferred types
export type User = z.infer<typeof UserSchema>;
export type InputUser = z.infer<typeof InputUserSchema>;
export type ProcessedUser = z.infer<typeof ProcessedUserSchema>;
export type GoogleWorkspaceMember = z.infer<typeof GoogleWorkspaceMemberSchema>;
export type FirestoreUserEvent = z.infer<typeof FirestoreUserEventSchema>;
export type IAMOperationResult = z.infer<typeof IAMOperationResultSchema>;
