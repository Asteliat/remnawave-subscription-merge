# Установка и эксплуатация

## Docker

Основной способ установки — Docker Compose. Он не требует Python на хосте и изолирует зависимости.

    sudo bash deploy/install.sh

Установщик создаёт /opt/remnawave-subscription-merge, защищённый .env, persistent storage, собирает образ и запускает сервис.

Сервис доступен только на 127.0.0.1:18080. Для публичной ссылки используйте существующий HTTPS reverse proxy.

## Обновление

    sudo bash deploy/update.sh

.env не перезаписывается, Docker volume с SQLite сохраняется.

## Команды

    docker compose -f deploy/docker-compose.yml ps
    docker compose -f deploy/docker-compose.yml logs --tail=100
    docker compose -f deploy/docker-compose.yml restart
    curl -fsS http://127.0.0.1:18080/healthz

## Rezeis runtime-addon

Официальный исходный код Rezeis/Reiwa не меняется.

    docker cp integrations/rezeis rezeis:/opt/remnawave-merge
    docker exec rezeis sh -lc 'chmod +x /opt/remnawave-merge/install-runtime-addon.sh && MERGE_PUBLIC_URL="https://merge.example.com" /opt/remnawave-merge/install-runtime-addon.sh'

После пересоздания Rezeis-контейнера overlay нужно применить повторно.

## Альтернатива

В репозитории сохранён systemd unit deploy/remnawave-subscription-merge.service. Для новой установки рекомендуется Docker.

## Безопасность

Не открывайте 18080 наружу. Не храните токены и полные subscription URL в Git или логах.
