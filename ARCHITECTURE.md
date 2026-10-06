# Архитектура

## Назначение

Remnawave Subscription Merge — отдельный middleware между клиентом и Remnawave. Remnawave остаётся источником истины и не изменяется.

## A2

    main_username -> main_username_addsub

Поток: client -> main user -> personal secondary -> две public subscription URL -> parallel fetch -> format detect -> merge -> metadata -> merged subscription.

## Ручная пара Rezeis

    Rezeis Admin
        |
        v
    Merge API
        |
        +--> проверить Bearer через Rezeis
        +--> получить exact subscription
        +--> получить configUrl
        v
    SQLite pair store
        |
        v
    /sub/merge/<pair-id>

SQLite используется только для ручных пар.

## Компоненты

- src/http_endpoint.py — FastAPI endpoints и response;
- src/remnawave/ — Remnawave client;
- src/merge.py — merge engine;
- src/metadata.py — subscription-userinfo;
- src/pair_store.py — SQLite;
- src/rezeis.py — Rezeis adapter;
- src/merge_pairs.py — admin API.

## Форматы

Base64/URI, Clash/Mihomo, Sing-box и Xray.

Слияние выполняется по структуре формата, а не через слепное объединение произвольных JSON.

## Безопасность

Upstream URL не приходит от клиента, есть timeout и size limit, TLS verification включён, partial merge не возвращается, Rezeis token не сохраняется, CORS разрешает только origin из REZEIS_BASE_URL.

## Deployment

    HTTPS reverse proxy
            |
            v
    127.0.0.1:18080
            |
            v
    Docker container
       |          |
       v          v
    Remnawave  Rezeis

SQLite pair store находится в persistent Docker volume.

## Rezeis overlay

Официальные Rezeis/Reiwa repositories не изменяются. Runtime addon копируется через docker cp и подключается к уже собранному SPA. После пересоздания контейнера overlay устанавливается снова.
