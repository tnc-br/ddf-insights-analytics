#!/usr/bin/env python3
"""
🧪 TESTE: create_mapa_local.py com Probabilidade Estatística

Valida que create_mapa_local.py foi atualizado corretamente para usar
z-test estatístico em vez de densidade normalizada.

VERIFICAÇÕES:
✅ Algoritmo usa z-test bilateral (norm.sf)
✅ Valores são percentuais (0-100), não densidades (sum=1.0)
✅ Colormap categórico (verde/amarelo/vermelho)
✅ Metadados corretos no GeoTIFF
"""

import os
import sys
import numpy as np
import pandas as pd
import rasterio
import geopandas as gpd
from scipy.stats import norm
import matplotlib.pyplot as plt

# Import from create_mapa_local.py
sys.path.insert(0, os.path.dirname(__file__))

# Create synthetic test data
def create_test_isoscape():
    """Cria isoscape sintético 100x100 pixels"""
    
    # Gradient: -30‰ (top) to -10‰ (bottom)
    height, width = 100, 100
    
    mean_values = np.linspace(-30, -10, height)
    mean_band = np.tile(mean_values[:, np.newaxis], (1, width))
    
    # Constant error: 3‰
    sd_band = np.full((height, width), 3.0)
    
    # Add some noise
    mean_band += np.random.normal(0, 0.5, (height, width))
    
    # Create GeoTIFF
    transform = rasterio.transform.from_bounds(
        -75, -35, -35, -5,  # West, South, East, North (Brasil bounds)
        width, height
    )
    
    profile = {
        'driver': 'GTiff',
        'dtype': 'float64',
        'width': width,
        'height': height,
        'count': 2,
        'crs': 'EPSG:4326',
        'transform': transform,
        'compress': 'lzw'
    }
    
    output_path = 'test_create_mapa_output/test_isoscape.tif'
    os.makedirs('test_create_mapa_output', exist_ok=True)
    
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(mean_band, 1)
        dst.write(sd_band, 2)
    
    print(f"✅ Created test isoscape: {output_path}")
    print(f"   • Size: {width}×{height}")
    print(f"   • δ18O range: {mean_band.min():.2f}‰ to {mean_band.max():.2f}‰")
    print(f"   • SD: {sd_band.mean():.2f}‰")
    
    return output_path, mean_band, sd_band, profile

def validate_algorithm():
    """Valida que algoritmo usa z-test (não densidade normalizada)"""
    
    print("\n" + "="*70)
    print("🧪 TESTE 1: Validar Algoritmo Z-Test")
    print("="*70)
    
    # Create test data
    isoscape_path, mean_band, sd_band, profile = create_test_isoscape()
    
    # Test sample: -20‰ (should match center of gradient)
    test_sample = pd.DataFrame({
        'ID': ['test_sample_center'],
        'O18': [-20.0]
    })
    
    # Import and run pd_raster
    from create_mapa_local import pd_raster
    
    result = pd_raster(
        r=isoscape_path,
        unknown=test_sample,
        prior=None,
        mask=None,
        genplot=False,
        out_dir='test_create_mapa_output'
    )
    
    # Load generated raster
    prob_path = 'test_create_mapa_output/prob_test_sample_center.tif'
    
    if not os.path.exists(prob_path):
        print("❌ FALHA: Arquivo de probabilidade não gerado!")
        return False
    
    with rasterio.open(prob_path) as src:
        prob_surface = src.read(1)
        band_desc = src.descriptions[0]
    
    # VALIDAÇÃO 1: Verificar metadados
    print(f"\n📊 Metadados da banda:")
    print(f"   • Descrição: {band_desc}")
    
    if 'z-test' not in band_desc.lower():
        print("❌ FALHA: Metadados não indicam z-test!")
        return False
    
    print("✅ Metadados corretos (z-test)")
    
    # VALIDAÇÃO 2: Verificar valores são percentuais (0-100), não densidade normalizada
    prob_valid = prob_surface[~np.isnan(prob_surface)]
    prob_sum = np.sum(prob_valid)
    prob_min = np.min(prob_valid)
    prob_max = np.max(prob_valid)
    
    print(f"\n📊 Estatísticas dos valores:")
    print(f"   • Mínimo: {prob_min:.6f}")
    print(f"   • Máximo: {prob_max:.6f}")
    print(f"   • Soma: {prob_sum:.2f}")
    
    # Se fosse densidade normalizada, soma deveria ser ~1.0
    # Se é probabilidade estatística, soma será >> 1.0
    if abs(prob_sum - 1.0) < 0.01:
        print("❌ FALHA: Valores parecem densidade normalizada (soma ≈ 1.0)!")
        return False
    
    print("✅ Valores são probabilidades independentes (não normalizadas)")
    
    # VALIDAÇÃO 3: Verificar algoritmo z-test manualmente
    sample_value = -20.0
    
    # Calcular z-test manualmente para pixel central
    center_y, center_x = mean_band.shape[0] // 2, mean_band.shape[1] // 2
    mean_center = mean_band[center_y, center_x]
    sd_center = sd_band[center_y, center_x]
    
    # Z-score
    z_score = abs((sample_value - mean_center) / sd_center)
    
    # P-value (two-tailed)
    p_value = 2 * norm.sf(z_score)
    prob_percentage_expected = p_value * 100
    
    # Comparar com valor gerado
    prob_center_generated = prob_surface[center_y, center_x]
    
    print(f"\n🔬 Validação manual do pixel central:")
    print(f"   • Sample: {sample_value}‰")
    print(f"   • Mean: {mean_center:.2f}‰")
    print(f"   • SD: {sd_center:.2f}‰")
    print(f"   • Z-score: {z_score:.4f}")
    print(f"   • P-value: {p_value:.6f}")
    print(f"   • Probabilidade esperada: {prob_percentage_expected:.2f}%")
    print(f"   • Probabilidade gerada: {prob_center_generated:.2f}%")
    
    # Tolerância de 1%
    if abs(prob_center_generated - prob_percentage_expected) > 1.0:
        print("❌ FALHA: Algoritmo não corresponde ao z-test!")
        return False
    
    print("✅ Algoritmo z-test validado!")
    
    return True

