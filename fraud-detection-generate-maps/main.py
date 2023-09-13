import base64
import functions_framework
from firebase_admin import initialize_app, firestore
import google.cloud.firestore

app = initialize_app()

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    document_id = str(base64.b64decode(cloud_event.data["message"]["data"]))

    client: google.cloud.firestore.Client = firestore.client()
    collection_ref = client.collection("untrusted_samples")

    # Check if the document exists
    doc = collection_ref.document(document_id).get()
    if doc.exists:
        print('Document exists')
    else:
        print('Document does not exist')
        # Get all documents in the collection
        docs = collection_ref.stream()
        # Iterate over the documents and print their IDs and data
        for doc in docs:
            print(f'Document ID: {doc.id}')
