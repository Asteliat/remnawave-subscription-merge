#!/usr/bin/env bash
set -Eeuo pipefail

REPO="https://github.com/Asteliat/remnawave-subscription-merge.git"
BRANCH="${BRANCH:-dev}"
INSTALL_DIR="${INSTALL_DIR:-/opt/remnawave-subscription-merge}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Запустите установщик от root: sudo bash deploy/install.sh"
  exit 1
fi

if [[ ! -f /etc/os-release ]]; then
  echo "Не удалось определить ОС."
  exit 1
fi
. /etc/os-release
case "${ID}" in
  ubuntu|debian) ;;
  *) echo "Поддерживаются Debian и Ubuntu."; exit 1 ;;
esac

apt-get update
apt-get install -y ca-certificates curl git

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker не найден. Устанавливаю Docker официальным установочным скриптом..."
  curl -fsSL https://get.docker.com | sh
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Не найден Docker Compose plugin."
  echo "Установите актуальный Docker Engine с Compose plugin и запустите установщик снова."
  exit 1
fi

if [[ -d "${INSTALL_DIR}/.git" ]]; then
  git -C "${INSTALL_DIR}" fetch origin "${BRANCH}"
  git -C "${INSTALL_DIR}" checkout "${BRANCH}"
  git -C "${INSTALL_DIR}" reset --hard "origin/${BRANCH}"
else
  rm -rf "${INSTALL_DIR}"
  git clone --branch "${BRANCH}" --depth 1 "${REPO}" "${INSTALL_DIR}"
fi

cd "${INSTALL_DIR}"

if [[ ! -f .env ]]; then
  cp .env.example .env
  chmod 600 .env

  read -r -p "Remnawave API URL: " REMNAWAVE_API_URL
  read -r -s -p "Remnawave API token: " REMNAWAVE_API_TOKEN
  echo

  python3 - "${REMNAWAVE_API_URL}" "${REMNAWAVE_API_TOKEN}" <<'PY'
from pathlib import Path
import sys
p = Path(".env")
s = p.read_text()
s = s.replace("REMNAWAVE_API_URL=", "REMNAWAVE_API_URL=" + sys.argv[1], 1)
s = s.replace("REMNAWAVE_API_TOKEN=", "REMNAWAVE_API_TOKEN=" + sys.argv[2], 1)
p.write_text(s)
PY
  unset REMNAWAVE_API_TOKEN
else
  chmod 600 .env
  echo ".env уже существует — существующая конфигурация сохранена."
fi

mkdir -p /opt/remnawave-subscription-merge-backup
docker compose -f deploy/docker-compose.yml config >/dev/null
docker compose -f deploy/docker-compose.yml up -d --build

echo
echo "Проверка сервиса..."
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:18080/healthz >/dev/null; then
    echo "Готово: middleware работает на 127.0.0.1:18080"
    docker compose -f deploy/docker-compose.yml ps
    exit 0
  fi
  sleep 2
done

echo "Сервис не прошёл healthcheck."
docker compose -f deploy/docker-compose.yml logs --tail=100
exit 1
