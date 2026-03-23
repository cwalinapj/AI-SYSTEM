#!/usr/bin/env bash
# Bootstrap MinIO buckets and folder structure for the agent system
set -euo pipefail

MC=${MC_ALIAS:-local}
BUCKET=${S3_BUCKET:-agent-memory}
ENDPOINT=${S3_ENDPOINT:-http://localhost:9000}
ACCESS_KEY=${S3_ACCESS_KEY:-minio}
SECRET_KEY=${S3_SECRET_KEY:-miniosecret}

echo "Waiting for MinIO to be ready..."
until mc alias set "${MC}" "${ENDPOINT}" "${ACCESS_KEY}" "${SECRET_KEY}"; do
  sleep 2
done

echo "Creating bucket: ${BUCKET}"
mc mb -p "${MC}/${BUCKET}" || true

# Create placeholder objects to establish folder hierarchy
for path in \
  "projects/.keep" \
  "experts/devops/playbooks/.keep" \
  "experts/luxonis/playbooks/.keep" \
  "experts/ml/playbooks/.keep"; do
  echo "" | mc pipe "${MC}/${BUCKET}/${path}" || true
done

echo "MinIO bootstrap complete."
