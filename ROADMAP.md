# Дорожная карта

Документ описывает состояние middleware слияния подписок.

## A — Основа

Завершено: репозиторий, append-only журнал, архитектура, безопасность и политика секретов.

## B — Remnawave API

Завершено: API client, поиск пользователя, subscription URL, A2 mapping, timeout и контролируемые ошибки.

## C — Merge engine

Завершено: Base64/URI, Clash/Mihomo, Sing-box, Xray, дедупликация, collision-safe имена и metadata policy.

## D — A2 и изоляция

Завершено: персональная secondary-подписка для каждого пользователя и cross-user isolation.

## E — HTTP API

Завершено: client endpoints, header forwarding, parallel upstream fetch, merge и controlled failures.

## F — Автоматическая проверка

Реализованы unit/format/HTTP/client tests и dependency audit через GitHub Actions. Статус конкретного commit необходимо проверять непосредственно в GitHub Actions.

## G — Deployment

Расширено: Dockerfile, Docker Compose, persistent volume, healthcheck, непривилегированный контейнер, localhost-only publication, серверный установщик, update script и systemd fallback.

## H — Rezeis

Реализовано: API ручных пар и runtime-addon без изменения официального исходного кода Rezeis/Reiwa.

## I — Production audit

В работе: проверка конкретного сервера, reverse proxy, реальная клиентская совместимость и восстановление после обновления/пересоздания контейнеров.
