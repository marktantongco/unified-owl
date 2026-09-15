# Unified OWL v1.1.3

## 🦉 Overview

**Unified OWL** (Unified Open-source Weighted Loadbalancer) is a comprehensive DNS synergy and AI routing system that provides:

- **Domain-based egress routing** with A/B strategy selection
- **slipnet:// URI** support for custom network configurations
- **Fine-grained domain routing** with 7 routing modes
- **Cost-optimized AI routing** via NadirClaw (40-70% savings)
- **Caddy/TLS auto-configuration** with Let's Encrypt support
- **Bulk credential management** for 500+ users
- **Real-time TUI dashboard** for monitoring and management
- **MCP integration** with 7 connected servers

### 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Fine-Grained Routing** | 7 routing modes: `direct`, `vpn`, `proxy`, `socks5`, `tailscale`, `dns_tunnel`, `tor` |
| **A/B Strategy** | Weighted channel selection based on success/failure history |
| **DNS Override** | Per-domain custom DNS servers with `force_dns` flag |
| **NadirClaw Integration** | Automatic cost optimization: cheap models for simple queries, premium for complex |
| **Response Caching** | LRU + disk cache with TTL for repeated queries |
| **Health Monitoring** | Background health checks for all upstream proxies |
| **Rate Limiting** | Adaptive per-domain rate limiting based on HTTP status codes |
| **MCP Integration** | 7 connected servers (caveman, owl_resilient, headroom, github, octocode, parallel-search, graphify) |
| **TUI Dashboard** | Curses-based real-time monitoring with keyboard navigation |
| **Bulk Credentials** | Manager for 500+ users with key rotation and cooldown tracking |

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/marktantongco/unified-owl.git
cd unified-owl

# Make installer executable
chmod +x install.sh

# Run the one-command installer
./install.sh
```

### 2. Start the System

```bash
# Start the dashboard (recommended first)
python3 -m owl_dns_synergy.dashboard

# Or just the proxy
python3 -m owl_dns_synergy.router
```

### 3. Verify Everything is Working

```bash
# Check OWL proxy health
curl -s http://localhost:60000/health
# {"status":"ok","proxies_total":55,"proxies_healthy":51,"uptime":99445s}

# Check NadirClaw routing
curl -s http://localhost:8856/v1/health

# Test slipnet:// URI parsing
python3 -c "from owl_dns_synergy.router import parse_slipnet_uri; print(parse_slipnet_uri('slipnet://api.internal:5353'))"
```

---

## 📁 Repository Structure

```
unified-owl/
├── install.sh                  # One-command installer script
├── AGENTS.md                   # Agent instructions
├── UNIFIED_OWL_PROJECT_SUMMARY.md  # Session summary
├── WIKI_SESSION_LOG.md         # Session state log
├── owl_dns_synergy/           # Main Python package
│   ├── __init__.py            # Package init, __version__ = "1.1.3"
│   ├── router.py              # Core: SmartChannelRouter, DomainPreference, routing, A/B strategy
│   ├── dashboard.py           # TUI dashboard (curses-based)
│   ├── caddy_tls.py           # Caddy/TLS auto-configuration
│   ├── bulk_credential_api.py # Bulk credential manager (500+ users)
│   └── config.py              # Configuration management
├── opencode.jsonc             # MCP + provider configuration
├── .env                       # Environment variables (create from template)
└── requirements.txt           # Python dependencies
```

---

## 📦 Installation Methods

### Option 1: Install Script (Recommended)

```bash
./install.sh
```

This will:
- Install all Python dependencies
- Create `.env` configuration
- Start OWL DNS Synergy proxy on port 60000
- Start NadirClaw on port 8856 for cost optimization
- Start Prometheus metrics on port 9090
- Configure MCP servers
- Verify the installation

### Option 2: Manual Installation

```bash
# 1. Install Python dependencies
pip install -e .

# 2. Create environment config
cp .env.example .env  # or create .env manually
# Edit .env with your API keys

# 3. Start the services
# Prometheus metrics
python3 -c "from prometheus_client import start_http_server; start_http_server(9090)"

# OWL DNS Synergy
nohup python3 -m owl_dns_synergy.cli serve --host 127.0.0.1 --port 60000 > /tmp/owl-dns.log 2>&1 &

# NadirClaw cost optimization
nohup nadirclaw serve > /tmp/nadirclaw.log 2>&1 &

# Start the dashboard
python3 -m owl_dns_synergy.dashboard
```

---

## 🛠️ Configuration

### `.env` File

Create a `.env` file in the root directory:

```env
# OWL DNS Synergy
OWL_PORT=60000
OWL_API_PORT=60001
OWL_GATEWAY_PORT=60010

# NadirClaw Cost Optimization
NADIRCLAW_BASE_URL=http://localhost:8856/v1
NADIRCLAW_MODEL=nadirclaw/auto

