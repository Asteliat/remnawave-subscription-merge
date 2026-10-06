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

The A2 access/merge foundation and the corrected public-subscription integration are implemented on dev. Live end-to-end merged output and automated CI execution remain to be verified.
