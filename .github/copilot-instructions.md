# TimberID Analytics - AI Copilot Instructions

Sistema de detecção de fraude em madeira usando análise isotópica, Google Earth Engine e MapBiomas. **Core**: Cloud Functions Python processando dados geoespaciais para validação de amostras.

## 🏗️ Architecture Overview

**Event-Driven Microservices**: 6 Cloud Functions organizadas por responsabilidade:

- **`fraud-detection-update-sample/`** ⭐ Core fraud detection pipeline (Firestore trigger)
- **`Firestore-Earth-Engine-ETL/`** ETL sync Firestore→Earth Engine (HTTP)
- **`fraud-detection-generate-maps/`** Interactive map generation (Pub/Sub)
- **`fraud-detection-new-isoscape/`** Isoscape update monitoring (HTTP)
- **`update-org-ee-auto-auth/`** Organization provisioning (Firestore trigger)
- **`user-update-iam-check/`** User permission management (Firestore trigger)

## 🔧 Development Patterns

### Cloud Functions Structure

```python
import functions_framework
from firebase_admin import initialize_app, firestore
from google.auth import compute_engine
import ee

app = initialize_app()

@functions_framework.cloud_event  # or @functions_framework.http
def main_handler(cloud_event):
    # Standard auth pattern
    credentials = compute_engine.Credentials(scopes=['https://www.googleapis.com/auth/earthengine'])
    ee.Initialize(credentials, project=GCP_PROJECT_ID)

    # Process with error handling per step
    try:
        step_result = process_step(data)
    except Exception as e:
        print(f'caught {type(e)} while processing: {e}')
        print(traceback.format_exc())
```

### Testing Strategy

- **Local Development**: Use extensive mocking system in `test_*.py` files
- **Integration Tests**: Files like `test_integration.py` validate real API contracts
- **Mock Pattern**: Each service has corresponding `mock_*.py` for offline development
- **Run Tests**: `python test_local.py` for isolated component testing

### Firestore Document Flow

**Critical**: Use `OUTPUT_FIELDS` pattern to prevent infinite update loops:

```python
OUTPUT_FIELDS = {"validity", "validity_details", "water_pct", "land_use_*", "alerts"}
# Check updateMask to avoid re-processing output-only updates
```

### Earth Engine Patterns

- Always use fixed asset paths: `projects/mapbiomas-public/assets/brazil/lulc/collection8/`
- Buffer calculations standard: 1km (point), 10km (regional context)
- Organization isolation: `projects/{project}/assets/ee_org/{org}/`

## 🛠️ Key Commands

```bash
# Local testing (no GCP auth needed)
python test_local.py

# Install core dependencies only
pip install earthengine-api firebase-admin google-cloud-firestore numpy scipy

# Deploy single function
gcloud functions deploy function-name --source . --entry-point main_handler
```

## 📊 Data Flow Understanding

**Main Pipeline**: Firestore untrusted_samples → isotopic analysis → land use calculation → map generation → MapBiomas alerts → results update

**Key Integration Points**:

- MapBiomas Collection 8.0 (2021) for land use data
- Custom isoscapes in Earth Engine for isotopic validation
- MapBiomas Alerta API for deforestation alerts
- Google Cloud Storage for generated map hosting

## 🚫 Critical Constraints

- **Never modify** existing `.md` files unless explicitly requested
- **Earth Engine quotas**: Batch operations when possible, respect rate limits
- **Firestore triggers**: Always check `updateMask` to prevent loops
- **Mock-first development**: Use local mocks before touching cloud resources

## 📁 Quick Navigation

- Core logic: `fraud-detection-update-sample/main.py` orchestrates 4-step fraud detection
- ETL pipeline: `Firestore-Earth-Engine-ETL/main.py` handles data synchronization
- Testing examples: `**/test_*.py` files show mock usage patterns
- Configuration: Each service has `requirements.txt` with pinned versions
