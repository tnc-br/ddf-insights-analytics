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

**Data Pipeline**: `untrusted_samples` (Firestore) → isotopic validation (Earth Engine) → land use analysis (MapBiomas) → map generation (geemap) → alert checking (MapBiomas API) → results update (Firestore)

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

**Critical Mock Pattern**: Create comprehensive mocks for Earth Engine, Firebase, and geemap:

```python
# In mock_*.py files
def create_mock_ee():
    mock_image = Mock()
    mock_image.select.return_value.reduceRegion.return_value.getInfo.return_value = {'b1': 24.5}
    return mock_image

# Test without GCP dependencies
python test_local.py  # No authentication required
```

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

## � Python Setup Requirements

**Python Version**: 3.11+ (Cloud Functions compatible - Python 3.12 works perfectly)

### Installation Steps:

```bash
# 1. Install Python dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install python3.12-venv python3-pip  # Use system Python 3.12

# 2. Create virtual environment for the project
python3 -m venv timberid-env
source timberid-env/bin/activate  # Linux/Mac
# timberid-env\Scripts\activate  # Windows

# 3. Install core dependencies (choose one service to start)
cd fraud-detection-update-sample/
pip install -r requirements.txt

# 4. Verify installation
python -c "import ee, firebase_admin, numpy; print('Core dependencies OK')"
```

### Alternative Python Installation (pyenv recommended):

```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.0
pyenv local 3.11.0

# Continue with virtual environment steps above
```

### Critical Dependencies Per Service:

- **Core**: `earthengine-api`, `firebase-admin`, `google-cloud-firestore`
- **Geospatial**: `geemap`, `numpy`, `scipy` (for isotopic calculations)
- **Cloud Functions**: `functions-framework`, `google-events`, `cloudevents`
- **Testing**: All services include `mock_*.py` files for offline development

**⚠️ Important**: Each service directory has its own `requirements.txt` - install dependencies per service, not globally.

## 🛠️ Key Commands

```bash
# Local testing (no GCP auth needed)
python test_local.py

# Install dependencies for specific service
cd fraud-detection-update-sample/  # or other service directory
pip install -r requirements.txt

# Deploy single function (from function directory)
gcloud functions deploy function-name --source . --entry-point main_handler

# Deploy with environment variables
gcloud functions deploy --set-env-vars GCP_PROJECT_ID=your-project

# Validate Earth Engine authentication
python -c "import ee; ee.Initialize(); print('EE authenticated')"
```

## 📊 Data Flow Understanding

**4-Step Core Pipeline** (in `fraud-detection-update-sample/main.py`):

1. **Isotopic Analysis**: Compare sample O-18, C-13, N-15 against Earth Engine isoscapes
2. **Land Use Calculation**: Query MapBiomas within 1km/10km buffers for vegetation percentages
3. **Map Generation**: Create geemap visualization and upload to Google Cloud Storage
4. **Alert Detection**: Query MapBiomas Alerta API for nearby deforestation events

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

## 🐛 Error Handling Pattern

Always wrap each processing step in try-catch with specific error context:

```python
# STEP 1: calculate the validity of the sample
try:
    value = fraud_detection_process_sample(value)
except Exception as e:
    print(f'caught {type(e)} while calculating validity: {e}')
    print(traceback.format_exc())
```

## 📁 Quick Navigation

- Core logic: `fraud-detection-update-sample/main.py` orchestrates 4-step fraud detection
- ETL pipeline: `Firestore-Earth-Engine-ETL/main.py` handles data synchronization
- Testing examples: `**/test_*.py` files show mock usage patterns
- Configuration: Each service has `requirements.txt` with pinned versions
