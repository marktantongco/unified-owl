#!/home/x1/.owl-agent/venv/bin/python3
"""
🦉 OWL-AGENT Specialized Domain & Schema Extraction Scraper
Extracts structured entity schemas (Metadata, Headings, Links, Articles, Tables) from web targets.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sqlite3
import sys
import time
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional
import urllib.parse

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
logger = logging.getLogger("owl-schema")

class SchemaExtractor(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.title = ""
        self.meta_tags: Dict[str, str] = {}
        self.headings: List[Dict[str, str]] = []
        self.links: List[Dict[str, str]] = []
        self.paragraphs: List[str] = []
        self._current_tag: Optional[str] = None
        self._current_data: List[str] = []
        self._in_title = False
        self._in_heading = False
        self._in_p = False

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        attrs_dict = dict(attrs)
        self._current_tag = tag

        if tag == "title":
            self._in_title = True
        elif tag in ["h1", "h2", "h3", "h4"]:
            self._in_heading = True
            self._current_heading_level = tag
        elif tag == "p":
            self._in_p = True
        elif tag == "meta":
            name = attrs_dict.get("name") or attrs_dict.get("property") or attrs_dict.get("http-equiv")
            content = attrs_dict.get("content")
            if name and content:
                self.meta_tags[name] = content
        elif tag == "a":
            href = attrs_dict.get("href")
            if href:
                full_url = urllib.parse.urljoin(self.base_url, href)
                self.links.append({
                    "href": full_url,
                    "rel": attrs_dict.get("rel", ""),
                    "text": ""
                })

    def handle_endtag(self, tag: str):
        data = "".join(self._current_data).strip()
        self._current_data = []

        if tag == "title":
            self.title = data
            self._in_title = False
        elif tag in ["h1", "h2", "h3", "h4"] and self._in_heading:
            if data:
                self.headings.append({"level": self._current_heading_level, "text": data})
            self._in_heading = False
        elif tag == "p" and self._in_p:
            if data:
                self.paragraphs.append(data)
            self._in_p = False
        elif tag == "a" and self.links and not self.links[-1]["text"]:
            self.links[-1]["text"] = data

    def handle_data(self, data: str):
        if self._in_title or self._in_heading or self._in_p or self._current_tag == "a":
            self._current_data.append(data)

    def get_schema(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "metadata": self.meta_tags,
            "headings_count": len(self.headings),
            "headings": self.headings[:15],
            "links_count": len(self.links),
            "links_sample": self.links[:10],
            "paragraphs_count": len(self.paragraphs),
            "summary_text": " ".join(self.paragraphs[:3])
        }

async def extract_schema_from_url(url: str, skip_cache: bool = False) -> Dict[str, Any]:
    start_time = time.time()
    async with ResilientClient() as client:
        resp: CachedResponse = await client.request(url=url, skip_cache=skip_cache)
        html_text = resp.content.decode("utf-8", errors="replace")
        
        parser = SchemaExtractor(base_url=url)
        try:
            parser.feed(html_text)
        except Exception as e:
            logger.warning(f"HTML parsing error on {url}: {e}")

        extracted = parser.get_schema()
        return {
            "url": url,
            "status": resp.status,
            "domain": urllib.parse.urlparse(url).netloc,
            "latency_seconds": round(time.time() - start_time, 4),
            "content_bytes": len(resp.content),
            "schema": extracted
        }

def main():
    parser = argparse.ArgumentParser(description="🦉 OWL Schema Extraction Scraper")
    parser.add_argument("url", nargs="?", default="https://example.com", help="Target URL to scrape & structure")
    parser.add_argument("-o", "--output", help="Output JSON path")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache for live egress")
    args = parser.parse_args()

    res = asyncio.run(extract_schema_from_url(args.url, skip_cache=args.no_cache))
    print(json.dumps(res, indent=2))

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(res, f, indent=2)
        print(f"\n✓ Saved structured schema to: {args.output}")

if __name__ == "__main__":
    main()
