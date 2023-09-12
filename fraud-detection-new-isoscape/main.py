import functions_framework
from google.events.cloud import firestore as firestoredata
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
import os
from os import path
import ee
from dateutil import parser
from origin_validation import ttest
from datetime import datetime, timedelta


app = initialize_app()
root = path.dirname(path.abspath(__file__))


@functions_framework.http
def reevaluate(request):
    # Initialize Earth Engine.
    if os.path.isfile('key.json'):

        # connection to the service account
        service_account = 'earth-engine-sa@river-sky-386919.iam.gserviceaccount.com'
        credentials = ee.ServiceAccountCredentials(
            service_account, 'key.json')
        ee.Initialize(credentials)
        print('initialized with key')

    # if in local env use the local user credential
    else:
        ee.Initialize()

    # Shared functions
    # TODO ddf common

    # get list of items in earth engine folder
    def get_asset_list(parent_name):
        parent_asset = ee.data.getAsset(parent_name)
        parent_id = parent_asset['name']
        asset_list = []
        child_assets = ee.data.listAssets({'parent': parent_id})['assets']
        update = False
        for child_asset in child_assets:
            child_id = child_asset['name']
            child_type = child_asset['type']
            if child_type in ['FOLDER', 'IMAGE_COLLECTION']:
                # Recursively call the function to get child assets
                asset_list.extend(get_asset_list(child_id))
            else:
                asset_list.append(child_id)

            asset = ee.data.getAsset(child_id)
            t = asset.get('updateTime')
            date_object = parser.parse(t).date()
            print(str(date_object))
            print((datetime.now()-timedelta(hours=27)) <= datetime.strptime(str(date_object), "%Y-%m-%d") <= (datetime.now()))
            if (datetime.now()-timedelta(hours=27)) <= datetime.strptime(str(date_object), "%Y-%m-%d") <= (datetime.now()):
                update = True
        return asset_list, update

        return ee.FeatureCollection(features)

    client: google.cloud.firestore.Client = firestore.client()

    ISOSCAPES_EE_PATH = 'projects/river-sky-386919/assets/isoscapes'

    # etl untrusted samples
    asset_list, update = get_asset_list(ISOSCAPES_EE_PATH)

    # TODO Verify if data didn't change
    # TODO Add versionning to assets (allow maximum to ten versions)
    if update:
        collectionSnapshot = client.collection(
            'untrusted_samples').get()
        for doc in collectionSnapshot:
            print(doc.id)
            value = doc.to_dict()
            is_invalid, combined_p_value, p_value_oxygen, p_value_carbon, p_value_nitrogen  = ttest(
                value.get('lat'), value.get('lon'), value.get('oxygen'),
                value.get('nitrogen'), value.get('carbon')).evaluate()
            value['is_invalid'] = is_invalid
            value['p_value'] = combined_p_value
            value['validity_details'] = {
                'p_value_oxygen': p_value_oxygen,
                'p_value_carbon': p_value_carbon,
                'p_value_nitrogen': p_value_nitrogen
            }

            affected_doc = client.collection('untrusted_samples').document(doc.id)
            affected_doc.set(value)

    return "Fraud detection on new isoscape executed"