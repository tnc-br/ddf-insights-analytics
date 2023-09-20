import functions_framework
from google.events.cloud import firestore as firestoredata
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
import os
from os import path
import ee
from dateutil import parser
from datetime import datetime, timedelta
from cloudevents.http import CloudEvent
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.auth
from google.cloud import storage

# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "river-sky-386919")

# The path to the assets in Earth Engine.
PARENT_PATH = f'projects/{GCP_PROJECT_ID}/assets/'

app = initialize_app()
root = path.dirname(path.abspath(__file__))

@functions_framework.cloud_event
def update_ee_acl(cloud_event: CloudEvent) -> None:
    """Triggers by a change to a Firestore document.
    Args:
        cloud_event: cloud event with information on the firestore event trigger
    """
    firestore_payload = firestoredata.DocumentEventData()
    firestore_payload._pb.ParseFromString(cloud_event.data)
    #print(f"Received event with ID: {cloud_event['id']} and data {cloud_event.data}")

    path_parts = firestore_payload.value.name.split("/")
    separator_idx = path_parts.index("documents")
    collection_path = path_parts[separator_idx + 1]
    document_path = "/".join(path_parts[(separator_idx + 2) :])

    print(f"Collection path: {collection_path}")
    print(f"Document path: {document_path}")
    client: google.cloud.firestore.Client = firestore.client()

    affected_doc = client.collection(collection_path).document(document_path)
    # cur_value = firestore_payload.value.fields["original"].string_value
    # new_value = cur_value.upper()
    doc = affected_doc.get()

    # Initialize Earth Engine.
    credentials, project_id = google.auth.default()
    ee.Initialize(credentials)

    # Shared functions
    # TODO ddf common


    def check_org(org_email, org_name):

        #Download service account file
        # Initialise a client
        storage_client = storage.Client()
        # Create a bucket object for our bucket
        bucket = storage_client.get_bucket("gadmin_credentials")
        # Create a blob object from the filepath
        blob = bucket.blob("credentials.json")
        # Download the file to a destination
        blob.download_to_filename('/tmp/credentials.json')
        #Google ADMIN
        SCOPES = ["https://www.googleapis.com/auth/cloud-identity.groups", "https://www.googleapis.com/auth/admin.directory.user", "https://www.googleapis.com/auth/admin.directory.group"]    

        SERVICE_ACCOUNT_FILE = '/tmp/credentials.json'

        service_account_credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES).with_subject("admin@timberid.org")

        service = build('admin', 'directory_v1', credentials=service_account_credentials)

        #add_request = service.members().insert(groupKey = org_email, body = member)
        add_request = service.groups().list(customer = 'C02hsynl1')
        add_response = add_request.execute()
        org_exists = False
        for group in add_response.get('groups'):
            if group['email'] == org_email:
                org_exists = True

        if org_exists == False:
            add_request = service.groups().insert(body = {
                "kind": "group",
                "email": org_email,
                "name": org_name,
                "description": "group for " + org_name + " organization" 
            })
            add_request.execute()
            #TODO ADD org folder to earth engine
            ee.data.createAsset({'type': 'Folder'}, PARENT_PATH + 'ee_org/' + org_name)
            print('new org created')

    # get list of items in earth engine folder
    def get_asset_list(parent_name, folder_list):
        parent_asset = ee.data.getAsset(parent_name)
        parent_id = parent_asset['name']
        asset_list = []
        child_assets = ee.data.listAssets({'parent': parent_id})['assets']
        for child_asset in child_assets:
            child_id = child_asset['name']
            child_type = child_asset['type']
            if child_type in ['FOLDER', 'IMAGE_COLLECTION']:
                # Recursively call the function to get child assets
                asset_list.extend(get_asset_list(child_id, folder_list))
            else:
                asset_list.append(child_id)
            if child_type == 'FOLDER' and child_id not in asset_list:
                folder_list.append(child_id)
        return asset_list


    def assign_acl(asset_list, folder_list, prefix, acl):
        #assign writer acl for an organization own folder and assets
        for asset_id in asset_list:
            print("asset  " + asset_id)
            if prefix in asset_id:
                print("in assseet " + asset_id)
                aclUpdate = ee.data.getAssetAcl(asset_id)
                arr = aclUpdate.get(acl)
                if ('group:'+org_email) not in arr:
                    arr.append('group:'+org_email)
                    aclUpdate[acl] = arr
                    ee.data.setAssetAcl(asset_id, aclUpdate)
        for asset_id in folder_list:
            print("folder  " + asset_id)
            if prefix in asset_id:
                print("in folder  " + asset_id)
                aclUpdate = ee.data.getAssetAcl(asset_id)
                arr = aclUpdate.get(acl)
                if ('group:'+org_email) not in arr:
                    arr.append('group:'+org_email)
                    aclUpdate[acl] = arr
                    ee.data.setAssetAcl(asset_id + '/', aclUpdate)




    # ORGANIZATIONS
    if doc.exists:

        folder_list = []
        asset_list = get_asset_list(PARENT_PATH, folder_list)
        
        value = doc.to_dict()
        if 'org_email' in value and 'org_name' in value:
            org_email = value.get('org_email')
            org_name = value.get('org_name')
\
            #check if org_email is associated to a google group
            check_org(org_email, org_name)

            prefix = PARENT_PATH + 'ee_org/' + org_name

            assign_acl(asset_list, folder_list, prefix, 'writers')
            
        else:
            print("org authorization setup failed because of missing field")

    #TODO ORGANIZATION DELETED

    return "Organizations EE ACL executed"