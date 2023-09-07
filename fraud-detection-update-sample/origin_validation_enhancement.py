import ee
import os

def origin_enhancement(lat: float, lon: float):
    # load MapBiomas Brazil water image
    point = ee.Geometry.Point(lon, lat)
    radius_1km_buffer = point.buffer(1000)
    radius_10km_buffer = point.buffer(10000)

    # WATER

    # load MapBiomas Brazil water image
    water_layers = ee.Image('projects/mapbiomas-workspace/public/collection6/mapbiomas-water-collection1-annual-water-coverage-1')
    water_layer_2020_mask = water_layers.select('water_coverage_2020').mask()
    full_brazil_geometry = water_layer_2020_mask.geometry().difference(radius_10km_buffer)

    # calculate point sample
    is_point_water = water_layer_2020_mask.sample(point).first().get('water_coverage_2020').getInfo()

    # calculate region water percentage
    water_mean_in_1km_buffer = water_layer_2020_mask.reduceRegion(
      reducer=ee.Reducer.mean(),
      geometry=radius_1km_buffer,
      maxPixels=1e8
    ).get('water_coverage_2020').getInfo()
    water_mean_in_10km_buffer = water_layer_2020_mask.reduceRegion(
      reducer=ee.Reducer.mean(),
      geometry=radius_10km_buffer,
      maxPixels=1e8
    ).get('water_coverage_2020').getInfo()

    water_results = {
        'is_point_water': True if is_point_water else False,
        'water_mean_in_1km_buffer': water_mean_in_1km_buffer,
        'water_mean_in_10km_buffer': water_mean_in_10km_buffer
    }

    # TREE COVER

    # create band names for each year between 2011 and 2021
    years = list(range(2011, 2022))
    year_band_dict = {"product_" + str(year): year for year in years}
    year_band_list = list(year_band_dict.keys())

    # load MapBiomas Brazil deforestation + land use dataset
    land_use_layers = ee.Image('projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_deforestation_regeneration_v1').select(year_band_list).divide(100).floor();

    # separate anthropic and vegetation to calculate percentages
    is_anthropic = land_use_layers.eq(1).Or(land_use_layers.eq(4)).Or(land_use_layers.eq(6))
    is_primary_vegetation = land_use_layers.eq(2)
    is_secondary_vegetation_or_regrowth = land_use_layers.eq(3).Or(land_use_layers.eq(5))

    # count the pixels in each region + band
    is_anthropic_sum = is_anthropic.reduceRegion(
      reducer=ee.Reducer.sum(),
      geometry=radius_10km_buffer,
      maxPixels=1e8
    ).getInfo()
    is_primary_vegetation_sum = is_primary_vegetation.reduceRegion(
      reducer=ee.Reducer.sum(),
      geometry=radius_10km_buffer,
      maxPixels=1e8
    ).getInfo()
    is_secondary_vegetation_or_regrowth_sum = is_secondary_vegetation_or_regrowth.reduceRegion(
      reducer=ee.Reducer.sum(),
      geometry=radius_10km_buffer,
      maxPixels=1e8
    ).getInfo()

    # sum and calculate the percentages
    total_sum = {}
    for year_band in year_band_list:
        total_sum[year_band] = is_anthropic_sum[year_band] + is_primary_vegetation_sum[year_band] + is_secondary_vegetation_or_regrowth_sum[year_band]

    is_anthropic_pct = {}
    is_primary_vegetation_pct = {}
    is_secondary_vegetation_or_regrowth_pct = {}

    for year_band in year_band_list:
        is_anthropic_pct[f"{year_band_dict[year_band]}"] = (is_anthropic_sum[year_band] / total_sum[year_band])
        is_primary_vegetation_pct[f"{year_band_dict[year_band]}"] = (is_primary_vegetation_sum[year_band] / total_sum[year_band])
        is_secondary_vegetation_or_regrowth_pct[f"{year_band_dict[year_band]}"] = (is_secondary_vegetation_or_regrowth_sum[year_band] / total_sum[year_band])

    return water_results, is_anthropic_pct, is_primary_vegetation_pct, is_secondary_vegetation_or_regrowth_pct
