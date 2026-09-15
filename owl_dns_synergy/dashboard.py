"""
Unified OWL Dashboard — Real-time monitoring and management TUI.

Provides:
- Real-time channel statistics display
- Key rotation status panel
- Domain routing table view
- DNS override status
- Quality score visualization
"""

import curses
import time
import sys
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from owl_dns_synergy.router import SmartChannelRouter, ChannelState
except ImportError:
    # Fallback for testing
    SmartChannelRouter = None
    ChannelState = None


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    refresh_rate: float = 1.0  # seconds
    show_header: bool = True
    show_stats: bool = True
    show_keys: bool = True
    show_domains: bool = True
    show_dns_override: bool = True
    color_mode: bool = True
    max_domain_rows: int = 20


class OWLDashboard:
    """Real-time TUI dashboard for Unified OWL monitoring."""

    def __init__(self, router: Optional[Any] = None, config: Optional[DashboardConfig] = None):
        self.router = router
        self.config = config or DashboardConfig()
        self._running = False
        self._last_update = 0
        self._stats_cache: Dict[str, Any] = {}
        self._domain_stats: Dict[str, Dict] = {}
        
        # Color pairs
        self.COLOR_GREEN = 1
        self.COLOR_YELLOW = 2
        self.COLOR_RED = 3
        self.COLOR_CYAN = 4
        self.COLOR_WHITE = 5
        self.COLOR_BOLD = 6
        self.COLOR_MAGENTA = 7

    def _init_colors(self):
        """Initialize color pairs for curses."""
        if not self.config.color_mode:
            return
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(self.COLOR_GREEN, curses.COLOR_GREEN, -1)
        curses.init_pair(self.COLOR_YELLOW, curses.COLOR_YELLOW, -1)
        curses.init_pair(self.COLOR_RED, curses.COLOR_RED, -1)
        curses.init_pair(self.COLOR_CYAN, curses.COLOR_CYAN, -1)
        curses.init_pair(self.COLOR_WHITE, curses.COLOR_WHITE, -1)
        curses.init_pair(self.COLOR_BOLD, curses.COLOR_WHITE, -1)
        curses.init_pair(self.COLOR_MAGENTA, curses.COLOR_MAGENTA, -1)

    def _get_color(self, name: str) -> int:
        """Get color pair by name."""
        if not self.config.color_mode:
            return curses.A_NORMAL
        return curses.color_pair(getattr(self, name, self.COLOR_WHITE))

    def _draw_header(self, stdscr, y: int = 0) -> int:
        """Draw dashboard header."""
        height, width = stdscr.getmaxyx()
        
        # Title
        title = "Unified OWL Dashboard v1.0.0"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        stdscr.attron(curses.A_BOLD | self._get_color("COLOR_CYAN"))
        stdscr.addstr(y, 0, title[:width-20])
        stdscr.attroff(curses.A_BOLD | self._get_color("COLOR_CYAN"))
        
        # Timestamp
        stdscr.attron(self._get_color("COLOR_YELLOW"))
        stdscr.addstr(y, width - len(timestamp) - 1, timestamp)
        stdscr.attroff(self._get_color("COLOR_YELLOW"))
        
        # Separator
        y += 1
        stdscr.addstr(y, 0, "=" * min(width-1, 78))
        return y + 2

    def _draw_channel_stats(self, stdscr, y: int) -> int:
        """Draw channel statistics section."""
        height, width = stdscr.getmaxyx()
        
        # Section header
        stdscr.attron(curses.A_BOLD | self._get_color("COLOR_GREEN"))
        stdscr.addstr(y, 0, "Channel Statistics")
        stdscr.attroff(curses.A_BOLD | self._get_color("COLOR_GREEN"))
        y += 1
        
        # Get stats from router or cache
        stats = self._stats_cache
        
        # HTTP Stats
        http_stats = stats.get("http", {})
        http_success = http_stats.get("success", 0)
        http_failure = http_stats.get("failure", 0)
        http_total = http_success + http_failure
        http_rate = (http_success / http_total * 100) if http_total > 0 else 0
        
        stdscr.addstr(y, 2, f"HTTP: ", curses.A_BOLD)
        stdscr.addstr(y, 8, f"Success: ")
        stdscr.attron(self._get_color("COLOR_GREEN"))
        stdscr.addstr(y, 17, f"{http_success}")
        stdscr.attroff(self._get_color("COLOR_GREEN"))
        stdscr.addstr(y, 25, f"Failed: ")
        stdscr.attron(self._get_color("COLOR_RED"))
        stdscr.addstr(y, 33, f"{http_failure}")
        stdscr.attroff(self._get_color("COLOR_RED"))
        stdscr.addstr(y, 41, f"Rate: ")
        color = self._get_color("COLOR_GREEN") if http_rate >= 90 else self._get_color("COLOR_YELLOW")
        stdscr.attron(color)
        stdscr.addstr(y, 47, f"{http_rate:.1f}%")
        stdscr.attroff(color)
        y += 1
        
        # DNS Stats
        dns_stats = stats.get("dns", {})
        dns_success = dns_stats.get("success", 0)
        dns_failure = dns_stats.get("failure", 0)
        dns_total = dns_success + dns_failure
        dns_rate = (dns_success / dns_total * 100) if dns_total > 0 else 0
        
        stdscr.addstr(y, 2, f"DNS:  ", curses.A_BOLD)
        stdscr.addstr(y, 8, f"Success: ")
        stdscr.attron(self._get_color("COLOR_GREEN"))
        stdscr.addstr(y, 17, f"{dns_success}")
        stdscr.attroff(self._get_color("COLOR_GREEN"))
        stdscr.addstr(y, 25, f"Failed: ")
        stdscr.attron(self._get_color("COLOR_RED"))
        stdscr.addstr(y, 33, f"{dns_failure}")
        stdscr.attroff(self._get_color("COLOR_RED"))
        stdscr.addstr(y, 41, f"Rate: ")
        color = self._get_color("COLOR_GREEN") if dns_rate >= 90 else self._get_color("COLOR_YELLOW")
        stdscr.attron(color)
        stdscr.addstr(y, 47, f"{dns_rate:.1f}%")
        stdscr.attroff(color)
        y += 1
        
        # Active Connections
        active_http = stats.get("active_http", 0)
        active_dns = stats.get("active_dns", 0)
        stdscr.addstr(y, 2, f"Active: ")
        stdscr.addstr(y, 10, f"HTTP={active_http}  DNS={active_dns}")
        y += 1
        
        return y + 1

    def _draw_key_status(self, stdscr, y: int) -> int:
        """Draw API key rotation status."""
        height, width = stdscr.getmaxyx()
        
        # Section header
        stdscr.attron(curses.A_BOLD | self._get_color("COLOR_YELLOW"))
        stdscr.addstr(y, 0, "API Key Status")
        stdscr.attroff(curses.A_BOLD | self._get_color("COLOR_YELLOW"))
        y += 1
        
        # Get key stats
        key_stats = self._stats_cache.get("key_rotator", {})
        total_keys = key_stats.get("total_keys", 0)
        available_keys = key_stats.get("available_keys", 0)
        current_index = key_stats.get("current_index", 0)
        cooldowns = key_stats.get("cooldowns", {})
        
        stdscr.addstr(y, 2, f"Total Keys: ")
        stdscr.attron(self._get_color("COLOR_CYAN"))
        stdscr.addstr(y, 14, f"{total_keys}")
        stdscr.attroff(self._get_color("COLOR_CYAN"))
        stdscr.addstr(y, 20, f"Available: ")
        color = self._get_color("COLOR_GREEN") if available_keys > 0 else self._get_color("COLOR_RED")
        stdscr.attron(color)
        stdscr.addstr(y, 31, f"{available_keys}")
        stdscr.attroff(color)
        stdscr.addstr(y, 37, f"Current: ")
        stdscr.attron(self._get_color("COLOR_MAGENTA"))
        stdscr.addstr(y, 46, f"#{current_index}")
        stdscr.attroff(self._get_color("COLOR_MAGENTA"))
        y += 1
        
        # Cooldown status
        if cooldowns:
            stdscr.addstr(y, 2, "Cooldowns: ")
            cooldown_items = [f"#{k}" for k, v in cooldowns.items() if v > time.time()]
            if cooldown_items:
                stdscr.attron(self._get_color("COLOR_RED"))
                stdscr.addstr(y, 13, ", ".join(cooldown_items))
                stdscr.attroff(self._get_color("COLOR_RED"))
            else:
                stdscr.attron(self._get_color("COLOR_GREEN"))
                stdscr.addstr(y, 13, "None")
                stdscr.attroff(self._get_color("COLOR_GREEN"))
            y += 1
        
        return y + 1

    def _draw_domain_table(self, stdscr, y: int) -> int:
        """Draw domain routing table."""
        height, width = stdscr.getmaxyx()
        
        # Section header
        stdscr.attron(curses.A_BOLD | self._get_color("COLOR_CYAN"))
        stdscr.addstr(y, 0, "Domain Routing Table")
        stdscr.attroff(curses.A_BOLD | self._get_color("COLOR_CYAN"))
        y += 1
        
        # Table header
        header = f"{'Domain':<25} {'Mode':<12} {'DNS Server':<18} {'State':<15} {'Score':<8}"
        stdscr.attron(curses.A_UNDERLINE)
        stdscr.addstr(y, 2, header[:width-4])
        stdscr.attroff(curses.A_UNDERLINE)
        y += 1
        
        # Get domain stats
        domain_stats = self._stats_cache.get("domains", {})
        
        if not domain_stats:
            stdscr.addstr(y, 2, "No domains configured")
            y += 1
        else:
            for i, (domain, stats) in enumerate(domain_stats.items()):
                if y >= height - 2:
                    break
                
                mode = stats.get("routing_mode", "direct")
                dns_server = stats.get("dns_server", "")
                dns_port = stats.get("dns_port", 53)
                force_dns = stats.get("force_dns", False)
                state = stats.get("state", "HTTP_PREFERRED")
                score = stats.get("score", 0)
                
                # Format DNS server
                dns_display = f"{dns_server}:{dns_port}" if dns_server else "-"
                
                # Color state
                if state == "HTTP_PREFERRED":
                    state_color = self._get_color("COLOR_GREEN")
                elif state == "DNS_FALLBACK":
                    state_color = self._get_color("COLOR_YELLOW")
                else:
                    state_color = self._get_color("COLOR_RED")
                
                # Draw row
                stdscr.addstr(y, 2, f"{domain[:24]:<25}")
                stdscr.addstr(y, 27, f"{mode:<12}")
                stdscr.addstr(y, 40, f"{dns_display[:17]:<18}")
                stdscr.attron(state_color)
                stdscr.addstr(y, 58, f"{state:<15}")
                stdscr.attroff(state_color)
                stdscr.addstr(y, 73, f"{score:.1f}")
                y += 1
                
                if i >= self.config.max_domain_rows - 1:
                    stdscr.addstr(y, 2, f"... and {len(domain_stats) - self.config.max_domain_rows} more")
                    y += 1
                    break
        
        return y + 1

    def _draw_dns_override(self, stdscr, y: int) -> int:
        """Draw DNS override status."""
        height, width = stdscr.getmaxyx()
        
        # Section header
        stdscr.attron(curses.A_BOLD | self._get_color("COLOR_MAGENTA"))
        stdscr.addstr(y, 0, "DNS Override Status")
        stdscr.attroff(curses.A_BOLD | self._get_color("COLOR_MAGENTA"))
        y += 1
        
        # Get DNS override stats
        domain_stats = self._stats_cache.get("domains", {})
        dns_overrides = {d: s for d, s in domain_stats.items() 
                        if s.get("dns_server") and s.get("force_dns")}
        
        if not dns_overrides:
            stdscr.addstr(y, 2, "No DNS overrides configured")
            y += 1
        else:
            for domain, stats in dns_overrides.items():
                if y >= height - 2:
                    break
                
                dns_server = stats.get("dns_server", "")
                dns_port = stats.get("dns_port", 53)
                
                stdscr.addstr(y, 2, f"{domain[:24]:<25}")
                stdscr.attron(self._get_color("COLOR_CYAN"))
                stdscr.addstr(y, 27, f"{dns_server}:{dns_port}")
                stdscr.attroff(self._get_color("COLOR_CYAN"))
                y += 1
        
        return y + 1

    def _draw_footer(self, stdscr, y: int) -> int:
        """Draw dashboard footer."""
        height, width = stdscr.getmaxyx()
        
        # Separator
        stdscr.addstr(y, 0, "=" * min(width-1, 78))
        y += 1
        
        # Help text
        help_text = "Press 'q' to quit, 'r' to refresh, 'h' for help"
        stdscr.addstr(y, 0, help_text[:width-1])
        
        return y + 1

    def _refresh_stats(self):
        """Refresh statistics from router."""
        if self.router and hasattr(self.router, 'get_channel_stats'):
            try:
                self._stats_cache = self.router.get_channel_stats()
            except Exception:
                pass

    def _draw(self, stdscr):
        """Main draw loop."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        y = 0
        
        # Draw sections
        if self.config.show_header:
            y = self._draw_header(stdscr, y)
        
        if self.config.show_stats:
            y = self._draw_channel_stats(stdscr, y)
        
        if self.config.show_keys:
            y = self._draw_key_status(stdscr, y)
        
        if self.config.show_domains:
            y = self._draw_domain_table(stdscr, y)
        
        if self.config.show_dns_override:
            y = self._draw_dns_override(stdscr, y)
        
        y = self._draw_footer(stdscr, y)
        
        stdscr.refresh()

    def run(self):
        """Run the dashboard."""
        if SmartChannelRouter is None:
            print("Error: SmartChannelRouter not available")
            return
        
        curses.wrapper(self._main)

    def _main(self, stdscr):
        """Main curses loop."""
        self._init_colors()
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(int(self.config.refresh_rate * 1000))
        
        self._running = True
        
        while self._running:
            # Refresh stats periodically
            now = time.time()
            if now - self._last_update >= self.config.refresh_rate:
                self._refresh_stats()
                self._last_update = now
            
            # Draw
            self._draw(stdscr)
            
            # Handle input
            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                self._running = False
            elif key == ord('r') or key == ord('R'):
                self._refresh_stats()
            elif key == ord('h') or key == ord('H'):
                self._show_help(stdscr)
        
    def _show_help(self, stdscr):
        """Show help screen."""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        help_lines = [
            "Unified OWL Dashboard - Help",
            "=" * 40,
            "",
            "Keyboard Shortcuts:",
            "  q/Q  - Quit dashboard",
            "  r/R  - Refresh statistics",
            "  h/H  - Show this help",
            "",
            "Sections:",
            "  Channel Statistics - HTTP/DNS success rates",
            "  API Key Status     - Key rotation and cooldowns",
            "  Domain Table       - Per-domain routing config",
            "  DNS Override       - Custom DNS server status",
            "",
            "Press any key to return..."
        ]
        
        for i, line in enumerate(help_lines):
            if i < height - 1:
                stdscr.addstr(i, 0, line[:width-1])
        
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        stdscr.nodelay(True)
        stdscr.timeout(int(self.config.refresh_rate * 1000))


def create_dashboard(router=None, **kwargs) -> OWLDashboard:
    """Create a dashboard instance."""
    config = DashboardConfig(**kwargs)
    return OWLDashboard(router=router, config=config)


def run_dashboard(router=None, **kwargs):
    """Run the dashboard with the given router."""
    dashboard = create_dashboard(router=router, **kwargs)
    dashboard.run()


# ─── CLI Entry Point ─────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified OWL Dashboard")
    parser.add_argument("--refresh", type=float, default=1.0, help="Refresh rate in seconds")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")
    parser.add_argument("--max-domains", type=int, default=20, help="Max domain rows to show")
    
    args = parser.parse_args()
    
    # Create a mock router for demo
    class MockRouter:
        def get_channel_stats(self):
            return {
                "http": {"success": 150, "failure": 5},
                "dns": {"success": 80, "failure": 12},
                "active_http": 3,
                "active_dns": 1,
                "key_rotator": {
                    "total_keys": 3,
                    "available_keys": 2,
                    "current_index": 0,
                    "cooldowns": {}
                },
                "domains": {
                    "api.example.com": {
                        "routing_mode": "direct",
                        "dns_server": "",
                        "dns_port": 53,
                        "force_dns": False,
                        "state": "HTTP_PREFERRED",
                        "score": 95.5
                    },
                    "internal.company.com": {
                        "routing_mode": "dns_tunnel",
                        "dns_server": "1.1.1.1",
                        "dns_port": 5353,
                        "force_dns": True,
                        "state": "DNS_FALLBACK",
                        "score": 88.2
                    }
                }
            }
    
    router = MockRouter()
    
    print("Starting OWL Dashboard...")
    print("Press 'q' to quit, 'h' for help")
    time.sleep(1)
    
    run_dashboard(
        router=router,
        refresh_rate=args.refresh,
        color_mode=not args.no_color,
        max_domain_rows=args.max_domains
    )
