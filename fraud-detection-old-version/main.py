from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore as firestoredata
# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from origin_validation import ttest
from origin_validation_enhancement import origin_enhancement
from upload_map_to_gcs import generate_map_and_upload_to_gcs
from fetch_mapbiomas_alerts import fetch_alerts
import collections.abc
import json

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
    print(cloud_event.data)
    print(firestore_payload.value)
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

    

    doc = affected_doc.get()

    if doc.exists:
      value = affected_doc.get().to_dict()

      if ('oxygen' in value) and ('nitrogen' in value) and ('carbon' in value) and ('lat' in value) and ('lon' in value):
        oxygen = value.get('oxygen')
        nitrogen = value.get('nitrogen')
        carbon = value.get('carbon')
        if isinstance(oxygen, collections.abc.Sequence) and isinstance(nitrogen, collections.abc.Sequence) and isinstance(carbon, collections.abc.Sequence):
          if len(oxygen) >=2 and len(nitrogen) >=2 and len(carbon) >=2 :
            fraud_rate, p_value_oxygen, p_value_carbon, p_value_nitrogen = ttest(float(value.get('lat')),float(value.get('lon')),oxygen,nitrogen,carbon).evaluate()
            validity_details = {
                'p_value_oxygen': p_value_oxygen,
                'p_value_carbon': p_value_carbon,
                'p_value_nitrogen': p_value_nitrogen
            }
            results_changed = False
            if( ('validity' in value) and (value['validity'] != fraud_rate)) or (('validity_details' in value) and (value['validity_details'] != validity_details)) : 
              results_changed = True
              value['validity'] = fraud_rate
              value['validity_details'] = validity_details

              if not 'alerts' in value:
                value['alerts'] = fetch_alerts(value['lat'], value['lon'])
                affected_doc.set(value)

            # see https://github.com/googleapis/python-firestore/blob/main/google/cloud/firestore_v1/document.py
            # affected_doc.set(value)
            if results_changed :
            
              # run origin_enhancement separately
              water_pct, land_use_anthropic_pct, land_use_primary_vegetation_pct, land_use_secondary_vegetation_or_regrowth_pct = origin_enhancement(float(value.get('lat')), float(value.get('lon')))

              value['water_pct'] = water_pct
              value['land_use_anthropic_pct'] = land_use_anthropic_pct
              value['land_use_primary_vegetation_pct'] = land_use_primary_vegetation_pct
              value['land_use_secondary_vegetation_or_regrowth_pct'] = land_use_secondary_vegetation_or_regrowth_pct

              affected_doc.set(value)

              generate_map_and_upload_to_gcs(float(value.get('lat')), float(value.get('lon')), document_path)
          else:
            print('isotopes must contain more than two measurements')
        else:
          print(f'1 or more invalid isotopes for oxygen: {oxygen}, carbon {carbon}, nitrogen {nitrogen}')
      else:
        print('origin verification can not be executed due to missing fields')

