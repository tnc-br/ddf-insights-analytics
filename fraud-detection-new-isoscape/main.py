import functions_framework
from google.events.cloud import firestore as firestoredata
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
import os
from os import path
import ee
from dateutil import parser
from datetime import datetime, timedelta
from google.auth import compute_engine

# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")

# The path to the isoscapes folder in Earth Engine.
ISOSCAPES_EE_PATH = f'projects/{GCP_PROJECT_ID}/assets/isoscapes'

app = initialize_app()
root = path.dirname(path.abspath(__file__))

@functions_framework.http
def reevaluate(request):
    # Initialize Earth Engine.
    # Authenticate to Earth Engine using service account creds
    credentials = compute_engine.Credentials(scopes=['https://www.googleapis.com/auth/earthengine'])
    ee.Initialize(credentials)

    # TODO asset list is not needed, update function to only return 

    # get list of items in earth engine folder
    def is_isoscapes_updated(parent_name):
        parent_asset = ee.data.getAsset(parent_name)
        parent_id = parent_asset['name']
        child_assets = ee.data.listAssets({'parent': parent_id})['assets']
        update = False
        for child_asset in child_assets:
            child_id = child_asset['name']
            asset = ee.data.getAsset(child_id)
            t = asset.get('updateTime')
            date_object = parser.parse(t).date()
            print(str(date_object))
            print((datetime.now()-timedelta(hours=27)) <= datetime.strptime(str(date_object), "%Y-%m-%d") <= (datetime.now()))
            if (datetime.now()-timedelta(hours=27)) <= datetime.strptime(str(date_object), "%Y-%m-%d") <= (datetime.now()):
                update = True
                break
        return update

    client: google.cloud.firestore.Client = firestore.client()

    # etl untrusted samples
    update = is_isoscapes_updated(ISOSCAPES_EE_PATH)

    # TODO Add versionning to assets (allow maximum to ten versions)
    if update:
        collectionSnapshot = client.collection(
            'untrusted_samples').get()
        for doc in collectionSnapshot:
            #rewrite doc to trigger fraud-detection-update-sample
            print(doc.id)
            value = doc.to_dict()
            affected_doc = client.collection('untrusted_samples').document(doc.id)
            affected_doc.set(value)

    return "Fraud detection on new isoscape executed"