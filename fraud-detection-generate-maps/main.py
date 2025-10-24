import base64
import functions_framework
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from google.cloud import storage
from google.auth import compute_engine
import ee
import geemap
import os
from google.cloud import pubsub_v1

app = initialize_app()

# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "river-sky-386919")

# Topic ID for GCS Pub/Sub topic. See fraud-detection-generate-maps/main.py for context.
TOPIC_ID = "fraud-detection-generate-maps-daily"

# Pub/Sub message to generate all maps (for every document) This is set in the Cloud Pub/Sub topic.
# See `fraud-detection-generate-maps-daily` Cloud Pub/Sub topic.
ALL_MAPS_MESSAGE_CONTENT = "ALL_MAPS"

# Google Cloud Storage bucket name and folder name
GCS_BUCKET_NAME = "timberid-public-to-internet"
GCS_FOLDER_NAME = "timberid-maps"

# Names of layers in geemap
RADIUS_MASK_1_KM_LAYER_NAME = "1 km radius mask"
RADIUS_MASK_10_KM_LAYER_NAME = "10 km radius mask"
BRAZIL_LAND_USE_LAYER_NAME = "Brazil Land Use"

# https://gee-community-catalog.org/projects/mapbiomas/
# Updated to Collection 8 (latest available version as of 2024)
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1"

# Triggered from a message on a Cloud Pub/Sub topic.
#
# Generates a land use map for the lat lon in the given Firestore document, using
# the MapBiomas Brazil deforestation / land use dataset.
#
# If message is empty or not a document_id, generates a land use map for all documents in the Firestore collection.
# If message is a document_id, generates a land use map for that document.
@functions_framework.cloud_event
def receive_pubsub_message_generate_maps(cloud_event):
    # Authenticate to Earth Engine using service account creds
    credentials = compute_engine.Credentials(scopes=['https://www.googleapis.com/auth/earthengine'])
    ee.Initialize(credentials, project=GCP_PROJECT_ID)

    # Print out the data from Pub/Sub, to prove that it worked
    pub_sub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()

    client: google.cloud.firestore.Client = firestore.client()
    collection_ref = client.collection("untrusted_samples")

    # Check if the document exists
    doc = collection_ref.document(pub_sub_message).get()

    # load MapBiomas Brazil deforestation / land use dataset
    land_use_mapbiomas_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
    # create the base geemap Map from which other maps will be generated
    mapbiomas_land_use_base_map = generate_initial_map(land_use_mapbiomas_image)

    if doc.exists:
        document_id = pub_sub_message
        print(f'Document exists, generating map for {document_id}')
        doc_dict = doc.to_dict()
        if 'lat' in doc_dict and 'lon' in doc_dict:
            generate_full_map_and_upload_to_gcs(doc_dict['lat'], doc_dict['lon'], land_use_mapbiomas_image, mapbiomas_land_use_base_map, document_id)
        else:
            print(f'Document {document_id} does not contain lat and lon.')
    elif pub_sub_message == ALL_MAPS_MESSAGE_CONTENT:
        print(f'Received message: {pub_sub_message}, generating all maps')

        # Get all documents in the collection
        docs = collection_ref.stream()

        # Setup Pub Sub topic to send messages
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(GCP_PROJECT_ID, TOPIC_ID)

        # Iterate over the documents and trigger the function per document_id
        for doc in docs:
            print(f'Publishing message for {doc.id}')
            document_id = doc.id
            doc_dict = doc.to_dict()
            if 'lat' in doc_dict and 'lon' in doc_dict:
                data = document_id.encode("utf-8")
                future = publisher.publish(topic_path, data)
                print(f"Published messaged for id: {document_id} to {topic_path}. Result: {future.result()}")
            else:
                print(f'Document {document_id} does not contain lat and lon.') 
    else:
        print(f'Received message: {pub_sub_message}. No action taken.')

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
    # Collection 8 uses "classification_YYYY" bands instead of "product_YYYY"
    land_use_layers_2021_simplified = (
        land_use_mapbiomas_image.select("classification_2021")
    )
    # display the full land use map
    # MapBiomas Collection 8 Land Use and Land Cover classification
    # Values range from 0-49 representing different land use classes
    vis_params = {
        "min": 0,
        "max": 49,
        "palette": [
            "#129912",  # 1 Forest
            "#1f4423",  # 3 Forest Formation
            "#006400",  # 4 Savanna Formation
            "#00ff00",  # 5 Mangrove
            "#687537",  # 49 Wooded Sandbank Vegetation
            "#935132",  # 11 Wetland
            "#bbfcac",  # 12 Grassland
            "#45c2a5",  # 32 Salt Flat
            "#b8af4f",  # 29 Rocky Outcrop
            "#f1c232",  # 50 Herbaceous Sandbank Vegetation
            "#ffffb2",  # 13 Other Non Forest Formations
            "#ffd966",  # 15 Pasture
            "#e974ed",  # 18 Agriculture
            "#d5a6bd",  # 19 Temporary Crops
            "#c27ba0",  # 39 Soy Beans
            "#fff3bf",  # 20 Sugar Cane
            "#ea9999",  # 40 Rice
            "#dd7e6b",  # 62 Cotton
            "#aa0000",  # 41 Other Temporary Crops
            "#ff99ff",  # 36 Perennial Crops
            "#d68fe2",  # 46 Coffee
            "#9c6f38",  # 47 Citrus
            "#0000ff",  # 35 Palm Oil
            "#d082de",  # 48 Other Perennial Crops
            "#cd49e4",  # 9 Forest Plantation
            "#e6ccff",  # 21 Mosaic of Uses
            "#af2a2a",  # 23 Beach and Dune
            "#8a2be2",  # 24 Urban Infrastructure
            "#968c46",  # 30 Mining
            "#0000ff",  # 25 Other Non Vegetated Areas
            "#45c2a5",  # 33 Water
            "#b5b5b5",  # 31 Aquaculture
            "#6b9932"   # 27 Not Observed
        ],
    }

    # Disable automatic EE initialization in geemap since we already initialized
    gee_mapbiomas_map = geemap.Map(ee_initialize=False)
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
    blob = bucket.blob(f"{GCS_FOLDER_NAME}/{document_id}.html")
    blob.upload_from_filename(html_file)
    print(f"Map uploaded to gs://{GCS_BUCKET_NAME}/{GCS_FOLDER_NAME}/{document_id}.html")
