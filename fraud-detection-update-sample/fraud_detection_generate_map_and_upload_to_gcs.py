import os
from google.cloud import pubsub_v1

# Get function environment variable for GCP project ID to use for accessing Earth Engine.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "river-sky-386919")

# Topic ID for GCS Pub/Sub topic. See fraud-detection-generate-maps/main.py for context.
TOPIC_ID = "fraud-detection-generate-maps-daily"

def fraud_detection_generate_map_and_upload_to_gcs(document_id):
    """
    Generates a land use map centered on a given latitude and longitude, and uploads it to Google Cloud Storage.
    This is done by publishing a message to a Pub/Sub topic, which triggers a Cloud Function that generates the map.

    Args:
        document_id (str): The ID of the document to be uploaded to GCS.

    Returns:
        None.
    """

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCP_PROJECT_ID, TOPIC_ID)

    data = document_id.encode("utf-8")
    future = publisher.publish(topic_path, data)
    
    print(f"Published messaged for id: {document_id} to {topic_path}. Result: {future.result()}")
