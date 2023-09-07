from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore as firestoredata
# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from origin_validation import ttest
from origin_validation_enhancement import origin_enhancement
from upload_map_to_gcs import generate_map_and_upload_to_gcs
import traceback
from collections.abc import Sequence
from fetch_mapbiomas_alerts import fetch_alerts

app = initialize_app()

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

    if not is_document_creation_or_update_with_new_inputs(firestore_payload.old_value, firestore_payload.value):
        print("No inputs have changed, skipping")
        return
    
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
            generate_map_and_upload_to_gcs(float(value.get('lat')), float(value.get('lon')), document_path)

        except Exception as e:
            print(f'caught {type(e)} while creating land use map from MapBiomas: e')
            print(traceback.format_exc())

        # STEP 4: query the MapBiomas Alerta API to get alerts near the given (lat,lon)
        try:
            value = fetch_alerts(float(value.get('lat')), float(value.get('lon')))
        except Exception as e:
            print(f'caught {type(e)} while querying the MapBiomas Alerta API: e')
            print(traceback.format_exc())
    
    # Finally: update the Firestore document with the validity and additional information
    # see https://github.com/googleapis/python-firestore/blob/main/google/cloud/firestore_v1/document.py
    affected_doc.set(value)

def is_document_creation_or_update_with_new_inputs(old_value, new_value) -> bool:
    """Checks whether a Firestore document is new or whether its input fields have been updated.
    Args:
        old_value: A dictionary representing the fields and their values of the Firestore document before the update. None if this is a document creation.
        new_value: A dictionary representing the fields and their values of the Firestore document after the update.
    Returns:
        True if this is a document creation or a document update with input fields have been updated. False if this is a document update where only output fields have changed.
    """
    if old_value:
        # Clear all the "output" fields, to verify whether the inputs have changed
        output_fields = ["validity", "validity_details", "water_pct", "land_use_anthropic_pct", "land_use_primary_vegetation_pct", "land_use_secondary_vegetation_or_regrowth_pct", "alerts"]
        new_value_without_outputs = new_value.copy()
        old_value_without_outputs = old_value.copy()

        for field in output_fields:
            if field in old_value_without_outputs:
                old_value_without_outputs.pop(field, None)
            if field in new_value_without_outputs:
                new_value_without_outputs.pop(field, None)
                
        return not new_value_without_outputs == old_value_without_outputs
    return True


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

def fraud_detection_fetch_land_use_data(value: dict):
    """
    Fetches land use data for a given sample location and updates the sample dictionary with the results.

    Args:
        value (dict): A dictionary representing the sample to be processed. Must contain the following keys:
            - lat (float): The latitude of the sample location.
            - lon (float): The longitude of the sample location.

    Returns:
        None.
    """
    water_pct, land_use_anthropic_pct, land_use_primary_vegetation_pct, land_use_secondary_vegetation_or_regrowth_pct = origin_enhancement(float(value.get('lat')), float(value.get('lon')))

    value['water_pct'] = water_pct
    value['land_use_anthropic_pct'] = land_use_anthropic_pct
    value['land_use_primary_vegetation_pct'] = land_use_primary_vegetation_pct
    value['land_use_secondary_vegetation_or_regrowth_pct'] = land_use_secondary_vegetation_or_regrowth_pct
    
    return value

def fraud_detection_process_sample(value: dict):
    """
    Performs fraud detection on a given sample and updates its validity and additional information.

    Args:
        value (dict): A dictionary representing the sample to be processed. For keys, see firestore or
          unit tests for more details.

    Returns:
        A dictionary representing the sample with updated validity and additional information.
    """
    if not('oxygen' in value and 'nitrogen' in value and 'carbon' in value):
        if not(isinstance(oxygen, Sequence) and isinstance(nitrogen, Sequence) and isinstance(carbon, Sequence)):
            if not(len(oxygen) >=2 and len(nitrogen) >=2 and len(carbon) >=2):
                print("Missing input data, skipping fraud detection. Sample must contain at least 2 oxygen, nitrogen and carbon measurements.")
                return value
            
    oxygen = value.get('oxygen')
    nitrogen = value.get('nitrogen')
    carbon = value.get('carbon')
    lat = float(value.get('lat'))
    lon = float(value.get('lon'))
    
    fraud_rate, p_value_oxygen, p_value_carbon, p_value_nitrogen = ttest(lat, lon,oxygen,nitrogen,carbon).evaluate()
    validity_details = {
        'p_value_oxygen': p_value_oxygen,
        'p_value_carbon': p_value_carbon,
        'p_value_nitrogen': p_value_nitrogen
    }
    value['validity'] = fraud_rate
    value['validity_details'] = validity_details
    return value
    
    