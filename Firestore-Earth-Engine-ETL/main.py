import functions_framework
from google.events.cloud import firestore as firestoredata
# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
import os
from os import path, environ
import ee
import time
import json
from datetime import datetime
import google.auth

# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "river-sky-386919")

# The path to the ee_org folder in Earth Engine.
ORG_EE_PATH = f'projects/{GCP_PROJECT_ID}/assets/ee_org'

app = initialize_app()
root = path.dirname(path.abspath(__file__))

@functions_framework.http
def etl(request):
    """Triggers by a change to a Firestore document.
    Args:
        cloud_event: cloud event with information on the firestore event trigger
    """
    # Initialize Earth Engine.
    # Initialize Earth Engine.
    credentials, project_id = google.auth.default()
    ee.Initialize(credentials)

    # Shared functions
    #TODO ddf common 

    #get list of items in earth engine folder
    def get_asset_list(parent_name):
        asset_list = []
        try:
            parent_asset = ee.data.getAsset(parent_name)
            parent_id = parent_asset['name']
            child_assets = ee.data.listAssets({'parent': parent_id})['assets']
            for child_asset in child_assets:
                child_id = child_asset['name']
                child_type = child_asset['type']
                if child_type in ['FOLDER', 'IMAGE_COLLECTION']:
                    # Recursively call the function to get child assets
                    asset_list.extend(get_asset_list(child_id))
                else:
                    asset_list.append(child_id)
        except Exception as e:
            print('can not retreive assets list of ' + parent_name + ' , verify if folder path exists')
            print (e)
            return "NaN"

        return asset_list

    def transform_snapshot_to_featuresCollection_trusted(collectionSnapshot) -> dict :
        features = {}
        for doc in collectionSnapshot:
            #TODO doc should come from an organization that is shared or trusted-org
            raw_value = doc.to_dict()
            try:
                is_lat_lon_valid = False
                if ('lat' in raw_value) and ('lon' in raw_value):
                    try:
                        lat = float(raw_value['lat'])
                        lon = float(raw_value['lon'])
                        is_lat_lon_valid = True
                    except Exception as e:
                        print("lat lon can not be casted into float")
                        print (e)
                if is_lat_lon_valid :
                    if 'org_name' in raw_value and raw_value['org_name'] != "":
                        org_name = raw_value['org_name'].lower()
                    else:
                        org_name = 'no-org'
                        raw_value['org_name'] = org_name
                    if "created_on" in raw_value:
                        try:
                            created_on = ee.Date(raw_value["created_on"])
                        except Exception as e :
                            print('date format is invalid')
                            created_on = ee.Date(datetime.now())
                            print(e)
                    else:
                        created_on = ee.Date(datetime.now())
                    if 'points' in raw_value:
                        for point in raw_value['points']:
                            value = point
                            new_dict = {k: str(v) for k, v in value.items()}
                            feature = ee.Feature(ee.Geometry.Point(lon, lat), new_dict)
                            feature.set('system:time_start', created_on)
                            features.setdefault(org_name,[]).append(feature)
                   
                else:
                    print("skipping entry: " + str(doc.id) + " , invalid lat/lon")
            except Exception as e:
                print("skipping entry: " + + str(doc.id) +  " , invalid untrusted sample format")
                print(e)
                #str(raw_value['id'])

        return features
        #return ee.FeatureCollection(features)

    def transform_snapshot_to_featuresCollection_untrusted(collectionSnapshot, schema) -> dict :
        features = {}
        for doc in collectionSnapshot:
            #TODO doc should come from an organization that is shared or trusted-org
            raw_value = doc.to_dict()
            try:
                is_lat_lon_valid = False
                if ('lat' in raw_value) and ('lon' in raw_value):
                    try:
                        lat = float(raw_value['lat'])
                        lon = float(raw_value['lon'])
                        is_lat_lon_valid = True
                    except Exception as e:
                        print("lat lon can not be casted into float")
                        print (e)
                if is_lat_lon_valid :
                    if 'org_name' in raw_value  and raw_value['org_name'] != "":
                        org_name = raw_value['org_name']
                    else:
                        org_name = 'no-org'
                        raw_value['org_name'] = 'no-org'
                    if "created_on" in raw_value:
                        try:
                            created_on = ee.Date(raw_value["created_on"])
                        except Exception as e :
                            print('date format is invalid')
                            created_on = ee.Date(datetime.now())
                            print(e)
                    else:
                        created_on = ee.Date(datetime.now())
                    value = {}
                    for field in schema:
                        if field in raw_value:
                            value[field] = raw_value[field]
                        else:
                            value[field] = "NaN"
                    
                    new_dict = {k: str(v) for k, v in value.items()}
                    feature = ee.Feature(ee.Geometry.Point(lon, lat), new_dict)
                    feature.set('system:time_start', created_on)
                    features.setdefault(org_name,[]).append(feature)
                else:
                    print("skipping entry: " + str(doc.id) + " , invalid lat/lon")
            except Exception as e:
                print("skipping entry: " + + str(doc.id) +  " , invalid untrusted sample format")
                print(e)
                #str(raw_value['id'])

        return features
        #return ee.FeatureCollection(features)


    def save_collection_to_ee(collection, asset_name):
        for k, v in collection.items():
            org_path = ORG_EE_PATH + '/' + k.lower()
            org_asset_list = get_asset_list(org_path)
            if org_asset_list != "NaN" :
                AssetId = org_path + '/' + asset_name

                #TODO Verify if data didn't change 
                #TODO Add versionning to assets (allow maximum to ten versions)
                #TODO Verify if data didn't change 


                if AssetId in org_asset_list:
                    ee.data.deleteAsset(AssetId)

                task = ee.batch.Export.table.toAsset(**{
                    'collection': ee.FeatureCollection(v),
                    'description': 'firestoreToAssetExample',
                    'assetId': AssetId
                    })
                task.start()
                while task.active():
                    print('Polling for task (id: {}).'.format(task.id))
                    time.sleep(5)

                    
                print(task.status())
                org_email = k.lower() + "-test@timberid.org"
                acl = { "writers": ['group:'+org_email]}
                ee.data.setAssetAcl(AssetId, acl)
    client: google.cloud.firestore.Client = firestore.client()

    try:

        #etl trusted samples 
        #TODO add "d18O of precipitation"
        trusted_schema = ["lat", "lon", "points", "created_on", "org_name"] # ,"d18o_cel","d15n_wood","d13c_wood","code","code_lab",  "date_of_harvest","vpd","mean_annual_temperature","mean_annual_precipitation"]
        trustedCollectionSnapshot = client.collection('trusted_samples').get() #.select(trusted_schema).get()
        trustedFeatureCollection = transform_snapshot_to_featuresCollection_trusted(trustedCollectionSnapshot)

        save_collection_to_ee(trustedFeatureCollection, "trusted_samples")

    except Exception as e:
        print("make sure all items in trusted samples database have all required fields")
        print(e)




    try:
        untrusted_schema = ["lat", "lon" ,"carbon","nitrogen","oxygen","validity","validity_details", "created_on", "date_of_harvest", "org_name"]
        untrustedCollectionSnapshot = client.collection('untrusted_samples').get() #.select(untrusted_schema).get()
        untrustedFeatureCollection = transform_snapshot_to_featuresCollection_untrusted(untrustedCollectionSnapshot, untrusted_schema)

        save_collection_to_ee(untrustedFeatureCollection, "untrusted_samples")

                
    except Exception as e:
        print("make sure all items in untrusted samples database have all required fields")
        print(e)
    
        
    return 'done'