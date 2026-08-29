# Persistent Memory

## Context
Use this skill when you need to persist state, configuration, billing data, or any key-value information across proxy restarts, agent sessions, or process boundaries. Essential for the OWL-AGENT billing system to maintain quota tracking and fingerprint state.

**Trigger phrases:** "persist state," "save billing data," "cross-session memory," "quota tracking," "key-value store," "state persistence."

## Purpose
Provides a durable key-value store with TTL, optimistic concurrency control, and snapshot capabilities. Acts as the memory backbone for the OWL-AGENT ecosystem — ensuring that billing quotas, rate limit counters, fingerprint caches, and configuration survive process restarts.

## Use-Case
- Persist billing quota usage across Python proxy restarts
- Store fingerprint rotation state so sessions resume with correct fingerprints
- Save rate limit counters so in-memory fallback can recover after crash
- Cross-session token and quota state for MCP agent orchestration
- Configuration snapshots for rollback after failed deployments

## Misconception
That Redis alone is sufficient for persistence. Redis persistence (RDB/AOF) is a backup mechanism, not a programmatic KV store with TTL and OCC. The persistent-memory skill provides application-level semantics that Redis does not: atomic compare-and-swap, structured snapshots, and per-key TTL with callbacks.

## Conspiracy
Persistent memory slows things down. Reality: File-based persistence (SQLite or JSON) adds ~1ms per write for billing state updates. This is negligible compared to the 200-2000ms latency of the upstream API call. In-memory cache with async disk writes means zero impact on the hot path.

## Mostly Overlooked
Snapshot capability. Most people think of persistent memory as just "save and load." The snapshot feature allows point-in-time recovery — if a billing cycle goes wrong, you can restore to the last known good state. This is critical for production billing systems.

## Contradictions
- Durability requires disk writes, but disk I/O is slower than memory
- Cross-process sharing requires external storage (Redis/file), but adds complexity
- TTL auto-expiry is convenient but can lose important billing records if misconfigured

## Compatible With
- **api-gateway-skill**: Stores billing state, rate limit counters, fingerprint caches
- **mcp-builder**: Exposes stored billing data as MCP resources for agent queries
- **deployment-manager**: Manages snapshot files during deployments
- **combined-proxy-billing**: Provides the data layer that the billing backend reads/writes

## Not Compatible With
- Ephemeral container deployments without volume mounts (data lost on restart)
- Multiple writers to the same SQLite file without WAL mode

## Stackable
Yes — designed to be the foundation layer that other skills build on.

## Not Stackable With
Another persistent-memory instance on the same database file. Use separate namespaces or databases.

## Stackable Best Combined To
- persistent-memory + api-gateway-skill = Stateful billing gateway
- persistent-memory + mcp-builder = Queryable billing history
- persistent-memory + deployment-manager = Rollback-capable deployments

## Stackable Worst Combined To
- persistent-memory + another-ORM = Schema conflicts, dual-write issues

## OWL-AGENT v5.0 Integration
In v5.0, the Python proxy's FingerprintRotator cache is in-memory by default but can be backed by persistent-memory for cross-restart continuity. The secrets.json file serves as the simplest form of persistent memory for configuration. For production, the billing middleware should write quota snapshots to persistent-memory every 60 seconds. Key data paths:
- ~/.owl-agent/config/secrets.json — configuration and tokens
- ~/.owl-agent/data/fingerprints.db — fingerprint rotation state (SQLite)
- ~/.owl-agent/data/billing_snapshots/ — point-in-time billing state
- ~/.owl-agent/cache/http/ — HTTP response cache

## Instructions
1. Initialize the KV store with `pmem.py --db ~/.owl-agent/data/state.db`
2. Set TTL for billing records: `pmem.py set billing:quota:{user} --ttl 86400 --value '{"used": 0, "limit": 1000}'`
3. Create snapshots before billing cycles: `pmem.py snapshot --tag pre-cycle`
4. Expose data to MCP: `pmem.py serve-mcp --port 4625`
