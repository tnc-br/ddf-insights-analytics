# Import Libraries
import ee
import os
import numpy as np
import scipy
import google.auth

"""Global Variable definition"""

# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "river-sky-386919")

# The path to the isoscapes folder in Earth Engine.
ISOSCAPES_EE_PATH = f'projects/{GCP_PROJECT_ID}/assets/isoscapes'


class ttest():
    """
      A class to perform a t-test on isotope data.

      Args:
          lat: The latitude of the point to test.
          lon: The longitude of the point to test.
          oxygen_measurements: A list of oxygen isotope measurements.
          nitrogen_measurements: A list of nitrogen isotope measurements.
          carbon_measurements: A list of carbon isotope measurements.

      """

    def __init__(self, lat, lon, oxygen_measurements, nitrogen_measurements, carbon_measurements):
        self.lat = lat
        self.lon = lon
        self.oxygen_measurements = oxygen_measurements
        self.nitrogen_measurements = nitrogen_measurements
        self.carbon_measurements = carbon_measurements

        # Initialize Earth Engine.
        credentials, project_id = google.auth.default()
        ee.Initialize(credentials)

        # fetching isoscapes

        def get_asset_list(parent_name) -> list:
          parent_asset = ee.data.getAsset(parent_name)
          parent_id = parent_asset['name']
          asset_list = []
          child_assets = ee.data.listAssets({'parent': parent_id})['assets']
          for child_asset in child_assets:
              child_id = child_asset['name']
              child_type = child_asset['type']
              if child_type in ['FOLDER', 'IMAGE_COLLECTION']:
                  # Recursively call the function to get child assets
                  asset_list.extend(get_asset_list(child_id))
              else:
                  asset_list.append(child_id)
          return asset_list
        asset_list = get_asset_list(ISOSCAPES_EE_PATH)
        for asset in asset_list:
            if ('oxygen' in asset) and ('mean' in asset):
                self.oxygen_means_iso = ee.Image(asset)
            elif 'oxygen' in asset and 'variance' in asset:
                self.oxygen_variances_iso = ee.Image(asset)
            elif 'd13C' in asset and 'gdal' in asset:
                self.carbon_means_iso = ee.Image(asset).select('b1')
                self.carbon_variances_iso = ee.Image(asset).select('b2')
            elif 'd15N' in asset and 'SD' in asset:
                self.nitrogen_variances_iso = ee.Image(asset)
            elif 'd15N' in asset and 'SD' not in asset:
                self.nitrogen_means_iso = ee.Image(asset)
        self.poi = ee.Geometry.Point(lon, lat)
        # self.carbon_means_iso.getInfo()

    def evaluate(self):
        isoscape_mean = self.oxygen_means_iso.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=self.poi,
            scale=30).getInfo().get('b1')
        isoscape_var = self.oxygen_variances_iso.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=self.poi,
            scale=30).getInfo().get('b1')
        if isoscape_var is not None:
            isoscape_std = np.sqrt(isoscape_var)
        else:
            isoscape_std = 0

        """Isotope calculation"""

        isotope_mean = np.mean(self.oxygen_measurements)
        isotope_std = np.std(self.oxygen_measurements)
        print(isotope_mean, isotope_std, isoscape_mean, isoscape_std)

        """ttest and p-value"""

        _, p_value_oxygen = scipy.stats.ttest_ind_from_stats(
            isotope_mean, isotope_std, len(self.oxygen_measurements), isoscape_mean, isoscape_std, 30, equal_var=False, alternative="two-sided")

        """**Carbon** Isoscape """

        isoscape_mean = self.carbon_means_iso.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=self.poi,
            scale=30).getInfo().get('b1')
        isoscape_var = self.carbon_variances_iso.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=self.poi,
            scale=30).getInfo().get('b2')
        if isoscape_var is not None:
            isoscape_std = np.sqrt(isoscape_var)
        else:
            isoscape_std = 0

        """Isotope calculation"""

        isotope_mean = np.mean(self.carbon_measurements)
        isotope_std = np.std(self.carbon_measurements)
        print(isotope_mean, isotope_std, isoscape_mean, isoscape_std)

        """ttest and p-value"""

        _, p_value_carbon = scipy.stats.ttest_ind_from_stats(
            isotope_mean, isotope_std, len(self.carbon_measurements), isoscape_mean, isoscape_std, 30, equal_var=False, alternative="two-sided")

        """**Nitrogen**

    Isoscape
    """

        isoscape_mean = self.nitrogen_means_iso.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=self.poi,
            scale=30).getInfo().get('b1')
        isoscape_var = self.nitrogen_variances_iso.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=self.poi,
            scale=30).getInfo().get('b1')
        if isoscape_var is not None:
            isoscape_std = np.sqrt(isoscape_var)
        else:
            isoscape_std = 0

        """Isotope calculation"""

        isotope_mean = np.mean(self.nitrogen_measurements)
        isotope_std = np.std(self.nitrogen_measurements)
        print(isotope_mean, isotope_std, isoscape_mean, isoscape_std)

        """ttest and p-value"""

        _, p_value_nitrogen = scipy.stats.ttest_ind_from_stats(
            isotope_mean, isotope_std, len(self.nitrogen_measurements), isoscape_mean, isoscape_std, 30, equal_var=False, alternative="two-sided")

        """Origin Verification"""

        origin_validity = p_value_oxygen * p_value_carbon * p_value_nitrogen
        return origin_validity, p_value_oxygen, p_value_carbon, p_value_nitrogen
