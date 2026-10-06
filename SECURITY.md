# Безопасность

## Секреты

Никогда не коммитьте Remnawave API token, Rezeis token, пароли, cookies, private keys, webhook secrets и реальные subscription URL.

## Remnawave

API token передаётся только через environment и не попадает в URL, логи, SQLite или клиентский ответ.

## Rezeis

Bearer-токен используется только во время административного запроса и не сохраняется. Браузер передаёт subscription ID и Telegram ID, а не произвольный configUrl.

## SSRF

Клиент не выбирает upstream. В A2 источник определяется Remnawave API. В Rezeis режиме configUrl получает сервер.

## CORS

Разрешён только origin из REZEIS_BASE_URL. Wildcard не используется.

## Docker

Публикуйте 18080 только на 127.0.0.1, используйте persistent volume, запускайте приложение не от root и завершайте HTTPS на reverse proxy.

## Runtime addon

Addon изменяет только runtime-файлы Rezeis. Перед index.html создаётся backup. Официальный source не меняется.

## Логи

Не логируйте Authorization, cookies, токены, полные subscription URL и subscription bodies.

## Fail closed

При ошибке main, secondary, формате, лимите размера или merge сервис не отдаёт частичную конфигурацию.

## Проверка перед public

Перед публикацией проверьте всю Git history, workflow logs и attachments. Ищите случайно попавшие JWT, private keys, passwords и tokens.

Если секрет попадал в историю, его необходимо отозвать и перевыпустить. Простого удаления строки недостаточно.
