#!/usr/bin/env bash
# Package an agent into the four native-path Lambda zips the CloudFormation
# native path expects, and (optionally) upload them to the LambdaCodeBucket.
#
# agent-service.yaml (DeployMode=native) reads:
#   s3://<LambdaCodeBucket>/<LambdaCodeKeyPrefix>/<AgentId>/{core,policy_gate,hitl_enqueue,finalize}.zip
# each with Handler `handler.lambda_handler`, runtime python3.12, arm64.
#
# Each zip contains: handler.py (the shared shim) + the agent's agent/ tools/ data/
# packages + edu_agent_platform/ (from platform_core) + governance/. The four zips
# are identical reference artifacts; specialize per Step Functions step as needed.
#
# Usage:
#   scripts/package_lambdas.sh --agent 01-student-family-concierge
#   scripts/package_lambdas.sh --agent 01-student-family-concierge \
#       --bucket my-lambda-bucket --prefix lambdas --agent-id 01-concierge --region us-east-1
#
# NOTE: LangGraph + LangChain are sizeable; for the native path prefer a container
# image Lambda or the AgentCore Runtime container if the unzipped size approaches
# the Lambda limit. The container path (build_and_push_image.sh) avoids this.
set -euo pipefail

AGENT=""; BUCKET=""; PREFIX="lambdas"; AGENT_ID=""; REGION="${AWS_REGION:-us-east-1}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2;;
    --bucket) BUCKET="$2"; shift 2;;
    --prefix) PREFIX="$2"; shift 2;;
    --agent-id) AGENT_ID="$2"; shift 2;;
    --region) REGION="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done
[[ -z "$AGENT" ]] && { echo "ERROR: --agent <agent-folder> is required" >&2; exit 2; }
AGENT_ID="${AGENT_ID:-$AGENT}"   # S3 key path; default to the folder name

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[[ -d "$ROOT/$AGENT" ]] || { echo "ERROR: agent folder '$AGENT' not found" >&2; exit 2; }

OUT="$ROOT/build/lambda/$AGENT_ID"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$OUT"

echo "==> assembling Lambda payload for ${AGENT}"
cp "$ROOT/aws-native-reference/_shared/lambda_handler.py" "$STAGE/handler.py"
cp -r "$ROOT/$AGENT/agent" "$STAGE/agent"
cp -r "$ROOT/$AGENT/tools" "$STAGE/tools"
[[ -d "$ROOT/$AGENT/data" ]] && cp -r "$ROOT/$AGENT/data" "$STAGE/data"
cp -r "$ROOT/platform_core/edu_agent_platform" "$STAGE/edu_agent_platform"
cp -r "$ROOT/governance" "$STAGE/governance"
# Drop tests/caches from the payload.
find "$STAGE" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true

BASE_ZIP="$STAGE/_base.zip"
( cd "$STAGE" && zip -qr "$BASE_ZIP" . -x "_base.zip" )

for fn in core policy_gate hitl_enqueue finalize; do
  cp "$BASE_ZIP" "$OUT/$fn.zip"
  echo "    built $OUT/$fn.zip"
done

echo "==> local artifacts in: $OUT"

if [[ -n "$BUCKET" ]]; then
  echo "==> uploading to s3://${BUCKET}/${PREFIX}/${AGENT_ID}/"
  for fn in core policy_gate hitl_enqueue finalize; do
    aws s3 cp "$OUT/$fn.zip" "s3://${BUCKET}/${PREFIX}/${AGENT_ID}/$fn.zip" --region "$REGION"
  done
  echo "LambdaCodeBucket=${BUCKET}  LambdaCodeKeyPrefix=${PREFIX}  AgentId=${AGENT_ID}"
fi
