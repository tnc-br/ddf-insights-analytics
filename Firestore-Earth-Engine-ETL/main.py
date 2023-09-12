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
    def get_asset_list(parent_name) -> list:
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
            print (e.message)

        return asset_list

    def transform_snapshot_to_featuresCollection(collectionSnapshot, schema) -> dict :
        features = {}
        for doc in collectionSnapshot:
            #TODO doc should come from an organization that is shared or trusted-org
            raw_value = doc.to_dict()
            print(doc)
            try:
                is_lat_lon_valid = False
                if ('lat' in raw_value) and ('lon' in raw_value):
                    try:
                        lat = float(raw_value['lat'])
                        lon = float(raw_value['lon'])
                        is_lat_lon_valid = True
                    except Exception as e:
                        print("lat lon can not be casted into float")
                        print (e.message)
                if is_lat_lon_valid :
                    if 'org_name' in raw_value:
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
                            print(e.message)
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
                print(e.message)
                #str(raw_value['id'])

        return features
        #return ee.FeatureCollection(features)

    client: google.cloud.firestore.Client = firestore.client()

    ORG_EE_PATH = 'projects/river-sky-386919/assets/ee_org'

    # try:

    #     #etl trusted samples 
    #     #TODO add "d18O of precipitation"
    #     trusted_schema = ["lat", "lon", "org_name" ,"d18o_cel","d15n_wood","d13c_wood","code","code_lab", "created_on", "date_of_harvest","vpd","mean_annual_temperature","mean_annual_precipitation"]
    #     trustedCollectionSnapshot = client.collection('trusted_samples').get() #.select(trusted_schema).get()
    #     trustedFeatureCollection = transform_snapshot_to_featuresCollection(trustedCollectionSnapshot, trusted_schema)




    #     for k, v in trustedFeatureCollection.items():
    #         org_path = ORG_EE_PATH + '/' + k 
    #         org_asset_list = get_asset_list(org_path)

    #         trustedAssetId = org_path + '/trusted_samples'

    #         #TODO Verify if data didn't change 
    #         #TODO Add versionning to assets (allow maximum to ten versions)
    #         #TODO Verify if data didn't change 


    #         if trustedAssetId in org_asset_list:
    #             ee.data.deleteAsset(trustedAssetId)

    #         task = ee.batch.Export.table.toAsset(**{
    #             'collection': ee.FeatureCollection(v),
    #             'description': 'firestoreToAssetExample',
    #             'assetId': trustedAssetId
    #             })
    #         task.start()
    #         while task.active():
    #             print('Polling for task (id: {}).'.format(task.id))
    #             time.sleep(5)

                
    #         print(task.status())
    # except:
    #     print("make sure all items in trusted samples database have all required fields")



    try:
        untrusted_schema = ["lat", "lon" ,"carbon","nitrogen","oxygen","validity","validity_details", "created_on", "date_of_harvest", "org_name"]
        untrustedCollectionSnapshot = client.collection('untrusted_samples').get() #.select(untrusted_schema).get()
        untrustedFeatureCollection = transform_snapshot_to_featuresCollection(untrustedCollectionSnapshot, untrusted_schema)

        for k, v in untrustedFeatureCollection.items():
            org_path = ORG_EE_PATH + '/' + k 
            org_asset_list = get_asset_list(org_path)
            print(k)
            if org_asset_list != []:
                untrustedAssetId = org_path + '/untrusted_samples'

                #TODO Verify if data didn't change 
                #TODO Add versionning to assets (allow maximum to ten versions)
                #TODO Verify if data didn't change 

                if untrustedAssetId in org_asset_list:
                    ee.data.deleteAsset(untrustedAssetId)

                task = ee.batch.Export.table.toAsset(**{
                    'collection': ee.FeatureCollection(v),
                    'description': 'firestoreToAssetExample',
                    'assetId': untrustedAssetId
                    })
                task.start()
                while task.active():
                    print('Polling for task (id: {}).'.format(task.id))
                    time.sleep(5)
                print(task.status())

                



    except:
        print("make sure all items in untrusted samples database have all required fields")
    
        
    return 'done'