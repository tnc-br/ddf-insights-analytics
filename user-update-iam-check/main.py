from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore as firestoredata
from firebase_admin import initialize_app
from iam import UserIam


app = initialize_app()

@functions_framework.cloud_event
def grant_access(cloud_event: CloudEvent) -> None:
  
  """Triggers by a change to a Firestore document.
  Args:
      cloud_event: cloud event with information on the firestore event trigger
  """
  #FIRESTORE
  firestore_payload = firestoredata.DocumentEventData()
  firestore_payload._pb.ParseFromString(cloud_event.data)


  print(f"Function triggered by change to: {cloud_event['source']}")
  is_value = 'value' in firestore_payload
  is_old_value = 'old_value' in firestore_payload

  user_iam = UserIam(firestore_payload)

  if is_value and not is_old_value : #document created
    print("document created")
    user_iam.grant_access_new_user()


  elif is_value and is_old_value : #document modified
    print("document updated")
    user_iam.ungrant_access_new_user()
    user_iam.grant_access_deleted_user()


    
  elif not is_value and is_old_value : #document deleted
    print("document deleted")
    user_iam.ungrant_access_deleted_user()
