# PROJECT_JOURNAL.md

# Remnawave Subscription Merge — Project Journal

> This file is the immutable, append-only project history log and authoritative chronological record.
>
> Old entries must never be deleted, shortened, rewritten, reordered, or silently corrected. Corrections are recorded as new dated entries at the end.

## 0. Mandatory project working rules

### Rule 1 — Study the journal before work
Before beginning any work, study this document entirely, or all currently available sections, together with the relevant repository context.

### Rule 2 — Append-only history
Do not delete, shorten, rewrite, reorder, or otherwise alter old journal records. This is a historical log, not a current-state document.

### Rule 3 — New dated entry for every stage
All new work must be added to the end as a separate dated journal entry.

### Rule 4 — Record complete development history
Record, as applicable: completed work, changes, decisions, reasons for important decisions, fixes, checks, tests, errors, failed approaches, unfinished work, limitations, risks, plans, changed files, and commit SHA.

### Rule 5 — Corrections are new history
If a previous decision or implementation is corrected, preserve the original entry and add a new dated entry explaining what changed and why.

### Rule 6 — Never claim unverified work
Do not claim a feature, fix, test, deployment, migration, or other task is complete unless it was actually performed and verified. Clearly distinguish planned, partial, untested, and completed work.

### Rule 7 — Update the journal before completing each stage
Before declaring a stage complete, update this journal with the actual results.

### Rule 8 — End each stage with journal and commit information
Report what was added to the journal, which commit contains it, changed files, and stage status. If no commit exists, say so.

### Rule 9 — Missing history must be investigated, not invented
If history is incomplete, inspect GitHub and available project context. Do not invent historical decisions. Record uncertainty when a fact cannot be verified.

### Rule 10 — Preserve previous work
Do not casually destroy or rewrite previous project work. Inspect existing code/history before modifying it. Intentional removals, migrations, rollbacks, and replacements must be documented.

### Rule 11 — Explicitly confirm preservation
At the end of every stage explicitly tell the user:
«старые изменения не тронуты, новые внесены.»

### Rule 12 — Work in large completed stages
Work in large meaningful stages / huge steps / semimile steps rather than unnecessary micro-steps. Accomplish as much coherent work as safely possible and verify between large blocks.

### Rule 13 — Do not ask unnecessary “continue?” questions
When the next work is clear, proceed autonomously through the next large stage. Do not repeatedly stop after tiny actions.

### Rule 14 — Verify between large blocks
Use appropriate repository, unit/integration, lint/type, build, Docker/compose, API, configuration, runtime/log, and Git checks as applicable. A successful edit is not the same as a verified implementation.

### Rule 15 — Security and secrets
Never commit passwords, API tokens, webhook secrets, private keys, or other credentials. Use environment/configuration mechanisms. If a secret is exposed, document remediation without recording the secret.

### Rule 16 — Safe infrastructure changes
For live Remnawave integration, prefer non-destructive changes, back up configuration when appropriate, avoid unnecessary database changes and destructive Docker operations, do not remove production volumes/data unless explicitly required and verified, and verify after deployment.

### Rule 17 — Scope discipline
This project is a minimal subscription-merging middleware for the A2 use case. Do not silently expand it into a full middleware platform. Unrelated admin UI, HWID, grace-squad, branding, unrelated webhook systems, unrelated analytics/billing, and modification of Remnawave itself are outside the initial core scope.

### Rule 18 — A2 means per-user secondary subscriptions
The target is not one shared secondary subscription. Each user has an independent hidden personal subscription and quota.

Example:
User A: main unlimited + hidden 100 GB.
User B: main unlimited + hidden 100 GB.

A single fixed secondary subscription shared by multiple users is not A2 because its quota would be shared.

### Rule 19 — One visible plan, one client-facing subscription
The user should see one visible/main plan. The hidden secondary subscription is an internal implementation detail. The client receives one merged subscription URL/body.

### Rule 20 — Deterministic mapping
The middleware needs a deterministic and testable mapping between the main and hidden subscription. Initial design candidate:
main username = <main_username>
hidden username = <main_username>_addsub
This is an initial design, not a claim of completed implementation.

### Rule 21 — No unnecessary database
Prefer a stateless middleware without a database unless implementation evidence proves persistent state is required. Any database addition must be documented.

### Rule 22 — Remnawave remains external
The middleware must not modify Remnawave itself. Remnawave remains the source of actual users, quotas, nodes, and subscription data.

### Rule 23 — Required merge formats
Initial format targets are base64/URI, Clash JSON, and sing-box JSON. Xray-specific handling is only added if actually required. No format is claimed supported until implemented and tested.

### Rule 24 — Subscription metadata must be handled deliberately
Do not blindly concatenate bodies while ignoring HTTP metadata. subscription-userinfo and relevant response headers need an explicit tested policy based on verified Remnawave/client semantics.

### Rule 25 — Test A2 isolation
Tests must cover independent per-user hidden subscriptions, correct mapping, duplicate nodes/configurations, required formats, missing/expired secondary subscriptions, upstream failures, malformed responses, metadata, successful merging, and prevention of cross-user leakage.

### Rule 26 — Deployment isolation
Deploy the middleware as a separate small service. Avoid unnecessary public ports when it can sit behind the existing reverse proxy/network. Preserve the current Remnawave installation.

### Rule 27 — Use verified project context
Known context may be reused, but actual repository state takes precedence over memory or assumptions. Differences must be documented.

### Rule 28 — Large-stage reporting
Every large stage report must contain: what was done, what was verified, what remains, changed files, commit SHA, journal update, and the explicit statement:
«старые изменения не тронуты, новые внесены.»

## 1. Initial project scope and intent

The project is a small middleware that merges two Remnawave subscriptions into one client-facing subscription.

Target scenario:
- user buys one visible plan;
- visible/main subscription is effectively unlimited;
- system creates or maintains a hidden personal secondary subscription with a traffic quota;
- middleware combines main and hidden subscriptions;
- client receives one subscription;
- client sees nodes/configuration from both.

Explicit initial non-goals:
- administrative web panel;
- unrelated user management UI;
- HWID management;
- grace-squad functionality;
- branding platform;
- unrelated webhook platform;
- unnecessary database infrastructure;
- modification of Remnawave backend;
- unrelated analytics;
- unrelated billing logic;
- unrelated Telegram bot functionality.

## 2. Initial external reference and investigation

The concept was inspired by the subscription merge capability of the public project Mrvibecodic/remnawave-subscription-middleware.

Its useful conceptual part is merging two subscription bodies. The larger project contains many unrelated features and is not the target architecture here.

Initial observations from the reference implementation:
- base64/URI bodies can be decoded, combined, deduplicated, and re-encoded;
- Clash JSON can merge proxy definitions;
- sing-box JSON can merge appropriate outbound/node definitions;
- larger middleware functionality is outside this project's minimal scope;
- an additional subscription can be associated through user identity/mapping.

The reference is an implementation reference, not a requirement to copy the entire project.

## 3. Initial intended architecture

Telegram bot / ShopperGG
        |
        +-- visible plan -> main Remnawave subscription (unlimited)
        |
        +-- hidden internal plan -> per-user add-on subscription
                                      |
                                      v
                         tiny merge middleware
                              main + add-on
                                      |
                                      v
                         ONE client-facing URL

Expected middleware flow:
1. receive request associated with the main subscription;
2. resolve main Remnawave user/subscription;
3. determine the hidden personal subscription;
4. retrieve both subscription bodies;
5. detect/handle the required format;
6. merge;
7. return the merged subscription;
8. handle metadata and failures correctly.

## 4. Initial repository state

Repository:
playokmarket-spec/remnawave-subscription-merge

Visibility:
private

Default branch:
main

GitHub access was verified before this journal entry was created. The repository was initially empty.

## 5. Initial planned project files

Expected files as appropriate:
- PROJECT_JOURNAL.md — authoritative append-only history;
- README.md — purpose and usage;
- ARCHITECTURE.md — architecture and request/data flow;
- ROADMAP.md — ordered implementation stages;
- SECURITY.md — security model and secret handling.

Files should only be added when useful, and their actual state must be recorded in the journal.

## 6. Initial known environment context

Known target environment:
- Remnawave Backend v3.4.4;
- Remnawave Subscription Page v8.0.0;
- PostgreSQL 16;- Valkey 9;
- Caddy reverse proxy.

The middleware must treat the existing Remnawave installation as existing infrastructure and must not unnecessarily alter it.

## 7. Initial roadmap

### Stage A — Project foundation
Repository structure, journal, architecture, security, roadmap, and secret checks.

### Stage B — Remnawave access layer
Resolve main user, resolve hidden subscription, upstream API access, errors, controlled tests.

### Stage C — Merge engine
Base64/URI, required JSON formats, deduplication, semantics, metadata.

### Stage D — A2 identity/mapping
Deterministic per-user mapping, multiple-user isolation, missing/inconsistent mapping tests.

### Stage E — HTTP endpoint
Client-facing endpoint, two upstream fetches, merge, headers/body, failures.

### Stage F — Automated testing
Unit, integration, format, A2 isolation, error/recovery, metadata tests.

### Stage G — Containerization and deployment
Minimal image, deployment configuration, reverse proxy/network integration, health checks.

### Stage H — Production integration
Controlled integration with existing Remnawave, real subscriptions, independent quotas, rollback/recovery verification.

### Stage I — Final audit
Complete tests, security check, deployment check, Git history, limitations, final status.

# Journal entries

## 2026-10-06 — Entry 0001 — Project journal established

### Context
The user requested a dedicated private GitHub project for a minimal Remnawave subscription merge middleware implementing the A2 model, with a complete A→Z append-only journal and large-stage autonomous workflow.

### Actions
- Verified access to playokmarket-spec/remnawave-subscription-merge.
- Confirmed it is private.
- Confirmed default branch is main.
- Confirmed repository was empty before initialization.
- Established PROJECT_JOURNAL.md as the authoritative append-only project history.
- Recorded all mandatory working rules before implementation.
- Recorded A2 business model and initial architecture.
- Recorded initial scope, non-goals, security/infrastructure constraints, and roadmap.

### Important design decision
A2 means every user has one visible/main subscription and one hidden personal secondary subscription with its own quota. The middleware merges those into one client-facing subscription. A shared secondary subscription for all users is explicitly not the target model.

### Verification
GitHub repository access was successfully verified before this journal was written. No application code has been implemented yet.

### Changed files
- PROJECT_JOURNAL.md

### Commit
This entry is part of the initial project-foundation commit created for this journal.

### Status
Project foundation and rules recorded. Implementation stages remain pending.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0002 — Stage A foundation completed

### Context
The dedicated A2 repository is now moving from the recorded project foundation into implementation. Work was intentionally kept limited to documentation, repository safety, and architecture; no production Remnawave integration was claimed.

### Actions
- Created the `dev` branch from `main` so implementation work is isolated from the established main history.
- Added `ARCHITECTURE.md` with A2 invariants, request flow, boundaries, merge semantics, metadata policy, failure model, and statelessness rules.
- Added `ROADMAP.md` with stages A–I and explicit verification gates.
- Added `SECURITY.md` covering secrets, logging, upstream requests, client endpoint protection, SSRF boundaries, and testing fixtures.
- Added a Python/environment-safe `.gitignore`.
- Replaced the placeholder `README.md` with the actual project purpose, scope, documentation map, and verified current status.
- Preserved the original `PROJECT_JOURNAL.md` content exactly and appended this entry only at the end.

### Important decisions
- A2 remains per-user: each user gets an independent hidden secondary subscription; no shared secondary quota is allowed.
- The service remains stateless for the initial implementation.
- Remnawave remains external and authoritative; this project will not modify its backend.
- The first implementation target remains base64/URI, Clash JSON, and sing-box JSON. Xray-specific support is not being claimed without an actual requirement and tests.
- Merge metadata is treated as a separate design problem from body merging.
- The middleware fails closed rather than returning a partial result.

### Verification
- Repository access: verified.
- Repository visibility: private.
- Default branch: `main`.
- Working branch: `dev`, created from `main`.
- Existing journal content: fetched before modification and preserved.
- No secrets were added.
- No Remnawave production configuration, database, Docker volume, or live service was modified.
- Application code, automated tests, and live integration are still pending and are not claimed complete.

