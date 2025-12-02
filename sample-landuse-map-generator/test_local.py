"""
Test script for sample-map-generator Cloud Function
Tests the Firestore trigger locally without deploying
"""

import json
import base64
from main import generate_sample_map

def create_test_event(document_id="test_sample_123", collection="untrusted_samples"):
    """
    Creates a mock CloudEvent for testing Firestore triggers locally.
    
    Args:
        document_id: The document ID to test
        collection: The Firestore collection name
    
    Returns:
        A CloudEvent-like object for testing
    """
    
    # Simulate Firestore document path
    document_path = f"projects/river-sky-386919/databases/(default)/documents/{collection}/{document_id}"
    
    # Mock CloudEvent data structure
    firestore_data = {
        "oldValue": {},
        "updateMask": {},
        "value": {
            "name": document_path,
            "fields": {
                "lat": {"doubleValue": -15.793889},
                "lon": {"doubleValue": -47.882778}
            },
            "createTime": "2025-11-21T14:30:00.123456Z",
            "updateTime": "2025-11-21T14:30:00.123456Z"
        }
    }
    
    # Create mock CloudEvent
    class MockCloudEvent:
        def __init__(self, data):
            self.data = data
    
    # Serialize the Firestore data (Cloud Functions does this automatically)
    from google.events.cloud.firestore_v1 import DocumentEventData
    from google.protobuf.json_format import ParseDict
    
    event_data = DocumentEventData()
    ParseDict(firestore_data, event_data._pb)
    
    # Return mock event with serialized data
    return MockCloudEvent(event_data._pb.SerializeToString())


def test_map_generation():
    """
    Tests the map generation function locally.
    
    NOTE: This requires:
    1. Firebase credentials (serviceAccountKey.json)
    2. The test document to exist in Firestore with lat/lon
    3. Google Cloud authentication for Earth Engine
    """
    
    print("=" * 60)
    print("🧪 TESTING SAMPLE MAP GENERATOR")
    print("=" * 60)
    print()
    
    # Test document ID (must exist in Firestore with lat/lon)
    test_doc_id = "6ed0ffa36587c49f5b54"  # Change this to a real document ID
    
    print(f"📄 Test Document: {test_doc_id}")
    print(f"📁 Collection: untrusted_samples")
    print()
    
    # Create mock event
    cloud_event = create_test_event(test_doc_id)
    
    print("🔥 Calling generate_sample_map()...")
    print()
    
    try:
        # Call the Cloud Function
        generate_sample_map(cloud_event)
        
        print()
        print("=" * 60)
        print("✅ TEST PASSED - Function executed successfully")
        print("=" * 60)
        print()
        print("🔍 Check Firestore document for 'map_url' field")
        print("🗺️  Check GCS bucket: timberid-public-to-internet/timberid-maps/")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_map_generation()
