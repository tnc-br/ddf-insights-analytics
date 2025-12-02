"""
Teste da nova versão com probabilidades estatísticas
(em vez de densidade normalizada)

Demonstra o mapa colorido:
- Verde (≥95%): Pixels altamente compatíveis com a amostra
- Amarelo (5-95%): Pixels com compatibilidade média
- Vermelho (<5%): Pixels incompatíveis com a amostra
"""

import os
import sys
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_bounds
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from generate_new_mapa import pd_raster


def create_test_isoscape_realistic(output_path, width=200, height=200):
    """
    Cria isoscape com gradiente realista de δ18O.
    """
    print(f"📊 Criando isoscape: {output_path}")
    
    west, south, east, north = -74, -34, -34, 5
    transform = from_bounds(west, south, east, north, width, height)
    
    # Gradiente latitudinal (mais negativo no sul do Brasil)
    y_coords = np.linspace(north, south, height)
    mean_values = np.tile(y_coords[:, np.newaxis], (1, width))
    mean_values = -30 + (mean_values + 34) * 1.5  # -30‰ a +28‰
    
    # Desvio padrão variável (maior incerteza nas bordas)
    x_coords = np.linspace(0, 1, width)
    y_grid, x_grid = np.meshgrid(np.linspace(0, 1, height), np.linspace(0, 1, width), indexing='ij')
    
    # SD maior nas bordas, menor no centro
    dist_from_center = np.sqrt((x_grid - 0.5)**2 + (y_grid - 0.5)**2)
    sd_values = 1.5 + dist_from_center * 3.0  # 1.5‰ a 4.5‰
    
    profile = {
        'driver': 'GTiff',
        'dtype': 'float32',
        'nodata': -9999,
        'width': width,
        'height': height,
        'count': 2,
        'crs': 'EPSG:4326',
        'transform': transform
    }
    
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(mean_values.astype('float32'), 1)
        dst.write(sd_values.astype('float32'), 2)
        dst.set_band_description(1, 'Mean O18')
        dst.set_band_description(2, 'SD O18')
    
    print(f"   ✅ Criado: {width}x{height} pixels")
    print(f"   📍 δ18O: {mean_values.min():.1f}‰ a {mean_values.max():.1f}‰")
    print(f"   📊 SD: {sd_values.min():.1f}‰ a {sd_values.max():.1f}‰")
    return output_path


def test_probability_maps():
    """
    Testa a nova versão com probabilidades estatísticas.
    """
    print("=" * 70)
    print("🧪 TESTE: Mapas de Probabilidade Estatística")
    print("=" * 70)
    print()
    
    test_dir = Path(__file__).parent / "test_probability_output"
    test_dir.mkdir(exist_ok=True)
    
    # Criar isoscape
    isoscape_path = test_dir / "test_isoscape.tif"
    create_test_isoscape_realistic(isoscape_path, width=150, height=150)
    print()
    
    # Criar amostras com diferentes compatibilidades
    print("📝 Criando amostras de teste...")
    unknown_samples = pd.DataFrame({
        'ID': ['match_center', 'match_south', 'no_match'],
        'O18': [-15.0, -25.0, 50.0]  # Centro (match), Sul (match), Fora (no match)
    })
    print(unknown_samples)
    print()
    print("🔬 Análise esperada:")
    print("   • match_center (-15‰): Verde no centro do Brasil")
    print("   • match_south (-25‰): Verde no sul do Brasil")
    print("   • no_match (50‰): Vermelho em todo lugar (valor impossível)")
    print()
    
    # Gerar mapas
    print("🔧 Gerando mapas de probabilidade...")
    print("-" * 70)
    
    prob_maps = pd_raster(
        r=str(isoscape_path),
        unknown=unknown_samples,
        genplot=True,
        out_dir=str(test_dir)
    )
    
    print()
    print("📊 Estatísticas dos mapas gerados:")
    print("-" * 70)
    
    for i, prob_map in enumerate(prob_maps):
        sample_id = unknown_samples.iloc[i, 0]
        sample_value = unknown_samples.iloc[i, 1]
        
        valid_probs = prob_map[prob_map != -9999]
        
        # Contar pixels por categoria
        high_prob = np.sum(valid_probs >= 95)
        medium_prob = np.sum((valid_probs >= 5) & (valid_probs < 95))
        low_prob = np.sum(valid_probs < 5)
        total = len(valid_probs)
        
        print(f"\n{sample_id} (δ18O = {sample_value:.1f}‰):")
        print(f"   🟢 Alta (≥95%):    {high_prob:5d} pixels ({high_prob/total*100:5.1f}%)")
        print(f"   🟡 Média (5-95%):  {medium_prob:5d} pixels ({medium_prob/total*100:5.1f}%)")
        print(f"   🔴 Baixa (<5%):    {low_prob:5d} pixels ({low_prob/total*100:5.1f}%)")
        print(f"   📈 Max prob:       {valid_probs.max():.2f}%")
        print(f"   📉 Min prob:       {valid_probs.min():.2e}%")
    
    print()
    print("=" * 70)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 70)
    print()
    print("📁 Resultados salvos em:", test_dir)
    print()
    print("🎨 Legenda do mapa:")
    print("   🟢 Verde:    ≥95% - Pixels altamente compatíveis")
    print("   🟡 Amarelo:  5-95% - Compatibilidade média")
    print("   🔴 Vermelho: <5% - Pixels incompatíveis")
    print()
    print("💡 Interpretação:")
    print("   Verde = 'É muito provável que a amostra venha daqui'")
    print("   Vermelho = 'É improvável que a amostra venha daqui'")
    print()


if __name__ == "__main__":
    test_probability_maps()
