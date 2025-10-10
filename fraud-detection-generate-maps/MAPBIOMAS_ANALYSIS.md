# Análise MapBiomas - Versão e Atualização

## 🔍 Status Atual da Implementação

### **Versão Utilizada**

```python
# ATUAL (main.py linha 34)
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_deforestation_regeneration_v1"
```

**Dataset**: MapBiomas Collection 7.1 - Deforestation & Regeneration v1  
**Ano dos dados**: 2021  
**Status**: ⚠️ **DESATUALIZADO**

---

## 📊 Versões Disponíveis do MapBiomas

### **Collection 8 (Mais Recente)** ✅

Segundo o [GEE Community Catalog](https://gee-community-catalog.org/projects/mapbiomas/):

```javascript
// MapBiomas Collection 8 assets
assets: {
    integration: 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    transitions: 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_transitions_v1',
}
```

**Melhorias da Collection 8:**

- Dados atualizados até 2022
- Melhor acurácia nas classificações
- Novos algoritmos de detecção
- Cobertura expandida para outras regiões (Pan-Amazônia, Indonésia, Bolívia, Peru)

### **Collection 7.1 (Atual no código)** ⚠️

```
projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_deforestation_regeneration_v1
```

- Dados até 2021
- Versão anterior

---

## 🔧 Recomendações de Atualização

### **Opção 1: Atualizar para Collection 8 Integration** (RECOMENDADO)

#### **Benefícios:**

- ✅ Dados mais recentes (2022)
- ✅ Melhor acurácia
- ✅ Dataset de integração (mais completo)
- ✅ Suporte oficial ativo

#### **Mudança necessária:**

```python
# De:
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_deforestation_regeneration_v1"

# Para:
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1"
```

#### **Impactos:**

- ⚠️ A banda pode ter nome diferente (verificar se ainda é `product_2021` ou se mudou para `product_2022`)
- ⚠️ Categorias de classificação podem ter sido refinadas
- ✅ Paleta de cores provavelmente mantém compatibilidade

---

### **Opção 2: Manter Collection 7.1 com documentação** (CONSERVADOR)

#### **Quando usar:**

- Sistema já em produção com validações baseadas em dados de 2021
- Necessidade de consistência histórica
- Mudança requer re-validação extensiva

#### **Ação:**

- Documentar explicitamente que usa dados de 2021
- Planejar migração futura
- Adicionar warning nos logs

---

## 📋 Checklist de Atualização

Se optar por atualizar para Collection 8:

### **1. Verificar estrutura do dataset**

```javascript
// No Earth Engine Code Editor
var image = ee.Image(
  "projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1"
);
print("Bands:", image.bandNames());
print("Properties:", image.propertyNames());
```

### **2. Verificar anos disponíveis**

```javascript
// Listar todas as bandas de anos
var bands = image.bandNames();
print("Anos disponíveis:", bands);
// Exemplo: classification_1985, classification_1986, ... classification_2022
```

### **3. Ajustar código**

```python
# Verificar se o nome da banda mudou
# Collection 7.1 usa: product_2021
# Collection 8 pode usar: classification_2022 ou product_2022

# Ajustar em generate_initial_map():
land_use_layers_2022_simplified = (
    land_use_mapbiomas_image.select("classification_2022").divide(100).floor()
)
```

### **4. Validar categorias**

Verificar se as 7 categorias ainda são:

1. Anthropic
2. Primary Vegetation
3. Secondary Vegetation
4. Deforestation in Primary Vegetation
5. Secondary Vegetation Regrowth
6. Deforestation in Secondary Vegetation
7. Not applied

### **5. Testar visualização**

- Gerar mapas de teste com Collection 8
- Comparar visualmente com mapas da Collection 7.1
- Validar cores e classificações

### **6. Atualizar testes**

```python
# Em test_local_maps.py e test_integration.py
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1"
```

### **7. Atualizar documentação**

- README.md
- Comentários no código
- TESTING.md

---

## 🔬 Verificação Técnica

### **Diferenças entre Deforestation/Regeneration e Integration**

#### **Deforestation & Regeneration (Collection 7.1 - Atual)**

- Foco específico em mudanças de vegetação
- Simplificado para 7 categorias
- Banda: `product_2021`

#### **Integration (Collection 8 - Recomendado)**

- Dataset completo de cobertura e uso da terra
- Mais de 30 classes detalhadas
- Bandas: `classification_YYYY` (onde YYYY é o ano)
- Pode ser simplificado para as mesmas 7 categorias

---

## 🎯 Recomendação Final

### **ATUALIZAR PARA COLLECTION 8** ✅

**Justificativa:**

1. Dados mais recentes (2022 vs 2021)
2. Melhor qualidade e acurácia
3. Suporte ativo da comunidade MapBiomas
4. Preparação para futuros updates
5. Alinhamento com melhores práticas

**Próximos passos:**

1. Testar Collection 8 em ambiente de desenvolvimento
2. Verificar nome das bandas
3. Validar classificações
4. Atualizar código e testes
5. Deploy gradual (canary deployment)

---

## 📝 Código Atualizado Sugerido

```python
# fraud-detection-generate-maps/main.py

# Constantes atualizadas
MAPBIOMAS_COLLECTION = "8"
MAPBIOMAS_YEAR = "2022"  # Ano mais recente disponível
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1"

def generate_initial_map(land_use_mapbiomas_image):
    """
    Generates an initial map using MapBiomas Collection 8 data.

    Args:
        land_use_mapbiomas_image (ee.Image): MapBiomas Collection 8 image

    Returns:
        A `geemap.Map` object representing the initial map.
    """
    # Verificar nome da banda (pode ser classification_2022 ou product_2022)
    # Ajustar conforme necessário após testes
    land_use_layers_2022_simplified = (
        land_use_mapbiomas_image.select(f"classification_{MAPBIOMAS_YEAR}").divide(100).floor()
    )

    # Paleta de cores mantém-se igual
    vis_params = {
        "min": 1,
        "max": 7,
        "palette": [
            "#fffbc2",  # 1, 'Anthropic'
            "#09611f",  # 2, 'Primary Vegetation'
            "#4ea376",  # 3, 'Secondary Vegetation'
            "#e31a1c",  # 4, 'Deforestation in Primary Vegetation'
            "#94fc03",  # 5, 'Secondary Vegetation Regrowth'
            "#ffa500",  # 6, 'Deforestation in Secondary Vegetation'
            "#212121",  # 7, 'Not applied'
        ],
    }

    gee_mapbiomas_map = geemap.Map()
    gee_mapbiomas_map.addLayer(
        land_use_layers_2022_simplified,
        vis_params,
        f"{BRAZIL_LAND_USE_LAYER_NAME} (MapBiomas Collection {MAPBIOMAS_COLLECTION})"
    )
    return gee_mapbiomas_map
```

---

## 🔗 Referências

- **MapBiomas Project**: https://mapbiomas.org/
- **GEE Community Catalog**: https://gee-community-catalog.org/projects/mapbiomas/
- **MapBiomas User Toolkit**: https://github.com/mapbiomas-brazil/user-toolkit
- **Earth Engine Data Catalog**: https://developers.google.com/earth-engine/datasets/catalog/

---

## ⚠️ Notas Importantes

1. **Teste antes de deploy em produção**
2. **Mantenha backup da versão anterior**
3. **Documente mudanças de comportamento**
4. **Comunique stakeholders sobre atualização**
5. **Monitore métricas pós-atualização**

---

**Status**: ⚠️ Requer Ação  
**Prioridade**: Média-Alta  
**Esforço estimado**: 4-8 horas (incluindo testes)  
**Risco**: Baixo-Médio (com testes adequados)
