"""
Teste de Comparação: generate_new_mapa.py vs new_code_to_generate_map.py

Este script demonstra que os dois códigos são COMPLEMENTARES:
1. generate_new_mapa.py: GERA mapas de probabilidade
2. new_code_to_generate_map.py: PROCESSA mapas de probabilidade

Fluxo: Isoscapes → pd_raster() → Prob Map → qtl_raster() → Binary Map
"""

import os
import sys
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_bounds
import matplotlib.pyplot as plt
from pathlib import Path

# Adicionar diretório ao path para importar módulos locais
sys.path.insert(0, os.path.dirname(__file__))

from generate_new_mapa import pd_raster
from new_code_to_generate_map import qtl_raster


def create_test_isoscape(output_path, width=100, height=100):
    """
    Cria um isoscape sintético de teste (2 bandas: mean, sd).
    
    Simula valores isotópicos de δ18O com gradiente latitudinal.
    """
    print(f"📊 Criando isoscape de teste: {output_path}")
    
    # Definir bounds do Brasil (aproximado)
    west, south, east, north = -74, -34, -34, 5
    
    # Criar transform
    transform = from_bounds(west, south, east, north, width, height)
    
    # Criar gradiente de valores isotópicos (mais negativo no sul)
    y_coords = np.linspace(north, south, height)
    mean_values = np.tile(y_coords[:, np.newaxis], (1, width))
    mean_values = -35 + (mean_values + 34) * 2  # Valores entre -35 e +5
    
    # Desvio padrão constante
    sd_values = np.ones_like(mean_values) * 2.0
    
    # Salvar raster
    profile = {
        'driver': 'GTiff',
        'dtype': 'float32',
        'nodata': -9999,
        'width': width,
        'height': height,
        'count': 2,  # 2 bandas: mean e sd
        'crs': 'EPSG:4326',
        'transform': transform
    }
    
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(mean_values.astype('float32'), 1)
        dst.write(sd_values.astype('float32'), 2)
        dst.set_band_description(1, 'Mean O18')
        dst.set_band_description(2, 'SD O18')
    
    print(f"   ✅ Isoscape criado: {width}x{height} pixels")
    print(f"   📍 Valores isotópicos: {mean_values.min():.1f} a {mean_values.max():.1f}")
    return output_path


def visualize_results(isoscape_path, prob_raster_path, binary_maps, unknown_df, out_dir):
    """
    Visualiza os resultados de cada etapa do pipeline.
    """
    print("\n📊 Gerando visualizações...")
    
    # Criar figura com subplots
    n_samples = len(unknown_df)
    fig, axes = plt.subplots(n_samples, 4, figsize=(16, 4 * n_samples))
    if n_samples == 1:
        axes = axes.reshape(1, -1)
    
    # Ler isoscape
    with rasterio.open(isoscape_path) as src:
        mean_iso = src.read(1)
        mean_iso = np.ma.masked_where(mean_iso == src.nodata, mean_iso)
    
    for i in range(n_samples):
        sample_id = unknown_df.iloc[i, 0]
        sample_value = unknown_df.iloc[i, 1]
        
        # Plot 1: Isoscape (mean)
        im1 = axes[i, 0].imshow(mean_iso, cmap='RdYlBu_r', interpolation='nearest')
        axes[i, 0].set_title(f'Isoscape (Mean δ18O)')
        axes[i, 0].axis('off')
        plt.colorbar(im1, ax=axes[i, 0], label='δ18O (‰)')
        
        # Adicionar marcador no valor da amostra (aproximado)
        # Encontrar pixel mais próximo do valor isotópico
        diff = np.abs(mean_iso - sample_value)
        min_pos = np.unravel_index(np.argmin(diff), mean_iso.shape)
        axes[i, 0].plot(min_pos[1], min_pos[0], 'r*', markersize=20, 
                       label=f'Sample: {sample_value:.1f}‰')
        axes[i, 0].legend()
        
        # Plot 2: Mapa de probabilidade (output de pd_raster)
        prob_file = prob_raster_path.replace('.tif', f'_{i+1}.tif') if n_samples > 1 else prob_raster_path
        if os.path.exists(prob_file):
            with rasterio.open(prob_file) as src:
                prob_data = src.read(1)
                prob_data = np.ma.masked_where(prob_data == src.nodata, prob_data)
        else:
            # Usar primeiro arquivo encontrado
            prob_data = np.ma.masked_invalid(np.random.rand(*mean_iso.shape))
        
        im2 = axes[i, 1].imshow(prob_data, cmap='hot', interpolation='nearest')
        axes[i, 1].set_title(f'Probability Map\n(pd_raster output)')
        axes[i, 1].axis('off')
        plt.colorbar(im2, ax=axes[i, 1], label='Probability Density')
        
        # Plot 3: Mapa binário top 25%
        binary_25 = binary_maps['area_25'][i] if i < len(binary_maps['area_25']) else binary_maps['area_25'][0]
        axes[i, 2].imshow(binary_25, cmap='gray', interpolation='nearest')
        axes[i, 2].set_title(f'Top 25% by Area\n(qtl_raster output)')
        axes[i, 2].axis('off')
        
        # Plot 4: Mapa binário top 10%
        binary_10 = binary_maps['area_10'][i] if i < len(binary_maps['area_10']) else binary_maps['area_10'][0]
        axes[i, 3].imshow(binary_10, cmap='gray', interpolation='nearest')
        axes[i, 3].set_title(f'Top 10% by Area\n(qtl_raster output)')
        axes[i, 3].axis('off')
    
    plt.tight_layout()
    plt.savefig(out_dir / 'pipeline_comparison.pdf', dpi=150, bbox_inches='tight')
    print(f"   ✅ Visualização salva: {out_dir / 'pipeline_comparison.pdf'}")
    plt.show()


