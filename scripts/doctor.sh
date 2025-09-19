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

echo "Portkey:"
use_portkey=$(printf '%s' "${USE_PORTKEY:-}" | tr '[:upper:]' '[:lower:]')
if [[ "$use_portkey" =~ ^(1|true|yes)$ ]]; then
  curl -fsS https://api.portkey.ai/v1/models \
    -H "x-portkey-api-key: $(py_key PORTKEY_API_KEY)" \
    -H "x-portkey-virtual-key: ${PORTKEY_VK_OPENROUTER:-${PORTKEY_VIRTUAL_KEY:-}}" | jq '.data|length' || fail
else
  echo "skipped (USE_PORTKEY not set)"
fi

echo "Together:"
curl -fsS https://api.together.ai/v1/models \
  -H "Authorization: Bearer $(py_key TOGETHER_API_KEY)" | jq '.data|length' || fail

echo "Anthropic:"
curl -fsS https://api.anthropic.com/v1/models \
  -H "x-api-key: $(py_key ANTHROPIC_API_KEY)" \
  -H "anthropic-version: 2023-06-01" | jq '.data|length' || fail
