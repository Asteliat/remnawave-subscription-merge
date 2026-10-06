# Remnawave Subscription Merge — Architecture

## Purpose

A small, stateless middleware for the A2 model: one visible/main Remnawave subscription plus one hidden, personal secondary subscription are presented to the client as one merged subscription.

The middleware is not a replacement for Remnawave and does not modify Remnawave data.

## A2 invariants

1. Every user has an independent secondary subscription.
2. Secondary subscriptions are never shared between users.
3. The client-facing result represents one merged subscription.
4. The main subscription remains the identity anchor.
5. The mapping from main identity to secondary identity is deterministic.
6. No application database is required by the initial design.
7. Upstream Remnawave remains the source of truth.

Initial mapping candidate: `<main_username>` -> `<main_username>_addsub`.

## Request flow

```text
Client
  |
  | GET merged subscription
  v
Merge HTTP endpoint
  |
  +--> resolve main subscription/user
  +--> derive hidden personal subscription
  +--> fetch main body
  +--> fetch secondary body
  +--> detect supported representation
  +--> merge + deduplicate
  +--> apply explicit metadata policy
  v
One client-facing response
```

## Boundaries

Middleware owns request validation, deterministic A2 mapping, upstream orchestration, format detection, format-specific merging, safe deduplication, metadata policy, controlled errors, and secret-safe diagnostics.

Remnawave owns users, subscriptions, quotas, nodes, source data, expiry, and access state.

Explicitly outside core scope: admin UI, billing, Telegram bot logic, HWID management, changes to Remnawave, general middleware orchestration, and unrelated analytics.

## Merge semantics

### Base64 / URI

Decode the subscription payload, normalize line-oriented entries, remove exact duplicates, preserve valid ordering, and re-encode for the client. Do not silently discard entries merely because they are not semantically understood.

### Clash JSON

Merge supported proxy/configuration collections with deterministic duplicate handling. Preserve unrelated top-level fields according to an explicit schema policy rather than blindly overlaying JSON objects.

### sing-box JSON

Merge supported outbound/node definitions while preserving required top-level semantics. Do not recursively merge arbitrary JSON.

### Unsupported or malformed data

Return a controlled error. Never guess a format or return a partially merged configuration.

## Metadata

Body merging and HTTP metadata are separate concerns. The implementation must explicitly define and test `subscription-userinfo`, content type, content disposition, cache headers, upstream status handling, and response encoding. Conflicting upstream headers must not be copied blindly.

## Statelessness

The initial service keeps no per-user mapping database. Mapping is derived from the main subscription identity. If future Remnawave behavior proves this insufficient, persistent state requires a documented architecture change.

## Failure model

Fail closed: main failure, secondary failure, missing/expired secondary, malformed body, or unsupported format must not produce a partial merged subscription. No cross-user fallback is permitted.

## Security model

Remnawave credentials are environment/configuration inputs, never source-controlled. Secrets are never included in URLs, logs, test fixtures, or errors. Upstream TLS verification remains enabled. The endpoint exposes only the minimum required client information.
