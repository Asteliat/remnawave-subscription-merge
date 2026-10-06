# Remnawave Subscription Merge

Minimal stateless middleware for the A2 use case.

## What it does

A user has:

- one visible/main Remnawave subscription;
- one hidden personal secondary subscription with its own traffic quota.

The middleware combines both into one client-facing subscription response.

The secondary subscription is never shared between users, and Remnawave remains the source of truth.

## Scope

Initial target formats:

- base64/URI;
- Clash JSON;
- sing-box JSON.

The service intentionally does not modify Remnawave and does not include an admin panel, billing system, Telegram bot, HWID subsystem, or unrelated middleware features.

## Documentation

- `PROJECT_JOURNAL.md` — immutable append-only project history;
- `ARCHITECTURE.md` — data flow and merge semantics;
- `ROADMAP.md` — implementation stages;
- `SECURITY.md` — secret and endpoint security rules.

## Current status

Foundation is complete on the `dev` branch. Application code and real Remnawave integration are not yet claimed complete.
