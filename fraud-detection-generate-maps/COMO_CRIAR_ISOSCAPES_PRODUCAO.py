"""
🗺️ GUIA: COMO CRIAR ISOSCAPES PARA PRODUÇÃO

Este documento explica como obter/criar isoscapes científicos válidos
para uso em análises reais de origem geográfica.
"""

print("=" * 80)
print("🗺️ COMO CRIAR ISOSCAPES PARA PRODUÇÃO")
print("=" * 80)

print("""
⚠️ AVISO IMPORTANTE:
Criar isoscapes científicos válidos é um processo que pode levar MESES ou ANOS.
Envolve coleta de amostras, análises laboratoriais, modelagem estatística e
validação por pares.

Você tem 3 OPÇÕES principais:
""")

print("=" * 80)
print("OPÇÃO 1: USAR ISOSCAPES PÚBLICOS EXISTENTES (RECOMENDADO)")
print("=" * 80)

print("""
🌐 IsoMAP (www.isomap.org)
   • Base de dados global de isoscapes
   • Mantido pela University of Utah
   • Isoscapes de precipitação (δ18O, δ2H)
   • Download gratuito em formato raster
   
   PASSOS:
   1. Acesse: https://isomap.org
   2. Selecione região: South America
   3. Selecione isótopo: δ18O in precipitation
   4. Download: GeoTIFF format
   5. Converter de precipitação → celulose (ver fórmulas abaixo)

🌿 assignR Package (R)
   • https://github.com/SPATIAL-Lab/assignR
   • Inclui isoscapes globais para δ18O e δ2H
   • Modelos de conversão para tecidos biológicos
   • Funções para criar isoscapes customizados
   
   PASSOS:
   1. Instalar R: https://www.r-project.org/
   2. Instalar assignR: install.packages("assignR")
   3. Carregar dados: data(d18o_world)
   4. Recortar para Brasil: crop() + mask()
   5. Exportar: writeRaster()

📚 Artigos Científicos com Dados Suplementares
   • Brienen et al. (2012) - Nature
   • Vuille et al. (2012) - Climate Dynamics
   • West et al. (2010) - GCB Bioenergy
   
   Muitos artigos disponibilizam dados em:
   • Zenodo (zenodo.org)
   • Dryad Digital Repository (datadryad.org)
   • Pangaea (pangaea.de)
""")

print("=" * 80)
print("OPÇÃO 2: CRIAR ISOSCAPE A PARTIR DE DADOS PRÓPRIOS")
print("=" * 80)

print("""
Se você tem DADOS DE CAMPO próprios (amostras coletadas e analisadas):

📋 REQUISITOS MÍNIMOS:
   • 50-100+ amostras distribuídas geograficamente
   • Coordenadas GPS precisas de cada amostra
   • Análises isotópicas em laboratório certificado
   • Metadados ambientais (clima, altitude, etc.)

🔬 PROCESSO COMPLETO:

1. COLETA DE AMOSTRAS (3-6 meses)
   ├─ Planejar amostragem representativa do Brasil
   ├─ Coletar amostras de madeira/celulose
   ├─ Registrar GPS, espécie, data, ambiente
   └─ Armazenar adequadamente (seco, refrigerado)

2. ANÁLISES LABORATORIAIS (2-4 meses)
   ├─ Preparação de amostras (limpeza, moagem)
   ├─ Extração de celulose (método Brendel/Jayme)
   ├─ Análise em IRMS (Isotope Ratio Mass Spectrometer)
   │  Laboratórios no Brasil:
   │  • CENA/USP (Piracicaba, SP)
   │  • EACH/USP (São Paulo, SP)
   │  • UNESP Rio Claro (SP)
   │  Custo: ~R$ 150-300 por amostra/isótopo
   └─ Controle de qualidade (replicatas, padrões)

3. MODELAGEM ESPACIAL (1-3 meses)
   ├─ Organizar dados: [lat, lon, δ18O, δ13C, δ15N]
   ├─ Análise exploratória (outliers, tendências)
   ├─ Modelagem geoestatística:
   │  a) Krigagem (método padrão)
   │  b) Regressão com variáveis ambientais
   │  c) Machine Learning (Random Forest, etc.)
   └─ Validação cruzada (LOOCV, k-fold)

4. GERAÇÃO DO RASTER (1-2 semanas)
   ├─ Interpolar valores para grid regular
   ├─ Calcular incerteza pixel-a-pixel
   ├─ Exportar 2 bandas: média + desvio padrão
   └─ Metadados (CRS, resolução, fonte, data)

5. VALIDAÇÃO INDEPENDENTE (2-4 meses)
   ├─ Coletar amostras de locais conhecidos
   ├─ "Esconder" origem e testar predição
   ├─ Calcular métricas (acurácia, precisão)
   └─ Refinar modelo se necessário

CUSTO ESTIMADO: R$ 50.000 - 150.000
   (100 amostras × R$ 500-1500 cada incluindo coleta + análise)

TEMPO TOTAL: 8-18 meses
""")

