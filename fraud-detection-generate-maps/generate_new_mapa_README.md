# generate_new_mapa.py - Documentação

## 📋 Visão Geral

Este arquivo implementa um sistema de **análise geoespacial probabilística** para determinar a origem geográfica de amostras desconhecidas usando dados isotópicos. É uma tradução Python do pacote R `assignR`, utilizado para análise de isoscapes (mapas de distribuição isotópica).

**Conceito**: Compara valores isotópicos de amostras desconhecidas com mapas de referência (isoscapes) para calcular a probabilidade de origem de cada pixel do mapa.

---

## 🎯 Funcionalidade Principal

**Input**:

- Rasters GeoTIFF com 2 bandas (média e desvio padrão isotópico)
- DataFrame com amostras desconhecidas (ID + valores isotópicos)

**Output**:

- Mapas de probabilidade (rasters) mostrando possíveis origens
- Gráficos PDF com visualização dos resultados

**Aplicações**: Rastreamento de origem de produtos (madeira, alimentos), estudos de migração animal, análise forense.

---

## 🔧 Funções - Organização Hierárquica

### 📍 **Função Principal (Entry Point)**

#### `pd_raster(r, unknown, prior=None, mask=None, genplot=True, out_dir=None)`

**O que faz**: Dispatcher principal que roteia para o processamento correto baseado no tipo de entrada.

**Parâmetros**:

- `r`: Caminho para um raster (single isoscape) OU lista de caminhos (múltiplos isoscapes)
- `unknown`: DataFrame com amostras (col 0 = ID, demais = valores isotópicos)
- `prior`: (Opcional) Raster com probabilidades prévias
- `mask`: (Opcional) Shapefile para mascarar área de análise
- `genplot`: Se deve gerar gráficos (padrão: True)
- `out_dir`: Diretório para salvar outputs

**Retorna**: Lista de arrays NumPy com superfícies de probabilidade

**Fluxo**:

1. Valida opções de entrada
2. Detecta se é single ou multi-isoscape
3. Valida dados das amostras
4. Cacheia profile do raster (otimização)
5. Roteia para `_pd_raster_default()` ou `_pd_raster_iso_stack()`

---

### 🔬 **Funções de Processamento Core**

#### `_pd_raster_default(r_path, unknown, prior=None, mask=None, genplot=True, out_dir=None)`

**O que faz**: Processa análise com **um único isoscape** (1 tipo de isótopo).

**Algoritmo**:

1. Abre raster e valida CRS e número de bandas (deve ter 2)
2. Aplica máscara geográfica se fornecida
3. Extrai valores de média e desvio padrão
4. Para cada amostra desconhecida:
   - Calcula PDF normal: `P(valor_amostra | média_pixel, sd_pixel)`
   - Multiplica por prior se existir
   - Normaliza para somar 1 (distribuição de probabilidade)
5. Salva rasters individuais e gera plots

**Estatística**: Usa distribuição normal univariada (`scipy.stats.norm.pdf`)

---

#### `_pd_raster_iso_stack(r_paths, unknown, prior=None, mask=None, genplot=True, out_dir=None)`

**O que faz**: Processa análise com **múltiplos isoscapes** (vários tipos de isótopos combinados).

**Algoritmo**:

1. Lê todos os rasters e valida que têm mesma geometria
2. Aplica máscara a todos os layers
3. Empilha dados de média e erro em arrays 3D
4. Verifica correlação entre isoscapes (avisa se >0.7)
5. **PRÉ-CALCULA** matriz de covariância para cada pixel válido
6. Para cada amostra:
   - Calcula PDF multivariada normal em cada pixel
   - Multiplica por prior se existir
   - Normaliza distribuição
7. Salva outputs

**Estatística**: Usa distribuição normal multivariada (`scipy.stats.multivariate_normal.pdf`)

**⚠️ Nota**: Pré-cálculo de covariâncias consome muita memória (aviso quando >1GB)

---

### ✅ **Funções de Validação**

#### `check_unknown(unknown, n_isoscapes)`

**O que faz**: Valida e padroniza dados das amostras desconhecidas.

**Valida**:

- Tipo correto (DataFrame ou dict/list de 'refTrans')
- Número de colunas corresponde ao número de isoscapes
- Sem valores faltantes (NaN)
- Todas colunas de dados são numéricas
- IDs coincidem se múltiplos refTrans

**Retorna**: DataFrame padronizado (col 0 = ID, demais = valores isotópicos)

---

#### `check_prior(prior_path, r_profile)`

**O que faz**: Valida raster de probabilidades prévias.

**Valida**:

- CRS existe
- CRS coincide com isoscape (lança NotImplementedError se diferente)
- Geometria coincide com isoscape

**Retorna**: Tupla `(valores_flatten, profile)` ou `(None, None)`

**⚠️ Limitação**: Reprojection automática não implementada

---

#### `check_mask(mask_path, r_profile)`

**O que faz**: Valida arquivo vetorial de máscara (shapefile/geopackage).

**Valida**:

- CRS existe
- Geometria é Polygon ou MultiPolygon
- Reprojecta automaticamente se CRS diferir

**Retorna**: GeoDataFrame reprojetado ou None

