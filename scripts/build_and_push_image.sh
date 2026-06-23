#!/usr/bin/env bash
# Build the ARM64 AgentCore Runtime container for one agent and push it to ECR.
# The image implements the AgentCore container contract (/invocations + /ping,
# port 8080) and is what `ContainerImageUri` (agent-service.yaml, container path)
# and demo-in-a-box.yaml consume.
#
# Usage:
#   scripts/build_and_push_image.sh --agent 01-student-family-concierge --region us-east-1
#   scripts/build_and_push_image.sh --agent 04-assessment-grading-feedback --region us-east-1 --repo edu-agents
#
# Requires: docker (with buildx for arm64), AWS CLI v2, ECR permissions.
set -euo pipefail

AGENT=""; REGION="${AWS_REGION:-us-east-1}"; REPO="edu-agents"; TAG="latest"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2;;
    --region) REGION="$2"; shift 2;;
    --repo) REPO="$2"; shift 2;;
    --tag) TAG="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done
[[ -z "$AGENT" ]] && { echo "ERROR: --agent <agent-folder> is required" >&2; exit 2; }

ROOT="$(cd "$(dirname "$0")/.." && pwd)"   # repo root = build context
[[ -d "$ROOT/$AGENT" ]] || { echo "ERROR: agent folder '$AGENT' not found in repo root" >&2; exit 2; }

ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"
IMAGE="${REGISTRY}/${REPO}:${AGENT}-${TAG}"
DOCKERFILE="$ROOT/aws-native-reference/_shared/Dockerfile.agentcore"

echo "==> account=${ACCOUNT} region=${REGION}"
echo "==> ensuring ECR repo '${REPO}' exists"
aws ecr describe-repositories --repository-names "$REPO" --region "$REGION" >/dev/null 2>&1 \
  || aws ecr create-repository --repository-name "$REPO" --region "$REGION" \
       --image-scanning-configuration scanOnPush=true \
       --encryption-configuration encryptionType=KMS >/dev/null

echo "==> ECR login"
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REGISTRY"

echo "==> building ARM64 image for ${AGENT}"
# buildx for cross-arch; falls back to plain build if the host is already arm64.
if docker buildx version >/dev/null 2>&1; then
  docker buildx build --platform linux/arm64 \
    --build-arg AGENT="$AGENT" \
    -f "$DOCKERFILE" -t "$IMAGE" --push "$ROOT"
  echo "==> pushed (buildx): ${IMAGE}"
else
  docker build --build-arg AGENT="$AGENT" -f "$DOCKERFILE" -t "$IMAGE" "$ROOT"
  docker push "$IMAGE"
  echo "==> pushed: ${IMAGE}"
fi

echo ""
echo "ContainerImageUri=${IMAGE}"
echo "# Pass this as the ContainerImageUri parameter (DeployMode=container) or to demo-in-a-box.yaml."
