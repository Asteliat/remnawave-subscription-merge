# Remnawave Subscription Merge — Roadmap

This roadmap is intentionally limited to the A2 subscription-merge middleware.

## A — Foundation

**Status: complete after this stage**

- repository and working branch;
- immutable project journal;
- architecture;
- security model;
- implementation roadmap;
- secret/configuration policy.

## B — Remnawave access layer

**Complete**

Implemented configurable Remnawave endpoint, environment-injected credentials, user/subscription resolution, deterministic secondary derivation, timeout/status handling, structured secret-safe errors, and mocked client-contract tests.

## C — Merge engine

**Complete**

Base64/URI, Clash/Mihomo YAML, sing-box JSON, Xray JSON, deterministic deduplication/name collision handling, malformed/unsupported input handling, and explicit metadata policy are implemented and live-verified.

## D — A2 identity and isolation

**Complete / verified**

Per-user `_addsub` mapping and cross-user response isolation were verified with independent live test users. Missing-user failure is covered. No shared secondary subscription is used.

## E — HTTP endpoint

**Complete / verified**

Client request headers, identity resolution, two upstream public-subscription fetches, merge engine, response metadata, explicit format routes, and controlled 502/504 failures are implemented and live-tested.

## F — Automated verification

**Complete / verified**

Unit/format/metadata/HTTP tests and controlled Remnawave client-contract tests are present. Full pytest has passed with 28 tests; CI run #63 on `dev` succeeded. Live A2 E2E verification also passed.

## G — Deployment hardening

**Complete / verified**

- non-root systemd runtime;
- restart-on-failure and boot persistence;
- journald-based operational logs;
- health endpoint verification;
- no direct public exposure of port 18080;
- deployment/update procedure;
- reverse-proxy integration remains deployment-specific.

Containerization is intentionally deferred until the host deployment is stable.

## H — Remnawave integration

**Partially complete / live verified**

Controlled test users/subscriptions, independent A2 outputs, merged configuration visibility, response-rule-driven formats, and upstream failure handling are verified. Real client compatibility, expiry/recovery edge cases, and production reverse-proxy rollout remain.

## I — Final audit

**In progress**

Repository/runtime audit is underway. Remaining gates are dependency/security review, production reverse-proxy design, final rollout/rollback procedure, and final live client compatibility checks.
