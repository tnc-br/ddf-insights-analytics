import base64
import functions_framework
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from google.cloud import storage
from google.auth import compute_engine
import ee
import geemap
import os

app = initialize_app()

# Google Cloud Storage bucket name and folder name
GCS_BUCKET_NAME = "timberid-public-to-internet"
GCS_FOLDER_NAME = "timberid-maps"

# Names of layers in geemap
RADIUS_MASK_1_KM_LAYER_NAME = "1 km radius mask"
RADIUS_MASK_10_KM_LAYER_NAME = "10 km radius mask"
BRAZIL_LAND_USE_LAYER_NAME = "Brazil Land Use"

# https://gee-community-catalog.org/projects/mapbiomas/
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE =  "projects/mapbiomas-workspace/public/collection7_1/mapbiomas_collection71_deforestation_regeneration_v1"

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Authenticate to Earth Engine using service account creds
    credentials = compute_engine.Credentials(scopes=['https://www.googleapis.com/auth/earthengine'])
    ee.Initialize(credentials)

    # Print out the data from Pub/Sub, to prove that it worked
    document_id = base64.b64decode(cloud_event.data["message"]["data"]).decode()

    client: google.cloud.firestore.Client = firestore.client()
    collection_ref = client.collection("untrusted_samples")

    # Check if the document exists
    doc = collection_ref.document(document_id).get()

    # load MapBiomas Brazil deforestation / land use dataset
    land_use_mapbiomas_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
    # create the base geemap Map from which other maps will be generated
    mapbiomas_land_use_base_map = generate_initial_map(land_use_mapbiomas_image)

    if doc.exists:
        print(f'Document exists, generating map for {document_id}')
        doc_dict = doc.to_dict()
        if 'lat' in doc_dict and 'lon' in doc_dict:
            generate_full_map_and_upload_to_gcs(doc_dict['lat'], doc_dict['lon'], land_use_mapbiomas_image, mapbiomas_land_use_base_map, document_id)
        else:
            print(f'Document {document_id} does not contain lat and lon.')
    else:
        print(f'Document does not exist for id: {document_id}, generating all maps')
        # Get all documents in the collection
        docs = collection_ref.stream()
        # Iterate over the documents and print their IDs and data
        for doc in docs:
            print(f'Generating map for {doc.id}')
            document_id = doc.id
            doc_dict = doc.to_dict()
            if 'lat' in doc_dict and 'lon' in doc_dict:
                generate_full_map_and_upload_to_gcs(doc_dict['lat'], doc_dict['lon'], land_use_mapbiomas_image, mapbiomas_land_use_base_map, document_id)
            else:
                print(f'Document {document_id} does not contain lat and lon.')    

def generate_initial_map(land_use_mapbiomas_image):
    """
    Generates an initial map of a given location using the Google Earth Engine (GEE) Python API.
    
    Args:
        lat (float): The latitude of the location in decimal degrees.
        lon (float): The longitude of the location in decimal degrees.
        land_use_mapbiomas_image (ee.Image): An `ee.Image` object representing the land use map.
    
    Returns:
        A `geemap.Map` object representing the initial map.
    """
    # load MapBiomas Brazil deforestation + land use dataset
    land_use_layers_2021_simplified = (
        land_use_mapbiomas_image.select("product_2021").divide(100).floor()
    )
    # display the full land use map
    vis_params = {
        "min": 1,
        "max": 7,
        "palette": [
            "#fffbc2",  # 1, 'Anthropic'
            "#09611f",  # 2, 'Primary Vegetation'
            "#4ea376",  # 3, 'Secondary Vegetation'
            "#e31a1c",  # 4, 'Deforestation in  Primary Vegetation'
            "#94fc03",  # 5, 'Secondary Vegetation Regrowth'
            "#ffa500",  # 6, 'Deforestation in Secondary Vegetation'
            "#212121",  # 7, 'Not applied'
        ],
    }

    gee_mapbiomas_map = geemap.Map()
    gee_mapbiomas_map.addLayer(land_use_layers_2021_simplified, vis_params, BRAZIL_LAND_USE_LAYER_NAME)
    return gee_mapbiomas_map

def generate_full_map_and_upload_to_gcs(lat, lon, land_use_mapbiomas_image, mapbiomas_land_use_base_map, document_id):
    """
    Generates a map of a given location using the Google Earth Engine (GEE) Python API and uploads the map to Google Cloud Storage (GCS).
    
    Args:
        lat (float): The latitude of the location in decimal degrees.
        lon (float): The longitude of the location in decimal degrees.
        land_use_mapbiomas_image (ee.Image): An `ee.Image` object representing the land use map.
        mapbiomas_land_use_base_map (geemap.Map): A `geemap.Map` object representing the base map.
        document_id (str): The ID of the Firestore document.
    
    Returns:
        None
    """
    # create a 1 km and 10 km radius buffer around the point
    point = ee.Geometry.Point(lon, lat)
    radius_1km_buffer = point.buffer(1000)
    radius_10km_buffer = point.buffer(10000)

    if len(mapbiomas_land_use_base_map.layers) > 2:
        mapbiomas_land_use_base_map.remove_ee_layer(RADIUS_MASK_1_KM_LAYER_NAME)
        mapbiomas_land_use_base_map.remove_ee_layer(RADIUS_MASK_10_KM_LAYER_NAME)

    # create a mask for the 10 km radius buffer with a 10km hole
    mapbiomas_land_use_base_map.addLayer(land_use_mapbiomas_image.mask().geometry().difference(radius_10km_buffer), {}, RADIUS_MASK_10_KM_LAYER_NAME)
    # add the 1 km radius buffer as a layer
    mapbiomas_land_use_base_map.addLayer(radius_1km_buffer, {"color": "white"}, RADIUS_MASK_1_KM_LAYER_NAME)
    # center the map on the point
    mapbiomas_land_use_base_map.centerObject(radius_10km_buffer, 11)
    
    # generate the html file and upload to GCS
    filename = generate_html_file_from_map(mapbiomas_land_use_base_map, document_id)
    upload_map_to_gcs(filename, document_id)

def generate_html_file_from_map(gee_mapbiomas_map, document_id):
    """
    Generates an HTML file from a Google Earth Engine (GEE) map and saves it to disk.
    
    Args:
        gee_map (geemap.Map): A `geemap.Map` object representing the map to convert to HTML.
        document_id (str): The ID of the Firestore document.
    
    Returns:
        The full filename of the generated HTML file.
    """

    download_dir = os.getcwd()
    html_file = os.path.join(download_dir, f"{document_id}.html")
    gee_mapbiomas_map.to_html(
        filename=html_file, title="Land Use details", width="100%", height="300px"
    )
    return html_file

def upload_map_to_gcs(html_file, document_id):
    """
    Uploads an HTML file to Google Cloud Storage (GCS).
    
    Args:
        html_file (str): The full filename of the HTML file to upload.
        document_id (str): The ID of the Firestore document.
    
    Returns:
        None
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(GCS_FOLDER_NAME + "/" + document_id)
    blob.upload_from_filename(html_file)
