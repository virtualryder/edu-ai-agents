# EDU AI Agent Suite — developer entrypoints.
# Demo mode runs with NO API key and deterministic fixtures.

PY ?= python
PYTHONPATH := platform_core:.
export PYTHONPATH
export EXTRACT_MODE ?= demo
export CONNECTOR_MODE ?= fixture

.PHONY: help install test test-platform test-governance test-agents manifest demo serve clean \
        test-provisioner golden-path-01 eval-concierge

help:
	@echo "make install        - install platform_core (editable) + test deps"
	@echo "make test           - run the FULL suite (platform + governance + 8 agents)"
	@echo "make test-platform  - platform_core gateway/masker tests"
	@echo "make test-governance- grounding, redteam, fairness, HITL, manifest"
	@echo "make test-agents     - all 8 agent graph tests"
	@echo "make manifest       - regenerate the hash-pinned prompt manifest"
	@echo "make eval-concierge - scored quality benchmark for Agent 01 (College Scorecard connector)"
	@echo "make demo AGENT=01-student-family-concierge - run an agent's Streamlit demo"
	@echo "make serve AGENT=01-student-family-concierge - run the AgentCore container server locally"
	@echo "make test-provisioner - unit-test the AgentCore provisioner Lambda (no AWS)"
	@echo "make golden-path-01 LAMBDA_BUCKET=.. TEMPLATE_BUCKET=.. IDP_METADATA=.. - one-command deploy of Agent 01 (env=test pilot, native)"

install:
	$(PY) -m pip install -e platform_core
	$(PY) -m pip install pytest langgraph langchain-core streamlit

# Each agent ships an identically-named `agent`/`tools` package, so agent test
# suites must run in SEPARATE processes (one import root each). Platform and
# governance run together.
test:
	$(PY) -m pytest platform_core/tests governance/tests -q
	@for d in $(wildcard [0-9][0-9]-*); do \
		echo "== $$d =="; $(PY) -m pytest $$d/tests -q -p no:cacheprovider || exit 1; \
	done

test-platform:
	$(PY) -m pytest platform_core/tests -q

test-governance:
	$(PY) -m pytest governance/tests -q

test-agents:
	$(PY) -m pytest $(wildcard [0-9][0-9]-*/tests) -q

manifest:
	$(PY) -m governance.prompt_registry --update

# Scored output-quality benchmark for Agent 01 (Student & Family Concierge):
# runs the real College Scorecard connector mapping + query classifier against the
# labeled golden set and gates on thresholds (student-PII leak = 0 is a hard gate).
# Deterministic, no API key. Writes governance/evals/eval-report-concierge.md.
eval-concierge:
	$(PY) -m governance.evals.score_concierge
	$(PY) -m pytest governance/evals 01-student-family-concierge/tests/test_collegescorecard_connector.py -q -p no:cacheprovider

demo:
	cd $(AGENT) && streamlit run app.py

serve:
	AGENT_DIR=$(PWD)/$(AGENT) $(PY) aws-native-reference/_shared/agentcore_server.py

test-provisioner:
	$(PY) -m pytest infra/lambdas/agentcore_provisioner -q

# ---------------------------------------------------------------------------
# Golden path: one-command deploy of Agent 01 (Student & Family Concierge).
# Builds + uploads the agent-01 Lambda artifacts, then deploys the nested
# quickstart stack with sensible pilot parameters (native path). The pilot
# environment maps to the templates' test env (a valid non-prod value in every
# template's Environment AllowedValues [dev,test,stage,prod]); override with ENV.
#
# Required (no live AWS without these):
#   LAMBDA_BUCKET   - S3 bucket for packaged Lambda zips
#   TEMPLATE_BUCKET - S3 bucket for the nested CloudFormation templates
#   IDP_METADATA    - institution IdP SAML/OIDC metadata URL
# Optional: REGION (us-east-1), AGENT_ID (01-concierge), ENV (test)
# Thin wrapper over scripts/package_lambdas.sh + scripts/deploy.sh.
# Dry-run: make -n golden-path-01 LAMBDA_BUCKET=x TEMPLATE_BUCKET=x IDP_METADATA=x
# ---------------------------------------------------------------------------
GP01_AGENT      := 01-student-family-concierge
AGENT_ID        ?= 01-concierge
ENV             ?= test
REGION          ?= us-east-1
LAMBDA_BUCKET   ?=
TEMPLATE_BUCKET ?=
IDP_METADATA    ?=

golden-path-01:
	@test -n "$(LAMBDA_BUCKET)"   || { echo "ERROR: set LAMBDA_BUCKET=<s3-bucket-for-lambda-zips>"; exit 2; }
	@test -n "$(TEMPLATE_BUCKET)" || { echo "ERROR: set TEMPLATE_BUCKET=<s3-bucket-for-cfn-templates>"; exit 2; }
	@test -n "$(IDP_METADATA)"    || { echo "ERROR: set IDP_METADATA=<idp-saml/oidc-metadata-url>"; exit 2; }
	@echo "==> [1/2] packaging + uploading Agent 01 Lambda artifacts"
	bash scripts/package_lambdas.sh --agent $(GP01_AGENT) --bucket $(LAMBDA_BUCKET) --agent-id $(AGENT_ID) --region $(REGION)
	@echo "==> [2/2] deploying Agent 01 (env=$(ENV) pilot, native path)"
	bash scripts/deploy.sh --env $(ENV) --agent-id $(AGENT_ID) --mode native --template-bucket $(TEMPLATE_BUCKET) --lambda-bucket $(LAMBDA_BUCKET) --idp-metadata $(IDP_METADATA) --region $(REGION)
	@echo "==> Agent 01 deploy submitted. Wire the AgentCore provisioner next: runbooks/agent-deploy/01-GOLDEN-PATH.md (step 7)"

deploy-all-01:
	@test -n "$(TEMPLATE_BUCKET)" || { echo "ERROR: set TEMPLATE_BUCKET=<s3-bucket-for-cfn-templates>"; exit 2; }
	@test -n "$(IDP_METADATA)"    || { echo "ERROR: set IDP_METADATA=<idp-saml/oidc-metadata-url>"; exit 2; }
	@test -n "$(ORIGIN_DOMAIN)"   || { echo "ERROR: set ORIGIN_DOMAIN=<regional app public origin host>"; exit 2; }
	@test -n "$(ACM_CERT_ARN)"    || { echo "ERROR: set ACM_CERT_ARN=<us-east-1 ACM cert arn>"; exit 2; }
	@test -n "$(LOGGING_BUCKET)"  || { echo "ERROR: set LOGGING_BUCKET=<cloudfront access-log bucket>"; exit 2; }
	@echo "==> unified regional + edge (us-east-1) deploy for Agent 01"
	bash scripts/deploy_full.sh --env $(ENV) --agent-id $(AGENT_ID) --region $(REGION) --mode native \
	  --template-bucket $(TEMPLATE_BUCKET) --lambda-bucket $(LAMBDA_BUCKET) --idp-metadata $(IDP_METADATA) \
	  --origin-domain $(ORIGIN_DOMAIN) --acm-cert-arn $(ACM_CERT_ARN) --logging-bucket $(LOGGING_BUCKET)

clean:
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
