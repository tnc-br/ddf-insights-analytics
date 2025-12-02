# Comparação: generate_new_mapa.py vs new_code_to_generate_map.py

## 📊 Visão Geral

Os dois arquivos têm **propósitos completamente diferentes**, apesar de ambos trabalharem com rasters de probabilidade:

| Aspecto          | `generate_new_mapa.py`                     | `new_code_to_generate_map.py`          |
| ---------------- | ------------------------------------------ | -------------------------------------- |
| **Propósito**    | **GERA** mapas de probabilidade isotópica  | **PROCESSA** mapas já gerados          |
| **Input**        | Isoscapes + valores isotópicos de amostras | Raster de probabilidade já calculado   |
| **Output**       | Raster de densidade de probabilidade       | Mapa binário (regiões acima do limiar) |
| **Algoritmo**    | Normal univariada/multivariada             | Quantis e limiares de probabilidade    |
| **Complexidade** | Alto (cálculos estatísticos complexos)     | Baixo (operações de limiar)            |

## 🔬 Análise Detalhada

### `generate_new_mapa.py` - GERADOR de Probabilidades

**O QUE FAZ:**

1. Recebe **isoscapes** (rasters com média e desvio padrão de isótopos)
2. Recebe **valores isotópicos** de amostras desconhecidas
3. Calcula **probabilidade de origem** usando distribuições normais
4. Gera **mapa de densidade de probabilidade** para cada amostra

**FUNÇÕES PRINCIPAIS:**

- `pd_raster()` - Função principal (dispatcher)
- `_pd_raster_default()` - Cálculo para 1 isoscape (Normal univariada)
- `_pd_raster_iso_stack()` - Cálculo para múltiplos isoscapes (Normal multivariada)
- `check_unknown()`, `check_mask()`, `check_prior()` - Validações

**EXEMPLO DE USO:**

```python
# Isoscape com 2 bandas: [média, desvio_padrão]
isoscape = "isoscapes/oxygen_18_detailed.tiff"

# Amostras com valores isotópicos
unknown_samples = pd.DataFrame({
    'ID': ['sample1', 'sample2'],
    'O18': [26.5, 24.8]
})

# Gera mapa de probabilidade
prob_maps = pd_raster(
    r=isoscape,
    unknown=unknown_samples,
    mask="shapefiles/brazil.shp",
    out_dir="output_maps/"
)
# Output: Raster com valores de 0 a 1 (probabilidade normalizada)
```

**ALGORITMO:**

```python
# Para cada pixel i no raster:
P(origem no pixel i) = PDF_normal(amostra_valor, μᵢ, σᵢ)

# Normaliza para somar 1
P_normalizada = P / Σ(P)
```

---

### `new_code_to_generate_map.py` - PROCESSADOR de Probabilidades

**O QUE FAZ:**

1. Recebe **raster de probabilidade já calculado** (output do `generate_new_mapa.py`)
2. Aplica **limiares** (threshold) para identificar regiões mais prováveis
3. Gera **mapa binário** (0 ou 1) destacando regiões acima do limiar

**FUNÇÃO PRINCIPAL:**

- `qtl_raster()` - Única função, processa rasters de probabilidade

**EXEMPLO DE USO:**

```python
# Raster de probabilidade (gerado previamente)
prob_raster = "output_maps/sample1_like.tif"

# Gera mapa binário: top 10% das regiões mais prováveis
binary_map = qtl_raster(
    pd_raster=prob_raster,
    threshold=0.10,           # Top 10%
    threshold_type="area",    # Por área (quantil)
    out_dir="output_maps/"
)
# Output: Array booleano (True nas regiões acima do limiar)
```

**ALGORITMO:**

```python
# threshold_type = "area" (quantil):
cutoff = quantile(probabilidades, 1 - threshold)
binary_map = probabilidades > cutoff

# threshold_type = "prob" (probabilidade acumulada):
# Ordena probabilidades e encontra corte onde soma = (1 - threshold) * total
```

---

## 🔄 Fluxo de Trabalho Completo

```
┌─────────────────────────────────────────────────────────────┐
│ ETAPA 1: Gerar Mapas de Probabilidade                      │
│ (generate_new_mapa.py)                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
    INPUT:               │
    • Isoscapes          │
    • Valores isotópicos │
                         │
                         ↓
              ┌──────────────────┐
              │  pd_raster()     │
              │  (Normal PDF)    │
              └────────┬─────────┘
                       │
                       ↓
    OUTPUT: prob_sample1.tif (valores 0-1, contínuos)
                       │
                       │
┌──────────────────────┴─────────────────────────────────────┐
│ ETAPA 2: Processar Mapas (Opcional)                        │
│ (new_code_to_generate_map.py)                              │
└────────────────────────┬───────────────────────────────────┘
                         │
    INPUT:               │
    • Raster de prob.    │
    • Threshold          │
                         │
                         ↓
              ┌──────────────────┐
              │  qtl_raster()    │
              │  (Quantis)       │
              └────────┬─────────┘
                       │
                       ↓
    OUTPUT: binary_map (True/False, top X%)
```

---

