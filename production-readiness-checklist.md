# Production Readiness Checklist — Complete Backend & Infrastructure
> No limits. No shortcuts. Every item you need before shipping.

---

## 1. Environment & Configuration Management

- [x] All configuration lives in environment variables — zero hardcoded values anywhere in code
- [x] `.env.example` file committed to git with every key documented and empty values
- [ ] Separate environment configs: `development`, `test`, `staging`, `production`
- [x] `APP_ENV` or `NODE_ENV` or `PYTHON_ENV` is set and respected at runtime
- [x] Config validation runs at app startup — app refuses to start if required vars are missing or invalid
- [x] Config validation includes type checking — not just presence (e.g., PORT must be a number)
- [ ] Staging environment is structurally identical to production — same OS, same runtime version, same stack
- [x] No debug mode, verbose logging, or developer tooling enabled in production config
- [x] No test credentials, test API keys, or seed data in production config
- [ ] Feature flags are config-driven, not code-deployed
- [ ] Environment-specific config files (`.env.production`, `.env.staging`) are in `.gitignore`
- [ ] App behaviour does not differ based on hostname or machine-specific assumptions
- [ ] Config hot-reloading either implemented or explicitly disabled (no partial reloads mid-request)
- [ ] All config values have documented default values and acceptable ranges
- [ ] Boolean env vars handled consistently — "true"/"1"/"yes" all mean the same thing
- [ ] Numeric env vars parsed and validated as numbers — not used as raw strings
- [ ] Config schema versioned — breaking config changes require explicit migration
- [ ] Infrastructure config (terraform vars, ansible vars) separated from app config
- [x] No `console.log(process.env)` or equivalent that dumps all env vars to logs

---

## 2. Secrets & Credentials Management

- [ ] All secrets stored in a dedicated secrets manager — Vault, Doppler, Infisical, AWS Secrets Manager, or GCP Secret Manager
- [ ] Secrets not in `.env` files on production servers if avoidable — injected at runtime by CI/CD or secret manager
- [ ] `.env` files on production servers have permissions `600` (owner read/write only)
- [ ] Every secret has a defined owner and rotation schedule
- [ ] Secret rotation is automated or has a step-by-step manual runbook
- [ ] Service-to-service secrets are different from human-facing secrets
- [ ] No shared secrets across services — each service has its own credentials
- [ ] Secrets scoped to minimum required permissions (principle of least privilege)
- [ ] Old secrets revoked immediately after rotation — not left active as backup
- [ ] Secret access is logged and audited — you know who accessed what and when
- [ ] Secrets never appear in logs, error messages, stack traces, or API responses
- [ ] Secrets never in Docker image layers — not even in intermediate build stages
- [ ] Secrets never in CI/CD pipeline YAML files — injected from CI secrets store
- [ ] Secrets never in git history — `git log` and `git blame` show nothing sensitive
- [ ] `git-secrets` or `truffleHog` or `gitleaks` runs in CI to catch accidental commits
- [ ] Leaked secret response plan documented — what to do in the first 15 minutes
- [ ] Test/staging secrets are different from production secrets — no shared keys
- [ ] API keys for third-party services documented with: service name, purpose, expiry, owner, rotation date
- [ ] Emergency access procedures defined — what if the secrets manager goes down?
- [ ] Hardware security modules (HSM) or KMS used for key material if handling payments or health data

---

## 3. Database — General

- [ ] Production DB is on a dedicated server or managed service — not colocated with the app
- [ ] Separate databases per environment — `app_production`, `app_staging`, `app_test`
- [ ] DB never directly accessible from the public internet — only from app servers via private network
- [ ] All DB connections use TLS/SSL — unencrypted connections refused
- [ ] DB superuser / root account never used by the application
- [ ] Application has its own DB user with only the permissions it needs (SELECT, INSERT, UPDATE, DELETE on specific tables — no DROP, no CREATE, no TRUNCATE in production)
- [ ] A separate DB user for migrations with elevated permissions — not the same as the app user
- [ ] Connection pooling configured and tuned (PgBouncer for PostgreSQL, SQLAlchemy pool, etc.)
- [ ] Pool size tuned based on actual load testing — not left at defaults
- [ ] Connection pool min/max documented and justified
- [ ] Pool overflow and timeout behavior defined — what happens when all connections are taken
- [ ] DB connection timeout set — app does not wait forever for a DB connection
- [ ] Query timeout set — no single query can run indefinitely
- [ ] Statement timeout set at DB level as a safety net (`statement_timeout` in PostgreSQL)
- [ ] Long-running transactions detected and killed — they hold locks and block other queries
- [ ] All tables have primary keys
- [ ] Primary keys are UUIDs (v4 or v7) or ULIDs — not sequential integers (prevents enumeration attacks and simplifies distributed inserts)
- [ ] If using sequential IDs, they are not exposed in API responses (use separate public-facing IDs)
- [ ] All foreign keys have indexes
- [ ] Composite indexes exist on multi-column query patterns
- [ ] Partial indexes used for filtered queries (e.g., `WHERE deleted_at IS NULL`)
- [ ] Index bloat monitored and `REINDEX` scheduled if needed
- [ ] No `SELECT *` in application queries — only fetch required columns
- [ ] N+1 query problems resolved — queries reviewed with an ORM query logger
- [ ] ORM lazy loading disabled or explicitly controlled in hot paths
- [ ] Bulk inserts and updates used instead of row-by-row loops
- [ ] Large result sets paginated — no queries that return unbounded rows
- [ ] Cursor-based pagination used for large datasets (not offset-based)
- [ ] All text fields have appropriate `VARCHAR(n)` limits — no unbounded `TEXT` where not needed
- [ ] Numeric precision fields use `DECIMAL`/`NUMERIC` not `FLOAT` — especially for financial data
- [ ] Currency stored as integers (cents/satoshis) not floating point
- [ ] All timestamps stored in UTC — never in local time
- [ ] `created_at` and `updated_at` columns on every table, auto-set by the DB
- [ ] Soft delete pattern (`deleted_at`) implemented if records should be recoverable
- [ ] Soft-deleted records excluded from all application queries by default
- [ ] JSON/JSONB columns indexed (GIN index for PostgreSQL) if queried
- [ ] Full-text search fields use proper FTS indexes — not `LIKE '%term%'`

---

## 4. Database — Migrations

- [ ] All schema changes managed via migrations — never manual `ALTER TABLE` in production
- [ ] Migration tool in use: Alembic (Python), Flyway, Liquibase, Prisma Migrate, golang-migrate, etc.
- [ ] Every migration has both `up` and `down` — reversible by default
- [ ] Migration files are immutable once merged to main — never edited after the fact
- [ ] Migrations run automatically on deployment or explicitly as a deploy step
- [ ] Migration status tracked in the DB itself — not just in file names
- [ ] Migrations tested on staging before production — never first run on production
- [ ] Large table migrations (adding columns, adding indexes to millions of rows) use online DDL or background jobs — not blocking ALTER TABLE
- [ ] Adding a NOT NULL column without a default is done in phases (add nullable → backfill → add constraint) — not in one migration
- [ ] Index creation uses `CREATE INDEX CONCURRENTLY` — not blocking index builds
- [ ] Migration dry-run available — `--dry-run` shows what would change
- [ ] Rollback of last migration tested at least once on staging
- [ ] Zero-downtime migration strategy documented for all breaking schema changes
- [ ] Old columns/tables kept temporarily after removing from code (two-phase removal)
- [ ] Seed data separated from migration scripts — migrations are schema only
- [ ] Migration lock prevents multiple instances from running migrations simultaneously on startup

---

## 5. Database — PostgreSQL Specific

- [ ] PostgreSQL version pinned and upgrade path documented
- [ ] `postgresql.conf` tuned for your workload — not running on defaults
- [ ] `shared_buffers` set to 25% of RAM
- [ ] `work_mem` tuned for sort/hash operations
- [ ] `effective_cache_size` set correctly
- [ ] `max_connections` set and enforced — PgBouncer used to not hit this limit
- [ ] `autovacuum` enabled and tuned — not disabled
- [ ] `VACUUM ANALYZE` runs scheduled for tables with heavy write load
- [ ] Table bloat monitored — `pg_stat_user_tables` reviewed periodically
- [ ] `pg_stat_statements` extension enabled — slow query analysis available
- [ ] `log_slow_statements` threshold set
- [ ] `wal_level` set to `replica` minimum — required for logical/physical replication
- [ ] Checkpoint tuning: `checkpoint_completion_target = 0.9`, `min_wal_size`, `max_wal_size`
- [ ] `log_checkpoints = on` to catch excessive checkpointing
- [ ] Connection SSL mode set to `verify-full` or `require` from application
- [ ] Row-level security (RLS) evaluated for multi-tenant schemas
- [ ] `pg_dump` or `pg_basebackup` used for backups — not filesystem copy while DB is running
- [ ] Replication slots monitored — unused slots cause WAL accumulation and disk fill
- [ ] Extensions audited — only necessary extensions installed
- [ ] `pg_cron` or external scheduler for DB-level maintenance tasks

---

## 6. Database — High Availability & Replication

- [ ] Primary/replica (read replica) setup in place for production
- [ ] Replication lag monitored — alert if replica falls > N seconds behind
- [ ] Read queries routed to replicas where safe — write queries always to primary
- [ ] Application handles primary failover gracefully — retries with backoff on connection failure
- [ ] Automatic failover configured (Patroni, repmgr, RDS Multi-AZ, etc.) or manual failover runbook documented with < 5 min RTO
- [ ] Failover tested in staging — never tested for the first time in an incident
- [ ] Split-brain prevention in place — fencing/STONITH configured if using automated failover
- [ ] Connection string uses a virtual IP or proxy (HAProxy, PgBouncer) that survives primary failover
- [ ] Replica promotion tested — replica can become writable primary
- [ ] WAL archiving enabled for point-in-time recovery (PITR)
- [ ] Cascading replicas documented and understood

---

## 7. Backups & Disaster Recovery

- [ ] Automated daily full DB backups
- [ ] Incremental or WAL-based backups for point-in-time recovery (PITR)
- [ ] Backup frequency matches RPO — if RPO is 1 hour, backups run hourly
- [ ] Backups encrypted at rest before leaving the source
- [ ] Backups stored in a physically separate location — different server, region, or provider
- [ ] Minimum 3-2-1 rule: 3 copies, 2 different media types, 1 offsite
- [ ] Backup retention policy defined and enforced: 7 daily, 4 weekly, 12 monthly minimum
- [ ] Old backups automatically pruned — backup storage does not grow forever
- [ ] Backup jobs monitored — alert fires if any backup job fails or does not run
- [ ] Backup file integrity verified after creation (checksum validation)
- [ ] Backup restoration tested on a schedule — minimum quarterly, monthly preferred
- [ ] Test restoration uses a separate database — does not touch production
- [ ] RTO (Recovery Time Objective) defined and documented
- [ ] RPO (Recovery Point Objective) defined and documented
- [ ] PITR tested — can restore DB to any point in the last 24 hours
- [ ] Application state beyond the DB backed up: uploaded files, config, secrets, certs
- [ ] Entire server state reproducible from IaC — not just the DB
- [ ] Disaster recovery runbook written, step-by-step, tested by at least one person
- [ ] Backup access credentials stored separately from the primary system
- [ ] Backups are immutable — cannot be overwritten or deleted accidentally
- [ ] All backup jobs run under a dedicated service account — not root
- [ ] Large DB backups verified to complete within the backup window

---

## 8. API Design & Contracts

