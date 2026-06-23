#!/usr/bin/env bash
# Local smoke test of the AgentCore container contract WITHOUT docker or AWS:
# starts the agentcore_server for one agent and exercises GET /ping and
# POST /invocations against deterministic fixtures. Use this to prove an agent's
# runtime artifact behaves before building/pushing the image.
#
# Usage: scripts/local_smoke.sh 01-student-family-concierge
set -euo pipefail

AGENT="${1:-01-student-family-concierge}"
PORT="${PORT:-8080}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[[ -d "$ROOT/$AGENT" ]] || { echo "ERROR: agent folder '$AGENT' not found" >&2; exit 2; }

export EXTRACT_MODE="${EXTRACT_MODE:-demo}"
export CONNECTOR_MODE="${CONNECTOR_MODE:-fixture}"
export AGENT_DIR="$ROOT/$AGENT"
export PORT

echo "==> starting agentcore_server for ${AGENT} on :${PORT}"
python "$ROOT/aws-native-reference/_shared/agentcore_server.py" &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 3

echo "==> GET /ping"
python - "$PORT" <<'PY'
import json, sys, urllib.request
port = sys.argv[1]
print("   ", json.load(urllib.request.urlopen(f"http://localhost:{port}/ping")))
PY

echo "==> POST /invocations (benign authenticated read)"
python - "$PORT" <<'PY'
import json, sys, urllib.request
port = sys.argv[1]
payload = {"request_id":"SMOKE-1","channel":"web","intent":"STATUS","authenticated":True,
           "question":"application status?",
           "acting_user_claims":{"sub":"smoke-stu","custom:edu_role":"STUDENT"}}
req = urllib.request.Request(f"http://localhost:{port}/invocations",
                            data=json.dumps(payload).encode(),
                            headers={"Content-Type":"application/json"})
r = json.load(urllib.request.urlopen(req))
res = r.get("result", {})
print("    ok:", r.get("ok"), "| status:", res.get("case_status"),
      "| audit entries:", len(res.get("audit_trail", [])))
assert r.get("ok") and res.get("audit_trail"), "smoke test failed"
print("    SMOKE OK")
PY
