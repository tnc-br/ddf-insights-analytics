# 🗺️ GUIA RÁPIDO - Visualizar Mapas

## ✅ **Solução Rápida**

### Para o seu mapa `6ed0ffa36587c49f5b54`:

**Abra esta URL no navegador:**

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

---

## 🔧 **Como Funciona**

### ❌ URL Errada (não funciona no navegador):

```
gs://timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

### ✅ URL Certa (funciona):

```
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

---

## 🚀 **Métodos para Obter URL**

### 1. **Usar Script Conversor** (Mais Fácil)

```bash
python get_url.py 6ed0ffa36587c49f5b54
```

### 2. **Executar `easy.py`** (Já mostra URL)

```bash
python easy.py 6ed0ffa36587c49f5b54
```

A URL HTTP aparece automaticamente no final!

### 3. **Conversão Manual**

```
Substituir: gs://BUCKET/PASTA/ARQUIVO
Por:        https://storage.googleapis.com/BUCKET/PASTA/ARQUIVO
```

---

## 🔍 **Verificar se Mapa Existe**

### Via navegador:

Abra a URL - se carregar = existe ✅

### Via PowerShell:

```powershell
curl -I https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html
```

- **200 OK** = Arquivo existe e está público ✅
- **403 Forbidden** = Arquivo existe mas não está público ⚠️
- **404 Not Found** = Arquivo não existe ❌

---

## 🛠️ **Se o Mapa Não Carregar**

### Possíveis Causas:

1. **Mapa ainda não foi criado:**

   - Verifique se a execução foi concluída
   - Execute novamente: `python easy.py 6ed0ffa36587c49f5b54`

2. **Bucket não está público:**

   ```bash
   gsutil iam ch allUsers:objectViewer gs://timberid-public-to-internet
   ```

3. **Arquivo em local diferente:**
   - Verifique no Console GCS: https://console.cloud.google.com/storage/browser/timberid-public-to-internet/timberid-maps

---

## 📋 **Exemplos de URLs**

```
# Documento 6ed0ffa36587c49f5b54
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/6ed0ffa36587c49f5b54.html

# Documento 01a6b48a8f43932a8d61
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/01a6b48a8f43932a8d61.html

# Template genérico
https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/SEU_DOC_ID.html
```

---

## 💡 **Dica Profissional**

Depois de executar `python easy.py DOCUMENT_ID`, o sistema já mostra:

```
🔗 Para visualizar o mapa, abra no navegador:
   https://storage.googleapis.com/timberid-public-to-internet/timberid-maps/DOCUMENT_ID.html
```

**Só copiar e colar no navegador!** 🚀