print("=" * 80)
print("OPÇÃO 3: USAR DADOS CLIMÁTICOS + MODELOS MECANÍSTICOS")
print("=" * 80)

print("""
Criar isoscapes SEM coleta de amostras, usando:
• Dados climáticos globais (WorldClim, ERA5)
• Modelos de fracionamento isotópico
• Equações físico-químicas conhecidas

🌡️ DADOS CLIMÁTICOS NECESSÁRIOS:
   • Temperatura média anual
   • Precipitação total anual
   • Umidade relativa
   • Altitude (DEM)
   • Latitude/longitude

📐 MODELOS DE FRACIONAMENTO:

Para δ18O em celulose a partir de δ18O na chuva:

   δ18O_celulose = δ18O_chuva + ε_total
   
   onde ε_total considera:
   • Fracionamento na absorção (raízes)
   • Fracionamento na evapotranspiração (folhas)
   • Fracionamento na síntese de celulose
   
   Valores típicos:
   ε_total ≈ +27‰ (para plantas C3 em clima tropical)

🐍 IMPLEMENTAÇÃO EM PYTHON:

import rasterio
import numpy as np
from rasterio.transform import from_bounds

# 1. Carregar dados climáticos (exemplo)
with rasterio.open('worldclim_precip_o18.tif') as src:
    precip_o18 = src.read(1)
    profile = src.profile

# 2. Aplicar modelo de fracionamento
enrichment_factor = 27.0  # ‰
cellulose_o18 = precip_o18 + enrichment_factor

# 3. Calcular incerteza (exemplo simplificado)
uncertainty = 1.5  # ‰ (baseado em literatura)
std_array = np.full_like(cellulose_o18, uncertainty)

# 4. Salvar isoscape
profile.update(count=2, dtype=rasterio.float32)
with rasterio.open('brazil_o18_cellulose.tif', 'w', **profile) as dst:
    dst.write(cellulose_o18, 1)
    dst.write(std_array, 2)

⚠️ LIMITAÇÕES:
   • Menos preciso que dados de campo
   • Não captura variações locais/microclimáticas
   • Incerteza maior
   • Requer validação com amostras reais

VANTAGEM:
   • Rápido (dias/semanas)
   • Baixo custo
   • Cobertura espacial completa
""")

print("=" * 80)
print("PASSO A PASSO PRÁTICO: OPÇÃO 1 (USAR ISOMAP)")
print("=" * 80)

print("""
Vou mostrar como usar dados do IsoMAP para criar um isoscape real:

1️⃣ DOWNLOAD DOS DADOS
   
   # Acesse IsoMAP
   https://isomap.org
   
   # Selecione:
   • Region: South America
   • Isotope: Growing Season δ18O Precipitation
   • Resolution: 10 km
   • Format: GeoTIFF
   
   # Baixe: GrowingSeasonAmount_d18O.tif

2️⃣ RECORTAR PARA BRASIL

import rasterio
import geopandas as gpd
from rasterio.mask import mask as rio_mask

# Carregar shapefile do Brasil
brazil = gpd.read_file('natural_earth_brazil.shp')

# Recortar isoscape global
with rasterio.open('GrowingSeasonAmount_d18O.tif') as src:
    brazil_precip_o18, transform = rio_mask(
        src, 
        shapes=brazil.geometry,
        crop=True,
        indexes=1
    )
    profile = src.profile
    profile.update({
        'height': brazil_precip_o18.shape[0],
        'width': brazil_precip_o18.shape[1],
        'transform': transform
    })

3️⃣ CONVERTER PRECIPITAÇÃO → CELULOSE

# Modelo de Sternberg et al. (1986) + Roden et al. (2000)
# δ18O_celulose ≈ δ18O_água_fonte + 27‰

cellulose_o18 = brazil_precip_o18 + 27.0

# Calcular incerteza (baseado em validação)
# Típico: ±2‰ para conversão chuva→celulose
uncertainty = np.full_like(cellulose_o18, 2.0, dtype=np.float32)

4️⃣ SALVAR ISOSCAPE FINAL

profile.update(count=2, dtype=rasterio.float32, nodata=-9999)

with rasterio.open('brazil_o18_cellulose_production.tif', 'w', **profile) as dst:
    dst.write(cellulose_o18.astype(np.float32), 1)
    dst.write(uncertainty, 2)
    
    # Adicionar metadados
    dst.update_tags(
        1, 
        description='δ18O in wood cellulose (‰ vs VSMOW)',
        source='IsoMAP + Sternberg model',
        date_created='2025-10-24',
        units='per mil'
    )

print("✅ Isoscape criado: brazil_o18_cellulose_production.tif")
""")

