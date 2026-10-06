# Remnawave Subscription Merge

Minimal stateless middleware for the A2 use case.

## What it does

A user has:

- one visible/main Remnawave subscription;
- one hidden personal secondary subscription with its own traffic quota.

The middleware combines both into one client-facing subscription response for the user's Telegram-bot flow.

The secondary subscription is never shared between users, and Remnawave remains the source of truth.

## Remnawave integration

The protected raw subscription API is an internal Remnawave DTO. The middleware does not treat that DTO as a client-facing profile.

Instead it:

1. resolves the main user and deterministic secondary user through the authenticated API;
2. fetches both users' public subscription URLs;
3. forwards the client User-Agent and HWID/device headers to both upstream subscriptions;
4. lets Remnawave's subscription response rules render the client format;
5. merges the two rendered bodies and their subscription-userinfo metadata.

Remnawave's public subscription protocol supports base64 URI, Xray/sing-box JSON, and Clash/Mihomo YAML selected by client request headers or explicit format suffixes. citeturn0search0turn0search1

## Metadata

subscription-userinfo is merged explicitly:

- download/upload are summed;
- expiry is the later expiry;
- total=0 remains unlimited if either subscription is unlimited.

The upstream profile-web-page-url is deliberately not forwarded because it identifies one individual subscription rather than the merged endpoint.

## Scope

The service intentionally does not modify Remnawave and does not contain unrelated Telegram-bot business logic, admin UI, billing system, HWID subsystem, or unrelated middleware features.

## Documentation

- PROJECT_JOURNAL.md — immutable append-only project history;
- ARCHITECTURE.md — data flow and merge semantics;
- ROADMAP.md — implementation stages;
- SECURITY.md — secret and endpoint security rules.

## Current status

The A2 access/merge foundation, corrected public-subscription integration, and host-level deployment hardening are implemented on `dev`. Live end-to-end output, cross-user isolation, systemd supervision, and automated CI have been verified. Final production exposure through a reverse proxy remains deployment-specific.


## Rezeis admin integration

The optional runtime integration adds explicit operator-selected subscription pairs without
changing the Rezeis or Reiwa source repositories.

Flow:

1. Rezeis admin lists the existing subscriptions from `GET /api/admin/subscriptions`.
2. The injected runtime addon adds **Слияние подписок** to the admin UI.
3. The operator selects one **Основная** and one **Подключаемая** subscription.
4. The addon sends only the Rezeis subscription IDs and user Telegram IDs.
5. The merge service validates the current Rezeis Bearer token against `/api/admin/auth/me`.
6. The merge service resolves both selected rows through Rezeis user detail and reads their stored `configUrl`.
7. The pair is stored in the merge service's own SQLite file, outside Rezeis.
8. The service returns a stable client URL such as `/sub/merge/<pair-id>`.

The runtime addon lives at `integrations/rezeis/admin-addon.js`. It is intentionally an
overlay artifact: copy it into the running Rezeis container and inject it into the already
served SPA shell. Do not commit it into the official Rezeis/Reiwa repositories.

Required integration settings:

- `REZEIS_BASE_URL` — Rezeis admin base URL.
- `MERGE_DATA_DIR` — persistent directory for selected pair mappings.
- The normal `REMNAWAVE_*` settings remain required for the middleware itself.

The selected-pair path preserves the existing client header forwarding, parallel upstream
fetch, response-size limits, subscription-userinfo merge, and format-specific merge logic.
