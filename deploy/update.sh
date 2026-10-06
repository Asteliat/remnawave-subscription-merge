#!/usr/bin/env bash
set -Eeuo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/remnawave-subscription-merge}"
BRANCH="${BRANCH:-dev}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите: sudo bash deploy/update.sh"
  exit 1
fi

cd "${INSTALL_DIR}"
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git reset --hard "origin/${BRANCH}"

docker compose -f deploy/docker-compose.yml config >/dev/null
docker compose -f deploy/docker-compose.yml up -d --build

for i in {1..30}; do
  if curl -fsS http://127.0.0.1:18080/healthz >/dev/null; then
    echo "Обновление завершено: сервис работает."
    docker compose -f deploy/docker-compose.yml ps
    exit 0
  fi
  sleep 2
done

echo "После обновления healthcheck не прошёл."
docker compose -f deploy/docker-compose.yml logs --tail=100
exit 1