print("=" * 80)
print("RECURSOS E REFERÊNCIAS")
print("=" * 80)

print("""
📚 LITERATURA FUNDAMENTAL:

1. West et al. (2006) - "Stable isotopes as one of nature's ecological recorders"
   Trends in Ecology & Evolution
   → Introdução conceitual

2. Bowen (2010) - "Isoscapes: Spatial Pattern in Isotopic Biogeochemistry"
   Annual Review of Earth and Planetary Sciences
   → Teoria e aplicações

3. Bataille & Bowen (2012) - "Mapping 87Sr/86Sr variations in bedrock and water"
   Journal of Geophysical Research
   → Metodologia de modelagem

4. Brienen et al. (2012) - "Oxygen isotopes in tree rings are a good proxy for Amazon..."
   Nature
   → Dados específicos do Brasil

🔧 FERRAMENTAS:

• R assignR: https://github.com/SPATIAL-Lab/assignR
• Python rasterio: https://rasterio.readthedocs.io
• QGIS: https://qgis.org (visualização e edição)
• IsoMAP: https://isomap.org (dados globais)

💬 COMUNIDADE:

• IsoCamp: Workshops anuais sobre isótopos
• IsoEcology Google Group: discussões técnicas
• ResearchGate: contato com autores de papers

📧 LABORATÓRIOS NO BRASIL:

• CENA/USP: https://www.cena.usp.br/
  Email: cena@cena.usp.br
  
• EACH/USP: https://each.uspnet.usp.br/
  Laboratório de Cronologia - Geocronologia Isotópica
  
• UNESP Rio Claro:
  Centro de Estudos Ambientais
""")

print("=" * 80)
print("💡 RECOMENDAÇÃO FINAL")
print("=" * 80)

print("""
Para o sistema TimberID em PRODUÇÃO:

1. CURTO PRAZO (1-2 meses):
   ✅ Use dados do IsoMAP + modelo de conversão
   ✅ Valide com amostras de referência (se disponível)
   ✅ Documente limitações claramente
   
2. MÉDIO PRAZO (6-12 meses):
   ✅ Estabeleça parceria com universidade (CENA/USP, etc.)
   ✅ Planeje amostragem representativa do Brasil
   ✅ Solicite financiamento para análises laboratoriais
   
3. LONGO PRAZO (1-2 anos):
   ✅ Desenvolva isoscape proprietário com dados de campo
   ✅ Publique em revista científica (Nature, Science, etc.)
   ✅ Compartilhe com comunidade (open science)

ATENÇÃO:
• Isoscapes sintéticos (atuais) são APENAS para testes/desenvolvimento
• NÃO use em decisões judiciais ou comerciais
• Sempre valide com amostras de origem conhecida antes de produção
""")

print("=" * 80)
print("📞 PRÓXIMOS PASSOS PRÁTICOS")
print("=" * 80)

print("""
Posso ajudar você a:

1. ✅ Baixar e processar dados do IsoMAP para o Brasil
2. ✅ Criar script de conversão precipitação → celulose
3. ✅ Implementar validação com amostras de referência
4. ✅ Conectar com pesquisadores/laboratórios brasileiros
5. ✅ Planejar estratégia de amostragem de campo

Qual opção você prefere seguir?
""")

print("=" * 80)
