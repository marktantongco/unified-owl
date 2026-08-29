#!/usr/bin/env python3
"""
OWL Mesh Alternatives v7.2

UDP multicast and TCP gossip mesh implementations for health broadcast.

v7.2 changes:
  - UDP mesh joins via INADDR_ANY (was binding to proxy host)
  - Stale peers pruned periodically (was unbounded memory growth)
  - TCP gossip reconnect uses jittered backoff (thundering herd)
  - Duplicate code consolidated
  - Peer identity includes sender addr for robustness
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import socket
import struct
import time
from typing import Awaitable, Callable, Optional

log = logging.getLogger("owl-mesh-alternatives")

MESH_GROUP = "239.255.255.250"  # unified, matches forward_proxy.py
DEFAULT_PORT = 42100
BROADCAST_INTERVAL = 30
PEER_TIMEOUT = 90
PRUNE_INTERVAL = 30
TCP_RECONNECT_BASE = 5
TCP_RECONNECT_MAX = 60


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _build_health_payload(
    host: str, port: int, max_connections: int,
) -> bytes:
    return json.dumps({
        "type": "owl-mesh",
        "host": host,
        "port": port,
        "max_connections": max_connections,
        "timestamp": time.time(),
    }).encode()


def _parse_health_message(data: bytes) -> Optional[dict]:
    try:
        msg = json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if msg.get("type") != "owl-mesh":
        return None
    if not msg.get("host") or not msg.get("port"):
        return None
    return msg


# ---------------------------------------------------------------------------
# UDP Multicast Mesh
# ---------------------------------------------------------------------------


class UDPMesh:
    """
    UDP multicast health broadcast + listener.

    Broadcasts node health every 30 seconds and listens for other OWL
    instances on the same multicast group/port.
    Uses asyncio.DatagramTransport — no thread-pool busy-poll.
    """

    def __init__(
        self,
        host: str,
        port: int,
        max_connections: int,
        on_peer: Callable[[dict], None] | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._max_connections = max_connections
        self._on_peer = on_peer
        self._transport: Optional[asyncio.DatagramTransport] = None
        self._broadcast_task: Optional[asyncio.Task] = None
        self._prune_task: Optional[asyncio.Task] = None
        self._peers: dict[str, dict] = {}
        self._running = False

    async def start(self) -> None:
        loop = asyncio.get_running_loop()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                pass
        sock.bind(("", self._port))
        sock.setblocking(False)

        # Join multicast group via INADDR_ANY (all interfaces).
        mreq = struct.pack(
            "4s4s",
            socket.inet_aton(MESH_GROUP),
            socket.inet_aton("0.0.0.0"),
        )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self._transport, _ = await loop.create_datagram_endpoint(
            lambda: _MeshReceiverProtocol(self._handle_message),
            sock=sock,
        )
        del sock  # ownership transferred to transport

        self._running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        self._prune_task = asyncio.create_task(self._prune_loop())
        log.info(
            "UDP mesh started: group=%s port=%d host=%s",
            MESH_GROUP, self._port, self._host,
        )

    async def stop(self) -> None:
        self._running = False
        for task in (self._broadcast_task, self._prune_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        if self._transport:
            self._transport.close()
        log.info("UDP mesh stopped")

    async def _broadcast_loop(self) -> None:
        while self._running:
            try:
                payload = _build_health_payload(
                    self._host, self._port, self._max_connections,
                )
                assert self._transport is not None
                self._transport.sendto(payload, (MESH_GROUP, self._port))
            except (OSError, RuntimeError) as exc:
                log.debug("Mesh broadcast error: %s", exc)
            await asyncio.sleep(BROADCAST_INTERVAL)

    async def _prune_loop(self) -> None:
        while self._running:
            await asyncio.sleep(PRUNE_INTERVAL)
            now = time.time()
            stale = [
                k for k, v in self._peers.items()
                if now - v["last_seen"] > PEER_TIMEOUT
            ]
            for k in stale:
                del self._peers[k]

    def _handle_message(self, data: bytes, addr: tuple[str, int]) -> None:
        msg = _parse_health_message(data)
        if not msg:
            return
        peer_host = msg["host"]
        peer_port = msg["port"]
        if peer_host == self._host and peer_port == self._port:
            return
        peer_key = f"{peer_host}:{peer_port}"
        self._peers[peer_key] = {
            "host": peer_host,
            "port": peer_port,
            "max_connections": msg.get("max_connections", 0),
            "timestamp": msg.get("timestamp", 0),
            "last_seen": time.time(),
            "sender_addr": f"{addr[0]}:{addr[1]}",
        }
        if self._on_peer:
            try:
                self._on_peer(self._peers[peer_key])
            except Exception:
                log.exception("on_peer callback raised")

    def get_peers(self) -> list[dict]:
        now = time.time()
        return [
            info for info in self._peers.values()
            if now - info["last_seen"] < PEER_TIMEOUT
        ]


class _MeshReceiverProtocol(asyncio.DatagramProtocol):
    """Minimal protocol for receiving UDP mesh broadcasts."""

    def __init__(
        self, on_message: Callable[[bytes, tuple[str, int]], None],
    ) -> None:
        self._on_message = on_message

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        pass

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        self._on_message(data, addr)

    def error_received(self, exc: Exception) -> None:
        log.debug("UDP mesh error: %s", exc)


# ---------------------------------------------------------------------------
# TCP Gossip Mesh — for cloud environments where UDP multicast is blocked
# ---------------------------------------------------------------------------


class TCPGossipMesh:
    """
    TCP gossip-based mesh for cloud/container environments.

    Seeds: comma-separated host:port pairs. Each node connects to seeds
    and exchanges health state. Reconnect uses exponential backoff with
    jitter to avoid thundering-herd reconnect storms.
    """

    def __init__(
        self,
        host: str,
        port: int,
        max_connections: int,
        seeds: list[str] | None = None,
        on_peer: Callable[[dict], None] | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._max_connections = max_connections
        self._seeds = seeds or []
        self._on_peer = on_peer
        self._peers: dict[str, dict] = {}
        self._server: Optional[asyncio.AbstractServer] = None
        self._client_tasks: dict[str, asyncio.Task] = {}
        self._prune_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        self._running = True
        self._server = await asyncio.start_server(
            self._handle_incoming, self._host, self._port,
        )
        log.info(
            "TCP gossip mesh listening on %s:%d",
            self._host, self._port,
        )

        for seed in self._seeds:
            task = asyncio.create_task(self._connect_to_seed(seed))
            self._client_tasks[seed] = task

        self._prune_task = asyncio.create_task(self._prune_loop())

    async def stop(self) -> None:
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        for task in self._client_tasks.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        if self._prune_task:
            self._prune_task.cancel()
            try:
                await self._prune_task
            except asyncio.CancelledError:
                pass
        log.info("TCP gossip mesh stopped")

    async def _connect_to_seed(self, seed: str) -> None:
        backoff = TCP_RECONNECT_BASE
        while self._running:
            try:
                host, port_s = seed.rsplit(":", 1)
                port = int(port_s)
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=10,
                )

                # Send our health immediately
                writer.write(
                    _build_health_payload(
                        self._host, self._port, self._max_connections,
                    ) + b"\n"
                )
                await writer.drain()
                backoff = TCP_RECONNECT_BASE  # reset on successful connect

                while self._running:
                    line = await asyncio.wait_for(
                        reader.readline(), timeout=60,
                    )
                    if not line:
                        break
                    self._handle_line(line)
                    # Respond with our own health (gossip exchange)
                    writer.write(
                        _build_health_payload(
                            self._host, self._port, self._max_connections,
                        ) + b"\n"
                    )
                    await writer.drain()

                writer.close()
                await writer.wait_closed()

            except (OSError, asyncio.TimeoutError, ValueError) as exc:
                log.debug("Seed %s connection error: %s", seed, exc)

            # Jittered exponential backoff
            delay = min(
                TCP_RECONNECT_MAX,
                backoff + random.uniform(0, backoff * 0.5),
            )
            await asyncio.sleep(delay)
            backoff = min(TCP_RECONNECT_MAX, backoff * 2)

    async def _handle_incoming(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        peer = writer.get_extra_info("peername")
        peer_name = f"{peer[0]}:{peer[1]}" if peer else "unknown"
        try:
            while self._running:
                line = await asyncio.wait_for(reader.readline(), timeout=60)
                if not line:
                    break
                self._handle_line(line)
                health = _build_health_payload(
                    self._host, self._port, self._max_connections,
                ) + b"\n"
                writer.write(health)
                await writer.drain()
        except (OSError, asyncio.TimeoutError):
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except OSError:
                pass

    async def _prune_loop(self) -> None:
        while self._running:
            await asyncio.sleep(PRUNE_INTERVAL)
            now = time.time()
            stale = [
                k for k, v in self._peers.items()
                if now - v["last_seen"] > PEER_TIMEOUT
            ]
            for k in stale:
                del self._peers[k]

    def _handle_line(self, line: bytes) -> None:
        msg = _parse_health_message(line)
        if not msg:
            return
        peer_host = msg["host"]
        peer_port = msg["port"]
        if peer_host == self._host and peer_port == self._port:
            return
        peer_key = f"{peer_host}:{peer_port}"
        self._peers[peer_key] = {
            "host": peer_host,
            "port": peer_port,
            "max_connections": msg.get("max_connections", 0),
            "timestamp": msg.get("timestamp", 0),
            "last_seen": time.time(),
        }
        if self._on_peer:
            try:
                self._on_peer(self._peers[peer_key])
            except Exception:
                log.exception("on_peer callback raised")

    def get_peers(self) -> list[dict]:
        now = time.time()
        return [
            info for info in self._peers.values()
            if now - info["last_seen"] < PEER_TIMEOUT
        ]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_mesh(
    mode: str,
    host: str,
    port: int,
    max_connections: int,
    seeds: list[str] | None = None,
    on_peer: Callable[[dict], None] | None = None,
) -> Optional[UDPMesh | TCPGossipMesh]:
    """
    Create the appropriate mesh implementation.

    Modes:
      'udp' — UDP multicast (default, works on LAN)
      'tcp' — TCP gossip (for cloud/container environments)
      other — returns None (mesh disabled)
    """
    if mode == "udp":
        return UDPMesh(host, port, max_connections, on_peer)
    if mode == "tcp":
        return TCPGossipMesh(host, port, max_connections, seeds, on_peer)
    return None
