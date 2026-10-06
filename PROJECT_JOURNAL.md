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
- PostgreSQL 16;
- Valkey 9;
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
