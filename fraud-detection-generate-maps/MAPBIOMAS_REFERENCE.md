# 🗺️ MapBiomas Collection 8 - Referência Completa

## 📚 Links Oficiais

### Documentação Principal

- **Site Oficial:** https://mapbiomas.org/
- **MapBiomas Brasil:** https://brasil.mapbiomas.org/
- **Collection 8:** https://brasil.mapbiomas.org/colecao-8/
- **Plataforma Web:** https://plataforma.brasil.mapbiomas.org/

### Recursos Técnicos

- **Earth Engine Catalog:** https://gee-community-catalog.org/projects/mapbiomas/
- **GitHub:** https://github.com/mapbiomas-brazil
- **Código Toolkit:** https://github.com/mapbiomas-brazil/mapbiomas-toolkit
- **API de Estatísticas:** https://plataforma.brasil.mapbiomas.org/api

### Downloads

- **Dados para Download:** https://storage.googleapis.com/mapbiomas-public/brasil/collection-8/
- **Relatórios:** https://brasil.mapbiomas.org/download/

## 🎯 O que é o MapBiomas Collection 8?

### Descrição

Mapeamento anual da cobertura e uso do solo do Brasil de **1985 a 2022** (38 anos).

### Especificações Técnicas

- **Resolução Espacial:** 30 metros
- **Cobertura:** Todo território brasileiro
- **Período:** 1985-2022 (38 anos)
- **Atualização:** Anual
- **Fonte:** Imagens Landsat
- **Classes:** 49 classes diferentes de uso e cobertura do solo
- **Precisão Geral:** ~90% (varia por classe)

### Biomas Cobertos

- Amazônia
- Cerrado
- Mata Atlântica
- Caatinga
- Pampa
- Pantanal

## 🔗 Earth Engine Asset Path

### Caminho Completo

```
projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1
```

### Estrutura do Caminho

```
projects/                                    → Tipo: Projeto GEE
  mapbiomas-public/                          → Organização MapBiomas (público)
    assets/                                  → Pasta de recursos
      brazil/                                → País: Brasil
        lulc/                                → Land Use and Land Cover
          collection8/                       → Coleção 8 (versão atual)
            mapbiomas_collection80_          → Nome do dataset
            integration_v1                   → Versão de integração
```

### Outros Assets Disponíveis

```
# Transições (mudanças entre anos)
projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_transitions_v1

# Qualidade (quality assessment)
projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_quality_v1

# Cobertura (cover)
projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_cover_v1
```

## 📊 Estrutura dos Dados

### Bandas Disponíveis

O asset `mapbiomas_collection80_integration_v1` contém **38 bandas**:

```
classification_1985    → Classificação de uso do solo em 1985
classification_1986    → Classificação de uso do solo em 1986
classification_1987    → Classificação de uso do solo em 1987
...
classification_2020    → Classificação de uso do solo em 2020
classification_2021    → Classificação de uso do solo em 2021
classification_2022    → Classificação de uso do solo em 2022
```

### Valores dos Pixels

Cada pixel contém um valor de **0 a 49** representando a classe de uso do solo.

## 🎨 Classes de Uso do Solo (Collection 8)

### Hierarquia Completa

#### 1. FLORESTA (Forest)

| Código | Classe             | Inglês                     | Cor Hex |
| ------ | ------------------ | -------------------------- | ------- |
| 1      | Floresta           | Forest                     | #129912 |
| 3      | Formação Florestal | Forest Formation           | #1f4423 |
| 4      | Formação Savânica  | Savanna Formation          | #006400 |
| 5      | Mangue             | Mangrove                   | #00ff00 |
| 49     | Restinga Arbórea   | Wooded Sandbank Vegetation | #687537 |
| 6      | Floresta Alagável  | Floodable Forest           | #02d659 |

#### 2. FORMAÇÃO NATURAL NÃO FLORESTAL

| Código | Classe                         | Inglês                         | Cor Hex |
| ------ | ------------------------------ | ------------------------------ | ------- |
| 10     | Formação Natural não Florestal | Natural Non Forest Formation   | #d6bc74 |
| 11     | Área Úmida                     | Wetland                        | #935132 |
| 12     | Campo                          | Grassland                      | #bbfcac |
| 32     | Apicum                         | Salt Flat                      | #45c2a5 |
| 29     | Afloramento Rochoso            | Rocky Outcrop                  | #b8af4f |
| 50     | Restinga Herbácea              | Herbaceous Sandbank Vegetation | #f1c232 |
| 13     | Outras Formações               | Other Non Forest Formations    | #ffffb2 |

