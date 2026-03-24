"""
APIM Token Metrics Test Client — Responses API Edition
Tests llm-emit-token-metric policy with the Responses API (not Chat Completions),
using GPT-5.4 mini with reasoning_effort=low, in both streaming and non-streaming modes.

Usage:
  python test_token_metrics.py --gateway-url <URL> --api-key <KEY>
  python test_token_metrics.py --gateway-url <URL> --api-key <KEY> --streaming
  python test_token_metrics.py --gateway-url <URL> --api-key <KEY> --all
"""

import argparse
import json
import sys
from datetime import datetime, timezone

import requests
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL = "gpt-5.4-mini"
REASONING_EFFORT = "low"

TEST_INPUTS = [
    "What is Azure API Management in one sentence?",
    "Explain token-based billing for LLM APIs in two sentences.",
    "List 3 benefits of using APIM as an AI gateway.",
]

CUSTOM_HEADERS = {
    "x-tenant-id": "tenant-alpha",
    "x-user-id": "test-user-alpha",
    "x-cost-center": "engineering",
    "x-environment": "testbed",
}


def _make_client(gateway_url: str, api_key: str) -> OpenAI:
    """Create an OpenAI client pointing at APIM gateway for the Responses API."""
    return OpenAI(
        base_url=f"{gateway_url.rstrip('/')}/openai/v1/",
        api_key=api_key,
        default_headers={"api-key": api_key},
    )


def test_non_streaming_http(gateway_url: str, api_key: str):
    """Test non-streaming Responses API call via raw HTTP."""
    print("\n" + "=" * 60)
    print("TEST 1: Non-Streaming HTTP Request (Responses API)")
    print("=" * 60)

    url = f"{gateway_url.rstrip('/')}/openai/v1/responses"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
        **CUSTOM_HEADERS,
    }
    payload = {
        "model": MODEL,
        "input": TEST_INPUTS[0],
        "reasoning": {"effort": REASONING_EFFORT},
        "max_output_tokens": 100,
        "stream": False,
    }

    print(f"POST {url}")
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        usage = data.get("usage", {})
        print(f"Input tokens:      {usage.get('input_tokens', 'N/A')}")
        print(f"Output tokens:     {usage.get('output_tokens', 'N/A')}")
        print(f"Total tokens:      {usage.get('total_tokens', 'N/A')}")
        reasoning_tokens = usage.get("output_tokens_details", {}).get("reasoning_tokens", 0)
        print(f"Reasoning tokens:  {reasoning_tokens}")
        print(f"Response: {data.get('output_text', '')[:120]}...")
        return True
    else:
        print(f"ERROR: {resp.text[:300]}")
        return False


def test_streaming_http(gateway_url: str, api_key: str):
    """Test streaming Responses API via raw HTTP (SSE) — the key billing scenario."""
    print("\n" + "=" * 60)
    print("TEST 2: Streaming HTTP Request (Responses API SSE)")
    print("=" * 60)

    url = f"{gateway_url.rstrip('/')}/openai/v1/responses"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
        **CUSTOM_HEADERS,
    }
    payload = {
        "model": MODEL,
        "input": TEST_INPUTS[1],
        "reasoning": {"effort": REASONING_EFFORT},
        "max_output_tokens": 200,
        "stream": True,
    }

    print(f"POST {url} (stream=true)")
    resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
    print(f"Status: {resp.status_code}")

    if resp.status_code == 200:
        event_count = 0
        full_content = ""
        for line in resp.iter_lines():
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                raw = decoded[6:]
                if raw == "[DONE]":
                    break
                event = json.loads(raw)
                event_type = event.get("type", "")
                if event_type == "response.output_text.delta":
                    full_content += event.get("delta", "")
                    event_count += 1
                elif event_type == "response.completed":
                    usage = event.get("response", {}).get("usage", {})
                    print(f"Final usage — Input: {usage.get('input_tokens')}, "
                          f"Output: {usage.get('output_tokens')}, "
                          f"Total: {usage.get('total_tokens')}")
        print(f"Streamed text deltas: {event_count}")
        print(f"Response: {full_content[:120]}...")
        print("NOTE: Token metrics are ESTIMATED during streaming by the policy.")
        return True
    else:
        print(f"ERROR: {resp.text[:300]}")
        return False


def test_sdk_non_streaming(gateway_url: str, api_key: str):
    """Test non-streaming via OpenAI Python SDK Responses API."""
    print("\n" + "=" * 60)
    print("TEST 3: Non-Streaming via SDK (Responses API)")
    print("=" * 60)

    client = _make_client(gateway_url, api_key)
    response = client.responses.create(
        model=MODEL,
        input=TEST_INPUTS[2],
        reasoning={"effort": REASONING_EFFORT},
        max_output_tokens=200,
        extra_headers=CUSTOM_HEADERS,
    )

    print(f"Input tokens:      {response.usage.input_tokens}")
    print(f"Output tokens:     {response.usage.output_tokens}")
    print(f"Total tokens:      {response.usage.total_tokens}")
    print(f"Response: {response.output_text[:120]}...")
    return True