# Prometheus Metrics
PROMETHEUS_PORT=9090

# Redis (optional - for persistent caching)
REDIS_URL=redis://localhost:6379
USE_REDIS=false

# DNS Configuration
DNS_PORT=53
DNS_OVERRIDE_PORT=5353

# Key Rotation (OpenRouter)
OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}

# Freebuff Configuration
FREEBUFF_UNIFIED_PORT=8080

# Logging
LOG_LEVEL=INFO
```

### `opencode.jsonc` Configuration

The MCP server configuration is in `opencode.jsonc`. Key settings:

```jsonc
"owl_dns_synergy": {
  "type": "local",
  "command": ["python3", "-m", "owl_dns_synergy.cli", "serve", "--host", "127.0.0.1", "--port", "60000"],
  "enabled": false,  // ← Set to false (it's DNS tunneling, not MCP)
  "cwd": "/home/x3/workspace/unified-owl",
  "description": "DNS tunneling server, NOT MCP. Use owl_resilient for MCP tools."
}

"owl_resilient": {
  "type": "local",
  "command": ["python3", "-m", "owl_resilient.mcp"],
  "enabled": true,
  "cwd": "/home/x3/workspace/unified-owl",
  "description": "Resilient MCP server with 26 tools including github, headroom, octocode"
}
```

---

## 📡 API Endpoints

### OWL DNS Synergy Proxy

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check: `{"status":"ok","proxies_total":55,"proxies_healthy":51,"uptime":99445s}` |
| `GET /stats` | Statistics: proxy counts, states, quality scores |
| `POST /route` | Route a URL through optimal channel |

### NadirClaw

| Endpoint | Description |
|----------|-------------|
| `GET /v1/health` | Health check |
| `POST /v1/route` | Get cost-optimized model routing |
| `POST /v1/chat/completions` | Chat completions with model selection |

### Caddy/TLS

```bash
# Generate Caddyfile
python3 -c "from owl_dns_synergy.caddy_tls import generate_caddyfile; print(generate_caddyfile('example.com', 'admin@example.com'))"

# Generate Let's Encrypt renewal cron
python3 -c "from owl_dns_synergy.caddy_tls import generate_lets_encrypt_renewal_cron; print(generate_lets_encrypt_renewal_cron())"

# Check Caddy availability
python3 -c "from owl_dns_synergy.caddy_tls import check_caddy_available; print(check_caddy_available())"

# Check Certbot availability
python3 -c "from owl_dns_synergy.caddy_tls import check_certbot_available; print(check_certbot_available())"
```

---

## 🔧 Usage Examples

### Fine-Grained Domain Routing

```python
from owl_dns_synergy.router import SmartChannelRouter, set_domain_routing_mode, set_dns_override

router = SmartChannelRouter()

# Set routing mode per domain
router.set_domain_routing_mode("api.internal", "socks5")     # SOCKS5 via Tailscale
router.set_domain_routing_mode("external.com", "vpn")        # VPN tunnel
router.set_domain_routing_mode("onion.site", "tor")         # Tor network

# Set DNS override
router.set_dns_override("api.internal", "1.1.1.1", 5353)     # Custom DNS with force_dns
router.set_dns_override("internal.com", "9.9.9.9", 5353)    # DNS over TLS

# Get routing decision
state = router._get_state("api.internal")  # → HTTP_PREFERRED or DNS_FALLBACK
```

### slipnet:// URI Support

```python
from owl_dns_synergy.router import parse_slipnet_uri, set_preference_from_slipnet_uri

# Parse URI
params = parse_slipnet_uri("slipnet://api.internal:5353")
# {"host": "api.internal", "port": 5353, "username": "", "password": "", "transport_mode": "dns"}

# Set preference from URI
set_preference_from_slipnet_uri(router, "internal.com", "slipnet://internal.com:5353")
```

### Bulk Credential Management

```python
from owl_dns_synergy.bulk_credential_api import get_bulk_credential_manager

mgr = get_bulk_credential_manager()
mgr.add_user("admin", ["key1", "key2", "key3"])
mgr.add_user("user1", ["key4", "key5"])

status = mgr.get_user_status("admin")
all_status = mgr.get_all_status()
```

### Caddy/TLS Auto-Configuration

```python
from owl_dns_synergy.caddy_tls import generate_caddyfile, generate_lets_encrypt_renewal_cron

# Generate Caddyfile
caddyfile = generate_caddyfile("example.com", "admin@example.com")
# Returns Caddy config with DNS-01 Cloudflare challenge

# Generate Certbot cron
cron = generate_lets_encrypt_renewal_cron("admin@example.com")
# Returns cron job for auto-renewal
```

### Version Checking

```python
from owl_dns_synergy.router import check_github_version, get_current_version

