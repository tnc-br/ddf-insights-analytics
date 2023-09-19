from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore as firestoredata
# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from fraud_detection_process_sample import fraud_detection_process_sample
from fraud_detection_fetch_land_use_data import fraud_detection_fetch_land_use_data
from fraud_detection_generate_map_and_upload_to_gcs import fraud_detection_generate_map_and_upload_to_gcs
from fraud_detection_fetch_mapbiomas_alerts import fraud_detection_fetch_mapbiomas_alerts
import traceback
from collections.abc import Sequence
from google.protobuf.json_format import MessageToDict
from google.auth import compute_engine
import ee

app = initialize_app()

# Fields that are not inputs to the fraud detection, and should not trigger a re-run
OUTPUT_FIELDS = set(["validity", "validity_details", "water_pct", "land_use_anthropic_pct", "land_use_primary_vegetation_pct", "land_use_secondary_vegetation_or_regrowth_pct", "alerts"])

@functions_framework.cloud_event
def hello_firestore(cloud_event: CloudEvent) -> None:
    """Triggers by a change to a Firestore document.
    Args:
        cloud_event: cloud event with information on the firestore event trigger
    """
    firestore_payload = firestoredata.DocumentEventData()
    firestore_payload._pb.ParseFromString(cloud_event.data)

    collection_path, document_path = parse_path_parts(firestore_payload.value.name)

    print(f"Collection path: {collection_path}")
    print(f"Document path: {document_path}")

    client: google.cloud.firestore.Client = firestore.client()
    affected_doc = client.collection(collection_path).document(document_path)

    # Checks whether Firestore document is new or whether its input fields have been updated
    firestore_payload_dict = MessageToDict(firestore_payload._pb)
    if "updateMask" in firestore_payload_dict:
        update_mask_inputs_only = set(firestore_payload_dict["updateMask"]["fieldPaths"]) - OUTPUT_FIELDS
        if len(update_mask_inputs_only) == 0:
            print("No inputs have changed, skipping")
            return

    # Authenticate to Earth Engine using service account creds
    credentials = compute_engine.Credentials(scopes=['https://www.googleapis.com/auth/earthengine'])
    ee.Initialize(credentials)
    
    value = affected_doc.get().to_dict()
    
    if "lat" in value and "lon" in value:
        # STEP 1: calculate the validity of the sample
        try:
            value = fraud_detection_process_sample(value)
        except Exception as e:
            print(f'caught {type(e)} while calculating the validity of the sample: e')
            print(traceback.format_exc())
        
        # STEP 2: calculate land use percentages from MapBiomas, and generate a map 
        try:
            value = fraud_detection_fetch_land_use_data(value)

        except Exception as e:
            print(f'caught {type(e)} while calculating land use percentages or map: e')
            print(traceback.format_exc())

        # STEP 3: upload a map to GCS showing land use from MapBiomas
        try:
            fraud_detection_generate_map_and_upload_to_gcs(document_path)

        except Exception as e:
            print(f'caught {type(e)} while creating land use map from MapBiomas: e')
            print(traceback.format_exc())

        # STEP 4: query the MapBiomas Alerta API to get alerts near the given (lat,lon)
        try:
            value = fraud_detection_fetch_mapbiomas_alerts(value)
        except Exception as e:
            print(f'caught {type(e)} while querying the MapBiomas Alerta API: e')
            print(traceback.format_exc())
    
    # Finally: update the Firestore document with the validity and additional information
    # see https://github.com/googleapis/python-firestore/blob/main/google/cloud/firestore_v1/document.py
    affected_doc.set(value)

def parse_path_parts(firestore_payload_name: str):
    """
    Parses a Firestore document path and returns the collection path and document path.

    Args:
        path_parts (List[str]): A list of strings representing the parts of the document path.

    Returns:
        A tuple containing the collection path (str) and document path (str).
    """
    path_parts = firestore_payload_name.split("/")
    separator_idx = path_parts.index("documents")
    collection_path = path_parts[separator_idx + 1]
    document_path = "/".join(path_parts[(separator_idx + 2) :])

    return collection_path, document_path
