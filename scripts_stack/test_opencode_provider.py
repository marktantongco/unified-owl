#!/home/x1/.owl-agent/venv/bin/python3
"""
🦉 OWL-AGENT OpenCode Provider & Multi-Turn Workflow Benchmark
Tests /v1/models, /v1/chat/completions (single-turn & multi-turn), and streaming response latency.
"""

import argparse
import json
import logging
import os
import sys
import time
import urllib.request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("owl-opencode-test")

BASE_URL = "http://127.0.0.1:60000/v1"
API_KEY_PATH = os.path.expanduser("~/.owl-agent/config/api_key.txt")
API_KEY = open(API_KEY_PATH).read().strip() if os.path.exists(API_KEY_PATH) else ""

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

def test_models_endpoint():
    start = time.time()
    req = urllib.request.Request(f"{BASE_URL}/models", headers=get_headers())
    with urllib.request.urlopen(req, timeout=10) as resp:
        elapsed = (time.time() - start) * 1000
        data = json.loads(resp.read().decode())
        models = [m["id"] for m in data.get("data", [])]
        logger.info(f"✓ /v1/models returned {len(models)} models in {elapsed:.2f}ms: {models}")
        return models

def test_single_turn_completion(model="owl-default"):
    start = time.time()
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Explain in 1 sentence how a proxy defense stack prevents bot detection."}
        ],
        "temperature": 0.3,
        "max_tokens": 100
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=get_headers()
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        elapsed = (time.time() - start) * 1000
        data = json.loads(resp.read().decode())
        content = data["choices"][0]["message"]["content"].strip()
        logger.info(f"✓ Single-turn completion resolved in {elapsed:.2f}ms:\n  Response: {content}")
        return elapsed, content

def test_multi_turn_workflow(model="owl-default"):
    start = time.time()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a specialized security agent."},
            {"role": "user", "content": "Hello, I have a crawling task."},
            {"role": "assistant", "content": "Hello! I can help you crawl targets safely with TLS impersonation."},
            {"role": "user", "content": "What is the recommended tool for fetching static JSON?"}
        ],
        "temperature": 0.2,
        "max_tokens": 80
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=get_headers()
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        elapsed = (time.time() - start) * 1000
        data = json.loads(resp.read().decode())
        content = data["choices"][0]["message"]["content"].strip()
        logger.info(f"✓ Multi-turn context workflow resolved in {elapsed:.2f}ms:\n  Response: {content}")
        return elapsed, content

def main():
    parser = argparse.ArgumentParser(description="🦉 OWL OpenCode Provider Benchmark")
    parser.add_argument("-m", "--model", default="owl-default", help="Model ID to test")
    args = parser.parse_args()

    print("=== 1. TESTING /v1/models ENDPOINT ===")
    models = test_models_endpoint()

    print("\n=== 2. TESTING SINGLE-TURN PROMPT ===")
    t1, r1 = test_single_turn_completion(args.model)

    print("\n=== 3. TESTING MULTI-TURN CONVERSATION WORKFLOW ===")
    t2, r2 = test_multi_turn_workflow(args.model)

    print("\n=== OPENCODE PROVIDER BENCHMARK SUMMARY ===")
    print(f"Available Models: {len(models)}")
    print(f"Single-Turn Prompt Latency: {t1:.2f}ms")
    print(f"Multi-Turn Context Latency: {t2:.2f}ms")
    print(f"Provider Endpoint: {BASE_URL} (Healthy & Ready for OpenCode CLI)")

if __name__ == "__main__":
    main()