---

#### `check_options(genplot, out_dir)`

**O que faz**: Valida opções de plotagem e output.

**Valida**:

- `genplot` é booleano
- `out_dir` é string (se fornecido)
- Cria diretório se não existir

---

### 🛠️ **Funções Auxiliares**

#### `compare_geom(r1_profile, r2_profile)`

**O que faz**: Compara geometria de dois rasters para garantir compatibilidade.

**Compara**:

- CRS (sistema de coordenadas)
- Transform (georeferenciamento) - usa tolerância para evitar erros de precisão
- Dimensões (altura e largura)

**Lança**: `ValueError` se qualquer aspecto não coincidir

**✅ Otimização**: Usa `np.allclose()` para comparar transforms (evita problemas de float)

---

#### `process_ref_trans(unknown)`

**O que faz**: Converte objetos 'refTrans' do R para DataFrame Python.

**Lógica**:

- Se 3 colunas: adiciona IDs sequenciais automaticamente
- Se 4 colunas: assume que ID está na primeira coluna
- Extrai apenas ID e valor isotópico

**Propósito**: Compatibilidade com workflow R→Python

---

#### `write_out(out_dir, genplot, result_stack, data, base_profile)`

**O que faz**: Gera visualizações e salva PDFs com mapas de probabilidade.

**Funcionalidade**:

- Limita a 50 plots para evitar problemas de memória
- Cria grid 5 colunas × N linhas
- Gera heatmap com colormap 'viridis'
- Salva PDF se `out_dir` fornecido, senão mostra na tela

**✅ Otimização**: Limite de MAX_PLOTS=50 para datasets grandes

---

## 📊 Fluxo de Execução

```
pd_raster()
    ↓
    ├─→ check_options() - valida parâmetros
    ├─→ check_unknown() - valida amostras
    ├─→ check_mask() - valida máscara
    ↓
    ┌─────────────────┬──────────────────┐
    │ Single Isoscape │ Multi-Isoscape   │
    ↓                 ↓
_pd_raster_default   _pd_raster_iso_stack
    │                 │
    ├─→ check_prior() ├─→ check_prior()
    ├─→ norm.pdf()    ├─→ compare_geom()
    │   (univariada)  ├─→ pre-calc covs
    │                 ├─→ multivariate_normal.pdf()
    ↓                 ↓
    └─────────────────┴──────────────────┘
                ↓
         write_out() - gera plots/PDFs
                ↓
         return result_stack
```

---

## 🔢 Conceitos Estatísticos

### Single Isoscape (Univariado)

```python
P(origem_pixel | amostra) ∝ Normal(valor_amostra | μ_pixel, σ_pixel) × prior_pixel
```

### Multi-Isoscape (Multivariado)

```python
P(origem_pixel | amostra) ∝ MVNormal(vetor_amostra | μ_pixel, Σ_pixel) × prior_pixel
```

Onde:

- `μ` = média isotópica do pixel
- `σ` = desvio padrão (univariado)
- `Σ` = matriz de covariância (multivariado)
- `prior` = conhecimento prévio sobre probabilidades

---

## ⚠️ Limitações e Considerações

### Memória

- **Multi-isoscape**: Pré-calcula N_pixels × N_isoscapes² matrizes
- Raster 1M pixels + 3 isoscapes = ~2GB RAM
- **Solução futura**: Implementar processamento em batches

### Performance

- Loop duplo em `_pd_raster_iso_stack` (samples × pixels)
- **Otimização futura**: Vetorizar com broadcasting

### Funcionalidades

- ❌ Reprojection automática de prior não implementada
- ✅ Máscara reprojecta automaticamente
- ✅ Limite de 50 plots para datasets grandes

---

## 📦 Dependências Críticas

```python
import rasterio          # Leitura/escrita de rasters GeoTIFF
import geopandas         # Manipulação de vetores (máscaras)
import numpy             # Operações numéricas
import pandas            # DataFrames
import scipy.stats       # PDFs estatísticas
import matplotlib        # Visualização
```

---

## 🎓 Casos de Uso

### Exemplo 1: Single Isoscape

```python
# Rastrear origem de madeira usando δ18O
result = pd_raster(
    r='path/to/oxygen18_isoscape.tif',
    unknown=pd.DataFrame({'ID': ['sample1'], 'O18': [-5.2]}),
    out_dir='./results'
)
```

### Exemplo 2: Multi-Isoscape

```python
# Rastrear com 3 isótopos combinados
result = pd_raster(
    r=['O18.tif', 'C13.tif', 'N15.tif'],
    unknown=pd.DataFrame({
        'ID': ['sample1'],
        'O18': [-5.2],
        'C13': [-28.1],
        'N15': [3.4]
    }),
    mask='brazil_amazon.shp',
    out_dir='./results'
)
```

---

## 🔗 Relação com o Projeto TimberID

**Status**: Este arquivo parece ser **experimental/não integrado**:

- ❌ Não é importado por nenhum outro módulo
- ❌ Não está nas Cloud Functions principais
- ✅ Pode ser protótipo para futuras funcionalidades

**Possível uso**: Análise avançada de isótopos com múltiplos marcadores para melhorar detecção de fraude.
