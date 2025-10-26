#!/usr/bin/env python3
"""
🗺️ Baixar shapefile do Brasil para usar como máscara
"""

import urllib.request
import zipfile
import os

def download_brazil_shapefile():
    """Baixa shapefile simplificado do Brasil do Natural Earth"""
    
    print("📥 Baixando shapefile do Brasil...")
    
    # URL do Natural Earth (dados livres e de qualidade)
    url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip"
    
    zip_path = "shapefiles/countries.zip"
    extract_path = "shapefiles/"
    
    # Criar diretório
    os.makedirs(extract_path, exist_ok=True)
    
    # Verificar se já existe
    if os.path.exists("shapefiles/ne_110m_admin_0_countries.shp"):
        print("✅ Shapefile já existe!")
        return "shapefiles/ne_110m_admin_0_countries.shp"
    
    # Baixar
    print(f"   URL: {url}")
    try:
        urllib.request.urlretrieve(url, zip_path)
        print(f"✅ Download completo: {zip_path}")
        
        # Extrair
        print("📂 Extraindo arquivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        print("✅ Arquivos extraídos!")
        
        # Remover zip
        os.remove(zip_path)
        
        return "shapefiles/ne_110m_admin_0_countries.shp"
        
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        print("\n💡 Download manual:")
        print("   1. Acesse: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/")
        print("   2. Baixe: Admin 0 - Countries")
        print("   3. Extraia na pasta: shapefiles/")
        return None

def filter_brazil_only():
    """Filtra apenas o Brasil do shapefile mundial"""
    import geopandas as gpd
    
    print("\n🇧🇷 Filtrando apenas o Brasil...")
    
    world_shp = "shapefiles/ne_110m_admin_0_countries.shp"
    brazil_shp = "shapefiles/brazil_only.shp"
    
    if os.path.exists(brazil_shp):
        print("✅ Shapefile do Brasil já existe!")
        return brazil_shp
    
    try:
        # Ler shapefile mundial
        world = gpd.read_file(world_shp)
        
        # Filtrar Brasil
        brazil = world[world['ADMIN'] == 'Brazil']
        
        # Salvar
        brazil.to_file(brazil_shp)
        
        print(f"✅ Brasil extraído: {brazil_shp}")
        print(f"   CRS: {brazil.crs}")
        print(f"   Bounds: {brazil.total_bounds}")
        
        return brazil_shp
        
    except Exception as e:
        print(f"❌ Erro ao filtrar: {e}")
        return None

def main():
    print("=" * 70)
    print("🗺️  DOWNLOAD DE SHAPEFILE DO BRASIL")
    print("=" * 70)
    
    # 1. Baixar shapefile mundial
    world_shp = download_brazil_shapefile()
    
    if not world_shp:
        return
    
    # 2. Filtrar apenas Brasil
    brazil_shp = filter_brazil_only()
    
    if brazil_shp:
        print("\n" + "=" * 70)
        print("✅ PRONTO!")
        print("=" * 70)
        print(f"""
📁 Arquivos criados:
   • {brazil_shp}

🚀 Agora execute novamente o gerador com a máscara:
   
   O script run_generate_mapa_auto.py será atualizado automaticamente
   para usar esta máscara.
        """)

if __name__ == "__main__":
    main()
