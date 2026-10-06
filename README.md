# Remnawave Subscription Merge

Отдельный middleware для Remnawave, который объединяет две подписки в одну клиентскую подписку.

Проект работает независимо от Remnawave, Rezeis и Reiwa и не изменяет их исходный код.

## Возможности

- Base64/URI, Clash/Mihomo, Sing-box и Xray;
- параллельное получение двух upstream-подписок;
- дедупликация и безопасное переименование конфликтующих узлов;
- переписывание структурированных ссылок после переименования;
- объединение subscription-userinfo;
- лимит размера upstream-ответа;
- передача необходимых клиентских заголовков;
- fail-closed: при ошибке одной подписки частичный результат не возвращается.

## Два режима

### A2

Основная подписка пользователя автоматически связывается с его личной secondary-подпиской: main_username -> main_username_addsub. Суффикс настраивается через REMNAWAVE_SECONDARY_SUFFIX. Secondary-подписка не является общей для пользователей.

### Ручная пара через Rezeis

В админке Rezeis появляется раздел «Слияние подписок». Администратор выбирает основную и подключаемую подписку. Merge-сервис проверяет Rezeis Bearer-токен, сам получает реальные configUrl и сохраняет пару в отдельном SQLite.

Официальные репозитории Rezeis/Reiwa не меняются.

## Установка на сервер

Рекомендуемый вариант — Docker.

    git clone -b dev https://github.com/Asteliat/remnawave-subscription-merge.git
    cd remnawave-subscription-merge
    sudo bash deploy/install.sh

Установщик проверяет Debian/Ubuntu, устанавливает Docker при необходимости, создаёт /opt/remnawave-subscription-merge, защищённый .env, постоянное хранилище и запускает контейнер.

После установки:

    curl -fsS http://127.0.0.1:18080/healthz
    docker compose -f /opt/remnawave-subscription-merge/deploy/docker-compose.yml ps

Порт слушает только localhost. Наружу сервис публикуется через существующий HTTPS reverse proxy.

## Ручной Docker-запуск

    cp .env.example .env
    nano .env
    docker compose -f deploy/docker-compose.yml up -d --build

Обязательные переменные:

    REMNAWAVE_API_URL=https://panel.example.com
    REMNAWAVE_API_TOKEN=...

Для Rezeis:

    REZEIS_BASE_URL=https://rezeis.example.com
    MERGE_DATA_DIR=/var/lib/remnawave-subscription-merge

## Rezeis runtime-addon

Addon специально устанавливается в работающий контейнер через docker cp, а не в официальный исходный код:

    docker cp integrations/rezeis rezeis:/opt/remnawave-merge
    docker exec rezeis sh -lc 'chmod +x /opt/remnawave-merge/install-runtime-addon.sh && MERGE_PUBLIC_URL="https://merge.example.com" /opt/remnawave-merge/install-runtime-addon.sh'

По умолчанию addon устанавливается в /app/web. После пересоздания контейнера Rezeis runtime-overlay исчезает и его нужно применить повторно.

## Основные endpoints

A2:

    GET /sub/{identifier}
    GET /sub/{identifier}/json
    GET /sub/{identifier}/singbox

Ручные пары:

    GET    /sub/merge/{pair_id}
    GET    /sub/merge/{pair_id}/json
    GET    /sub/merge/{pair_id}/singbox
    GET    /api/admin/merge/pairs
    POST   /api/admin/merge/pairs
    DELETE /api/admin/merge/pairs/{pair_id}

## Обновление

    cd /opt/remnawave-subscription-merge
    git fetch origin dev
    git reset --hard origin/dev
    docker compose -f deploy/docker-compose.yml up -d --build
    curl -fsS http://127.0.0.1:18080/healthz

## Проверка

    python -m pytest -q
    pip-audit

GitHub Actions запускает эти проверки для dev и pull request.

## Документация

- ARCHITECTURE.md — архитектура;
- SECURITY.md — безопасность;
- ROADMAP.md — этапы;
- deploy/README.md — установка и эксплуатация;
- integrations/rezeis/ — runtime-интеграция Rezeis.
