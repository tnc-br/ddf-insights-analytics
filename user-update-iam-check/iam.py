import google.cloud.firestore
from firebase_admin import firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.auth

from google.cloud import storage


class UserIam():


  def __init__(self, firestore_payload):
    self.set_service()
    self.firestore_payload = firestore_payload

  def set_service(self):
    #Download service account file
    # Initialise a client
    storage_client = storage.Client()
    # Create a bucket object for our bucket
    bucket = storage_client.get_bucket("gadmin_credentials")
    # Create a blob object from the filepath
    blob = bucket.blob("credentials.json")
    # Download the file to a destination
    blob.download_to_filename('/tmp/credentials.json')
    #Google ADMIN
    SCOPES = ["https://www.googleapis.com/auth/cloud-identity.groups", "https://www.googleapis.com/auth/admin.directory.user", "https://www.googleapis.com/auth/admin.directory.group"]          
    SERVICE_ACCOUNT_FILE = '/tmp/credentials.json'
    service_account_credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES).with_subject("admin@timberid.org")
    self.service = build('admin', 'directory_v1', credentials=service_account_credentials)

  def grant_access_new_user(self):
    value = self.curr_value()
    email = value.get('email')
    role = value.get('role')
    org_id = value.get('org')
    requests = []
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")

    if role == "admin": #have access to the GCP project
      member= {
        "kind": "member",
        "email": email,
        "role": "MEMBER",
        "type": "USER"
      }
      grp_key = 'earth-engine-developers@timberid.org'
      if GCP_PROJECT_ID == 'river-sky-386919':
        grp_key = 'earth-engine-developers-test@timberid.org'

      add_request = self.service.members().insert(groupKey = grp_key, body = member)
      requests.append(add_request)
      member= {
        "kind": "admin",
        "email": email,
        "role": "OWNER",
        "type": "USER"
      }
    elif role == "site_admin": #manage the organization and have access to the GCP project
      member= {
        "kind": "member",
        "email": email,
        "role": "MEMBER",
        "type": "USER"
      }
      add_request = self.service.members().insert(groupKey = 'gcp-organization-admins@timberid.org', body = member)
      requests.append(add_request)
      member= {
        "kind": "admin",
        "email": email,
        "role": "OWNER",
        "type": "USER"
      }
    elif role == "member": #Only has access to earth engine assets
      member= {
        "kind": "member",
        "email": email,
        "role": "MEMBER",
        "type": "USER"
      }
      grp_key = 'earth-engine-developers@timberid.org'
      if GCP_PROJECT_ID == 'river-sky-386919':
        grp_key = 'earth-engine-developers-test@timberid.org'
      add_request = self.service.members().insert(groupKey = grp_key, body = member)
      requests.append(add_request)
      
    client: google.cloud.firestore.Client = firestore.client()

    if org_id != '':
      org_email = ((client.collection('organizations').document(org_id)).get().to_dict()).get('org_email')
      if (org_email != None) and (org_email != "") :
        org_email = org_email.lower()
        print("org email is ")
        print(org_email)
        add_request = self.service.members().insert(groupKey = org_email, body = member)
        requests.append(add_request)

    for request in requests:
      self.run_request(request)

  def curr_value(self):
    path_parts = self.firestore_payload.value.name.split("/")
    separator_idx = path_parts.index("documents")
    collection_path = path_parts[separator_idx + 1]
    document_path = "/".join(path_parts[(separator_idx + 2) :])

    print(f"Collection path: {collection_path}")
    print(f"Document path: {document_path}")
    client: google.cloud.firestore.Client = firestore.client()

    affected_doc = client.collection(collection_path).document(document_path)

    doc = affected_doc.get()
    value = affected_doc.get().to_dict()
    
    return value

  def old_value (self, fields):
    content = {}
    
    for field in fields:
      content [field] = self.firestore_payload.old_value.fields[field].string_value
    
    return content

  def run_request (self, request):
    try:
        response = request.execute()
        print(response)
    except Exception as e:
        print(e)


  def ungrant_access_deleted_user(self):
    value = self.old_value(['email', 'org', 'role'])
    email = value.get('email')
    role = value.get('role')
    org_id = value.get('org')
    requests = []
    client: google.cloud.firestore.Client = firestore.client()
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")

    if role == "admin" or role == "member": #have access to the GCP project
      grp_key = 'earth-engine-developers@timberid.org'
      if GCP_PROJECT_ID == 'river-sky-386919':
        grp_key = 'earth-engine-developers-test@timberid.org'
      add_request = self.service.members().delete(groupKey = grp_key, memberKey = email)
      requests.append(add_request)
    elif role == "site_admin": #manage the organization and have access to the GCP project
      add_request = self.service.members().delete(groupKey = 'gcp-organization-admins@timberid.org', memberKey = email)
      requests.append(add_request)

    if org_id != '':
      org_email = ((client.collection('organizations').document(org_id)).get().to_dict()).get('org_email')
      if (org_email != None) and (org_email != "") :
        org_email = org_email.lower()
        add_request = self.service.members().delete(groupKey = org_email, memberKey = email)
        print("org email is ")
        print(org_email)
        requests.append(add_request)

    for request in requests:
      self.run_request(request)
