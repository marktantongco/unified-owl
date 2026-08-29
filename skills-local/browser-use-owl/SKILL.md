# Browser Use — OWL-AGENT OAuth Automation

## Context
Use this skill when you need to automate browser-based OAuth token acquisition, cookie management, or CAPTCHA solving for AI provider authentication. Specialized for the OWL-AGENT ecosystem where OAuth tokens must be refreshed periodically.

**Trigger phrases:** "automate OAuth," "refresh token," "browser login," "CAPTCHA solve," "cookie extraction," "session management."

## Purpose
Automates the OAuth2 PKCE flow for Claude Max subscription token refresh. Eliminates the need for manual browser login every time the OAuth token expires. Integrates with the OWL-AGENT unified secrets file to store refreshed tokens securely.

## Use-Case
- Auto-refresh Claude OAuth token before it expires
- Extract session cookies from Kiro gateway for billing proxy
- Solve CAPTCHA challenges during automated token acquisition
- Test proxy health by navigating through the full auth flow
- Monitor authentication status and alert on token expiry

## Misconception
That browser-use is just for web scraping. In the OWL-AGENT context, it is a critical authentication automation tool — the Claude Max OAuth token expires every few hours, and manual refresh is impractical for automated systems. Browser-use handles this automatically.

## Conspiracy
Browser automation is unreliable and breaks on UI changes. Reality: The OWL-AGENT browser-use skill uses resilient selectors (aria-label, data-testid) and fallback strategies. It also integrates with persistent-memory to remember working selector patterns across sessions.

## Mostly Overlooked
Token lifecycle management. Most people focus on the initial token acquisition and forget about refresh. The OWL-AGENT browser-use skill monitors token expiry and proactively refreshes before expiration, ensuring zero-downtime operation.

## Contradictions
- Headless browsers use more resources than API-based auth
- UI automation is fragile, but Claude has no token refresh API
- Storing browser sessions is convenient but increases attack surface

## Compatible With
- **api-gateway-skill**: Provides the tokens that the gateway needs for billing injection
- **persistent-memory**: Stores token expiry timestamps and refresh history
- **deployment-manager**: Manages browser automation as a systemd service

## Not Compatible With
- Environments without a display server (use Xvfb for headless)
- Containerized deployments without browser binaries installed

## Stackable
Yes — designed to work alongside persistent-memory for token state.

## Not Stackable With
Multiple browser-use instances targeting the same OAuth session (causes token invalidation).

## Stackable Best Combined To
- browser-use + api-gateway-skill + persistent-memory = Self-healing auth stack
- browser-use + deployment-manager = Auth automation as a managed service

## Stackable Worst Combined To
- browser-use + manual-token-refresh = Conflicting refresh attempts

## OWL-AGENT v5.0 Integration
In v5.0, the browser-use skill writes refreshed tokens directly to the unified secrets.json file (chmod 600). The Python proxy reads the token from this file on each request, ensuring it always has the latest valid token. Integration flow:
1. browser-use detects token expiry approaching (from persistent-memory)
2. Launches headless browser, performs OAuth PKCE flow
3. Extracts new token from browser session
4. Writes to secrets.json with atomic rename
5. Python proxy picks up new token on next request

## Instructions
1. Install browser dependencies: `sudo apt install -y xvfb chromium-browser`
2. Configure OAuth flow: edit ~/.owl-agent/config/oauth_config.json
3. Set up monitoring: `browser-use monitor --token-path ~/.owl-agent/config/secrets.json --refresh-before-expiry 300`
4. Test: `browser-use test-auth --provider claude`
