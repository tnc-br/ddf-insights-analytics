# ⚠️ SOLUÇÃO - Erro de Permissão Earth Engine

## 🔍 Erro Encontrado

```
❌ Erro: Caller does not have required permission to use project river-sky-386919
Grant the caller the roles/serviceusage.serviceUsageConsumer role
```

## 💡 **Causa**

O **service account** precisa de permissões específicas para usar o Earth Engine no projeto.

---

## ✅ **SOLUÇÃO RÁPIDA** (Recomendada)

### Opção 1: Adicionar Permissões ao Service Account

1. **Acesse o Console IAM:**

   ```
   https://console.cloud.google.com/iam-admin/iam?project=river-sky-386919
   ```

2. **Encontre o service account** (email termina com `@river-sky-386919.iam.gserviceaccount.com`)

3. **Adicionar as seguintes roles:**

   - ✅ `Service Usage Consumer` (roles/serviceusage.serviceUsageConsumer)
   - ✅ `Earth Engine Resource Admin` (roles/earthengine.admin)
   - ✅ `Storage Admin` (roles/storage.admin) - já deve ter

4. **Salvar e aguardar 1-2 minutos** para propagar

5. **Testar novamente:**
   ```bash
   python easy.py 6ed0ffa36587c49f5b54
   ```

---

### Opção 2: Usar Conta Pessoal (Temporário)

Se você não tem permissão para modificar IAM, pode autenticar com sua conta:

```bash
# Autenticar Earth Engine com sua conta Google
earthengine authenticate

# Depois executar o script que use suas credenciais
```

**Criar arquivo:** `easy_personal.py` que use autenticação pessoal.

---

## 🔧 **Permissões Necessárias**

Para o system funcionar completamente, o service account precisa de:

| Permissão     | Role                                      | Para que serve        |
| ------------- | ----------------------------------------- | --------------------- |
| Earth Engine  | `roles/earthengine.admin`                 | Processar mapas no EE |
| Service Usage | `roles/serviceusage.serviceUsageConsumer` | Usar APIs do projeto  |
| Storage       | `roles/storage.admin`                     | Upload para GCS       |
| Firestore     | `roles/datastore.user`                    | Ler documentos        |

---

## 📋 **Comandos gcloud (se tiver acesso)**

```bash
# Obter email do service account
gcloud iam service-accounts list

# Adicionar role Earth Engine
gcloud projects add-iam-policy-binding river-sky-386919 \
    --member="serviceAccount:SEU-SA@river-sky-386919.iam.gserviceaccount.com" \
    --role="roles/earthengine.admin"

# Adicionar role Service Usage
gcloud projects add-iam-policy-binding river-sky-386919 \
    --member="serviceAccount:SEU-SA@river-sky-386919.iam.gserviceaccount.com" \
    --role="roles/serviceusage.serviceUsageConsumer"
```

---

## 🚀 **Alternativa: Usar Cloud Function Existente**

Se não conseguir adicionar permissões, pode usar a Cloud Function que já está configurada:

```bash
# Publicar mensagem no Pub/Sub
gcloud pubsub topics publish fraud-detection-generate-maps-daily \
    --message="6ed0ffa36587c49f5b54"
```

Isso vai triggerar a função que JÁ TEM as permissões corretas!

---

## 🎯 **Próximos Passos**

1. **Pedir ao admin do projeto** para adicionar as permissões
2. **Ou usar a Cloud Function** via Pub/Sub
3. **Ou autenticar com conta pessoal** temporariamente

**Após adicionar permissões, o easy.py vai funcionar perfeitamente!** 🚀