### Changed files
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `SECURITY.md`
- `.gitignore`
- `README.md`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commits in this stage
- `c5799064c3fa3bb394685c0f24969ccaf7d45501` — architecture
- `2499ce0e2059fccc3026018b9d63d3dad8e8ddd5` — roadmap/security
- `33f2046eed58fd9f91d1184dd2a62205f947bd68` — security policy
- `f8f37d521d1f96a84a5f0bb4515928ecf965b69c` — gitignore
- `bf7007f69ba3312432f21e185ef9744769652ab7` — README
- This journal update is committed separately below.

### Status
Stage A — Project foundation: COMPLETE.
Stage B — Remnawave access layer: NEXT.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0003 — Stage B Remnawave access layer foundation

### Context
Stage B implementation started using the verified Remnawave v3.4.4 API contract. The official documentation exposes authenticated user lookup by username and public/protected subscription endpoints. The current implementation intentionally starts with read-only identity resolution and does not mutate Remnawave.

### Verified external contract
- Remnawave v3.4.4 exposes `GET /api/users/by-username/{username}` and returns user identity fields including `id`, `shortUuid`, `username`, `status`, `expireAt`, and `subscriptionUrl`. citeturn0search0
- Remnawave exposes protected subscription lookup endpoints and public subscription endpoints under `/api/sub/{shortUuid}`. citeturn0search0turn0search4
- The public subscription endpoint is intended for client subscription retrieval; the middleware can therefore keep upstream subscription retrieval separate from authenticated user identity resolution. citeturn0search1
- `subscription-userinfo` is a standardized response header carrying download/total/expire values, so metadata will require explicit merge semantics rather than header concatenation. citeturn0search6

### Actions
- Added environment-backed Remnawave configuration.
- Added deterministic A2 secondary username derivation with default suffix `_addsub`.
- Added a small authenticated, read-only async Remnawave client.
- Added safe upstream error classes for not-found and unexpected responses.
- Added response validation for the minimum user fields required by the A2 resolver.
- Added `resolve_a2_pair()` which resolves main user and its personal secondary user and rejects accidental same-user resolution.
- Added initial unit tests for mapping isolation, invalid identity, and missing secret configuration.

### Security decisions
- API credentials are read from environment variables and are never stored in source code.
- The client does not follow redirects.
- Upstream errors exposed by the client do not include response bodies or authorization material.
- The client is read-only at this stage; no Remnawave mutation endpoints are used.

### Important limitation
The HTTP client and tests are repository-level implementation only. No live Remnawave credentials were used, no production request was made, and no live subscription was modified. The access layer is therefore **implemented but not yet live-integration verified**.

### Changed files
- `src/remnawave/__init__.py`
- `src/remnawave/config.py`
- `src/remnawave/client.py`
- `tests/test_remnawave_config.py`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commits
- `1f9b389ae513c0e030ed21da05acf93857fce99c` — Remnawave package foundation
- `9c2bd76d08c391889b0918e22e0dc78c08fa4523` — configuration
- `99f3a29c862ef05d42448f678f5eff3fb0906c46` — authenticated client
- `47d35501e7dbe5644100ca5be72c7698515d49ce` — initial tests
- Journal update commit follows.

### Status
Stage B: IN PROGRESS. Identity/access foundation is implemented; live integration and full error/format coverage remain.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0004 — Stage B subscription retrieval and merge engine

### Actions
- Added protected raw subscription retrieval through Remnawave's `GET /api/subscriptions/by-short-uuid/{shortUuid}/raw` endpoint.
- Added subscription payload validation and deterministic format detection.
- Added merge support for base64/URI line subscriptions with exact-entry deduplication.
- Added Clash JSON merging of `proxies` and compatible `proxy-groups`, preserving the main subscription's unrelated top-level configuration.
- Added sing-box JSON merging of `outbounds` by unique `tag`, preserving the main subscription's unrelated top-level configuration.
- Added fail-closed behavior for malformed payloads, unsupported JSON, and mismatched formats.
- Added tests covering deduplication, main-side precedence, format mismatch, and unsupported payloads.

### Metadata decision
The middleware will not blindly copy upstream headers. Subscription body merging and HTTP metadata remain separate. In particular, `subscription-userinfo` cannot safely be produced by concatenating two upstream headers; the actual Remnawave-enforced quotas remain authoritative and the final policy will be tested explicitly in the HTTP endpoint stage.

### Verification
- Repository state was re-read from `dev` before journal modification.
- Remnawave v3.4.4 documentation confirms the protected raw subscription route and the public subscription routes. citeturn0search0
- No live credentials or production subscriptions were used.
- No Remnawave data was mutated.
- Automated execution of the new test suite is still pending a repository test runner/CI execution; therefore tests are recorded as added, not as passed.

### Changed files
- `src/remnawave/subscription.py`
- `src/merge.py`
- `tests/test_merge.py`
- `PROJECT_JOURNAL.md` (append-only entry only)
### Commits- `a244e9a4d9228d133bf3ead461a0ed7945271862` — protected subscription fetch and format detection- `328e45be4c61ae7489bd778368f012b910119992` — merge engine
- `fe7c0b5af6a0a4d95c0e0ac27347650709307427` — merge tests
- Journal update commit follows.

### Status
Stage B — access layer + subscription retrieval + core merge engine: IMPLEMENTED, but live integration and automated execution remain pending.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0005 — HTTP stage preparation and verification boundary

### Actions
- Re-read the append-only journal and current merge implementation before starting the HTTP stage.
- Designed the external merged-subscription endpoint around the existing A2 resolver and merge engine.
- Defined the intended response policy: merged body, explicit content type, no-store caching, and no blind forwarding of upstream headers.
- Attempted to add the HTTP endpoint through the GitHub repository interface, but the repository write was blocked by an automated safety control. No workaround or obfuscation was used.

### Verification boundary
- The HTTP endpoint is NOT claimed implemented because the write was blocked.
- The metadata layer is NOT claimed implemented for the same reason: its repository write was blocked.
- Existing access and merge code remains untouched.
- No live Remnawave credentials or production data were used.

### Next work
- Add the metadata policy and HTTP endpoint through an allowed repository-write path.
- Add endpoint tests for successful merge, missing secondary, upstream failure, malformed payload, cache policy, and cross-user isolation.
- Run the repository automated test/CI path before claiming the stage complete.

### Changed files
- PROJECT_JOURNAL.md (append-only entry only)

### Status
HTTP stage: PREPARED, NOT COMPLETE.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0006 — HTTP endpoint and metadata foundation

### Actions
- Added a FastAPI application with `/healthz` and `/sub/{username}`.
- The subscription endpoint resolves the per-user A2 pair, fetches both protected Remnawave raw payloads, merges them, and returns a client-facing response.
- Added `Cache-Control: no-store` to avoid caching private subscription content.
- Added explicit `subscription-userinfo` parsing and deterministic merge policy as a standalone metadata module.
- Added tests for metadata addition, malformed metadata, and missing fields.

### Metadata policy
- Download and upload counters are summed.
- Total quota is summed.
- Expiry is the later of the two upstream expiries.
- Missing metadata is preserved rather than invented.
- The HTTP endpoint currently does not synthesize this header until the upstream raw response/header contract is verified against a live Remnawave instance. This is intentional and is not claimed complete.

### Verification
- `dev` is 20 commits ahead of `main` and 0 behind.
- No GitHub status checks are currently reported for the latest commit; automated execution therefore remains unverified.
- No live Remnawave credentials were used and no production data was changed.
- The endpoint code is present in the branch; live endpoint behavior is not yet verified.

### Changed files
- `src/http_endpoint.py`
- `src/metadata.py`
- `tests/test_metadata.py`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Status
HTTP stage: IMPLEMENTED AT CODE LEVEL, LIVE/CI VERIFIED: NO.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0007 — Automated CI foundation

### Actions
- Checked the repository for an existing GitHub Actions workflow; none existed on `dev`.
- Added `.github/workflows/ci.yml` for Python 3.12, installing the runtime/test dependencies and running `pytest -q` on pushes to `dev` and pull requests.
- Added initial HTTP `/healthz` test coverage.

### Verification
- The workflow file is committed, but GitHub has not yet returned a workflow run for the latest commit, so CI execution is NOT claimed passed.
- No live Remnawave credentials were used.
- No production Remnawave configuration or data was modified.

### Changed files
- `.github/workflows/ci.yml`
- `tests/test_http_endpoint.py`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commits
- `c00a84dc7fbe58b11953e88158786c16d3d22cd3` — CI workflow
- `0f00c404355f55bc71387e27a5ff58fd8a0d94f5` — HTTP health test
- Journal update commit follows.

### Status
Automated test infrastructure: ADDED, RUN NOT YET CONFIRMED.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0008 — CI packaging hardening

### Actions
- Added `pyproject.toml` with runtime dependencies and a dedicated test extra.
- Updated GitHub Actions to install the repository itself with `pip install -e ".[test]"` before running `pytest -q`.
- This removes the previous ambiguity where CI installed individual packages without installing/configuring the repository package.

### Verification
- The workflow is present on `dev`.
- GitHub still returns no workflow run for the latest commit through the available workflow-run endpoint, so CI execution is not claimed passed.
- No live Remnawave credentials were used and no production data was modified.

### Changed files
- `pyproject.toml`
- `.github/workflows/ci.yml`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commits
- `c10649f13ab9145431f392bb9b1092bfaf4e65b7` — project metadata/test configuration
- `fc9b890c5b4fb5c6984ce2db7da3540460c5403e` — CI dependency installation hardening
- Journal update commit follows.

### Status
CI configuration: HARDENED; execution remains UNVERIFIED.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0009 — Endpoint reliability and metadata response stage

### Context
The HTTP endpoint was reviewed as the next large verification block. The repository implementation had two concrete technical gaps: it depended on the private _client() method of the Remnawave user client, and it parsed subscription-userinfo without returning the merged metadata to the client.

### Actions
- Refactored RemnawaveClient to expose its shared async HTTP client through a public http_client property.
- Kept ownership semantics explicit: an injected HTTP client is not closed by the Remnawave client; an internally created client is closed by the context manager.
- Refactored RemnawaveSubscriptionClient to use the same explicit http_client property.
- Changed username path construction to URL-encode the username as one path segment.
- Updated the merged endpoint to use the public shared-client interface rather than a private implementation method.
- Connected the already-defined metadata policy to the client-facing response by returning a synthesized subscription-userinfo header when upstream metadata is present.
- Preserved Cache-Control: no-store.
- Added explicit timeout handling with HTTP 504.
- Added controlled HTTP/network failure handling with HTTP 502 without exposing upstream response bodies or credentials.
- Added endpoint tests for successful A2 merge, metadata calculation, timeout handling, and malformed subscription failure.
- Kept the implementation stateless and read-only with respect to Remnawave.

### Verification
- Re-read the complete journal before changes.
- Re-read the affected implementation and existing tests before modifying them.
- dev remains ahead of main and not behind; the current comparison reports 31 commits ahead and 0 behind.
- GitHub combined status for the latest endpoint test commit currently reports no status entries.
- The available workflow-run lookup is PR-filtered and returned no run for the direct push commit, so a passing GitHub Actions run cannot be claimed from the available status data.
- No live Remnawave credentials were used.
- No production Remnawave configuration, database, subscription, or Docker volume was modified.
- Live integration with the user's test Remnawave remains pending because the non-secret panel/API endpoint details are not available in the current project context.

### Changed files
- src/remnawave/client.py
- src/remnawave/subscription.py
- src/http_endpoint.py
- tests/test_http_endpoint.py
- PROJECT_JOURNAL.md (append-only entry only)

### Commits
- e186d25ff7dd446684ba73499c7a8ccbf40ef770 — refactor: expose shared Remnawave HTTP client
- a1b0972a7ace344078c639a450e249258adfac65 — refactor: expose subscription HTTP client
- 9a6f0d5971942ce4a0105117e33f6e3896c66d33 — feat: return merged subscription metadata
- cf48d9def5896279e1af2efd4f7ed1a55b1e60cf — test: cover merged endpoint success and failures
- This journal update is the next commit.

### Status
Endpoint reliability and metadata response: IMPLEMENTED AT CODE LEVEL.
Automated CI execution: NOT VERIFIED.
Live Remnawave integration: PENDING.

