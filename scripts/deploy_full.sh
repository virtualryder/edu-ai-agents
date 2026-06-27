#!/usr/bin/env bash
# Unified, one-shot deploy: the REGIONAL application stack (in --region) followed by
# the global EDGE stack (CloudFront + WAFv2, which MUST be deployed in us-east-1 for
# its ACM viewer certificate). This is the single orchestration the second review
# asked for — "one procedure that deploys regional app + us-east-1 edge + origin
# lock-down + DNS + a tested authenticated endpoint" — instead of several manually
# coordinated stacks.
#
# Order matters: the edge distribution forwards to the regional app's public origin
# (your ALB / API Gateway / authorizer endpoint in front of the AgentCore runtime),
# so the regional stack (or that origin) must exist first. Pass its hostname as
# --origin-domain.
#
# Usage (native path):
#   scripts/deploy_full.sh \
#     --env prod --agent-id 01-concierge --region us-west-2 --mode native \
#     --template-bucket my-cfn-bucket --lambda-bucket my-lambda-bucket \
#     --idp-metadata https://idp/app/x/sso/saml/metadata \
#     --origin-domain app-alb-123.us-west-2.elb.amazonaws.com \
#     --acm-cert-arn arn:aws:acm:us-east-1:111122223333:certificate/abc \
#     --logging-bucket my-cloudfront-logs \
#     [--domain-name agents.example.edu --hosted-zone-id Z123 --waf-rate-limit 2000]
set -euo pipefail

ENVIRONMENT="dev"; AGENT_ID="01-concierge"; MODE="native"; REGION="${AWS_REGION:-us-east-1}"
TEMPLATE_BUCKET=""; LAMBDA_BUCKET=""; IDP_METADATA=""; IMAGE=""
ORIGIN_DOMAIN=""; ACM_CERT_ARN=""; LOGGING_BUCKET=""
DOMAIN_NAME=""; HOSTED_ZONE_ID=""; WAF_RATE_LIMIT="2000"
EDGE_REGION="us-east-1"   # CloudFront + its ACM cert are us-east-1 by AWS requirement

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) ENVIRONMENT="$2"; shift 2;;
    --agent-id) AGENT_ID="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --region) REGION="$2"; shift 2;;
    --template-bucket) TEMPLATE_BUCKET="$2"; shift 2;;
    --lambda-bucket) LAMBDA_BUCKET="$2"; shift 2;;
    --idp-metadata) IDP_METADATA="$2"; shift 2;;
    --image) IMAGE="$2"; shift 2;;
    --origin-domain) ORIGIN_DOMAIN="$2"; shift 2;;
    --acm-cert-arn) ACM_CERT_ARN="$2"; shift 2;;
    --logging-bucket) LOGGING_BUCKET="$2"; shift 2;;
    --domain-name) DOMAIN_NAME="$2"; shift 2;;
    --hosted-zone-id) HOSTED_ZONE_ID="$2"; shift 2;;
    --waf-rate-limit) WAF_RATE_LIMIT="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

req() { [[ -z "$2" ]] && { echo "ERROR: $1 is required" >&2; exit 2; } || true; }
req --template-bucket "$TEMPLATE_BUCKET"
req --idp-metadata "$IDP_METADATA"
req --origin-domain "$ORIGIN_DOMAIN"
req --acm-cert-arn "$ACM_CERT_ARN"
req --logging-bucket "$LOGGING_BUCKET"
case "$ACM_CERT_ARN" in
  arn:aws:acm:us-east-1:*) : ;;
  *) echo "ERROR: --acm-cert-arn must be a us-east-1 certificate (CloudFront requirement)" >&2; exit 2;;
esac

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EDGE_STACK="edu-${AGENT_ID}-edge"

echo "==> [1/2] REGIONAL app stack  (region=${REGION}, mode=${MODE})"
REGIONAL_ARGS=(--env "$ENVIRONMENT" --agent-id "$AGENT_ID" --mode "$MODE"
               --template-bucket "$TEMPLATE_BUCKET" --idp-metadata "$IDP_METADATA" --region "$REGION")
[[ -n "$LAMBDA_BUCKET" ]] && REGIONAL_ARGS+=(--lambda-bucket "$LAMBDA_BUCKET")
[[ -n "$IMAGE" ]] && REGIONAL_ARGS+=(--image "$IMAGE")
bash "$ROOT/scripts/deploy.sh" "${REGIONAL_ARGS[@]}"

echo "==> [2/2] EDGE stack  (CloudFront + WAFv2, region=${EDGE_REGION})"
aws cloudformation deploy \
  --region "$EDGE_REGION" \
  --stack-name "$EDGE_STACK" \
  --template-file "$ROOT/infra/cloudformation/edge.yaml" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    "Environment=${ENVIRONMENT}" \
    "OriginDomainName=${ORIGIN_DOMAIN}" \
    "AcmCertificateArn=${ACM_CERT_ARN}" \
    "LoggingBucketName=${LOGGING_BUCKET}" \
    "DomainName=${DOMAIN_NAME}" \
    "HostedZoneId=${HOSTED_ZONE_ID}" \
    "WafRateLimit=${WAF_RATE_LIMIT}"

CF_DOMAIN="$(aws cloudformation describe-stacks --region "$EDGE_REGION" --stack-name "$EDGE_STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='DistributionDomainName'].OutputValue" --output text 2>/dev/null || true)"

echo ""
echo "==> Unified deploy submitted."
echo "    Regional app stack : edu-${AGENT_ID}-${ENVIRONMENT}  (region ${REGION})"
echo "    Edge distribution  : ${CF_DOMAIN:-<pending — check the ${EDGE_STACK} stack outputs>}"
echo ""
echo "    Next (customer-owned hardening, see runbooks/agent-deploy/01-GOLDEN-PATH.md):"
echo "      1. Lock the origin (${ORIGIN_DOMAIN}) so it ONLY accepts traffic from this"
echo "         distribution (Origin-Verify header and/or the CloudFront managed prefix list)."
echo "      2. Point your Cognito app-client callback/logout URLs at https://${DOMAIN_NAME:-$CF_DOMAIN}."
echo "      3. Smoke-test the authenticated endpoint through CloudFront (a read, a denied"
echo "         over-reach, a consequential action blocked then approved)."
