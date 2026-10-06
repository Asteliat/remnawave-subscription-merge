# Remnawave Subscription Merge — Security

## Secrets

Receive Remnawave credentials through environment variables or an external secret mechanism.

Never commit API tokens, passwords, webhook secrets, private keys, session cookies, or real subscription URLs containing credentials or private identifiers.

Example configuration names may be documented, but example values must be placeholders.

## Logs

Logs may contain request timing, upstream status, format selected, and non-sensitive correlation identifiers.

Logs must not contain authorization headers, API tokens, cookies, full private subscription URLs, full subscription bodies, or user secrets.

## Upstream requests

- Use HTTPS in deployed environments.
- Verify TLS certificates.
- Set finite connect/read/request timeouts.
- Do not follow arbitrary redirects from untrusted sources.
- Send only the required authorization material to the configured Remnawave endpoint.

## Client endpoint

The merge endpoint is sensitive because possession of a valid subscription URL may grant access to the user's configuration. Do not expose debugging information in client errors or upstream credentials in response headers. Do not add endpoints that enumerate users or subscriptions.

## SSRF boundary

The Remnawave upstream target is configuration, not user input. The request handler must not accept an arbitrary upstream URL from the client.

## Error handling

Return stable, minimal errors to clients. Keep detailed upstream diagnostics server-side and secret-safe.

## Testing

Fixtures should use synthetic users, URLs, tokens, and subscription bodies. Any accidental secret exposure must be removed from active code/configuration and documented without recording the secret itself.