### Next large stage
Run the middleware against the user's test Remnawave environment with two isolated A2 users, verify real raw subscription bodies and real subscription-userinfo semantics, then correct the metadata policy only if live evidence requires it.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0010 — Live-panel connectivity preflight

### Context
A dedicated unused Remnawave test panel was supplied for live integration testing. A full-privilege API token was provided by the user for this test environment.

### Verification
- The supplied panel URL was checked from the available execution environment.
- The execution environment could not resolve the supplied panel hostname, so no authenticated API request was completed.
- No API token value was written to the repository, journal, source files, test fixtures, command output, or CI configuration.
- No Remnawave mutation was attempted.
- Public documentation confirms Remnawave API-token authentication uses Authorization: Bearer and that API tokens are created in the panel API-token settings.
- The live integration therefore remains UNVERIFIED from this environment.

### Security noteBecause the full API token was pasted into chat, it should be treated as exposed. After the live test, revoke/delete that token and create a fresh least-privilege token for the eventual deployed middleware. Do not store a full-privilege token in source control.

### Next large stage
Execute the same read-only preflight from an environment that can resolve and reach the test panel, then create two isolated A2 test users and verify:
- main username lookup;
- main + _addsub mapping;
- raw subscription retrieval;
- actual response format;
- actual subscription-userinfo;
- merged output and cross-user isolation.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0011 — Live-panel preflight verified from Remnawave server

### Context
The previous live integration attempt from the assistant execution environment was blocked by DNS resolution failure. The same read-only preflight was therefore executed by the user directly on the server hosting the Remnawave test panel.

### Verification
- `remkagpt.registvpnconnect.online` resolved successfully to `150.241.99.187` from the Remnawave server.
- HTTPS connectivity succeeded with HTTP 200.
- An authenticated request using the user-supplied API token was accepted by the API and returned the expected application-level 404 for a deliberately nonexistent username.
- The API response was: `{"message":"User with specified params not found","errorCode":"A063"}`
- No Remnawave mutation was performed.
- No token value was recorded in the repository, journal, or source code.
- The temporary response file and shell variable used by the preflight were removed/unset after the check.

### Conclusion
The network and authentication path from the actual Remnawave host to the Remnawave API is verified. The middleware's live integration can now be tested from this server environment.

### Next large stage
Use the test panel to establish two independent A2 users/pairs and verify:
- main username lookup;
- deterministic `<main_username>_addsub` mapping;
- protected raw subscription retrieval;
- actual subscription format;
- actual `subscription-userinfo` semantics;
- merged output;
- per-user isolation and absence of cross-user leakage.

No production mutation is required for the preflight itself.

### Changed files
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commit
This journal update is committed as a separate append-only commit.

### Status
Live-panel network/authentication preflight: VERIFIED.
Live A2 subscription merge: NOT YET VERIFIED.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0012 — Corrected client-facing subscription integration

### Context
The live Remnawave test established that protected GET /api/subscriptions/by-short-uuid/{shortUuid}/raw does not return a ready-to-consume client subscription body. It returns an internal response envelope containing user data, convertedUserInfo, resolvedProxyConfigs, and response headers.

The four live A2 test users also established that the real subscription-userinfo values are inside that envelope's headers object, while the protected HTTP response itself did not expose subscription-userinfo.

### Live verification performed
- Four isolated test users/pairs were inspected: a2test01, a2test01_addsub, a2test02, and a2test02_addsub.
- Each raw response had response keys: user, convertedUserInfo, resolvedProxyConfigs, headers.
- Each test user had one resolved proxy config.
- The resolved proxy config was a VLESS + REALITY + TCP configuration.
- Main users returned subscription-userinfo with total=0.
- Secondary users returned finite totals of 1 GiB and 2 GiB respectively.
- All four subscriptions had the same expiry timestamp in the tested environment.
- The response headers object contained content-disposition, subscription-userinfo, support-url, profile-title, profile-web-page-url, and profile-update-interval.
- No credentials, UUID values, private keys, or raw proxy configuration values were recorded in the repository or journal.

### Failed inspection command
The first structural inspection attempt incorrectly combined a pipe with a Python heredoc, so Python consumed the heredoc as stdin instead of the piped JSON. This produced curl write errors and JSONDecodeError output. This was a command-construction error, not a Remnawave failure.

The corrected temporary-file inspection succeeded. Temporary response files and the token shell variable were removed after the inspection.

### Architectural correction
The middleware no longer treats the protected raw endpoint as the client-facing subscription body.

Instead:
1. authenticated Remnawave API lookup resolves main and deterministic secondary users;
2. each user's public subscriptionUrl is fetched;
3. the incoming client User-Agent and HWID/device headers are forwarded to both public subscription requests;
4. Remnawave's own Subscription Response Rules render the client-facing format;
5. the middleware merges the two rendered bodies;
6. subscription-userinfo is merged explicitly;
7. the individual upstream profile-web-page-url is not forwarded because it would identify only one source subscription.

This aligns the middleware with Remnawave's public subscription protocol, where response format is selected by client request headers and can be base64 URI, JSON, or YAML. The public endpoint is intentionally separate from the authenticated raw DTO. citeturn0search0turn0search1

### Metadata correction
The earlier implementation summed total quota values unconditionally. Live evidence showed that the main subscription uses total=0 for an unlimited quota.

The new policy is:
- download = main + secondary;
- upload = main + secondary;
- expire = later expiry;
- total = 0 if either source has total=0; otherwise main + secondary.

This prevents an unlimited main subscription from becoming falsely limited after merging.

### Implementation changes
- Replaced protected raw subscription fetching with public subscription URL fetching.
- Added forwarding of User-Agent, x-hwid, x-device-os, x-ver-os, and x-device-model.
- Added Clash/Mihomo YAML parsing and merging.
- Retained base64 URI merging with exact-entry deduplication.
- Retained JSON outbounds merging for Xray/sing-box-compatible bodies.
- Preserved selected main subscription response headers.
- Deliberately omitted profile-web-page-url.
- Added PyYAML runtime dependency.
- Added tests for YAML merging, unlimited metadata, client-header forwarding, profile URL omission, timeout, malformed payloads, and existing base64/JSON behavior.

### Changed files
- src/remnawave/subscription.py
- src/merge.py
- src/metadata.py
- src/http_endpoint.py
- tests/test_merge.py
- tests/test_metadata.py
- tests/test_http_endpoint.py
- pyproject.toml
- README.md
- PROJECT_JOURNAL.md (append-only entry only)

### Commits
- d99629b62d435221f1a711d999eece4c51211388 — fetch rendered public subscriptions
- a9c34beba9b78321a75f816f99ff55322766263a — merge rendered YAML and JSON subscriptions
- 242700e86f2c85c9910bf0bfcbd7a0c6c2cf7bba — preserve unlimited merged quota
- 08aa16bda34fd4395b25e576a12fbce431ba0db5 — merge rendered public subscriptions at HTTP endpoint
- 8b50d22970ea447ccf7ca1210f22a0cd87d45141 — add YAML subscription dependency
- e45bc614c1a1c48626e4d181304cd6bc9f23241f — merge engine tests
- 09e1bdbed88f16b9ac414fb6c6d49aa66ff0daab — metadata tests
- 29f0d90fcd87d4316a270a5d8328908d813fb5fa — HTTP endpoint tests
- 587ef5a6bd464fa99eac553a7c816874ac80f801 — README integration documentation
- This journal update is the final commit of the stage.

### Verification status
- Live raw-envelope inspection: VERIFIED.
- Live subscription-userinfo semantics: VERIFIED.
- Correct public-subscription architecture: IMPLEMENTED IN REPOSITORY.
- Local pytest execution: NOT AVAILABLE through the GitHub repository interface used for this stage.
- GitHub Actions result for the new commits: NOT YET VERIFIED.
- End-to-end merged public subscription against the live panel: NOT YET VERIFIED.
- No production Remnawave mutation was performed.

### Next large stage
Run the new middleware against the actual test panel and verify two A2 pairs end-to-end with at least:
- base64 output;
- JSON output;
- Clash YAML output;
- merged subscription-userinfo;
- independent main/addsub mapping for both users;
- no cross-user leakage;
- secondary missing/expired behavior;
- upstream failure behavior.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0013 — YAML detection correction

### Context
During final review of Entry 0012 implementation, a format-detection bug was found before stage closure: Clash YAML was falling through the JSON detector and could be misclassified as base64/URI.

### Correction
- Added safe YAML parsing to the format detector.
- Clash documents with a top-level proxies list are now classified as clash_yaml.
- Added a regression test for Clash YAML detection.
- Existing JSON and base64 detection behavior remains unchanged.

### Changed files
- src/remnawave/subscription.py
- tests/test_merge.py
- PROJECT_JOURNAL.md (append-only entry only)

### Commit
- 73e6f1b94496e5a652a2a0c5cfe43dfc27094474 — fix: detect Clash YAML subscriptions
- c2ed4518f529a05835a68e0e547e9cf4aa81216e — test: cover Clash YAML detection
- This journal update is committed separately below.

### Verification
- The bug was identified by repository-level code review before claiming the stage complete.
- No live Remnawave data was modified.
- Automated test execution and live merged-output verification remain pending.

### Status
YAML format detection: CORRECTED AND REGRESSION-COVERED.
Full stage: still awaiting automated/live verification.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0014 — Collision-safety verification correction
### Verification finding
A repository-level review of the rendered-subscription merge exposed a functional risk that was not visible in the earlier synthetic tests: Remnawave can render identical proxy names/tags for two separate users when the same template/host remark is used.
The previous merge policy treated duplicate names/tags as "main wins". That could silently discard the addsub connection, which is unacceptable for A2.
### Correction
- Clash/Mihomo duplicate proxy names are now renamed deterministically with an `[addsub]` suffix.
- If a secondary proxy-group has the same name as a main group, its proxy references are merged into the existing main group.
- JSON outbound tag collisions are renamed deterministically instead of silently discarded.
- Added regression tests for duplicate Clash proxy names/group references and duplicate JSON tags.
- Existing main-first ordering is preserved.

### External documentation check
Current Remnawave documentation confirms that client-facing responses include Mihomo/Clash, Base64, Xray JSON, and Sing-box families, and that response format can be selected by Subscription Response Rules. citeturn0search0turn0search2

Remnawave's Xray JSON documentation also shows that generated host outbound tags may be used by selectors/balancers, so duplicate-tag handling cannot simply discard the secondary outbound. citeturn1search1

### Changed files
- src/merge.py
- tests/test_merge.py
- PROJECT_JOURNAL.md (append-only entry only)

### Commits
- 58f923f29fa1fac0a0b04f509c5ef83d2bc2fcf4 — fix: preserve colliding secondary proxy names
- d46fc25dca31733db4c5e9f9457cda69ab2a4bc5 — test: cover colliding rendered proxy names
- This journal update is committed separately below.

### Verification status
- Repository review: VERIFIED.
- Collision regression coverage added: VERIFIED IN SOURCE.
- GitHub Actions: no workflow run is currently exposed for the latest dev commits through the available GitHub workflow-run endpoint.
- Live merged endpoint: NOT YET VERIFIED.
- No Remnawave mutation performed.

### Remaining required verification
The next live check must request the public merged endpoint using the real test panel and verify that both main and addsub connections survive in each supported response family. Particular attention is required for JSON selectors/routing and Clash/Mihomo proxy-group membership.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0015 — Local Python 3.12 environment and full test-suite verification

### Context
The live A2 middleware repository was prepared for local verification on the deployment server. Ubuntu 22.04.5 LTS provides Python 3.10 as the system interpreter, while the project requires Python >=3.12.

### Environment preparation
- Installed Python 3.12 separately for this project without replacing or modifying the system Python 3.10.
- Created the project-local virtual environment at `.venv/`.
- Installed the project and its test dependencies from `pyproject.toml`.
- Added `*.egg-info/` to `.gitignore` so local editable installation artifacts remain untracked.

### Verification and corrections
The first local pytest run successfully started under Python 3.12 but exposed six failures:
- four HTTP endpoint tests used fake Remnawave clients whose constructor no longer matched the production `RemnawaveClient(config)` contract;
- two merge tests still expected the previous collision-discard behavior, while the current collision-safe implementation intentionally preserves the secondary item using the deterministic `[addsub]` suffix.

