import rasterio
from rasterio.mask import mask as rio_mask
import geopandas as gpd

# Carregar shapefile
mask_gdf = gpd.read_file('shapefiles/brazil_simplified.shp')

# Carregar raster
with rasterio.open('isoscapes/oxygen_18_brazil.tif') as src:
    print(f"Raster bands: {src.count}")
    print(f"Raster shape: {src.shape}")
    print(f"Raster profile: {src.profile}")
    
    # Testar rio_mask
    print("\nTestando rio_mask com indexes=1:")
    result1, transform1 = rio_mask(src, shapes=mask_gdf.geometry, crop=True, indexes=1)
    print(f"Result1 shape: {result1.shape}")
    print(f"Result1 type: {type(result1)}")
    
    print("\nTestando rio_mask com indexes=[1]:")
    result2, transform2 = rio_mask(src, shapes=mask_gdf.geometry, crop=True, indexes=[1])
    print(f"Result2 shape: {result2.shape}")
    print(f"Result2 type: {type(result2)}")
    
    print("\nTestando rio_mask sem indexes:")
    result3, transform3 = rio_mask(src, shapes=mask_gdf.geometry, crop=True)
    print(f"Result3 shape: {result3.shape}")
    print(f"Result3 type: {type(result3)}")