#### 3. AGROPECUÁRIA

| Código | Classe                      | Inglês                | Cor Hex |
| ------ | --------------------------- | --------------------- | ------- |
| 14     | Agropecuária                | Farming               | #ea9999 |
| 15     | Pastagem                    | Pasture               | #ffd966 |
| 18     | Agricultura                 | Agriculture           | #e974ed |
| 19     | Culturas Temporárias        | Temporary Crops       | #d5a6bd |
| 39     | Soja                        | Soy Beans             | #c27ba0 |
| 20     | Cana-de-açúcar              | Sugar Cane            | #fff3bf |
| 40     | Arroz                       | Rice                  | #ea9999 |
| 62     | Algodão                     | Cotton                | #dd7e6b |
| 41     | Outras Culturas Temporárias | Other Temporary Crops | #aa0000 |
| 36     | Culturas Perenes            | Perennial Crops       | #ff99ff |
| 46     | Café                        | Coffee                | #d68fe2 |
| 47     | Citrus                      | Citrus                | #9c6f38 |
| 35     | Palma de Óleo               | Palm Oil              | #0000ff |
| 48     | Outras Culturas Perenes     | Other Perennial Crops | #d082de |
| 9      | Silvicultura                | Forest Plantation     | #cd49e4 |
| 21     | Mosaico de Usos             | Mosaic of Uses        | #e6ccff |

#### 4. ÁREA NÃO VEGETADA

| Código | Classe                     | Inglês                    | Cor Hex |
| ------ | -------------------------- | ------------------------- | ------- |
| 22     | Área não Vegetada          | Non Vegetated Area        | #af2a2a |
| 23     | Praia e Duna               | Beach and Dune            | #af2a2a |
| 24     | Infraestrutura Urbana      | Urban Infrastructure      | #8a2be2 |
| 30     | Mineração                  | Mining                    | #968c46 |
| 25     | Outras Áreas não Vegetadas | Other Non Vegetated Areas | #ff0000 |

#### 5. CORPO D'ÁGUA

| Código | Classe             | Inglês                | Cor Hex |
| ------ | ------------------ | --------------------- | ------- |
| 26     | Corpo D'água       | Water                 | #0000ff |
| 33     | Rio, Lago e Oceano | River, Lake and Ocean | #45c2a5 |
| 31     | Aquicultura        | Aquaculture           | #b5b5b5 |

#### 6. NÃO OBSERVADO

| Código | Classe        | Inglês       | Cor Hex |
| ------ | ------------- | ------------ | ------- |
| 27     | Não Observado | Not Observed | #6b9932 |

## 💻 Código de Exemplo

### Python (Earth Engine API)

```python
import ee

# Inicializar Earth Engine
ee.Initialize(project='seu-projeto-id')

# Carregar MapBiomas Collection 8
mapbiomas = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1')

# Selecionar apenas o ano 2021
lulc_2021 = mapbiomas.select('classification_2021')

# Ver informações
print('Bandas disponíveis:', mapbiomas.bandNames().getInfo())
print('Projeção:', lulc_2021.projection().getInfo())

# Criar visualização
vis_params = {
    'min': 0,
    'max': 49,
    'palette': ['#129912', '#1f4423', '#006400', ...]  # Paleta completa
}

# Adicionar ao mapa (com geemap)
import geemap
Map = geemap.Map()
Map.addLayer(lulc_2021, vis_params, 'MapBiomas 2021')
Map.centerObject(lulc_2021, 4)
Map
```

### JavaScript (Earth Engine Code Editor)

```javascript
// Carregar MapBiomas Collection 8
var mapbiomas = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1');

// Selecionar apenas 2021
var lulc_2021 = mapbiomas.select('classification_2021');

// Parâmetros de visualização
var vis = {
  min: 0,
  max: 49,
  palette: ['#129912', '#1f4423', '#006400', ...]  // Paleta completa
};

// Adicionar ao mapa
Map.addLayer(lulc_2021, vis, 'MapBiomas 2021');
Map.setCenter(-55.0, -10.0, 4);  // Centro do Brasil

// Imprimir informações
print('Bandas:', mapbiomas.bandNames());
print('Info:', lulc_2021);
```

## 🔍 Como Nosso Código Usa o MapBiomas

### 1. Carregar a Imagem Completa (38 anos)

```python
land_use_mapbiomas_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
# Carrega: projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1
```

**Resultado:** Objeto `ee.Image` com 38 bandas (1985-2022)

### 2. Selecionar Apenas 2021

```python
land_use_layers_2021_simplified = (
    land_use_mapbiomas_image.select("classification_2021")
)
```

**O que faz:**