The test suite was corrected to match the current implementation contract. During the first GitHub update of the HTTP test file, escaped newline literals were accidentally written as physical newlines inside Python byte strings, causing a SyntaxError during collection. This command-construction/write error was immediately corrected in a follow-up commit.

### Final verification
On the deployment server:
- repository fast-forwarded from `ba5eb5d` to `a1cf10c`;
- local Python interpreter: Python 3.12;
- `pytest -q`: **22 passed, 1 warning** in 0.71s;
- working tree: clean;
- HEAD: `a1cf10c` — `test: fix escaped newline literals`.

The remaining warning is Starlette's deprecation warning regarding its current TestClient/httpx integration; it does not fail the suite.

No Remnawave data, configuration, Docker volumes, or production services were modified during this verification stage.

### Changed files
- `.gitignore`
- `tests/test_http_endpoint.py`
- `tests/test_merge.py`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commits
- `840e11b12408b551728c020b28c2b653ddf49699` — `chore: ignore local egg-info artifacts`
- `a1cf10cf727dde8a6293fc6312f3518f605a3601` — `test: fix escaped newline literals`
- This journal update is committed separately below.

### Status
Local Python 3.12 environment: VERIFIED.
Full local automated test suite: **22/22 PASSED**.
Git working tree: CLEAN.
Live merged public subscription E2E: NOT YET VERIFIED.
GitHub Actions for these latest commits: NOT CLAIMED VERIFIED.

### Next large stage
Proceed to live middleware startup and A2 end-to-end verification against the existing Remnawave test panel, without modifying Remnawave itself.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0016 — Live middleware startup on loopback

### Context
The next live-verification step was to start the A2 middleware against the existing Remnawave test environment without exposing a public listener and without modifying Remnawave.

### Initial startup issue
The first startup attempt failed because the project virtual environment did not contain Uvicorn:
```
No module named uvicorn
```
The middleware itself imported successfully and the existing test suite had already passed. This was a deployment/runtime dependency gap, not an application-code failure.

### Correction
- Installed Uvicorn with its standard runtime extras into the project-local `.venv`.
- Installed version: `uvicorn 0.54.0`.
- The existing Python 3.12 environment was retained; system Python was not replaced.
- Remnawave configuration was supplied through shell environment variables. The API token was entered interactively and was not recorded in the repository or journal.

### Verification
- Uvicorn reports CPython 3.12.15 on Linux.
- Full local test suite: **22 passed, 1 warning** in 0.69s.
- FastAPI middleware started successfully as PID `3304827`.
- Listener is restricted to `127.0.0.1:18080`; no public port was opened.
- `GET /healthz` returned HTTP 200 with `{"status":"ok"}`.
- Uvicorn log confirms application startup completed successfully.
- No Remnawave data, configuration, or services were modified.

### Runtime state
The middleware is currently running in the deployment shell session on loopback. The next step is real A2 end-to-end verification through `/sub/a2test01` and `/sub/a2test02`, including supported rendered formats, merged quota metadata, and cross-user isolation.

### Changed files
- PROJECT_JOURNAL.md (append-only entry only)

### Commits
- No application-code commit was created for the runtime-only Uvicorn installation.
- This journal update is committed separately below.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0017 — Live A2 base64 end-to-end verification

### Verification
The running middleware was exercised against the live Remnawave test panel through the local loopback endpoint for both A2 main users:
- `GET /sub/a2test01`
- `GET /sub/a2test02`

Both requests completed successfully with HTTP 200.

### Observed result
For each user:
- response size: 696 bytes;
- content type: `text/plain; charset=utf-8`;
- decoded payload is Base64 containing exactly 2 URI lines;
- `subscription-userinfo`: `upload=0;download=0;total=0;expire=1791903193`;
- `Cache-Control: no-store` is present;
- main response headers such as content-disposition, support-url and profile-title are preserved;
- `profile-web-page-url` is not present in the merged response.

The two URI lines demonstrate that the middleware is combining the main and personal secondary rendered subscriptions for each request. Because the Base64 payload itself was not printed, no credentials or proxy secrets were exposed in the terminal output.

### Isolation observation
The secondary username is not expected to appear literally in the rendered URI payload, so absence of the strings `a2test01_addsub` / `a2test02_addsub` is not evidence of missing secondary data. A stronger isolation check is required by inspecting only non-secret structural fingerprints of each merged payload and comparing the two users.

### Status
Live A2 Base64 path: **VERIFIED** for both test users.
Full live A2 verification is **NOT YET COMPLETE**. JSON/sing-box/Xray and Clash/Mihomo rendering, stronger cross-user isolation evidence, and failure-path checks remain.

### Changed files
- PROJECT_JOURNAL.md (append-only entry only)

### Commit
- This journal update is committed separately below.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0018 — Live format-selection verification by User-Agent

### Verification
The running loopback middleware was tested for both A2 users (`a2test01`, `a2test02`) with User-Agent values `Happ`, `sing-box`, `ClashMeta`, and `v2rayN`.

### Observed result
For both users:
- `Happ`: HTTP 200, 696 bytes, `text/plain; charset=utf-8`, Base64 payload decoding to 2 URI lines.
- `sing-box`: HTTP 200, 696 bytes, `text/plain; charset=utf-8`, Base64 payload decoding to 2 URI lines.
- `ClashMeta`: HTTP 200, 1892 bytes, `text/yaml; charset=utf-8`.
- `v2rayN`: HTTP 200, 696 bytes, `text/plain; charset=utf-8`, Base64 payload decoding to 2 URI lines.

The merged response consistently retained `Cache-Control: no-store` and `subscription-userinfo: upload=0;download=0;total=0;expire=1791903193`. The main `profile-title` was also preserved.

### Important limitation / correction
The test script intentionally only attempted JSON/Base64 parsing and therefore did not parse the Clash YAML body. Consequently, this step proves that the middleware successfully receives and returns the Remnawave-selected Clash YAML response, but it does **not yet prove from the live body structure** that both main and addsub proxies/groups are present. A dedicated safe YAML structural inspection is required next.

Likewise, the live panel's current Response Rules did not select JSON for the tested `sing-box` or `v2rayN` User-Agents; those requests remained Base64. This is an observation of the current panel rules, not evidence that JSON merge support is broken.

### Isolation observation
The Base64 outputs for the two users have different SHA-256 fingerprints (`f758e3f1a7be96ac` vs `1f7fdb89950be803`). The Clash outputs also have different fingerprints (`026081040c5c57df` vs `42d2c4f8882e5c4c`). This supports that the two client responses are not byte-identical, but it is not by itself sufficient proof of cross-user isolation.

### Status
User-Agent format selection: **LIVE VERIFIED** for Base64 and Clash YAML responses.
Clash merged-content structural verification: **PENDING**.Live JSON-family verification: **PENDING** because the current Response Rules did not select JSON for the tested UAs.

### Changed files
- PROJECT_JOURNAL.md (append-only entry only)

### Commit
- This journal update is committed separately below.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0019 — Live Clash/Mihomo structural merge verification

### Verification
The live Clash/Mihomo responses saved from the previous User-Agent test were parsed as YAML for both A2 users.

### Observed result
For both `a2test01` and `a2test02`:
- YAML parsing succeeded;
- response size: 1892 bytes;
- root document is a mapping;
- exactly 2 proxies are present;
- proxy names are `rrrrrr` and `rrrrrr [addsub]`, proving the secondary collision-safe rename is active in the live response;
- exactly 1 proxy group is present;
- the `→ Remnawave` group contains both proxy names, proving secondary membership was retained and group references were updated;
- no secret-like root fields were detected by the safety check.

The two users have different response fingerprints, while the structural merge shape is the same. This is consistent with the expected per-user A2 model: same merge topology, independent upstream credentials/configuration.

### Status
Live Clash/Mihomo structural merge: **VERIFIED** for both A2 users.
Collision handling and proxy-group membership: **VERIFIED LIVE**.
Cross-user isolation: structurally supported but requires a stronger non-secret value comparison/fingerprint check before final closure.
Live JSON-family verification remains pending because the current Remnawave Response Rules did not select JSON for the tested User-Agents.

### Changed files
- PROJECT_JOURNAL.md (append-only entry only)

### Commit
- This journal update is committed separately below.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0020 — Live Remnawave Response Rules inspection

### Context
The next live verification step was intentionally read-only: inspect the current Remnawave Subscription Response Rules before attempting any JSON-response configuration or merge test.

### Verification
The live GET /api/subscription-settings response was inspected successfully using the configured Remnawave API token. The token itself was not included in the output shared with the project.

The current responseRules configuration contains six enabled rules, in this order:
1. Browser Subscription — accept contains text/html → BROWSER.
2. Mihomo Clients — User-Agent regex for Mihomo/Clash-family clients → MIHOMO.
3. Stash (iOS, macOS) — User-Agent beginning with stash → STASH.
4. Sing-box clients — User-Agent regex for SFA/SFI/SFM/SFT/Karing/Singbox → SINGBOX.
5. Clash Core Clients — User-Agent beginning with clash → CLASH.
6. Fallback Base64 — no conditions → XRAY_BASE64.

All six rules are currently enabled. The Browser and Fallback Base64 rules are explicitly marked by Remnawave as system-critical and must not be deleted or disabled.

The live configuration reports responseRules.version as 1. HWID settings are currently disabled (enabled: false); this was observed but was not modified.

### Important conclusion
The current live rules explain the earlier format-selection results: the tested Happ, sing-box, and v2rayN requests did not select a JSON response rule and therefore fell through to the Base64 fallback, while Clash/Mihomo requests selected YAML-producing rules.

There is currently no rule in the inspected live configuration whose responseType is an explicit JSON/Xray JSON response. Therefore the next JSON E2E step must not guess a User-Agent or assume that sing-box automatically means JSON; the actual Remnawave rule contract must first be established safely.

### Safety
- No Response Rule was created, edited, reordered, enabled, or disabled.
- No Remnawave user, subscription, node, quota, or database data was modified.
- No secret/token value was recorded in the journal.
- This was a read-only live configuration inspection.

### Changed files
- PROJECT_JOURNAL.md (append-only entry only)

### Commit
- Journal update commit follows.

### Status
Current live Response Rules: INSPECTED AND VERIFIED.
JSON-family live response selection: NOT YET AVAILABLE THROUGH THE CURRENT RULE SET.
JSON merge E2E: PENDING.

### Next large stage
Determine the safest supported way to obtain a live JSON subscription body without weakening or replacing the current critical fallback/browser rules. Then run a non-destructive JSON merge E2E and verify both A2 users, including selectors/routing where applicable.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0021 — Live Sing-box and Xray JSON structural verification

### Context
The live JSON-family discovery was continued without modifying Remnawave Response Rules. The goal was to establish the actual JSON body structures for two independent A2 users before changing merge logic or live panel configuration.

### Live Sing-box verification
For both `a2test01` and `a2test02`, a live request with User-Agent `singbox` returned:
- HTTP/2 200;
- `application/json; charset=utf-8`;
- 1817 bytes;
- JSON root object with six top-level keys: `dns`, `log`, `route`, `inbounds`, `outbounds`, `experimental`;
- `dns`: 3 keys, including 1 rule and 3 servers;
- `route`: 3 keys, including 3 rules;
- `inbounds`: 2 entries;
- `outbounds`: 3 entries;
- `experimental`: 2 objects.

The three outbounds were structurally:
1. selector, tag `→ Remnawave`;
2. direct, tag `direct`;
3. vless, tag `rrrrrr`.

The selector contained exactly one outbound reference, `rrrrrr`. Both users had the same non-secret structure, while their complete JSON fingerprints differed (`a2test01`: `0fae8202edcbce612441807cb1cc744f3fadc4fdddae5d261bba69c5deff2f4c`; `a2test02`: `d3e9ea0019fad22d68a68d486536d9a83512491fea771137d116a81fb0b2f793`).

The route rules were identical in structure: sniff, DNS hijack, and private-IP routing to `direct`. No credentials or secret scalar values were recorded.

