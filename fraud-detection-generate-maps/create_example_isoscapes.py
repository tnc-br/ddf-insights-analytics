#!/usr/bin/env python3
"""
🧪 GERADOR DE ISOSCAPES DE EXEMPLO

Cria isoscapes sintéticos para testar o generate_new_mapa.py
Gera rasters GeoTIFF com 2 bandas (média e desvio padrão)

Uso:
    python create_example_isoscapes.py

Saída:
    isoscapes/
        ├── oxygen_18_brazil.tif
        ├── carbon_13_brazil.tif
        └── nitrogen_15_brazil.tif
"""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS
import os

def create_synthetic_isoscape(output_path, isotope_name, bounds, resolution=0.1):
    """
    Cria um isoscape sintético com gradientes realísticos
    
    Args:
        output_path: Caminho do arquivo de saída
        isotope_name: Nome do isótopo para gerar valores típicos
        bounds: Tupla (west, south, east, north) em graus
        resolution: Resolução em graus (default 0.1 ≈ 11km)
    """
    
    west, south, east, north = bounds
    
    # Calcular dimensões
    width = int((east - west) / resolution)
    height = int((north - south) / resolution)
    
    # Criar grids de coordenadas
    x = np.linspace(west, east, width)
    y = np.linspace(south, north, height)
    xx, yy = np.meshgrid(x, y)
    
    # Parâmetros isotópicos REALISTAS para BRASIL (celulose de madeira vs VSMOW)
    # Baseados em literatura científica: Brienen et al. (2012), Vuille et al. (2012)
    isotope_params = {
        'oxygen_18': {'mean_range': (23, 30), 'std': 1.5},    # δ18O positivo em celulose!
        'carbon_13': {'mean_range': (-30, -24), 'std': 1.2},  # δ13C plantas C3
        'nitrogen_15': {'mean_range': (0, 8), 'std': 0.8},    # δ15N solos tropicais
    }
    
    params = isotope_params.get(isotope_name, {'mean_range': (0, 10), 'std': 1.0})
    
    # Gerar padrão de média com gradientes espaciais
    # Simula variação latitudinal + longitudinal + ruído
    lat_gradient = (yy - south) / (north - south)  # 0 a 1
    lon_gradient = (xx - west) / (east - west)      # 0 a 1
    
    mean_min, mean_max = params['mean_range']
    mean_base = mean_min + (mean_max - mean_min) * lat_gradient
    
    # Adicionar variação longitudinal menor
    mean_base += (mean_max - mean_min) * 0.2 * np.sin(lon_gradient * 2 * np.pi)
    
    # Adicionar ruído espacial correlacionado (simula variações regionais)
    from scipy.ndimage import gaussian_filter
    noise = np.random.randn(height, width) * (mean_max - mean_min) * 0.1
    noise_smooth = gaussian_filter(noise, sigma=5)
    
    mean_data = mean_base + noise_smooth
    
    # Gerar banda de desvio padrão (variação espacial realística)
    # Maior incerteza em áreas remotas (bordas) e menor no centro
    dist_from_center = np.sqrt((xx - (west + east)/2)**2 + (yy - (south + north)/2)**2)
    dist_normalized = dist_from_center / dist_from_center.max()
    
    std_base = params['std']
    std_data = std_base * (1 + 0.5 * dist_normalized)
    
    # Adicionar ruído à incerteza também
    std_noise = np.random.randn(height, width) * std_base * 0.1
    std_noise_smooth = gaussian_filter(std_noise, sigma=3)
    std_data += std_noise_smooth
    std_data = np.abs(std_data)  # Garantir que std é positivo
    
    # Configurar transformação geoespacial
    transform = from_bounds(west, south, east, north, width, height)
    
    # Definir CRS (EPSG:4326 = WGS84)
    crs = CRS.from_epsg(4326)
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar raster com 2 bandas
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=2,  # 2 bandas: mean e std
        dtype=rasterio.float32,
        crs=crs,
        transform=transform,
        nodata=-9999
    ) as dst:
        dst.write(mean_data.astype(rasterio.float32), 1)
        dst.write(std_data.astype(rasterio.float32), 2)
        
        # Adicionar metadados
        dst.update_tags(1, description=f'{isotope_name} - Mean values')
        dst.update_tags(2, description=f'{isotope_name} - Standard deviation')
    
    print(f"✅ Criado: {output_path}")
    print(f"   Dimensões: {width}x{height} pixels")
    print(f"   Valores médios: {mean_data.min():.2f} a {mean_data.max():.2f}")
    print(f"   Desvio padrão: {std_data.min():.2f} a {std_data.max():.2f}")

def create_brazil_isoscapes():
    """Cria isoscapes de exemplo cobrindo o Brasil"""
    
    print("=" * 70)
    print("🧪 GERADOR DE ISOSCAPES DE EXEMPLO PARA O BRASIL")
    print("=" * 70)
    
    # Bounding box do Brasil (aproximado)
    # Oeste, Sul, Leste, Norte
    brazil_bounds = (-74, -34, -34, 6)
    
    print(f"\n📍 Área de cobertura:")
    print(f"   Oeste:  {brazil_bounds[0]}°")
    print(f"   Sul:    {brazil_bounds[1]}°")
    print(f"   Leste:  {brazil_bounds[2]}°")
    print(f"   Norte:  {brazil_bounds[3]}°")
    
    resolution = 0.1  # ~11km
    print(f"\n📏 Resolução: {resolution}° (~11km)")
    
    isoscapes = [
        ('oxygen_18', 'Oxigênio-18 (δ18O)'),
        ('carbon_13', 'Carbono-13 (δ13C)'),
        ('nitrogen_15', 'Nitrogênio-15 (δ15N)')
    ]
    
    print(f"\n🧪 Criando {len(isoscapes)} isoscapes...")
    print()
    
    for isotope_id, isotope_name_pt in isoscapes:
        output_path = f'isoscapes/{isotope_id}_brazil.tif'
        print(f"📊 {isotope_name_pt}")
        create_synthetic_isoscape(
            output_path=output_path,
            isotope_name=isotope_id,
            bounds=brazil_bounds,
            resolution=resolution
        )
        print()
    
    print("=" * 70)
    print("✅ ISOSCAPES CRIADOS COM SUCESSO!")
    print("=" * 70)
    print(f"""
📁 Arquivos gerados em: isoscapes/
   • oxygen_18_brazil.tif
   • carbon_13_brazil.tif
   • nitrogen_15_brazil.tif

🎯 Próximos passos:

1. Execute o script principal com um ID do Firebase:
   
   python execute_generate_mapa.py <document_id>

2. Quando perguntado sobre isoscapes, responda 's' e forneça:
   
   Single isoscape:
   isoscapes/oxygen_18_brazil.tif
   
   Multi-isoscape (3 isótopos combinados):
   isoscapes/oxygen_18_brazil.tif,isoscapes/carbon_13_brazil.tif,isoscapes/nitrogen_15_brazil.tif

⚠️ NOTA: Estes são dados SINTÉTICOS para demonstração!
   Para análises reais, use isoscapes validados cientificamente.
    """)

def main():
    try:
        create_brazil_isoscapes()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
