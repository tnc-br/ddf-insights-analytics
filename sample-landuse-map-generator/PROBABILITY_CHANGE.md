# Mudança: Densidade Normalizada → Probabilidade Estatística

## 📊 O Que Mudou

### ❌ ANTES: Densidade de Probabilidade Normalizada

```python
# Calculava PDF (Probability Density Function)
prob_density = norm.pdf(sample_value, mean, sd)
prob_normalized = prob_density / sum(prob_density)  # Soma = 1.0
```

**Problema:** Os valores somavam 1.0, mas não diziam se cada pixel era **compatível** com a amostra.

### ✅ DEPOIS: Probabilidade Estatística (p-value)

```python
# Calcula z-test (quantos desvios padrão de distância)
z_score = abs((sample_value - mean) / sd)
p_value = 2 * norm.sf(z_score)  # Two-tailed test
probability_percent = p_value * 100  # 0-100%
```

**Vantagem:** Cada pixel diz **independentemente** se é compatível com a amostra.

---

## 🎨 Interpretação Visual

### Mapa de Cores (3 categorias):

| Cor             | Probabilidade | Significado                                                |
| --------------- | ------------- | ---------------------------------------------------------- |
| 🟢 **Verde**    | ≥95%          | **Alta compatibilidade** - Amostra provavelmente vem daqui |
| 🟡 **Amarelo**  | 5-95%         | **Compatibilidade média** - Possível, mas não conclusivo   |
| 🔴 **Vermelho** | <5%           | **Incompatível** - Amostra improvável de vir daqui         |

### Exemplo Real (do teste):

```
Amostra: match_center (δ18O = -15.0‰)
   🟢 Alta (≥95%):      150 pixels (  0.7%)  ← Região de origem provável
   🟡 Média (5-95%):   3792 pixels ( 16.9%)  ← Regiões possíveis
   🔴 Baixa (<5%):    18558 pixels ( 82.5%)  ← Regiões improváveis

Amostra: no_match (δ18O = 50.0‰)
   🟢 Alta:        0 pixels (0.0%)  ← Nenhum pixel compatível!
   🟡 Média:       0 pixels (0.0%)
   🔴 Baixa:   22500 pixels (100%)  ← Amostra não vem do Brasil
```

---

## 🔬 Algoritmo Técnico

### Single Isoscape (1 isótopo):

```python
# Two-tailed z-test
z = |sample - mean_pixel| / sd_pixel
p_value = 2 × (1 - CDF(z))  # Probability sample matches pixel
percentage = p_value × 100
```

**Interpretação do z-score:**

- z < 1.96 → p > 5% (compatível, amarelo/verde)
- z ≥ 1.96 → p ≤ 5% (incompatível, vermelho)
- z ≥ 2.58 → p ≤ 1% (muito incompatível)

### Multi-Isoscape (múltiplos isótopos):

```python
# Chi-squared test (Mahalanobis distance)
diff = sample - mean_pixel
mahal_dist² = diffᵀ × Σ⁻¹ × diff
p_value = 1 - χ²_CDF(mahal_dist², df=n_isotopes)
percentage = p_value × 100
```

---

## 📁 Mudanças nos Arquivos

### Arquivos Salvos:

- **Antes:** `{sample_id}_like.tif` (densidade)
- **Depois:** `prob_{sample_id}.tif` (probabilidade %)

### Metadados:

```python
# Single isoscape
band_description = "Probability (%) - Two-tailed z-test"

# Multi-isoscape
band_description = "Probability (%) - Chi-squared test"
```

---

## 🧪 Validação

### Teste 1: Amostra compatível (δ18O = -15‰)

- ✅ Pixels verdes (~1%) na região esperada
- ✅ Pixels amarelos (~17%) ao redor
- ✅ Maioria vermelho (regiões distantes)

### Teste 2: Amostra incompatível (δ18O = 50‰)

- ✅ 100% pixels vermelhos
- ✅ Nenhum pixel verde ou amarelo
- ✅ Conclusão: Amostra não vem do Brasil

### Teste 3: Valores não somam 1.0

- ✅ **CORRETO!** Cada pixel é independente
- ✅ Exemplo: 150 pixels verdes (≥95%) simultaneamente
- ✅ Antes: Impossível (soma deveria ser 1.0)

---

## 💡 Casos de Uso

### 1. Identificar Região de Origem

```
Pergunta: "De onde veio esta amostra?"
Resposta: "Procure pixels verdes (≥95%)"
```

### 2. Validar Declaração de Origem

```
Pergunta: "Esta madeira é do Pará?"
Resposta: "Veja se o Pará tem pixels verdes"
   - Verde no Pará → Declaração plausível ✅
   - Vermelho no Pará → Declaração improvável ❌
```

### 3. Detectar Fraude

```
Pergunta: "A origem declarada é compatível?"
Resposta: Calcule % de área verde na região declarada
   - ≥10% verde → Possível (investigar mais)
   - <1% verde → Fraude provável (alerta!)
```

---

## 🔄 Compatibilidade

### Código antigo ainda funciona!

```python
# Mesmo uso, output diferente
prob_maps = pd_raster(
    r="isoscape.tif",
    unknown=samples_df,
    out_dir="results/"
)
# Antes: valores 0-1, soma=1.0
# Depois: valores 0-100%, independentes
```

### Ferramentas downstream precisam adaptar:

- **qtl_raster()**: Usar thresholds de 5% e 95% agora
- **Visualizações**: Usar colormap categórico (verde/amarelo/vermelho)

---

## 📖 Referências Estatísticas

### Z-test (univariado):

- **Hipótese nula:** "Amostra vem deste pixel"
- **p-value:** Probabilidade de observar diferença tão grande por acaso
- **Threshold:** p < 0.05 = rejeita hipótese (pixel incompatível)

### Chi-squared test (multivariado):

- **Distância de Mahalanobis:** Considera correlações entre isótopos
- **Graus de liberdade:** Número de isótopos
- **Threshold:** Similar ao z-test (p < 0.05)

---

## 🚀 Como Usar

### Gerar mapas:

```bash
cd sample-landuse-map-generator
python test_probability_maps.py
```

### Interpretar resultados:

```python
# Ler raster de probabilidade
with rasterio.open("prob_sample.tif") as src:
    prob = src.read(1)  # Valores 0-100%

# Identificar regiões compatíveis
high_prob = prob >= 95    # Verde
medium_prob = (prob >= 5) & (prob < 95)  # Amarelo
low_prob = prob < 5       # Vermelho

print(f"Área compatível: {high_prob.sum() / prob.size * 100:.1f}%")
```

---

**Data da mudança:** 21 de novembro de 2025  
**Autor:** TimberID Analytics Team  
**Status:** ✅ Testado e funcionando