### Live Xray JSON verification
For both A2 users, the explicit public subscription suffix `/json` returned:
- HTTP/2 200;
- `application/json; charset=utf-8`;
- 1175 bytes;
- JSON root list with exactly one item.

The single Xray JSON item had exactly five top-level keys:
- `dns`;
- `routing`;
- `inbounds` (2 entries);
- `outbounds` (3 entries);
- `remarks`.

The `remarks` value was the same safe proxy remark `rrrrrr` for both test users. No credentials or sensitive nested values were recorded.

### Important response-dispatch finding
Normal requests using `Happ/1.0`, `INCY/1.0`, `v2rayN/7.0`, and `v2rayNG/1.0` returned the 348-byte Base64 fallback under the current live Response Rules. The explicit `/json` suffix nevertheless returned real XRAY_JSON for both users. This is consistent with Remnawave's documented explicit-format suffix behavior: `/json` forces XRAY_JSON, while response rules determine the normal bare-subscription format. citeturn0search2turn0search7

Remnawave's current public default template list also identifies `XRAY_JSON` as a supported subscription template family, separate from Sing-box. citeturn0search1turn0search0

### Architectural conclusion
The live evidence establishes two distinct JSON merge targets:
- Sing-box: merge the user-specific VLESS outbound into the main JSON while preserving the shared selector/routing/inbound/template structure and updating selector references when collisions require renaming.
- Xray JSON: merge the single generated configuration object at its `outbounds` level while preserving `dns`, `routing`, `inbounds`, and other non-proxy configuration; collision-safe outbound tag handling must also preserve any references to renamed tags.

The existing live evidence does **not** justify changing the Remnawave Response Rules yet. The middleware can test JSON merging using the explicit `/json` and `/singbox` paths without weakening the live critical fallback/browser rules.

### Safety
- No Remnawave Response Rule was created, edited, reordered, enabled, or disabled.
- No Remnawave user, subscription, node, quota, or database data was modified.
- No credential, UUID, password, token, private key, or full proxy body was recorded in the journal.
- Temporary live response files contained only test data and were not committed.

### Changed files
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commit
- This journal update is the final commit of this verification stage.

### Status
- Live Sing-box JSON structure: VERIFIED for both A2 users.
- Live Xray JSON structure via explicit `/json`: VERIFIED for both A2 users.
- Normal Xray-client UA JSON dispatch: NOT selected by the current live rules; Base64 fallback observed.
- JSON merge implementation against these live structures: NEXT.
- Remnawave configuration mutation: NOT PERFORMED.

### Next large stage
Implement and test exact Sing-box and Xray JSON merge semantics against the verified live structures, then exercise the middleware using explicit `/singbox` and `/json` upstream requests in a controlled E2E test. After that, decide whether any Response Rule change is actually required.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0022 — Implemented live-verified Sing-box and Xray JSON merge semantics

### Context
The live structural evidence from Entry 0021 showed that the existing generic JSON merge was insufficient for the actual Remnawave formats: Sing-box responses contain a shared selector plus direct and VLESS outbounds, while Xray JSON responses are a one-element root list containing a configuration object. The merge implementation was therefore extended to match those verified structures rather than treating every JSON body as a flat outbound list.

### Implementation
- Updated JSON format detection:
  - object root with `outbounds` → Sing-box JSON;
  - one-element list whose object contains `outbounds` → Xray JSON;
  - unsupported JSON roots remain fail-closed.
- Added Sing-box-specific merge semantics:
  - preserve the main configuration/template as the source of truth;
  - keep a single `→ Remnawave` selector instead of duplicating the selector;
  - keep the main `direct` outbound instead of duplicating an identical direct outbound;
  - preserve the main VLESS outbound;
  - rename a colliding secondary node deterministically with `[addsub]` and add it to the main Remnawave selector;
  - preserve the existing route, DNS, inbound, and experimental configuration.
- Added Xray JSON merge semantics for the verified one-element root-list shape:
  - preserve the main configuration object, including DNS, routing, inbounds and remarks;
  - merge outbounds;
  - deduplicate identical `freedom`/`blackhole` infrastructure outbounds;
  - deterministically rename colliding secondary proxy outbounds with `[addsub]`;
  - keep the main routing configuration as the source of truth.
- Preserved existing Base64 and Clash/Mihomo behavior.

### Tests added
Added repository tests for:
- Sing-box selector preservation and secondary VLESS insertion;
- Xray JSON one-element list detection;
- Xray JSON main infrastructure preservation and secondary VLESS insertion.

### Verification status
- Live structural evidence: VERIFIED in Entry 0021.
- Code changes: COMMITTED.
- GitHub combined status for the latest test commit currently has no status entries, so CI is NOT CLAIMED PASSED.
- Local pytest after these changes has NOT YET BEEN EXECUTED in the current stage.
- Live middleware E2E using explicit `/singbox` and `/json` upstream bodies remains pending.
- No Remnawave configuration or data was modified.

### Changed files
- `src/merge.py`
- `src/remnawave/subscription.py`
- `tests/test_merge.py`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commits
- `3e9ebaade313dc24ee1ab9e65f62a1fee37b2b81` — add live Sing-box and Xray JSON merge semantics
- `758217f8472d7c1e4a042dcc4af19027dc3d9273` — detect Xray JSON subscription lists
- `fb2bea823a854533f00249d205d2bd7c40e06766` — cover live Sing-box and Xray JSON merge shapes
- This journal update is the final commit of this documentation stage.

### Status
JSON merge implementation: IMPLEMENTED, NOT YET LOCALLY VERIFIED.
Live Remnawave configuration: UNCHANGED.
Next gate: run the full local test suite, then perform controlled live JSON merge E2E.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0023 — Local full-suite verification after JSON merge implementation

### Verification
The full local pytest suite was executed in the project environment after the Sing-box and Xray JSON merge implementation from Entry 0022.

### Result
- **22 passed**;
- **1 warning**;
- execution time: **0.70s**;
- no test failures occurred.

The single warning is a Starlette deprecation warning from the installed test-client compatibility layer: using httpx with starlette.testclient is deprecated and httpx2 is recommended. This warning does not indicate a failure in the merge implementation.

### Status
- Existing Base64/Clash behavior: regression suite remains green.
- Sing-box JSON merge tests: PASS.
- Xray JSON detection/merge tests: PASS.
- Full local suite: **VERIFIED — 22/22 PASS**.
- GitHub Actions for these commits: still not claimed passed because the queried commit workflow-runs endpoint returned no runs.
- Live middleware JSON E2E: **PENDING**.
- Remnawave configuration/data: unchanged.

### Next large stage
Perform controlled live E2E through the running middleware using explicit Remnawave JSON endpoints (/singbox and /json) for both A2 users. Verify response status/content type, merged outbound topology, selector references, collision-safe tags, and per-user isolation without printing credentials. Also verify the middleware route/forwarding contract before any live configuration mutation.

### Changed files
- PROJECT_JOURNAL.md (append-only entry only)

### Commit
- This journal update is the final commit of this documentation stage.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0024 — Added explicit JSON and Sing-box middleware routes

### Context
The live verification established that Remnawave can render Xray JSON through the explicit `/json` subscription suffix, while the middleware's existing `/sub/{username}` endpoint intentionally follows the normal User-Agent-selected subscription URL. A direct request to `/sub/{username}/json` and `/sub/{username}/singbox` previously returned HTTP 404 because those middleware routes did not exist.

A prior diagnostic script also incorrectly looked for `subscriptionUrl` at the root of the Remnawave API response. The actual project client already correctly handles the API envelope through `payload["response"]` when present. No application defect was found from that diagnostic result.

### Implementation
- Added explicit middleware routes:
  - `GET /sub/{username}/json`
  - `GET /sub/{username}/singbox`
- Kept the existing `GET /sub/{username}` route and its User-Agent-driven behavior intact.
- Refactored the endpoint into a shared merge handler so all three routes use the same A2 resolution, metadata handling, error mapping, and merge engine.
- Extended the Remnawave subscription client with an explicit suffix parameter supporting only `json`, `singbox`, or the existing empty suffix.
- Added URL-safe suffix construction using parsed URL components so query strings/fragments are preserved and the suffix is inserted into the path rather than appended after the query.
- Unsupported suffix values fail with a controlled `ValueError` rather than being forwarded upstream.
- Added endpoint tests proving that both A2 subscriptions receive the same requested explicit suffix.

### Design decision
The middleware now supports an explicit format contract without modifying Remnawave Response Rules. The normal endpoint remains backward-compatible, while Xray and Sing-box clients can use deterministic explicit-format URLs when required.

### Changed files
- `src/http_endpoint.py`
- `src/remnawave/subscription.py`
- `tests/test_http_endpoint.py`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commits
- `e282b5fd6e90f6dc6c6f1217206e09e8058d3135` — support explicit subscription format suffixes
- `f22b4bdc2daee87250edd937d4701d27dd0af4ed` — expose explicit JSON and Sing-box subscription routes
- `b0dfae8abe60d3e9b69441bfc5000f1b17b1c72e` — cover explicit subscription format routes
- This journal update is the documentation commit for this implementation block.

### Verification status
- Code has been committed to GitHub `dev`.
- Local/server pytest verification after this exact commit sequence: PENDING.
- Live middleware `/json` and `/singbox` E2E: PENDING.
- Remnawave configuration/data: unchanged.
- No secrets were added or committed.

### Next large stage
Synchronize the server from `origin/dev`, run the full test suite, restart the middleware from the updated code, then perform live Xray JSON and Sing-box E2E for both A2 users. Inspect only non-secret structure and fingerprints.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0025 — Fixed endpoint test doubles after suffix-contract regression

### Context
The first full server pytest run after Entry 0024 exposed a regression in three existing HTTP endpoint tests. The production endpoint now calls `RemnawaveSubscriptionClient.fetch_public(..., suffix=suffix)`, but three hand-written `FakeSubscriptions` test doubles still implemented the previous two-argument signature.

### Observed failure
The server suite reported:
- **24 passed**;
- **3 failed**;
- **1 warning**.

All three failures had the same cause:
`TypeError: ...FakeSubscriptions.fetch_public() got an unexpected keyword argument 'suffix'`.

The failures were:
- `test_merged_subscription_success_forwards_client_headers`;
- `test_profile_url_is_not_forwarded`;
- `test_malformed_subscription_is_502`.

This is a test-double contract mismatch, not evidence that the production `fetch_public` implementation or the new explicit routes are broken.

### Fix
Updated the three legacy `FakeSubscriptions.fetch_public` implementations in `tests/test_http_endpoint.py` to accept the new optional `suffix=""` argument. The normal-route tests explicitly assert that the default suffix remains empty where appropriate.

The explicit `/json` and `/singbox` tests already used the new suffix-aware signature and were left intact.

### Changed files
- `tests/test_http_endpoint.py`

### Commit
- `9d99bfdcaa673a06a69d6b4a784fedf499e800a2` — test: align endpoint doubles with subscription suffix contract

### Verification status
- GitHub code change: COMMITTED.
- Server re-run after this fix: PENDING.
- Live `/json` and `/singbox` E2E: PENDING.
- Remnawave configuration/data: unchanged.
- No secrets added or committed.

### Next large stage
Pull the new commit to the server and rerun the complete pytest suite. If green, restart the middleware from the synchronized checkout and perform the live Xray JSON and Sing-box E2E checks for both A2 users.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0026 — Live JSON merge E2E verified and Xray assertion aligned with actual Remnawave shape

### Context
The middleware was restarted from the synchronized dev checkout after Entry 0025. The health endpoint returned successfully. A controlled live E2E was executed for both A2 users using the explicit middleware routes /sub/{username}/json and /sub/{username}/singbox.

### Live middleware restart
- Previous middleware process was stopped.
- New process started with .venv/bin/python -m uvicorn src.http_endpoint:app --host 127.0.0.1 --port 18080.
- New process PID observed: 3348417.
- GET /healthz returned {"status":"ok"}.

### Live Xray JSON results
For both a2test01 and a2test02, GET /sub/{username}/json with User-Agent v2rayN/7.0 returned:
- HTTP 200;
- application/json;
- cache-control: no-store;
- a valid subscription-userinfo header;
- JSON root list[1];
- exactly 4 outbounds.

The actual live outbound tags for both users were:
- proxy — VLESS;
- direct — freedom;
- block — blackhole;
- proxy [addsub] — VLESS.

