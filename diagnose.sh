#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
#  OWL-AGENT v7.2 — Diagnostics v3.1
#  5-Section Health Check: Service · Connectivity · Environment · Resources · Auto-Tune
#
#  v3.1 changes:
#   - Exit code reflects failures (0 = all pass, 1 = issues found)
#   - Removed references to deleted proxy_defense_fixed_v3.py
#   - /proc/meminfo reads guarded (no arithmetic on empty values)
#   - AutoTuner section reflects observability-only design
#   - Version bumped to 3.1
#
#  v3.0 (v7.1):
#   - DELETED --fix mode. Diagnostics report; humans fix.
#   - DELETED httpbin.org dependency. Connectivity uses proxy /health.
#   - DELETED `rg` hard dependency; falls back to grep.
# ═══════════════════════════════════════════════════════════════════════════
set -uo pipefail

readonly VERSION="3.1"
readonly OWL_HOME="${OWL_HOME:-$HOME/.owl-agent}"
readonly PROXY_PORT="${OWL_PROXY_PORT:-60000}"
readonly GATEWAY_PORT=8333
readonly MESH_PORT="${OWL_MESH_PORT:-42100}"

# ── Colors ─────────────────────────────────────────────────────────────────
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly DIM='\033[2m'
readonly NC='\033[0m'

# ── Flags ──────────────────────────────────────────────────────────────────
VERBOSE=false
FAILURES=0

# ── Logging ────────────────────────────────────────────────────────────────
pass() { echo -e "  ${GREEN}✓${NC} $*"; }
fail() { echo -e "  ${RED}✗${NC} $*"; FAILURES=$((FAILURES + 1)); }
warn() { echo -e "  ${YELLOW}⚠${NC} $*"; }
info() { echo -e "  ${CYAN}›${NC} $*"; }
header() { echo -e "\n${BOLD}${CYAN}══ $1 ══${NC}\n"; }

# ── Usage ──────────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
OWL-AGENT Diagnostics v${VERSION}

USAGE:
  $(basename "$0") [OPTIONS]

OPTIONS:
  --verbose    Show detailed output (logs, full JSON responses)
  --version    Print version and exit
  -h, --help   Show this help message

EXIT CODES:
  0   All checks passed
  1   One or more checks failed

NOTE:
  Diagnostics report only. When an issue is detected, the suggested
  command is printed for you to run manually.
EOF
}

# ── Parse Arguments ────────────────────────────────────────────────────────
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --verbose) VERBOSE=true; shift ;;
      --version) echo "OWL-AGENT Diagnostics v${VERSION}"; exit 0 ;;
      -h|--help) usage; exit 0 ;;
      --fix)
        echo "--fix mode was removed in v7.1. Diagnostics report; humans fix." >&2
        exit 2
        ;;
      *)
        echo "Unknown option: $1" >&2
        usage >&2
        exit 2
        ;;
    esac
  done
}

# ── Suggest fix helper ─────────────────────────────────────────────────────
suggest_fix() {
  local desc="$1"
  local cmd="$2"
  echo -e "  ${YELLOW}→ Suggested fix:${NC} ${desc}"
  echo -e "    ${DIM}\$ ${cmd}${NC}"
}

# ── Search helper ──────────────────────────────────────────────────────────
search() {
  local pattern="$1"
  local file="$2"
  if [[ ! -r "$file" ]]; then
    echo "0"
    return
  fi
  if command -v rg &>/dev/null; then
    rg -c "${pattern}" "${file}" 2>/dev/null || echo "0"
  else
    grep -cE "${pattern}" "${file}" 2>/dev/null || echo "0"
  fi
}

search_lines() {
  local pattern="$1"
  local file="$2"
  if [[ ! -r "$file" ]]; then
    return
  fi
  if command -v rg &>/dev/null; then
    rg "${pattern}" "${file}" 2>/dev/null | tail -5
  else
    grep -E "${pattern}" "${file}" 2>/dev/null | tail -5
  fi
}

