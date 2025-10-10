Explicação do arquivo main.py e sistema user-update-iam-check
Este sistema implementa uma Cloud Function que gerencia automaticamente permissões IAM (Identity and Access Management) para usuários no Google Workspace e Google Cloud Platform. Aqui está o que ele faz:

Funcionalidade Principal
O arquivo main.py define uma função grant_access que é ativada automaticamente sempre que há mudanças em documentos de usuários no Firestore, gerenciando permissões de acesso baseadas no ciclo de vida do usuário.

Fluxo de Execução

1. Trigger do Firestore
   A função é disparada quando um documento de usuário é criado, atualizado ou deletado no Firestore
   Analisa o tipo de mudança através dos campos value e old_value
2. Detecção do Tipo de Evento

if is_value and not is_old_value:     # Documento CRIADOif is_value and is_old_value:         # Documento ATUALIZADO  if not is_value and is_old_value:     # Documento DELETADO 3. Gerenciamento de Permissões por Evento
📝 Documento CRIADO:

Executa grant_access_new_user() - Concede permissões ao novo usuário
✏️ Documento ATUALIZADO:

Executa ungrant_access_new_user() - Remove permissões antigas
Executa grant_access_deleted_user() - Aplica novas permissões
🗑️ Documento DELETADO:

Executa ungrant_access_deleted_user() - Remove todas as permissões
Classe UserIam (arquivo iam.py)
Configuração de Credenciais (set_service)
Baixa credenciais do Google Cloud Storage
Autentica com Google Admin SDK usando service account
Configura acesso aos grupos do Google Workspace
Concessão de Permissões (grant_access_new_user)
Baseado no role do usuário:

🔵 Role: "admin"

Adiciona ao grupo earth-engine-developers@timberid.org
Acesso total ao projeto GCP
🟡 Role: "site_admin"

Adiciona ao grupo gcp-organization-admins@timberid.org
Gerencia organizações + acesso ao GCP
🟢 Role: "member"

Adiciona ao grupo earth-engine-developers@timberid.org
Acesso apenas aos assets do Earth Engine
🟠 Organização Específica

Se org_id existe, adiciona ao grupo da organização
Acesso restrito aos recursos da organização
Remoção de Permissões (ungrant_access_deleted_user)
Remove o usuário de todos os grupos relevantes
Baseado no role e organização anterior
Limpa permissões completamente
Campos Esperados no Firestore
email: Email do usuário
role: "admin" | "site_admin" | "member"
org: ID da organização (opcional)
Estrutura de Grupos do Google Workspace

📁 Grupos Principais:├── earth-engine-developers@timberid.org (produção)├── earth-engine-developers-test@timberid.org (teste)├── gcp-organization-admins@timberid.org└── {org_email} (grupos específicos por organização)
Integração com Serviços
Google Firestore: Trigger e dados do usuário
Google Admin SDK: Gerenciamento de grupos
Google Cloud Storage: Credenciais seguras
Google Workspace: Controle de acesso organizacional
Ambientes
Produção: gadmin_credentials_prd + grupos @timberid.org
Teste: gadmin_credentials + grupos -test@timberid.org
Propósito
Este sistema automatiza o gerenciamento de acesso garantindo que:

Usuários novos recebem permissões adequadas automaticamente
Mudanças de role são refletidas instantaneamente
Usuários removidos perdem acesso imediatamente
Organizações mantêm isolamento de dados
Segurança é aplicada consistentemente
É essencialmente um sistema de provisionamento automático de IAM que sincroniza mudanças no Firestore com permissões reais no Google Workspace e GCP, garantindo que o acesso seja sempre consistente com o estado atual dos usuários no sistema.