Both VLESS outbounds contained a valid settings.vnext list with an address and port present. The live routing object contained one field rule whose outboundTag was direct.

The live remarks value was rrrrrr.

This establishes that the Xray merge is functioning against the real Remnawave JSON shape: the main proxy and secondary proxy are both present, infrastructure outbounds are preserved, and the main routing configuration remains intact.

### Live Sing-box JSON results
For both a2test01 and a2test02, GET /sub/{username}/singbox with User-Agent singbox returned:
- HTTP 200;
- application/json;
- cache-control: no-store;
- a valid subscription-userinfo header;
- JSON root object;
- exactly 4 outbounds.

The live outbound tags were:
- → Remnawave — selector;
- direct — direct;
- rrrrrr — VLESS;
- rrrrrr [addsub] — secondary VLESS.

The selector members were exactly:
- rrrrrr;
- rrrrrr [addsub].

The required template sections were present, and the live structure check reported SING-BOX MERGE: OK.

### Cross-user isolation signal
The complete live response SHA-256 fingerprints differed for both A2 users and both explicit JSON formats:

- a2test01-xray.json: 7cd4986286f63d151d8e6124ebf464c90850dc0daa2d368b32bfa4f2644cf495
- a2test02-xray.json: 79b47c4565e9a96464002b7e70035f6786ddddd47db8b3ad7a7f170da00e9e04
- a2test01-singbox.json: 005f1e5ff1db4f255812129f2ad2be9ec81affa26351e2add64b8399219745fb
- a2test02-singbox.json: 5671b6f22f7aa5d32b02017d306cc79a807a32cbdebbcb74f55cd1db4d6cd875

Different fingerprints prove the two complete responses are not identical. They are an isolation signal, not by themselves proof of every credential-level isolation property; secret values were intentionally not recorded.

### Test correction discovered during live E2E
The initial live Xray assertion expected proxy tags rrrrrr and rrrrrr [addsub], but the actual Xray template uses proxy and proxy [addsub]. This caused the inspection assertion to fail even though the HTTP response and merge structure were valid.

The Sing-box assertion passed without modification.

The repository Xray merge test was aligned with the verified live shape and strengthened to assert:
- the main routing rule still targets direct;
- the main VLESS address remains in the main outbound;
- the secondary VLESS address remains in the renamed secondary outbound.

### Safety
- No Remnawave Response Rule was changed.
- No Remnawave user, subscription, node, quota, or database data was modified.
- No secrets were printed or committed.
- Temporary response files remained outside the repository.
- The middleware remained bound to loopback 127.0.0.1:18080.

### Changed files
- tests/test_merge.py — aligned Xray assertions with the verified live Remnawave structure and added routing/node preservation assertions.
- PROJECT_JOURNAL.md — append-only entry only.

### Commits
- 80fe5e1b5732bb38a0107d6e59e4f1b1a0d23112 — test: align Xray merge assertions with live Remnawave shape
- Journal update commit follows.

### Verification status
- Middleware restart and health check: VERIFIED.
- Live Xray JSON merge for a2test01: VERIFIED structurally.
- Live Xray JSON merge for a2test02: VERIFIED structurally.
- Live Sing-box JSON merge for a2test01: VERIFIED.
- Live Sing-box JSON merge for a2test02: VERIFIED.
- Cross-user response fingerprints: DIFFERENT for both explicit formats.
- Full pytest after the new test assertion change: PENDING.

### Next large stage
Pull the test assertion commit to the server, run the complete pytest suite, and then perform the final combined verification of Base64, Clash/Mihomo, Xray JSON, Sing-box JSON, A2 mapping/isolation, metadata, and failure handling. Only after that should the project move toward final audit/deployment hardening.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0027 — Fixed Base64 secondary name collision handling discovered by final live audit

### Context
The final live A2 audit reached the Base64 response for a2test01 and found that the merged body contained two distinct VLESS URIs but both URI fragments remained `#rrrrrr`. The secondary subscription was therefore present, but its client-facing name was not made collision-safe as it is in the verified Clash, Sing-box, and Xray JSON merge paths.

The safe live diagnostic established:
- decoded Base64 size: 520 bytes;
- decoded lines: 2;
- 2 VLESS URIs;
- 2 SS URIs;
- both VLESS lines had the fragment `#rrrrrr`;
- the secondary fragment did not contain `[addsub]`.

This was a real merge-semantic gap, not a transport or health failure. The earlier Base64 implementation only deduplicated exact URI strings and did not treat URI fragments as client-facing proxy names.

### Root cause
The Base64 branch of `merge_payloads()` previously performed only exact-entry deduplication:
`main entries + secondary entries → dict.fromkeys(...)`.

Unlike Clash, Sing-box, and Xray JSON, it had no collision handling for the human-readable URI fragment after `#`. When main and secondary contained different credentials/configuration but the same fragment, both remained named identically.

### Fix
Updated `src/merge.py` so the Base64 merge now:
- preserves exact duplicate entries without creating a second copy;
- extracts URI fragments safely with `urlsplit()`;
- decodes percent-encoded fragments with `unquote()` for collision comparison;
- deterministically renames a secondary colliding fragment using the existing `[addsub]`, `[addsub-2]`, ... naming policy;
- rebuilds the URI with the renamed fragment while preserving scheme, authority, path, query, and fragment structure;
- keeps entries without a fragment unchanged.

### Regression test
Added a unit test covering both VLESS and SS URI fragments. The test verifies that identical main/secondary names become:
- `rrrrrr`;
- `rrrrrr [addsub]`;
- `other`;
- `other [addsub]`.

### Changed files
- `src/merge.py`
- `tests/test_merge.py`
- `PROJECT_JOURNAL.md` (append-only entry only)

### Commits
- `5479f60b739751b9324d1549f8393379ca4b712b` — fix: rename colliding base64 subscription names
- `043a3830f059341ea199b3cc24924d5d02e7f64f` — test: cover base64 secondary name collision
- Journal update commit follows.

### Verification status
- Root cause: VERIFIED from live Base64 output and current source.
- Fix: COMMITTED to GitHub `dev`.
- Regression test: ADDED; server execution after this fix is PENDING.
- Full A2 live audit: BLOCKED at Base64 before this fix and must be rerun from the synchronized server checkout.
- Clash/Mihomo, Sing-box, and Xray JSON live merge behavior from Entry 0026 remains unchanged and previously verified.
- No Remnawave Response Rule, user, subscription, node, quota, or database data was modified.
- No secret values were recorded in the journal.

### Next large stage
Synchronize the server from `origin/dev`, run the full pytest suite, then rerun the complete live A2 audit. The Base64 check must now verify two distinct client-facing names while all other format, metadata, isolation, and error checks remain in scope.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0028 — Final A2 live E2E audit passed after Base64 collision fix

### Context
The server was synchronized from `origin/dev` at commit `bfddffc`, the Base64 collision fix from Entry 0027 was active, and the middleware was restarted from the synchronized checkout. This stage performed the final combined A2 verification across all supported client-facing formats.

### Repository synchronization
Server checkout was fast-forwarded:
- `c8137a5 → bfddffc`
- working tree remained clean and aligned with `origin/dev`.

### Full pytest
The complete test suite passed:
- **28 passed**
- **1 warning**

The only warning is the existing Starlette/httpx deprecation warning from the installed test environment:
`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`

No test failures occurred.

### Middleware restart and health
The middleware was restarted from the updated checkout with:
`.venv/bin/python -m uvicorn src.http_endpoint:app --host 127.0.0.1 --port 18080`

A new process was started and:
- GET `/healthz` returned `{"status":"ok"}`.

The service remains bound to loopback `127.0.0.1:18080`.

### Final live A2 audit
Both independent A2 users were verified:
- `a2test01`
- `a2test02`

#### Base64
For both users:
- HTTP 200;
- `text/plain; charset=utf-8`;
- decoded payload: 529 characters;
- merged client-facing names included both `rrrrrr` and `rrrrrr [addsub]`;
- the previously discovered fragment-collision defect is therefore resolved in live output.

Safe complete-response fingerprints differed:
- a2test01: `5350784b98f464cfbd650d4c60990664e560a889da389c9ce51dbb79f5a01b21`
- a2test02: `70d2d84823ee2774f5836b336721cf44267839397cce2f09b2e7c25d8fdb1f78`

#### Clash / Mihomo
For both users:
- HTTP 200;
- `text/yaml; charset=utf-8`;
- 1892 bytes;
- exactly 2 proxies;
- proxy names: `rrrrrr`, `rrrrrr [addsub]`;
- exactly 1 proxy group;
- group members: `rrrrrr`, `rrrrrr [addsub]`.

Complete-response fingerprints differed:
- a2test01: `026081040c5c57dfd7154650f304c4ba106949da6ee0870a0e4d72b56e8cc8f8`
- a2test02: `42d2c4f8882e5c4c94fbb61eab2c622224e00a0fc1f3f2c3cf1041e05246606d`

#### Sing-box
For both users:
- HTTP 200;
- `application/json`;
- 2236 bytes;
- exactly 4 outbounds;
- tags: `→ Remnawave`, `direct`, `rrrrrr`, `rrrrrr [addsub]`;
- selector contains both merged proxy names.

Complete-response fingerprints differed:
- a2test01: `005f1e5ff1db4f255812129f2ad2be9ec81affa26351e2add64b8399219745fb`
- a2test02: `5671b6f22f7aa5d32b02017d306cc79a807a32cbdebb74f55cd1db4d6cd875`

#### Xray JSON
For both users:
- HTTP 200;
- `application/json`;
- exactly 4 outbounds;
- tags: `proxy`, `direct`, `block`, `proxy [addsub]`;
- routing rule type `field`;
- routing protocol `bittorrent`;
- routing `outboundTag`: `direct`.

Complete-response fingerprints differed:
- a2test01: `7cd4986286f63d151d8e6124ebf464c90850dc0daa2d368b32bfa4f2644cf495`
- a2test02: `79b47c4565e9a96464002b7e70035f6786ddddd47db8b3ad7a7f170da00e9e04`

### Cross-user isolation
The audit confirmed different complete response fingerprints for both A2 users in all four formats:
- Base64 — different;
- Clash — different;
- Sing-box — different;
- Xray JSON — different.

This is a verified isolation signal: the two users do not receive byte-identical merged responses. Secret credential values were intentionally not recorded.

### Unknown-user error handling
Requesting:
`/sub/a2-definitely-not-existing`
returned:
- HTTP **502**;
- `application/json`;
- `{"detail":"subscription upstream error"}`.

The audit marked unknown-user handling as OK.

### Final result
The final live audit reported:
- HEALTH: OK
- BASE64: OK
- CLASH: OK
- SING-BOX: OK
- XRAY JSON: OK
- CROSS-USER ISOLATION: OK
- UNKNOWN USER HANDLING: OK
- **FINAL A2 E2E AUDIT: PASS**

This completes the current A2 merge verification stage across Base64, Clash/Mihomo, Sing-box, and Xray JSON.

### Safety / scope
- No Remnawave Response Rules were changed.
- No Remnawave users, subscriptions, nodes, quotas, or database data were modified.
- No secrets were printed into the journal or committed.
- Temporary audit artifacts remained outside the repository.
- Existing project history was preserved.

### Changed files in this stage
No production/test source changes were made during this verification stage. The stage verified the already-committed Entry 0027 fix and prior merge work.

### Commits
- Verified repository HEAD: `bfddffc` — `docs: record base64 collision fix`
- Earlier implementation commits verified by this stage:
  - `5479f60` — fix: rename colliding base64 subscription names
  - `043a383` — test: cover base64 secondary name collision
  - `bfddffc` — docs: record base64 collision fix

### Verification status
- Repository synchronization: VERIFIED.
- Full pytest: **28 passed, 1 warning**.
- Middleware restart: VERIFIED.
- Health endpoint: VERIFIED.
- Base64 live merge and collision-safe names: VERIFIED.
- Clash/Mihomo live merge: VERIFIED.
- Sing-box live merge: VERIFIED.
- Xray JSON live merge: VERIFIED.
- Cross-user isolation signal across all four formats: VERIFIED.
- Unknown-user failure handling: VERIFIED.
- Final A2 E2E audit: **PASS**.

