# OWL-DNS-Synergy

**Unified Dual-Channel Resilient Access Engine** — HTTP proxy evasion (OWL-AGENT v4.2) + DNS tunneling (LLM-DNS-Proxy) + 5 auxiliary repos in one hardened stack.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/marktantongco/owl-dns-synergy)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/)

> **Live docs:** <https://marktantongco.github.io/owl-dns-synergy/> · **Repo:** <https://github.com/marktantongco/owl-dns-synergy>

## Quick Start

```bash
git clone https://github.com/marktantongco/owl-dns-synergy.git
cd owl-dns-synergy
./install.sh
source ~/.owl-dns-synergy/config.env
source /run/user/$(id -u)/owl-dns-synergy/env
owl-dns-synergy fetch https://example.com --verbose
owl-dns-synergy test-connection
```

## Architecture

See the [README](https://github.com/marktantongco/owl-dns-synergy#architecture) for the full 5-layer diagram and 7-channel cascade.

## Installation

The unified installer (`install.sh` v4.0.0) handles everything: venv, fernet keys, systemd units, Prometheus metrics.

```bash
./install.sh              # full install
./install.sh --uninstall  # remove
```

For isolated testing (does not touch your real HOME):

```bash
HOME=$(mktemp -d) bash ./install.sh
```

## CLI

| Command | Description |
|---|---|
| `owl-dns-synergy fetch <url>` | Fetch via optimal channel (auto-failover) |
| `owl-dns-synergy test-connection` | Probe HTTP + DNS channels |
| `owl-dns-synergy serve` | Start DNS tunneling server (:5353) |
| `owl-dns-synergy stats` | Channel stats + key rotator status |
| `owl-dns-synergy key-status` | Show OpenRouter key rotation |
| `scripts/keysync.py` | Vault-to-runtime secret hydration (tmpfs) |

## Production Deployment

- Systemd units: `~/.config/systemd/user/owl-dns-synergy.service` (user), `deploy/owl-dns-synergy.service` (system)
- Metrics: Prometheus on `:9091` (user) / `:9090` (system)
- Secrets: fernet pairs in `~/.owl-dns-synergy/secrets/` + vault `secure-tokens/` → hydrated to `/run/user/<uid>/owl-dns-synergy/env` (tmpfs, never on disk)

See [DEPLOY.md](https://github.com/marktantongco/owl-dns-synergy/blob/main/DEPLOY.md) for system-wide deployment.

## Reports

- [Final Report](OWL-DNS-Synergy-Final-Report.pdf)
- [Audit Critique v3](OWL-DNS-Synergy-Audit-Critique-v3.pdf)
- [Combined Fix Summary](OWL-DNS-Synergy-Combined-Fix-Summary.pdf)
- [Memory Analysis Deep Dive](OWL-DNS-Synergy-Memory-Analysis-Deep-Dive.pdf)

## License

[MIT](https://github.com/marktantongco/owl-dns-synergy/blob/main/LICENSE)
