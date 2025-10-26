# 🗺️ Guia Rápido - Generate New Mapa

Sistema para gerar mapas isotópicos probabilísticos a partir de dados do Firebase.

## 📋 Pré-requisitos

```bash
# Instalar dependências necessárias
pip install rasterio geopandas numpy pandas scipy matplotlib firebase-admin google-cloud-firestore
```

## 🚀 Uso Rápido (3 passos)

### 1️⃣ Gerar Isoscapes de Exemplo

Se você não tem isoscapes reais, crie dados sintéticos:

```bash
cd fraud-detection-generate-maps
python create_example_isoscapes.py
```

Isso cria:

```
isoscapes/
├── oxygen_18_brazil.tif    # δ18O
├── carbon_13_brazil.tif    # δ13C
└── nitrogen_15_brazil.tif  # δ15N
```

### 2️⃣ Executar Geração de Mapa

Com um ID de documento do Firebase:

```bash
python execute_generate_mapa.py 6ed0ffa36587c49f5b54
```

**O script irá:**

1. ✅ Buscar o documento no Firebase
2. ✅ Extrair coordenadas e dados isotópicos
3. ✅ Perguntar sobre os isoscapes disponíveis
4. ✅ Executar `pd_raster()` com `write_out()`
5. ✅ Gerar PDF com visualização do mapa

### 3️⃣ Visualizar Resultado

```bash
# Abre o PDF gerado
start output_maps/<doc_id>_<timestamp>/output_pdRaster.pdf   # Windows
open output_maps/<doc_id>_<timestamp>/output_pdRaster.pdf    # Mac
xdg-open output_maps/<doc_id>_<timestamp>/output_pdRaster.pdf # Linux
```

## 📊 Modos de Uso

### Single Isoscape (1 isótopo)

Quando perguntado sobre caminhos:

```
isoscapes/oxygen_18_brazil.tif
```

### Multi-Isoscape (3 isótopos combinados)

Quando perguntado sobre caminhos:

```
isoscapes/oxygen_18_brazil.tif,isoscapes/carbon_13_brazil.tif,isoscapes/nitrogen_15_brazil.tif
```

## 🎯 Estrutura de Dados Esperada

### Documento Firebase

O documento deve ter:

```json
{
  "id": "6ed0ffa36587c49f5b54",
  "lat": -3.119,
  "lon": -60.0217,
  "O18": -5.2, // ou d18O, oxygen_18
  "C13": -28.1, // ou d13C, carbon_13
  "N15": 3.4, // ou d15N, nitrogen_15
  "org_name": "Exemplo Org"
}
```

**Campos de isótopos reconhecidos:**

- `O18`, `d18O`, `oxygen_18`
- `C13`, `d13C`, `carbon_13`
- `N15`, `d15N`, `nitrogen_15`
- `H2`, `d2H`, `hydrogen_2`
- `S34`, `d34S`, `sulfur_34`

### Arquivo Isoscape (GeoTIFF)

- **Formato**: GeoTIFF (.tif)
- **Bandas**: 2 (banda 1 = média, banda 2 = desvio padrão)
- **CRS**: Qualquer (preferencialmente EPSG:4326)
- **NoData**: Definido no raster

## 📁 Estrutura de Saída

```
output_maps/
└── <doc_id>_<timestamp>/
    ├── output_pdRaster.pdf          # 🎨 VISUALIZAÇÃO PRINCIPAL
    ├── <doc_id>_like.tif            # Raster de probabilidade
    └── (mais rasters se múltiplas amostras)
```

## 🔬 O que o Mapa Mostra

O mapa gerado é um **heatmap de probabilidade de origem**:

- 🟢 **Verde/Amarelo**: Alta probabilidade de origem
- 🔵 **Azul escuro**: Baixa probabilidade
- ⚫ **Preto/NoData**: Áreas sem dados

**Interpretação estatística:**

```
P(origem no pixel X | valores isotópicos) =
    Normal(valores_amostra | μ_pixel, σ_pixel) / Σ(todas probabilidades)
```

## ⚙️ Opções Avançadas

### Com Prior (conhecimento prévio)

Edite `execute_generate_mapa.py` linha ~95:

```python
result = pd_raster(
    r=r_paths,
    unknown=unknown_df,
    prior='path/to/prior.tif',  # ← Adicione aqui
    mask=None,
    genplot=True,
    out_dir=out_dir
)
```

### Com Máscara Geográfica

```python
result = pd_raster(
    r=r_paths,
    unknown=unknown_df,
    prior=None,
    mask='shapefiles/brazil_legal_amazon.shp',  # ← Adicione aqui
    genplot=True,
    out_dir=out_dir
)
```

## 🐛 Troubleshooting

### Erro: "Documento não encontrado"

- ✅ Verifique se o ID está correto
- ✅ Verifique se `serviceAccountKey.json` está na pasta
- ✅ Documento pode estar em coleção diferente (script busca em 3)

### Erro: "Nenhum dado isotópico encontrado"

- ✅ Adicione campos de isótopos ao documento
- ✅ Use nomes reconhecidos: O18, d18O, oxygen_18, etc.

### Erro: "Raster must have 2 layers"

- ✅ Isoscape deve ter exatamente 2 bandas
- ✅ Use `create_example_isoscapes.py` para gerar formato correto

### Erro: "Rasters have different CRS"

- ✅ Todos isoscapes devem ter mesmo CRS
- ✅ Ou reprojecte com QGIS/rasterio antes

### PDF vazio ou sem plots

- ✅ Certifique-se que `genplot=True`
- ✅ Verifique se há pixels válidos após máscara
- ✅ Veja logs para warnings sobre probabilidades zero

## 🔗 Integração com Sistema Principal

Este módulo (`generate_new_mapa.py`) é **independente** do sistema principal TimberID.

**Sistema Principal (Earth Engine + MapBiomas):**

```bash
# Usa isoscapes e dados do Earth Engine
python fraud-detection-update-sample/test_local.py

# Ou via Cloud Function
python easy_pubsub.py <doc_id>
```

**Este Módulo (Análise Isotópica Avançada):**

```bash
# Usa isoscapes locais (GeoTIFF) e análise estatística multi-isotópica
python execute_generate_mapa.py <doc_id>
```

## 📚 Referências

- **assignR (R package)**: https://github.com/SPATIAL-Lab/assignR
- **IsoMAP**: http://isomap.org
- **Rasterio docs**: https://rasterio.readthedocs.io/

## 💡 Próximos Passos

1. **Para usar em produção**: Obtenha isoscapes validados cientificamente
2. **Para integração**: Adapte para ler isoscapes do Earth Engine
3. **Para performance**: Implemente processamento em batches (ver code review)

---

**Criado para**: DDF Insights Analytics - TimberID  
**Data**: Outubro 2025  
**Autor**: Code Review + Documentation