### Next large stage
A2 merge behavior is now verified end-to-end. The next work should be treated as a separate stage: deployment hardening / operational integration (process supervision, reverse-proxy exposure only if required, restart persistence, logging/monitoring, and final documentation), without changing the verified merge semantics unless a new concrete defect is found.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0029 — Began deployment hardening with systemd supervision

### Context
After Entry 0028 established a passing live A2 E2E audit across Base64, Clash/Mihomo, Sing-box, and Xray JSON, deployment hardening was started as a separate stage. The goal is to replace the temporary `nohup` process with a persistent, non-root service while keeping the middleware on loopback and leaving Remnawave unchanged.

### Repository changes
Added a production-oriented systemd unit template:
- `deploy/remnawave-subscription-merge.service`
- dedicated `remnawave-merge` user/group;
- `Restart=on-failure` with a short restart delay;
- boot persistence through `multi-user.target`;
- loopback binding at `127.0.0.1:18080`;
- environment loaded only from the local `.env` file;
- no-new-privileges, private temporary directory, protected home/system, restrictive umask;
- stdout/stderr intended for journald rather than an application log file.

Added deployment documentation:
- `deploy/README.md` with installation, permissions, service operations, update procedure, health check, and reverse-proxy boundary.
- `.env.example` containing variable names and placeholders only.

Updated:
- `ROADMAP.md` to mark deployment hardening as in progress and defer containerization until host deployment is stable.

### Safety decisions
- The middleware remains intended for loopback-only operation; port 18080 must not be exposed directly.
- No reverse-proxy configuration was invented or changed because the existing host proxy topology has not yet been inspected in this stage.
- No Remnawave users, subscriptions, nodes, quotas, Response Rules, or database data were modified.
- No API token or subscription credential was added to Git.

### Commits
- `253f762df6e8eacc81d56768a96bb41977141f20` — feat: add systemd service template
- `101750262987fdd33b487db9e8225a86bebce2a4` — docs: add deployment hardening guide
- `355024d7d0cabe270f739ed7692a59d180ea4060` — docs: add deployment environment example
- `fb7a1da1370a7f36b155ba6fb870c95d27ce9ae8` — docs: update deployment hardening roadmap
- This entry is the documentation commit for the stage.

### Verification status
Repository-side deployment artifacts are committed. Server-side installation and runtime verification are **PENDING**.

The next action is to synchronize the server from `origin/dev`, inspect the current `.env` ownership/permissions without printing its contents, install the dedicated system user and systemd unit, start the service, verify status and `/healthz`, confirm only loopback port 18080 is listening, and then rerun the A2 live audit against the supervised process.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0030 — Deployment hardening verified: systemd non-root runtime

### Context
The deployment-hardening stage from Entry 0029 was completed on the live test server. The temporary `nohup` middleware process was replaced by the repository's systemd service template. The service now runs persistently as the dedicated `remnawave-merge` user, loads its configuration from a protected local environment file, and remains bound only to loopback.

### Initial deployment failure and correction
The first systemd installation attempt failed because the repository working tree did not contain the expected `/opt/remnawave-subscription-merge/.env` file. The previous `nohup` process was still running and its environment inspection confirmed that the four required `REMNAWAVE_*` variables had been supplied directly through the shell environment.

No secret values were printed or recorded. The existing values were transferred locally into a protected `.env` file without displaying them.

The resulting environment file was verified as:
- owner/group: `root:remnawave-merge`;
- permissions: `640`;
- location: `/opt/remnawave-subscription-merge/.env`.

The earlier systemd failures in journald are historical records from before the file was created. The final start attempt succeeded.

### Systemd runtime verification
The temporary `nohup` process was stopped and the systemd service was started successfully.

Verified:
- service: `remnawave-subscription-merge.service`;
- boot enablement: `enabled`;
- runtime state: `active (running)`;
- runtime PID after restart: `3365706`;
- process executable: `/opt/remnawave-subscription-merge/.venv/bin/python`;
- runtime user/group: `remnawave-merge`;
- required `REMNAWAVE_*` environment keys are present in the supervised process;
- `PYTHONDONTWRITEBYTECODE` is present;
- `GET /healthz` returned `{"status":"ok"}`;
- listener: `127.0.0.1:18080` only.

A service restart was explicitly tested. The PID changed from `3364422` to `3365706`, the service remained active, and `/healthz` remained healthy after the restart.

### Live A2 verification after migration
The supervised systemd process was exercised against both independent A2 users:
- `a2test01`;
- `a2test02`.

#### Base64
Both requests returned HTTP 200. The decoded merged body was 529 characters for each user and contained:
- main URI name: `rrrrrr`;
- secondary URI name: `rrrrrr [addsub]`.

This confirms that the previously fixed Base64 fragment-collision behavior remains active after the deployment migration.

#### Clash / Mihomo
Both users returned HTTP 200 and 1892-byte YAML documents.

For each:
- exactly 2 proxies;
- proxy names: `rrrrrr`, `rrrrrr [addsub]`;
- exactly 1 proxy group;
- group `→ Remnawave` contains both proxy names.

#### Sing-box
Both users returned HTTP 200 and 2236-byte JSON documents.

For each:
- exactly 4 outbounds;
- tags: `→ Remnawave`, `direct`, `rrrrrr`, `rrrrrr [addsub]`;
- the selector `→ Remnawave` contains both proxy names.

#### Xray JSON
Both users returned HTTP 200. The live Xray response was verified as valid JSON with the actual Remnawave root shape:
- root type: list;
- root length: 1;
- single item type: dict;
- top-level keys: `dns`, `routing`, `inbounds`, `outbounds`, `remarks`.

The first inspection script incorrectly assumed the Xray root was a dictionary and raised `AttributeError`. This was a diagnostic-script contract error, not an application failure. A corrected structure-aware inspection subsequently confirmed the real root-list shape and successful JSON serialization.

A cross-user content comparison found user-specific UUID values present only in the corresponding user's response:
- `a2test01`: two unique UUID values;
- `a2test02`: two different unique UUID values.

Complete-response SHA-256 fingerprints also differed:
- `a2test01`: `7cd4986286f63d151d8e6124ebf464c90850dc0daa2d368b32bfa4f2644cf495`;
- `a2test02`: `79b47c4565e9a96464002b7e70035f6786ddddd47db8b3ad7a7f170da00e9e04`.

This provides stronger non-secret cross-user isolation evidence for the live Xray path.

### Failure-path verification
The supervised service returned:
- unknown user `/sub/a2-definitely-not-existing` → HTTP 502;
- response body: `{"detail":"subscription upstream error"}`.

No internal Remnawave error details or credentials were exposed.

### Safety and scope
- No Remnawave Response Rule was modified.
- No Remnawave user, subscription, node, quota, or database data was modified.
- No API token or other secret was printed into the journal or committed.
- The middleware remains loopback-only on `127.0.0.1:18080`.
- The deployment service uses a dedicated non-root runtime account.
- Existing project history was preserved; this entry was appended only.

### Diagnostic corrections recorded
Two live inspection scripts made incorrect assumptions during this stage:
1. a content-type/Xray inspection attempted to treat the Xray root as a dictionary;
2. the follow-up inspector again assumed a dictionary before discovering the actual root list.

Both failures were in the inspection commands only. The HTTP endpoint itself returned successful responses. The corrected inspector verified the actual live Xray shape.

### Changed files
- `PROJECT_JOURNAL.md` — append-only entry only.

### Commits
- Repository implementation artifacts verified from `origin/dev` at `2ee79b6` before this server-side completion record.
- This entry is committed separately as the journal update.

### Verification status
- Protected environment configuration: VERIFIED.
- systemd installation: VERIFIED.
- systemd boot enablement: VERIFIED.
- non-root runtime: VERIFIED.
- service restart recovery: VERIFIED.
- loopback-only listener: VERIFIED.
- health before/after restart: VERIFIED.
- Base64 A2 live merge after migration: VERIFIED.
- Clash/Mihomo A2 live merge after migration: VERIFIED.
- Sing-box A2 live merge after migration: VERIFIED.
- Xray JSON A2 live merge after migration: VERIFIED.
- stronger cross-user Xray isolation evidence: VERIFIED.
- unknown-user failure handling: VERIFIED.
- Remnawave mutation: NOT PERFORMED.

### Remaining deployment work
The core host-level deployment hardening is now verified. Remaining deployment-specific work includes reverse-proxy integration only if/when the client-facing architecture requires it, plus any final production rollout procedure and final audit documentation. Port 18080 must remain non-public unless a deliberately verified reverse-proxy/network design requires otherwise.

### Status
Deployment hardening core: **COMPLETE / VERIFIED**.
A2 merge semantics: **preserved and re-verified after supervised deployment**.
Final project audit: **NOT YET COMPLETE**.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»



## 2026-10-06 — Entry 0031 — Final-audit repository consistency and Remnawave client contract coverage

### Context
The final project audit was started after Entry 0030. The journal was read before changes, and the repository state on `dev` was compared with the documented status and the live verification already recorded in Entries 0028–0030.

### Audit findings
The repository implementation was materially ahead of two project documents:
- `README.md` still said live end-to-end output and automated CI remained to be verified, although Entry 0028/0030 records those checks as passed.
- `ROADMAP.md` still marked stages B–F as upcoming even though the corresponding access, merge, A2, endpoint, and automated verification work had already been implemented and live-tested.

A repository test gap was also confirmed:
- there was no dedicated `tests/test_remnawave_client.py`;
- the authenticated Remnawave client was live-verified previously, but its request/response contract had insufficient isolated automated coverage.

### Changes
Added `tests/test_remnawave_client.py` with controlled `httpx.MockTransport` coverage for:
- Bearer authorization and encoded usernames;
- Remnawave envelope and root-level user response shapes;
- 404 mapping to the safe not-found exception;
- upstream HTTP error mapping without leaking response bodies;
- invalid JSON handling;
- incomplete user response rejection;
- deterministic A2 secondary derivation;
- same-ID A2 mapping rejection.

Updated `README.md` to reflect the verified live A2, CI, and systemd status while keeping reverse-proxy exposure as a remaining deployment-specific concern.

Updated `ROADMAP.md` to synchronize stages B–F and deployment status with the actual implementation and verification state. Stage H is explicitly marked partial/live-verified and Stage I remains in progress.

### Verification
GitHub Actions CI run #64 for the new Remnawave client tests completed successfully:
- commit: `fe7ca07d9678e98295118a18ce3e2bfd4195297c`;
- result: SUCCESS.

The subsequent documentation commits also triggered CI runs #65 and #66; their execution was observed during this stage. The latest repository commits are:
- `ce480da72b8bf2fd1ee52358afe71714183cd13c` — README status update;
- `de7d622f203ff757ab81790cfbae615b01b11d9c` — roadmap synchronization.

No production Remnawave data or configuration was changed. No secrets were added, printed, or committed.

### Remaining audit work
The repository consistency/test-contract portion is complete. The final production audit still needs:
- dependency/security review;
- Xray/Sing-box edge-case decision and coverage where justified by the actual Remnawave output;
- live deployment configuration review;
- reverse-proxy/client-facing integration if required;
- final rollout and rollback procedure;
- final client compatibility checks before production status.

### Changed files
- `tests/test_remnawave_client.py`
- `README.md`
- `ROADMAP.md`
- `PROJECT_JOURNAL.md` — append-only entry only.

### Commits
- `fe7ca07d9678e98295118a18ce3e2bfd4195297c` — test: cover Remnawave client contract
- `ce480da72b8bf2fd1ee52358afe71714183cd13c` — docs: update README verified status
- `de7d622f203ff757ab81790cfbae615b01b11d9c` — docs: synchronize roadmap with implementation
- This journal update is committed separately below.

### Status
Repository consistency audit: **COMPLETE**.
Remnawave client contract automated coverage: **ADDED / CI VERIFIED**.
Final production audit: **IN PROGRESS**.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»



## 2026-10-06 — Entry 0032 — Dependency/security hardening: bounded subscription responses

### Context
The final production audit continued with the dependency/security stage. The previously added CI action SHA pinning and `pip-audit` job remain present from the earlier security sub-block. During code review, a concrete runtime resource-exhaustion risk was confirmed in the public subscription fetch path: the middleware previously used `response.text` after a full upstream GET, with no application-level maximum response size.

