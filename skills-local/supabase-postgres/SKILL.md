# Supabase Postgres Best Practices

---
name: supabase-postgres-best-practices
description: Postgres performance optimization and best practices from Supabase. Use this skill when writing, reviewing, or optimizing Postgres queries, schema designs, or database configurations.
metadata:
  author: supabase
  version: "1.1.1"
  organization: Supabase
---

# Supabase Postgres Best Practices

Comprehensive performance optimization guide for Postgres, maintained by Supabase. Contains rules across 8 categories, prioritized by impact to guide automated query optimization and schema design.

## When to Apply

Reference these guidelines when:
- Writing SQL queries or designing schemas
- Implementing indexes or query optimization
- Reviewing database performance issues
- Configuring connection pooling or scaling
- Optimizing for Postgres-specific features
- Working with Row-Level Security (RLS)

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Query Performance | CRITICAL | `query-` |
| 2 | Connection Management | CRITICAL | `conn-` |
| 3 | Security & RLS | CRITICAL | `security-` |
| 4 | Schema Design | HIGH | `schema-` |
| 5 | Concurrency & Locking | MEDIUM-HIGH | `lock-` |
| 6 | Data Access Patterns | MEDIUM | `data-` |
| 7 | Monitoring & Diagnostics | LOW-MEDIUM | `monitor-` |
| 8 | Advanced Features | LOW | `advanced-` |

## Key Rules

### Query Performance (CRITICAL)
- Always use indexes for columns in WHERE, JOIN, and ORDER BY clauses
- Use partial indexes for filtered queries
- Avoid SELECT * — specify only needed columns
- Use EXPLAIN ANALYZE to verify query plans
- Prefer EXISTS over IN for subqueries

### Connection Management (CRITICAL)
- Use connection pooling (PgBouncer or Supavisor)
- Set appropriate pool sizes based on available connections
- Close connections properly in application code
- Monitor connection usage and leaks

### Security & RLS (CRITICAL)
- Enable RLS on all public-facing tables
- Use policy-based access control
- Never expose service_role key to client
- Validate all inputs server-side

### Schema Design (HIGH)
- Choose appropriate data types (smallest that fits)
- Use CHECK constraints for data integrity
- Normalize to 3NF, denormalize for read performance
- Plan partitioning strategy for large tables

### Concurrency & Locking (MEDIUM-HIGH)
- Use advisory locks for application-level coordination
- Avoid long-running transactions
- Use NOWAIT or SKIP LOCKED for non-blocking operations
- Monitor lock waits and deadlocks

### Data Access Patterns (MEDIUM)
- Batch inserts instead of single-row inserts
- Use UPSERT (INSERT ... ON CONFLICT) for idempotent operations
- Implement cursor-based pagination for large result sets
- Use materialized views for expensive aggregations

### Monitoring & Diagnostics (LOW-MEDIUM)
- Monitor pg_stat_activity for active queries
- Track slow queries with pg_stat_statements
- Set up alerts for connection count thresholds
- Monitor bloat and run VACUUM strategically

### Advanced Features (LOW)
- Use JSONB for semi-structured data
- Implement full-text search with tsvector/tsquery
- Use LISTEN/NOTIFY for real-time notifications
- Leverage CTEs for complex queries

## References

- https://www.postgresql.org/docs/current/
- https://supabase.com/docs
- https://wiki.postgresql.org/wiki/Performance_Optimization
- https://supabase.com/docs/guides/database/overview
- https://supabase.com/docs/guides/auth/row-level-security
