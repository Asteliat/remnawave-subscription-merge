# Deployment

The middleware is intentionally bound to `127.0.0.1:18080` and is not exposed directly to the Internet.

## Requirements

- Python 3.12 virtual environment at `/opt/remnawave-subscription-merge/.venv`;
- `/opt/remnawave-subscription-merge/.env` containing the required Remnawave settings;
- a dedicated system account named `remnawave-merge`.

Required environment variables:

- `REMNAWAVE_API_URL`
- `REMNAWAVE_API_TOKEN`

Optional:

- `REMNAWAVE_SECONDARY_SUFFIX` (default `_addsub`)
- `REMNAWAVE_TIMEOUT_SECONDS` (default `10`)
- `REMNAWAVE_MAX_SUBSCRIPTION_BYTES` (default `8388608`, 8 MiB)

Never put secrets into Git or this documentation.

## Install the service

Run as root:

1. Create the service account if it does not exist: `useradd --system --home /nonexistent --shell /usr/sbin/nologin remnawave-merge`
2. Ensure the application tree is readable by the service account: `chown -R root:remnawave-merge /opt/remnawave-subscription-merge` and `chmod -R g+rX /opt/remnawave-subscription-merge`
3. Restrict the environment file: `chown root:remnawave-merge /opt/remnawave-subscription-merge/.env` and `chmod 640 /opt/remnawave-subscription-merge/.env`
4. Install the unit: `install -o root -g root -m 0644 deploy/remnawave-subscription-merge.service /etc/systemd/system/remnawave-subscription-merge.service`
5. Reload and enable: `systemctl daemon-reload` then `systemctl enable --now remnawave-subscription-merge.service`
6. Verify: `systemctl status remnawave-subscription-merge.service --no-pager` and `curl -fsS http://127.0.0.1:18080/healthz`

## Operations

- Status: `systemctl status remnawave-subscription-merge.service --no-pager`
- Logs: `journalctl -u remnawave-subscription-merge.service -n 100 --no-pager`
- Restart: `systemctl restart remnawave-subscription-merge.service`
- Stop: `systemctl stop remnawave-subscription-merge.service`

The service has no application log file requirement; stdout/stderr are collected by journald.

## Update procedure

From the repository checkout:

`git fetch origin dev`
`git pull --ff-only origin dev`
`.venv/bin/python -m pytest -q`
`systemctl restart remnawave-subscription-merge.service`
`curl -fsS http://127.0.0.1:18080/healthz`

Run the live A2 audit after changes affecting merge behavior.

## Reverse proxy

If the client-facing endpoint must be exposed outside the host, put it behind an existing HTTPS reverse proxy and forward only the required subscription request headers. Do not expose port `18080` directly. A production-oriented Nginx template is provided at `deploy/nginx.conf.example`; adapt the hostname and certificate paths to the actual host. TLS verification and the proxy's access/error logging must follow the project's security rules.
