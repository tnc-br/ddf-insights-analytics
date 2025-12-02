import { z } from "zod";

/**
 * Zod validation schemas for organization management in Earth Engine Auto Auth system
 * Based on the update-org-ee-auto-auth system
 *
 * These schemas enforce:
 * - Email format validation
 * - Organization name constraints
 * - URL validation for websites
 * - Phone number format
 * - Country code validation
 * - Date format validation
 */

// Email validation regex (RFC 5322 compliant)
const emailRegex =
  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

// Organization name validation (alphanumeric, spaces, hyphens, underscores)
const orgNameRegex = /^[a-zA-Z0-9\s\-_\.]+$/;

// Phone number validation (international format)
const phoneRegex = /^\+?[1-9]\d{1,14}$/;

// ISO 8601 date validation
const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/;

// URL validation (more permissive than default)
const urlRegex =
  /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/;

// Country codes (ISO 3166-1 alpha-2) - most common ones
const countryCodes = [
  "AD",
  "AE",
  "AF",
  "AG",
  "AI",
  "AL",
  "AM",
  "AO",
  "AQ",
  "AR",
  "AS",
  "AT",
  "AU",
  "AW",
  "AX",
  "AZ",
  "BA",
  "BB",
  "BD",
  "BE",
  "BF",
  "BG",
  "BH",
  "BI",
  "BJ",
  "BL",
  "BM",
  "BN",
  "BO",
  "BQ",
  "BR",
  "BS",
  "BT",
  "BV",
  "BW",
  "BY",
  "BZ",
  "CA",
  "CC",
  "CD",
  "CF",
  "CG",
  "CH",
  "CI",
  "CK",
  "CL",
  "CM",
  "CN",
  "CO",
  "CR",
  "CU",
  "CV",
  "CW",
  "CX",
  "CY",
  "CZ",
  "DE",
  "DJ",
  "DK",
  "DM",
  "DO",
  "DZ",
  "EC",
  "EE",
  "EG",
  "EH",
  "ER",
  "ES",
  "ET",
  "FI",
  "FJ",
  "FK",
  "FM",
  "FO",
  "FR",
  "GA",
  "GB",
  "GD",
  "GE",
  "GF",
  "GG",
  "GH",
  "GI",
  "GL",
  "GM",
  "GN",
  "GP",
  "GQ",
  "GR",
  "GS",
  "GT",
  "GU",
  "GW",
  "GY",
  "HK",
  "HM",
  "HN",
  "HR",
  "HT",
  "HU",
  "ID",
  "IE",
  "IL",
  "IM",
  "IN",
  "IO",
  "IQ",
  "IR",
  "IS",
  "IT",
  "JE",
  "JM",
  "JO",
  "JP",
  "KE",
  "KG",
  "KH",
  "KI",
  "KM",
  "KN",
  "KP",
  "KR",
  "KW",
  "KY",
  "KZ",
  "LA",
  "LB",
  "LC",
  "LI",
  "LK",
  "LR",
  "LS",
  "LT",
  "LU",
  "LV",
  "LY",
  "MA",
  "MC",
  "MD",
  "ME",
  "MF",
  "MG",
  "MH",
  "MK",
  "ML",
  "MM",
  "MN",
  "MO",
  "MP",
  "MQ",
  "MR",
  "MS",
  "MT",
  "MU",
  "MV",
  "MW",
  "MX",
  "MY",
  "MZ",
  "NA",
  "NC",
  "NE",
  "NF",
  "NG",
  "NI",
  "NL",
  "NO",
  "NP",
  "NR",
  "NU",
  "NZ",
  "OM",
  "PA",
  "PE",
  "PF",
  "PG",
  "PH",
  "PK",
  "PL",
  "PM",
  "PN",
  "PR",
  "PS",
  "PT",
  "PW",
  "PY",
  "QA",
  "RE",
  "RO",
  "RS",
  "RU",
  "RW",
  "SA",
  "SB",
  "SC",
  "SD",
  "SE",
  "SG",
  "SH",
  "SI",
  "SJ",
  "SK",
  "SL",
  "SM",
  "SN",
  "SO",
  "SR",
  "SS",
  "ST",
  "SV",
  "SX",
  "SY",
  "SZ",
  "TC",
  "TD",
  "TF",
  "TG",
  "TH",
  "TJ",
  "TK",
  "TL",
  "TM",
  "TN",
  "TO",
  "TR",
  "TT",
  "TV",
  "TW",
  "TZ",
  "UA",
  "UG",
  "UM",
  "US",
  "UY",
  "UZ",
  "VA",
  "VC",
  "VE",
  "VG",
  "VI",
  "VN",
  "VU",
  "WF",
  "WS",
  "YE",
  "YT",
  "ZA",
  "ZM",
  "ZW",
] as const;

// Google Workspace group schema
export const GoogleWorkspaceGroupSchema = z.object({
  kind: z.literal("group"),
  email: z.string().regex(emailRegex, "Invalid email format"),
  name: z.string().min(1).max(200),
  description: z.string().max(500),
  id: z.string().optional(),
  directMembersCount: z.string().optional(),
  adminCreated: z.boolean().optional(),
});

// Earth Engine asset schema
export const EarthEngineAssetSchema = z.object({
  name: z.string().min(1, "Asset name is required"),
  type: z.enum(["FOLDER", "IMAGE_COLLECTION", "IMAGE", "TABLE", "ALGORITHM"]),
  startTime: z.string().regex(isoDateRegex).optional(),
  endTime: z.string().regex(isoDateRegex).optional(),
  updateTime: z.string().regex(isoDateRegex).optional(),
  sizeBytes: z.string().optional(),
  properties: z.record(z.any()).optional(),
});

