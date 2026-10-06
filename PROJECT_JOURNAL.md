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