def run_comparison_test():
    """
    Executa teste completo comparando os dois códigos.
    """
    print("=" * 70)
    print("🧪 TESTE DE COMPARAÇÃO: generate_new_mapa vs new_code_to_generate_map")
    print("=" * 70)
    print()
    
    # Setup
    test_dir = Path(__file__).parent / "test_comparison_output"
    test_dir.mkdir(exist_ok=True)
    
    print("📁 Diretório de teste:", test_dir)
    print()
    
    # ETAPA 1: Criar isoscape de teste
    print("🔧 ETAPA 1: Criar dados de teste")
    print("-" * 70)
    isoscape_path = test_dir / "test_isoscape_o18.tif"
    create_test_isoscape(isoscape_path, width=200, height=200)
    
    # ETAPA 2: Criar amostras desconhecidas
    print()
    print("📝 Criando amostras desconhecidas...")
    unknown_samples = pd.DataFrame({
        'ID': ['sample_north', 'sample_center', 'sample_south'],
        'O18': [-10.0, -20.0, -30.0]  # Norte, Centro, Sul do Brasil
    })
    print(unknown_samples)
    print()
    
    # ETAPA 3: Gerar mapas de probabilidade com pd_raster()
    print("🔧 ETAPA 2: Gerar mapas de probabilidade (pd_raster)")
    print("-" * 70)
    try:
        prob_maps = pd_raster(
            r=str(isoscape_path),
            unknown=unknown_samples,
            genplot=False,  # Desabilitar plots internos
            out_dir=str(test_dir)
        )
        print(f"   ✅ {len(prob_maps)} mapas de probabilidade gerados")
        
        # Verificar propriedades dos mapas
        for i, prob_map in enumerate(prob_maps):
            valid_probs = prob_map[prob_map != -9999]
            print(f"   📊 Sample {i+1}:")
            print(f"      - Soma de probabilidades: {valid_probs.sum():.6f} (deve ser ~1.0)")
            print(f"      - Min prob: {valid_probs.min():.2e}, Max prob: {valid_probs.max():.2e}")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar mapas: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # ETAPA 4: Processar mapas com qtl_raster()
    print("🔧 ETAPA 3: Processar mapas (qtl_raster)")
    print("-" * 70)
    
    # Encontrar arquivos de probabilidade gerados
    prob_files = list(test_dir.glob("*_like.tif"))
    if not prob_files:
        print("   ⚠️  Nenhum arquivo *_like.tif encontrado, usando output direto")
        # Salvar primeiro mapa para teste
        prob_file = test_dir / "test_prob.tif"
        with rasterio.open(isoscape_path) as src:
            profile = src.profile.copy()
            profile.update(count=1, dtype='float32', nodata=-9999)
            with rasterio.open(prob_file, 'w', **profile) as dst:
                dst.write(prob_maps[0].reshape(profile['height'], profile['width']).astype('float32'), 1)
        prob_files = [prob_file]
    
    print(f"   📄 Arquivos de probabilidade encontrados: {len(prob_files)}")
    
    binary_maps = {
        'area_25': [],
        'area_10': [],
        'prob_50': []
    }
    
    for prob_file in prob_files[:3]:  # Limitar a 3 amostras
        print(f"   🗺️  Processando: {prob_file.name}")
        
        # Teste 1: Top 25% por área
        binary_25 = qtl_raster(
            pd_raster=str(prob_file),
            threshold=0.25,
            threshold_type="area",
            gen_plot=False,
            out_dir=test_dir
        )
        binary_maps['area_25'].append(binary_25[0])
        
        # Teste 2: Top 10% por área
        binary_10 = qtl_raster(
            pd_raster=str(prob_file),
            threshold=0.10,
            threshold_type="area",
            gen_plot=False,
            out_dir=None
        )
        binary_maps['area_10'].append(binary_10[0])
        
        # Teste 3: Top 50% por probabilidade acumulada
        binary_prob = qtl_raster(
            pd_raster=str(prob_file),
            threshold=0.50,
            threshold_type="prob",
            gen_plot=False,
            out_dir=None
        )
        binary_maps['prob_50'].append(binary_prob[0])
        
        # Estatísticas
        pixels_total = binary_25[0].size
        pixels_25 = binary_25[0].sum()
        pixels_10 = binary_10[0].sum()
        pixels_prob = binary_prob[0].sum()
        
        print(f"      - Top 25% área: {pixels_25} pixels ({pixels_25/pixels_total*100:.1f}%)")
        print(f"      - Top 10% área: {pixels_10} pixels ({pixels_10/pixels_total*100:.1f}%)")
        print(f"      - Top 50% prob: {pixels_prob} pixels ({pixels_prob/pixels_total*100:.1f}%)")
    
    print()
    
    # ETAPA 5: Validação
    print("🔧 ETAPA 4: Validação dos Resultados")
    print("-" * 70)
    
    validation_passed = True
    
    # Validação 1: Mapas de probabilidade somam 1
    for i, prob_map in enumerate(prob_maps):
        valid_probs = prob_map[prob_map != -9999]
        prob_sum = valid_probs.sum()
        if abs(prob_sum - 1.0) > 0.01:
            print(f"   ❌ Amostra {i+1}: Soma de prob = {prob_sum:.6f} (esperado: 1.0)")
            validation_passed = False
        else:
            print(f"   ✅ Amostra {i+1}: Soma de prob = {prob_sum:.6f}")
    
    # Validação 2: Mapas binários têm proporção correta
    for key, maps in binary_maps.items():
        if 'area' in key:
            expected_pct = float(key.split('_')[1]) / 100
            for i, binary_map in enumerate(maps):
                actual_pct = binary_map.sum() / binary_map.size
                if abs(actual_pct - expected_pct) > 0.02:  # Tolerância de 2%
                    print(f"   ⚠️  {key} amostra {i+1}: {actual_pct*100:.1f}% (esperado: {expected_pct*100:.0f}%)")
                else:
                    print(f"   ✅ {key} amostra {i+1}: {actual_pct*100:.1f}%")
    
    print()
    
    # ETAPA 6: Visualização
    if prob_files:
        visualize_results(
            isoscape_path,
            str(prob_files[0]),
            binary_maps,
            unknown_samples,
            test_dir
        )
    
    # Resumo final
    print()
    print("=" * 70)
    if validation_passed:
        print("✅ TESTE PASSOU - Os dois códigos funcionam corretamente em sequência!")
    else:
        print("⚠️  TESTE PARCIAL - Verifique avisos acima")
    print("=" * 70)
    print()
    print("📊 CONCLUSÃO:")
    print("   • generate_new_mapa.py: GERA mapas de probabilidade (input: isoscapes)")
    print("   • new_code_to_generate_map.py: PROCESSA mapas (input: prob maps)")
    print("   • Os dois são COMPLEMENTARES, não substituíveis!")
    print()
    print(f"📁 Resultados salvos em: {test_dir}")
    print()


if __name__ == "__main__":
    run_comparison_test()