current = get_current_version()      # "1.1.3"
update_available = check_github_version("1.1.3")  # True if latest > current
```

---

## 📊 Monitoring & Dashboard

### TUI Dashboard

Run the dashboard:

```bash
python3 -m owl_dns_synergy.dashboard
```

**Keyboard Shortcuts:**
- `q` / `Q` - Quit
- `r` / `R` - Refresh statistics
- `h` / `H` - Show help

**Dashboard Sections:**
- **Channel Statistics** - HTTP/DNS success rates with color coding
- **API Key Status** - Key rotation and cooldown status
- **Domain Table** - Per-domain routing config (mode, DNS server, state, score)
- **DNS Override** - Custom DNS server visualization
- **Help Screen** - Complete keyboard shortcuts list

### Prometheus Metrics

Metrics are available on port 9090. Key metrics include:

- `synergy_requests_total` - Total requests processed [channel, domain, status]
- `synergy_active_connections` - Currently active connections [channel]
- `synergy_channel_switches_total` - Number of channel switches [from_channel, to_channel]
- `synergy_circuit_breaker_state` - Circuit breaker state [channel, domain]
- `synergy_key_rotation_total` - Number of API key rotations

---

## 🔒 Security

### Recommendations

1. **API Key Management**: Keep `OPENROUTER_API_KEY` and other secrets secure
2. **Redis for Persistent Caching**: Enable `USE_REDIS=true` in `.env` for production
3. **Rate Limiting**: The adaptive rate limiter protects against 429/503 errors
4. **Circuit Breakers**: Automatic protection against failed upstreams
5. **TLS/SSL**: Use Caddy with Let's Encrypt for HTTPS termination
6. **Bulk Credential Rotation**: Regular key rotation via the bulk credential manager

### Permissions

- The system runs with permissive permissions by design
- `external_directory: allow` enables `~/`, `/tmp` access
- MCP github uses user-scoped token (`GITHUB_PAT`)
- Bulk credential manager has per-user key rotation and cooldown tracking

---

## 🤝 Contributing

### Development Setup

```bash
# 1. Fork the repository
git fork https://github.com/marktantongco/unified-owl

# 2. Create a branch
git checkout -b feature/your-feature

# 3. Make your changes
# 4. Test your changes
python3 -m py_compile owl_dns_synergy/*.py

# 5. Commit and push
git add .
git commit -m "feat: your description"
git push origin feature/your-feature

# 6. Open a Pull Request
```

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function signatures
- Document all public functions with docstrings
- Keep caveman mode for terse communication in sessions
- All new features must have test coverage

### Adding New Features

1. Add the feature to the appropriate file (`router.py`, `dashboard.py`, etc.)
2. Add tests in the `tests/` directory (if applicable)
3. Update `opencode.jsonc` if MCP configuration changes
4. Update `.env` template if new environment variables are needed
5. Add documentation to this README
6. Run `./install.sh` to verify

---

## 📜 Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0.0** | Initial release | Core: slipnet:// URI, DomainPreference, A/B strategy |
| **1.1.0** | Added Phase 2 | Version checking, Caddy TLS, bulk credential API |
| **1.1.1** | Fixed MCP timeout | Set owl_dns_synergy as non-MCP |
| **1.1.2** | Phase 3 Item 7 | Fine-grained domain routing (7 modes) |
| **1.1.3** | Phase 3 Items 8-9 | DNS override, TUI dashboard, NadirClaw integration, caching, health checks |

---

## 🐛 Known Issues

| Issue | Workaround |
|-------|------------|
| **Docker socket permissions** | Cannot manage Docker containers without socket access |
| **NadirClaw required for full optimization** | System works without NadirClaw, falls back to direct routing |
| **Redis not installed** | Caching works in memory only; enable `USE_REDIS=true` to install Redis |
| **opencode.jsonc MCP probe timeout** | Fixed by setting `owl_dns_synergy.enabled: false` |
| **Domain routing defaults to `direct`** | Set explicit routing modes via `set_domain_routing_mode()` |

---

## 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

- **GitHub**: [https://github.com/marktantongco/unified-owl](https://github.com/marktantongco/unified-owl)
- **Author**: marktantongco
- **Issue Tracker**: [GitHub Issues](https://github.com/marktantongco/unified-owl/issues)
- **Discussion**: [Git Discussions](https://github.com/marktantongco/unified-owl/discussions)

---

## 🙏 Acknowledgments

- **NadirClaw**: Cost-optimized AI routing
- **Prometheus**: Metrics monitoring
- **Caddy**: TLS/HTTP reverse proxy
- **OpenCode**: CLI framework
- **All contributors**: Who have helped shape this project

---

*Unified OWL v1.1.3 - Intelligent DNS Synergy & AI Router for the Modern Era*