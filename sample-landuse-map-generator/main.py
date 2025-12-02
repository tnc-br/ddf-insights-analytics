from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore as firestoredata
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from google.cloud import storage
from google.auth import compute_engine
import ee
import geemap
import os
import traceback
from google.protobuf.json_format import MessageToDict

app = initialize_app()

# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "river-sky-386919")

# Google Cloud Storage bucket name and folder name
GCS_BUCKET_NAME = "timberid-public-to-internet"
GCS_FOLDER_NAME = "timberid-maps"

# Fields that should trigger map regeneration (inputs only)
# If only output fields are updated (like map_url), skip regeneration
OUTPUT_FIELDS = set([
    "map_url",
    "map_generated_at",
])

# Names of layers in geemap
RADIUS_MASK_1_KM_LAYER_NAME = "1 km radius mask"
RADIUS_MASK_10_KM_LAYER_NAME = "10 km radius mask"
BRAZIL_LAND_USE_LAYER_NAME = "Brazil Land Use"

# https://gee-community-catalog.org/projects/mapbiomas/
# Updated to Collection 8 (latest available version as of 2024)
MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE = "projects/mapbiomas-public/assets/brazil/lulc/collection8/mapbiomas_collection80_integration_v1"

# Triggered by a change to a Firestore document in the untrusted_samples collection.
#
# Generates an interactive HTML map for the sample location showing:
# - MapBiomas Brazil land use data (Collection 8)
# - 1km radius buffer (white circle)
# - 10km radius context area
#
# The map is uploaded to Google Cloud Storage and the URL is saved back to the document.
#
# Args:
#     cloud_event: CloudEvent with information on the Firestore document change
@functions_framework.cloud_event
def generate_sample_map(cloud_event: CloudEvent) -> None:
    """Generates an interactive map when a sample document is created or updated."""
    
    firestore_payload = firestoredata.DocumentEventData()
    firestore_payload._pb.ParseFromString(cloud_event.data)

    collection_path, document_id = parse_path_parts(firestore_payload.value.name)

    print(f"Collection: {collection_path}")
    print(f"Document ID: {document_id}")

    # Check if only output fields were updated (prevent infinite loop)
    firestore_payload_dict = MessageToDict(firestore_payload._pb)
    if "updateMask" in firestore_payload_dict:
        updated_fields = set(firestore_payload_dict["updateMask"]["fieldPaths"])
        input_fields_updated = updated_fields - OUTPUT_FIELDS
        
        if len(input_fields_updated) == 0:
            print(f"Only output fields updated: {updated_fields}. Skipping map generation.")
            return
    
    # Get the document data
    client: google.cloud.firestore.Client = firestore.client()
    affected_doc = client.collection(collection_path).document(document_id)
    doc_data = affected_doc.get().to_dict()

    # Validate required fields
    if not doc_data:
        print(f"Document {document_id} not found or empty.")
        return
    
    if 'lat' not in doc_data or 'lon' not in doc_data:
        print(f"Document {document_id} missing lat/lon coordinates. Skipping map generation.")
        return

    lat = doc_data['lat']
    lon = doc_data['lon']
    print(f"Generating map for sample at ({lat}, {lon})")

    # Authenticate to Earth Engine using service account credentials
    try:
        credentials = compute_engine.Credentials(scopes=['https://www.googleapis.com/auth/earthengine'])
        ee.Initialize(credentials, project=GCP_PROJECT_ID)
    except Exception as e:
        print(f"Failed to initialize Earth Engine: {e}")
        print(traceback.format_exc())
        return

    # Generate and upload the map
    try:
        # Load MapBiomas Brazil land use dataset
        land_use_mapbiomas_image = ee.Image(MAPBIOMAS_BRAZIL_LAND_USE_EE_IMAGE)
        
        # Create the base map
        mapbiomas_land_use_base_map = generate_initial_map(land_use_mapbiomas_image)
        
        # Generate full map with buffers and upload to GCS
        map_url = generate_full_map_and_upload_to_gcs(
            lat, lon, 
            land_use_mapbiomas_image, 
            mapbiomas_land_use_base_map, 
            document_id
        )
        
        # Update the document with the map URL
        from datetime import datetime
        affected_doc.update({
            "map_url": map_url,
            "map_generated_at": datetime.utcnow()
        })
        
        print(f"✅ Map generated and uploaded successfully: {map_url}")
        
    except Exception as e:
        print(f"❌ Error generating map for {document_id}: {e}")
        print(traceback.format_exc())

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
        str: The public URL of the uploaded map in Google Cloud Storage.
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
    map_url = upload_map_to_gcs(filename, document_id)
    
    return map_url

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
        str: The public URL of the uploaded map.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"{GCS_FOLDER_NAME}/{document_id}.html")
    blob.upload_from_filename(html_file)
    
    # Generate public URL
    map_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{GCS_FOLDER_NAME}/{document_id}.html"
    print(f"Map uploaded to {map_url}")
    
    return map_url

def parse_path_parts(firestore_payload_name: str):
    """
    Parses a Firestore document path and returns the collection path and document ID.
    
    Args:
        firestore_payload_name (str): The full Firestore document path from the event payload.
            Example: "projects/PROJECT_ID/databases/(default)/documents/untrusted_samples/DOCUMENT_ID"
    
    Returns:
        tuple: (collection_path, document_id)
            Example: ("untrusted_samples", "6ed0ffa36587c49f5b54")
    """
    path_parts = firestore_payload_name.split("/documents/")[1].split("/")
    collection_path = path_parts[0]
    document_id = path_parts[1]
    
    return collection_path, document_id
