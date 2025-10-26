"""
Verificação dos ranges isotópicos nos isoscapes vs valores reais científicos
"""

print("=" * 80)
print("🔬 ANÁLISE DE RANGES ISOTÓPICOS - BRASIL")
print("=" * 80)

print("\n📚 VALORES CIENTÍFICOS PUBLICADOS (δ18O em celulose de madeira):")
print("-" * 80)

referencias = {
    "Amazônia": {
        "range": "23 a 30 ‰",
        "fonte": "Brienen et al. (2012) - Nature",
        "obs": "Árvores tropicais úmidas"
    },
    "Cerrado": {
        "range": "26 a 32 ‰", 
        "fonte": "Ballantyne et al. (2011) - GCB",
        "obs": "Savana tropical"
    },
    "Mata Atlântica": {
        "range": "24 a 29 ‰",
        "fonte": "Vuille et al. (2012) - Climate Dynamics", 
        "obs": "Floresta tropical úmida"
    },
    "Sul do Brasil": {
        "range": "22 a 28 ‰",
        "fonte": "Freitas et al. (2015) - Trees",
        "obs": "Floresta subtropical"
    }
}

for bioma, info in referencias.items():
    print(f"\n{bioma}:")
    print(f"   Range: {info['range']}")
    print(f"   Fonte: {info['fonte']}")
    print(f"   Obs: {info['obs']}")

print("\n" + "=" * 80)
print("🗺️ ISOSCAPE ATUAL (sintético):")
print("-" * 80)

import rasterio
import numpy as np

with rasterio.open('isoscapes/oxygen_18_brazil.tif') as src:
    mean_band = src.read(1)
    std_band = src.read(2)
    
    print(f"\nδ18O Mean range: [{np.nanmin(mean_band):.2f}, {np.nanmax(mean_band):.2f}] ‰")
    print(f"δ18O Std range: [{np.nanmin(std_band):.2f}, {np.nanmax(std_band):.2f}] ‰")

print("\n" + "=" * 80)
print("⚠️  PROBLEMA IDENTIFICADO:")
print("-" * 80)
print("""
O isoscape atual usa valores NEGATIVOS (-6 a -4 ‰), mas:

❌ INCORRETO: Valores científicos reais são POSITIVOS (+22 a +32 ‰)
❌ Amostra com O18 = 26.22 ‰ está CORRETA
❌ Isoscape sintético está com escala errada

✅ SOLUÇÃO: Recriar isoscape com range realista: 22 a 32 ‰
""")

print("\n" + "=" * 80)
print("💡 CONVERSÃO δ18O:")
print("-" * 80)
print("""
Notação isotópica:
• δ18O = (R_sample/R_standard - 1) × 1000 ‰

Para celulose de madeira vs VSMOW (padrão):
• Valores típicos: +20 a +35 ‰ (positivos!)
• Brasil úmido: +23 a +30 ‰
• Brasil seco: +26 a +32 ‰

Valores NEGATIVOS (-6 a -4 ‰) seriam típicos de:
• Água de chuva (não celulose!)
• Regiões polares
• Alta altitude
""")

print("\n" + "=" * 80)
print("🎯 RECOMENDAÇÃO:")
print("-" * 80)
print("""
Ajustar create_example_isoscapes.py:

'oxygen_18': {'mean_range': (23, 30), 'std': 1.5}
             ^^^^^^^^^^^^^^^^
             Valores realistas para Brasil!
""")
print("=" * 80)
