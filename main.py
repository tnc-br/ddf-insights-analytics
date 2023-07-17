from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore as firestoredata
# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
#from fraud import Fraud
#import nbformat
#from nbconvert.preprocessors import ExecutePreprocessor


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

    fraud_rate = 0.77 # Fraud().evaluate(value)
    value['validity'] = fraud_rate
    # see https://github.com/googleapis/python-firestore/blob/main/google/cloud/firestore_v1/document.py
    affected_doc.set(value)


    # filename = 'origin_validation.ipynb'
    # with open(filename) as ff:
    #     nb_in = nbformat.read(ff, nbformat.NO_CONVERT)
        
    # ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    
    # nb_out = ep.preprocess(nb_in)
