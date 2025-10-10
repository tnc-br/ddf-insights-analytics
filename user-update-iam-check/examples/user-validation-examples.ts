import {
  validateInputUser,
  validateProcessedUser,
  validateUserWithRules,
  validateFirestoreEvent,
  validateUserGroups,
} from "../validation/user-validation";
import { InputUser, ProcessedUser, FirestoreUserEvent } from "../types/user";

/**
 * Exemplos de uso das validações de usuário
 * Para o sistema user-update-iam-check
 */

// Exemplo de usuário de entrada válido
const validInputUser: InputUser = {
  email: "john.smith@timberid.org",
  role: "site_admin",
  org: "tech-corp-123",
  first_name: "John",
  last_name: "Smith",
  display_name: "John Smith",
  phone: "+15551234567",
  department: "Engineering",
  job_title: "Senior Developer",
  status: "active",
};

// Exemplo de usuário admin
const validAdminUser: InputUser = {
  email: "admin@timberid.org",
  role: "admin",
  first_name: "System",
  last_name: "Administrator",
  display_name: "System Admin",
  status: "active",
};

// Exemplo de usuário member
const validMemberUser: InputUser = {
  email: "member@company.com",
  role: "member",
  org: "external-org-456",
  first_name: "Jane",
  last_name: "Doe",
  status: "active",
};

// Exemplo de usuário processado (após criação do IAM)
const validProcessedUser: ProcessedUser = {
  ...validInputUser,
  created_at: "2023-09-19T10:30:00.000Z",
  updated_at: "2023-09-19T10:30:00.000Z",
  permissions_granted_at: "2023-09-19T10:30:15.000Z",
  google_groups: [
    "gcp-organization-admins@timberid.org",
    "tech-corp-123@timberid.org",
  ],
  workspace_user_id: "1234567890",
  login_count: 0,
};

// Exemplo de evento do Firestore
const validFirestoreEvent: FirestoreUserEvent = {
  type: "created",
  user: {
    email: "new.user@timberid.org",
    role: "member",
    org: "sample-org",
  },
  timestamp: "2023-09-19T10:30:00.000Z",
};

console.log("=== Validação de Usuário de Entrada ===");
const inputResult = validateInputUser(validInputUser);
if (inputResult.success) {
  console.log("✅ Usuário de entrada válido");
  console.log("Email (normalizado):", inputResult.data.email);
  console.log("Role:", inputResult.data.role);
  console.log("Organização:", inputResult.data.org);
} else {
  console.error("❌ Erros de validação:", inputResult.error.issues);
}

console.log("\n=== Validação de Usuário Admin ===");
const adminResult = validateInputUser(validAdminUser);
if (adminResult.success) {
  console.log("✅ Usuário admin válido");
  console.log("Role:", adminResult.data.role);
  console.log(
    "Organização necessária:",
    adminResult.data.org || "Não especificada"
  );
} else {
  console.error("❌ Erros de validação:", adminResult.error.issues);
}

console.log("\n=== Validação de Usuário Member ===");
const memberResult = validateInputUser(validMemberUser);
if (memberResult.success) {
  console.log("✅ Usuário member válido");
  console.log("Email:", memberResult.data.email);
  console.log("Organização:", memberResult.data.org);
} else {
  console.error("❌ Erros de validação:", memberResult.error.issues);
}

console.log("\n=== Validação de Usuário Processado ===");
const processedResult = validateProcessedUser(validProcessedUser);
if (processedResult.success) {
  console.log("✅ Usuário processado válido");
  console.log(
    "Permissões concedidas em:",
    processedResult.data.permissions_granted_at
  );
  console.log(
    "Grupos do Google:",
    processedResult.data.google_groups?.length || 0
  );
} else {
  console.error("❌ Erros de validação:", processedResult.error.issues);
}

console.log("\n=== Validação com Regras Específicas ===");
const rulesResult = validateUserWithRules(validInputUser, {
  allowedDomains: ["timberid.org", "company.com"],
  requireOrgForSiteAdmin: true,
});
if (rulesResult.success) {
  console.log("✅ Usuário válido com todas as regras");
} else {
  console.error("❌ Erro nas regras:", rulesResult.error.issues);
}

console.log("\n=== Validação de Evento do Firestore ===");
const eventResult = validateFirestoreEvent(validFirestoreEvent);
if (eventResult.success) {
  console.log("✅ Evento do Firestore válido");
  console.log("Tipo:", eventResult.data.type);
  console.log("Email do usuário:", eventResult.data.user?.email);
} else {
  console.error("❌ Erros de validação:", eventResult.error.issues);
}

// Exemplos de validação com dados inválidos
console.log("\n=== Exemplos de Dados Inválidos ===");

// Email inválido
const invalidEmailUser = {
  ...validInputUser,
  email: "invalid-email",
};
const emailResult = validateInputUser(invalidEmailUser);
if (!emailResult.success) {
  console.log("❌ Email inválido:", emailResult.error.issues[0].message);
}

// Role inválido
const invalidRoleUser = {
  ...validInputUser,
  role: "invalid_role" as any,
};
const roleResult = validateInputUser(invalidRoleUser);
if (!roleResult.success) {
  console.log("❌ Role inválido:", roleResult.error.issues[0].message);
}

// Site admin sem organização
const siteAdminNoOrg = {
  email: "admin@timberid.org",
  role: "site_admin" as const,
  // org: undefined - faltando organização
};
const orgResult = validateUserWithRules(siteAdminNoOrg);
if (!orgResult.success) {
  console.log(
    "❌ Site admin sem organização:",
    orgResult.error.issues[0].message
  );
}

// Email de domínio não permitido para admin
const invalidDomainAdmin = {
  email: "admin@unauthorized.com",
  role: "admin" as const,
};
const domainResult = validateUserWithRules(invalidDomainAdmin);
if (!domainResult.success) {
  console.log(
    "❌ Domínio não permitido para admin:",
    domainResult.error.issues[0].message
  );
}

// Nome com caracteres inválidos
const invalidNameUser = {
  ...validInputUser,
  first_name: "John123@#",
};
const nameResult = validateInputUser(invalidNameUser);
if (!nameResult.success) {
  console.log("❌ Nome inválido:", nameResult.error.issues[0].message);
}

// Telefone em formato inválido
const invalidPhoneUser = {
  ...validInputUser,
  phone: "123-456-7890", // Formato não internacional
};
const phoneResult = validateInputUser(invalidPhoneUser);
if (!phoneResult.success) {
  console.log("❌ Telefone inválido:", phoneResult.error.issues[0].message);
}

// Validação de grupos por role
console.log("\n=== Validação de Grupos por Role ===");
const adminGroups = validateUserGroups("admin", "production");
const testAdminGroups = validateUserGroups("admin", "test");
const siteAdminGroups = validateUserGroups("site_admin");

console.log(
  "Grupos para admin (produção):",
  adminGroups._def.type.options[0]._def.value
);
console.log(
  "Grupos para admin (teste):",
  testAdminGroups._def.type.options[0]._def.value
);
console.log(
  "Grupos para site_admin:",
  siteAdminGroups._def.type.options[0]._def.value
);

export {
  validInputUser,
  validAdminUser,
  validMemberUser,
  validProcessedUser,
  validFirestoreEvent,
};
