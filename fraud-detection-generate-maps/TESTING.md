# Testes Locais - Fraud Detection Generate Maps

Sistema completo de testes para desenvolvimento e validação local das funções de geração de mapas, **sem necessidade de autenticação Google Cloud ou Earth Engine**.

---

## 📋 Arquivos de Teste

### **1. Mocks (Simuladores)**

#### `mock_earth_engine.py`

- **Mock do Google Earth Engine**
- Simula: `ee.Image`, `ee.Geometry.Point`, buffers, operações de imagem
- Sem necessidade de autenticação ou credenciais

#### `mock_geemap.py`

- **Mock do geemap**
- Simula: `geemap.Map`, `addLayer`, `to_html`
- Gera arquivos HTML reais para visualização

#### `mock_gcs.py`

- **Mock do Google Cloud Storage**
- Simula: upload de arquivos, buckets, blobs
- Valida arquivos localmente sem enviar para cloud

#### `mock_firestore.py`

- **Mock do Firestore**
- Simula: coleções, documentos, queries
- Permite testar fluxo completo sem banco de dados

---

### **2. Scripts de Teste**

#### `test_local_maps.py` ⭐ (PRINCIPAL)

**Sistema completo de testes com mocks**

**Funções testadas:**

- ✅ `generate_initial_map()` - Criação do mapa base
- ✅ `generate_full_map_and_upload_to_gcs()` - Mapa completo com buffers
- ✅ `generate_html_file_from_map()` - Geração de HTML
- ✅ `upload_map_to_gcs()` - Upload para GCS

**Testes disponíveis:**

1. Geração de mapa inicial
2. Geração de mapa completo
3. Processamento de múltiplas amostras
4. Geração de HTML
5. Coordenadas customizadas

#### `test_integration.py`

**Testes de validação sem mocks**

**Validações testadas:**

- ✅ Coordenadas geográficas (lat/lon)
- ✅ Document IDs (formato, caracteres)
- ✅ Parâmetros de visualização
- ✅ Paths do Google Cloud Storage

---

## 🚀 Como Usar

### **Instalação de Dependências**

```bash
# Não precisa instalar Earth Engine ou Firebase para testes!
# Mocks não requerem autenticação

# Opcional: instalar apenas para ver estrutura
pip install geemap
```

### **Executar Testes Principais**

```bash
cd fraud-detection-generate-maps

# Menu interativo completo
python test_local_maps.py
```

### **Menu Interativo**

```
🗺️  MENU DE TESTES - FRAUD DETECTION GENERATE MAPS
================================================================
1. Executar todos os testes
2. Testar geração de mapa inicial
3. Testar geração de mapa completo
4. Testar múltiplas amostras
5. Testar geração de HTML
6. Testar com coordenadas customizadas
7. Sair
================================================================
```

### **Testes de Validação**

```bash
# Executa testes de validação de dados
python test_integration.py
```

---

## 📊 Exemplos de Uso

### **Teste 1: Mapa Inicial**

```python
from test_local_maps import test_generate_initial_map

# Testa criação do mapa base com dados MapBiomas
base_map, image = test_generate_initial_map()

# Output:
# ✅ Earth Engine inicializado (MOCK)
# 🗺️  Carregando imagem: projects/mapbiomas-workspace/...
# 🎯 Banda selecionada: product_2021
# ✅ Mapa inicial criado com sucesso
```

### **Teste 2: Mapa Completo**

```python
from test_local_maps import test_generate_full_map

# Testa geração completa: buffers + HTML + upload
test_generate_full_map()

# Output:
# 📌 Ponto criado: (-13.0845, -53.3795)
# 📍 Buffer de 1000m criado
# 📍 Buffer de 10000m criado
# 💾 HTML gerado: test_sample_001.html
# ☁️  Upload simulado para GCS
```

### **Teste 3: Múltiplas Amostras**

```python
from test_local_maps import test_multiple_samples

# Processa 3 amostras em sequência
test_multiple_samples()

# Output:
# 📦 Processando: sample_001
# 📦 Processando: sample_002
# 📦 Processando: sample_003
# ✅ TESTE 3 PASSOU!
```

### **Teste 4: Coordenadas Customizadas**

