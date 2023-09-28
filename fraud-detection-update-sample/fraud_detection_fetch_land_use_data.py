import ee

MAPBIOMAS_BRAZIL_ANNUAL_WATER_COVERAGE_GEE_IMAGE = 'projects/mapbiomas-workspace/public/collection8/mapbiomas_water_collection2_annual_water_coverage_v1'
MAPBIOMAS_WATER_BAND_NAME = 'annual_water_coverage_2022'

MAPBIOMAS_BRAZIL_LAND_USE_GEE_IMAGE = 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_deforestation_secondary_vegetation_v1'
MAPBIOMAS_LAND_USE_BAND_NAME_PREFIX = 'classification_'

def fraud_detection_fetch_land_use_data(value: dict):
    """
    Fetches land use data for a given sample location and updates the sample dictionary with the results.

    Args:
        value (dict): A dictionary representing the sample to be processed. Must contain the following keys:
            - lat (float): The latitude of the sample location.
            - lon (float): The longitude of the sample location.

    Returns:
        A dictionary representing the sample with updated validity land use data.
    """
    water_pct, land_use_anthropic_pct, land_use_primary_vegetation_pct, land_use_secondary_vegetation_or_regrowth_pct = _fraud_detection_fetch_land_use_data(float(value.get('lat')), float(value.get('lon')))

    value['water_pct'] = water_pct
    value['land_use_anthropic_pct'] = land_use_anthropic_pct
    value['land_use_primary_vegetation_pct'] = land_use_primary_vegetation_pct
    value['land_use_secondary_vegetation_or_regrowth_pct'] = land_use_secondary_vegetation_or_regrowth_pct

    return value

def _fraud_detection_fetch_land_use_data(lat: float, lon: float):
    """
    Enhances the origin point with additional information about the surrounding area.

    Args:
        lat (float): The latitude of the origin point.
        lon (float): The longitude of the origin point.

    Returns:
        A tuple containing the following dictionaries:
        - water_results (Dict[str, Union[bool, float]]): A dictionary containing the following keys:
            - is_point_water (bool): True if the origin point is covered by water, False otherwise.
            - water_mean_in_1km_buffer (float): The mean water coverage percentage within a 1km buffer around the origin point.
            - water_mean_in_10km_buffer (float): The mean water coverage percentage within a 10km buffer around the origin point.
        - is_anthropic_pct (Dict[str, float]): A dictionary containing the percentage of pixels classified as anthropic (e.g. urban areas, agriculture) for each year between 2011 and 2021.
        - is_primary_vegetation_pct (Dict[str, float]): A dictionary containing the percentage of pixels classified as primary vegetation (e.g. forests) for each year between 2011 and 2021.
        - is_secondary_vegetation_or_regrowth_pct (Dict[str, float]): A dictionary containing the percentage of pixels classified as secondary vegetation or regrowth (e.g. pastures, fallows) for each year between 2011 and 2021.
    """
    # load MapBiomas Brazil water image
    point = ee.Geometry.Point(lon, lat)
    radius_1km_buffer = point.buffer(1000)
    radius_10km_buffer = point.buffer(10000)

    # WATER
    # ==========

    # load MapBiomas Brazil water image
    water_layers = ee.Image(MAPBIOMAS_BRAZIL_ANNUAL_WATER_COVERAGE_GEE_IMAGE).select(MAPBIOMAS_WATER_BAND_NAME)
    water_layer_mask = water_layers.mask()

    # calculate point sample
    is_point_water = water_layer_mask.sample(point).first().get(MAPBIOMAS_WATER_BAND_NAME).getInfo()

    # calculate region water percentage
    water_mean_in_1km_buffer = water_layer_mask.reduceRegion(
      reducer=ee.Reducer.mean(),
      geometry=radius_1km_buffer,
      maxPixels=1e8
    ).get(MAPBIOMAS_WATER_BAND_NAME).getInfo()
    water_mean_in_10km_buffer = water_layer_mask.reduceRegion(
      reducer=ee.Reducer.mean(),
      geometry=radius_10km_buffer,
      maxPixels=1e8
    ).get(MAPBIOMAS_WATER_BAND_NAME).getInfo()

    water_results = {
        'is_point_water': True if is_point_water else False,
        'water_mean_in_1km_buffer': water_mean_in_1km_buffer,
        'water_mean_in_10km_buffer': water_mean_in_10km_buffer
    }

    # TREE COVER
    # ==========

    # create band names for each year between 2011 and 2021
    years = list(range(2011, 2022))
    year_band_dict = {MAPBIOMAS_LAND_USE_BAND_NAME_PREFIX + str(year): year for year in years}
    year_band_list = list(year_band_dict.keys())

    # load MapBiomas Brazil deforestation + land use dataset
    land_use_layers = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_GEE_IMAGE).select(year_band_list).divide(100).floor();

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
