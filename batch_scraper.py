#!/home/x1/.owl-agent/venv/bin/python3
"""
🦉 OWL-AGENT High-Throughput Batch Queue Scraper Utility
Supports direct CLI execution and library imports.
"""

import argparse
import asyncio
import json
import logging
import os
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional

# Add stack directories to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OWL_HOME = os.getenv("OWL_HOME", os.path.expanduser("~/.owl-agent"))
for p in [OWL_HOME, os.path.dirname(SCRIPT_DIR), "/home/x1/.owl-agent", "/home/x1/owl-agent-stack"]:
    if p not in sys.path and os.path.exists(p):
        sys.path.insert(0, p)

from proxy_defense import ResilientClient, CachedResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("owl-batch")


class BatchScraper:
    def __init__(
        self,
        concurrency: int = 5,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        skip_cache: bool = False,
        primary_proxy: Optional[str] = "http://127.0.0.1:8081",
        db_path: Optional[str] = None,
    ):
        self.concurrency = concurrency
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.skip_cache = skip_cache
        self.primary_proxy = primary_proxy
        self.db_path = db_path
        if self.db_path:
            self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scraped_data (
                    url TEXT PRIMARY KEY,
                    domain TEXT,
                    status INTEGER,
                    content_length INTEGER,
                    content TEXT,
                    latency_seconds REAL,
                    retries INTEGER,
                    timestamp REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_domain ON scraped_data(domain);")
            conn.commit()

    def _save_to_db(self, url: str, status: int, content: str, latency: float, retries: int):
        if not self.db_path:
            return
        try:
            import urllib.parse
            domain = urllib.parse.urlparse(url).netloc or "unknown"
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO scraped_data 
                    (url, domain, status, content_length, content, latency_seconds, retries, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (url, domain, status, len(content), content, latency, retries, time.time()))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to persist {url} to SQLite: {e}")

    async def _worker(self, worker_id: int, queue: asyncio.Queue, client: ResilientClient, results: Dict[str, Any]):
        while True:
            try:
                url = await asyncio.wait_for(queue.get(), timeout=1.0)
            except (asyncio.TimeoutError, asyncio.QueueEmpty):
                break

            attempts = 0
            last_error = None
            response_payload = None
            start_req = time.time()

            while attempts <= self.max_retries:
                attempts += 1
                try:
                    resp: CachedResponse = await client.request(
                        url=url,
                        method="GET",
                        skip_cache=self.skip_cache,
                        timeout=25
                    )
                    if 200 <= resp.status < 500:
                        content_str = resp.content.decode("utf-8", errors="replace")
                        req_time = time.time() - start_req
                        response_payload = {
                            "status": resp.status,
                            "content_length": len(resp.content),
                            "content": content_str,
                            "latency_seconds": round(req_time, 3),
                            "retries": attempts - 1,
                            "worker": worker_id,
                        }
                        self._save_to_db(url, resp.status, content_str, req_time, attempts - 1)
                        break
                    else:
                        last_error = f"HTTP {resp.status}"
                except Exception as e:
                    last_error = str(e)

                if attempts <= self.max_retries:
                    delay = (self.backoff_factor ** attempts) * 0.5
                    logger.debug(f"[Worker #{worker_id}] Retrying {url} in {delay:.2f}s (attempt {attempts}/{self.max_retries}): {last_error}")
                    await asyncio.sleep(delay)

            if response_payload:
                results[url] = response_payload
            else:
                req_time = time.time() - start_req
                results[url] = {
                    "status": 502,
                    "error": last_error,
                    "retries": attempts - 1,
                    "worker": worker_id,
                    "latency_seconds": round(req_time, 3)
                }

            queue.task_done()

    async def scrape(self, urls: List[str]) -> Dict[str, Any]:
        start = time.time()
        queue = asyncio.Queue()
        for u in urls:
            queue.put_nowait(u)

        results: Dict[str, Any] = {}
        async with ResilientClient(primary_proxy=self.primary_proxy) as client:
            stats = await client.get_stats()
            healthy_proxies = max(1, stats.get("proxies_healthy", self.concurrency))
            effective_concurrency = min(self.concurrency, healthy_proxies + 3)

            workers = [
                asyncio.create_task(self._worker(i, queue, client, results))
                for i in range(effective_concurrency)
            ]
            await queue.join()
            await asyncio.gather(*workers, return_exceptions=True)

        elapsed = time.time() - start
        return {
            "total_urls": len(urls),
            "successful": sum(1 for r in results.values() if r.get("status", 0) == 200),
            "failed": sum(1 for r in results.values() if r.get("status", 0) != 200),
            "elapsed_seconds": round(elapsed, 3),
            "concurrency_used": effective_concurrency,
            "results": results
        }


# ── Standalone Library Function ───────────────────────────────────────────────
def batch_scrape(
    urls: List[str],
    concurrency: int = 5,
    max_retries: int = 3,
    skip_cache: bool = False,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Synchronous entry point for library usage."""
    scraper = BatchScraper(
        concurrency=concurrency,
        max_retries=max_retries,
        skip_cache=skip_cache,
        db_path=db_path
    )
    return asyncio.run(scraper.scrape(urls))


# ── CLI Interface ─────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="🦉 OWL-AGENT High-Throughput Batch Scraper")
    parser.add_argument("urls", nargs="*", help="Target URLs to scrape")
    parser.add_argument("-f", "--file", help="File containing list of URLs (one per line)")
    parser.add_argument("-c", "--concurrency", type=int, default=5, help="Number of concurrent workers (default: 5)")
    parser.add_argument("-r", "--retries", type=int, default=3, help="Max retries with exponential backoff (default: 3)")
    parser.add_argument("-o", "--output", help="Output JSON path to write results")
    parser.add_argument("--db", help="SQLite database path to persist scraped records")
    parser.add_argument("--no-cache", action="store_true", help="Bypass persistent LRU cache for live egress")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    target_urls = list(args.urls)
    if args.file and os.path.exists(args.file):
        with open(args.file, "r") as f:
            target_urls.extend([line.strip() for line in f if line.strip() and not line.startswith("#")])

    if not target_urls:
        print("Error: No target URLs provided. Specify URLs as arguments or via -f/--file.", file=sys.stderr)
        sys.exit(1)

    logger.info(f"🚀 Starting batch scrape of {len(target_urls)} URLs (concurrency: {args.concurrency}, retries: {args.retries})...")

    summary = batch_scrape(
        urls=target_urls,
        concurrency=args.concurrency,
        max_retries=args.retries,
        skip_cache=args.no_cache,
        db_path=args.db
    )

    print(f"\n=== BATCH SCRAPE SUMMARY ===")
    print(f"Total: {summary['total_urls']} | Successful: {summary['successful']} | Failed: {summary['failed']} | Elapsed: {summary['elapsed_seconds']}s")
    for url, data in summary["results"].items():
        st = data.get("status", "ERR")
        sz = data.get("content_length", 0)
        rt = data.get("retries", 0)
        w = data.get("worker", -1)
        print(f"  [{st}] {url} -> {sz} bytes (Retries: {rt}, Worker #{w})")

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n✓ Saved JSON results to: {args.output}")

    if args.db:
        print(f"✓ Scraped records persisted to SQLite DB: {args.db}")


if __name__ == "__main__":
    main()
