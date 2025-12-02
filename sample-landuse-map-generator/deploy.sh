#!/bin/bash

# Deploy script for Sample Map Generator Cloud Function
# Triggers on Firestore document writes in untrusted_samples collection

set -e  # Exit on error

FUNCTION_NAME="sample-map-generator"
REGION="us-central1"
PROJECT_ID="river-sky-386919"

echo "🚀 Deploying $FUNCTION_NAME to $REGION..."

gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=generate_sample_map \
  --trigger-event-filters="type=google.cloud.firestore.document.v1.written" \
  --trigger-event-filters="database=(default)" \
  --trigger-location=$REGION \
  --trigger-event-filters-path-pattern="document=untrusted_samples/{documentId}" \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID" \
  --memory=2GB \
  --timeout=540s \
  --max-instances=10 \
  --min-instances=0

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Function details:"
echo "   Name: $FUNCTION_NAME"
echo "   Region: $REGION"
echo "   Trigger: Firestore document.written"
echo "   Collection: untrusted_samples"
echo ""
echo "🔍 View logs:"
echo "   gcloud functions logs read $FUNCTION_NAME --region=$REGION --limit=50"
echo ""
echo "🧪 Test the function by creating/updating a document in Firestore:"
echo "   Collection: untrusted_samples"
echo "   Required fields: { lat: -15.793889, lon: -47.882778 }"