def test_sdk_streaming(gateway_url: str, api_key: str):
    """Test streaming via OpenAI Python SDK Responses API — the critical billing scenario."""
    print("\n" + "=" * 60)
    print("TEST 4: Streaming via SDK (Responses API)")
    print("=" * 60)

    client = _make_client(gateway_url, api_key)
    stream = client.responses.create(
        model=MODEL,
        input="Describe APIM token metrics in 3 bullet points.",
        reasoning={"effort": REASONING_EFFORT},
        max_output_tokens=300,
        stream=True,
        extra_headers=CUSTOM_HEADERS,
    )

    event_count = 0
    full_content = ""
    for event in stream:
        if event.type == "response.output_text.delta":
            full_content += event.delta
            event_count += 1
        elif event.type == "response.completed":
            usage = event.response.usage
            print(f"Final usage — Input: {usage.input_tokens}, "
                  f"Output: {usage.output_tokens}, "
                  f"Total: {usage.total_tokens}")

    print(f"Streamed text deltas: {event_count}")
    print(f"Response: {full_content[:120]}...")
    print("NOTE: Token metrics are ESTIMATED during streaming by the policy.")
    return True


def test_multi_tenant_load(gateway_url: str, api_keys: dict[str, str]):
    """Send calls under different subscription keys to test per-tenant metrics segregation."""
    print("\n" + "=" * 60)
    print("TEST 5: Multi-Tenant Load (different subscription keys)")
    print("=" * 60)

    for tenant_name, key in api_keys.items():
        headers_for_tenant = {
            **CUSTOM_HEADERS,
            "x-user-id": f"user-{tenant_name}",
            "x-cost-center": tenant_name,
        }
        client = _make_client(gateway_url, key)
        response = client.responses.create(
            model=MODEL,
            input=f"Hello from {tenant_name}. What is 2+2?",
            reasoning={"effort": REASONING_EFFORT},
            max_output_tokens=50,
            extra_headers=headers_for_tenant,
        )
        total = response.usage.total_tokens
        print(f"  {tenant_name}: {total} total tokens")

    print("\nAll tenants responded. Check App Insights to verify metrics are segregated by Subscription ID dimension.")
    return True


def main():
    parser = argparse.ArgumentParser(description="APIM Token Metrics Test Client (Responses API)")
    parser.add_argument("--gateway-url", required=True, help="APIM gateway URL (e.g., https://apim-xxx.azure-api.net)")
    parser.add_argument("--api-key", required=True, help="APIM subscription key")
    parser.add_argument("--streaming", action="store_true", help="Run streaming tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--multi-tenant-keys", type=str, default=None,
                        help="JSON dict of tenant_name:api_key for multi-tenant test")
    args = parser.parse_args()

    print("APIM Token Metrics Test Client — Responses API")
    print(f"Model:   {MODEL} (reasoning_effort={REASONING_EFFORT})")
    print(f"Gateway: {args.gateway_url}")
    print(f"Time:    {datetime.now(timezone.utc).isoformat()}")

    passed = 0
    failed = 0

    if args.streaming:
        tests = [
            ("Streaming HTTP", lambda: test_streaming_http(args.gateway_url, args.api_key)),
            ("Streaming SDK", lambda: test_sdk_streaming(args.gateway_url, args.api_key)),
        ]
    elif args.all:
        tests = [
            ("Non-Streaming HTTP", lambda: test_non_streaming_http(args.gateway_url, args.api_key)),
            ("Streaming HTTP", lambda: test_streaming_http(args.gateway_url, args.api_key)),
            ("Non-Streaming SDK", lambda: test_sdk_non_streaming(args.gateway_url, args.api_key)),
            ("Streaming SDK", lambda: test_sdk_streaming(args.gateway_url, args.api_key)),
        ]
    else:
        tests = [
            ("Non-Streaming HTTP", lambda: test_non_streaming_http(args.gateway_url, args.api_key)),
            ("Non-Streaming SDK", lambda: test_sdk_non_streaming(args.gateway_url, args.api_key)),
        ]

    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\nFAILED: {name} - {e}")
            failed += 1

    # Multi-tenant test if keys provided
    if args.multi_tenant_keys:
        try:
            keys = json.loads(args.multi_tenant_keys)
            if test_multi_tenant_load(args.gateway_url, keys):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\nFAILED: Multi-Tenant - {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    print("\nMetrics take ~3-5 minutes to appear in Application Insights.")
    print("Run 'python validate_metrics.py' after waiting to verify metrics landed.")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
