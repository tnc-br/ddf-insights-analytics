# 🗺️ Comandos Disponíveis - TimberID Mapas Isotópicos

Referência completa de comandos para geração e análise de mapas de probabilidade isotópica.

---

## 📋 Índice

1. [Ambiente Virtual Python](#ambiente-virtual-python)
2. [Geração de Mapas Local](#geração-de-mapas-local)
3. [Geração de Mapas Cloud](#geração-de-mapas-cloud)
4. [Utilitários e Testes](#utilitários-e-testes)
5. [Estrutura de Arquivos](#estrutura-de-arquivos)

---

## 🐍 Ambiente Virtual Python

### Ativar Ambiente Virtual

```bash
# Ativar o ambiente virtual do projeto
source ~/job/Be220/ddf-insights-analytics/timberid-env/bin/activate

# Verificar se Python está correto
which python3
python3 --version  # Deve mostrar Python 3.12.x
```

### Desativar Ambiente Virtual

```bash
deactivate
```

### Instalar/Atualizar Dependências

```bash
cd fraud-detection-generate-maps
pip install -r requirements.txt
```

**Dependências principais:**

- `rasterio` - Processamento de rasters GeoTIFF
- `geopandas` - Manipulação de shapefiles
- `scipy` - Cálculos estatísticos (Normal univariada/multivariada)
- `matplotlib` - Geração de PDFs com visualizações
- `firebase-admin` - Integração com Firestore
- `google-cloud-firestore` - Cliente Firestore

---

## 🗺️ Geração de Mapas Local

### `create_mapa_local.py` - Gerador Standalone Completo

**Descrição:** Script principal para gerar mapas de probabilidade isotópica usando isoscapes locais.

#### **Uso Básico:**

```bash
# Usar documento padrão (6ed0ffa36587c49f5b54)
python3 create_mapa_local.py

# Usar documento específico do Firebase
python3 create_mapa_local.py abc123def456

# Usar valor isotópico manual (modo teste)
python3 create_mapa_local.py test_sample 26.5

# Documento Firebase + valor manual (override)
python3 create_mapa_local.py abc123def456 -12.5
```

#### **Funcionalidades:**

✅ **Conexão Firebase** - Busca documentos em 3 coleções (`trusted_samples`, `untrusted_samples`, `unknown_samples`)  
✅ **Extração Inteligente** - Prioriza `d18O_cel` (média de listas), fallback para `isotopes.O18`  
✅ **Isoscape Alta Resolução** - Usa `oxygen_18_detailed.tiff` (1024×1024 pixels, ~4.3km/pixel)  
✅ **Máscara Geográfica** - Aplica shapefile do Brasil (IBGE 2020) automaticamente  
✅ **Modo Offline** - Funciona sem Firebase usando dados de teste  
✅ **Output Completo** - Gera GeoTIFF + PDF com visualização  
✅ **Abertura Automática** - Abre PDF no navegador/visualizador padrão

#### **Saída Gerada:**

```
output_maps/
└── {DOC_ID}_{TIMESTAMP}/
    ├── prob_{DOC_ID}.tif           # Raster de probabilidade (GeoTIFF)
    └── output_pdRaster.pdf         # Visualização colorida
```

#### **Exemplos de Uso:**

```bash
# Gerar mapa para amostra real do Firebase
python3 create_mapa_local.py 6ed0ffa36587c49f5b54

# Teste com valor isotópico conhecido
python3 create_mapa_local.py test_validation 26.5

# Ajuda
python3 create_mapa_local.py --help
```

---

## ☁️ Geração de Mapas Cloud

### `create_mapa_cloud.py` - Executor Pub/Sub com Espera

**Descrição:** Publica mensagem no Google Pub/Sub para disparar Cloud Function e aguarda processamento.

#### **Uso:**

```bash
# Publicar no Pub/Sub e aguardar 2 minutos
python3 create_mapa_cloud.py 6ed0ffa36587c49f5b54
```

#### **Funcionalidades:**

✅ **Publicação Pub/Sub** - Dispara Cloud Function `fraud-detection-generate-maps`  
✅ **Aguarda Processamento** - Espera 2 minutos e verifica status a cada 30s  
✅ **Busca URL** - Consulta Firestore para obter `map_url` gerado  
✅ **Feedback Visual** - Mostra progresso e tempo estimado de conclusão  
✅ **Fallback** - Mostra URL padrão se timeout ocorrer

#### **Fluxo de Execução:**

```
1. Publica mensagem no Pub/Sub
   ↓
2. Cloud Function processa (Earth Engine + MapBiomas)
   ↓
3. Script aguarda e verifica status a cada 30s
   ↓
4. Mostra URL do mapa HTML quando pronto
```

#### **Configuração:**

- **Project ID:** `river-sky-386919`
- **Topic:** `fraud-detection-generate-maps-daily`
- **Timeout:** 120 segundos (2 minutos)
- **Verificações:** 30s, 60s, 90s, 120s

#### **Exemplo de Saída:**

```
🗺️  GERANDO MAPA: 6ed0ffa36587c49f5b54
🔥 Publicando mensagem no Pub/Sub via gcloud...
✅ Mensagem publicada!

⏰ AGUARDANDO PROCESSAMENTO...
   🕐 Hora atual: 11:25:30
   ⏳ Estimativa de conclusão: 11:27:30

⏳ Aguardando 30s...
   ⏳ Ainda processando... (verificado aos 30s)

🎉 MAPA PRONTO!
📊 INFORMAÇÕES:
   URL: https://storage.googleapis.com/.../6ed0ffa36587c49f5b54.html
   Atualizado em: 2025-11-07 11:27:15
```

---

## 🛠️ Utilitários e Testes

### `generate_new_mapa.py` - Biblioteca Core

**Descrição:** Biblioteca com implementações de algoritmos isotópicos (importada por outros scripts).

**Funções principais:**

- `pd_raster()` - Função principal (dispatcher single/multi-isoscape)
- `_pd_raster_default()` - Implementação single isoscape (Normal univariada)
- `_pd_raster_iso_stack()` - Implementação multi-isoscape (Normal multivariada)
- `check_unknown()` - Validação de dados de amostras
- `check_mask()` - Validação de máscaras geográficas
- `compare_geom()` - Comparação de geometrias de rasters

**Não executar diretamente** - É uma biblioteca importada por `create_mapa_local.py`.

### `create_example_isoscapes.py` - Gerador de Isoscapes de Teste

**Descrição:** Cria isoscapes sintéticos para testes (NÃO usar em produção).

```bash
python3 create_example_isoscapes.py
```

**Gera:**

- `isoscapes/oxygen_18_brazil.tif` - δ18O sintético (400×400 pixels)
- `isoscapes/carbon_13_brazil.tif` - δ13C sintético
- `isoscapes/nitrogen_15_brazil.tif` - δ15N sintético

⚠️ **Apenas para testes** - Usa gradientes artificiais, não dados reais.

### `create_brazil_mask.py` - Criador de Máscaras

**Descrição:** Cria shapefile do Brasil a partir de dados IBGE.

```bash
python3 create_brazil_mask.py
```

**Gera:**

- `shapefiles/brazil_simplified.shp` - Contorno do Brasil simplificado

---

## 📁 Estrutura de Arquivos

### **Isoscapes (Mapas de Referência Isotópica)**

```
isoscapes/
├── oxygen_18_detailed.tiff    # 🎯 PRINCIPAL (1024×1024, ~4.3km/pixel)
├── carbon_13_brazil.tif       # Carbono-13 (400×400, reserva)
└── nitrogen_15_brazil.tif     # Nitrogênio-15 (400×400, reserva)
```

### **Shapefiles (Máscaras Geográficas)**

```
shapefiles/
├── bra_admbnda_adm0_ibge_2020.shp  # 🎯 PRINCIPAL (contorno nacional)
├── bra_admbnda_adm1_ibge_2020.shp  # Estados (fallback)
└── [arquivos auxiliares .prj, .dbf, .shx, etc.]
```

### **Outputs Gerados**

```
output_maps/
└── {DOC_ID}_{TIMESTAMP}/
    ├── prob_{DOC_ID}.tif           # Raster de probabilidade
    └── output_pdRaster.pdf         # Visualização em PDF
```

---

## 🔬 Comparação: Local vs Cloud

| Aspecto             | `create_mapa_local.py`       | `create_mapa_cloud.py`       |
| ------------------- | ---------------------------- | ---------------------------- |
| **Execução**        | Local (sua máquina)          | Cloud Function (GCP)         |
| **Isoscapes**       | Arquivos locais (.tiff)      | Earth Engine assets          |
| **Dados**           | MapBiomas local/Earth Engine | Earth Engine + MapBiomas API |
| **Velocidade**      | Rápido (segundos)            | Médio (1-2 minutos)          |
| **Output**          | GeoTIFF + PDF                | HTML interativo (geemap)     |
| **Firestore**       | Lê apenas                    | Lê e escreve (`map_url`)     |
| **Dependências**    | rasterio, geopandas          | Earth Engine, geemap         |
| **Uso recomendado** | Testes, desenvolvimento      | Produção, batch processing   |

---

## 🎯 Workflows Comuns

### **1. Desenvolvimento/Teste Rápido**

```bash
# Ativar ambiente
source ~/job/Be220/ddf-insights-analytics/timberid-env/bin/activate

# Gerar mapa local
cd fraud-detection-generate-maps
python3 create_mapa_local.py test_validation 26.5

# Ver resultado
xdg-open output_maps/test_validation_*/output_pdRaster.pdf
```

### **2. Análise de Amostra Real**

```bash
# Com documento do Firebase
python3 create_mapa_local.py 6ed0ffa36587c49f5b54

# Output automático em output_maps/
```

### **3. Processamento em Produção (Cloud)**

```bash
# Disparar Cloud Function via Pub/Sub
python3 create_mapa_cloud.py 6ed0ffa36587c49f5b54

# Aguarda e mostra URL do mapa HTML
```

### **4. Batch Processing (Múltiplas Amostras)**

```bash
# Loop para processar várias amostras
for doc_id in abc123 def456 ghi789; do
    python3 create_mapa_local.py $doc_id
done
```

---

## ⚙️ Configurações e Variáveis

### **Credenciais Firebase**

O sistema procura credenciais em:

1. `fraud-detection-generate-maps/serviceAccountKey.json`
2. `fraud-detection-generate-maps/../serviceAccountKey.json`

### **Coleções Firestore**

Ordem de busca de documentos:

1. `trusted_samples`
2. `untrusted_samples`
3. `unknown_samples`

### **Campos Isotópicos Reconhecidos**

Prioridade de extração de δ18O:

1. `d18O_cel` (média de lista, compatível com sistema principal)
2. `isotopes.O18` (fallback)
3. Campos alternativos: `O18`, `d18O`, `oxygen_18`

---

## 🐛 Troubleshooting

### **Erro: "Arquivo não encontrado: isoscapes/oxygen_18_detailed.tiff"**

```bash
# Verificar se arquivo existe
ls -lh isoscapes/oxygen_18_detailed.tiff

# Se não existir, arquivo foi movido ou deletado
# Restaurar do git ou obter isoscape válido
```

### **Erro: "Mask file not found"**

```bash
# Verificar shapefiles disponíveis
ls -lh shapefiles/bra_admbnda_adm0_ibge_2020.shp

# Sistema funciona sem máscara (processa mundo todo)
# Mas é mais lento e menos preciso
```

### **PDF não abre automaticamente**

```bash
# Abrir manualmente
xdg-open output_maps/{DOC_ID}_{TIMESTAMP}/output_pdRaster.pdf  # Linux
open output_maps/{DOC_ID}_{TIMESTAMP}/output_pdRaster.pdf      # macOS
start output_maps/{DOC_ID}_{TIMESTAMP}/output_pdRaster.pdf     # Windows
```

### **Erro: "Firebase não disponível"**

```bash
# Verificar credenciais
ls -lh serviceAccountKey.json ../serviceAccountKey.json

# Usar modo offline com valor manual
python3 create_mapa_local.py test_sample 26.5
```

---

## 📚 Referências Técnicas

### **Fórmulas Estatísticas**

**Single Isoscape (Normal Univariada):**

```
P(origem no pixel i) = (1/√(2πσᵢ²)) × exp(-(x-μᵢ)²/2σᵢ²) / Σ(P)
```

**Multi-Isoscape (Normal Multivariada):**

```
P(origem no pixel i) = (1/√((2π)^k|Σᵢ|)) × exp(-½(x-μᵢ)ᵀΣᵢ⁻¹(x-μᵢ)) / Σ(P)
```

Onde:

- `x` = valor isotópico da amostra
- `μᵢ` = média no pixel i
- `σᵢ` = desvio padrão no pixel i
- `Σᵢ` = matriz de covariância no pixel i
- `k` = número de isótopos

### **Documentação Completa**

- `GENERATE_MAPA_GUIA.md` - Guia detalhado com todas as funções
- `ARQUIVOS_PYTHON_INVENTARIO.md` - Inventário de todos os scripts
- `fraud-detection-generate-maps/README.md` - Documentação do módulo

---

**Última atualização:** 7 de novembro de 2025  
**Autor:** TimberID Analytics Team  
**Projeto:** DDF Insights Analytics - Detecção de Fraude em Madeira