## 🆚 Diferenças Técnicas Detalhadas

### 1. **Inputs Completamente Diferentes**

#### `generate_new_mapa.py`:

```python
# Precisa de ISOSCAPES (2 bandas: média e SD)
isoscape_structure = {
    'Band 1': 'Média isotópica por pixel',
    'Band 2': 'Desvio padrão por pixel'
}

# E amostras com valores isotópicos
sample_structure = {
    'ID': 'Identificador da amostra',
    'O18': 26.5,  # Valor isotópico medido
}
```

#### `new_code_to_generate_map.py`:

```python
# Precisa de RASTER DE PROBABILIDADE (1 banda: probabilidade)
prob_raster_structure = {
    'Band 1': 'Probabilidade normalizada (0-1) por pixel'
}

# Não precisa de valores isotópicos, só o threshold
```

### 2. **Outputs Diferentes**

#### `generate_new_mapa.py`:

- **Tipo:** Array de floats (0 a 1)
- **Significado:** Probabilidade relativa de origem em cada pixel
- **Propriedade:** Soma de todos os pixels = 1 (distribuição normalizada)
- **Visualização:** Gradiente contínuo (cores quentes = maior probabilidade)

#### `new_code_to_generate_map.py`:

- **Tipo:** Array booleano (True/False)
- **Significado:** Pixel está ou não nas regiões mais prováveis
- **Propriedade:** Binário (inclui/exclui pixel)
- **Visualização:** Preto e branco (regiões destacadas)

### 3. **Complexidade Algorítmica**

#### `generate_new_mapa.py`:

```python
# Single isoscape (O(n) por amostra, n = pixels válidos):
for cada_pixel:
    prob = norm.pdf(amostra_valor, mean_pixel, sd_pixel)

# Multi-isoscape (O(n*k²) onde k = num_isótopos):
for cada_pixel:
    # Cálculo de matriz de covariância
    cov_matrix = calcular_covariancia(erros_pixel)
    prob = multivariate_normal.pdf(amostra_valores, mean_pixel, cov_matrix)
```

**Complexidade:** O(n) a O(n\*k²) onde n pode ser milhões de pixels

#### `new_code_to_generate_map.py`:

```python
# O(n log n) para quantis:
sorted_data = np.sort(probabilidades)
cutoff = np.quantile(sorted_data, 1 - threshold)
binary_map = probabilidades > cutoff

# O(n log n) para probabilidade acumulada:
cumsum = np.cumsum(sorted_data)
```

**Complexidade:** O(n log n) - muito mais rápido

### 4. **Dependências**

#### `generate_new_mapa.py`:

```python
scipy.stats.norm              # Cálculos estatísticos
scipy.stats.multivariate_normal
geopandas                     # Máscaras geográficas
rasterio.mask                 # Operações espaciais complexas
```

#### `new_code_to_generate_map.py`:

```python
numpy                         # Operações básicas de array
rasterio                      # Leitura de raster
matplotlib                    # Visualização apenas
# Muito mais leve!
```

---

## ⚠️ Por Que NÃO São Intercambiáveis

### Tentativa INCORRETA de usar `qtl_raster()` para gerar mapas:

```python
# ❌ ERRO: qtl_raster() não calcula probabilidades, só processa!
isoscape = "oxygen_18_detailed.tiff"
unknown_sample = {'O18': 26.5}

# Isso NÃO VAI FUNCIONAR:
result = qtl_raster(isoscape, threshold=0.1)
# Motivo: qtl_raster() espera PROBABILIDADES, não isoscapes
```

### Uso CORRETO (em sequência):

```python
# ✅ CORRETO: Usar os dois em sequência

# PASSO 1: Gerar probabilidades
prob_map = pd_raster(
    r=isoscape,
    unknown=unknown_sample,
    out_dir="temp/"
)

# PASSO 2: Processar (opcional, para visualizar regiões)
binary_map = qtl_raster(
    pd_raster="temp/sample_like.tif",
    threshold=0.1,
    threshold_type="area"
)
```

---

## 🎯 Quando Usar Cada Um

### Use `generate_new_mapa.py` quando:

- ✅ Você tem isoscapes e valores isotópicos de amostras
- ✅ Precisa CALCULAR probabilidades de origem
- ✅ Quer análise isotópica completa (bayesiana)
- ✅ Tem múltiplos isótopos para análise multivariada

### Use `new_code_to_generate_map.py` quando:

- ✅ Já tem mapas de probabilidade calculados
- ✅ Quer identificar regiões mais prováveis (top X%)
- ✅ Precisa de mapas binários para decisões
- ✅ Quer diferentes thresholds sem recalcular tudo

---

## 🧪 Teste de Comparação (Próxima Seção)

Veja `test_comparison.py` para um teste completo que:

1. Gera isoscapes sintéticos
2. Calcula probabilidades com `pd_raster()`
3. Processa resultado com `qtl_raster()`
4. Valida que o output de um é o input do outro

---

**Conclusão:** Os dois arquivos são **complementares**, não substitutos. Um gera probabilidades (análise isotópica), o outro processa probabilidades (identificação de regiões).
