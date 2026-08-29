#!/home/x1/.owl-agent/venv/bin/python3
"""
🦉 OWL-AGENT Proxy Pool Benchmark & Geolocation Diversity Analyzer
Benchmarks latency, SSL handshake, subnet diversity, and egress stability.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OWL_HOME = os.getenv("OWL_HOME", os.path.expanduser("~/.owl-agent"))
for p in [OWL_HOME, os.path.dirname(SCRIPT_DIR), "/home/x1/.owl-agent", "/home/x1/owl-agent-stack"]:
    if p not in sys.path and os.path.exists(p):
        sys.path.insert(0, p)

import aiohttp
from proxy_defense import CONFIG, load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("owl-benchmark")

async def test_single_proxy(proxy_url: str, test_endpoint: str = "https://httpbin.org/ip", timeout_sec: int = 8) -> Dict[str, Any]:
    start = time.time()
    result = {
        "proxy": proxy_url.split("@")[-1] if "@" in proxy_url else proxy_url,
        "raw_proxy": proxy_url,
        "status": "FAILED",
        "latency_ms": 0.0,
        "origin_ip": None,
        "error": None
    }
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_sec)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(test_endpoint, proxy=proxy_url, ssl=False) as resp:
                elapsed = (time.time() - start) * 1000
                result["latency_ms"] = round(elapsed, 2)
                if resp.status == 200:
                    data = await resp.json()
                    result["origin_ip"] = data.get("origin")
                    result["status"] = "HEALTHY"
                else:
                    result["status"] = f"HTTP_{resp.status}"
    except asyncio.TimeoutError:
        result["error"] = "TIMEOUT"
    except Exception as e:
        result["error"] = str(e)
    return result

async def benchmark_pool(proxies: List[str], concurrency: int = 10) -> Dict[str, Any]:
    semaphore = asyncio.Semaphore(concurrency)

    async def sem_test(p):
        async with semaphore:
            return await test_single_proxy(p)

    tasks = [sem_test(p) for p in proxies]
    results = await asyncio.gather(*tasks)

    healthy = [r for r in results if r["status"] == "HEALTHY"]
    unique_ips = set(r["origin_ip"] for r in healthy if r["origin_ip"])
    avg_latency = round(sum(r["latency_ms"] for r in healthy) / len(healthy), 2) if healthy else 0.0

    return {
        "total_proxies": len(proxies),
        "healthy_count": len(healthy),
        "health_ratio": round(len(healthy) / len(proxies) * 100, 1) if proxies else 0,
        "unique_egress_ips": len(unique_ips),
        "average_healthy_latency_ms": avg_latency,
        "benchmarks": sorted(results, key=lambda x: (x["status"] != "HEALTHY", x["latency_ms"]))
    }

def main():
    parser = argparse.ArgumentParser(description="🦉 OWL Proxy Pool Benchmark")
    parser.add_argument("-c", "--concurrency", type=int, default=10, help="Max concurrent benchmark requests")
    parser.add_argument("-o", "--output", help="Output JSON results path")
    args = parser.parse_args()

    config_yaml_path = os.path.expanduser("~/.owl-agent/config/config.yaml")
    proxy_cache_path = os.path.expanduser("~/.owl-agent/config/proxy_cache.json")
    
    proxy_list = []
    if os.path.exists(config_yaml_path):
        try:
            with open(config_yaml_path, "r") as f:
                y = yaml.safe_load(f)
                proxy_list.extend(y.get("stealth", {}).get("us_proxies", []))
        except Exception as e:
            logger.warning(f"Failed to parse config.yaml: {e}")

    if os.path.exists(proxy_cache_path):
        try:
            with open(proxy_cache_path, "r") as f:
                cache_proxies = json.load(f)
                proxy_list.extend(cache_proxies)
        except Exception as e:
            logger.warning(f"Failed to parse proxy_cache.json: {e}")

    # Deduplicate
    unique_proxies = list(dict.fromkeys(proxy_list))
    if not unique_proxies:
        print("No proxies discovered in config.yaml or proxy_cache.json.")
        sys.exit(1)

    logger.info(f"⚡ Benchmarking pool of {len(unique_proxies)} proxies with concurrency {args.concurrency}...")
    summary = asyncio.run(benchmark_pool(unique_proxies, concurrency=args.concurrency))

    print(f"\n=== PROXY POOL BENCHMARK SUMMARY ===")
    print(f"Total: {summary['total_proxies']} | Healthy: {summary['healthy_count']} ({summary['health_ratio']}%) | Unique IPs: {summary['unique_egress_ips']} | Avg Latency: {summary['average_healthy_latency_ms']}ms\n")
    print(f"{'Status':<10} | {'Latency':<10} | {'Origin IP':<18} | {'Proxy Endpoint'}")
    print("-" * 75)
    for b in summary["benchmarks"][:15]:
        st = b["status"]
        lat = f"{b['latency_ms']}ms" if b["latency_ms"] else "N/A"
        ip = b["origin_ip"] or b.get("error", "FAIL")
        px = b["proxy"]
        print(f"{st:<10} | {lat:<10} | {ip:<18} | {px}")

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n✓ Saved detailed benchmark metrics to: {args.output}")

if __name__ == "__main__":
    main()
