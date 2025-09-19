"""Utilities for repo metadata collection and PI redaction."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable

EMAIL_RE = re.compile(r"(?i)\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b")
JWT_RE = re.compile(r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")
CARD_RE = re.compile(r"\b\d{13,19}\b")
API_KEY_RE = re.compile(r"(?i)(sk|pk|api|key|token)[-_]?[a-z0-9]{8,}")

_REPLACERS = (
    (EMAIL_RE, "EMAIL"),
    (PHONE_RE, "PHONE"),
    (JWT_RE, "TOKEN"),
    (API_KEY_RE, "KEY"),
)


def _luhn_checksum(number: str) -> bool:
    digits = [int(d) for d in number]
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def _replace_match(text: str, pattern: re.Pattern[str], label: str, counter: Dict[str, int]) -> str:
    def _replacement(match: re.Match[str]) -> str:
        counter[label] = counter.get(label, 0) + 1
        return f"[{label}#{counter[label]}]"

    return pattern.sub(_replacement, text)


def redact_text(text: str) -> str:
    counter: Dict[str, int] = {}
    for pattern, label in _REPLACERS:
        text = _replace_match(text, pattern, label, counter)
    # Handle potential card numbers via Luhn
    def _card_replacement(match: re.Match[str]) -> str:
        number = match.group(0)
        if _luhn_checksum(number):
            counter.setdefault("PAN", 0)
            counter["PAN"] += 1
            return f"[PAN#{counter['PAN']}]"
        return number

    text = CARD_RE.sub(_card_replacement, text)
    return text


def redact_payload(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_payload(val) for key, val in value.items()}
    return value


def collect_repo_state(cwd: Path | None = None) -> Dict[str, Any]:
    cwd = cwd or Path.cwd()
    def _run(cmd: Iterable[str]) -> str:
        try:
            return subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except Exception:
            return "unknown"

    sha = _run(["git", "rev-parse", "--short", "HEAD"])
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    dirty_flag = "clean"
    try:
        subprocess.check_call(["git", "diff", "--quiet"], cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        dirty_flag = "dirty"

    return {
        "git_sha": sha,
        "git_branch": branch,
        "git_status": dirty_flag,
    }


def provider_metadata(provider: str, model: str, usage: Dict[str, Any] | None = None, cost_usd: float | None = None) -> Dict[str, Any]:
    meta = {
        "provider": provider,
        "model": model,
    }
    if usage:
        meta["input_tokens"] = usage.get("prompt_tokens")
        meta["output_tokens"] = usage.get("completion_tokens")
        meta["total_tokens"] = usage.get("total_tokens")
    if cost_usd is not None:
        meta["cost_usd"] = cost_usd
    return meta


__all__ = [
    "collect_repo_state",
    "provider_metadata",
    "redact_payload",
    "redact_text",
]
