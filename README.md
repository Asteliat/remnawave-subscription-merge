# Remnawave Subscription Merge

Minimal stateless middleware for the A2 use case.

## What it does

A user has:

- one visible/main Remnawave subscription;
- one hidden personal secondary subscription with its own traffic quota.

The middleware combines both into one client-facing subscription response for the user's Telegram-bot flow.

The secondary subscription is never shared between users, and Remnawave remains the source of truth.

## Scope

Initial target formats:

- base64/URI;
- Clash JSON;
- sing-box JSON.

The service intentionally does not modify Remnawave and does not contain unrelated Telegram-bot business logic, admin UI, billing system, HWID subsystem, or unrelated middleware features.

## Documentation

- `PROJECT_JOURNAL.md` — immutable append-only project history;
- `ARCHITECTURE.md` — data flow and merge semantics;
- `ROADMAP.md` — implementation stages;
- `SECURITY.md` — secret and endpoint security rules.

## Current status

Stage A foundation and the Stage B Remnawave access/merge foundation are implemented on the `dev` branch. Live credentials, production integration, HTTP client endpoint, and automated CI execution are not yet claimed complete.
