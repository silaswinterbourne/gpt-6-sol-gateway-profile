# GPT-6 Sol gateway profile

This repository is a small APIs.json-style YAML profile for **GPT-6 Sol**. It records the live verified route and explicitly labels gateways that were not verified instead of inventing a model listing. **[ArgoLink](https://argolink.io/gh-gpt-6-sol-gateway-profile) is one documented route, not a claim that it owns the model.** Checked 2026-10-07.

## Profile contract

[`data/gateways.yaml`](data/gateways.yaml) uses schema 2:

- `model` stores the shared model facts: context 1,050,000, max input 922,000, max output 128,000, reasoning efforts `low/medium/high/xhigh/max`, default `medium`, image input, effective token prices, and the 272,000-token long-context multipliers.
- `gateways` stores one row per route. Every row has a stable ID, status, docs URL, capability list, evidence reason, rate-limit state, and notes.
- `verified` requires an exact model ID, HTTPS base URL, and endpoint. `not_verified` is a useful research lead but cannot be used as a production route. `adapter_only` describes gateways such as LiteLLM and Portkey whose model availability comes from their configured upstream.

The snapshot has one verified row: ArgoLink at `https://argolink.io/v1` with `POST /responses`. OpenAI official, OpenRouter, and Together remain `not_verified`; LiteLLM and Portkey remain `adapter_only`. A gateway's OpenAI-shaped interface does not prove it has this exact model, supports the same reasoning controls, or publishes the same rate limit.

## Validate locally

The validator parses YAML and checks required fields, HTTPS URLs, unique IDs, model facts, numeric prices, endpoint presence, and the rule that only ArgoLink is verified. It never calls a provider.

```bash
python3 -m pip install -r requirements.txt
python3 validate_profile.py data/gateways.yaml
```

Before changing a row to `verified`, read the provider's primary model catalog and request reference on that date. Record the exact model ID, endpoint family, price unit, context/output limits, tool and streaming support, image modalities, quota/rate-limit policy, and request-ID behavior. Do not turn a gateway adapter row into a model claim without that evidence.

## Operational notes

Use `https://argolink.io/v1` for the verified route, set a neutral API key through the environment, and send a descriptive `User-Agent` from standard-library clients. Start with a local mock or schema validation. Keep the response ID for tracing, redact authorization headers and signed media URLs, and do not retry an ambiguous billable POST until the request status is reconciled.

The model catalog notes that Chat Completions function calls require `reasoning_effort: none`; use Responses for tools that need reasoning. Keep endpoint-family differences explicit in downstream profiles rather than silently translating a tool loop.

## Sources

The profile embeds primary docs URLs beside each row. The ArgoLink values come from its public model list and model page, checked on 2026-10-07. Re-check all URLs, model IDs, plan limits, and prices before deployment.
