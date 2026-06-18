# EDU AI Agent Suite — developer entrypoints.
# Demo mode runs with NO API key and deterministic fixtures.

PY ?= python
PYTHONPATH := platform_core:.
export PYTHONPATH
export EXTRACT_MODE ?= demo
export CONNECTOR_MODE ?= fixture

.PHONY: help install test test-platform test-governance test-agents manifest demo serve clean

help:
	@echo "make install        - install platform_core (editable) + test deps"
	@echo "make test           - run the FULL suite (platform + governance + 8 agents)"
	@echo "make test-platform  - platform_core gateway/masker tests"
	@echo "make test-governance- grounding, redteam, fairness, HITL, manifest"
	@echo "make test-agents     - all 8 agent graph tests"
	@echo "make manifest       - regenerate the hash-pinned prompt manifest"
	@echo "make demo AGENT=01-student-family-concierge - run an agent's Streamlit demo"
	@echo "make serve AGENT=01-student-family-concierge - run the AgentCore container server locally"

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

demo:
	cd $(AGENT) && streamlit run app.py

serve:
	AGENT_DIR=$(PWD)/$(AGENT) $(PY) aws-native-reference/_shared/agentcore_server.py

clean:
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
