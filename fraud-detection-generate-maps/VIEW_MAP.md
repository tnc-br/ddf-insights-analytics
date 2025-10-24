# 🗺️ Como Visualizar os Mapas Gerados

## 🔗 Conversão de URL

O caminho GCS precisa ser convertido para URL HTTP pública:

### ❌ Formato GCS (não funciona no navegador):

```
gs://timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

### ✅ Formato HTTP Público (funciona):

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

---

## 🚀 Fórmula de Conversão

```
gs://BUCKET/PASTA/ARQUIVO.html
       ↓
https://storage.googleapis.com/BUCKET/PASTA/ARQUIVO.html
```

**Exemplo:**

- GCS: `gs://timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html`
- HTTP: `https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html`

---

## 🔍 Links Diretos dos Seus Mapas

**Para o documento `6ed0ffa36587c49f5b54`:**

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

**Para o documento `01a6b48a8f43932a8d61`:**

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/01a6b48a8f43932a8d61.html
```

**Template genérico:**

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/SEU_DOC_ID.html
```

---

## 🛠️ Verificar se o Bucket é Público

Se o link não funcionar, pode ser que o bucket não esteja configurado como público.

### Opção 1: Via Console GCP

1. Acesse: https://console.cloud.google.com/storage/browser
2. Encontre o bucket `timberid-public-to-internet`
3. Verifique permissões:
   - Click no bucket → Permissions
   - Deve ter `allUsers` com role `Storage Object Viewer`

### Opção 2: Via gcloud CLI

```bash
# Tornar bucket público para leitura
gsutil iam ch allUsers:objectViewer gs://timberid-public-to-internet

# Ou tornar um arquivo específico público
gsutil acl ch -u AllUsers:R gs://timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

---

## 🧪 Testar Acesso

### No navegador:

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

### Via curl (para testar se está público):

```bash
curl -I https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

**Se retornar `200 OK`** = Público ✅  
**Se retornar `403 Forbidden`** = Não público ❌

---

## 📝 Exemplo Prático

Abra esta URL no seu navegador:

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

Se não funcionar, o arquivo pode:

1. Não ter sido criado ainda (verificar no console GCS)
2. Não estar público (ajustar permissões)
3. Estar em outra pasta/bucket

---

## 💡 Dica: Script Automático

Vou criar um script que já mostra a URL HTTP correta!
