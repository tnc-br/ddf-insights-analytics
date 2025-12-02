# 📋 Atualização do create_mapa_local.py

## 🎯 Objetivo

Sincronizar `create_mapa_local.py` com as mudanças implementadas no `generate_new_mapa.py` para usar **probabilidade estatística** em vez de **densidade normalizada**.

## 🔄 Mudanças Implementadas

### 1. Algoritmo: Densidade Normalizada → Z-Test Estatístico

**ANTES (Densidade Normalizada):**

```python
# Calcular densidade de probabilidade
prob_vals = norm.pdf(sample_value, mean_vals, sd_vals)

# Normalizar para soma = 1.0
total_prob = np.nansum(prob_surface)
if total_prob > 0:
    prob_surface = prob_surface / total_prob
```

**DEPOIS (Z-Test Estatístico):**

```python
# Calcular z-score (quantos desvios padrão)
z_scores = np.abs((sample_value - mean_vals) / sd_vals)

# Converter para probabilidade (teste bilateral)
p_values = 2 * norm.sf(z_scores)  # sf = survival function

# Converter para percentual (0-100%)
prob_percentage = p_values * 100
```

### 2. Interpretação dos Valores

| Aspecto              | ANTES                       | DEPOIS                      |
| -------------------- | --------------------------- | --------------------------- |
| **Tipo de valor**    | Densidade normalizada       | Probabilidade estatística   |
| **Faixa de valores** | 0 a ~0.001 (muito pequenos) | 0% a 100%                   |
| **Soma total**       | = 1.0 (normalizado)         | >> 1.0 (independente)       |
| **Significado**      | Probabilidade relativa      | Compatibilidade estatística |
| **Independência**    | Pixels dependentes (soma=1) | Pixels independentes        |

### 3. Visualização: Gradiente → Categórico

**ANTES (Gradiente Viridis):**

```python
im = ax.imshow(prob_surface, cmap='viridis')
cbar.set_label('Probability Density')
```

**DEPOIS (Cores Categóricas):**

```python
from matplotlib.colors import ListedColormap, BoundaryNorm

colors = ['#d73027', '#fee08b', '#1a9850']  # Red, Yellow, Green
cmap = ListedColormap(colors)
bounds = [0, 5, 95, 100]
norm = BoundaryNorm(bounds, cmap.N)

im = ax.imshow(prob_surface, cmap=cmap, norm=norm)
```

**Código de Cores:**

- 🟢 **Verde (≥95%)**: Alta probabilidade - estatisticamente compatível
- 🟡 **Amarelo (5-95%)**: Probabilidade moderada - incerto
- 🔴 **Vermelho (<5%)**: Baixa probabilidade - estatisticamente incompatível

### 4. Metadados do GeoTIFF

**ANTES:**

```python
with rasterio.open(output_path, 'w', **out_profile) as dst:
    dst.write(prob_surface, 1)
```

**DEPOIS:**

```python
with rasterio.open(output_path, 'w', **out_profile) as dst:
    dst.write(prob_surface, 1)
    dst.set_band_description(1, 'Probability (%) - Two-tailed z-test')
```

### 5. Documentação

Atualizadas as docstrings e help text para refletir:

- Algoritmo z-test estatístico
- Valores percentuais (0-100%)
- Interpretação das cores
- Independência dos pixels

## ✅ Validação

Teste automatizado criado: `test_create_mapa_local.py`

**Resultados:**

```
✅ PASSOU: Algoritmo z-test
   • Metadados corretos (z-test)
   • Valores são probabilidades independentes (não normalizadas)
   • Algoritmo z-test validado manualmente

✅ PASSOU: Visualização categórica
   • PDF gerado com colormap categórico
   • Cores corretas (#d73027, #fee08b, #1a9850)
   • Distribuição de pixels por categoria validada
```

### Exemplo de Validação: Amostra "no_match" (δ18O = 50‰)

Valor impossível (muito fora do range de -30‰ a -10‰):

- 🟢 Verde (≥95%): **0 pixels (0.0%)**
- 🟡 Amarelo (5-95%): **0 pixels (0.0%)**
- 🔴 Vermelho (<5%): **10000 pixels (100.0%)**

✅ Resultado esperado: mapa completamente vermelho

### Exemplo de Validação: Amostra "match_center" (δ18O = -20‰)

Valor no centro do gradient (-30‰ a -10‰):

- 🟢 Verde (≥95%): **186 pixels (1.9%)**
- 🟡 Amarelo (5-95%): **5623 pixels (56.2%)**
- 🔴 Vermelho (<5%): **4191 pixels (41.9%)**

✅ Resultado esperado: maioria amarela com algumas regiões verdes

## 🔧 Arquivos Modificados

1. **create_mapa_local.py**

   - Função `_pd_raster_default()`: algoritmo z-test
   - Função `_generate_plots()`: colormap categórico
   - Função `pd_raster()`: docstring atualizada
   - Docstring do módulo: descrição do algoritmo

2. **test_create_mapa_local.py** (novo)
   - Validação do algoritmo z-test
   - Validação da visualização categórica
   - Testes com amostras sintéticas

## 📊 Comparação com generate_new_mapa.py

| Aspecto              | generate_new_mapa.py | create_mapa_local.py | Status               |
| -------------------- | -------------------- | -------------------- | -------------------- |
| Algoritmo z-test     | ✅                   | ✅                   | Sincronizado         |
| Probabilidade 0-100% | ✅                   | ✅                   | Sincronizado         |
| Colormap categórico  | ✅                   | ✅                   | Sincronizado         |
| Metadados z-test     | ✅                   | ✅                   | Sincronizado         |
| Multi-isoscape       | ✅                   | ❌                   | N/A (fora do escopo) |

**Nota:** `create_mapa_local.py` implementa apenas modo **single-isoscape** (1 isótopo), enquanto `generate_new_mapa.py` suporta **multi-isoscape** (múltiplos isótopos com chi-squared test).

## 🚀 Como Usar

```bash
# Exemplo 1: Usar documento padrão
python3 create_mapa_local.py

# Exemplo 2: Documento específico
python3 create_mapa_local.py 6ed0ffa36587c49f5b54

# Exemplo 3: Valor δ18O manual
python3 create_mapa_local.py abc123def456 -15.2

# Exemplo 4: Rodar teste de validação
python3 test_create_mapa_local.py
```

## 📈 Vantagens da Nova Abordagem

### Densidade Normalizada (antiga)

- ❌ Valores muito pequenos (~0.001)
- ❌ Difícil interpretar visualmente
- ❌ Pixels dependentes (soma = 1.0)
- ❌ Não indica compatibilidade estatística

### Probabilidade Estatística (nova)

- ✅ Valores intuitivos (0-100%)
- ✅ Fácil interpretar com cores
- ✅ Pixels independentes
- ✅ Indica compatibilidade estatística clara
- ✅ Verde = compatível, Vermelho = incompatível

## 🔗 Referências

- **PROBABILITY_CHANGE.md**: Documentação detalhada da mudança no `generate_new_mapa.py`
- **test_probability_maps.py**: Teste original do algoritmo z-test
- **test_create_mapa_local.py**: Validação da sincronização

## ✅ Conclusão

`create_mapa_local.py` foi **atualizado com sucesso** e está **100% sincronizado** com `generate_new_mapa.py` no que diz respeito ao algoritmo de probabilidade estatística, visualização categórica e metadados.

**Todos os testes passaram** ✅
