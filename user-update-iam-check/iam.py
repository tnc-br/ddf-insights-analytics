import google.cloud.firestore
from firebase_admin import firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build




class UserIam():


  def __init__(self, firestore_payload):
    self.set_service()
    self.firestore_payload = firestore_payload

  def set_service(self):
    #Google ADMIN
    SCOPES = ["https://www.googleapis.com/auth/cloud-identity.groups", "https://www.googleapis.com/auth/admin.directory.user", "https://www.googleapis.com/auth/admin.directory.group"]          
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    service_account_credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES).with_subject("admin@timberid.org")
    self.service = build('admin', 'directory_v1', credentials=service_account_credentials)

  def grant_access_new_user(self):
    value = self.curr_value(self.firestore_payload)
    email = value.get('email')
    role = value.get('role')
    org_id = value.get('org')
    requests = []
    if role == "admin": #have access to the GCP project
      member= {
        "kind": "member",
        "email": email,
        "role": "MEMBER",
        "type": "USER"
      }
      add_request = self.service.members().insert(groupKey = 'earth-engine-developers@timberid.org', body = member)
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
      add_request = self.service.members().insert(groupKey = 'earth-engine-developers@timberid.org', body = member)
      requests.append(add_request)

    if org_id != '':
      org_email = ((client.collection('organizations').document(org_id)).get().to_dict()).get('org_email')
      add_request = this.service.members().insert(groupKey = org_email, body = member)
      requests.append(add_request)

    for request in requests:
      run_request(request)

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
    except ValueError:
        print(ValueError)


  def ungrant_access_deleted_user(self):
    value = self.old_value(['email', 'org', 'role'])
    email = value.get('email')
    role = value.get('role')
    org_id = value.get('org')
    requests = []
    if role == "admin" or role == "member": #have access to the GCP project
      add_request = self.service.members().delete(groupKey = 'earth-engine-developers@timberid.org', memberKey = email)
      requests.append(add_request)
    elif role == "site_admin": #manage the organization and have access to the GCP project
      add_request = self.service.members().delete(groupKey = 'gcp-organization-admins@timberid.org', memberKey = email)
      requests.append(add_request)

    if org_id != '':
      org_email = ((client.collection('organizations').document(org_id)).get().to_dict()).get('org_email')
      add_request = this.service.members().delete(groupKey = org_email, memberKey = email)
      requests.append(add_request)

    for request in requests:
      run_request(request)
