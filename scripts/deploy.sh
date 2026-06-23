#!/usr/bin/env bash
# Stage the nested CloudFormation templates and deploy the master stack for one
# agent. Wraps DEPLOYMENT-HANDBOOK Step "Deploy CloudFormation".
#
# Usage (container path — recommended; build the image first):
#   IMAGE=$(scripts/build_and_push_image.sh --agent 01-student-family-concierge --region us-east-1 | sed -n 's/^ContainerImageUri=//p')
#   scripts/deploy.sh --env prod --agent-id 01-concierge --mode container \
#       --template-bucket my-cfn-bucket --idp-metadata https://idp/app/x/sso/saml/metadata \
#       --image "$IMAGE" --region us-east-1
#
# Usage (native path — package the Lambdas first):
#   scripts/package_lambdas.sh --agent 01-student-family-concierge --bucket my-lambda-bucket --agent-id 01-concierge
#   scripts/deploy.sh --env prod --agent-id 01-concierge --mode native \
#       --template-bucket my-cfn-bucket --lambda-bucket my-lambda-bucket \
#       --idp-metadata https://idp/app/x/sso/saml/metadata --region us-east-1
set -euo pipefail

ENVIRONMENT="dev"; AGENT_ID="01-concierge"; MODE="container"; REGION="${AWS_REGION:-us-east-1}"
TEMPLATE_BUCKET=""; LAMBDA_BUCKET=""; IDP_METADATA=""; IMAGE=""; STACK=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) ENVIRONMENT="$2"; shift 2;;
    --agent-id) AGENT_ID="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --template-bucket) TEMPLATE_BUCKET="$2"; shift 2;;
    --lambda-bucket) LAMBDA_BUCKET="$2"; shift 2;;
    --idp-metadata) IDP_METADATA="$2"; shift 2;;
    --image) IMAGE="$2"; shift 2;;
    --region) REGION="$2"; shift 2;;
    --stack) STACK="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done
[[ -z "$TEMPLATE_BUCKET" ]] && { echo "ERROR: --template-bucket is required" >&2; exit 2; }
[[ -z "$IDP_METADATA" ]] && { echo "ERROR: --idp-metadata is required" >&2; exit 2; }
[[ "$MODE" == "container" && -z "$IMAGE" ]] && { echo "ERROR: --image required for container mode" >&2; exit 2; }
[[ "$MODE" == "native" && -z "$LAMBDA_BUCKET" ]] && { echo "ERROR: --lambda-bucket required for native mode" >&2; exit 2; }
STACK="${STACK:-edu-${AGENT_ID}-${ENVIRONMENT}}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE_URL="https://${TEMPLATE_BUCKET}.s3.${REGION}.amazonaws.com/cfn"

echo "==> staging nested templates to s3://${TEMPLATE_BUCKET}/cfn/"
aws s3 cp "$ROOT/infra/cloudformation/" "s3://${TEMPLATE_BUCKET}/cfn/" \
  --recursive --exclude "*" --include "*.yaml" --region "$REGION"

echo "==> deploying stack ${STACK} (mode=${MODE})"
PARAMS=(
  "Environment=${ENVIRONMENT}"
  "AgentId=${AGENT_ID}"
  "DeployMode=${MODE}"
  "TemplateBaseUrl=${BASE_URL}"
  "IdpMetadataUrl=${IDP_METADATA}"
)
[[ "$MODE" == "native" ]] && PARAMS+=( "LambdaCodeBucket=${LAMBDA_BUCKET}" )
[[ "$MODE" == "container" ]] && PARAMS+=( "ContainerImageUri=${IMAGE}" )

aws cloudformation deploy \
  --region "$REGION" \
  --stack-name "$STACK" \
  --template-file "$ROOT/infra/cloudformation/quickstart.yaml" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides "${PARAMS[@]}"

echo "==> done. Stack outputs:"
aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs" --output table || true
