import json
from pathlib import Path

from cli.agents.metadata import redact_payload, redact_text

def test_redact_text_masks_pii():
    text = "Contact alice@example.com or call 555-123-4567. Card 4111111111111111"
    sanitized = redact_text(text)
    assert "alice@example.com" not in sanitized
    assert "555-123-4567" not in sanitized
    assert "4111111111111111" not in sanitized
    assert "[EMAIL#1]" in sanitized
    assert "[PHONE#1]" in sanitized
    assert "[PAN#1]" in sanitized


def test_redact_payload_recurses():
    data = {
        "user": "bob@example.com",
        "details": ["call 555-000-1111", {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.signature"}],
    }
    sanitized = redact_payload(data)
    serialized = json.dumps(sanitized)
    assert "example.com" not in serialized
    assert "555-000-1111" not in serialized
    assert "eyJhbGci" not in serialized
