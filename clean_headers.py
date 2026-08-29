"""🦉 mitmproxy Sanitisation Script for OWL-AGENT v5.4.0"""
import random
from mitmproxy import http

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]
SENSITIVE_HEADERS = ["X-Forwarded-For", "X-Real-IP", "Via", "Forwarded", "X-Proxy-Location"]

def request(flow: http.HTTPFlow) -> None:
    flow.request.headers["User-Agent"] = random.choice(USER_AGENTS)
    for h in SENSITIVE_HEADERS:
        flow.request.headers.pop(h, None)
    flow.request.headers.pop("Proxy-Connection", None)

def response(flow: http.HTTPFlow) -> None:
    for h in SENSITIVE_HEADERS:
        flow.response.headers.pop(h, None)
