# Resumo: Diferenças entre generate_new_mapa.py e new_code_to_generate_map.py

## ✅ RESULTADO DO TESTE

**Status:** ✅ TESTE PASSOU - Os dois códigos funcionam corretamente em sequência!

## 📊 Diferenças Principais

### `generate_new_mapa.py` - GERADOR de Probabilidades

- **Função:** `pd_raster()` - Calcula probabilidades de origem
- **Input:** Isoscapes (2 bandas: média + desvio padrão) + valores isotópicos
- **Output:** Raster de probabilidade (valores 0-1, soma = 1.0)
- **Algoritmo:** Distribuição Normal (univariada ou multivariada)
- **Uso:** Análise isotópica primária

### `new_code_to_generate_map.py` - PROCESSADOR de Probabilidades

- **Função:** `qtl_raster()` - Identifica regiões mais prováveis
- **Input:** Raster de probabilidade (output de `pd_raster()`)
- **Output:** Mapa binário (True/False) destacando top X%
- **Algoritmo:** Quantis ou probabilidade acumulada
- **Uso:** Pós-processamento, visualização de regiões

## 🔄 Fluxo Correto (Em Sequência)

```
1. Isoscapes (mean, sd) + Valores Isotópicos
         ↓
   pd_raster() (generate_new_mapa.py)
         ↓
2. Raster de Probabilidade (valores contínuos 0-1)
         ↓
   qtl_raster() (new_code_to_generate_map.py)
         ↓
3. Mapa Binário (regiões top X%)
```

## 🧪 Resultados do Teste

### Validações Aprovadas:

- ✅ Soma de probabilidades = 1.000000 (para todas as 3 amostras)
- ✅ Top 25% área: exatamente 25.0% dos pixels
- ✅ Top 10% área: exatamente 10.0% dos pixels
- ✅ Processamento em sequência funciona corretamente

### Estatísticas:

- **3 amostras testadas** (Norte, Centro, Sul do Brasil)
- **Isoscape:** 200×200 pixels (40.000 pixels totais)
- **Valores isotópicos testados:** -10.0‰, -20.0‰, -30.0‰
- **Mapas gerados:** 3 probabilidade + 9 binários (3 amostras × 3 thresholds)

## 📁 Arquivos Gerados pelo Teste

Localizados em: `sample-landuse-map-generator/test_comparison_output/`

```
test_comparison_output/
├── test_isoscape_o18.tif              # Isoscape sintético (input)
├── sample_north_like.tif              # Prob map (pd_raster output)
├── sample_center_like.tif             # Prob map (pd_raster output)
├── sample_south_like.tif              # Prob map (pd_raster output)
├── qtl_raster_result.pdf              # Mapas binários (qtl_raster)
├── output_pdRaster.pdf                # Visualização (pd_raster)
└── pipeline_comparison.pdf            # Comparação completa
```

## 💡 Conclusão

**Os dois códigos NÃO são intercambiáveis - são COMPLEMENTARES:**

1. **`generate_new_mapa.py`** faz a análise isotópica pesada (cálculo de probabilidades)
2. **`new_code_to_generate_map.py`** faz o pós-processamento leve (identificação de regiões)

**Analogia:**

- `generate_new_mapa.py` = "Motor de busca" (analisa e ranqueia tudo)
- `new_code_to_generate_map.py` = "Filtro de resultados" (mostra só o top X%)

## 🚀 Como Usar

### Cenário 1: Análise completa (primeira vez)

```python
# Passo 1: Gerar probabilidades
prob_maps = pd_raster(
    r="isoscapes/oxygen_18.tif",
    unknown=samples_df,
    out_dir="results/"
)

# Passo 2: Identificar regiões (opcional)
binary_map = qtl_raster(
    pd_raster="results/sample_like.tif",
    threshold=0.10,
    threshold_type="area"
)
```

### Cenário 2: Testar diferentes thresholds (já tem probabilidades)

```python
# Não precisa recalcular probabilidades!
# Só processar com diferentes thresholds:

top_10 = qtl_raster("results/sample_like.tif", threshold=0.10)
top_25 = qtl_raster("results/sample_like.tif", threshold=0.25)
top_50_prob = qtl_raster("results/sample_like.tif", threshold=0.50,
                         threshold_type="prob")
```

## 📖 Documentação Completa

- **Comparação detalhada:** `COMPARISON.md`
- **Script de teste:** `test_comparison.py`
- **Executar teste:** `python test_comparison.py`

---

**Data do teste:** 21 de novembro de 2025  
**Status:** ✅ Teste passou com 100% de validações aprovadas
