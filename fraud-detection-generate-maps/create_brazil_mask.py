#!/usr/bin/env python3
"""
🇧🇷 Criar shapefile simplificado do Brasil
"""

import geopandas as gpd
from shapely.geometry import Polygon
import os

def create_brazil_shapefile():
    """Cria um shapefile simplificado do Brasil"""
    
    print("🇧🇷 Criando shapefile simplificado do Brasil...")
    
    # Coordenadas melhoradas do contorno do Brasil
    # Formato mais preciso mantendo proporções corretas
    brazil_coords = [
        # Norte - Roraima/Amapá
        (-50.5, 5.3), (-51.5, 4.5), (-52.5, 3.5), (-54.0, 2.5),
        (-56.0, 2.0), (-58.0, 2.0), (-60.0, 2.5), (-62.0, 3.0),
        (-64.0, 2.5), (-65.5, 1.5), (-67.0, 0.5), (-69.0, -0.5),
        (-70.5, -2.0), (-72.0, -4.0), (-73.0, -6.0), (-73.5, -7.5),
        
        # Oeste - Acre/Rondônia/Mato Grosso
        (-73.0, -9.0), (-72.0, -10.5), (-70.5, -11.5), (-69.0, -11.0),
        (-68.0, -12.5), (-66.5, -14.5), (-65.0, -16.0), (-63.0, -17.0),
        (-61.0, -17.5), (-59.0, -18.5), (-58.0, -19.5), (-57.0, -20.5),
        
        # Sudoeste - Mato Grosso do Sul/Paraná
        (-56.0, -22.0), (-55.0, -23.5), (-54.5, -24.5), (-54.0, -26.0),
        (-53.5, -27.5), (-53.0, -29.0), (-52.0, -30.5), (-51.0, -31.5),
        
        # Sul - Rio Grande do Sul
        (-50.5, -32.0), (-50.0, -32.5), (-49.5, -33.0), (-49.0, -33.5),
        
        # Litoral Sul
        (-48.5, -29.0), (-48.5, -27.5), (-48.5, -26.0), (-48.5, -25.0),
        (-48.7, -26.5), (-49.0, -25.5), (-49.0, -24.0), (-48.5, -23.5),
        
        # Litoral Sudeste
        (-47.5, -24.0), (-46.5, -24.0), (-45.5, -23.8), (-44.5, -23.5),
        (-43.5, -23.0), (-43.0, -22.5), (-42.0, -22.0), (-41.5, -21.0),
        (-41.0, -20.5), (-40.5, -20.0), (-40.0, -19.5), (-39.8, -18.5),
        
        # Litoral Nordeste (ES, BA)
        (-39.5, -17.5), (-39.2, -16.5), (-39.0, -15.5), (-38.8, -14.5),
        (-38.7, -13.5), (-38.5, -12.5), (-38.0, -11.5), (-37.5, -10.5),
        (-37.0, -9.5), (-36.5, -8.5), (-36.0, -7.5), (-35.5, -6.5),
        (-35.2, -5.5), (-35.0, -5.0),
        
        # Litoral Norte (RN, CE, PI, MA)
        (-35.5, -5.5), (-36.5, -5.0), (-37.5, -4.8), (-38.5, -4.5),
        (-39.5, -4.0), (-40.5, -3.5), (-41.5, -3.2), (-42.5, -3.0),
        (-43.5, -2.8), (-44.5, -2.6), (-45.5, -2.4), (-46.5, -2.0),
        (-47.5, -1.5), (-48.5, -1.2), (-49.5, -1.0), (-50.5, -0.5),
        (-51.0, 0.0), (-51.5, 0.5), (-51.5, 1.5), (-51.0, 2.5),
        (-50.5, 3.5), (-50.5, 4.5),
        
        # Fechar
        (-50.5, 5.3),
    ]
    
    # Criar polígono
    brazil_polygon = Polygon(brazil_coords)
    
    # Criar GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {'name': ['Brazil'], 'iso': ['BRA']},
        geometry=[brazil_polygon],
        crs='EPSG:4326'
    )
    
    # Criar diretório
    os.makedirs('shapefiles', exist_ok=True)
    
    # Salvar
    output_path = 'shapefiles/brazil_simplified.shp'
    gdf.to_file(output_path)
    
    print(f"✅ Shapefile criado: {output_path}")
    print(f"   CRS: {gdf.crs}")
    print(f"   Bounds: {gdf.total_bounds}")
    print(f"   Área: {brazil_polygon.area:.2f} graus²")
    
    return output_path

if __name__ == "__main__":
    print("=" * 70)
    print("🇧🇷 CRIAR SHAPEFILE SIMPLIFICADO DO BRASIL")
    print("=" * 70)
    print()
    
    shapefile = create_brazil_shapefile()
    
    print("\n" + "=" * 70)
    print("✅ PRONTO!")
    print("=" * 70)
    print(f"""
📁 Arquivo criado:
   • {shapefile}

🚀 Agora o script usará esta máscara para mostrar apenas o Brasil!
    """)
