"""Caddy and Let's Encrypt TLS automation for OWL-AGENT.

Provides functions to:
- Generate Caddyfile configurations with DNS-01 challenges
- Generate Certbot renewal cron jobs
- Check tool availability (Caddy, Certbot)
- Manage TLS certificate lifecycle
"""

import datetime
import shutil


def generate_caddyfile(domain, email, dns_provider="cloudflare", http_port=80, https_port=443):
    """Generate a Caddyfile for the given domain with Let's Encrypt TLS.

    Args:
        domain: Domain name to secure
        email: Email for Let's Encrypt account registration
        dns_provider: DNS provider for challenge (cloudflare, duckdns, namecheap)
        http_port: HTTP port for ACME challenge
        https_port: HTTPS port for production traffic

    Returns:
        Caddyfile configuration string
    """
    CLOUDFLARE_API = "https://api.cloudflare.com/client/v4"

    lines = []
    lines.append(f"{domain} {{")
    lines.append(f"    http_port {http_port}")
    lines.append(f"    https_port {https_port}")
    lines.append("")
    lines.append("    # TLS via Let's Encrypt")
    lines.append(f"    tls {email} {{")
    lines.append("        # DNS-01 challenge via Cloudflare")
    lines.append(f"        dns cloudflare {CLOUDFLARE_API}")
    lines.append("    }")
    lines.append("")
    lines.append("    # HTTP handling")
    lines.append("    reverse_proxy localhost:7860")
    lines.append("")
    lines.append("    # Health check")
    lines.append("    header /health Status OK")
    lines.append("}")

    return "\n".join(lines)


def generate_lets_encrypt_renewal_cron(domain, email, dns_provider="cloudflare"):
    """Generate a cron job entry for Let's Encrypt certificate renewal.

    Args:
        domain: Domain name
        email: Email for Let's Encrypt account
        dns_provider: DNS provider for challenges

    Returns:
        cron job entry string
    """
    now = datetime.datetime.now()
    renewal_time = now.replace(hour=2, minute=0, second=0) + datetime.timedelta(days=1)

    cron_entry = """# OWL-AGENT Let's Encrypt renewal cron job
# Renew certificates daily at 2:00 AM
0 2 * * * /usr/local/bin/certbot renew --dns-cloudflare --dns-cloudflare-credentials /etc/letsencreep/credentials.json --domain {domain} --email {email} >> /var/log/owl-letsencrypt.log 2>&1

# OWL-AGENT: Auto-reload Caddy after renewal
# (uncomment if using Caddy)
# 0 3 * * * systemctl reload caddy 2>/dev/null || true""".format(domain=domain, email=email)

    return cron_entry


def check_caddy_available():
    """Check if Caddy is installed and available."""
    import shutil
    return shutil.which("caddy") is not None


def check_certbot_available():
    """Check if Certbot (Let's Encrypt client) is installed."""
    import shutil
    return shutil.which("certbot") is not None


# Example usage
_EXAMPLE = """

# To set up TLS for your domain:

# 1. Install Caddy: sudo apt install -y caddy
# 2. Install Certbot: sudo apt install -y certbot
# 3. Generate Caddyfile: generate_caddyfile("yourdomain.com", "you@example.com")
# 4. Set up cron: generate_lets_encrypt_renewal_cron("yourdomain.com", "you@example.com")
# 5. Run: caddy run --config /etc/caddy/Caddyfile

"""

if __name__ == "__main__":
    print("Caddy/TLS module loaded")
    print(f"check_caddy_available: {check_caddy_available()}")
    print(f"check_certbot_available: {check_certbot_available()}")
    print()
    print("Sample Caddyfile:")
    print(generate_caddyfile("example.com", "admin@example.com"))