# Import Libraries
import ee
import os
import numpy as np
import scipy
import google.auth

"""Global Variable definition"""

ISOSCAPES_EE_PATH = 'projects/kazob-370920/assets/isoscapes'

def fraud_detection_process_sample(value: dict):
    """
    Performs fraud detection on a given sample and updates its validity and additional information.

    Args:
        value (dict): A dictionary representing the sample to be processed. For keys, see firestore or
          unit tests for more details.

    Returns:
        A dictionary representing the sample with updated validity and additional information.
    """
    if not('oxygen' in value and 'nitrogen' in value and 'carbon' in value):
        if not(isinstance(oxygen, Sequence) and isinstance(nitrogen, Sequence) and isinstance(carbon, Sequence)):
            if not(len(oxygen) >=2 and len(nitrogen) >=2 and len(carbon) >=2):
                print("Missing input data, skipping fraud detection. Sample must contain at least 2 oxygen, nitrogen and carbon measurements.")
                return value
            
    oxygen = value.get('oxygen')
    nitrogen = value.get('nitrogen')
    carbon = value.get('carbon')
    lat = float(value.get('lat'))
    lon = float(value.get('lon'))
    
    fraud_rate, p_value_oxygen, p_value_carbon, p_value_nitrogen = ttest(lat, lon,oxygen,nitrogen,carbon).evaluate()
    validity_details = {
        'p_value_oxygen': p_value_oxygen,
        'p_value_carbon': p_value_carbon,
        'p_value_nitrogen': p_value_nitrogen
    }
    value['validity'] = fraud_rate
    value['validity_details'] = validity_details
    return value

class _ttest():
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
        
        self.oxygen_isoscape = None
        self.carbon_isoscape = None
        self.nitrogen_isoscape = None
        self.p_value_theshold = 0
        asset_list = get_asset_list(ISOSCAPES_EE_PATH)
        for asset in asset_list:
            if 'd18O_isoscape' in asset:
                self.oxygen_isoscape = ee.Image(asset)
                self.p_value_theshold = float(ee.data.getAsset(asset)['properties']['p_value'])
            elif 'd13C_isoscape' in asset:
                self.carbon_isoscape = ee.Image(asset)
            elif 'd15N_isoscape' in asset:
                self.nitrogen_isoscape = ee.Image(asset)
        self.poi = ee.Geometry.Point(lon, lat)

    
    def _calc_p_value(
            self,
            measured_mean: float,
            measured_std: float,
            num_measurements : int,
            poi: ee.Geometry.Point,
            isoscape: ee.Image):
        isoscape_mean = isoscape.select('b1').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=poi).getInfo().get('b1')
        isoscape_var = isoscape.select('b2').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=poi,).getInfo().get('b2')
        isoscape_std = np.sqrt(isoscape_var)

        _, p_value = scipy.stats.ttest_ind_from_stats(
            measured_mean, measured_std,
            num_measurements, isoscape_mean,
            isoscape_std, 30,
            equal_var=False, alternative="two-sided")

        return p_value

    def evaluate(self):
        p_value_oxygen, p_value_carbon, p_value_nitrogen = 1, 1, 1
        if self.oxygen_isoscape:
            p_value_oxygen = self._calc_p_value(
                np.mean(self.oxygen_measurements),
                np.std(self.oxygen_measurements),
                len(self.oxygen_measurements),
                self.poi,
                self.oxygen_isoscape)

        if self.carbon_isoscape:
            p_value_carbon = self._calc_p_value(
                np.mean(self.carbon_measurements),
                np.std(self.carbon_measurements),
                len(self.carbon_measurements),
                self.poi,
                self.carbon_isoscape)

        if self.nitrogen_isoscape:
            p_value_nitrogen = self._calc_p_value(
                np.mean(self.nitrogen_measurements),
                np.std(self.nitrogen_measurements),
                len(self.nitrogen_measurements),
                self.poi,
                self.nitrogen_isoscape)

        combined_p_value = p_value_oxygen * p_value_carbon * p_value_nitrogen
        is_invalid = combined_p_value <= self.p_value_theshold
        return is_invalid, combined_p_value, p_value_oxygen, p_value_carbon, p_value_nitrogen
