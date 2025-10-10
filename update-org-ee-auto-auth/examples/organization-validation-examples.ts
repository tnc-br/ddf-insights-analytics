import {
  validateInputOrganization,
  validateProcessedOrganization,
  validateUniqueOrganization,
} from "../validation/organization-validation";
import {
  InputOrganization,
  ProcessedOrganization,
} from "../types/organization";

/**
 * Exemplos de uso das validações de organização
 * Para o sistema update-org-ee-auto-auth
 */

// Exemplo de organização de entrada válida
const validInputOrganization: InputOrganization = {
  org_email: "TechCorp@Example.com", // Será convertido para lowercase
  org_name: "Tech Corp Solutions", // Será convertido para lowercase
  description:
    "Technology solutions provider specializing in environmental monitoring",
  website: "https://www.techcorp.com",
  country: "US",
  contact_person: "John Smith",
  phone: "+15551234567",
  status: "active",
  admins: ["admin@techcorp.com", "manager@techcorp.com"],
  members: ["user1@techcorp.com", "user2@techcorp.com"],
};

// Exemplo de organização processada (após criação automática)
const validProcessedOrganization: ProcessedOrganization = {
  ...validInputOrganization,
  org_email: "techcorp@example.com", // Convertido para lowercase
  org_name: "tech corp solutions", // Convertido para lowercase
  created_at: "2023-09-19T10:30:00.000Z",
  updated_at: "2023-09-19T10:30:00.000Z",
  google_group_created: true,
  ee_folder_created: true,
  ee_folder_path: "projects/river-sky-386919/assets/ee_org/tech corp solutions",
};

// Lista de organizações existentes (para teste de unicidade)
const existingOrganizations = [
  { org_email: "existing@company.com", org_name: "existing company" },
  { org_email: "another@org.com", org_name: "another organization" },
];

console.log("=== Validação de Organização de Entrada ===");
const inputResult = validateInputOrganization(validInputOrganization);
if (inputResult.success) {
  console.log("✅ Organização de entrada válida");
  console.log("Email (normalizado):", inputResult.data.org_email);
  console.log("Nome (normalizado):", inputResult.data.org_name);
  console.log("País:", inputResult.data.country);
  console.log("Admins:", inputResult.data.admins?.length || 0);
} else {
  console.error("❌ Erros de validação:", inputResult.error.issues);
}

console.log("\n=== Validação de Organização Processada ===");
const processedResult = validateProcessedOrganization(
  validProcessedOrganization
);
if (processedResult.success) {
  console.log("✅ Organização processada válida");
  console.log(
    "Google Group criado:",
    processedResult.data.google_group_created
  );
  console.log("Pasta EE criada:", processedResult.data.ee_folder_created);
  console.log("Caminho da pasta:", processedResult.data.ee_folder_path);
} else {
  console.error("❌ Erros de validação:", processedResult.error.issues);
}

console.log("\n=== Validação com Verificação de Unicidade ===");
const uniqueResult = validateUniqueOrganization(
  validInputOrganization,
  existingOrganizations
);
if (uniqueResult.success) {
  console.log("✅ Organização única e válida");
} else {
  console.error("❌ Erro de unicidade:", uniqueResult.error.issues);
}

// Exemplos de validação com dados inválidos
console.log("\n=== Exemplos de Dados Inválidos ===");

// Email inválido
const invalidEmailOrg = {
  ...validInputOrganization,
  org_email: "invalid-email",
};
const emailResult = validateInputOrganization(invalidEmailOrg);
if (!emailResult.success) {
  console.log("❌ Email inválido:", emailResult.error.issues[0].message);
}

// Nome da organização inválido (caracteres especiais)
const invalidNameOrg = {
  ...validInputOrganization,
  org_name: "Invalid@Name#$%",
};
const nameResult = validateInputOrganization(invalidNameOrg);
if (!nameResult.success) {
  console.log("❌ Nome inválido:", nameResult.error.issues[0].message);
}

// Website em formato inválido
const invalidWebsiteOrg = {
  ...validInputOrganization,
  website: "not-a-valid-url",
};
const websiteResult = validateInputOrganization(invalidWebsiteOrg);
if (!websiteResult.success) {
  console.log("❌ Website inválido:", websiteResult.error.issues[0].message);
}

// Código de país inválido
const invalidCountryOrg = {
  ...validInputOrganization,
  country: "INVALID" as any,
};
const countryResult = validateInputOrganization(invalidCountryOrg);
if (!countryResult.success) {
  console.log("❌ País inválido:", countryResult.error.issues[0].message);
}

// Telefone em formato inválido
const invalidPhoneOrg = {
  ...validInputOrganization,
  phone: "123-456-7890", // Formato não internacional
};
const phoneResult = validateInputOrganization(invalidPhoneOrg);
if (!phoneResult.success) {
  console.log("❌ Telefone inválido:", phoneResult.error.issues[0].message);
}

// Teste de unicidade - organização duplicada
const duplicateOrg = {
  ...validInputOrganization,
  org_email: "existing@company.com", // Email já existe
};
const duplicateResult = validateUniqueOrganization(
  duplicateOrg,
  existingOrganizations
);
if (!duplicateResult.success) {
  console.log(
    "❌ Organização duplicada:",
    duplicateResult.error.issues[0].message
  );
}

// Muitos admins
const tooManyAdminsOrg = {
  ...validInputOrganization,
  admins: Array.from({ length: 51 }, (_, i) => `admin${i}@company.com`),
};
const adminsResult = validateInputOrganization(tooManyAdminsOrg);
if (!adminsResult.success) {
  console.log("❌ Muitos admins:", adminsResult.error.issues[0].message);
}

export {
  validInputOrganization,
  validProcessedOrganization,
  existingOrganizations,
};