// Earth Engine ACL schema
export const EarthEngineACLSchema = z.object({
  owners: z.array(z.string().regex(emailRegex)).optional(),
  readers: z.array(z.string().regex(emailRegex)).optional(),
  writers: z.array(z.string().regex(emailRegex)).optional(),
  all_users_can_read: z.boolean().optional(),
});

// Base organization schema
export const OrganizationSchema = z.object({
  // Required fields
  org_email: z
    .string()
    .min(1, "Organization email is required")
    .max(254, "Email too long")
    .regex(emailRegex, "Invalid email format")
    .transform((email) => email.toLowerCase()), // Automatically convert to lowercase

  org_name: z
    .string()
    .min(1, "Organization name is required")
    .max(100, "Organization name must be less than 100 characters")
    .regex(
      orgNameRegex,
      "Organization name can only contain letters, numbers, spaces, hyphens, underscores, and dots"
    )
    .transform((name) => name.toLowerCase()), // Automatically convert to lowercase

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
  status: z.enum(["active", "inactive", "pending"]).default("pending"),

  // Optional descriptive fields
  description: z
    .string()
    .max(1000, "Description must be less than 1000 characters")
    .optional(),
  website: z.string().regex(urlRegex, "Invalid website URL format").optional(),
  country: z
    .enum(countryCodes, {
      errorMap: () => ({
        message:
          "Invalid country code. Must be ISO 3166-1 alpha-2 format (e.g., US, BR, DE)",
      }),
    })
    .optional(),
  contact_person: z
    .string()
    .min(1, "Contact person name cannot be empty")
    .max(100, "Contact person name must be less than 100 characters")
    .optional(),
  phone: z
    .string()
    .regex(
      phoneRegex,
      "Invalid phone number format. Use international format (+1234567890)"
    )
    .optional(),

  // System fields (managed automatically)
  google_group_created: z.boolean().default(false),
  ee_folder_created: z.boolean().default(false),
  ee_folder_path: z
    .string()
    .min(1, "EE folder path cannot be empty")
    .optional(),

  // Access control
  admins: z
    .array(z.string().regex(emailRegex, "Admin emails must be valid"))
    .max(50, "Too many admins")
    .optional(),
  members: z
    .array(z.string().regex(emailRegex, "Member emails must be valid"))
    .max(1000, "Too many members")
    .optional(),
});

// Input organization schema (for creation/updates) - excludes system-managed fields
export const InputOrganizationSchema = OrganizationSchema.omit({
  google_group_created: true,
  ee_folder_created: true,
  ee_folder_path: true,
  created_at: true,
  updated_at: true,
});

// Processed organization schema (after system processing) - requires system fields
export const ProcessedOrganizationSchema = OrganizationSchema.extend({
  created_at: z.string().regex(isoDateRegex),
  google_group_created: z.boolean(),
  ee_folder_created: z.boolean(),
  ee_folder_path: z.string().min(1),
});

// Custom validation for organization uniqueness
export const validateOrganizationUniqueness = (
  org: unknown,
  existingOrgs: Array<{ org_email: string; org_name: string }> = []
) => {
  const parsed = OrganizationSchema.parse(org);

  // Check for duplicate email
  const emailExists = existingOrgs.some(
    (existing) =>
      existing.org_email.toLowerCase() === parsed.org_email.toLowerCase()
  );

  if (emailExists) {
    throw new z.ZodError([
      {
        code: "custom",
        message: "Organization email already exists",
        path: ["org_email"],
      },
    ]);
  }

  // Check for duplicate name
  const nameExists = existingOrgs.some(
    (existing) =>
      existing.org_name.toLowerCase() === parsed.org_name.toLowerCase()
  );

  if (nameExists) {
    throw new z.ZodError([
      {
        code: "custom",
        message: "Organization name already exists",
        path: ["org_name"],
      },
    ]);
  }

  return parsed;
};

// Validation functions
export const validateOrganization = (data: unknown) => {
  return OrganizationSchema.safeParse(data);
};

export const validateInputOrganization = (data: unknown) => {
  return InputOrganizationSchema.safeParse(data);
};

export const validateProcessedOrganization = (data: unknown) => {
  return ProcessedOrganizationSchema.safeParse(data);
};

// Validation with uniqueness check
export const validateUniqueOrganization = (
  data: unknown,
  existingOrgs: Array<{ org_email: string; org_name: string }> = []
) => {
  // First validate basic schema
  const basicValidation = InputOrganizationSchema.safeParse(data);
  if (!basicValidation.success) {
    return basicValidation;
  }

  // Then apply uniqueness validation
  try {
    const validatedOrg = validateOrganizationUniqueness(data, existingOrgs);
    return { success: true as const, data: validatedOrg };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false as const, error };
    }
    throw error;
  }
};

// Export the inferred types
export type Organization = z.infer<typeof OrganizationSchema>;
export type InputOrganization = z.infer<typeof InputOrganizationSchema>;
export type ProcessedOrganization = z.infer<typeof ProcessedOrganizationSchema>;
export type GoogleWorkspaceGroup = z.infer<typeof GoogleWorkspaceGroupSchema>;
export type EarthEngineAsset = z.infer<typeof EarthEngineAssetSchema>;
export type EarthEngineACL = z.infer<typeof EarthEngineACLSchema>;
