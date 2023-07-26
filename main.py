from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore as firestoredata
# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from origin_validation import ttest

app = initialize_app()

@functions_framework.cloud_event
def hello_firestore(cloud_event: CloudEvent) -> None:
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
    
    value = affected_doc.get().to_dict()

    fraud_rate, p_value_oxygen, p_value_carbon, p_value_nitrogen = ttest(float(value.get('lat')),float(value.get('lon')),value.get('oxygen'),value.get('nitrogen'),value.get('carbon')).evaluate()
    value['validity'] = fraud_rate
    value['validity_details']['p_value_oxygen'] = p_value_oxygen
    value['validity_details']['p_value_carbon'] = p_value_carbon
    value['validity_details']['p_value_nitrogen'] = p_value_nitrogen
    # see https://github.com/googleapis/python-firestore/blob/main/google/cloud/firestore_v1/document.py
    affected_doc.set(value)