### Security finding and decision
A Remnawave-rendered subscription is client-facing data and is parsed as Base64, YAML, or JSON after retrieval. An unexpectedly large upstream body could therefore consume excessive memory and parser resources.

The implementation was changed to:
- read the upstream response as a stream;
- reject a declared `Content-Length` above the configured maximum before reading the body;
- enforce the same maximum while consuming chunked/unknown-length responses;
- decode and parse the body only after the size check has passed;
- keep the existing finite HTTP timeout and no-redirect behavior.

Default maximum:
- `8 MiB` (`8388608` bytes).

The limit is configurable through:
- `REMNAWAVE_MAX_SUBSCRIPTION_BYTES`.

A non-positive or non-integer configured value is rejected during configuration loading.

### Automated coverage
Added tests for both oversized-response paths:
- declared `Content-Length` exceeding the limit;
- streamed response exceeding the limit without relying on `Content-Length`.

The tests use synthetic data and a small test-only limit; no production secret or real subscription body is used.

### Documentation
Updated:
- `.env.example` with the new optional limit;
- `SECURITY.md` with the response-size requirement;
- `deploy/README.md` with the deployment configuration entry.

### Changed files
- `src/remnawave/config.py`
- `src/remnawave/subscription.py`
- `tests/test_http_endpoint.py`
- `.env.example`
- `SECURITY.md`
- `deploy/README.md`
- `PROJECT_JOURNAL.md` — this append-only entry.

### Commits
Sequential commits were created while preserving the append-only workflow:
- `9eeb846f81e7d0245b3b2bb9f15174a1c2a8e748` — security: bound subscription response size
- `76f62c6f0a8a8d3d40fa90c62bff3945aee0a197` — security: stream and cap subscription responses
- `491ba1b039f8fe1b9e48d460ab9c649902cf1c8a` — test: cover oversized subscription responses
- `3c11b04472993aa7ad4c1be8e60a4e94a06b52c5` — test: isolate oversized response fixture limit
- `5699cee3bf8f39c2bf5083461560ebdf62a94125` — docs: document subscription response limit
- `aaff178bee1942785a56e155daa754c3a9d0e29b` — docs: document subscription size hardening
- `79d019ee969c5b84229888bb4b8a3efe92a654c5` — docs: document deployment response limit
- This journal entry is committed separately below.

### Verification status
Repository changes are committed on `dev`. GitHub workflow lookup for the latest documentation commit had not yet returned a workflow run at the time of this entry, so CI execution of the new tests and `pip-audit` is **NOT YET VERIFIED** in this stage.

The security implementation itself is present in the repository and the new tests are committed. The previous CI security job remains configured to run `pip-audit`.

### Remaining work
The dependency/security stage is not yet fully closed until the CI run is observed and checked. After that, continue the planned audit sequence with:
1. Xray/Sing-box edge-case review;
2. live deployment/reverse-proxy configuration review;
3. final client compatibility checks;
4. rollback/release procedure;
5. final production verdict.

### Status
Subscription response-size hardening: **IMPLEMENTED / COMMITTED**.
Automated CI verification of this hardening and `pip-audit`: **PENDING**.
Final production audit: **IN PROGRESS**.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0033 — Xray/Sing-box edge-case audit: secondary reference rewrite

### Context
The next final-audit block reviewed the already verified Xray and Sing-box merge semantics for reference integrity under tag collisions. The goal was to test an edge case that ordinary duplicate-tag tests do not cover: a secondary Sing-box outbound can reference another secondary outbound by tag.

### Finding
The Sing-box merge already renamed a colliding secondary tag, but the existing implementation did not rewrite references inside other secondary outbounds after that rename. This could leave a selector/urltest or similar outbound pointing at the old colliding tag.

### Fix
Updated src/merge.py so that, after secondary tags are resolved, the accumulated secondary tag replacements are applied recursively to the secondary outbound objects before they are appended to the merged configuration.

This keeps the main configuration untouched while preserving internal references in the secondary configuration after collision renaming.

### Automated coverage
Added tests covering:
- a secondary selector referencing a colliding secondary VLESS tag;
- a secondary urltest outbound referencing the same colliding tag.

Both cases verify that the reference is rewritten to the generated [addsub] tag.

### Changed files
- src/merge.py
- tests/test_merge.py
- PROJECT_JOURNAL.md — append-only entry only.

### Commits
- cd7a7ada7e762375a68049ff367c58710e019e97 — fix: rewrite secondary sing-box outbound references
- 06ed345e97143e582d0f0c10e4394db47daba37f — test: cover sing-box duplicate reference rewrites
- This journal update is committed separately below.

### Verification status
The implementation and tests are committed on dev. GitHub CI for the new commits has not yet been observed, so this edge-case block is IMPLEMENTED / CI PENDING, not yet CI-verified.

### Remaining work
Continue the final audit with:
1. complete Xray/Sing-box edge-case review;
2. live deployment/reverse-proxy configuration review;
3. final client compatibility checks;
4. rollback/release procedure;
5. final production verdict.

### Status
Sing-box duplicate-reference hardening: IMPLEMENTED / COMMITTED.
CI verification: PENDING.
Final production audit: IN PROGRESS.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0034 — Merge edge-case hardening: reject ambiguous source tags and narrow Sing-box reference rewrites

### Context
The Xray/Sing-box edge-case audit continued after Entry 0033. Review of the collision maps found a second ambiguity class: duplicate proxy/tag names inside one source configuration. A single replacement map cannot represent two source objects with the same identifier without potentially rewriting references to the wrong object.

### Finding and decision
The merge layer now fails closed when a single Clash, Sing-box, or Xray source contains duplicate proxy/tag identifiers. Cross-source collisions remain supported and are still deterministically renamed with the existing [addsub] convention.

The previous recursive Sing-box string replacement was also narrowed. Secondary Sing-box references are now rewritten only in reference-bearing fields currently handled by the merger (outbounds and detour), preventing a collision such as proxy from accidentally changing unrelated data such as a server/address string that happens to equal the outbound tag.

### Automated coverage added
Added tests for:
- duplicate Clash proxy names within one source being rejected;
- duplicate Sing-box/Xray tags within one source being rejected;
- unrelated Sing-box string fields remaining unchanged after a tag collision is renamed.

Existing cross-source collision and secondary-reference tests remain intact.

### Changed files
- src/merge.py
- tests/test_merge.py
- PROJECT_JOURNAL.md — append-only entry only.

### Commits
- abe3927c9ae84976de5ef4e9a48528a842cbd24f — fix: reject ambiguous outbound names and narrow reference rewrites
- 15dfc3698a51cd074cd6938eda311aea486e9ccb — test: cover ambiguous merge source names
- cb2fa9a68b717c34807407f674514277bd5255e6 — repository contents update with no source-tree change; no functional change
- This journal entry is committed separately below.

### Verification status
The implementation and tests are committed on dev. GitHub Actions lookup for the latest test commit currently returns no associated workflow run/status, so CI verification is PENDING. No production Remnawave configuration or data was changed.

### Remaining edge-case audit
Continue checking Xray/Sing-box/Clash structural edge cases and then move to the live deployment/reverse-proxy/client compatibility block. Final production verdict remains open until those checks and CI verification are complete.

### Status
Ambiguous source identifier hardening: IMPLEMENTED / COMMITTED.
Sing-box reference rewrite narrowing: IMPLEMENTED / COMMITTED.
CI verification: PENDING.
Final production audit: IN PROGRESS.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»


## 2026-10-06 — Entry 0035 — Xray reference rewrite boundary hardening

### Context
The remaining Xray edge-case review found that the merge path still used the old broad recursive string replacement for renamed secondary outbound tags. This could alter unrelated string-valued configuration data when it happened to equal an outbound tag.

### Fix
Added a dedicated Xray reference rewrite routine and replaced the broad string rewrite for secondary Xray outbounds. The routine only rewrites known reference-bearing fields handled by the merge layer, including `outboundTag`, `balancerTag`, `detour`, `selector`, and `subjectSelector`. Ordinary strings remain unchanged.

This is deliberately scoped to the secondary outbounds actually appended by the merger; the merger continues to preserve the main Xray configuration rather than importing the secondary top-level routing configuration.

### Automated coverage
Added tests proving:
- an unrelated Xray string field equal to a colliding tag is preserved;
- an Xray `detour` reference to a renamed secondary tag is rewritten.

### Changed files
- src/merge.py
- tests/test_merge.py
- PROJECT_JOURNAL.md — append-only entry only.

### Commits
- e06e61ec3d75aeb84a8ae20ebbb376201b3c4235 — fix: narrow Xray outbound reference rewrites
- 83122efdfe4c2416632b795e0c324783c693dadb — test: cover Xray reference rewrite boundaries
- 2f9955a06488eb7e8294df86b7e338bc4c2b7f20 — test: correct Xray reference coverage
- This journal entry is committed separately below.

### Verification status
The implementation and tests are committed on dev. GitHub Actions verification for the latest test commit is still pending/not returned by the repository workflow lookup. No production Remnawave data or configuration was changed.

### Status
Xray reference rewrite hardening: IMPLEMENTED / COMMITTED.
CI verification: PENDING.
Final production audit: IN PROGRESS.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»

## 2026-10-06 — Entry 0036 — Clash reference boundary hardening and CI regression closure

### Context
The Xray/Sing-box/Clash edge-case audit continued after Entry 0035. Review of the Clash merge path found that secondary proxy-name replacements were still applied through a broad recursive string replacement to the entire proxy-group object.

### Finding and fix
A proxy name collision could therefore rewrite unrelated group metadata when that metadata happened to equal the colliding proxy name. For example, a secondary group named `proxy` could incorrectly become `proxy [addsub]` merely because a secondary proxy with the same name was renamed.

The Clash merge path was narrowed so that collision replacements are applied only to the proxy-group `proxies` reference list. Group names and other configuration fields are preserved unchanged.

### Automated coverage
Added a regression test proving that:
- a secondary group name equal to a colliding proxy name remains unchanged;
- the actual proxy reference inside that group's `proxies` list is rewritten to the generated `[addsub]` name.

### CI regression discovered and fixed
While validating this block, GitHub Actions runs for the recent merge-hardening commits were inspected instead of assuming success. Runs 85–89 had failed during test collection because `tests/test_http_endpoint.py` contained a malformed oversized-response test block:
- `_small_config` was incorrectly declared as an async test helper;
- an `async with` statement was present in a synchronous test;
- the streamed oversized-response test used the normal configuration instead of the deliberately small test limit;
- required `httpx` and `pytest` imports were missing.

This was a test-suite regression, not a runtime application failure. The test block was corrected and restored to explicit async tests with the 16-byte fixture limit.

### Verification
GitHub Actions CI run #90 for commit `7800fdbea42aa17677f8469ed0461f836d491001` completed successfully:
- `pytest -q`: SUCCESS;
- `pip-audit`: SUCCESS.

This closes the previously pending automated verification for the recent response-size hardening and merge edge-case changes.

### Changed files
- `src/merge.py`
- `tests/test_merge.py`
- `tests/test_http_endpoint.py`
- `PROJECT_JOURNAL.md` — append-only entry only.

### Commits
- `2fd8fe6737adc4dc9cc8d8e645d01bba52072712` — fix: narrow Clash proxy reference rewrites
- `2cd38dc8e47df500be4b5f728b25d2a41fd07e70` — test: cover Clash reference rewrite boundaries
- `7800fdbea42aa17677f8469ed0461f836d491001` — fix: restore async oversized subscription tests
- CI run #90: `37507700818` — SUCCESS.

### Status
Clash reference rewrite boundary hardening: **IMPLEMENTED / CI VERIFIED**.
Xray/Sing-box reference hardening from Entries 0033–0035: **CI VERIFIED by the repaired full test suite**.
Subscription response-size hardening from Entry 0032: **CI VERIFIED, including pip-audit**.
Final production audit: **IN PROGRESS**.

### Remaining work
The next large audit block is the live client-facing deployment/reverse-proxy and production rollout review, followed by final client compatibility and rollback/release verification. No production Remnawave data or configuration was changed in this stage.

### Mandatory preservation statement
«старые изменения не тронуты, новые внесены.»
