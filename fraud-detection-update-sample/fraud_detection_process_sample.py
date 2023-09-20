# Import Libraries
import ee
import os
import numpy as np
import scipy
import google.auth
from typing import Sequence

"""Global Variable definition"""

# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "river-sky-386919")

# The path to the isoscapes folder in Earth Engine.
ISOSCAPES_EE_PATH = f'projects/{GCP_PROJECT_ID}/assets/isoscapes'

# If enabled, performs t-test of oxygen cellulose measurements against the values in the d18O_isoscape.
_ENABLE_d18O_ANALYSIS = True
# If enabled, performs t-test of carbon cellulose measurements against the values in the d13C_isoscape.
_ENABLE_d13C_ANALYSIS = False
# If enabled, performs t-test of nitrogen cellulose measurements against the values in the d15N_isoscape.
_ENABLE_d15N_ANALYSIS = False

_VALIDATION_PASSED_LABEL = "Possible"
_VALIDATION_FAILED_LABEL = "Not Likely"

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
                self.oxygen_isoscape_name = ee.data.getAsset(asset)['properties']['REFERENCE_ISOSCAPE_NAME']
                self.oxygen_isoscape_date = ee.data.getAsset(asset)['properties']['DATE_TIME']
                self.p_value_theshold = float(ee.data.getAsset(asset)['properties']['P_VALUE_THRESHOLD'])
                self.oxygen_isoscape_precision = ee.data.getAsset(asset)['properties']['PRECISION']
                self.oxygen_isoscape_recall = ee.data.getAsset(asset)['properties']['RECALL']

                print(f'found d18O_isoscape in EE assets with properties: name {self.oxygen_isoscape_name} date {self.oxygen_isoscape_date} threshold {self.p_value_theshold} precision {self.oxygen_isoscape_precision} recall {self.oxygen_isoscape_recall}')
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
            geometry=poi).getInfo().get('b2')

        if not isoscape_mean or not isoscape_var:
            raise ValueError("Failed to get reference data at ", poi)
        
        isoscape_std = np.sqrt(isoscape_var)

        _, p_value = scipy.stats.ttest_ind_from_stats(
            measured_mean, measured_std,
            num_measurements, isoscape_mean,
            isoscape_std, 5,
            equal_var=False, alternative="two-sided")

        return p_value, isoscape_mean, isoscape_var

    def evaluate(self):
        p_value_oxygen, p_value_carbon, p_value_nitrogen = 1, 1, 1
        o_mean, o_var, c_mean, c_var, n_mean, n_var = None, None, None, None, None, None 
        if self.oxygen_isoscape and _ENABLE_d18O_ANALYSIS:
            p_value_oxygen, o_mean, o_var = self._calc_p_value(
                np.mean(self.oxygen_measurements),
                np.std(self.oxygen_measurements),
                len(self.oxygen_measurements),
                self.poi,
                self.oxygen_isoscape)

        if self.carbon_isoscape and _ENABLE_d13C_ANALYSIS:
            p_value_carbon, c_mean, c_var = self._calc_p_value(
                np.mean(self.carbon_measurements),
                np.std(self.carbon_measurements),
                len(self.carbon_measurements),
                self.poi,
                self.carbon_isoscape)

        if self.nitrogen_isoscape and _ENABLE_d15N_ANALYSIS:
            p_value_nitrogen, n_mean, n_var = self._calc_p_value(
                np.mean(self.nitrogen_measurements),
                np.std(self.nitrogen_measurements),
                len(self.nitrogen_measurements),
                self.poi,
                self.nitrogen_isoscape)

        combined_p_value = p_value_oxygen * p_value_carbon * p_value_nitrogen
        is_invalid = combined_p_value <= self.p_value_theshold
        return is_invalid, combined_p_value, p_value_oxygen, o_mean, o_var, p_value_carbon, p_value_nitrogen

def fraud_detection_process_sample(doc: dict):
    """
    Performs fraud detection on a given sample and updates its validity and additional information.

    Args:
        sample_measurements(dict): A dictionary representing the sample to be processed. For keys, see firestore or
          unit tests for more details.

    Returns:
        A dictionary representing the sample with updated validity and additional information.
    """

    # Use .get(key) instead of [key] so that it defaults to None
    oxygen_measurements = doc.get('d18O_cel') 
    nitrogen_measurements = doc.get('d15N_cel') 
    carbon_measurements = doc.get('d13C_cel') 

    if _ENABLE_d18O_ANALYSIS:
        if not(isinstance(oxygen_measurements, Sequence) and len(oxygen_measurements) >=2):
            print("Missing oxygen input data, skipping fraud detection. Measurements must be in list form and contain at least 2 measurements.")
            return doc
        else:
            oxygen_measurements = list(np.float_(oxygen_measurements))

    if _ENABLE_d15N_ANALYSIS:
        if not(isinstance(nitrogen_measurements, Sequence) and len(nitrogen_measurements) >=2):
            print("Missing nitrogen input data, skipping fraud detection. Measurements must be in list form and contain at least 2 measurements.")
            return doc
        else:
            nitrogen_measurements = list(np.float_(nitrogen_measurements))
    
    if _ENABLE_d13C_ANALYSIS:
        if not(isinstance(carbon_measurements, Sequence) and len(carbon_measurements) >=2):
            print("Missing carbon input data, skipping fraud detection. Measurements must be in list form and contain at least 2 measurements.")
            return doc
        else:
            carbon_measurements = list(np.float_(carbon_measurements))


    lat = float(doc['lat'])
    lon = float(doc['lon'])
    
    t = _ttest(lat, lon, oxygen_measurements, nitrogen_measurements, carbon_measurements)
    is_invalid, combined_p_value, p_value_oxygen, o_ref_mean, o_ref_var, p_value_carbon, p_value_nitrogen = t.evaluate()

    validity_details = {
        'p_value_oxygen': p_value_oxygen,
        'p_value_carbon': p_value_carbon,
        'p_value_nitrogen': p_value_nitrogen,
        'reference_oxygen_isoscape_name': t.oxygen_isoscape_name,
        'reference_oxygen_isoscape_creation_date': t.oxygen_isoscape_date,
        'reference_oxygen_isoscape_precision': t.oxygen_isoscape_precision,
        'reference_oxygen_isoscape_recall': t.oxygen_isoscape_recall,
        'd18O_cel_sample_mean': np.mean(oxygen_measurements),
        'd18O_cel_sample_variance': np.std(oxygen_measurements) ** 2,
        'd18O_cel_reference_mean': o_ref_mean,
        'd18O_cel_reference_variance': o_ref_var,
        'p_value': combined_p_value,
        'p_value_threshold': t.p_value_theshold,
    }
    
    doc['validity_details'] = validity_details
    doc['validity'] = _VALIDATION_FAILED_LABEL if is_invalid else _VALIDATION_PASSED_LABEL
    
    return doc