- [ ] API versioned from day one: `/api/v1/`, `/api/v2/` — never break consumers
- [ ] API version in URL path — not just headers (easier to test, bookmark, document)
- [ ] Version deprecation policy documented — how much notice before sunsetting a version
- [ ] All endpoints return consistent response envelope: `{status, data, error, meta}`
- [ ] Success responses always use `data` field — not flat JSON
- [ ] Error responses always include: machine-readable `code`, human-readable `message`, optional `details`
- [ ] HTTP status codes used semantically correct throughout
- [ ] `200 OK` for successful reads/updates, `201 Created` for resource creation
- [ ] `400 Bad Request` for validation failures — with field-level error detail
- [ ] `401 Unauthorized` for missing/invalid auth, `403 Forbidden` for insufficient permissions
- [ ] `404 Not Found` for missing resources — never expose existence of unauthorized resources (use 403 or 404 uniformly)
- [ ] `409 Conflict` for duplicate resource creation
- [ ] `422 Unprocessable Entity` for semantically invalid input (valid JSON, invalid business logic)
- [ ] `429 Too Many Requests` for rate limiting — always with `Retry-After` header
- [ ] `500 Internal Server Error` never leaks stack traces, internal paths, or DB error messages
- [ ] Input validation on every endpoint — validated before it touches business logic
- [ ] Input validation schema defined in code (Pydantic, Joi, Zod, marshmallow) — not ad hoc
- [ ] Unknown fields rejected or stripped (no mass assignment from raw request body)
- [ ] All string inputs have max length enforced
- [ ] All numeric inputs have min/max range enforced
- [ ] Enum fields validated against allowed values
- [ ] Date/time inputs parsed and validated — invalid dates rejected with clear error
- [ ] File upload endpoints validate: MIME type, file size, file extension, magic bytes
- [ ] Pagination implemented on all list endpoints — no endpoint returns unbounded results
- [ ] Pagination uses cursor-based approach for large/fast-moving datasets
- [ ] Offset pagination limited to a max offset to prevent deep pagination abuse
- [ ] Filtering and sorting validated against an allowed list — not passed directly to DB
- [ ] Sort direction constrained to ASC/DESC — nothing else
- [ ] API returns total count separately from data array in paginated responses
- [ ] Idempotency keys supported on all state-changing endpoints (POST, DELETE)
- [ ] Long-running operations return `202 Accepted` with a job ID — not a synchronous timeout
- [ ] Job status endpoint exists: `GET /jobs/{id}` returns status, progress, result
- [ ] Webhooks supported for async result delivery where applicable
- [ ] Request body size limit enforced at reverse proxy level
- [ ] Request header size limit enforced
- [ ] Multi-part upload supported for large files — not loading entire file into memory
- [ ] Streaming responses used where appropriate (large exports, logs, etc.)
- [ ] `HEAD` and `OPTIONS` methods handled correctly on all endpoints
- [ ] OpenAPI 3.x spec generated from code (not hand-written, which drifts)
- [ ] OpenAPI spec validated against actual responses in CI
- [ ] API changelog maintained — every breaking change documented
- [ ] Backward compatibility: never remove a field, never change a field type
- [ ] Deprecation headers returned before removing a field (`Deprecation: true`, `Sunset: <date>`)
- [ ] HATEOAS links in responses where appropriate (not required, but documented if used)
- [ ] Content negotiation: `Content-Type: application/json` enforced, other types either supported or rejected with `415`
- [ ] `Accept` header respected — return appropriate format when multiple are supported
- [ ] `ETag` and `Last-Modified` headers for cacheable resources
- [ ] Conditional requests (`If-None-Match`, `If-Modified-Since`) handled correctly — return `304 Not Modified`

---

## 9. API Gateway

- [ ] API gateway in place (Kong, Traefik, AWS API Gateway, nginx with lua, custom middleware)
- [ ] Rate limiting enforced at gateway level — not just application level
- [ ] Authentication verified at gateway level for all protected routes
- [ ] Request/response logging at gateway level — captures all traffic
- [ ] Request transformation handled at gateway (header injection, path rewriting)
- [ ] Circuit breaker configured at gateway for downstream services
- [ ] Timeout configured at gateway — not relying solely on upstream timeout
- [ ] Request size limit enforced at gateway
- [ ] IP allowlisting/denylisting managed at gateway level
- [ ] Bot detection and filtering at gateway level
- [ ] Gateway itself is highly available — not a single point of failure
- [ ] Gateway config is version-controlled and deployed via CI/CD

---

## 10. Authentication

- [ ] Auth implemented via proven library — never hand-rolled crypto or JWT parsing
- [ ] Passwords hashed with bcrypt (cost ≥ 12), Argon2id, or scrypt — never MD5, SHA1, SHA256 raw
- [ ] Password hashing happens server-side — never on the client
- [ ] Minimum password requirements enforced: length ≥ 12, no maximum length that is too short
- [ ] Common password list checked on registration (HIBP API or local list of top 10k passwords)
- [ ] Password complexity rules do not make passwords weaker (no "must include symbol" that encourages predictable patterns)
- [ ] Timing-safe comparison used for password hash verification — prevents timing attacks
- [ ] JWT access tokens: short expiry (15–60 min)
- [ ] JWT refresh tokens: longer expiry (7–30 days), stored securely
- [ ] JWT secret is cryptographically random, minimum 256 bits, stored as env var
- [ ] JWT `alg` field explicitly whitelisted server-side — `alg: none` attack mitigated
- [ ] JWT audience (`aud`) and issuer (`iss`) claims validated
- [ ] JWT `kid` (key ID) claim used if rotating signing keys
- [ ] Refresh tokens rotated on every use — old refresh token invalidated immediately
- [ ] Refresh token reuse detection implemented — if old token is reused, all sessions invalidated (theft indicator)
- [ ] Refresh tokens stored hashed in DB — not plaintext
- [ ] Sessions invalidated on logout — token blacklist or short-lived tokens
- [ ] Session invalidation propagates across all app instances (Redis-backed blacklist)
- [ ] "Logout from all devices" endpoint implemented
- [ ] Auth tokens are never logged anywhere
- [ ] Auth tokens never in URL query strings — only in headers or body
- [ ] Account lockout after N failed attempts (5–10) with exponential backoff
- [ ] Account lockout is per-account, not per-IP — bypassing with different IPs still locks
- [ ] Lockout state persisted in DB — not in memory (survives restarts)
- [ ] Failed login attempts logged with: timestamp, IP, user agent, account attempted
- [ ] CAPTCHA / bot protection on login endpoint after N failures
- [ ] Email verification required before account activation
- [ ] Email verification tokens: cryptographically random, single-use, time-limited (24h)
- [ ] Password reset tokens: cryptographically random, single-use, short-lived (1h)
- [ ] Password reset does not reveal whether an email exists (prevent user enumeration)
- [ ] Magic link auth tokens: single-use, short-lived (15min), invalidated after use
- [ ] OAuth2 state parameter validated to prevent CSRF on OAuth callback
- [ ] PKCE enforced for OAuth2 public clients
- [ ] OAuth2 scopes minimal — only request what is needed
- [ ] SSO integration (SAML, OIDC) tested with both IdP-initiated and SP-initiated flows
- [ ] MFA (TOTP, WebAuthn) available for all accounts, required for admin/privileged accounts
- [ ] MFA backup codes: generated, shown once, stored hashed in DB
- [ ] MFA recovery flow documented and secure
- [ ] API key authentication: keys generated with `secrets.token_urlsafe(32)` or equivalent
- [ ] API keys stored hashed in DB — only the hash, never the raw key
- [ ] API keys shown to user only once on creation — after that, only the prefix is visible
- [ ] API key scopes defined — keys can be created with specific permission subsets
- [ ] API key expiry supported
- [ ] API key revocation immediate and propagated
- [ ] Service-to-service auth uses short-lived tokens or mTLS — not long-lived shared secrets where avoidable

---

## 11. Authorization

- [ ] Authorization checked on every endpoint — never trust the client's claimed identity
- [ ] Authorization is server-side — never based on fields the client can manipulate
- [ ] Resource ownership validated: user can only access their own resources
- [ ] Horizontal privilege escalation prevented — `GET /users/123/data` requires you to be user 123 or an admin
- [ ] Vertical privilege escalation prevented — users cannot elevate their own roles
- [ ] Role-based access control (RBAC) implemented with clearly defined roles and permissions
- [ ] Permissions enumerated and documented — no implicit permissions
- [ ] Permission changes require explicit re-authentication for sensitive operations
- [ ] Admin endpoints protected by both auth and an explicit admin role check
- [ ] Admin endpoints on a separate path prefix or subdomain
- [ ] Resource-level permissions (not just endpoint-level) — e.g., can edit THIS document, not all documents
- [ ] Indirect object references: DB IDs in requests validated against ownership — never just `WHERE id = $id`
- [ ] Batch operations validate ownership of every item in the batch
- [ ] Authorization decisions logged for audit trail
- [ ] Permission matrix documented — roles × permissions × resources

---

## 12. Session Management

- [ ] Sessions stored server-side (Redis, DB) — not in client-readable cookies where sensitive
- [ ] Session IDs are cryptographically random — not predictable or sequential
- [ ] Session ID regenerated on privilege change (login, MFA success, role change) — prevents session fixation
- [ ] Session cookies: `HttpOnly`, `Secure`, `SameSite=Strict` or `SameSite=Lax`
- [ ] Session cookie `Domain` and `Path` scoped tightly
- [ ] Session expiry: idle timeout (30 min inactivity) and absolute timeout (24h max) enforced
- [ ] Concurrent session policy defined — max sessions per user, or list of active sessions visible to user
- [ ] Session metadata stored: IP, user agent, created_at, last_active — visible to user for security review
- [ ] Suspicious session activity triggers notification to user (new login from new country/device)

---

## 13. Security — Transport Layer