def validate_visualization():
    """Valida que visualização usa colormap categórico"""
    
    print("\n" + "="*70)
    print("🧪 TESTE 2: Validar Visualização Categórica")
    print("="*70)
    
    # Create test data
    isoscape_path, _, _, _ = create_test_isoscape()
    
    # Test samples com diferentes probabilidades esperadas
    test_samples = pd.DataFrame({
        'ID': ['match_center', 'match_edge', 'no_match'],
        'O18': [-20.0, -30.0, 50.0]  # Center, edge, impossible
    })
    
    from create_mapa_local import pd_raster
    
    result = pd_raster(
        r=isoscape_path,
        unknown=test_samples,
        prior=None,
        mask=None,
        genplot=True,  # Gerar PDF
        out_dir='test_create_mapa_output'
    )
    
    # Verificar PDF gerado
    pdf_path = 'test_create_mapa_output/output_pdRaster.pdf'
    
    if not os.path.exists(pdf_path):
        print("❌ FALHA: PDF não gerado!")
        return False
    
    print(f"✅ PDF gerado: {pdf_path}")
    
    # Verificar que código de visualização usa colormap categórico
    # (checando que _generate_plots foi atualizado)
    from create_mapa_local import _generate_plots
    import inspect
    
    source = inspect.getsource(_generate_plots)
    
    if 'ListedColormap' not in source:
        print("❌ FALHA: Visualização não usa ListedColormap!")
        return False
    
    if 'BoundaryNorm' not in source:
        print("❌ FALHA: Visualização não usa BoundaryNorm!")
        return False
    
    if '#d73027' not in source or '#fee08b' not in source or '#1a9850' not in source:
        print("❌ FALHA: Cores categóricas não encontradas!")
        return False
    
    print("✅ Visualização usa colormap categórico correto")
    
    # Analisar distribuição de probabilidades
    for i, sample_id in enumerate(test_samples['ID']):
        prob_path = f'test_create_mapa_output/prob_{sample_id}.tif'
        
        with rasterio.open(prob_path) as src:
            prob_surface = src.read(1)
        
        prob_valid = prob_surface[~np.isnan(prob_surface)]
        
        # Contar pixels em cada categoria
        red_pixels = np.sum(prob_valid < 5)
        yellow_pixels = np.sum((prob_valid >= 5) & (prob_valid < 95))
        green_pixels = np.sum(prob_valid >= 95)
        
        total_pixels = len(prob_valid)
        
        print(f"\n📊 Amostra '{sample_id}':")
        print(f"   • Verde (≥95%): {green_pixels} pixels ({100*green_pixels/total_pixels:.1f}%)")
        print(f"   • Amarelo (5-95%): {yellow_pixels} pixels ({100*yellow_pixels/total_pixels:.1f}%)")
        print(f"   • Vermelho (<5%): {red_pixels} pixels ({100*red_pixels/total_pixels:.1f}%)")
    
    return True

def main():
    print("="*70)
    print("🧪 TESTE: create_mapa_local.py - Probabilidade Estatística")
    print("="*70)
    
    # Teste 1: Algoritmo
    success1 = validate_algorithm()
    
    # Teste 2: Visualização
    success2 = validate_visualization()
    
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    tests = [
        ("Algoritmo z-test", success1),
        ("Visualização categórica", success2)
    ]
    
    for test_name, success in tests:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status}: {test_name}")
    
    all_passed = all(success for _, success in tests)
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ create_mapa_local.py está atualizado com:")
        print("   • Algoritmo de z-test estatístico (norm.sf)")
        print("   • Probabilidades percentuais (0-100%)")
        print("   • Visualização categórica (verde/amarelo/vermelho)")
        print("   • Metadados corretos no GeoTIFF")
        return 0
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("💡 Verifique se create_mapa_local.py está sincronizado com generate_new_mapa.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