- Pega a imagem completa (38 bandas)
- Extrai **apenas** a banda `classification_2021`
- Armazena em `land_use_layers_2021_simplified`

**Por que 2021?**

- É o ano mais recente com dados completos e validados
- 2022 pode ter áreas ainda em validação
- Queremos mostrar a situação **atual** do uso do solo

**Analogia:**

```
Imagine um livro com 38 capítulos (1985-2022)
.select("classification_2021") → Pega APENAS o capítulo 37 (2021)
```

### 3. Aplicar Visualização

```python
vis_params = {
    "min": 0,
    "max": 49,
    "palette": [...]  # 33 cores
}

gee_mapbiomas_map.addLayer(land_use_layers_2021_simplified, vis_params, "Brazil Land Use")
```

**O que faz:**

- Define que valores 0-49 terão cores específicas
- Floresta (3) = Verde escuro (#1f4423)
- Pastagem (15) = Amarelo (#ffd966)
- Água (33) = Azul (#45c2a5)
- etc.

## 📈 Estatísticas e Análises

### API de Estatísticas

```python
# Endpoint
https://plataforma.brasil.mapbiomas.org/api/v1/statistics

# Exemplo: Área de cada classe em 2021
GET /api/v1/statistics?year=2021&territory=1&classification=1
```

### Calcular Área de uma Classe

```python
# Calcular área de Floresta (classe 3) em 2021
forest_2021 = lulc_2021.eq(3)  # Máscara onde valor = 3
area = forest_2021.multiply(ee.Image.pixelArea()).reduceRegion(
    reducer=ee.Reducer.sum(),
    geometry=brazil_boundary,
    scale=30,
    maxPixels=1e13
)
print('Área de floresta (m²):', area.getInfo())
```

## 🎓 Tutoriais e Recursos

### Tutoriais Oficiais

- **MapBiomas Toolkit:** https://github.com/mapbiomas-brazil/mapbiomas-toolkit
- **Vídeos YouTube:** https://www.youtube.com/@mapbiomas

### Artigos Científicos

- **Paper Collection 8:** https://www.nature.com/articles/s41597-024-03095-2
- **Metodologia:** https://mapbiomas.org/download-dos-atbds

### Cursos

- **Earth Engine for MapBiomas:** https://www.youtube.com/watch?v=... (buscar no canal)

## 📞 Suporte e Comunidade

### Contato

- **Email:** contato@mapbiomas.org
- **Forum:** https://groups.google.com/g/mapbiomas

### Citação

```
MapBiomas Project - Collection 8.0 of Brazilian Land Cover & Use Map Series,
accessed on [DATE] through the link: https://mapbiomas.org
```

## 🔄 Diferenças entre Versions

### Integration vs Cover vs Transitions

| Asset              | Descrição                     | Uso                     |
| ------------------ | ----------------------------- | ----------------------- |
| **integration_v1** | Dados integrados (filtrados)  | Mapeamento geral        |
| **cover_v1**       | Dados brutos de classificação | Análises avançadas      |
| **transitions_v1** | Mudanças entre anos           | Análise de desmatamento |
| **quality_v1**     | Qualidade da classificação    | Validação               |

**Nós usamos:** `integration_v1` (dados integrados e filtrados)

## ⚙️ Parâmetros de Performance

### Recomendações

- **Scale:** 30m (nativo Landsat)
- **Max Pixels:** 1e13 para Brasil inteiro
- **Região:** Usar geometria específica quando possível
- **Cache:** Usar `ee.Image.load()` para evitar recarregamentos

### Exemplo Otimizado

```python
# Definir região de interesse
roi = ee.Geometry.Point([-53.3795, -13.0845]).buffer(10000)  # 10km

# Clip para região
lulc_roi = lulc_2021.clip(roi)

# Processar apenas a região necessária
vis_roi = lulc_roi.getMapId(vis_params)
```

## 📝 Notas Importantes

### Limitações

1. Resolução de 30m (não detecta pequenas áreas)
2. Classificação automática (pode ter erros)
3. Nuvens podem afetar algumas áreas
4. Atualização anual (não tempo real)

### Validação

- Acurácia geral ~90%
- Varia por classe e bioma
- Floresta: ~95%
- Pastagem: ~85%
- Agricultura: ~80%

### Licença

**Creative Commons CC-BY-SA**

- ✅ Uso livre (até comercial)
- ✅ Modificação permitida
- ⚠️ Citação obrigatória
- ⚠️ Mesma licença para derivados

---

**Última atualização:** Collection 8 (2024)  
**Próxima coleção:** Collection 9 (previsão 2025)
