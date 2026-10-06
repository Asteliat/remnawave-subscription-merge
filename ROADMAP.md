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

**Next**

Build a small upstream client with configurable Remnawave endpoint, credential injection through environment, user/subscription resolution, secondary subscription derivation, timeout and status handling, structured secret-safe errors, and mocked tests before real integration.

## C — Merge engine

Implement and test base64/URI, Clash JSON, sing-box JSON, deterministic deduplication, malformed/unsupported input handling, and metadata policy.

## D — A2 identity and isolation

Prove two users map to two different secondary subscriptions, one user's secondary data can never enter another user's result, missing/expired secondary subscriptions fail safely, and duplicate nodes/configurations are deterministic.

## E — HTTP endpoint

Connect client request, identity resolution, two upstream fetches, merge engine, response body/metadata, and controlled failures.

## F — Automated verification

Add unit tests, format fixtures, A2 isolation tests, upstream failure tests, malformed-response tests, metadata tests, and integration tests with a controlled fake upstream.

## G — Deployment hardening

**In progress**

- non-root systemd runtime;
- restart-on-failure and boot persistence;
- journald-based operational logs;
- health endpoint verification;
- no direct public exposure of port 18080;
- deployment/update procedure;
- reverse-proxy integration remains deployment-specific.

Containerization is intentionally deferred until the host deployment is stable.

## H — Remnawave integration

Use controlled test users/subscriptions and verify independent quotas, merged configuration visibility, client compatibility, expiry behavior, and recovery after upstream failure. No destructive changes to existing Remnawave.

## I — Final audit

Before production status: full test suite, configuration/secret audit, dependency audit where available, container/build check, runtime check, Git history review, explicit limitations, and rollback procedure.