```python
from test_local_maps import generate_full_map_and_upload_to_gcs
from test_local_maps import ee, geemap

# Inicializa
ee.Initialize()
image = ee.Image("projects/mapbiomas-workspace/...")
base_map = geemap.Map()

# Testa com suas próprias coordenadas
generate_full_map_and_upload_to_gcs(
    lat=-15.7942,  # Brasília
    lon=-47.8822,
    land_use_mapbiomas_image=image,
    mapbiomas_land_use_base_map=base_map,
    document_id="brasilia_test"
)
```

---

## 🧪 Validações Testadas

### **Coordenadas Geográficas**

```python
from test_integration import validate_coordinates

# Testa coordenadas
is_valid, message = validate_coordinates(-13.0845, -53.3795)
# ✅ (True, "Coordenadas válidas")

is_valid, message = validate_coordinates(91, 0)
# ❌ (False, "Latitude fora do range válido")
```

### **Document IDs**

```python
from test_integration import validate_document_id

# Testa IDs
is_valid, msg = validate_document_id("sample_001")
# ✅ (True, "Document ID válido")

is_valid, msg = validate_document_id("sample/001")
# ❌ (False, "Document ID contém caractere inválido: '/'")
```

### **Parâmetros de Visualização**

```python
from test_integration import validate_vis_params

vis_params = {
    "min": 1,
    "max": 7,
    "palette": ["#fffbc2", "#09611f", "#4ea376"]
}

is_valid, msg = validate_vis_params(vis_params)
# ✅ (True, "Parâmetros de visualização válidos")
```

### **Paths do GCS**

```python
from test_integration import validate_gcs_path

is_valid, path, msg = validate_gcs_path(
    "timberid-public-to-internet",
    "timberid-maps",
    "sample_001"
)
# ✅ (True, "gs://timberid-public-to-internet/timberid-maps/sample_001.html", "Path GCS válido")
```

---

## 🎯 Casos de Teste

### **Coordenadas Válidas**

- ✅ Brasil: `(-13.0845, -53.3795)`
- ✅ Equador: `(0, 0)`
- ✅ Limites: `(-90, -180)` a `(90, 180)`

### **Coordenadas Inválidas**

- ❌ Latitude > 90: `(91, 0)`
- ❌ Latitude < -90: `(-91, 0)`
- ❌ Longitude > 180: `(0, 181)`
- ❌ Não numérica: `("invalid", 0)`

### **Document IDs Válidos**

- ✅ Hash: `ef8c9fc3c7983d512b71`
- ✅ Com underscore: `sample_001`
- ✅ Com hífen: `test-sample-123`

### **Document IDs Inválidos**

- ❌ Vazio: `""`
- ❌ Muito longo: `"a" * 2000`
- ❌ Com caracteres especiais: `sample/001`, `sample:001`

---

## 📈 Output de Exemplo

### **Teste Completo**

```
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪
TESTE 2: GERAÇÃO DE MAPA COMPLETO
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪

🗺️  GERANDO MAPA INICIAL
============================================================
  🗺️  Carregando imagem: projects/mapbiomas-workspace/...
  🎯 Banda selecionada: product_2021
  ➗ Dividindo por 100
  ⬇️  Aplicando floor()
  🗺️  Mapa geemap criado (MOCK)
  ➕ Camada adicionada: 'Brazil Land Use' (total: 1 camadas)
✅ Mapa inicial criado com sucesso

🌍 GERANDO MAPA COMPLETO PARA: test_sample_001
============================================================
📍 Coordenadas: (-13.0845, -53.3795)
  📌 Ponto criado: (-13.0845, -53.3795)
  📍 Buffer de 1000m criado ao redor de [-53.3795, -13.0845]
  📍 Buffer de 10000m criado ao redor de [-53.3795, -13.0845]
  🎭 Obtendo máscara da imagem
  🌍 Obtendo geometria da imagem
  🔺 Aplicando diferença entre geometrias
  ➕ Camada adicionada: '10 km radius mask' (total: 2 camadas)
  ➕ Camada adicionada: '1 km radius mask' (total: 3 camadas)
  🎯 Mapa centralizado com zoom 11

📝 GERANDO ARQUIVO HTML
============================================================
  💾 HTML gerado: test_sample_001.html
✅ HTML gerado: test_sample_001.html

☁️  UPLOAD PARA GOOGLE CLOUD STORAGE
============================================================
  🪣 Bucket acessado: timberid-public-to-internet (MOCK)
  ☁️  Upload simulado:
     Arquivo: test_sample_001.html
     Tamanho: 1234 bytes
     Destino: gs://timberid-public-to-internet/timberid-maps/test_sample_001.html
✅ Map uploaded to gs://timberid-public-to-internet/timberid-maps/test_sample_001.html

✅ MAPA COMPLETO GERADO E ENVIADO COM SUCESSO!

✅ TESTE 2 PASSOU!
```

