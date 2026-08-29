#!/usr/bin/env python3
"""
🦉 OWL-AGENT Challenge Solver & Bot Detection Handler
Detects and automates resolution of Cloudflare Turnstile, hCaptcha, and challenge checkboxes.
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("owl-challenge-solver")

class ChallengeSolver:
    def __init__(self, browser_cmd: str = "browser-stealth"):
        self.browser_cmd = browser_cmd

    def _run_cli(self, args: list) -> str:
        cmd = [self.browser_cmd] + args
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return res.stdout.strip()

    def navigate(self, url: str) -> bool:
        logger.info(f"Navigating to {url}...")
        out = self._run_cli(["open", url])
        time.sleep(2)
        return "✓" in out or "http" in out

    def detect_challenges(self) -> Dict[str, Any]:
        """Inspects live DOM for Turnstile, hCaptcha, reCAPTCHA, and Cloudflare indicators."""
        check_js = """
        (() => {
            const hasCloudflare = document.title.includes("Just a moment") || 
                                  document.body.innerText.includes("Verifying you are human") ||
                                  document.body.innerText.includes("Cloudflare");
            const turnstileIframe = document.querySelector('iframe[src*="challenges.cloudflare.com"], iframe[src*="turnstile"]');
            const hcaptchaIframe = document.querySelector('iframe[src*="hcaptcha.com"]');
            const recaptchaIframe = document.querySelector('iframe[src*="google.com/recaptcha"]');
            const genericCheckbox = document.querySelector('input[type="checkbox"][id*="challenge"], input[type="checkbox"][name*="cf-turnstile"]');
            
            return JSON.stringify({
                is_challenge_page: hasCloudflare || Boolean(turnstileIframe || hcaptchaIframe || recaptchaIframe),
                turnstile: Boolean(turnstileIframe),
                hcaptcha: Boolean(hcaptchaIframe),
                recaptcha: Boolean(recaptchaIframe),
                generic_checkbox: Boolean(genericCheckbox),
                title: document.title
            });
        })()
        """
        raw = self._run_cli(["eval", check_js])
        try:
            # Strip potential extra output lines
            clean_json = raw.strip()
            if clean_json.startswith('"') and clean_json.endswith('"'):
                clean_json = json.loads(clean_json)
            return json.loads(clean_json)
        except Exception:
            return {"is_challenge_page": False, "raw": raw}

    def solve_turnstile(self, max_attempts: int = 5) -> bool:
        """Locates Turnstile iframe or checkbox and triggers verification."""
        logger.info("Attempting automated challenge bypass / resolution...")
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Resolution attempt {attempt}/{max_attempts}...")
            
            # Step 1: Check snapshot refs
            snapshot = self._run_cli(["snapshot", "-i"])
            logger.debug(f"Interactive snapshot:\n{snapshot}")

            # Step 2: Try clicking challenge container or checkbox via JS
            click_js = """
            (() => {
                const turnstile = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                if (turnstile) {
                    const rect = turnstile.getBoundingClientRect();
                    return JSON.stringify({x: Math.round(rect.left + 30), y: Math.round(rect.top + 30)});
                }
                const btn = document.querySelector('#challenge-stage input, .cf-turnstile, [role="checkbox"]');
                if (btn) {
                    btn.click();
                    return JSON.stringify({clicked: true});
                }
                return JSON.stringify({notFound: true});
            })()
            """
            click_res = self._run_cli(["eval", click_js])
            logger.info(f"Evaluation trigger response: {click_res}")
            
            time.sleep(2)
            detection = self.detect_challenges()
            if not detection.get("is_challenge_page"):
                logger.info("✓ Challenge successfully cleared / bypassed!")
                return True

        return False

    def capture_evidence(self, output_png: str = "/tmp/challenge-solved.png") -> str:
        self._run_cli(["screenshot", output_png])
        logger.info(f"✓ Saved verification screenshot: {output_png}")
        return output_png

    def close(self):
        self._run_cli(["close"])

def main():
    parser = argparse.ArgumentParser(description="🦉 OWL Challenge Solver")
    parser.add_argument("url", nargs="?", default="https://httpbin.org/forms/post", help="Target URL")
    parser.add_argument("-o", "--output", default="/tmp/challenge-result.png", help="Output screenshot path")
    args = parser.parse_args()

    solver = ChallengeSolver()
    solver.navigate(args.url)
    detection = solver.detect_challenges()
    print("Challenge Detection Summary:", json.dumps(detection, indent=2))
    
    if detection.get("is_challenge_page"):
        solved = solver.solve_turnstile()
        print(f"Challenge Solved: {solved}")
    else:
        print("Page is clean (no active bot challenge detected).")
        
    solver.capture_evidence(args.output)
    solver.close()

if __name__ == "__main__":
    main()
