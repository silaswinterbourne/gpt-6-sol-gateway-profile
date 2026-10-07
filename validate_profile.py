"""Validate the small GPT-6 Sol gateway profile without network access."""
from __future__ import annotations

import argparse
import pathlib
import sys
import re

try:
    import yaml
except ImportError as exc:  # pragma: no cover - only exercised without dependency
    raise SystemExit("PyYAML is required: python3 -m pip install -r requirements.txt") from exc

STATUSES = {"verified", "not_verified", "adapter_only"}
REQUIRED_GATEWAY_FIELDS = {"id", "name", "status", "model_id", "base_url", "endpoints", "docs", "capabilities", "rate_limits", "evidence", "notes"}


def _url(value: str | None, required: bool = True) -> None:
    if value is None:
        if required:
            raise ValueError("required URL is missing")
        return
    if not re.fullmatch(r"https://[^/\s]+(?:/.*)?", value):
        raise ValueError(f"URL must be absolute HTTPS: {value}")


def validate(path: pathlib.Path) -> dict:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot load profile: {exc}") from exc
    if not isinstance(document, dict) or document.get("schema") != 2:
        raise ValueError("profile schema must be 2")
    if str(document.get("checked")) != "2026-10-07":
        raise ValueError("checked must be an ISO date for this snapshot")
    model = document.get("model")
    if not isinstance(model, dict) or model.get("id") != "gpt-6-sol":
        raise ValueError("model.id must be gpt-6-sol")
    for key in ("context_tokens", "max_input_tokens", "max_output_tokens"):
        if not isinstance(model.get(key), int) or model[key] <= 0:
            raise ValueError(f"model.{key} must be a positive integer")
    efforts = model.get("reasoning_efforts")
    if not isinstance(efforts, list) or not efforts or model.get("default_reasoning_effort") not in efforts:
        raise ValueError("reasoning_efforts/default_reasoning_effort are inconsistent")
    prices = model.get("effective_price_usd_per_million_tokens")
    if not isinstance(prices, dict) or any(not isinstance(v, (int, float)) or v < 0 for v in prices.values()):
        raise ValueError("effective prices must be non-negative numbers")
    long_context = model.get("long_context")
    if not isinstance(long_context, dict) or long_context.get("threshold_tokens", 0) <= 0:
        raise ValueError("long_context threshold is required")
    gateways = document.get("gateways")
    if not isinstance(gateways, list) or not gateways:
        raise ValueError("gateways must be a non-empty list")
    ids = set()
    verified = []
    for gateway in gateways:
        if not isinstance(gateway, dict) or not REQUIRED_GATEWAY_FIELDS <= gateway.keys():
            raise ValueError("each gateway is missing a required field")
        if gateway["id"] in ids:
            raise ValueError(f"duplicate gateway id: {gateway['id']}")
        ids.add(gateway["id"])
        if gateway["status"] not in STATUSES:
            raise ValueError(f"unknown gateway status: {gateway['status']}")
        _url(gateway["docs"])
        _url(gateway.get("model_catalog"), required=False)
        _url(gateway.get("model_page"), required=False)
        _url(gateway.get("pricing_source"), required=False)
        if gateway["status"] == "verified":
            if gateway.get("model_id") != model["id"] or not gateway.get("base_url"):
                raise ValueError("verified gateway must identify the model and base URL")
            _url(gateway["base_url"])
            if not gateway.get("endpoints"):
                raise ValueError("verified gateway needs an endpoint")
            verified.append(gateway["id"])
        elif gateway.get("status") == "adapter_only" and gateway.get("base_url") is not None:
            raise ValueError("adapter-only gateway must leave base_url null")
    if verified != ["argolink"]:
        raise ValueError("this snapshot expects only ArgoLink to be verified")
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an offline GPT-6 Sol gateway profile")
    parser.add_argument("path", type=pathlib.Path)
    args = parser.parse_args()
    validate(args.path)
    print(f"valid: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
