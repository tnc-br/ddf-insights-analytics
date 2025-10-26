import rasterio
import numpy as np

print("=" * 80)
print("🗺️ EXPLICAÇÃO DOS ARQUIVOS ISOSCAPES")
print("=" * 80)

files = {
    'isoscapes/oxygen_18_brazil.tif': 'Oxigênio-18 (δ18O)',
    'isoscapes/carbon_13_brazil.tif': 'Carbono-13 (δ13C)', 
    'isoscapes/nitrogen_15_brazil.tif': 'Nitrogênio-15 (δ15N)'
}

for filepath, name in files.items():
    print(f"\n📊 {name}")
    print(f"   Arquivo: {filepath}")
    
    with rasterio.open(filepath) as src:
        mean_band = src.read(1)
        std_band = src.read(2)
        
        print(f"   Bandas: {src.count} (banda 1 = média, banda 2 = desvio padrão)")
        print(f"   Dimensões: {src.height}x{src.width} pixels")
        print(f"   CRS: {src.crs}")
        print(f"   Banda 1 (μ): {np.nanmin(mean_band):.2f} a {np.nanmax(mean_band):.2f} ‰")
        print(f"   Banda 2 (σ): {np.nanmin(std_band):.2f} a {np.nanmax(std_band):.2f} ‰")

print("\n" + "=" * 80)
print("🔬 O QUE SÃO ISOSCAPES?")
print("=" * 80)
print("""
Um ISOSCAPE (Isotopic Landscape) é um mapa geoespacial que representa a 
distribuição espacial de composições isotópicas em uma região.

Pense nele como um "mapa de temperatura", mas ao invés de temperatura,
mostra valores isotópicos!
""")

print("=" * 80)
print("📐 ESTRUTURA DE UM ISOSCAPE (GeoTIFF)")
print("=" * 80)
print("""
Cada arquivo .tif contém 2 BANDAS:

┌─────────────────────────────────────┐
│ BANDA 1: MÉDIA (μ)                  │  ← Valor isotópico esperado
│ Cada pixel = δ18O médio na região   │     naquela localização
├─────────────────────────────────────┤
│ BANDA 2: DESVIO PADRÃO (σ)          │  ← Incerteza/variabilidade
│ Cada pixel = variação do δ18O       │     natural do valor
└─────────────────────────────────────┘

Exemplo prático:
  Pixel (lat=-13°, lon=-53°):
    • Banda 1: 26.5 ‰  → "O valor típico de δ18O aqui é 26.5"
    • Banda 2: 1.2 ‰   → "Varia ±1.2 em torno desse valor"
""")

print("=" * 80)
print("🎯 PARA QUE SERVEM?")
print("=" * 80)
print("""
Os isoscapes são usados para ANÁLISE DE ORIGEM geográfica:

1. 📍 ENTRADA: Você tem uma amostra de madeira com δ18O = 26.22 ‰

2. 🗺️ PROCESSAMENTO: O algoritmo compara esse valor com TODOS os pixels
   do isoscape, calculando:
   
   P(origem no pixel X) = Normal(26.22 | μ_pixel, σ_pixel)
   
3. 🎨 SAÍDA: Mapa de probabilidade mostrando:
   - AMARELO/VERDE: Alta probabilidade (valores compatíveis)
   - ROXO/AZUL: Baixa probabilidade (valores incompatíveis)
   - BRANCO: Sem dados

Interpretação: "Onde no Brasil essa madeira poderia ter crescido?"
""")

print("=" * 80)
print("🧪 POR QUE 3 ISÓTOPOS DIFERENTES?")
print("=" * 80)
print("""
Cada isótopo revela informações ambientais diferentes:

• δ18O (Oxigênio-18):
  → Relacionado à PRECIPITAÇÃO e UMIDADE
  → Varia com altitude, latitude e distância do oceano
  → Valores altos = regiões mais secas/interiores
  
• δ13C (Carbono-13):
  → Relacionado à FOTOSSÍNTESE e tipo de vegetação
  → C3 (árvores): -30 a -24 ‰
  → C4 (gramíneas): -15 a -9 ‰
  → Indica densidade de dossel/luz disponível
  
• δ15N (Nitrogênio-15):
  → Relacionado à DISPONIBILIDADE DE NITROGÊNIO no solo
  → Valores altos = solos degradados ou secos
  → Valores baixos = florestas primárias úmidas

VANTAGEM: Usar 3 isótopos simultaneamente aumenta a PRECISÃO da análise!
""")

print("=" * 80)
print("⚙️ COMO SÃO USADOS NO CÓDIGO?")
print("=" * 80)
print("""
1. Modo SINGLE-ISOSCAPE (1 arquivo):
   
   pd_raster(
       r='isoscapes/oxygen_18_brazil.tif',  # ← Apenas δ18O
       unknown=DataFrame({'ID': ['amostra'], 'O18': [26.22]}),
       ...
   )
   
   Usa: Normal univariada
   Função: P(x) = (1/√(2πσ²)) × exp(-(x-μ)²/2σ²)

2. Modo MULTI-ISOSCAPE (3 arquivos):
   
   pd_raster(
       r=['oxygen_18.tif', 'carbon_13.tif', 'nitrogen_15.tif'],  # Lista!
       unknown=DataFrame({
           'ID': ['amostra'],
           'O18': [26.22],
           'C13': [-27.5],
           'N15': [4.2]
       }),
       ...
   )
   
   Usa: Normal multivariada
   Função: P(x) = (1/√((2π)^k|Σ|)) × exp(-½(x-μ)ᵀΣ⁻¹(x-μ))
   
   Considera CORRELAÇÕES entre isótopos (mais preciso!)
""")

print("=" * 80)
print("📦 FORMATO GEOTIFF")
print("=" * 80)
print("""
Os arquivos .tif são rasters geoespaciais padrão:

• Formato: GeoTIFF (Tagged Image File Format + georreferenciamento)
• Leitura: Qualquer software GIS (QGIS, ArcGIS, Python rasterio)
• Georeferencing: Sistema de coordenadas definido (EPSG:4326 = WGS84)
• Pixels: Cada pixel = área geográfica (aqui: 0.1° ≈ 11km)
• NoData: Pixels sem dados (oceano, regiões fora do Brasil)

Abrir no QGIS para visualizar:
  Layer → Add Raster Layer → oxygen_18_brazil.tif
""")

print("=" * 80)
print("🌍 GERAÇÃO DESTES ARQUIVOS")
print("=" * 80)
print("""
ATUAL: Dados sintéticos gerados por create_example_isoscapes.py
  → Gradientes artificiais baseados em coordenadas geográficas
  → Bom para TESTES e DEMONSTRAÇÃO
  → NÃO usar para análises reais!

PRODUÇÃO: Isoscapes científicos validados
  → Compilados de centenas de amostras reais
  → Modelagem climática + medições de campo
  → Fontes: IsoMAP (isomap.org), artigos científicos
  → Processo: anos de pesquisa e validação
""")

print("=" * 80)
print("💡 RESUMO EXECUTIVO")
print("=" * 80)
print("""
🗺️ ISOSCAPES = "Mapas de Referência Isotópica"

   Cada pixel contém: (valor_esperado, incerteza)
   
   Usado para: "Onde essa amostra poderia ter vindo?"
   
   Método: Comparação estatística Bayesiana
   
   Output: Mapa de probabilidade de origem
   
   Precisão: Aumenta com mais isótopos (1 → 3)
""")
print("=" * 80)
