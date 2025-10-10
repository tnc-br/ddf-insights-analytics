Explicação do arquivo main.py
Este arquivo implementa uma Cloud Function do Google Cloud que gerencia automaticamente organizações e permissões no Google Earth Engine. Aqui está o que ele faz:

Funcionalidade Principal
O arquivo define uma função update_ee_acl que é ativada automaticamente sempre que há mudanças em documentos do Firestore relacionados a organizações.

Fluxo de Execução

1. Trigger do Firestore
   A função é disparada quando um documento de organização é criado ou atualizado no Firestore
   Extrai informações do evento (collection e document path)
2. Verificação e Criação de Organização (check_org)
   Baixa credenciais do Google Cloud Storage (gadmin_credentials)
   Conecta ao Google Admin SDK para gerenciar grupos do Google Workspace
   Verifica se existe um grupo no Google com o email da organização
   Se não existir:
   Cria um novo grupo no Google Workspace
   Cria uma pasta no Earth Engine (ee_org/{org_name})
   Registra "new org created"
3. Gerenciamento de Assets (get_asset_list)
   Lista recursivamente todos os assets e pastas do Earth Engine
   Navega por:
   FOLDER - Pastas
   IMAGE_COLLECTION - Coleções de imagens
   Outros tipos de assets
   Constrói listas de assets e pastas para processamento
4. Configuração de Permissões (assign_acl)
   Configura ACLs (Access Control Lists) no Earth Engine
   Para assets e pastas que pertencem à organização:
   Adiciona o grupo da organização como writers
   Permite que membros do grupo tenham acesso de escrita
   Evita duplicação de permissões
5. Processamento Principal
   Extrai dados do documento: org_email e org_name
   Executa verificação de organização
   Aplica permissões para assets da organização específica
   Integração com Serviços
   Google Firestore: Trigger e armazenamento de dados
   Google Earth Engine: Gerenciamento de assets geoespaciais
   Google Admin SDK: Criação de grupos no Google Workspace
   Google Cloud Storage: Armazenamento de credenciais
   Campos Esperados no Firestore
   org_email: Email da organização (convertido para lowercase)
   org_name: Nome da organização (convertido para lowercase)
   Estrutura de Assets no Earth Engine
   Propósito
   Este sistema automatiza o onboarding de novas organizações no sistema TimberID, garantindo que:

Grupos do Google sejam criados automaticamente
Pastas dedicadas no Earth Engine sejam provisionadas
Permissões corretas sejam aplicadas automaticamente
Membros da organização tenham acesso apenas aos seus próprios dados
É essencialmente um sistema de provisionamento automático que garante isolamento e segurança entre diferentes organizações que usam a plataforma.