# ── Safe numeric read from /proc/meminfo ───────────────────────────────────
meminfo_kb() {
  local key="$1"
  awk -v k="^${key}:" '$0 ~ k {print $2; exit}' /proc/meminfo 2>/dev/null || echo "0"
}

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 1: Service Status
# ═══════════════════════════════════════════════════════════════════════════
section_service_status() {
  header "1. Service Status"

  if command -v systemctl &>/dev/null; then
    if systemctl is-active --quiet owl-forward-proxy 2>/dev/null; then
      pass "owl-forward-proxy service: active"
    else
      fail "owl-forward-proxy service: NOT running"
      suggest_fix "start the proxy service" \
        "sudo systemctl start owl-forward-proxy"
    fi

    if systemctl is-enabled --quiet owl-forward-proxy 2>/dev/null; then
      pass "owl-forward-proxy: enabled on boot"
    else
      warn "owl-forward-proxy: not enabled on boot"
      suggest_fix "enable on boot" \
        "sudo systemctl enable owl-forward-proxy"
    fi

    if systemctl is-active --quiet kiro-gateway 2>/dev/null; then
      pass "kiro-gateway service: active"
    else
      warn "kiro-gateway service: NOT running (may be --skip-gateway)"
    fi
  else
    warn "systemctl not available — skipping service checks"
  fi

  if command -v ss &>/dev/null; then
    if ss -tln 2>/dev/null | grep -q ":${PROXY_PORT} "; then
      pass "Port ${PROXY_PORT} (proxy): listening"
    else
      fail "Port ${PROXY_PORT} (proxy): NOT listening"
    fi
    if ss -tln 2>/dev/null | grep -q ":${GATEWAY_PORT} "; then
      pass "Port ${GATEWAY_PORT} (gateway): listening"
    else
      warn "Port ${GATEWAY_PORT} (gateway): NOT listening"
    fi
  else
    warn "ss not available — skipping port checks"
  fi

  if pgrep -f "forward_proxy.py" &>/dev/null; then
    pass "forward_proxy.py process: running (PID $(pgrep -f 'forward_proxy.py' | head -1))"
  else
    fail "forward_proxy.py process: NOT running"
  fi

  if [[ "${VERBOSE}" == true ]] && command -v journalctl &>/dev/null; then
    echo -e "\n  ${DIM}── Recent owl-forward-proxy logs ──${NC}"
    sudo journalctl -u owl-forward-proxy --no-pager -n 10 2>/dev/null \
      || echo "  (no logs available)"
  fi
}

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 2: Connectivity
# ═══════════════════════════════════════════════════════════════════════════
section_connectivity() {
  header "2. Connectivity"

  if ! command -v curl &>/dev/null; then
    warn "curl not available — skipping connectivity checks"
    return
  fi

  # ── Proxy /health endpoint ────────────────────────────────────────────
  local health_resp
  health_resp=$(curl -s --connect-timeout 3 \
    "http://127.0.0.1:${PROXY_PORT}/health" 2>/dev/null || echo "")
  if echo "${health_resp}" | python3 -c \
      "import sys,json; d=json.load(sys.stdin); assert d['status']=='ok'" \
      2>/dev/null; then
    pass "Proxy /health: OK"
    if [[ "${VERBOSE}" == true ]]; then
      echo -e "  ${DIM}$(echo "${health_resp}" | python3 -m json.tool 2>/dev/null)${NC}"
    fi
  else
    fail "Proxy /health: not responding or malformed"
    suggest_fix "check proxy is running" \
      "sudo systemctl status owl-forward-proxy"
  fi

  # ── Proxy forwarding probe ────────────────────────────────────────────
  local probe_code
  probe_code=$(curl -x "http://127.0.0.1:${PROXY_PORT}" \
    -s -o /dev/null -w "%{http_code}" \
    --connect-timeout 5 -m 10 \
    "https://api.anthropic.com/" 2>/dev/null || echo "000")
  if [[ "${probe_code}" =~ ^[2-4][0-9]{2}$ ]]; then
    pass "Proxy forwarding: working (probe returned ${probe_code})"
  else
    fail "Proxy forwarding: not working (probe returned ${probe_code})"
  fi

  # ── Gateway /v1/models ────────────────────────────────────────────────
  local models_resp
  models_resp=$(curl -s --connect-timeout 3 \
    "http://127.0.0.1:${GATEWAY_PORT}/v1/models" 2>/dev/null || echo "")
  if [[ -n "${models_resp}" ]] && echo "${models_resp}" | \
      python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    pass "Gateway /v1/models: responding with valid JSON"
  else
    warn "Gateway /v1/models: not available (gateway may not be running)"
  fi

  # ── Direct internet (optional, non-fatal) ─────────────────────────────
  local direct_code
  direct_code=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout 5 -m 8 "https://www.google.com" 2>/dev/null || echo "000")
  if [[ "${direct_code}" =~ ^[23][0-9]{2}$ ]]; then
    pass "Direct internet: reachable"
  else
    warn "Direct internet: may be blocked (expected in proxy-required networks)"
  fi

  # ── DNS ───────────────────────────────────────────────────────────────
  if command -v host &>/dev/null; then
    if host api.anthropic.com &>/dev/null; then
      pass "DNS resolution: working (api.anthropic.com)"
    else
      fail "DNS resolution: FAILED for api.anthropic.com"
      suggest_fix "check /etc/resolv.conf" "cat /etc/resolv.conf"
    fi
  elif command -v getent &>/dev/null; then
    if getent hosts api.anthropic.com &>/dev/null; then
      pass "DNS resolution: working (api.anthropic.com via getent)"
    else
      fail "DNS resolution: FAILED for api.anthropic.com"
    fi
  else
    warn "Neither 'host' nor 'getent' available — skipping DNS check"
  fi
}

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 3: Environment
# ═══════════════════════════════════════════════════════════════════════════
section_environment() {
  header "3. Environment Variables"

  local proxy_vars=(HTTP_PROXY HTTPS_PROXY UPSTREAM_PROXY NO_PROXY)
  for var in "${proxy_vars[@]}"; do
    local val="${!var:-<unset>}"
    if [[ "${val}" != "<unset>" ]]; then
      pass "${var}=${val}"
    elif [[ "${var}" == "NO_PROXY" ]]; then
      info "${var}=<unset> (optional)"
    else
      warn "${var}=<unset>"
    fi
  done

  local api_vars=(
    ANTIGRAVITY_API_KEY ANTHROPIC_API_KEY OPENCODE_API_KEY
    GITHUB_COPILOT_TOKEN KIRO_API_KEY HERMES_API_KEY
  )
  echo -e "\n  ${DIM}── API Keys ──${NC}"
  for var in "${api_vars[@]}"; do
    local val="${!var:-<unset>}"
    if [[ "${val}" != "<unset>" ]]; then
      local masked
      if [[ ${#val} -ge 8 ]]; then
        masked="${val:0:4}...${val: -4}"
      else
        masked="${val:0:2}***"
      fi
      pass "${var}=${masked} (set)"
    else
      warn "${var}=<unset>"
    fi
  done

  local owl_vars=(
    OWL_HOME OWL_PROXY_HOST OWL_PROXY_PORT OWL_PROXY_TOKEN
    OWL_MAX_CONNECTIONS OWL_ENABLE_MESH OWL_MESH_PORT OWL_ALLOW_EXTRA
  )
  echo -e "\n  ${DIM}── OWL Configuration ──${NC}"
  for var in "${owl_vars[@]}"; do
    local val="${!var:-<default>}"
    if [[ "${var}" == "OWL_PROXY_TOKEN" && -n "${!var:-}" ]]; then
      val="<set, length=${#val}>"
    fi
    info "${var}=${val}"
  done

  if [[ ":${PATH}:" == *":${HOME}/.local/bin:"* ]]; then
    pass "~/.local/bin in PATH"
  else
    warn "~/.local/bin NOT in PATH"
    suggest_fix "add to PATH (one-time)" \
      "echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc"
  fi
}

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 4: Resources
# ═══════════════════════════════════════════════════════════════════════════
section_resources() {
  header "4. Resources"

  local mem_total mem_available mem_used mem_percent
  mem_total=$(meminfo_kb "MemTotal")
  mem_available=$(meminfo_kb "MemAvailable")

  if [[ "${mem_total}" -eq 0 ]]; then
    warn "Cannot read /proc/meminfo — skipping memory checks"
  else
    if [[ "${mem_available}" -eq 0 ]]; then
      local mem_free buffers cached
      mem_free=$(meminfo_kb "MemFree")
      buffers=$(meminfo_kb "Buffers")
      cached=$(meminfo_kb "^Cached")
      mem_available=$((mem_free + buffers + cached))
    fi
    mem_used=$((mem_total - mem_available))
    mem_percent=$((mem_used * 100 / mem_total))

    local mem_total_gb=$((mem_total / 1024 / 1024))
    local mem_avail_gb=$((mem_available / 1024 / 1024))
    info "RAM: ${mem_total_gb}GB total, ${mem_avail_gb}GB available (${mem_percent}% used)"

    if [[ ${mem_total} -lt $((4 * 1024 * 1024)) ]]; then
      warn "RAM is below 4GB. Services may be memory-constrained."
    else
      pass "RAM is 4GB or above"
    fi

    if [[ ${mem_percent} -gt 90 ]]; then
      fail "Memory usage above 90%! Services may crash."
      suggest_fix "free memory or restart services" \
        "sudo systemctl restart owl-forward-proxy"
    elif [[ ${mem_percent} -gt 75 ]]; then
      warn "Memory usage above 75%. Monitor closely."
    else
      pass "Memory usage is healthy"
    fi
  fi

  local swap_total swap_free swap_total_mb
  swap_total=$(meminfo_kb "SwapTotal")
  swap_free=$(meminfo_kb "SwapFree")
  swap_total_mb=$((swap_total / 1024))

  if [[ "${swap_total}" -eq 0 ]]; then
    warn "No swap configured. Consider adding swap for stability."
    suggest_fix "add 2GB swap" \
      "sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile"
  else
    info "Swap: ${swap_total_mb}MB total, $((swap_free / 1024))MB free"
    pass "Swap is configured"
  fi

  local owl_disk_info
  owl_disk_info=$(df -h "${OWL_HOME}" 2>/dev/null | tail -1 || echo "")
  if [[ -n "${owl_disk_info}" ]]; then
    local disk_use disk_avail disk_pct
    disk_use=$(echo "${owl_disk_info}" | awk '{print $5}')
    disk_avail=$(echo "${owl_disk_info}" | awk '{print $4}')
    disk_pct=$(echo "${disk_use}" | tr -d '%')
    info "Disk (${OWL_HOME}): ${disk_use} used, ${disk_avail} available"
    if [[ "${disk_pct}" =~ ^[0-9]+$ ]]; then
      if [[ ${disk_pct} -gt 90 ]]; then
        fail "Disk usage above 90%!"
      elif [[ ${disk_pct} -gt 80 ]]; then
        warn "Disk usage above 80%."
      else
        pass "Disk usage is healthy"
      fi
    fi
  fi

  if [[ "${VERBOSE}" == true && -r /proc/meminfo ]]; then
    echo -e "\n  ${DIM}── /proc/meminfo (selected) ──${NC}"
    for key in MemTotal MemFree MemAvailable Buffers Cached SwapTotal SwapFree Shmem; do
      local val
      val=$(meminfo_kb "${key}")
      info "${key}: ${val} kB"
    done
  fi

  echo -e "\n  ${DIM}── Service Memory Usage ──${NC}"
  if command -v systemctl &>/dev/null; then
    for svc in owl-forward-proxy; do
      local pid
      pid=$(systemctl show "${svc}" --property=MainPID --value 2>/dev/null || echo "0")
      if [[ "${pid}" != "0" && -d "/proc/${pid}" ]]; then
        local rss
        rss=$(awk '/VmRSS/ {print $2}' "/proc/${pid}/status" 2>/dev/null || echo "0")
        info "${svc}: PID=${pid}, RSS=$((rss / 1024))MB"
      else
        info "${svc}: not running"
      fi
    done
  else
    info "(systemctl not available)"
  fi
}

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 5: Auto-Tune Status
# ═══════════════════════════════════════════════════════════════════════════
section_auto_tune() {
  header "5. Auto-Tune Status"

  info "AutoTuner is observability-only in v7.2."
  info "Connection limit is fixed at startup; restart to change OWL_MAX_CONNECTIONS."

  local log_dir="${OWL_HOME}/logs"
  local proxy_log="${log_dir}/forward_proxy.log"

  if [[ -f "${proxy_log}" ]]; then
    local rl_count
    rl_count=$(search "rate.limit|blocked|circuit.open|throttl" "${proxy_log}")
    if [[ "${rl_count}" -gt 0 ]]; then
      warn "Rate-limit/block events: ${rl_count}"
      if [[ "${VERBOSE}" == true ]]; then
        search_lines "rate.limit|blocked|circuit.open" "${proxy_log}"
      fi
    else
      pass "No rate-limit or block events in proxy log"
    fi
  elif command -v journalctl &>/dev/null; then
    info "Proxy log not found — checking journald"
    local journal_rl
    journal_rl=$(sudo journalctl -u owl-forward-proxy --no-pager -n 100 2>/dev/null \
      | grep -cE "rate.limit|blocked|circuit.open" 2>/dev/null || echo "0")
    if [[ "${journal_rl}" -gt 0 ]]; then
      warn "Rate-limit events in journal: ${journal_rl}"
    else
      pass "No rate-limit events found in recent journal"
    fi
  else
    info "No proxy log or journal available"
  fi

  # Rate-limit / circuit state from live /health
  if command -v curl &>/dev/null; then
    local health
    health=$(curl -s --connect-timeout 3 \
      "http://127.0.0.1:${PROXY_PORT}/health" 2>/dev/null || echo "")
    if [[ -n "${health}" ]]; then
      echo -e "\n  ${DIM}── Live circuit state ──${NC}"
      echo "${health}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    cs = d.get('circuit_states', {})
    if cs:
        for domain, state in sorted(cs.items()):
            print(f'    {domain}: {state}')
    else:
        print('    (no circuits tracked yet)')
    print(f'    active_connections: {d.get(\"active_connections\", \"?\")}')
    print(f'    total_requests: {d.get(\"total_requests\", \"?\")}')
    print(f'    mesh_peers: {d.get(\"mesh_peers\", 0)}')
except Exception:
    print('    (could not parse /health)')
"
    fi
  fi

  # ── Geo-fence: assert egress is US (freebuff US relay contract) ──
  if command -v curl &>/dev/null && command -v python3 &>/dev/null; then
    echo -e "\n  ${DIM}── Geo-fence (US relay) ──${NC}"
    local country
    country=$(curl -s --max-time 5 https://ipinfo.io/country 2>/dev/null | tr -d '[:space:]' || echo "unknown")
    if [[ "${country}" == "US" ]]; then
      pass "Egress country: US ✅"
    elif [[ "${country}" == "unknown" ]]; then
      warn "Egress country: unknown (ipinfo blocked)"
    else
      fail "Egress country: ${country} — expected US (freebuff US relay contract)"
      suggest_fix "check us_relay chain or OWL_EXTRA_PROXIES tier=residential" \
        "OWL_EXTRA_PROXIES=socks5://us-residential:pass@us-proxy:1080 bash install.sh --verify-agents && curl -s https://ipinfo.io/country"
    fi
    # also check owl_security + us_relay health if available
    if command -v python3 &>/dev/null && [[ -f "/home/x2/airspace/us_relay/chain.py" ]]; then
      local chain_score
      chain_score=$(python3 -c "from us_relay.chain import chain; print(chain.stats()['tiers']['residential']['score'])" 2>/dev/null || echo "0.5")
      info "us_relay residential score: ${chain_score}"
    fi
  fi
}

# ═══════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
print_summary() {
  echo ""
  echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
  echo -e "${BOLD}  DIAGNOSTICS COMPLETE${NC}"

  if [[ ${FAILURES} -eq 0 ]]; then
    echo -e "  ${GREEN}All checks passed. No issues found.${NC}"
  else
    echo -e "  ${RED}${FAILURES} issue(s) detected.${NC}"
    echo -e "  ${YELLOW}Review the suggested fix commands above.${NC}"
  fi

  echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
  echo ""
}

# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════
main() {
  parse_args "$@"

  echo -e "${BOLD}${CYAN}"
  echo "  ╔═══════════════════════════════════════════════╗"
  echo "  ║     OWL-AGENT Diagnostics v${VERSION}              ║"
  echo "  ║     Service · Connect · Env · Resource · Tune ║"
  echo "  ╚═══════════════════════════════════════════════╝"
  echo -e "${NC}"

  if [[ "${VERBOSE}" == true ]]; then
    info "Verbose mode: ON"
  fi

  section_service_status
  section_connectivity
  section_environment
  section_resources
  section_auto_tune

  print_summary

  if [[ ${FAILURES} -gt 0 ]]; then
    exit 1
  fi
}

main "$@"