---

## 🔧 Personalização

### **Adicionar Novos Testes**

```python
# Em test_local_maps.py

def test_custom_scenario():
    """Seu teste customizado"""
    print("\n🧪 MEU TESTE CUSTOMIZADO")

    # Setup
    ee.Initialize()
    image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
    base_map = generate_initial_map(image)

    # Seu código de teste aqui
    # ...

    print("✅ TESTE PASSOU!")

# Adicionar ao menu
# Na função interactive_menu(), adicionar:
# elif choice == "8":
#     test_custom_scenario()
```

### **Modificar Dados de Teste**

```python
# Em test_local_maps.py, função test_multiple_samples()

samples = [
    {"id": "minha_sample_1", "lat": -10.0, "lon": -50.0},
    {"id": "minha_sample_2", "lat": -20.0, "lon": -45.0},
    # Adicione mais samples aqui
]
```

---

## 🐛 Troubleshooting

### **Erro: ModuleNotFoundError**

```bash
# Se faltar algum mock
python -c "import sys; print(sys.path)"

# Verifique se está no diretório correto
cd fraud-detection-generate-maps
python test_local_maps.py
```

### **HTML não é gerado**

```python
# Verifique permissões de escrita
import os
print(os.getcwd())  # Diretório atual
print(os.access('.', os.W_OK))  # Pode escrever?
```

### **Teste falha inesperadamente**

```bash
# Execute com debug
python -u test_local_maps.py 2>&1 | tee test_output.log

# Verifique o log
cat test_output.log
```

---

## 📚 Estrutura dos Mocks

### **Mock vs Real**

| Componente   | Real                | Mock              | Diferença                  |
| ------------ | ------------------- | ----------------- | -------------------------- |
| Earth Engine | Requer autenticação | Não requer        | Print de operações         |
| geemap       | Gera mapa real EE   | HTML simplificado | Sem tiles do EE            |
| GCS          | Upload real         | Print de upload   | Arquivo não vai para cloud |
| Firestore    | Banco de dados      | Dict em memória   | Dados não persistem        |

### **Vantagens dos Mocks**

- ✅ Sem necessidade de credenciais
- ✅ Execução instantânea (sem API calls)
- ✅ Testes determinísticos
- ✅ Não consome quotas do GCP
- ✅ Funciona offline

### **Limitações dos Mocks**

- ❌ Não valida autenticação real
- ❌ Não testa performance de rede
- ❌ Mapas HTML simplificados
- ❌ Não detecta mudanças na API do GCP

---

## 🎓 Boas Práticas

1. **Execute testes locais antes de deploy**

   ```bash
   python test_local_maps.py
   python test_integration.py
   ```

2. **Valide coordenadas antes de processar**

   ```python
   from test_integration import validate_coordinates
   is_valid, msg = validate_coordinates(lat, lon)
   if not is_valid:
       raise ValueError(msg)
   ```

3. **Teste com múltiplas amostras**

   - Use samples de diferentes regiões do Brasil
   - Teste casos extremos (limites de lat/lon)
   - Valide comportamento em lote

4. **Verifique HTMLs gerados**

   - Abra arquivos HTML no navegador
   - Confirme que camadas estão corretas
   - Valide informações exibidas

5. **Mantenha mocks atualizados**
   - Quando API real mudar, atualize mocks
   - Documente diferenças entre mock e real

---

## 🚀 Próximos Passos

Após validar localmente:

1. **Configure GCP credentials**

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
   ```

2. **Teste com Earth Engine real**

   ```bash
   earthengine authenticate
   ```

3. **Deploy para Cloud Functions**

   ```bash
   gcloud functions deploy fraud-detection-generate-maps \
     --runtime python39 \
     --trigger-topic fraud-detection-generate-maps-daily
   ```

4. **Monitore execução**
   ```bash
   gcloud functions logs read fraud-detection-generate-maps
   ```

---

**Desenvolvido para facilitar desenvolvimento local e CI/CD** 🎯
