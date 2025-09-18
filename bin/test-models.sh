#!/bin/bash
set -euo pipefail

echo "Testing OpenAI Models with Web Access..."

# Export API key
export OPENAI_API_KEY="${OPENAI_API_KEY:-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}"

# Test gpt-5-mini (latest mini model with web access)
echo -e "\n1. Testing gpt-5-mini:"
curl -s -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5-mini",
    "messages": [
      {"role": "system", "content": "You have web access. Use it to get current information when needed."},
      {"role": "user", "content": "Write a Python hello world function"}
    ]
  }' | jq -r '.choices[0].message.content // .error.message'

# Test gpt-5-codex (requires org verification)
echo -e "\n2. Testing gpt-5-codex:"
curl -s -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5-codex",
    "messages": [
      {"role": "system", "content": "You are a coding assistant with web access."},
      {"role": "user", "content": "Write def hello_world():"}
    ]
  }' | jq -r '.choices[0].message.content // .error.message'

# Test claude-opus-4-1 (if Anthropic key is set)
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  echo -e "\n3. Testing claude-opus-4-1:"
  curl -s -X POST https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-4-1",
      "messages": [{"role": "user", "content": "Write a Python hello world"}],
      "max_tokens": 1024
    }' | jq -r '.content[0].text // .error.message'
else
  echo -e "\n3. Skipping claude-opus-4-1 (ANTHROPIC_API_KEY not set)"
fi

echo -e "\n✅ Model tests complete"