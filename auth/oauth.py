#!/usr/bin/env python3
"""
auth/oauth.py — THE GATEKEEPER (freebuff-auth-automation)
Implements Improvement #2: Intelligent Auth Pipeline
- Encrypted vault (Fernet) for tokens
- TTL monitoring + pre-emptive renewal (80% TTL)
- Per-provider routing (proxy-routing.json) — NEVER proxy OAuth endpoints
- Transparent injection via middleware
"""
import asyncio
import json
import os
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any
import logging
logger = logging.getLogger("auth.oauth")

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Fernet = None

VAULT_PATH = Path.home() / ".owl-agent" / "vault" / "tokens.enc"
CONFIG_PATH = Path(__file__).parent.parent / "config" / "proxy-routing.json"

# OAuth endpoints that MUST NOT be proxied (proxy breaks token refresh)
OAUTH_BYPASS = {
    "oauth", "token", "refresh", ".well-known", "authorize",
    "accounts.google.com", "login.microsoftonline.com", "github.com/login/oauth"
}

class Vault:
    """Fernet-encrypted token vault."""
    def __init__(self, key: Optional[str] = None):
        if CRYPTO_AVAILABLE:
            if key:
                self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
            else:
                # derive from machine id or generate
                k = os.getenv("OWL_VAULT_KEY")
                if k:
                    self.fernet = Fernet(k.encode())
                else:
                    self.fernet = Fernet(Fernet.generate_key())
                    logger.warning(f"Generated ephemeral vault key — set OWL_VAULT_KEY to persist")
            self.key = self.fernet._fernet_key if hasattr(self.fernet, '_fernet_key') else b""
        else:
            self.fernet = None
            self.key = b""
            logger.warning("cryptography not available — vault is plaintext")

    def encrypt(self, data: dict) -> bytes:
        raw = json.dumps(data).encode()
        if self.fernet:
            return self.fernet.encrypt(raw)
        return base64.b64encode(raw)

    def decrypt(self, blob: bytes) -> dict:
        if self.fernet:
            return json.loads(self.fernet.decrypt(blob))
        return json.loads(base64.b64decode(blob))

    def save(self, tokens: dict, path: Path = VAULT_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        blob = self.encrypt(tokens)
        path.write_bytes(blob)
        path.chmod(0o600)
        logger.info(f"Vault saved {len(tokens)} tokens to {path}")

    def load(self, path: Path = VAULT_PATH) -> dict:
        if not path.exists():
            return {}
        try:
            return self.decrypt(path.read_bytes())
        except Exception as e:
            logger.error(f"Vault decrypt failed: {e}")
            return {}

class TokenEntry:
    def __init__(self, token: str, ttl: int = 3600, provider: str = "generic"):
        self.token = token
        self.created = time.time()
        self.ttl = ttl
        self.provider = provider
        self.refresh_count = 0

    @property
    def expires_at(self) -> float:
        return self.created + self.ttl

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    @property
    def should_refresh(self) -> bool:
        # Pre-emptive at 80% TTL
        return time.time() >= self.created + self.ttl * 0.8

    def to_dict(self):
        return {"token": self.token, "created": self.created, "ttl": self.ttl, "provider": self.provider}

    @classmethod
    def from_dict(cls, d):
        e = cls(d["token"], d["ttl"], d["provider"])
        e.created = d["created"]
        return e

class AuthManager:
    """Intelligent Auth Pipeline — TTL monitor + background refresh."""
    def __init__(self, vault_key: Optional[str] = None):
        self.vault = Vault(vault_key)
        self.tokens: Dict[str, TokenEntry] = {}
        self._load()
        self._monitor_task: Optional[asyncio.Task] = None
        # router config
        self.routing = {}
        if CONFIG_PATH.exists():
            try:
                self.routing = json.loads(CONFIG_PATH.read_text()).get("providers", {})
            except Exception:
                pass

    def _load(self):
        raw = self.vault.load()
        for k, v in raw.items():
            try:
                self.tokens[k] = TokenEntry.from_dict(v)
            except Exception:
                pass
        logger.info(f"AuthManager loaded {len(self.tokens)} tokens")

    def _save(self):
        self.vault.save({k: v.to_dict() for k, v in self.tokens.items()})

    def set_token(self, provider: str, token: str, ttl: int = 3600):
        self.tokens[provider] = TokenEntry(token, ttl, provider)
        self._save()
        logger.info(f"Token set for {provider} ttl={ttl}s")

    def get_token(self, provider: str) -> Optional[str]:
        e = self.tokens.get(provider)
        if not e or e.is_expired:
            return None
        return e.token

    def should_proxy(self, url: str) -> bool:
        """Never proxy OAuth endpoints."""
        low = url.lower()
        for kw in OAUTH_BYPASS:
            if kw in low:
                return False
        return True

    def get_provider_route(self, provider: str) -> dict:
        return self.routing.get(provider, {"proxy": "direct", "type": "none"})

    async def refresh_if_needed(self, provider: str, refresher=None):
        e = self.tokens.get(provider)
        if not e or not e.should_refresh:
            return
        logger.info(f"Pre-emptive refresh for {provider} (80% TTL)")
        if refresher:
            try:
                new_token = await refresher(provider, e.token) if asyncio.iscoroutinefunction(refresher) else refresher(provider, e.token)
                if new_token:
                    e.token = new_token
                    e.created = time.time()
                    e.refresh_count += 1
                    self._save()
                    logger.info(f"Refreshed {provider} count={e.refresh_count}")
            except Exception as ex:
                logger.error(f"Refresh failed for {provider}: {ex}")

    async def start_monitor(self, interval: int = 60):
        """Background TTL monitor."""
        async def _loop():
            while True:
                for prov in list(self.tokens.keys()):
                    await self.refresh_if_needed(prov)
                await asyncio.sleep(interval)
        self._monitor_task = asyncio.create_task(_loop())
        logger.info(f"Auth monitor started every {interval}s")

    def stats(self):
        return {
            "providers": len(self.tokens),
            "tokens": {k: {"ttl": v.ttl, "expires_in": int(v.expires_at - time.time()), "should_refresh": v.should_refresh, "refresh_count": v.refresh_count} for k, v in self.tokens.items()},
            "vault_encrypted": CRYPTO_AVAILABLE,
            "routing_providers": len(self.routing),
        }

# Singleton
manager = AuthManager()

if __name__ == "__main__":
    m = AuthManager()
    m.set_token("openrouter", "sk-test-123", ttl=3600)
    print(m.stats())
    print("should_proxy oauth?", m.should_proxy("https://accounts.google.com/o/oauth2/token"))
    print("should_proxy api?", m.should_proxy("https://api.openai.com/v1/chat/completions"))
