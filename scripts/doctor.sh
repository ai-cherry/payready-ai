#!/usr/bin/env bash
# Diagnose connectivity to key providers using secrets stored in keyring/env.
set -euo pipefail

py_key() {
  python3 - "$1" <<'PY'
import sys
try:
    import keyring
except ModuleNotFoundError:
    sys.exit(0)
value = keyring.get_password("payready", sys.argv[1])
if value:
    sys.stdout.write(value)
PY
}

fail() {
  echo "fail"; return 0
}

echo "OpenRouter:"
curl -fsS https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $(py_key OPENROUTER_API_KEY)" \
  -H "HTTP-Referer: ${OPENROUTER_REFERER:-https://payready.ai}" \
  -H "X-Title: ${OPENROUTER_TITLE:-PayReady AI CLI}" | jq '.data|length' || fail

echo "AIMLAPI:"
if [[ -n "${AIMLAPI_KEY:-}" ]]; then
  curl -fsS https://api.aimlapi.com/v1/models \
    -H "Authorization: Bearer $(py_key AIMLAPI_KEY)" | jq '.data|length' || echo "fail"
else
  echo "skipped (AIMLAPI_KEY not set)"
fi

echo "Together:"
curl -fsS https://api.together.ai/v1/models \
  -H "Authorization: Bearer $(py_key TOGETHER_API_KEY)" | jq '.data|length' || fail

echo "Anthropic:"
curl -fsS https://api.anthropic.com/v1/models \
  -H "x-api-key: $(py_key ANTHROPIC_API_KEY)" \
  -H "anthropic-version: 2023-06-01" | jq '.data|length' || fail