- [ ] All traffic over HTTPS — HTTP redirects to HTTPS with `301 Permanent`
- [ ] TLS 1.2 minimum in production, TLS 1.3 preferred
- [ ] TLS 1.0 and TLS 1.1 explicitly disabled
- [ ] Weak cipher suites disabled — use Mozilla SSL Configuration Generator recommendations
- [ ] HTTPS certificate valid, not expired, and auto-renews (Let's Encrypt + Certbot, or managed cert)
- [ ] Certificate expiry monitored — alert 30 days before expiry
- [ ] HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- [ ] HSTS preload list submission evaluated
- [ ] Certificate Transparency (CT) logs monitored for unauthorized certs issued for your domain
- [ ] CAA (Certification Authority Authorization) DNS record set — restricts which CAs can issue for your domain
- [ ] OCSP stapling enabled on your web server
- [ ] Mutual TLS (mTLS) used for service-to-service communication inside the private network
- [ ] Certificate pinning evaluated for mobile app API clients
- [ ] DNSSEC enabled for your domain if your registrar supports it

---

## 14. Security — Application Layer (OWASP Top 10 + Beyond)

### Injection Prevention
- [ ] SQL injection: parameterized queries / ORM used everywhere — zero string interpolation in queries
- [ ] NoSQL injection: input validated before passed to NoSQL query operators
- [ ] Command injection: shell commands never constructed from user input — if unavoidable, use argument arrays not strings
- [ ] LDAP injection: LDAP queries escaped if LDAP is used
- [ ] XPath injection: XPath queries parameterized if XML is used
- [ ] Template injection (SSTI): user input never rendered directly in server-side templates
- [ ] Log injection: newline characters stripped from user input before logging

### Broken Authentication — (see Authentication section)

### Sensitive Data Exposure
- [ ] PII encrypted at rest in the database (not just disk encryption — field-level encryption)
- [ ] Sensitive fields (`password_hash`, `ssn`, `card_token`) never in API responses
- [ ] PII masked in logs — emails, phone numbers, IPs anonymized or truncated
- [ ] Error responses never include internal file paths, stack traces, or DB schema info
- [ ] HTTP response headers do not expose server version (`Server: nginx`, `X-Powered-By`)
- [ ] Debug endpoints (`/debug`, `/__admin`, `/_pprof`) protected or removed in production
- [ ] Source maps not served in production API (if relevant to your stack)

### XML External Entity (XXE)
- [ ] XML parsing has external entity resolution disabled if XML is accepted as input
- [ ] YAML parsing uses safe loader — not the default (full) loader that can execute code

### Broken Access Control — (see Authorization section)

### Security Misconfiguration
- [ ] All default credentials changed before deployment (DB passwords, admin panel passwords)
- [ ] Unnecessary features, routes, and middleware disabled in production
- [ ] Directory listing disabled on web server
- [ ] Error handling returns generic messages in production — not verbose errors
- [ ] Stack traces never returned in production HTTP responses
- [x] CORS configured for specific origins — `*` never used for authenticated endpoints
- [x] Security headers: `X-Content-Type-Options: nosniff`
- [x] Security headers: `X-Frame-Options: DENY` or `SAMEORIGIN`
- [x] Security headers: `Referrer-Policy: strict-origin-when-cross-origin`
- [x] Security headers: `Permissions-Policy` restricting unneeded browser features
- [x] Security headers: `Content-Security-Policy` defined (even if basic)
- [x] `Server` header removed or set to a generic value
- [x] `X-Powered-By` header removed
- [ ] `ETag` header does not expose inode information (nginx: `ETag off` or configure `FileEtag`)
- [ ] Admin interfaces not accessible from public internet

### Cross-Site Scripting (XSS) — Backend Contribution
- [x] All user-generated content HTML-escaped when rendered server-side
- [x] `Content-Type` header always set — prevents MIME sniffing
- [x] JSON responses served with `Content-Type: application/json` — not `text/html`
- [x] User-uploaded HTML or SVG files never served directly — sanitized or proxied through safe renderer

### Insecure Deserialization
- [x] Deserialization of untrusted data avoided entirely where possible
- [ ] If unavoidable: integrity checks on serialized data (HMAC signature)
- [x] Python `pickle` never used to deserialize user-supplied data
- [ ] Java object deserialization with untrusted data prevented
- [x] JSON deserialization typed — not generic `object` parsing

### Vulnerable Components
- [ ] Dependency vulnerability scanning in CI (`pip-audit`, `npm audit`, `trivy`, `snyk`)
- [ ] No critical or high CVE dependencies in production
- [ ] Dependency update policy defined (e.g., security patches applied within 72h)
- [ ] Transitive dependencies audited — not just direct dependencies
- [ ] Abandoned / unmaintained packages in critical paths replaced

### Insufficient Logging & Monitoring — (see Observability sections)

### CSRF Prevention
- [ ] CSRF tokens required on all state-changing requests from browser clients
- [ ] `SameSite` cookie attribute used as a CSRF defense layer
- [ ] `Origin` and `Referer` header validation as additional CSRF check on sensitive endpoints
- [ ] Double-submit cookie pattern or synchronizer token pattern implemented

### Open Redirect Prevention
- [ ] Redirect destinations validated against an allowlist — never trust a redirect URL from user input
- [ ] `?next=`, `?redirect=`, `?url=` parameters validated strictly

### Server-Side Request Forgery (SSRF)
- [ ] Outbound HTTP requests from the app do not accept URLs from user input without validation
- [ ] If user-supplied URLs are required: allowlist of permitted hosts/schemes
- [ ] Metadata endpoint (`169.254.169.254`) blocked for outbound requests from app server
- [ ] Internal network ranges (10.x, 172.16.x, 192.168.x) blocked for outbound requests
- [ ] DNS rebinding attack mitigated — DNS resolution result validated against IP allowlist

### Insecure Direct Object Reference (IDOR)
- [ ] Resource IDs in URLs are not predictable sequential integers
- [ ] Ownership/access validated on every resource fetch — not just auth

### HTTP Request Smuggling
- [ ] `Content-Length` and `Transfer-Encoding` conflict handling standardized at proxy layer
- [ ] Proxy and app server agree on how to handle ambiguous requests

### HTTP Response Splitting
- [ ] User input is never directly placed into HTTP response headers
- [ ] Newline characters stripped from any value placed in headers

### Regex Denial of Service (ReDoS)
- [ ] All regexes in input validation reviewed for catastrophic backtracking
- [ ] `validator.js`, `safe-regex`, or equivalent used to detect vulnerable patterns

### Algorithmic Complexity Attacks
- [ ] Hash tables use randomized seeds (Python does this by default, others may not)
- [ ] Sort operations on user-supplied data have size limits before sorting
- [ ] Deeply nested JSON parsing has depth limits

### Zip Bomb / XML Bomb / Billion Laughs
- [ ] Compressed file uploads decompressed to a size-limited buffer — not unlimited
- [ ] XML entity expansion depth and count limited
- [ ] Archive extraction (zip, tar) limits maximum extracted size

### Unicode and Encoding Attacks
- [ ] Input normalized to NFC Unicode form before processing and storage
- [ ] Null bytes (`\x00`) stripped from string inputs
- [ ] Homograph/IDN attacks mitigated in domain input fields (reject mixed-script inputs)
- [ ] Overlong UTF-8 sequences rejected

---

## 15. Security — Infrastructure

- [ ] OS packages up to date — unattended-upgrades or equivalent for security patches
- [ ] Unneeded services disabled and uninstalled (`netstat -tlnp` / `ss -tlnp` shows only expected ports)
- [ ] SSH: root login disabled (`PermitRootLogin no`)
- [ ] SSH: password authentication disabled (`PasswordAuthentication no`)
- [ ] SSH: key-based auth only — RSA 4096 or Ed25519 keys
- [ ] SSH: `AllowUsers` or `AllowGroups` restricts who can SSH in
- [ ] SSH: `MaxAuthTries 3` set
- [ ] SSH port changed from 22 or protected by port knocking (reduces automated scanning noise)
- [ ] SSH idle timeout set (`ClientAliveInterval`, `ClientAliveCountMax`)
- [ ] SSH host key fingerprints documented — verify on first connection
- [ ] `sudo` access restricted — only specific commands permitted via sudoers where possible
- [ ] `sudo` usage logged
- [ ] Firewall (UFW / iptables / nftables): default deny-in, allow-out
- [ ] Only ports 80, 443, and SSH open inbound — everything else blocked
- [ ] DB ports (5432, 3306, 27017) blocked from public internet — accessible only on private network
- [ ] Redis port (6379) blocked from public internet
- [ ] Internal admin ports (Flower, Bull Board, etc.) behind VPN or Tailscale
- [ ] fail2ban configured for SSH, nginx 4xx patterns, and auth endpoint abuse
- [ ] AppArmor or SELinux configured for sensitive processes
- [ ] Docker socket (`/var/run/docker.sock`) not mounted inside containers
- [ ] Kernel kept up to date — reboot scheduled after kernel updates
- [ ] `sysctl` hardening applied: IP spoofing protection, ICMP redirects disabled, SYN flood protection
- [ ] File system: `/tmp` mounted with `noexec, nosuid`
- [ ] Core dumps disabled in production (prevent memory leaks from crashed processes)
- [ ] ASLR enabled (`kernel.randomize_va_space = 2`)
- [ ] Unnecessary SUID/SGID binaries removed or restricted

---

## 16. Security — Supply Chain

- [ ] Software Bill of Materials (SBOM) generated for production deployments
- [ ] All dependencies verified against known-good checksums or signatures
- [ ] Package registry used is authoritative — no random `--index-url` overrides
- [ ] Typosquatting risk mitigated — package names reviewed for common typos
- [ ] CI/CD system access controlled — only authorized pipelines can deploy
- [ ] CI/CD runner has minimal permissions — cannot access production secrets directly
- [ ] Build artifacts are immutable — a given git SHA always produces the same artifact
- [ ] Dockerfile `FROM` base images pinned to digest, not just tag: `python:3.11-slim@sha256:...`
- [ ] Base images from official sources — not unofficial forks
- [ ] Internal package registry considered for critical dependencies (reduces external dependency)
- [ ] Third-party GitHub Actions pinned to commit SHA — not floating tags

---

## 17. Security — Audit Logging

- [ ] Audit log separate from application log — different sink, cannot be disabled by app code
- [ ] Audit log is append-only — cannot be edited or deleted by the application
- [ ] Audit log captures: who, what, when, from where, on which resource, before/after state
- [ ] Auth events logged: login success, login failure, logout, MFA events, password changes
- [ ] Authorization events logged: access denied, role changes, permission changes
- [ ] Data access logged for sensitive resources (PII access, financial records)
- [ ] Admin actions logged in full detail
- [ ] Audit log retention: minimum 1 year, longer if compliance requires
- [ ] Audit log access itself is audited
- [ ] Audit logs shipped to an immutable store (WORM storage, cloud append-only bucket)

---

## 18. Security — Penetration Testing & Scanning

- [ ] OWASP Top 10 manually reviewed before every major launch
- [ ] SAST (Static Application Security Testing) run in CI: Bandit (Python), ESLint security rules, SonarQube, Semgrep
- [ ] DAST (Dynamic Application Security Testing) run against staging: OWASP ZAP, Nuclei
- [ ] Container image scanning before deployment: Trivy, Grype, Snyk
- [ ] Infrastructure scanning: Prowler (AWS), Lynis (Linux hardening audit)
- [ ] Third-party penetration test before first public launch (even a basic one)
- [ ] Bug bounty program considered after launch
- [ ] Vulnerability disclosure policy published (security.txt at `/.well-known/security.txt`)
- [ ] CVE monitoring subscription for all major dependencies in use

---

## 19. Rate Limiting & Throttling

- [ ] Rate limiting on all public-facing endpoints
- [ ] Rate limiting on auth endpoints is significantly stricter (3–10 req/min vs 100+ for general)
- [ ] Rate limiting by IP address
- [ ] Rate limiting by authenticated user ID (per account limit)
- [ ] Rate limiting by API key (per key limit)
- [ ] Rate limiting stored in Redis or equivalent shared store — not in-process (doesn't work with multiple workers)
- [ ] Sliding window algorithm used — not fixed window (fixed window can be exploited at window boundary)
- [ ] Rate limit headers in all responses: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] `429 Too Many Requests` returns `Retry-After` header with concrete value
- [ ] Rate limit response body is informative — not just an empty 429
- [ ] Burst allowance defined — short spikes acceptable, sustained abuse is not
- [ ] Different tier limits per plan (free vs paid vs enterprise)
- [ ] Rate limit exemptions for internal services (bypass with a secret header, not IP-based)
- [ ] Global rate limit (total requests per second across all users) as a safety net
- [ ] Request queue (smoothing buffer) for endpoints that can tolerate brief queuing
- [ ] Admin endpoint for viewing and manually resetting rate limit state

---

## 20. DDoS Protection

- [ ] Traffic sits behind Cloudflare or equivalent CDN/proxy with DDoS mitigation
- [ ] Cloudflare Bot Fight Mode or equivalent bot protection enabled
- [ ] Bandwidth throttling configured on reverse proxy for abusive IPs
- [ ] Challenge page (JS challenge or CAPTCHA) served to suspicious traffic before hitting app
- [ ] Connection limits per IP at nginx/HAProxy level
- [ ] Slowloris attack mitigation: `keepalive_timeout`, `client_header_timeout`, `client_body_timeout` set
- [ ] Request flooding mitigation: `limit_req_zone` and `limit_conn_zone` in nginx
- [ ] Syn flood protection: `net.ipv4.tcp_syncookies = 1` in sysctl
- [ ] UDP flood considered if exposing UDP services (DNS, game servers)
- [ ] Anycast network considered for high-availability DNS
- [ ] Upstream bandwidth capacity matches your risk tolerance

---

## 21. Caching — Application Cache

- [ ] Caching strategy defined: cache-aside, read-through, write-through, write-behind
- [ ] Cache layer in place: Redis, Memcached, or in-process LRU (know the tradeoffs)
- [ ] Every cached key has a TTL — no indefinite cache entries
- [ ] Cache TTLs are appropriate for data freshness requirements — not copied from Stack Overflow
- [ ] Cache invalidation strategy defined per cached resource type
- [ ] Event-driven cache invalidation where possible (on write, evict related keys)
- [ ] Cache stampede / thundering herd mitigation: probabilistic early expiry or distributed lock on populate
- [ ] Cache miss fallback is safe — goes to DB and populates cache correctly
- [ ] Sensitive data (PII, auth tokens) not cached in plaintext in shared cache
- [ ] Cache data encrypted if stored in Redis (Redis ACLs, TLS, or field-level encryption)
- [ ] Cache hit/miss ratio monitored — hit rate < 80% warrants investigation
- [ ] Cache eviction policy set appropriately: `allkeys-lru`, `volatile-lru`, etc. — not default `noeviction` unless intentional
- [ ] Redis `maxmemory` set — Redis does not exhaust server RAM
- [ ] Cache can be fully flushed without requiring app restart
- [ ] Cache warming strategy for critical paths on deployment
- [ ] Negative caching (caching "not found" results) implemented where appropriate to reduce DB hammering
- [ ] Cache key design: namespace + entity type + ID — no collisions across tenants or entity types

---

## 22. Caching — CDN & Edge Cache

- [ ] CDN in place for static assets (Cloudflare, CloudFront, Fastly, Bunny.net)
- [ ] `Cache-Control` headers set correctly on all responses: `public/private`, `max-age`, `s-maxage`, `no-store`
- [ ] Cache-busting strategy for versioned assets (content hash in filename or `?v=` query string)
- [ ] `Vary` header set correctly — cache respects `Accept-Encoding`, `Accept-Language` etc.
- [ ] CDN cache purge API available and wired into deployment pipeline
- [ ] API responses that should not be cached have `Cache-Control: no-store`
- [ ] Authenticated responses have `Cache-Control: private, no-store`
- [ ] CDN never caches: auth tokens, cookies, session data, personalized content
- [ ] Origin shield / tiered caching configured to reduce origin load
- [ ] CDN logs analyzed periodically for cache hit ratio and anomalies

---

## 23. Background Jobs & Task Queues

- [ ] Task queue system in place: Celery (Python), RQ, BullMQ, Faktory, Sidekiq, pg-boss
- [ ] Workers run as completely separate processes from the API server
- [ ] Workers and the API server do not share memory or in-process state
- [ ] Each worker type (email, indexing, heavy compute) in separate queue with separate workers
- [ ] Job definition includes: task type, payload schema, retry policy, timeout, priority
- [ ] Retry logic with exponential backoff and jitter — not linear retries
- [ ] Max retry count set per job type — permanently failed jobs go to DLQ
- [ ] Dead letter queue (DLQ) exists — failed jobs are not silently dropped
- [ ] DLQ is monitored — alert on DLQ size > 0
- [ ] DLQ has a runbook — what to do with jobs that land there
- [ ] Job idempotency enforced — safe to retry the same job twice (e.g., use idempotency keys with external APIs)
- [ ] Job payload is minimal — store IDs and fetch fresh data inside the job, not stale serialized objects
- [ ] Long-running jobs have a timeout — they cannot run indefinitely
- [ ] Job progress trackable via API: `GET /jobs/{id}` returns `{status, progress, result, error}`
- [ ] Job cancellation supported for long-running jobs
- [ ] Worker crashes are auto-restarted by supervisor (systemd, supervisord, PM2, Docker restart policy)
- [ ] Worker count scaled based on queue depth — not a fixed count that is either too few or too many
- [ ] Queue depth monitored with alerts: DLQ > 0, processing queue > N, job age > X minutes
- [ ] Scheduled jobs (cron) centralized — not scattered across crontab, systemd timers, and code
- [ ] Cron job failures trigger an alert — no silent failures
- [ ] Cron job schedule in UTC — no DST surprises
- [ ] Job store (Redis, DB) backed up — lost jobs are a data loss event
- [ ] Job visibility timeout set correctly — a job claimed by a crashed worker is returned to the queue
- [ ] At-least-once delivery acknowledged — jobs designed to be idempotent accordingly
- [ ] Exactly-once delivery evaluated — use transactional outbox pattern if needed

---

## 24. Event-Driven Architecture & Message Brokers (if applicable)

- [ ] Message broker chosen with eyes open: Kafka (throughput, persistence), RabbitMQ (routing), Redis Streams (simple), NATS (lightweight)
- [ ] Topics/queues named with a clear convention: `service.entity.action` (e.g., `payments.invoice.paid`)
- [ ] Message schema versioned: producers publish schema version, consumers handle multiple versions
- [ ] Schema registry in place if using Avro or Protobuf
- [ ] Consumer groups defined — each consumer group processes messages independently
- [ ] Consumer group offset management understood — `auto.offset.reset` is intentional
- [ ] At-least-once delivery default — consumers are idempotent
- [ ] Exactly-once delivery implemented via transactional outbox pattern if critical
- [ ] Transactional outbox pattern: write event to DB in same transaction as the data change, relay reads from DB and publishes
- [ ] Message replay supported — consumers can reprocess from a historical offset
- [ ] Dead letter topic configured — messages that fail N times go there
- [ ] Message TTL set — messages do not accumulate indefinitely
- [ ] Broker replication factor ≥ 3 for production topics
- [ ] Message ordering guarantees understood — partition key chosen accordingly
- [ ] Consumer lag monitored per consumer group — alert on growing lag
- [ ] Broker disk usage monitored — retention policy prevents disk fill
- [ ] Message payload does not contain sensitive data in cleartext if broker is not fully trusted

---

## 25. Webhooks Infrastructure (if you deliver or receive them)

### Receiving Webhooks
- [ ] Webhook payload signature validated on receipt (HMAC-SHA256 or provider-specific method)
- [ ] Signature validation uses timing-safe comparison
- [ ] Raw request body used for signature validation — not parsed JSON (body parsers can alter the byte sequence)
- [ ] Webhook endpoint returns `200 OK` immediately, queues the event for async processing
- [ ] Duplicate delivery handled — idempotency key checked before processing
- [ ] Webhook events stored in DB for replay and audit
- [ ] Failed webhook processing triggers retry from the stored event — not relying on provider retry
- [ ] Webhook endpoint rate-limited by provider IP

### Delivering Webhooks
- [ ] Webhook delivery is async — does not block the request that triggered the event
- [ ] Delivery retried with exponential backoff on failure
- [ ] Delivery failure after N retries: event logged, subscriber notified, DLQ entry created
- [ ] Payload signed with HMAC before delivery — consumers can verify
- [ ] Delivery attempt log maintained: status, attempts, response codes
- [ ] Subscriber endpoint URL validated before registration (no SSRF vector)
- [ ] Subscriber endpoint must respond within timeout — no infinite waiting
- [ ] Circuit breaker: stop delivery to consistently failing endpoints after N failures
- [ ] Subscription management: list, update, delete, test webhook
- [ ] Webhook documentation published for consumers

---

## 26. Observability — Structured Logging

- [ ] Structured logging (JSON) throughout — no raw `print()` or unformatted log strings
- [ ] Every log entry has: `timestamp` (ISO 8601, UTC), `level`, `service`, `environment`, `message`
- [ ] Every request log has: `request_id`, `user_id`, `tenant_id`, `method`, `path`, `status`, `duration_ms`, `ip`
- [ ] Request ID (correlation ID) generated at entry point (API gateway or reverse proxy) and propagated through all log entries for that request
- [ ] Request ID returned in response header (`X-Request-ID`) for client-side correlation
- [ ] Log levels used correctly and consistently: DEBUG (dev only), INFO (normal operation), WARN (unexpected but handled), ERROR (failure requiring attention), FATAL (unrecoverable)
- [ ] DEBUG logs completely disabled in production — not just filtered, actually disabled
- [ ] Log context enrichment: user ID, tenant ID, request ID automatically attached to all log entries within a request scope
- [ ] Database query logs include: query duration, query plan hash (not full SQL in production — too noisy and may contain PII)
- [ ] Slow query threshold logged (queries > 1s logged as WARN)
- [ ] Outbound HTTP request logs: method, URL (path only, not query string if it contains tokens), status, duration
- [ ] Job execution logs: job type, job ID, attempt number, duration, outcome
- [ ] Errors logged with full stack trace
- [ ] Unhandled exceptions caught at the top level and logged before process exit
- [ ] Sensitive data never logged: passwords, tokens, API keys, PII, card numbers
- [ ] Log sampling considered for ultra-high-volume endpoints (log 1% of successful requests, 100% of errors)
- [ ] Logs aggregated to a central system: ELK, Grafana Loki, Datadog, Logtail, Papertrail
- [ ] Log retention: 90 days hot, 1 year cold minimum
- [ ] Log retention enforced — logs cannot fill disk
- [ ] Log rotation configured with `logrotate` or equivalent
- [ ] Access logs and error logs in separate files/streams
- [ ] Audit logs in a completely separate, immutable stream
- [ ] Log pipeline is reliable — log loss on app crash is minimized (write to stdout, let process manager capture)
- [ ] Log search and filter working in your aggregation system — not just stored, but queryable

---

## 27. Observability — Metrics

- [ ] Application-level metrics collected: request rate, error rate, latency (p50, p95, p99)
- [ ] Latency histograms per endpoint — not just averages
- [ ] Error rate broken down by error type and endpoint
- [ ] Active users / active sessions count
- [ ] Business metrics: signups/hour, payments/hour, key feature usage counts
- [ ] DB metrics: query rate, query latency, connection pool usage, pool wait time, slow queries/min
- [ ] Cache metrics: hit rate, miss rate, eviction rate, memory usage, connected clients
- [ ] Queue metrics: queue depth per queue, processing rate, DLQ depth, job age (time since enqueue)
- [ ] Worker metrics: active workers, idle workers, job processing rate, failure rate
- [ ] Infrastructure metrics: CPU usage, memory usage, disk usage, disk I/O, network I/O
- [ ] Load average vs CPU count — sustained load average > CPU count is a warning
- [ ] File descriptor usage — systems fail when FD limit is hit
- [ ] TCP connection states (TIME_WAIT accumulation can indicate misconfiguration)
- [ ] Garbage collector metrics if applicable (GC pause duration, GC frequency)
- [ ] Memory leak detection: RSS memory over time should be flat, not monotonically increasing
- [ ] Third-party API call metrics: calls/min, error rate, latency per service
- [ ] All metrics have labels: service name, environment, instance ID
- [ ] Metrics shipped to Prometheus + Grafana, Datadog, InfluxDB, or equivalent
- [ ] Metrics retention: 15 days high-resolution, 1 year downsampled
- [ ] All metrics dashboards version-controlled as code (Grafana JSON, Terraform for Datadog)

---

## 28. Observability — Distributed Tracing

- [ ] Distributed tracing instrumented (OpenTelemetry SDK preferred — vendor-neutral)
- [ ] Trace IDs propagated via `traceparent` / `tracestate` headers (W3C Trace Context standard)
- [ ] Every inbound request creates a new root span
- [ ] DB queries instrumented as child spans — slow queries visible in trace timeline
- [ ] Cache operations instrumented as child spans
- [ ] Outbound HTTP calls to external services instrumented as child spans
- [ ] Background job execution creates a new root span linked to the originating trace
- [ ] Trace sampling configured — 100% sampling for errors, 1–10% for successful requests
- [ ] Traces shipped to Jaeger, Zipkin, Tempo, Datadog APM, or equivalent
- [ ] Trace retention: 7 days minimum
- [ ] P99 traces (slowest 1%) are inspectable without special configuration

---

## 29. Observability — Alerting

- [ ] Alerts on: error rate > 1% for 5 minutes
- [ ] Alerts on: p99 latency > 2s for 5 minutes
- [ ] Alerts on: DB connection pool exhaustion (pool utilization > 90%)
- [ ] Alerts on: DB replica lag > 30 seconds
- [ ] Alerts on: disk usage > 80% (warning), > 90% (critical)
- [ ] Alerts on: memory usage > 85% for 10 minutes
- [ ] Alerts on: CPU usage > 85% for 15 minutes
- [ ] Alerts on: queue depth growing continuously for 15 minutes
- [ ] Alerts on: DLQ depth > 0
- [ ] Alerts on: any backup job failure
- [ ] Alerts on: TLS certificate expiry < 30 days
- [ ] Alerts on: health check endpoint returning non-200
- [ ] Alerts on: external dependency (third-party API) error rate > 10%
- [ ] Alerts on: cron job not running within expected window (deadman alert)
- [ ] Alerts on: app instance not emitting metrics for 5 minutes (heartbeat)
- [ ] Alerts routed to channels you will actually see: Telegram bot, email, PagerDuty, Opsgenie
- [ ] Alert severity levels defined: P1 (page immediately), P2 (notify, fix within 4h), P3 (fix next business day)
- [ ] Each alert has a runbook linked in the alert message
- [ ] Alert fatigue prevention: only actionable alerts, no informational noise alerts
- [ ] Alert deduplication and grouping configured — one incident per problem, not 1000 alerts
- [ ] Alert silencing/suppression during maintenance windows
- [ ] On-call rotation defined and documented

---

## 30. Observability — Error Tracking

- [ ] Error tracking system in place: Sentry, Rollbar, Bugsnag, GlitchTip (self-hosted), Honeybadger
- [ ] All unhandled exceptions captured automatically
- [ ] Handled errors explicitly reported with context: `Sentry.capture_exception(e, extra={...})`
- [ ] Error context includes: user ID, request ID, environment, git commit SHA, app version
- [ ] Error context never includes PII beyond user ID (no email, no name)
- [ ] Errors grouped intelligently — similar errors don't create N separate issues
- [ ] New unseen exception types trigger an immediate alert
- [ ] Error resolution workflow defined: triage → assign → fix → resolve
- [ ] Error count trending monitored — a new deployment causing error spikes is immediately visible
- [ ] Release tracking integrated — errors tagged by deployment version
- [ ] Error sampling configured for high-volume, low-severity errors
- [ ] Error tracking SDK does not have access to sensitive config

---

## 31. Observability — Dashboards

- [ ] Overview dashboard: error rate, latency, request rate, uptime — visible at a glance
- [ ] Infrastructure dashboard: CPU, memory, disk, network per instance
- [ ] DB dashboard: query rate, connection pool, slow queries, replication lag
- [ ] Cache dashboard: hit rate, memory, eviction
- [ ] Queue dashboard: depth, processing rate, DLQ, worker count
- [ ] Business metrics dashboard: revenue events, signups, active users, key conversion funnels
- [ ] On-call dashboard: open incidents, recent deploys, alert history
- [ ] All dashboards version-controlled — not manually created in the UI
- [ ] Dashboards reviewed and kept current — stale panels removed

---

## 32. Performance — Benchmarking & Load Testing

- [ ] Baseline performance numbers documented before launch: p50, p95, p99 for all critical paths
- [ ] Load tests written for critical paths: signup, login, main feature, checkout
- [ ] Load test target defined: must handle X requests/second at < Y ms p99
- [ ] Load test tool chosen: k6, Locust, Artillery, Gatling, wrk
- [ ] Soak tests run: sustain 60–70% of peak load for 30+ minutes (catches memory leaks and resource exhaustion)
- [ ] Spike tests run: sudden jump to 200% of normal load (catches cold start and autoscaling behavior)
- [ ] Stress tests run: find the breaking point — what request rate causes failures?
- [ ] Load tests run against staging — not production
- [ ] Load test results stored and compared over time — regression detection
- [ ] DB performance under load measured separately from API layer
- [ ] Memory usage under load is flat — not monotonically increasing (memory leak check)
- [ ] CPU usage under load is proportional to request rate — not unexpectedly high

---

## 33. Performance — Application Optimization

- [ ] Response payload size minimized — no unnecessary fields in API responses
- [ ] Gzip / Brotli compression enabled on all text responses (JSON, HTML, CSS, JS)
- [ ] Large payload endpoints (data exports) support streaming or chunked transfer encoding
- [ ] Efficient serialization: Pydantic, msgspec, or equivalent for Python; avoid `JSON.stringify` on huge objects in tight loops
- [ ] Avoid synchronous blocking I/O in async codebases — no `time.sleep()` in async handlers
- [ ] Database calls not made inside loops — batch or use joins
- [ ] Object creation inside hot loops minimized (GC pressure)
- [ ] Connection objects (DB, Redis) not created per-request — reuse from pool
- [ ] Expensive computations cached aggressively
- [ ] Computation offloaded to background workers when not needed in the HTTP response
- [ ] Async I/O used for I/O-bound work (HTTP calls, DB queries, file reads)
- [ ] Thread pool sized correctly for sync I/O in async frameworks
- [ ] Event loop not blocked by CPU-bound work — offloaded to a process pool or worker queue
- [ ] HTTP keep-alive enabled — not creating new TCP connections per request
- [ ] HTTP/2 enabled on the reverse proxy — multiplexing reduces connection overhead
- [ ] Internal service calls use HTTP/2 or gRPC where possible
- [ ] JSON parsing and serialization is not in the hot path for frequently-called endpoints
- [ ] Avoid deep object copying or serialization of large structures unnecessarily

---

## 34. Performance — OS & System Level Tuning

- [ ] File descriptor limit increased (`ulimit -n 65536` minimum, `/etc/security/limits.conf`)
- [ ] Process limit increased if running many workers
- [ ] `net.core.somaxconn` increased for high-connection servers (512 or 1024+)
- [ ] `net.ipv4.tcp_tw_reuse = 1` to reuse TIME_WAIT sockets
- [ ] `vm.swappiness` reduced (10 or lower) for latency-sensitive servers
- [ ] Swap configured but only as emergency buffer — not expected to be used under normal load
- [ ] Transparent huge pages (THP) disabled for Redis and Java workloads
- [ ] `net.ipv4.ip_local_port_range` expanded for high-connection-rate servers
- [ ] Disk I/O scheduler set appropriately (none/mq-deadline for SSDs)
- [ ] NTP synchronized — clock drift causes issues with JWT expiry, distributed tracing, and log correlation
- [ ] `chronyc tracking` or `timedatectl` confirms clock is synchronized

---

## 35. Infrastructure — Server Configuration

- [ ] Servers provisioned reproducibly — build script or IaC can recreate from scratch
- [ ] Server OS and version documented and pinned
- [ ] All system package versions pinned in `apt-mark hold` or equivalent
- [ ] Hostname set correctly on all servers — not generic cloud defaults
- [ ] Timezone set to UTC on all servers (`timedatectl set-timezone UTC`)
- [ ] NTP client running and synchronized
- [ ] `unattended-upgrades` configured for automatic security patches
- [ ] Reboot after kernel updates automated or scheduled in maintenance window
- [ ] Disk partitioning separates: OS, logs, DB data, application data (so log overflow doesn't kill the OS)
- [ ] Separate partitions: `/`, `/var`, `/tmp`, `/home`, `/data`
- [ ] Disk SMART monitoring enabled — `smartmontools` or cloud disk monitoring
- [ ] RAID or cloud disk replication for persistent data volumes
- [ ] System metrics agent running: Prometheus node_exporter, Datadog agent, Netdata
- [ ] Centralized logging agent running: Filebeat, Fluentd, Promtail, Vector
- [ ] Startup sequence tested: does the app come up correctly after a clean reboot?
- [ ] Server can survive graceful reboot without manual intervention
- [ ] Runbook for adding a new server to the fleet — reproducible onboarding

---

## 36. Infrastructure — Containers (Docker)

- [ ] Official base images only — not community forks
- [ ] Base images pinned to digest (`sha256:...`) not floating tag
- [ ] Multi-stage builds: build stage separate from production stage
- [ ] Production image has no build tools (`gcc`, `make`, `curl`, `git`) unless required at runtime
- [ ] Run as non-root user inside container — `USER appuser` in Dockerfile
- [ ] Filesystem is read-only at runtime where possible (`--read-only` flag)
- [ ] Only necessary files copied into image — `.dockerignore` covers: `.git`, `.env`, `node_modules`, `__pycache__`, test files
- [ ] No secrets in image layers — not even in `ENV` instructions (they appear in `docker inspect`)
- [ ] Image size minimized — smaller attack surface, faster pulls
- [ ] Image scanned for CVEs before push: Trivy, Grype, Snyk, or Docker Scout
- [ ] Image tagged with git commit SHA — not `:latest` in production
- [ ] `HEALTHCHECK` instruction defined in Dockerfile
- [ ] Resource limits defined: `--memory`, `--cpus` — container cannot starve the host
- [ ] Restart policy set: `--restart unless-stopped` or `always`
- [ ] Volumes mounted for persistent data — not stored in container layer
- [ ] Docker daemon configured with log rotation (`json-file` driver with `max-size` and `max-file`)
- [ ] Docker socket not exposed — containers do not have access to `/var/run/docker.sock` unless required
- [ ] Docker network: custom bridge network used — not default bridge (for service isolation)
- [ ] Ports not published directly on `0.0.0.0` unless explicitly needed — bind to `127.0.0.1` if reverse proxy handles external access
- [ ] Docker Compose files version-controlled
- [ ] Docker Compose production file separate from development (`docker-compose.prod.yml`)
- [ ] `docker system prune` scheduled to prevent disk fill from dangling images/volumes

---

## 37. Infrastructure — Reverse Proxy (nginx / Caddy)

- [ ] App server (gunicorn, uvicorn, node) sits behind reverse proxy — not directly exposed
- [ ] Reverse proxy handles TLS termination
- [ ] Reverse proxy handles gzip/brotli compression
- [ ] Reverse proxy handles static file serving — not the app process
- [ ] Reverse proxy buffers upstream responses — protects from slow clients
- [ ] `client_max_body_size` set — large upload attempts rejected at proxy level
- [ ] `proxy_read_timeout`, `proxy_send_timeout`, `proxy_connect_timeout` set — no infinite waits
- [ ] `keepalive_timeout` set — old connections not held open forever
- [ ] `client_header_timeout` and `client_body_timeout` set — slowloris mitigation
- [ ] `limit_req_zone` configured for rate limiting at nginx level
- [ ] `limit_conn_zone` configured for connection limiting per IP
- [ ] `server_tokens off` — nginx version not exposed in response headers
- [ ] Custom `error_page` pages for 404, 500, etc. — no default nginx error pages in production
- [ ] Access log format includes: timestamp, method, path, status, bytes, latency, upstream address, request ID
- [ ] Access log and error log locations configured (not just default)
- [ ] Proxy config version-controlled — never manually edited on server without committing
- [ ] Config tested with `nginx -t` in CI before deployment
- [ ] Reload without downtime: `nginx -s reload` / `systemctl reload nginx`

---

## 38. Infrastructure — Load Balancing

- [ ] Load balancer in place (even single-node: nginx upstream, HAProxy, or managed LB)
- [ ] Health check configured on load balancer — unhealthy backends automatically removed
- [ ] Sticky sessions evaluated — if not needed, disabled (stateless is better)
- [ ] If sticky sessions needed: cookie-based affinity (not IP-based — IP changes break it)
- [ ] Session state in shared store (Redis) so any backend can serve any request
- [ ] Load balancing algorithm chosen deliberately: round-robin, least-connections, ip_hash
- [ ] Backend drain on deployment: new instances added before old ones removed
- [ ] Graceful connection draining: in-flight requests complete before backend is removed
- [ ] Backend timeout set on load balancer — slow backends removed from rotation
- [ ] Connection pool from load balancer to backends tuned
- [ ] Load balancer itself is not a single point of failure — HA pair or managed service

---

## 39. Infrastructure — Networking

- [ ] Private network (VPC / VLAN) isolates app servers, DB servers, cache servers from each other
- [ ] Public internet access only through the reverse proxy / load balancer
- [ ] DB server has no public IP — accessible only on private network
- [ ] Redis server has no public IP
- [ ] Internal services communicate on private IPs, not via the public internet
- [ ] Network ACLs / security groups enforce private network access controls
- [ ] All outbound requests from app server proxied or firewalled — not unrestricted
- [ ] Outbound requests to third-party APIs have timeout and retry — no infinite waits
- [ ] MTU set correctly — jumbo frames enabled if network supports it (reduces segmentation overhead)
- [ ] TCP keepalive enabled for long-lived DB and cache connections
- [ ] IPv6 configured and tested if applicable (or explicitly disabled if not used)

---

## 40. Infrastructure — DNS

- [ ] DNS managed via code or a reliable provider (Cloudflare, Route53, DNSimple)
- [ ] DNS records version-controlled — changes tracked in git
- [ ] TTL reduced to 60–300 seconds 48 hours before any cutover
- [ ] TTL increased to 3600+ after stable deployment
- [ ] All DNS records documented: A, CNAME, MX, TXT, CAA, SRV
- [ ] Wildcard DNS (`*.domain.com`) only used intentionally — not by default
- [ ] DNS failover configured for critical services
- [ ] Secondary DNS provider configured — single DNS provider is a SPOF
- [ ] DNSSEC enabled if supported by registrar
- [ ] CAA records set — prevent unauthorized certificate issuance
- [ ] SPF, DKIM, DMARC records configured for email sending domains
- [ ] Reverse DNS (PTR records) set for mail sending IPs
- [ ] DNS monitoring: alert if any critical record changes unexpectedly

---

## 41. Infrastructure — Infrastructure as Code (IaC)

- [ ] All infrastructure defined in code: Terraform, Pulumi, Ansible, CloudFormation, or documented shell scripts
- [ ] IaC code version-controlled in git
- [ ] IaC changes reviewed via pull request — not applied directly from local machine
- [ ] `terraform plan` / dry-run step in CI before applying
- [ ] Infrastructure state stored remotely (Terraform state in S3 + DynamoDB lock)
- [ ] Infrastructure state backed up
- [ ] Environment parity enforced via IaC — staging and production use the same templates with different vars
- [ ] IaC secrets injected from secrets manager — not hardcoded in Terraform variables
- [ ] Unused resources cleaned up — IaC removes as well as creates
- [ ] Infrastructure drift detection configured — alert if actual state diverges from IaC
- [ ] Destroy protection enabled for production databases and critical resources
- [ ] IaC runbook for: create environment, destroy environment, scale up, scale down, failover

---

## 42. CI/CD — Pipeline Design

- [ ] All code changes via git — no direct edits to production servers
- [ ] Branch strategy defined and documented: trunk-based, gitflow, or ship-on-merge
- [ ] `main` / `master` branch is always deployable — no broken main
- [ ] PR (pull request) required for merging to main — no direct push
- [ ] PR must have at least one reviewer approval before merge (or documented exception for solo teams)
- [ ] CI runs on every push and every PR — not just on merge
- [ ] CI must pass before merge — no overriding CI failures except under documented procedure
- [ ] CI pipeline stages clearly defined: lint → test → build → scan → deploy
- [ ] CI pipeline runs in < 10 minutes for the test stage — longer pipelines lose adoption
- [ ] CI pipeline is hermetic — results do not vary based on external state
- [ ] CI secrets injected from CI secrets store — never in pipeline YAML files
- [ ] CI pipeline version-controlled in the same repo (`.github/workflows`, `.gitlab-ci.yml`, etc.)
- [ ] CI pipeline changes reviewed like code changes — not bypassed

---

## 43. CI/CD — Build

- [ ] Build is reproducible: same input → same output every time
- [ ] Build dependencies cached: Docker layer cache, pip cache, npm cache — build time is fast
- [ ] Build artifacts versioned by git SHA — `image:abc123`, not `image:latest`
- [ ] Docker images built with `--platform linux/amd64` (or target platform) explicitly
- [ ] Build step does not run migrations or touch the database
- [ ] Build artefact (Docker image, binary) is what gets deployed — not a rebuild in the deployment step
- [ ] Build logs stored and accessible for debugging

---

## 44. CI/CD — Testing in CI

- [ ] Unit tests run in CI on every push
- [ ] Integration tests run in CI on every push (against a test DB/Redis spun up in CI)
- [ ] Code coverage measured and reported — not a gate, but tracked over time
- [ ] Linting enforced: flake8/ruff (Python), ESLint (JS), golint (Go), etc.
- [ ] Type checking enforced: mypy (Python), TypeScript strict mode, etc.
- [ ] Security scanning run in CI: Bandit, npm audit, Trivy on Docker image
- [ ] Dependency license check run in CI (prevent GPL license surprises)
- [ ] API contract tests run in CI against a running staging instance
- [ ] Database migration test: run all up migrations on a clean DB, run all down migrations
- [ ] Smoke tests run post-deployment against staging before production cutover

---

## 45. CI/CD — Deployment Strategies

- [ ] Deployment is fully automated — no SSH and manual steps on the server
- [ ] Zero-downtime deployment strategy implemented: blue/green, rolling, or canary
- [ ] Blue/green: two identical environments, switch traffic between them
- [ ] Canary: route X% of traffic to new version, monitor, then fully cut over
- [ ] Rolling: replace instances one at a time — requires app to handle mixed versions simultaneously
- [ ] Deployment includes DB migration step that is backward-compatible with the old app version
- [ ] Rollback is a single command or button — not a manual process
- [ ] Rollback tested — never tested for the first time during an incident
- [ ] Rollback of DB migration is documented and tested separately
- [ ] Post-deployment smoke tests run automatically — deployment fails if smoke tests fail
- [ ] Deployment notifications sent to team channel: started, succeeded, failed
- [ ] Deployment triggers a cache warm-up for critical paths
- [ ] Every production deployment tagged in the monitoring system for correlation with alerts
- [ ] Feature flags used to decouple code deployment from feature release
- [ ] Deployment window defined — no deployments during peak traffic (unless hotfix)

---

## 46. CI/CD — Artifact Management

- [ ] Container registry in use: Docker Hub, GitHub Container Registry, ECR, or self-hosted
- [ ] Images in registry are immutable — tags do not get overwritten
- [ ] Image retention policy: keep last N releases, delete old images automatically
- [ ] Registry access controlled — only CI can push, deployment systems can pull
- [ ] Images scanned in the registry for new CVEs (not just at build time)
- [ ] Rollback artifacts retained for at least 5 releases
- [ ] Artifact signing considered (cosign, Notary) for supply chain verification

---

## 47. Testing — Unit

- [ ] Pure business logic unit tested in isolation from I/O (no DB, no HTTP in unit tests)
- [ ] Dependencies injected (not hardcoded) to make testing possible without mocking frameworks
- [ ] Test coverage tracked — target 80%+ on core business logic
- [ ] Tests run in < 30 seconds — slow tests lose adoption
- [ ] Tests are deterministic — no random failures, no time-dependent tests without time mocking
- [ ] Tests are independent — no shared mutable state between tests
- [ ] Test naming is descriptive: `test_create_invoice_fails_when_user_has_no_credit_card`
- [ ] Edge cases tested explicitly: empty inputs, null/None, maximum values, boundary conditions
- [ ] Error paths tested — not just the happy path

---

## 48. Testing — Integration

- [ ] API endpoints tested end-to-end through the HTTP stack against a real test DB
- [ ] Test DB spun up fresh for each test run — not shared between runs
- [ ] Test DB state reset between tests (transactions rolled back, or truncation)
- [ ] Auth tested: unauthenticated requests rejected, wrong role returns 403
- [ ] Input validation tested: each invalid input combination returns correct 400 error
- [ ] Pagination tested: first page, last page, out of bounds page
- [ ] Sorting and filtering tested
- [ ] Rate limiting tested: N+1 request returns 429
- [ ] DB constraints tested: duplicate creation returns 409, FK violation handled correctly
- [ ] Concurrent request tests for race conditions on shared resources

---

## 49. Testing — Contract & API

- [ ] Consumer-driven contract tests if multiple services consume your API (Pact)
- [ ] OpenAPI spec validated against actual API responses in CI
- [ ] Breaking change detection: CI fails if a new commit removes or changes an existing API field
- [ ] Postman/Insomnia collection checked into version control for manual testing reference
- [ ] API versioning tested: v1 and v2 both work simultaneously

---

## 50. Testing — Chaos Engineering

- [ ] Chaos testing considered for critical services (kill a random instance — does the app recover?)
- [ ] DB connection drop simulated — does app recover and reconnect?
- [ ] Cache (Redis) unavailability simulated — does app degrade gracefully without crashing?
- [ ] External API timeout simulated — does circuit breaker kick in?
- [ ] High latency injected (via tc or Toxiproxy) — does app handle slow dependencies gracefully?
- [ ] Disk full simulated — does app fail gracefully or corrupt data?
- [ ] Worker crash simulated — do jobs in flight get reprocessed correctly?
- [ ] Chaos results documented — failure modes understood and either fixed or accepted

---

## 51. File Storage & Uploads

- [ ] User uploads stored in object storage: S3, R2, Backblaze B2, MinIO — not on app server local disk
- [ ] App server is stateless — can be replaced without losing data
- [ ] File type validated server-side by magic bytes (not extension, not `Content-Type` from client)
- [ ] File size limit enforced server-side — before writing to disk or memory
- [ ] Filename sanitized before storage: no path traversal sequences, no special chars
- [ ] Stored filename is a UUID or content hash — not the user-supplied filename
- [ ] User-supplied filename stored in DB metadata — not in the filesystem path
- [ ] Files served via CDN pre-signed URLs — not via the app server
- [ ] Pre-signed URLs have short TTL (15 min to 1 hour) — not permanent public URLs for private files
- [ ] Private files never accessible without a valid pre-signed URL or auth check
- [ ] Public files explicitly designated — default is private
- [ ] Malware scanning on uploads considered if accepting user-generated content
- [ ] Image resizing and processing done in a background worker — not in the HTTP request handler
- [ ] Processed/resized images stored in a separate bucket/prefix from originals
- [ ] Orphaned files (files in storage with no DB reference) cleaned up by a periodic job
- [ ] Storage bucket versioning enabled — accidental overwrites/deletions recoverable
- [ ] Storage bucket replication enabled for DR (if budget allows)
- [ ] Storage bucket public access blocked at bucket policy level — no accidental public exposure
- [ ] Storage access logged — who accessed which file and when
- [ ] File download counts tracked in DB for analytics

---

## 52. Email & Notifications

- [ ] Transactional email via dedicated ESP: Postmark, Resend, Sendgrid, SES, Mailgun
- [ ] Do not send transactional email directly from VPS IP — deliverability will be poor
- [ ] SPF record published for sending domain
- [ ] DKIM configured and validated — email signed with private key
- [ ] DMARC policy published: `p=quarantine` or `p=reject` — not `p=none` in production
- [ ] DMARC `rua` (aggregate) and `ruf` (forensic) report addresses configured
- [ ] Sending domain is a subdomain of your main domain (`mail.yourdomain.com`) — isolates reputation
- [ ] PTR (reverse DNS) record set for any dedicated sending IP
- [ ] Email warm-up performed before sending high volume from a new domain/IP
- [ ] Bounce handling configured at ESP — hard bounces unsubscribed automatically
- [ ] Spam complaint handling configured — complaints trigger unsubscribe
- [ ] Unsubscribe link in all marketing/bulk emails (CAN-SPAM, GDPR requirement)
- [ ] One-click unsubscribe header: `List-Unsubscribe-Post: List-Unsubscribe=One-Click`
- [ ] Email sending is async (queued) — never blocks an API request
- [ ] Email templates version-controlled in code — not only in ESP dashboard
- [ ] Email rendering tested in common clients: Gmail, Outlook, Apple Mail
- [ ] Mobile email rendering tested — over 60% of email is read on mobile
- [ ] Transactional email logs stored: to, from, template, timestamp, delivery status — for debugging and compliance
- [ ] Push notifications (FCM, APNs) have retry logic on failure
- [ ] Push notification delivery status tracked and stored
- [ ] Notification preferences stored per user — users can opt out of specific notification types
- [ ] Notification deduplication — no duplicate notifications sent for the same event
- [ ] Critical notifications (password change, new login) not opt-out-able

---

## 53. Search Infrastructure (if applicable)

- [ ] Search implemented via dedicated system: Elasticsearch, OpenSearch, Meilisearch, Typesense, pg FTS
- [ ] `LIKE '%term%'` never used for user-facing search — uses full-text search
- [ ] Search index kept in sync with DB via CDC (Change Data Capture) or event-driven sync
- [ ] Index rebuild procedure documented and tested — can rebuild from scratch
- [ ] Search query sanitized — no injection via query DSL
- [ ] Search results paginated
- [ ] Search latency monitored — alert if P99 > threshold
- [ ] Relevance tuning documented — how is ranking determined?
- [ ] Typo tolerance / fuzzy matching configured appropriately for your domain
- [ ] Multi-language / unicode support tested
- [ ] Sensitive fields excluded from search index or masked in results

---

## 54. Data Integrity & Consistency

- [ ] Database constraints enforced at DB level: NOT NULL, UNIQUE, CHECK, FOREIGN KEY — not just in application code
- [ ] Transactions used for all multi-step writes that must succeed or fail together
- [ ] Transaction isolation level set appropriately: `READ COMMITTED` for most, `SERIALIZABLE` for critical financial operations
- [ ] Optimistic locking used for concurrent updates (version field or timestamp check on UPDATE)
- [ ] Pessimistic locking (`SELECT FOR UPDATE`) used where concurrent modification must be prevented
- [ ] Race condition on concurrent reads-then-writes to the same resource is prevented
- [ ] Check-then-act operations performed inside transactions — not `SELECT ... then UPDATE` outside a transaction
- [ ] Idempotency keys stored in DB to prevent duplicate processing of the same event
- [ ] Soft deletes maintain referential integrity — deleted records still satisfiy FK constraints
- [ ] Data archival strategy defined for records past retention period
- [ ] Data archival preserves referential integrity — archived data is consistent
- [ ] Audit trail (who changed what and when) maintained for critical entities
- [ ] Event sourcing considered for entities requiring full audit trail of every state change
- [ ] CQRS considered if read and write models have significantly different shapes
- [ ] Eventual consistency windows defined and tested — when do denormalized read models catch up?

---

## 55. Distributed Systems Patterns (if applicable)

- [ ] Circuit breaker pattern implemented for all external service calls
- [ ] Circuit breaker states: closed (normal), open (failing fast), half-open (testing recovery)
- [ ] Circuit breaker thresholds tuned per service — not the same timeout for all
- [ ] Bulkhead pattern: separate thread/connection pools for different downstream services (slow service doesn't starve fast ones)
- [ ] Timeout hierarchy: request timeout > service timeout > DB timeout — outer always longer than inner
- [ ] Timeout on all: outbound HTTP calls, DB queries, cache operations, queue operations
- [ ] Retry policy defined: which errors are retryable, how many times, with what backoff
- [ ] Idempotency enforced for all retried operations
- [ ] Retry storms prevented: jitter added to backoff, global retry budget enforced
- [ ] Backpressure implemented: producers slow down when consumers are overwhelmed
- [ ] Saga pattern for distributed transactions that span multiple services
- [ ] Compensating transactions defined for each step of a saga
- [ ] Distributed lock used when needed (Redlock or equivalent) — not ad hoc
- [ ] Clock skew between distributed nodes handled — don't assume clocks are synchronized

---

## 56. Resilience Patterns

- [ ] Graceful degradation defined: if component X fails, app does Y instead of crashing
- [ ] Fallback responses defined for every external dependency failure
- [ ] Feature flags can disable non-critical features at runtime without a deployment
- [ ] Dependency health exposed via `/health` endpoint — consuming systems know when to back off
- [ ] Retry with exponential backoff + jitter everywhere a transient failure is possible
- [ ] All external API calls have a hard timeout — no call can block a request forever
- [ ] DB connection failure handled at startup — app retries connecting instead of crashing immediately
- [ ] Redis unavailability handled — app falls back to DB or in-process cache, not crashes
- [ ] Message broker unavailability handled — events stored locally (outbox) and replayed when broker recovers
- [ ] Process crash recovery does not lose in-flight data — use durable queues, not in-memory

---

## 57. Health Checks & Readiness

- [ ] `GET /health` endpoint returns `200 OK` with a JSON body showing component status
- [ ] Health check validates live dependencies: DB, Redis, required external services
- [ ] Health check runs DB `SELECT 1` (not just checks if the pool is open)
- [ ] Health check is fast — < 500ms — it is called frequently by load balancer
- [ ] Liveness check (is the process running?) separate from readiness check (is it ready to serve traffic?)
- [ ] Readiness check fails during startup until the app is fully initialized
- [ ] Readiness check fails during graceful shutdown so load balancer stops routing
- [ ] Deep health check (`GET /health/deep`) available for debugging — not exposed to load balancer (too slow)
- [ ] Health endpoint does not authenticate — load balancer must reach it without auth
- [ ] Health endpoint rate limited separately — a flapping service doesn't exhaust rate limit budget
- [ ] Health check result cached briefly (1–2 seconds) to prevent DB overload from frequent polling

---

## 58. Graceful Shutdown

- [ ] SIGTERM signal handled — triggers graceful shutdown sequence
- [ ] On SIGTERM: stop accepting new connections, finish in-flight requests, then exit
- [ ] Shutdown timeout defined — if in-flight requests don't finish in X seconds, force exit
- [ ] Background workers: finish current job before shutdown, do not pick up new jobs
- [ ] DB connections closed cleanly on shutdown — no connection leaks in pool
- [ ] Redis connections closed cleanly on shutdown
- [ ] Queued outbound requests (email, webhooks) not lost on shutdown — persisted to DB or queue first
- [ ] Graceful shutdown tested in staging — `kill -TERM <pid>` with in-flight requests active
- [ ] Process manager (systemd, Docker) configured with `TimeoutStopSec` that matches the shutdown timeout
- [ ] Log line emitted at each stage of shutdown — observable in aggregated logs

---

## 59. Process Management

- [ ] App managed by process manager: systemd, supervisord, PM2, s6, Docker
- [ ] App auto-starts on system boot
- [ ] App auto-restarts on crash with delay (exponential backoff on repeated crashes)
- [ ] Process manager logs: app stdout/stderr captured and rotated
- [ ] Number of worker processes set based on CPU count (CPU-bound) or I/O concurrency needs (I/O-bound)
- [ ] Worker process count documented and justified — not left at default
- [ ] Each worker process has a memory limit — OOM killed worker is restarted cleanly
- [ ] Zombie process prevention: child processes are reaped properly (Docker: use `--init` or tini)
- [ ] Process memory usage monitored over time — monotonically increasing RSS indicates leak
- [ ] Periodic worker restart configured as temporary mitigation for known small leaks

---

## 60. Feature Flags

- [ ] Feature flag system in place: LaunchDarkly, Unleash (self-hosted), GrowthBook, or simple DB/Redis-backed flags
- [ ] New features deployed behind feature flags — deployed code can be invisible until flag is on
- [ ] Feature flags checked with low latency (cached, not a DB query per request)
- [ ] Feature flag state change does not require a deployment
- [ ] Feature flags used for: gradual rollout, A/B testing, kill switches, canary releases
- [ ] Kill switches defined for every high-risk feature — can be turned off in < 1 minute
- [ ] Feature flag evaluation logged — you know who saw which variant
- [ ] Stale feature flags (fully rolled out or permanently off) cleaned up periodically
- [ ] Feature flag SDK failure handled — defaults defined for every flag (default to off for new features)

---

## 61. Data Privacy & Compliance — GDPR

- [ ] Data Processing Register maintained — inventory of all personal data, purpose, legal basis, retention period
- [ ] Legal basis defined for every data processing activity: consent, contract, legitimate interest, etc.
- [ ] Privacy policy published, accessible, and up to date
- [ ] Terms of service published and up to date
- [ ] Cookie consent mechanism implemented (if operating cookies in EU)
- [ ] GDPR consent captured with timestamp, version of policy accepted, and channel
- [ ] Right to access: `GET /me/data` exports all user data in machine-readable format
- [ ] Right to erasure: `DELETE /me` deletes all personal data — or documents why retention is legally required
- [ ] Right to portability: data export in standard format (JSON, CSV)
- [ ] Right to rectification: user can update their personal data
- [ ] Data minimization: collect only what is necessary for the stated purpose
- [ ] Storage limitation: personal data automatically purged after retention period
- [ ] Data retention periods defined per data type and enforced by automated job
- [ ] Data breach notification plan: 72 hours to notify supervisory authority under GDPR
- [ ] Data breach internal escalation: who to notify and when
- [ ] Data processor agreements (DPA) signed with all third-party services that process user data
- [ ] PII not stored in third-party services unless DPA is in place
- [ ] Data transferred outside EU only to adequate jurisdictions or under Standard Contractual Clauses
- [ ] DPO (Data Protection Officer) appointed if required by your processing volume
- [ ] Pseudonymization used where possible — reduce risk of data breach impact
- [ ] Test/staging databases use anonymized data — not a copy of production PII

---

## 62. Data Privacy & Compliance — General

- [ ] CCPA compliance evaluated if serving California residents
- [ ] PIPEDA compliance evaluated if serving Canadian users
- [ ] LGPD compliance evaluated if serving Brazilian users
- [ ] Applicable laws documented per target market
- [ ] Payment data: no raw card numbers stored — tokenized via payment processor (Stripe, Paystack, etc.)
- [ ] PCI DSS SAQ level determined — at minimum SAQ A if using hosted payment forms
- [ ] HIPAA compliance evaluated if handling health data
- [ ] Data classification defined: public, internal, confidential, restricted
- [ ] Data handling policies per classification documented
- [ ] Retention and deletion policies per classification enforced

---

## 63. Documentation

- [ ] README: what the project does, tech stack, prerequisites, how to run locally, environment variables, how to run tests, how to deploy
- [ ] Architecture decision records (ADRs) for significant technical choices
- [ ] Architecture diagram: services, data flows, external dependencies (updated, not a relic)
- [ ] API documentation: auto-generated from OpenAPI spec and published
- [ ] Data model / ERD: all tables, columns, relationships documented
- [ ] Service dependency map: what external services does this system call?
- [ ] Sequence diagrams for complex flows: auth, payment, async job lifecycle
- [ ] Runbooks: deployment, rollback, DB restore, scaling, incident response
- [ ] On-call escalation contacts documented: who to call for what
- [ ] CHANGELOG.md or release notes maintained
- [ ] Glossary of domain-specific terms — new team members can get up to speed
- [ ] Code comments on non-obvious sections — not redundant with code, but explaining why
- [ ] All documentation in version control — no orphaned Google Docs that go stale

---

## 64. Runbooks & Incident Management

- [ ] Runbook exists for every alert — alert without runbook is noise
- [ ] Runbook content: symptom → diagnosis steps → resolution steps → escalation path
- [ ] Runbooks stored in version control, not a wiki that might be unavailable during an incident
- [ ] Incident severity levels defined: SEV1 (all users affected), SEV2 (partial), SEV3 (minor degradation)
- [ ] Incident response process documented: detection → triage → communicate → resolve → post-mortem
- [ ] Incident communication template: status page update, internal channel message
- [ ] Status page configured: Statuspage.io, Better Uptime, or self-hosted
- [ ] Status page updated within 5 minutes of confirming an incident
- [ ] Post-mortem required for SEV1 and SEV2 — blameless, focused on system improvement
- [ ] Post-mortem template: timeline, root cause, impact, action items, owners, deadlines
- [ ] Action items from post-mortems tracked to completion — not just written and forgotten
- [ ] War room channel defined for incidents — not in the general engineering channel

---

## 65. SLA / SLO / SLI & Error Budgets

- [ ] SLI (Service Level Indicators) defined: latency, error rate, uptime are the three universal SLIs
- [ ] SLO (Service Level Objectives) defined: "99.9% of requests under 500ms over 30 days"
- [ ] SLA (Service Level Agreement) defined (external commitment, if applicable) — SLO is internal target
- [ ] Error budget calculated from SLO: 99.9% uptime = 43 minutes downtime budget per month
- [ ] Error budget consumption tracked in real time
- [ ] Policy defined for error budget exhaustion: freeze risky deployments, focus on reliability
- [ ] Error budget reporting in team weekly review

---

## 66. Capacity Planning

- [ ] Current resource utilization baselined: CPU, memory, disk, DB connections, network
- [ ] Growth projection: expected user/traffic growth over next 6 months
- [ ] Resource headroom maintained: no resource should be at > 70% under normal load
- [ ] Scaling triggers defined: when to add more capacity (manually or automatically)
- [ ] Horizontal scaling tested: adding an instance works without manual intervention
- [ ] DB scaling plan: when read replicas become necessary, when sharding becomes necessary
- [ ] Disk growth rate monitored: when will disk fill?
- [ ] Log and metric storage growth rate monitored and controlled
- [ ] Dependency rate limits documented: third-party APIs have limits, plan accordingly
- [ ] Cost projection as volume grows — no surprise bills

---

## 67. Cost Management

- [ ] Infrastructure spend monitored and alerted on anomaly (unexpected 2x spike)
- [ ] Budget alerts configured at cloud provider level
- [ ] Reserved instances / committed use purchased for predictable baseline workloads
- [ ] Idle resources identified and shut down: unused DBs, old snapshots, orphaned volumes
- [ ] Data transfer costs understood — inter-region data transfer is expensive at scale
- [ ] Log and metric retention costs bounded — retention policies limit storage growth
- [ ] Object storage lifecycle policies: archive to cold storage after 90 days, delete after 365 days (if appropriate)
- [ ] DB instance sized correctly — oversized instances waste money
- [ ] Egress costs reviewed — CDN reduces egress from origin
- [ ] Third-party service costs reviewed quarterly — unused seats, deprecated plans
- [ ] Cost per customer calculated and trending in the right direction
- [ ] Build and test infrastructure costs minimized: cache layers, parallelization, ephemeral runners

---

## 68. Dependency & Package Management

- [ ] All dependencies pinned to exact versions in production lock files
- [ ] Lock files committed to git: `requirements.txt`, `poetry.lock`, `package-lock.json`, `go.sum`
- [ ] Lock file is the authoritative dependency spec — not regenerated on deploy
- [ ] `pip install` / `npm ci` used in deployment (not `npm install` which can diverge from lock)
- [ ] Unused dependencies removed — smaller attack surface, faster installs
- [ ] Direct vs transitive dependencies understood — you know what each direct dependency pulls in
- [ ] License compliance checked: GPL libraries avoided in proprietary commercial products
- [ ] Dependency update policy defined: patch (within 48h for security), minor (weekly), major (planned)
- [ ] Dependabot or Renovate configured for automated dependency update PRs
- [ ] Vendored dependencies (in-repo copies) clearly marked and update process documented

---

## 69. Date, Time & Timezone Handling

- [ ] All timestamps stored in UTC in the database — never local time
- [ ] App servers run in UTC timezone — `TZ=UTC` set in OS and Docker
- [ ] User-facing times converted to user's local timezone at display time — not stored per-user timezone
- [ ] ISO 8601 format used for all date/time in API: `2024-01-15T14:30:00Z`
- [ ] Unix timestamps (epoch) used for machine-to-machine date comparison — not strings
- [ ] DST transitions handled correctly — no appointments that disappear or duplicate at DST change
- [ ] Leap year edge cases tested: Feb 29 accepted for inputs that allow it
- [ ] Leap second handling understood (most systems skip/smear — be aware of your stack's behavior)
- [ ] Scheduling relative to a specific timezone uses a proper timezone library — not a fixed UTC offset
- [ ] Date-only fields stored as `DATE` type — not as a `TIMESTAMP` at midnight UTC (causes timezone confusion)
- [ ] Age / duration calculations use proper date arithmetic — not naive subtraction
- [ ] Expiry calculations use actual calendar math — not 86400 seconds per day (DST breaks this)

---

## 70. Internationalization (i18n) Backend

- [ ] All user-facing strings in a translation file — not hardcoded in source
- [ ] `Accept-Language` header respected where appropriate
- [ ] Locale-specific formatting handled server-side: numbers, currencies, dates
- [ ] Currency display locale-aware: `$1,234.56` vs `1.234,56 €`
- [ ] RTL language support considered in API responses if applicable
- [ ] Collation and sorting locale-aware in DB queries involving text
- [ ] Character encoding: UTF-8 everywhere — DB, files, HTTP responses, emails
- [ ] Database collation set to `utf8mb4_unicode_ci` (MySQL) or `utf8` with proper collation (PostgreSQL)
- [ ] Email templates localized for each supported language

---

## 71. WebSocket / Real-time (if applicable)

- [ ] WebSocket connections authenticated on handshake — not just at connection time
- [ ] WebSocket connections have per-connection rate limiting
- [ ] Connection limits per user enforced — no user holds thousands of connections
- [ ] WebSocket server behind a reverse proxy that supports WebSocket upgrade (nginx: `proxy_http_version 1.1`, `Upgrade`, `Connection` headers)
- [ ] Heartbeat / ping-pong implemented — detect and clean up dead connections
- [ ] Connection backpressure implemented — slow consumers don't exhaust server memory
- [ ] WebSocket horizontal scaling handled — connection state in Redis pub/sub or similar (sticky sessions as fallback)
- [ ] Reconnection logic implemented on the client protocol side
- [ ] WebSocket upgrade endpoint protected against CSRF (check `Origin` header)
- [ ] Long-polling fallback defined if WebSocket is unavailable

---

## 72. External API Integration Patterns

- [ ] All external API calls have a timeout configured — per-request timeout
- [ ] Timeout is appropriate for the API's expected latency + buffer — not copied from Stack Overflow
- [ ] Retry with exponential backoff + jitter for transient errors (5xx, network timeout)
- [ ] Retry only on idempotent calls or with idempotency keys for non-idempotent calls
- [ ] Non-retryable errors (4xx) fail immediately — no retry loop on 400/401/403/404
- [ ] Circuit breaker wraps every external service client
- [ ] Circuit breaker open threshold tuned per service — a slow service trips the breaker
- [ ] Fallback behavior defined: what happens when this external service is unavailable?
- [ ] External API keys rotated if service notifies of breach
- [ ] External API version pinned — not using `latest` or `v1` that may be deprecated
- [ ] API changes monitored via service provider changelog or RSS
- [ ] Webhook payloads from providers validated via signature
- [ ] Idempotency key sent on every payment / mutation API call to prevent double-charges
- [ ] External API mock server used in tests — not real API calls in CI
- [ ] External API cost monitored — per-call billing can surprise you at scale

---

## 73. Multi-Tenancy (if applicable)

- [ ] Tenancy model chosen deliberately: silo (separate DB), bridge (separate schema), pool (shared schema with tenant_id)
- [ ] Every table in pool model has `tenant_id` column — no exceptions
- [ ] All queries filtered by `tenant_id` — cannot be bypassed by the application
- [ ] `tenant_id` never accepted from user input — always derived from the authenticated session
- [ ] Cross-tenant data access is structurally impossible — not just tested
- [ ] Row-level security (RLS) in PostgreSQL used as an additional enforcement layer
- [ ] Tenant onboarding is automated — no manual DB changes per new tenant
- [ ] Tenant offboarding (data export + deletion) is automated
- [ ] Resource quotas per tenant: API rate limits, storage, seats, compute
- [ ] Tenant billing tied to resource usage
- [ ] "Noisy neighbor" mitigation: one tenant's heavy usage cannot degrade another's experience
- [ ] Tenant-specific config supported without code changes

---

## 74. Change Management

- [ ] Every production change tracked: what changed, who changed it, when, why
- [ ] Change review process for high-risk changes (DB migrations, infra changes, schema changes)
- [ ] Maintenance windows defined for high-risk changes
- [ ] Production change requires at least one reviewer who is not the author
- [ ] Rollback procedure documented for every type of change
- [ ] Change communications sent to affected users/stakeholders before maintenance windows
- [ ] Emergency change process defined — speed vs rigor tradeoff documented
- [ ] Change log maintained and accessible to all engineers

---

## 75. Final Launch Gate Checklist

- [ ] All P1 security issues resolved
- [ ] Staging mirrors production — smoke tests green on staging
- [ ] Load test run — system handles 2× expected peak load
- [ ] Backup restoration tested in last 30 days
- [ ] Monitoring dashboards operational — all metrics flowing
- [ ] Alerting tested — a test alert was actually delivered to the on-call channel
- [ ] Rollback plan documented and tested
- [ ] Error tracking operational — a test exception appears in Sentry/equivalent
- [ ] All secrets rotated from dev values to production values
- [ ] All API keys for third-party services are production keys — not sandbox
- [ ] Payment integration in production mode — not test mode
- [ ] Email in production mode — not sandbox
- [ ] DNS TTL reduced 48h before cutover
- [ ] Status page configured and tested
- [ ] On-call rotation active — someone is responsible for the next 24h
- [ ] Launch runbook written — step-by-step for the day
- [ ] Communication plan ready — what to post on status page if something breaks
- [ ] Legal review complete: privacy policy, terms of service, cookie policy current
- [ ] Monitoring dashboards open during launch
- [ ] War room / incident channel active during launch window
- [ ] Post-launch review scheduled for 24h and 72h after launch

---

*Total: 700+ items across 75 categories*
*Priority if resources are limited: Security → Backups → Observability (Logging + Alerting) → Health Checks + Graceful Shutdown → CI/CD → Everything else*
